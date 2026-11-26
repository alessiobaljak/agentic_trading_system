"""Il programma del trader AI sulla macchina (REGOLE.md, versione 3). Gira sempre; ogni 30 secondi:

1. controlla che il conto sia SUO: nessuna posizione e nessun ordine su altri simboli, nessun ordine di altri, nessuna posizione che
   il trader non abbia aperto, modalità a una posizione; se no si ferma senza toccare niente e lo scrive (revisione del 23 novembre
   2026, problema 95);
2. a mezzanotte UTC scrive il resoconto del giorno finito e riparte dal conto di quel momento;
3. se l'operazione aperta si è chiusa (stop, obiettivo, liquidazione) la scrive nella memoria e chiama subito il modello;
4. la posizione aperta deve avere lo stop sul conto: se manca lo rimette; se il prezzo l'ha già superato, chiude a mercato (problema 96);
5. a +3% dal conto della mezzanotte chiude tutto e si ferma fino alla mezzanotte dopo;
6. a ogni candela da 15 minuti chiusa chiama il modello (se il tetto di spesa lo permette) ed esegue la decisione accettata, dopo aver
   riletto il prezzo e ricontrollato la decisione; se lo stop viene rifiutato dopo l'apertura, chiude subito.

    python -m trader_ai.avvio controlla   # prova del collegamento (sola lettura): prezzo, saldo, posizioni, ordini, modalità
    python -m trader_ai.avvio gira        # il servizio
    python -m trader_ai.avvio chiudi      # chiude tutto e ferma il trader finché non arriva «riparti»
    python -m trader_ai.avvio riparti
"""
from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional

from trader_ai import sveglia
from trader_ai.conto_demo import ContoDemo, arrotonda, controlla_chiavi, nostro
from trader_ai.costi import Budget, costo_massimo
from trader_ai.giro import decidi
from trader_ai.limiti import ORDINE_MIN_VALORE, LEVA_MAX, Conto, Posizione, controlla, obiettivo_raggiunto
from trader_ai.messaggio import bilancio_di_oggi, blocco_memoria, costruisci
from trader_ai.modello import Esito, chiama, crea_client

#: I dati (stato, diario, spesa, resoconti) stanno in una copia del repository diversa da quella del codice (problema 98):
#: sulla macchina TRADER_AI_DATI=/opt/trader-ai-dati/trader_ai/avanti; nei test e in locale, accanto al codice.
CARTELLA = Path(os.environ.get("TRADER_AI_DATI") or Path(__file__).with_name("avanti"))
CONFIG = Path(__file__).with_name("config.json")
#: Lo stesso file di blocco lo usa vps/salva.sh: git non lavora mentre il programma scrive (problema 103).
BLOCCO = Path(os.environ.get("TRADER_AI_BLOCCO", "/tmp/trader-ai-dati.lock"))
INTERVALLI = ("5m", "15m", "30m")
PAUSA_S = 30


def mezzanotte_dopo(ora: datetime) -> datetime:
    return (ora + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


@contextmanager
def bloccato(percorso: Path = BLOCCO, attesa_s: Optional[float] = None):
    """Il blocco condiviso con vps/salva.sh. Con `attesa_s` si rinuncia dopo quel tempo (TimeoutError)."""
    with open(percorso, "a") as f:
        inizio = time.monotonic()
        while True:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | (fcntl.LOCK_NB if attesa_s is not None else 0))
                break
            except BlockingIOError:
                if time.monotonic() - inizio > attesa_s:
                    raise TimeoutError("blocco occupato") from None
                time.sleep(0.5)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


class Trader:
    def __init__(self, conto: ContoDemo, chiama_modello: Callable[[str, str], Esito], cartella: Path = CARTELLA,
                 ora: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> None:
        self.c, self.chiama, self.cartella, self.ora = conto, chiama_modello, Path(cartella), ora
        self.f_stato = self.cartella / "stato.json"
        self.diario = self.cartella / "diario.jsonl"
        self.budget = Budget(self.cartella / "spesa.json")
        #: il fermo a mano: un file scritto da «chiudi» senza aspettare il blocco, letto a inizio passo e prima di ogni ordine
        self.f_fermo = self.cartella / "fermo"
        self._ultimo_controllo_completo = 0.0

    # --- stato -----------------------------------------------------------------------------------------------------
    def carica(self) -> Optional[dict]:
        try:
            return json.loads(self.f_stato.read_text())
        except FileNotFoundError:
            return None

    def salva(self, st: dict) -> None:
        self.cartella.mkdir(parents=True, exist_ok=True)
        tmp = self.f_stato.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1))
        tmp.replace(self.f_stato)

    def evento(self, ora: datetime, cosa: str, **altro) -> None:
        self.cartella.mkdir(parents=True, exist_ok=True)
        with open(self.diario, "a") as f:
            f.write(json.dumps({"ora": ora.isoformat(), "evento": cosa, **altro}, ensure_ascii=False) + "\n")

    def fermo_a_mano(self) -> bool:
        return self.f_fermo.exists()

    def _cid(self, ora: datetime, tipo: str) -> str:
        return f"tai{tipo}{int(ora.timestamp() * 1000)}"

    # --- il conto è suo? -------------------------------------------------------------------------------------------
    def estraneo(self, st: Optional[dict], posizioni: list, ordini: list, modo: bool = True) -> Optional[str]:
        """Il motivo per cui il conto non sembra solo del trader, o None. `modo`: controlla anche la modalità di posizione."""
        if modo and self.c.modo_doppio():
            return "il conto è nella modalità a due posizioni (serve quella a una posizione)"
        altri = sorted({p["simbolo"] for p in posizioni if p["simbolo"] != self.c.simbolo}
                       | {o.get("symbol") for o in ordini if o.get("symbol") != self.c.simbolo})
        if altri:
            return "posizioni o ordini su altri simboli: " + ", ".join(map(str, altri))
        if any(not nostro(o) for o in ordini):
            return "ordini aperti che non sono del trader"
        mia = [p for p in posizioni if p["simbolo"] == self.c.simbolo]
        if mia and not (st and st.get("aperta")):
            return "una posizione che il trader non ha aperto"
        return None

    # --- un passo --------------------------------------------------------------------------------------------------
    def passo(self) -> None:
        ora = self.ora()
        if self.fermo_a_mano():
            return
        st = self.carica()
        # il controllo completo del conto (tutti i simboli e la modalità) costa richieste pesanti: ogni 5 minuti e prima di ogni
        # ordine; negli altri passi solo il simbolo del trader (revisione del 23 novembre 2026, problema 120)
        completo = time.monotonic() - self._ultimo_controllo_completo >= 300 or st is None
        posizioni, ordini = (self.c.posizioni_tutte(), self.c.ordini_tutti()) if completo else \
            (self.c.posizioni_simbolo(), self.c.ordini_simbolo())
        motivo_estraneo = self.estraneo(st, posizioni, ordini, modo=completo)
        if completo and not motivo_estraneo:
            self._ultimo_controllo_completo = time.monotonic()
        if motivo_estraneo:
            st = st or {"operazioni": [], "note": [], "oi": []}
            if st.get("estraneo") != motivo_estraneo:
                self.evento(ora, "FERMO: il conto non è solo del trader, non tocco niente", motivo=motivo_estraneo)
            st["estraneo"] = motivo_estraneo
            self.salva(st)
            return
        if st is None:
            st = {"operazioni": [], "note": [], "oi": []}
            self.evento(ora, "primo avvio su un conto pulito")
        st["estraneo"] = None
        s = self.c.saldo()
        m = self.c.mercato()
        prezzo = m["prezzo"]
        pos = next(({k: v for k, v in p.items() if k != "simbolo"} for p in posizioni if p["simbolo"] == self.c.simbolo), None)
        giorno = ora.strftime("%Y-%m-%d")

        if st.get("giorno") != giorno:                                    # mezzanotte UTC
            if st.get("giorno"):
                self.resoconto(st, st["giorno"])
            st.update(giorno=giorno, conto_mezzanotte=s["conto"], prezzo_mezzanotte=prezzo, fermo_fino=None)
            self.evento(ora, "giorno nuovo", conto=s["conto"])

        chiusa = None
        a = st.get("aperta")
        if a and pos is not None and a.get("inviata"):                     # risposta persa ma ordine eseguito: è nostra
            a.pop("inviata", None)
            self.evento(ora, "apertura eseguita anche se la risposta si era persa")
        if a and pos is None and a.get("inviata"):                         # ordine a mercato mai eseguito (risposta persa o rifiuto)
            if not any(o.get("clientOrderId") == a.get("cid") for o in ordini):
                st["aperta"] = a = None
                self.evento(ora, "ordine di apertura non eseguito")
        if a and pos is None:
            if a.get("in_attesa"):                                        # ordine limite: ancora sul libro?
                if not any(o.get("clientOrderId") == a.get("cid") for o in ordini):
                    st["aperta"] = None
                    self.evento(ora, "ordine limite non più aperto (annullato, scaduto o eseguito e già chiuso)")
            else:
                chiusa = self._registra_chiusura(st, a, s["conto"], prezzo, ora)
        if a and a.get("in_attesa") and pos is not None:                  # ordine limite eseguito
            a.update(in_attesa=False, entrata=pos["entrata"])
        if pos is not None and st.get("aperta"):
            try:
                self._protezione(st, pos, prezzo, [o for o in ordini if o["_algo"]], ora)
            except Exception as e:  # noqa: BLE001 - si scrive e il passo continua (obiettivo e modello non si bloccano)
                self.evento(ora, "protezione non riuscita", errore=str(e)[:300])
            if st.get("aperta") is None:                                  # chiusa dalla protezione
                pos, chiusa = None, chiusa or "chiusa: prezzo oltre lo stop"
                s = self.c.saldo()

        st["oi"] = [x for x in st.get("oi", []) if x[0] > (ora - timedelta(hours=2)).timestamp()]
        st["oi"].append([ora.timestamp(), m["interesse_aperto"]])

        if st.get("fermo_fino") and ora < datetime.fromisoformat(st["fermo_fino"]):
            self.salva(st)
            return
        conto = self._conto(st, s, pos)
        if obiettivo_raggiunto(conto):
            self.c.chiudi(pos, self._cid(ora, "x"))
            if st.get("aperta"):
                st["aperta"]["chiusa_da"] = "obiettivo del giorno"
                self._registra_chiusura(st, st["aperta"], self.c.saldo()["conto"], prezzo, ora)
            st["fermo_fino"] = mezzanotte_dopo(ora).isoformat()
            self.evento(ora, "obiettivo del giorno raggiunto: chiuso tutto, fermo fino a mezzanotte UTC",
                        conto=s["conto"], guadagno=round(s["conto"] - st["conto_mezzanotte"], 2))
            self.salva(st)
            return
        if pos is None and not st.get("aperta") and s["disponibile"] * LEVA_MAX < ORDINE_MIN_VALORE:
            if not st.get("esaurito"):
                self.evento(ora, "FERMO: il conto non basta più per l'ordine minimo", conto=s["conto"])
            st["esaurito"] = True
            self.salva(st)
            return
        st["esaurito"] = False

        motivo = sveglia.motivo(ora, datetime.fromisoformat(st["ultima"]) if st.get("ultima") else None, chiusa)
        if motivo is None:
            self.salva(st)
            return
        ora_ms = int(ora.timestamp() * 1000)
        candele = {tf: self.c.candele(tf, ora_ms) for tf in INTERVALLI}
        mercato = {"prezzo": prezzo, "funding": m["funding"],
                   "minuti_al_prossimo_funding": round((m["prossimo_funding_ms"] - ora_ms) / 60000),
                   "interesse_aperto": m["interesse_aperto"], "interesse_aperto_var_1h_pct": self._oi_1h(st, ora)}
        memoria = blocco_memoria(st["operazioni"], st.get("approccio"), st["note"], st.get("ultimo_scarto"),
                                 bilancio_di_oggi(st["operazioni"], giorno, st.get("prezzo_mezzanotte"), prezzo))
        system, utente = costruisci(ora, motivo, self.budget.rimasto(ora), self.c.simbolo, candele, mercato, conto, memoria)
        ris = decidi(ora, motivo, self.budget, conto, prezzo, lambda: self.chiama(system, utente),
                     costo_massimo(len(system) + len(utente)), self.diario)
        st["ultima"] = ora.isoformat()
        st["ultimo_scarto"] = ris.scarto
        r = ris.esito.risposta if ris.esito else None
        if r is not None:
            if r.cambio_approccio:
                st["cambi_approccio"] = st.get("cambi_approccio", 0) + 1
            st["approccio"] = r.approccio
            st["note"] = (st["note"] + [f"{ora.strftime('%H:%M')} {r.diario}"])[-10:]
        self.salva(st)
        if ris.accettata is not None:
            try:
                self._esegui(st, ris.accettata, pos, s, ora)
            except Exception as e:  # noqa: BLE001 - un rifiuto di Binance si scrive e il modello lo vede alla chiamata dopo
                st["ultimo_scarto"] = f"Binance ha rifiutato: {str(e)[:200]}"
                self.evento(ora, "errore di esecuzione", errore=str(e)[:300])
        self.salva(st)

    # --- pezzi -----------------------------------------------------------------------------------------------------
    def _conto(self, st: dict, s: dict, pos: Optional[dict]) -> Conto:
        a = st.get("aperta") or {}
        p = None
        if pos is not None:
            p = Posizione(pos["lato"], pos["quantita"], pos["entrata"], pos["leva"], a.get("stop") or 0.0, a.get("obiettivo"),
                          pos["liquidazione"])
        elif a.get("in_attesa"):                       # un ordine limite in attesa conta come operazione aperta
            p = Posizione(a["lato"], a["quantita"], a["entrata"], a["leva"], a["stop"], a.get("obiettivo"))
        return Conto(s["conto"], s["disponibile"], st["conto_mezzanotte"], p)

    def _oi_1h(self, st: dict, ora: datetime) -> Optional[float]:
        vecchi = [x for x in st["oi"] if x[0] <= (ora - timedelta(hours=1)).timestamp()]
        if not vecchi or not vecchi[-1][1]:
            return None
        return round((st["oi"][-1][1] / vecchi[-1][1] - 1) * 100, 3)

    def _registra_chiusura(self, st: dict, a: dict, conto_ora: float, prezzo: float, ora: datetime) -> str:
        lungo = a["lato"] == "lungo"
        if a.get("chiusa_da"):
            come = a["chiusa_da"]
        elif a.get("stop") and (prezzo <= a["stop"] * 1.003 if lungo else prezzo >= a["stop"] * 0.997):
            come = "stop"
        elif a.get("obiettivo") and (prezzo >= a["obiettivo"] * 0.997 if lungo else prezzo <= a["obiettivo"] * 1.003):
            come = "obiettivo"
        else:
            come = "chiusa sul conto (stop, obiettivo o liquidazione)"
        op = {"aperta": a["aperta"], "chiusa": ora.isoformat(), "lato": a["lato"], "leva": a["leva"], "entrata": a["entrata"],
              "uscita": prezzo, "come": come, "risultato": round(conto_ora - a["conto_prima"], 2),
              "approccio": a.get("approccio", ""), "margine": a.get("margine")}
        st["operazioni"] = (st["operazioni"] + [op])[-200:]
        st["aperta"] = None
        self.c.annulla_tutto()                        # l'altro ordine condizionato (stop o obiettivo) non serve più
        self.evento(ora, "operazione chiusa", **op)
        return come

    def _chiudi_ora(self, st: dict, pos: dict, prezzo: float, ora: datetime, perche: str) -> None:
        self.c.chiudi(pos, self._cid(ora, "x"))
        st["aperta"]["chiusa_da"] = perche
        self._registra_chiusura(st, st["aperta"], self.c.saldo()["conto"], prezzo, ora)

    def _protezione(self, st: dict, pos: dict, prezzo: float, condizionati: list, ora: datetime) -> None:
        """La posizione aperta deve avere il suo stop sul conto. Se manca: con il prezzo già oltre lo stop si chiude a mercato,
        altrimenti si rimette (e si rimette anche l'obiettivo, se c'era)."""
        a = st["aperta"]
        tick = self.c.filtri()["passo_prezzo"]
        stop_ok = any(str(o.get("clientAlgoId", "")).startswith("tais") for o in condizionati)
        if stop_ok:
            self._obiettivo_sul_conto(a, pos, condizionati, tick, ora)
            return
        stop = a.get("stop")
        lungo = pos["lato"] == "lungo"
        if not stop or (prezzo <= stop if lungo else prezzo >= stop):
            self._chiudi_ora(st, pos, prezzo, ora, "chiusa: senza stop valido sul conto")
            return
        try:
            self.c.condizionato(pos["lato"], "STOP_MARKET", arrotonda(stop, tick), self._cid(ora, "s"))
        except Exception as e:  # noqa: BLE001 - lo stop non si mette: la posizione non resta scoperta
            self.evento(ora, "stop rifiutato: chiudo a mercato", errore=str(e)[:200])
            self._chiudi_ora(st, pos, prezzo, ora, "chiusa: stop rifiutato da Binance")
            return
        self.evento(ora, "stop rimesso sul conto", stop=stop)
        self._obiettivo_sul_conto(a, pos, condizionati, tick, ora)

    def _obiettivo_sul_conto(self, a: dict, pos: dict, condizionati: list, tick: float, ora: datetime) -> None:
        if a.get("obiettivo") and not any(str(o.get("clientAlgoId", "")).startswith("tait") for o in condizionati):
            try:
                self.c.condizionato(pos["lato"], "TAKE_PROFIT_MARKET", arrotonda(a["obiettivo"], tick), self._cid(ora, "t"))
                self.evento(ora, "obiettivo messo sul conto", obiettivo=a["obiettivo"])
            except Exception as e:  # noqa: BLE001
                a["obiettivo"] = None                  # non si riprova a ogni passo; il modello lo vede nel conto
                self.evento(ora, "obiettivo rifiutato", errore=str(e)[:200])

    def _esegui(self, st: dict, r, pos: Optional[dict], s: dict, ora: datetime) -> None:
        if self.fermo_a_mano():
            raise RuntimeError("il proprietario ha fermato il trader")
        posizioni = self.c.posizioni_tutte()
        motivo = self.estraneo(st, posizioni, self.c.ordini_tutti(), modo=False)
        if motivo:
            raise RuntimeError(f"il conto non è solo del trader: {motivo}")
        # la posizione si rilegge adesso: un ordine limite può essersi eseguito mentre il modello pensava (problema 133)
        pos = next(({k: v for k, v in p.items() if k != "simbolo"} for p in posizioni if p["simbolo"] == self.c.simbolo), None)
        if pos is not None and (st.get("aperta") or {}).get("in_attesa"):
            st["aperta"].update(in_attesa=False, entrata=pos["entrata"])
        f = self.c.filtri()
        tick = f["passo_prezzo"]
        prezzo = self.c.mercato()["prezzo"]                       # il prezzo è cambiato mentre il modello pensava
        scarto = controlla(r, self._conto(st, s, pos), prezzo)
        if scarto:
            raise RuntimeError(f"con il prezzo di adesso ({prezzo:g}) la decisione non vale più: {scarto}")
        if r.azione in ("apri_lungo", "apri_corto"):
            lato = "lungo" if r.azione == "apri_lungo" else "corto"
            leva = int(r.leva)
            limite = r.tipo_ordine == "limite"
            rif = r.prezzo_limite if limite else prezzo
            q = arrotonda(r.margine_usdt * leva / rif, f["passo_quantita_limite" if limite else "passo_quantita"])
            if q < f["quantita_min"] or q * rif < f["valore_min"]:
                raise RuntimeError(f"quantità {q} sotto i minimi del simbolo")
            cid = self._cid(ora, "o")
            # l'intenzione si salva PRIMA dell'invio: se la risposta si perde, al passo dopo l'ordine si riconosce dal nome
            st["aperta"] = {"aperta": ora.isoformat(), "lato": lato, "leva": leva, "entrata": rif, "quantita": q, "cid": cid,
                            "stop": r.stop_prezzo, "obiettivo": r.obiettivo_prezzo, "approccio": r.approccio,
                            "conto_prima": s["conto"], "margine": r.margine_usdt, "in_attesa": limite, "inviata": not limite}
            self.salva(st)
            self.c.prepara(leva)
            if self.fermo_a_mano():
                st["aperta"] = None
                raise RuntimeError("il proprietario ha fermato il trader")
            esito = self.c.apri(lato, q, cid, "LIMIT" if limite else "MARKET", arrotonda(rif, tick) if limite else None)
            st["aperta"].pop("inviata", None)
            if self.fermo_a_mano():                    # «chiudi» è arrivato mentre l'ordine partiva: si richiude subito
                if limite:
                    self._annulla_limite(st, prezzo, ora, "ordine limite annullato: fermo a mano")
                else:
                    st["aperta"]["entrata"] = float(esito.get("avgPrice") or 0) or prezzo
                    self._chiudi_ora(st, {"lato": lato, "quantita": float(esito.get("executedQty") or q)}, prezzo, ora,
                                     "chiusa a mano dal proprietario")
                raise RuntimeError("il proprietario ha fermato il trader mentre l'ordine partiva: richiuso")
            if limite:                                 # stop subito: scatta solo quando la posizione c'è (da provare sul demo)
                try:
                    self.c.condizionato(lato, "STOP_MARKET", arrotonda(r.stop_prezzo, tick), self._cid(ora, "s"))
                except Exception as e:  # noqa: BLE001 - lo metterà la protezione appena l'ordine è eseguito
                    self.evento(ora, "stop dell'ordine limite non accettato prima dell'esecuzione", errore=str(e)[:200])
            if not limite:
                st["aperta"]["entrata"] = float(esito.get("avgPrice") or 0) or prezzo
                nuova = {"lato": lato, "quantita": float(esito.get("executedQty") or q)}
                try:
                    self.c.condizionato(lato, "STOP_MARKET", arrotonda(r.stop_prezzo, tick), self._cid(ora, "s"))
                except Exception as e:  # noqa: BLE001 - nessuna posizione senza stop: si chiude subito
                    self.evento(ora, "stop rifiutato dopo l'apertura: chiudo a mercato", errore=str(e)[:200])
                    self._chiudi_ora(st, nuova, prezzo, ora, "chiusa: stop rifiutato da Binance")
                    raise RuntimeError(f"stop rifiutato, operazione chiusa subito: {str(e)[:150]}") from None
                if r.obiettivo_prezzo:
                    try:
                        self.c.condizionato(lato, "TAKE_PROFIT_MARKET", arrotonda(r.obiettivo_prezzo, tick), self._cid(ora, "t"))
                    except Exception as e:  # noqa: BLE001
                        st["aperta"]["obiettivo"] = None
                        self.evento(ora, "obiettivo rifiutato (lo stop c'è)", errore=str(e)[:200])
            self.evento(ora, "aperta", **{k: v for k, v in st["aperta"].items() if k != "conto_prima"})
        elif r.azione == "chiudi":
            a = st.get("aperta") or {}
            if pos is None:                            # solo un ordine limite in attesa: si annulla
                self._annulla_limite(st, prezzo, ora, "ordine limite annullato dal modello")
            else:
                a["chiusa_da"] = "chiusa dal modello"
                self.c.chiudi(pos, self._cid(ora, "x"))
                self._registra_chiusura(st, a, self.c.saldo()["conto"], prezzo, ora)
        elif r.azione == "modifica":
            a = st.get("aperta") or {}
            condizionati = [o for o in self.c.ordini_tutti() if o["_algo"]]
            # con l'ordine limite in attesa la posizione non c'è ancora, ma stop e obiettivo sul conto sì
            bersaglio = pos if pos is not None else {"lato": a["lato"], "quantita": a["quantita"], "in_attesa": True}
            for campo, tipo, sigla, valore in (("stop", "STOP_MARKET", "s", r.stop_prezzo),
                                               ("obiettivo", "TAKE_PROFIT_MARKET", "t", r.obiettivo_prezzo)):
                if valore is None:
                    continue
                vecchi = [o for o in condizionati if str(o.get("clientAlgoId", "")).startswith("tai" + sigla)]
                self._sostituisci(st, a, bersaglio, prezzo, ora, campo, tipo, sigla, valore, vecchi, tick)
                if st.get("aperta") is None:           # chiusa (o limite annullato) perché nessuno stop è stato accettato
                    return
                a[campo] = valore
            self.evento(ora, "modificata", stop=a.get("stop"), obiettivo=a.get("obiettivo"))

    def _annulla_limite(self, st: dict, prezzo: float, ora: datetime, perche: str) -> None:
        """Annulla l'ordine limite (e stop e obiettivo); poi rilegge: se nel frattempo si è eseguito, la posizione si chiude subito
        a mercato con «solo riduzione», perché senza stop non deve restare (revisione del 23 novembre 2026, problemi 133 e 134)."""
        self.c.annulla_tutto()
        rimasta = next(({k: v for k, v in p.items() if k != "simbolo"} for p in self.c.posizioni_simbolo()), None)
        if rimasta is None:
            # l'annullamento può non riuscire senza errore (annulla_tutto scrive e va avanti): se l'ordine limite del trader è
            # ancora sul libro, l'operazione resta «in attesa» e si riprova (revisione del 23 novembre 2026, problemi 136 e 140)
            if any(nostro(o) and not o["_algo"] for o in self.c.ordini_simbolo()):
                self.evento(ora, "ordine limite ancora aperto dopo l'annullamento: resta in attesa")
                raise RuntimeError("l'ordine limite non si è annullato: riprovo alla chiamata dopo")
            st["aperta"] = None
            self.evento(ora, perche)
            return
        a = st.get("aperta") or {"aperta": ora.isoformat(), "lato": rimasta["lato"], "leva": rimasta["leva"],
                                 "conto_prima": st.get("conto_mezzanotte", 0.0)}
        a.update(in_attesa=False, entrata=rimasta["entrata"])
        st["aperta"] = a
        self.evento(ora, "il limite si era eseguito mentre lo annullavo: chiudo a mercato")
        self._chiudi_ora(st, rimasta, prezzo, ora, "chiusa: limite eseguito durante l'annullamento")

    def _sostituisci(self, st, a, pos, prezzo, ora, campo, tipo, sigla, valore, vecchi, tick) -> None:
        """Mette il nuovo stop (o obiettivo) senza lasciare mai la posizione scoperta: prima il nuovo accanto al vecchio; se Binance
        lo rifiuta, si toglie il vecchio e si riprova il nuovo; se ancora no, si rimette il vecchio; se nemmeno quello, per uno
        stop si chiude a mercato (revisione del 23 novembre 2026, problemi 99 e 118)."""
        def metti(prezzo_ordine):
            self.c.condizionato(pos["lato"], tipo, arrotonda(prezzo_ordine, tick), self._cid(ora, sigla))
        try:
            metti(valore)
            messo = True
        except Exception:  # noqa: BLE001
            messo = False
        if messo:
            for o in vecchi:
                try:
                    self.c.annulla_condizionato(o)
                except Exception as e:  # noqa: BLE001 - resta un ordine in più, più stretto o più largo: si scrive
                    self.evento(ora, f"{campo} vecchio non annullato", errore=str(e)[:200])
            return
        for o in vecchi:
            self.c.annulla_condizionato(o)
        try:
            metti(valore)
            return
        except Exception as e:  # noqa: BLE001
            errore = str(e)[:200]
        vecchio = a.get(campo)
        rimesso = False
        if vecchio:
            try:
                metti(vecchio)
                rimesso = True
            except Exception:  # noqa: BLE001 - qualunque errore: si passa alla chiusura
                pass
        if rimesso:
            raise RuntimeError(f"{campo} nuovo rifiutato, rimesso il vecchio: {errore}")
        if campo == "stop" and pos.get("in_attesa"):
            self.evento(ora, "nessuno stop accettato: annullo l'ordine limite", errore=errore)
            self._annulla_limite(st, prezzo, ora, "ordine limite annullato: nessuno stop accettato")
            return
        if campo == "stop":
            self.evento(ora, "nessuno stop accettato: chiudo a mercato", errore=errore)
            self._chiudi_ora(st, pos, prezzo, ora, "chiusa: stop rifiutato da Binance")
            return
        a["obiettivo"] = None
        raise RuntimeError(f"obiettivo rifiutato: {errore}")

    def chiudi_tutto_e_ferma(self, attesa_blocco_s: float = 30.0) -> None:
        """Il fermo si scrive SUBITO (file, senza blocco): il programma non apre più niente da quel momento, anche se la chiusura
        fallisce. Poi la chiusura su Binance, poi lo stato (con il blocco, al massimo `attesa_blocco_s`)."""
        ora = self.ora()
        self.cartella.mkdir(parents=True, exist_ok=True)
        tmp = self.f_fermo.with_suffix(".tmp")
        tmp.write_text(ora.isoformat())
        tmp.replace(self.f_fermo)
        posizioni, ordini = self.c.posizioni_tutte(), self.c.ordini_tutti()
        st = self.carica()
        motivo = self.estraneo(st, posizioni, ordini, modo=False)
        if motivo:
            raise SystemExit(f"fermo scritto, ma il conto non è solo del trader ({motivo}): non chiudo niente, guarda il conto")
        pos = next(({k: v for k, v in p.items() if k != "simbolo"} for p in posizioni if p["simbolo"] == self.c.simbolo), None)
        try:
            self.c.chiudi(pos, self._cid(ora, "x"))
        except Exception as e:  # noqa: BLE001
            raise SystemExit(f"fermo scritto, ma la chiusura NON è riuscita: {str(e)[:200]}; riprova tra poco") from None
        try:
            with bloccato(BLOCCO, attesa_blocco_s):
                st = self.carica() or {"operazioni": [], "note": [], "oi": []}
                if st.get("aperta") and pos is not None:
                    st["aperta"]["chiusa_da"] = "chiusa a mano dal proprietario"
                    self._registra_chiusura(st, st["aperta"], self.c.saldo()["conto"], self.c.mercato()["prezzo"], ora)
                st["aperta"] = None
                self.evento(ora, "chiuso tutto a mano; fermo finché non arriva «riparti»")
                self.salva(st)
        except TimeoutError:
            print("[trader_ai] chiuso e fermo; lo stato si aggiornerà al passo dopo (il blocco era occupato)")
        # un ordine partito nei secondi fra il controllo del fermo e l'invio: si rilegge e si richiude
        rimasta = next(({k: v for k, v in p.items() if k != "simbolo"} for p in self.c.posizioni_simbolo()), None)
        if rimasta is not None or any(nostro(o) for o in self.c.ordini_simbolo()):
            self.c.chiudi(rimasta, self._cid(self.ora(), "x"))
            print("[trader_ai] trovata e richiusa un'operazione partita durante il comando")

    def riparti(self) -> None:
        self.f_fermo.unlink(missing_ok=True)
        self.evento(self.ora(), "riparti")

    def resoconto(self, st: dict, giorno: str) -> Path:
        ops = [o for o in st["operazioni"] if o["chiusa"].startswith(giorno)]
        spesa = self.budget.speso(datetime.fromisoformat(giorno + "T12:00:00+00:00"))
        guadagno = sum(o["risultato"] for o in ops)
        righe = [f"# Trader AI, {giorno} (UTC)", "",
                 f"* Conto a mezzanotte: {st.get('conto_mezzanotte', 0):.2f} USDT; risultato delle operazioni chiuse: "
                 f"{guadagno:+.2f} USDT; obiettivo del 3%: {'sì' if st.get('fermo_fino') else 'no'}",
                 f"* Operazioni chiuse: {len(ops)} (in guadagno {sum(o['risultato'] > 0 for o in ops)}); "
                 f"cambi di approccio dall'inizio: {st.get('cambi_approccio', 0)}",
                 f"* Costo delle chiamate al modello: {spesa:.2f} dollari", "",
                 "| aperta | chiusa | lato | leva | entrata | uscita | come | risultato | approccio |", "|---|---|---|---|---|---|---|---|---|"]
        for o in ops:
            righe.append(f"| {o['aperta'][11:16]} | {o['chiusa'][11:16]} | {o['lato']} | {o['leva']:g} | {o['entrata']:g} | "
                         f"{o['uscita']:g} | {o['come']} | {o['risultato']:+.2f} | {o['approccio']} |")
        p = self.cartella / "resoconti" / f"{giorno}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("\n".join(righe) + "\n")
        return p


def _commit() -> str:
    try:
        return subprocess.run(["git", "-C", str(Path(__file__).parent), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, timeout=10).stdout.strip() or "?"
    except Exception:  # noqa: BLE001
        return "?"


def main(argv: list) -> int:
    cfg = json.loads(CONFIG.read_text())
    if cfg.get("conto", "simulato") == "simulato":   # decisione del proprietario del 24 novembre 2026
        from trader_ai.conto_simulato import ContoSimulato, MercatoPubblico
        conto = ContoSimulato(MercatoPubblico(cfg["moneta"]), CARTELLA / "conto_simulato.json")
    else:
        chiave, segreto = controlla_chiavi()
        conto = ContoDemo(chiave, segreto, cfg["moneta"])
    comando = argv[1] if len(argv) > 1 else "controlla"
    if comando == "controlla":                         # sola lettura
        m, s = conto.mercato(), conto.saldo()
        pos, ordini = conto.posizioni_tutte(), conto.ordini_tutti()
        print(f"[trader_ai] {cfg['moneta']} prezzo {m['prezzo']}; conto {s['conto']:.2f} USDT, disponibile {s['disponibile']:.2f}")
        print(f"[trader_ai] modalità a due posizioni: {conto.modo_doppio()}; posizioni aperte: {len(pos)}; ordini aperti: "
              f"{len(ordini)} (condizionati {sum(o['_algo'] for o in ordini)}); filtri {conto.filtri()}")
        motivo = Trader(conto, lambda *_: None).estraneo(None, pos, ordini)
        if motivo is None and (pos or ordini):          # pulito vuol dire vuoto, anche di ordini del trader
            motivo = f"{len(pos)} posizioni e {len(ordini)} ordini aperti"
        print(f"[trader_ai] conto pulito per il primo avvio: {'sì' if motivo is None else 'NO: ' + motivo}")
        return 0
    trader = Trader(conto, lambda *_: None)
    if comando in ("chiudi", "riparti"):
        trader.chiudi_tutto_e_ferma() if comando == "chiudi" else trader.riparti()
        print(f"[trader_ai] {comando}: fatto")
        return 0
    if comando != "gira":
        print("uso: python -m trader_ai.avvio controlla|gira|chiudi|riparti")
        return 2
    client = crea_client()
    trader.chiama = lambda system, utente: chiama(client, system, utente)
    print(f"[trader_ai] acceso su {cfg['moneta']}, conto {cfg.get('conto', 'simulato')}, codice al commit {_commit()}, "
          f"dati in {CARTELLA}", flush=True)
    trader.evento(datetime.now(timezone.utc), "acceso", commit=_commit(), moneta=cfg["moneta"], conto=cfg.get("conto", "simulato"))
    while True:
        try:
            with bloccato():
                trader.passo()
        except Exception:  # noqa: BLE001 - un errore non ferma il servizio: si scrive e si riprova
            print("[trader_ai] errore nel passo:\n" + traceback.format_exc()[-1500:], flush=True)
        time.sleep(PAUSA_S)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
