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

Dal 26 novembre 2026 (controllo del 26 novembre, `trader_ai/revisioni/2026-11-26-controllo-istruzioni-e-dati.md`): un ordine limite in
attesa non è un'operazione aperta; un limite eseguito e chiuso fra due controlli si registra (e chiama subito il modello); uscita, modo,
spese e funding di ogni operazione si leggono dal conto (`esito_ordine`); dopo un «chiudi» del modello il modello si richiama subito;
la memoria scritta prima si ricostruisce una volta dal conto simulato (`ripara.py`).

    python -m trader_ai.avvio controlla   # prova del collegamento (sola lettura): prezzo, saldo, posizioni, ordini, modalità
    python -m trader_ai.avvio gira        # il servizio
    python -m trader_ai.avvio chiudi      # chiude tutto e ferma il trader finché non arriva «riparti»
    python -m trader_ai.avvio riparti
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import re
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
from trader_ai.limiti import ORDINE_MIN_VALORE, LEVA_MAX, Conto, Posizione, controlla, obiettivo_raggiunto, obiettivo_usdt
from trader_ai.messaggio import Memoria, atr_per_intervallo, costruisci
from trader_ai.modello import Esito, chiama, crea_client
from trader_ai.operazioni import bilancio, escursione, iso_da_ms, ms, spese_entrata, tipo_di_stop, un_r
from trader_ai.ripara import lezioni_dal_diario, ricostruisci

#: I dati (stato, diario, spesa, resoconti) stanno in una copia del repository diversa da quella del codice (problema 98):
#: sulla macchina TRADER_AI_DATI=/opt/trader-ai-dati/trader_ai/avanti; nei test e in locale, accanto al codice.
CARTELLA = Path(os.environ.get("TRADER_AI_DATI") or Path(__file__).with_name("avanti"))
#: I messaggi interi al modello (1-2 MB al giorno) stanno FUORI da avanti/: vps/salva.sh aggiunge tutta avanti/ a git prima di
#: riallinearsi, e il .gitignore nuovo arriverebbe solo con quel riallineamento (revisione del 26 novembre 2026, problema 191).
#: Sulla macchina: /opt/trader-ai-dati/trader_ai/messaggi_modello, mai aggiunta da salva.sh.
CARTELLA_MESSAGGI = Path(os.environ.get("TRADER_AI_MESSAGGI") or CARTELLA.parent / "messaggi_modello")
CONFIG = Path(__file__).with_name("config.json")
#: Lo stesso file di blocco lo usa vps/salva.sh: git non lavora mentre il programma scrive (problema 103).
BLOCCO = Path(os.environ.get("TRADER_AI_BLOCCO", "/tmp/trader-ai-dati.lock"))
INTERVALLI = ("5m", "15m", "30m")
#: Candele per intervallo: 300 da 5 minuti coprono più di un giorno (prezzo e VWAP dalla mezzanotte, punti 2.8 e 2.9 del controllo
#: del 26 novembre 2026); 200 da 15 e da 30 minuti (100 ore per i livelli dei giorni prima).
QUANTE = {"5m": 300, "15m": 200, "30m": 200}
PAUSA_S = 30
#: La versione della memoria: sotto la 7 si ricostruisce dal conto (ripara.py) una volta sola.
VERSIONE_MEMORIA = 7
#: I messaggi interi al modello restano sulla macchina, fuori da git, per questi giorni (punto 2.7).
GIORNI_MESSAGGI = 7
#: Il capitale con cui è partita la prova (decisione del 23 novembre 2026: 1.000 USDT), se il conto non lo dice.
CAPITALE_PROVA = 1000.0


def _hm_iso(iso: Optional[str]) -> str:
    return datetime.fromisoformat(iso).astimezone(timezone.utc).strftime("%H:%M") if iso else "-"


def _ieri(giorno: str) -> str:
    return (datetime.fromisoformat(giorno + "T12:00:00+00:00") - timedelta(days=1)).strftime("%Y-%m-%d")


class Scartata(RuntimeError):
    """Una decisione che il programma non esegue (non un rifiuto del conto): il modello lo legge alla chiamata dopo."""


def taglia(testo: Optional[str], n: int) -> str:
    testo = (testo or "").strip()
    return testo if len(testo) <= n else testo[:n - 1].rstrip() + "…"


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
                 ora: Callable[[], datetime] = lambda: datetime.now(timezone.utc), messaggi: Optional[Path] = None) -> None:
        self.c, self.chiama, self.cartella, self.ora = conto, chiama_modello, Path(cartella), ora
        self.cartella_messaggi = Path(messaggi) if messaggi else self.cartella / "messaggi"
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
    def stato_nuovo(self) -> dict:
        return {"operazioni": [], "note": [], "lezioni": [], "versione_memoria": VERSIONE_MEMORIA, "prossimo_n": 1}

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
            st = st or self.stato_nuovo()
            if st.get("estraneo") != motivo_estraneo:
                self.evento(ora, "FERMO: il conto non è solo del trader, non tocco niente", motivo=motivo_estraneo)
            st["estraneo"] = motivo_estraneo
            self.salva(st)
            return
        if st is None:
            st = self.stato_nuovo()
            self.evento(ora, "primo avvio su un conto pulito")
        st["estraneo"] = None
        giorno = ora.strftime("%Y-%m-%d")
        st.setdefault("inizio", {"giorno": str((st["operazioni"] or [{}])[0].get("aperta", giorno))[:10],
                                 "conto": float(getattr(self.c, "capitale", 0) or CAPITALE_PROVA)})
        if st.get("versione_memoria", 0) < VERSIONE_MEMORIA:
            self._ripara_memoria(st, ora)
        s = self.c.saldo()
        m = self.c.mercato()
        prezzo = m["prezzo"]
        pos = next(({k: v for k, v in p.items() if k != "simbolo"} for p in posizioni if p["simbolo"] == self.c.simbolo), None)

        # una chiusura (o un annullamento) decisa dal modello al passo prima: il modello si richiama subito (punto 2.10 del
        # controllo del 26 novembre); qui c'è già il motivo intero della chiamata
        richiama = st.pop("richiama", None)
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
                    pos, chiusa = self._limite_sparito(st, a, ora, s["conto"], prezzo)
            else:
                chiusa = self._registra_chiusura(st, a, s["conto"], prezzo, ora)
        elif a and a.get("in_attesa") and pos is not None:                # ordine limite eseguito
            self._eseguito(a, self._esito_o_niente(a), ora, pos)
            self.evento(ora, "ordine limite eseguito", entrata=a["entrata"], eseguita=a["eseguita"])
        if pos is not None and st.get("aperta"):
            come_protezione = None
            try:
                come_protezione = self._protezione(st, pos, prezzo, [o for o in ordini if o["_algo"]], ora)
            except Exception as e:  # noqa: BLE001 - si scrive e il passo continua (obiettivo e modello non si bloccano)
                self.evento(ora, "protezione non riuscita", errore=str(e)[:300])
            if st.get("aperta") is None:                                  # chiusa dalla protezione
                pos, chiusa = None, chiusa or come_protezione or "chiusa dal programma"
                s = self.c.saldo()

        # mezzanotte UTC: dopo aver registrato le chiusure trovate in questo passo, così un'operazione chiusa nell'ultimo minuto del
        # giorno entra nel resoconto del suo giorno (revisione del 26 novembre 2026, S6)
        if st.get("giorno") != giorno:
            if st.get("giorno"):
                self.resoconto(st, st["giorno"], s["conto"], prezzo)
            g = st.get("stat_giorno") or {}
            if g.get("chiamate"):
                st["costo_medio_ieri"] = g["costo"] / g["chiamate"]
            st["tetto_ieri"] = st.get("tetto_dalle")
            st.update(giorno=giorno, conto_mezzanotte=s["conto"], prezzo_inizio_giorno=prezzo, fermo_fino=None, obiettivo_ora=None,
                      tetto_dalle=None, massimo_giorno=s["conto"], discesa_max_giorno=0.0, discesa_dalle=ora.isoformat(),
                      stat_giorno={})
            st.pop("prezzo_mezzanotte", None)
            self.evento(ora, "giorno nuovo", conto=s["conto"])
            self._pulisci_messaggi(ora)
        st.setdefault("discesa_dalle", ora.isoformat())
        st["massimo_giorno"] = max(st.get("massimo_giorno", s["conto"]), s["conto"])
        st["discesa_max_giorno"] = max(st.get("discesa_max_giorno", 0.0), st["massimo_giorno"] - s["conto"])

        if st.get("fermo_fino") and ora < datetime.fromisoformat(st["fermo_fino"]):
            self.salva(st)
            return
        conto = self._conto(st, s, pos)
        if obiettivo_raggiunto(conto):
            chiuso = self.c.chiudi(pos, self._cid(ora, "x"))
            if st.get("aperta") and pos is None and st["aperta"].get("in_attesa"):
                st["aperta"] = None                                       # un limite mai eseguito non è un'operazione
                self.evento(ora, "ordine limite annullato: obiettivo del giorno raggiunto")
            elif st.get("aperta"):
                if chiuso:
                    st["aperta"]["chiusa_da"] = "obiettivo del giorno (chiusa dal programma)"
                self._registra_chiusura(st, st["aperta"], self.c.saldo()["conto"], prezzo, ora)
            st["fermo_fino"] = mezzanotte_dopo(ora).isoformat()
            st["obiettivo_ora"] = ora.isoformat()
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
        if richiama and not chiusa:
            motivo = richiama
        if motivo is None:
            self.salva(st)
            return
        self._decidi_ed_esegui(st, ora, motivo, s, m, pos, conto, giorno)

    def _decidi_ed_esegui(self, st: dict, ora: datetime, motivo: str, s: dict, m: dict, pos: Optional[dict], conto: Conto,
                          giorno: str) -> None:
        ora_ms = int(ora.timestamp() * 1000)
        prezzo = m["prezzo"]
        candele = {tf: self.c.candele(tf, ora_ms, n=QUANTE[tf]) for tf in INTERVALLI}
        try:
            storia_oi = self.c.interesse_aperto_storia()
        except Exception:  # noqa: BLE001 - senza la storia il messaggio dice «-»
            storia_oi = []
        mercato = {"prezzo": prezzo, "indice": m.get("indice"), "funding": m["funding"],
                   "minuti_al_prossimo_funding": round((m["prossimo_funding_ms"] - ora_ms) / 60000),
                   "interesse_aperto": m["interesse_aperto"], "interesse_aperto_storia": storia_oi}
        a = st.get("aperta")
        if a and pos is not None and a.get("eseguita"):
            try:
                a["escursione"] = list(self._escursione(a, None, ora))
            except Exception as e:  # noqa: BLE001 - il messaggio parte lo stesso, senza questa riga
                self.evento(ora, "escursione della posizione non calcolata", errore=str(e)[:200])
            esito = self._esito_o_niente(a)                               # il funding già pagato o ricevuto (punto M1)
            if esito and esito.get("funding") is not None:
                a["funding"] = esito["funding"]
        memoria = Memoria(st["operazioni"], st.get("lezioni", []), st["note"], st.get("approccio"), st.get("ultimo_scarto"),
                          st["inizio"], giorno)
        system, stabile, variabile = costruisci(ora, motivo, self.c.simbolo, candele, mercato, conto, a, memoria,
                                                self._chiamate(st, ora))
        impronta = hashlib.sha256((system + stabile + variabile).encode()).hexdigest()[:12]
        costo_max = costo_massimo(len(system) + len(stabile) + len(variabile))
        ris = decidi(ora, motivo, self.budget, conto, prezzo, lambda: self.chiama(system, [stabile, variabile]), costo_max,
                     self.diario, {"impronta": impronta})
        self._salva_messaggio(ora, motivo, impronta, stabile, variabile, ris)
        self._conta(st, ris, costo_max)
        st["ultima"] = ora.isoformat()
        if ris.esito is not None:                     # senza chiamata (tetto) lo scarto di prima resta da dire (R7-07)
            st["ultimo_scarto"] = ris.scarto and f"scartata dal programma: {ris.scarto}"
        if ris.stato == "tetto" and not st.get("tetto_dalle"):
            st["tetto_dalle"] = ora.isoformat()
        if ris.esito is not None and ris.stato != "ok":
            # la risposta non letta non deve sembrare eseguita (punto 2.5 del controllo del 26 novembre)
            st["ultimo_scarto"] = (f"la tua risposta delle {ora:%H:%M} non è stata letta ({ris.stato}"
                                   + (f": {ris.esito.dettaglio[:150]}" if ris.esito.dettaglio else "") + "): nessuna azione eseguita")
        if ris.esito is not None:
            st.pop("tetto_ieri", None)                                    # detto una volta, alla prima chiamata del giorno
        r = ris.esito.risposta if ris.esito else None
        if r is not None:
            if r.cambio_approccio:
                st["cambi_approccio"] = st.get("cambi_approccio", 0) + 1
            st["approccio"] = taglia(r.approccio, 250)
            diario = re.sub(r"^\s*\d{1,2}[:.]\d{2}(?::\d{2})?\s*[:,—–-]?\s*", "", r.diario or "")   # l'ora c'è già (R7-10)
            st["note"] = (st["note"] + [f"{ora:%d/%m %H:%M} {taglia(diario, 700)}"])[-10:]
            self._lezioni(st, r, ora, motivo, conto)
        self.salva(st)
        if ris.accettata is not None and ris.accettata.azione != "aspetta":
            try:
                self._esegui(st, ris.accettata, pos, s, ora, atr_per_intervallo(candele, ora).get("15m"))
            except Scartata as e:
                st["ultimo_scarto"] = f"non eseguita dal programma: {str(e)[:300]}"
                self.evento(ora, "decisione non eseguita", motivo=str(e)[:300])
            except Exception as e:  # noqa: BLE001 - un rifiuto del conto si scrive e il modello lo vede alla chiamata dopo
                st["ultimo_scarto"] = f"rifiutata dal conto: {str(e)[:200]}"
                self.evento(ora, "errore di esecuzione", errore=str(e)[:300])
        self.salva(st)

    def _lezioni(self, st: dict, r, ora: datetime, motivo: str, conto: Conto) -> None:
        """Le lezioni scritte dal modello (e i perché dei cambi di approccio) restano anche nei giorni dopo (punto 3.4). Entrano
        nella memoria stabile alla chiusura dopo: così la cache non si riscrive a ogni chiamata."""
        ultima = (st["operazioni"] or [{}])[-1].get("n")
        base = {"ora": ora.isoformat(), "dopo": ultima, "giorno_netto": round(conto.conto - conto.conto_mezzanotte, 2),
                "fissata": False}
        nuove = []
        if r.lezione and r.lezione.strip():
            nuove.append({**base, "testo": taglia(r.lezione, 400)})
        if r.cambio_approccio and r.perche and r.perche.strip():
            nuove.append({**base, "testo": "cambio di approccio: " + taglia(r.perche, 380)})
        if nuove:
            st["lezioni"] = (st.get("lezioni", []) + nuove)[-50:]

    def _conta(self, st: dict, ris, costo_max: float) -> None:
        """I numeri del giorno per il resoconto e per le chiamate rimaste."""
        st["ultimo_costo_massimo"] = round(costo_max, 4)
        if ris.esito is None:
            return
        g = st.setdefault("stat_giorno", {})
        g["chiamate"] = g.get("chiamate", 0) + 1
        g["costo"] = round(g.get("costo", 0.0) + ris.costo, 6)
        esiti = g.setdefault("esiti", {})
        chiave = "scartata" if ris.scarto else ris.stato
        esiti[chiave] = esiti.get(chiave, 0) + 1
        g["durata_tot"] = round(g.get("durata_tot", 0.0) + ris.esito.durata_s, 1)
        g["durata_max"] = max(g.get("durata_max", 0.0), ris.esito.durata_s)
        uscita = ris.esito.usage.get("output_tokens") or 0
        g["uscita_tot"] = g.get("uscita_tot", 0) + uscita
        if ris.esito.risposta is not None and ris.esito.risposta.cambio_approccio:
            g["cambi"] = g.get("cambi", 0) + 1

    def _chiamate(self, st: dict, ora: datetime) -> str:
        """Quante chiamate restano oggi, senza dollari (punto 3.5: il modello aspettava «per risparmiare budget», ma le chiamate
        arrivano comunque a ogni candela)."""
        rimasto = self.budget.rimasto(ora)
        g = st.get("stat_giorno") or {}
        medio = (g["costo"] / g["chiamate"]) if g.get("chiamate") else (st.get("costo_medio_ieri") or 0.06)
        riserva = st.get("ultimo_costo_massimo") or 0.45
        quante = int(max(0.0, rimasto - riserva) / max(medio, 0.001)) + 1
        alla_mezzanotte = math.ceil((mezzanotte_dopo(ora) - ora).total_seconds() / 900)
        if quante >= alla_mezzanotte:
            testo = "bastano fino a mezzanotte UTC con il ritmo di oggi"
        else:
            ultima = ora + timedelta(minutes=15 * (quante - 1))
            testo = (f"circa {quante} rimaste oggi, questa compresa: l'ultima verso le {ultima:%H:%M} UTC; poi niente chiamate fino "
                     f"a mezzanotte UTC e l'operazione aperta resta solo con il suo stop e il suo obiettivo")
        if st.get("tetto_ieri"):
            testo += f"; ieri il tetto è finito alle {_hm_iso(st['tetto_ieri'])} UTC e non sei stato chiamato fino a mezzanotte"
        return testo

    def _salva_messaggio(self, ora: datetime, motivo: str, impronta: str, stabile: str, variabile: str, ris) -> None:
        """Il messaggio intero e il ragionamento restano sulla macchina, un file al giorno, fuori da git (punto 2.7)."""
        try:
            cartella = self.cartella_messaggi
            cartella.mkdir(parents=True, exist_ok=True)
            riga = {"ora": ora.isoformat(), "motivo": motivo, "impronta": impronta, "stabile": stabile, "variabile": variabile,
                    "stato": ris.stato}
            if ris.esito is not None:
                riga.update(pensiero=ris.esito.pensiero, durata_s=ris.esito.durata_s,
                            risposta=ris.esito.risposta.model_dump(exclude_none=True) if ris.esito.risposta else None)
            with open(cartella / f"{ora:%Y-%m-%d}.jsonl", "a") as f:
                f.write(json.dumps(riga, ensure_ascii=False) + "\n")
        except Exception as e:  # noqa: BLE001 - un disco pieno non deve fermare il trader
            self.evento(ora, "messaggio non salvato", errore=str(e)[:200])

    def _pulisci_messaggi(self, ora: datetime) -> None:
        limite = (ora - timedelta(days=GIORNI_MESSAGGI)).strftime("%Y-%m-%d")
        for f in self.cartella_messaggi.glob("*.jsonl"):
            if f.stem < limite:
                f.unlink(missing_ok=True)

    # --- pezzi -----------------------------------------------------------------------------------------------------
    def _conto(self, st: dict, s: dict, pos: Optional[dict]) -> Conto:
        a = st.get("aperta") or {}
        p = None
        if pos is not None:
            p = Posizione(pos["lato"], pos["quantita"], pos["entrata"], pos["leva"], a.get("stop") or 0.0, a.get("obiettivo"),
                          pos["liquidazione"])
        elif a.get("in_attesa"):                       # un ordine limite in attesa: non è una posizione (punto 2.1)
            p = Posizione(a["lato"], a["quantita"], a["entrata"], a["leva"], a["stop"], a.get("obiettivo"), in_attesa=True)
        return Conto(s["conto"], s["disponibile"], st["conto_mezzanotte"], p)

    def _esito(self, a: dict) -> Optional[dict]:
        """L'esito dell'ordine di apertura dal conto. Un errore di lettura si propaga: non vuol dire «mai eseguito» (revisione del
        26 novembre 2026, problema 189)."""
        return self.c.esito_ordine(a.get("cid"))

    def _esito_o_niente(self, a: dict) -> Optional[dict]:
        """L'esito quando serve solo a precisare (ora di esecuzione, spese, funding): senza, si stima."""
        try:
            return self._esito(a)
        except Exception:  # noqa: BLE001
            return None

    def _limite_sparito(self, st: dict, a: dict, ora: datetime, conto_ora: float, prezzo: float):
        """L'ordine limite non è più sul libro e la posizione letta prima non c'era. Si chiede l'esito e si RILEGGE la posizione:
        l'ordine può essersi eseguito fra la lettura delle posizioni e quella degli ordini (revisione del 26 novembre 2026,
        problema 188: prima si cancellava lo stop di una posizione appena aperta). Ritorna (posizione, come): la posizione se c'è,
        come si è chiusa se si è chiusa; (None, None) se l'ordine è stato annullato senza eseguirsi o se non si sa ancora (si
        riprova al passo dopo, senza toccare niente)."""
        try:
            esito = self._esito(a)
        except Exception as e:  # noqa: BLE001 - stato sconosciuto: niente annullamenti, si riprova
            self.evento(ora, "esito dell'ordine limite non letto: riprovo al passo dopo", errore=str(e)[:200])
            return None, None
        pos = next(({k: v for k, v in p.items() if k != "simbolo"} for p in self.c.posizioni_simbolo()), None)
        if pos is not None:
            self._eseguito(a, esito, ora, pos)
            self.evento(ora, "ordine limite eseguito", entrata=a["entrata"], eseguita=a["eseguita"])
            return pos, None
        stato = (esito or {}).get("stato")
        if stato in ("chiusa", "eseguito"):
            # eseguito e chiuso fra due controlli: prima spariva dalla memoria (punto 2.2 del controllo del 26 novembre)
            self._eseguito(a, esito, ora)
            self.evento(ora, "ordine limite eseguito e chiuso fra due controlli", entrata=a["entrata"])
            return None, self._registra_chiusura(st, a, conto_ora, prezzo, ora, esito)
        if stato in ("in_attesa", "aperta"):                              # letture che non tornano fra loro: si riprova
            self.evento(ora, "ordine limite: conto e ordini non tornano, riprovo al passo dopo", stato=stato)
            return None, None
        st["aperta"] = None
        self.c.annulla_tutto()                                            # niente stop o obiettivo rimasti senza posizione
        self.evento(ora, "ordine limite non più sul conto e mai eseguito")
        return None, None

    def _eseguito(self, a: dict, esito: Optional[dict], ora: datetime, pos: Optional[dict] = None) -> None:
        """L'ordine di apertura si è eseguito: entrata, ora, stop e obiettivo in vigore in quel momento, spese d'entrata e 1 R."""
        a["in_attesa"] = False
        a.pop("inviata", None)
        if pos is not None:
            a["entrata"] = pos["entrata"]
        elif esito and esito.get("entrata"):
            a["entrata"] = esito["entrata"]
        if esito and esito.get("quantita"):
            a["quantita"] = esito["quantita"]
        # l'ora vera dal conto; senza, l'ora di adesso (non l'inizio del passo: il modello può aver pensato minuti, revisione del
        # 26 novembre 2026, punto M2)
        a["eseguita"] = iso_da_ms(esito.get("eseguita_ms")) if esito and esito.get("eseguita_ms") else self.ora().isoformat()
        a["stop_iniziale"], a["obiettivo_iniziale"] = a.get("stop"), a.get("obiettivo")
        limite = a.get("tipo") == "limite"
        a["spese_entrata"] = (esito.get("spese_entrata") if esito and esito.get("spese_entrata") is not None
                              else spese_entrata(a["quantita"] * a["entrata"], limite))
        r = un_r(a["lato"], a["entrata"], a["quantita"], a.get("stop"), a["spese_entrata"], self.c.simbolo)
        a["R"] = round(r, 4) if r else None

    def _escursione(self, a: dict, chiusa_ms: Optional[int], ora: datetime):
        es = ms(a.get("eseguita"))
        if not es:
            return None
        fine = chiusa_ms or int(ora.timestamp() * 1000)
        n = min(1500, max(2, int((fine - es) / 60000) + 3))
        c1 = self.c.candele("1m", int(ora.timestamp() * 1000), n=n, inizio_ms=es - es % 60000)
        return escursione(c1, a["lato"], a["entrata"], es, chiusa_ms, a.get("tipo") == "limite")

    def _registra_chiusura(self, st: dict, a: dict, conto_ora: float, prezzo: float, ora: datetime,
                           esito: Optional[dict] = None) -> str:
        """Scrive l'operazione chiusa nella memoria con i dati del conto (uscita, ora, modo, spese, funding: punti 2.2 e 2.4 del
        controllo del 26 novembre); senza i dati del conto (conto demo), l'uscita è il prezzo di adesso, segnata come stimata."""
        if esito is None or esito.get("stato") != "chiusa":
            esito = self._esito_o_niente(a) or esito
        dati = esito if esito and esito.get("stato") == "chiusa" else None
        lungo = a["lato"] == "lungo"
        come_stop = tipo_di_stop(a.get("spostamenti") or [])
        if a.get("chiusa_da"):
            come = a["chiusa_da"]
        elif dati and dati.get("come") == "stop":
            come = come_stop
        elif dati and dati.get("come") in ("obiettivo", "liquidazione"):
            come = dati["come"]
        elif dati:
            come = dati.get("come") or "chiusa sul conto"
        elif a.get("stop") and (prezzo <= a["stop"] * 1.003 if lungo else prezzo >= a["stop"] * 0.997):
            come = come_stop
        elif a.get("obiettivo") and (prezzo >= a["obiettivo"] * 0.997 if lungo else prezzo <= a["obiettivo"] * 1.003):
            come = "obiettivo"
        else:
            come = "chiusa sul conto (stop, obiettivo o liquidazione)"
        chiusa_iso = iso_da_ms(dati["chiusa_ms"]) if dati and dati.get("chiusa_ms") else ora.isoformat()
        op = {"n": st.get("prossimo_n") or len(st["operazioni"]) + 1, "aperta": a["aperta"], "tipo": a.get("tipo"),
              "eseguita": a.get("eseguita"), "chiusa": chiusa_iso, "lato": a["lato"], "leva": a["leva"],
              "quantita": a.get("quantita"), "entrata": a["entrata"], "uscita": dati["uscita"] if dati else prezzo,
              "uscita_stimata": dati is None, "come": come, "stop_iniziale": a.get("stop_iniziale"),
              "obiettivo_iniziale": a.get("obiettivo_iniziale"), "spostamenti": a.get("spostamenti") or [],
              "atr15": a.get("atr15"), "motivo": a.get("motivo", ""), "approccio": a.get("approccio", ""),
              "margine": a.get("margine"), "giorno_prima": a.get("giorno_prima"), "mancava": a.get("mancava"),
              "ore_a_mezzanotte": a.get("ore_a_mezzanotte"), "rischio_pct": a.get("rischio_pct"), "nota": a.get("nota"),
              "inviato": a.get("inviato")}
        if dati:
            op.update(spese_entrata=dati.get("spese_entrata"), spese=round(dati.get("spese") or 0.0, 6),
                      funding=round(dati.get("funding") or 0.0, 6), risultato_prezzo=round(dati.get("risultato_prezzo") or 0.0, 6),
                      risultato=round(dati["netto"], 2))
        else:
            op["risultato"] = round(conto_ora - a["conto_prima"], 2)
        if a.get("R"):
            op["R"], op["r"] = a["R"], round(op["risultato"] / a["R"], 2)
            try:
                fav, contro = self._escursione(a, ms(chiusa_iso), ora) or (None, None)
                if fav is not None and a.get("quantita"):
                    op["favore_r"] = round(fav * a["quantita"] / a["R"], 2)
                    op["contro_r"] = round(contro * a["quantita"] / a["R"], 2)
            except Exception as e:  # noqa: BLE001 - la scheda resta senza quella misura
                self.evento(ora, "escursione non calcolata", errore=str(e)[:200])
        st["operazioni"] = (st["operazioni"] + [op])[-200:]
        st["prossimo_n"] = op["n"] + 1
        for lez in st.get("lezioni", []):                                 # le lezioni entrano nella memoria stabile
            lez["fissata"] = True
        st["aperta"] = None
        self.c.annulla_tutto()                        # l'altro ordine condizionato (stop o obiettivo) non serve più
        self.evento(ora, "operazione chiusa", **{k: v for k, v in op.items() if k not in ("motivo", "spostamenti")})
        return come

    def _ripara_memoria(self, st: dict, ora: datetime) -> None:
        """Una volta sola: ricostruisce dal conto simulato e dal diario la memoria scritta prima del 26 novembre 2026, con le
        uscite vere, l'operazione che mancava e i perché dei cambi di approccio (ripara.py); rifà i resoconti dei giorni passati.
        Se il conto non si legge si riprova ai passi dopo (al massimo 5 volte: revisione del 26 novembre 2026, problema 190)."""
        st.pop("oi", None)
        st.setdefault("lezioni", [])
        storia = None
        if hasattr(self.c, "storia"):
            try:
                storia = self.c.storia()
            except Exception as e:  # noqa: BLE001
                st["tentativi_ripara"] = st.get("tentativi_ripara", 0) + 1
                if st["tentativi_ripara"] < 5:
                    self.evento(ora, "memoria non ricostruita: conto non letto, riprovo al passo dopo", errore=str(e)[:200])
                    return
                self.evento(ora, "memoria non ricostruita: conto non letto 5 volte, rinuncio", errore=str(e)[:200])
        st["versione_memoria"] = VERSIONE_MEMORIA
        st.pop("tentativi_ripara", None)
        try:
            diario = [json.loads(x) for x in self.diario.read_text().splitlines() if x.strip()] if self.diario.exists() else []
            ops, rapporto = ricostruisci(st.get("operazioni") or [], storia, diario, self.c.simbolo)
        except Exception as e:  # noqa: BLE001 - la memoria resta com'era (numerata), senza riprovare a ogni passo
            ops = st.get("operazioni") or []
            for n, o in enumerate(ops, start=1):
                o.setdefault("n", n)
            st["prossimo_n"] = len(ops) + 1
            self.evento(ora, "memoria non ricostruita", motivo="conto e diario non tornano: la lascio com'era", errore=str(e)[:300])
            return
        for o in ops[-30:]:                                               # quanto il prezzo è andato a favore e contro
            if o.get("R") and o.get("eseguita") and o.get("quantita") and o.get("favore_r") is None:
                try:
                    fav, contro = self._escursione(o, ms(o["chiusa"]), ora) or (None, None)
                    if fav is not None:
                        o["favore_r"], o["contro_r"] = round(fav * o["quantita"] / o["R"], 2), round(contro * o["quantita"] / o["R"], 2)
                except Exception:  # noqa: BLE001
                    break
        st["operazioni"] = ops
        st["prossimo_n"] = len(ops) + 1
        if not st["lezioni"]:
            st["lezioni"] = lezioni_dal_diario(diario, ops)[-50:]
        self.evento(ora, "memoria ricostruita dal conto e dal diario (controllo del 26 novembre 2026)", **rapporto,
                    lezioni=len(st["lezioni"]))
        if not (rapporto["corrette"] or rapporto["aggiunte"]):
            return
        oggi = ora.strftime("%Y-%m-%d")
        for giorno in sorted({o["chiusa"][:10] for o in ops if o["chiusa"][:10] < oggi}):
            fine = st.get("conto_mezzanotte") if st.get("giorno") and giorno == _ieri(st["giorno"]) else None
            inizio = st["inizio"]["conto"] if st.get("inizio") and giorno == st["inizio"]["giorno"] else None
            self.resoconto(st, giorno, fine, None, conto_inizio=inizio, rifatto=True)

    def _chiudi_ora(self, st: dict, pos: dict, prezzo: float, ora: datetime, perche: str) -> str:
        """Chiude a mercato e registra; ritorna come si è chiusa. Il motivo del programma vale solo se la chiusura l'ha fatta lui:
        se nel frattempo lo stop o l'obiettivo l'avevano già chiusa, vale quello del conto (revisione del 26 novembre 2026, S5)."""
        if self.c.chiudi(pos, self._cid(ora, "x")):
            st["aperta"]["chiusa_da"] = perche
        return self._registra_chiusura(st, st["aperta"], self.c.saldo()["conto"], prezzo, ora)

    def _protezione(self, st: dict, pos: dict, prezzo: float, condizionati: list, ora: datetime) -> Optional[str]:
        """La posizione aperta deve avere il suo stop sul conto. Se manca: con il prezzo già oltre lo stop si chiude a mercato,
        altrimenti si rimette (e si rimette anche l'obiettivo, se c'era). Ritorna come si è chiusa, se si è chiusa."""
        a = st["aperta"]
        tick = self.c.filtri()["passo_prezzo"]
        stop_ok = any(str(o.get("clientAlgoId", "")).startswith("tais") for o in condizionati)
        if stop_ok:
            return self._obiettivo_sul_conto(st, a, pos, condizionati, tick, ora)
        stop = a.get("stop")
        lungo = pos["lato"] == "lungo"
        if not stop or (prezzo <= stop if lungo else prezzo >= stop):
            return self._chiudi_ora(st, pos, prezzo, ora, "chiusa: senza stop valido sul conto")
        try:
            self.c.condizionato(pos["lato"], "STOP_MARKET", arrotonda(stop, tick), self._cid(ora, "s"))
        except Exception as e:  # noqa: BLE001 - lo stop non si mette: la posizione non resta scoperta
            self.evento(ora, "stop rifiutato: chiudo a mercato", errore=str(e)[:200])
            return self._chiudi_ora(st, pos, prezzo, ora, "chiusa: stop rifiutato da Binance")
        self.evento(ora, "stop rimesso sul conto", stop=stop)
        return self._obiettivo_sul_conto(st, a, pos, condizionati, tick, ora)

    def _obiettivo_sul_conto(self, st: dict, a: dict, pos: dict, condizionati: list, tick: float,
                             ora: datetime) -> Optional[str]:
        """L'obiettivo va sul conto quando la posizione c'è (per un ordine limite: all'esecuzione). Se il prezzo l'ha già superato
        (l'ordine si è eseguito e il prezzo è andato oltre l'obiettivo prima del passo), si chiude a mercato: è l'obiettivo
        raggiunto (revisione del 26 novembre 2026, R7-03). Se il conto lo rifiuta per un altro motivo, l'obiettivo si toglie."""
        if a.get("obiettivo") and not any(str(o.get("clientAlgoId", "")).startswith("tait") for o in condizionati):
            try:
                self.c.condizionato(pos["lato"], "TAKE_PROFIT_MARKET", arrotonda(a["obiettivo"], tick), self._cid(ora, "t"))
                self.evento(ora, "obiettivo messo sul conto", obiettivo=a["obiettivo"])
            except Exception as e:  # noqa: BLE001
                prezzo = self.c.mercato()["prezzo"]
                if prezzo >= a["obiettivo"] if pos["lato"] == "lungo" else prezzo <= a["obiettivo"]:
                    self.evento(ora, "obiettivo già superato: chiudo a mercato", obiettivo=a["obiettivo"], prezzo=prezzo)
                    return self._chiudi_ora(st, pos, prezzo, ora, "obiettivo")
                a["obiettivo"] = None                  # non si riprova a ogni passo; il modello lo vede nel conto
                self.evento(ora, "obiettivo rifiutato", errore=str(e)[:200])
        return None

    def _esegui(self, st: dict, r, pos: Optional[dict], s: dict, ora: datetime, atr15: Optional[float] = None) -> None:
        if self.fermo_a_mano():
            raise Scartata("il proprietario ha fermato il trader")
        posizioni = self.c.posizioni_tutte()
        motivo = self.estraneo(st, posizioni, self.c.ordini_tutti(), modo=False)
        if motivo:
            raise Scartata(f"il conto non è solo del trader: {motivo}")
        # la posizione si rilegge adesso: mentre il modello pensava (anche minuti) un ordine limite può essersi eseguito, e
        # un'operazione può essersi chiusa (problema 133; controllo del 26 novembre 2026, punto 2.2)
        pos = next(({k: v for k, v in p.items() if k != "simbolo"} for p in posizioni if p["simbolo"] == self.c.simbolo), None)
        a = st.get("aperta")
        if a and a.get("in_attesa") and pos is not None:
            self._eseguito(a, self._esito_o_niente(a), ora, pos)
            self.evento(ora, "ordine limite eseguito", entrata=a["entrata"], eseguita=a["eseguita"])
        elif a and a.get("in_attesa"):
            if not any(o.get("clientOrderId") == a.get("cid") for o in self.c.ordini_simbolo()):
                pos, come = self._limite_sparito(st, a, ora, self.c.saldo()["conto"], self.c.mercato()["prezzo"])
                if come:
                    st["richiama"] = f"operazione chiusa ({come})"
                    raise Scartata(f"mentre decidevi il tuo ordine limite si è eseguito ed è già stato chiuso ({come}): la "
                                   f"decisione non vale più; vieni richiamato subito")
                if pos is None and st.get("aperta") is None:
                    raise Scartata("mentre decidevi il tuo ordine limite è sparito senza eseguirsi: la decisione non vale più")
                if pos is None:
                    raise Scartata("lo stato del tuo ordine limite non si è potuto leggere: nessuna azione, riprovo dopo")
        elif a and pos is None:                       # la posizione si è chiusa mentre il modello pensava
            come = self._registra_chiusura(st, a, self.c.saldo()["conto"], self.c.mercato()["prezzo"], ora)
            st["richiama"] = f"operazione chiusa ({come})"
            raise Scartata(f"mentre decidevi la tua operazione si è chiusa ({come}): la decisione non vale più; vieni richiamato "
                           f"subito")
        f = self.c.filtri()
        tick = f["passo_prezzo"]
        prezzo = self.c.mercato()["prezzo"]                       # il prezzo è cambiato mentre il modello pensava
        scarto = controlla(r, self._conto(st, s, pos), prezzo)
        if scarto:
            raise Scartata(f"con il prezzo di adesso ({prezzo:.10g}) la decisione non vale più: {scarto}")
        if r.azione in ("apri_lungo", "apri_corto"):
            lato = "lungo" if r.azione == "apri_lungo" else "corto"
            leva = int(r.leva)
            limite = r.tipo_ordine == "limite"
            rif = r.prezzo_limite if limite else prezzo
            q = arrotonda(r.margine_usdt * leva / rif, f["passo_quantita_limite" if limite else "passo_quantita"])
            if q < f["quantita_min"] or q * rif < f["valore_min"]:
                raise Scartata(f"quantità {q:g} (valore {q * rif:.0f} USDT dopo l'arrotondamento per difetto al passo "
                               f"{f['passo_quantita_limite' if limite else 'passo_quantita']:g}) sotto il minimo del simbolo "
                               f"({f['quantita_min']:g} e {f['valore_min']:g} USDT): aumenta margine o leva")
            cid = self._cid(ora, "o")
            giorno_prima = s["conto"] - st["conto_mezzanotte"]
            obiettivo = obiettivo_usdt(Conto(s["conto"], s["disponibile"], st["conto_mezzanotte"]))
            rischio = un_r(lato, rif, q, r.stop_prezzo, spese_entrata(q * rif, limite), self.c.simbolo)
            # l'intenzione si salva PRIMA dell'invio: se la risposta si perde, al passo dopo l'ordine si riconosce dal nome
            st["aperta"] = {"aperta": ora.isoformat(), "tipo": "limite" if limite else "mercato", "lato": lato, "leva": leva,
                            "entrata": rif, "quantita": q, "cid": cid, "stop": r.stop_prezzo, "obiettivo": r.obiettivo_prezzo,
                            "spostamenti": [], "approccio": taglia(r.approccio, 250), "motivo": taglia(r.diario, 300),
                            "atr15": round(atr15, 4) if atr15 else None, "conto_prima": s["conto"], "margine": r.margine_usdt,
                            "giorno_prima": round(giorno_prima, 2), "mancava": round(obiettivo - giorno_prima, 2),
                            "ore_a_mezzanotte": round((mezzanotte_dopo(ora) - ora).total_seconds() / 3600, 1),
                            "rischio_pct": round(rischio / s["conto"] * 100, 2) if rischio and s["conto"] else None,
                            "in_attesa": limite, "inviata": not limite}
            self.salva(st)
            self.c.prepara(leva)
            if self.fermo_a_mano():
                st["aperta"] = None
                raise Scartata("il proprietario ha fermato il trader")
            st["aperta"]["inviato"] = self.ora().isoformat()
            esito = self.c.apri(lato, q, cid, "LIMIT" if limite else "MARKET", arrotonda(rif, tick) if limite else None)
            st["aperta"].pop("inviata", None)
            if limite and float(esito.get("executedQty") or 0) > 0:
                # un limite già oltre il prezzo si esegue subito a mercato: da qui è un'operazione a mercato, con lo stop messo
                # subito e la chiusura se il conto lo rifiuta (revisione del 26 novembre 2026, problema 193); un resto non
                # eseguito (solo sul conto demo) si annulla prima di mettere lo stop
                if float(esito.get("executedQty") or 0) < q:
                    self.c.annulla_tutto()
                limite = False
                st["aperta"].update(tipo="mercato", in_attesa=False, nota="limite già oltre il prezzo: eseguito subito a mercato")
                self.evento(ora, "ordine limite eseguito subito a mercato (era già oltre il prezzo)")
            if self.fermo_a_mano():                    # «chiudi» è arrivato mentre l'ordine partiva: si richiude subito
                if limite:
                    self._annulla_limite(st, prezzo, ora, "ordine limite annullato: fermo a mano")
                else:
                    st["aperta"]["entrata"] = float(esito.get("avgPrice") or 0) or prezzo
                    self._eseguito(st["aperta"], None, ora)
                    self._chiudi_ora(st, {"lato": lato, "quantita": float(esito.get("executedQty") or q)}, prezzo, ora,
                                     "chiusa a mano dal proprietario")
                raise Scartata("il proprietario ha fermato il trader mentre l'ordine partiva: richiuso")
            if limite:                                 # stop subito: scatta solo quando la posizione c'è (da provare sul demo)
                try:
                    self.c.condizionato(lato, "STOP_MARKET", arrotonda(r.stop_prezzo, tick), self._cid(ora, "s"))
                except Exception as e:  # noqa: BLE001 - lo metterà la protezione appena l'ordine è eseguito
                    self.evento(ora, "stop dell'ordine limite non accettato prima dell'esecuzione", errore=str(e)[:200])
            if not limite:
                st["aperta"]["entrata"] = float(esito.get("avgPrice") or 0) or prezzo
                st["aperta"]["quantita"] = float(esito.get("executedQty") or q)
                self._eseguito(st["aperta"], self._esito_o_niente(st["aperta"]), ora)
                nuova = {"lato": lato, "quantita": st["aperta"]["quantita"]}
                try:
                    self.c.condizionato(lato, "STOP_MARKET", arrotonda(r.stop_prezzo, tick), self._cid(ora, "s"))
                except Exception as e:  # noqa: BLE001 - nessuna posizione senza stop: si chiude subito
                    self.evento(ora, "stop rifiutato dopo l'apertura: chiudo a mercato", errore=str(e)[:200])
                    st["richiama"] = f"operazione chiusa ({self._chiudi_ora(st, nuova, prezzo, ora, 'chiusa: stop rifiutato dal conto')})"
                    raise RuntimeError(f"stop rifiutato, operazione chiusa subito: {str(e)[:150]}") from None
                if r.obiettivo_prezzo:
                    try:
                        self.c.condizionato(lato, "TAKE_PROFIT_MARKET", arrotonda(r.obiettivo_prezzo, tick), self._cid(ora, "t"))
                    except Exception as e:  # noqa: BLE001
                        st["aperta"]["obiettivo"] = st["aperta"]["obiettivo_iniziale"] = None
                        self.evento(ora, "obiettivo rifiutato (lo stop c'è)", errore=str(e)[:200])
            self.evento(ora, "aperta", **{k: v for k, v in st["aperta"].items() if k not in ("conto_prima", "motivo")})
        elif r.azione == "chiudi":
            a = st.get("aperta") or {}
            n_prima = st.get("prossimo_n")
            if pos is None:                            # solo un ordine limite in attesa: si annulla
                self._annulla_limite(st, prezzo, ora, "ordine limite annullato da te")
                st["richiama"] = ("ordine limite annullato da te (nessuna operazione)" if st.get("prossimo_n") == n_prima
                                  else f"operazione chiusa ({st['operazioni'][-1]['come']})")
            else:
                if self.c.chiudi(pos, self._cid(ora, "x")):
                    a["chiusa_da"] = "chiusa da te"    # solo dopo la chiusura riuscita (revisione del 26 novembre, 192 e S5)
                # il modello si richiama subito anche dopo una chiusura sua (punto 2.10 del controllo del 26 novembre)
                st["richiama"] = f"operazione chiusa ({self._registra_chiusura(st, a, self.c.saldo()['conto'], prezzo, ora)})"
        elif r.azione == "modifica":
            a = st.get("aperta") or {}
            condizionati = [o for o in self.c.ordini_tutti() if o["_algo"]]
            # con l'ordine limite in attesa la posizione non c'è ancora, ma stop e obiettivo sul conto sì
            bersaglio = pos if pos is not None else {"lato": a["lato"], "quantita": a["quantita"], "in_attesa": True}
            n_prima = st.get("prossimo_n")
            for campo, tipo, sigla, valore in (("stop", "STOP_MARKET", "s", r.stop_prezzo),
                                               ("obiettivo", "TAKE_PROFIT_MARKET", "t", r.obiettivo_prezzo)):
                if valore is None:
                    continue
                vecchio = a.get(campo)
                if not (campo == "obiettivo" and a.get("in_attesa")):
                    # l'obiettivo di un limite in attesa sta solo nello stato: va sul conto all'esecuzione (R7-03)
                    vecchi = [o for o in condizionati if str(o.get("clientAlgoId", "")).startswith("tai" + sigla)]
                    self._sostituisci(st, a, bersaglio, prezzo, ora, campo, tipo, sigla, valore, vecchi, tick)
                if st.get("aperta") is None:           # chiusa (o limite annullato) perché nessuno stop è stato accettato
                    st["richiama"] = (f"operazione chiusa ({st['operazioni'][-1]['come']})" if st.get("prossimo_n") != n_prima
                                      else "ordine limite annullato: nessuno stop accettato dal conto (nessuna operazione)")
                    return
                a[campo] = valore
                if vecchio is None or abs(valore - vecchio) > 1e-9:
                    a.setdefault("spostamenti", []).append({"ora": ora.isoformat(), "campo": campo, "da": vecchio, "a": valore,
                                                            "prima_dell_esecuzione": bool(a.get("in_attesa"))})
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
        a.setdefault("quantita", rimasta["quantita"])
        self._eseguito(a, self._esito_o_niente(a), ora, rimasta)
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

    def resoconto(self, st: dict, giorno: str, conto_fine: Optional[float] = None, prezzo_fine: Optional[float] = None,
                  conto_inizio: Optional[float] = None, rifatto: bool = False) -> Path:
        """Il resoconto del giorno per il proprietario (REGOLE.md, sezione 7; controllo del 26 novembre 2026, punto 2.6): il risultato
        dal conto (non dalla somma delle operazioni), la discesa massima, il costo delle chiamate, BTC negli stessi orari, le uscite
        per tipo e ogni apertura con il suo rischio. Al modello non va niente di questo."""
        ops = [o for o in st["operazioni"] if str(o.get("chiusa", "")).startswith(giorno)]
        spesa = self.budget.speso(datetime.fromisoformat(giorno + "T12:00:00+00:00"))
        corrente = not rifatto
        if conto_inizio is None and corrente:
            conto_inizio = st.get("conto_mezzanotte")
        g = (st.get("stat_giorno") or {}) if corrente else {}

        def soldi(x):
            return "non registrato" if x is None else f"{x:.2f}"
        righe = [f"# Trader AI, {giorno} (UTC)", ""]
        if rifatto:
            righe += ["Rifatto il 26 novembre 2026 dopo la ricostruzione della memoria dal conto simulato (controllo del 26 novembre: "
                      "uscite vere e un'operazione che mancava). I numeri che il programma non aveva salvato sono «non registrato».",
                      ""]
        risultato = (conto_fine - conto_inizio) if conto_fine is not None and conto_inizio is not None else None
        if risultato is not None:
            righe.append(f"* Conto: da {conto_inizio:.2f} a {conto_fine:.2f} USDT, {risultato:+.2f} ({risultato / conto_inizio * 100:+.2f}%); "
                         f"togliendo il costo delle chiamate ({spesa:.2f} dollari): {risultato - spesa:+.2f}")
        else:
            righe.append(f"* Conto: a inizio giorno {soldi(conto_inizio)}, a fine giorno {soldi(conto_fine)} USDT; costo delle "
                         f"chiamate {spesa:.2f} dollari")
        if conto_inizio:
            obiettivo = conto_inizio * 0.03
            raggiunto = f"raggiunto alle {_hm_iso(st['obiettivo_ora'])} UTC" if corrente and st.get("obiettivo_ora") else "non raggiunto"
            righe.append(f"* Obiettivo del 3% ({obiettivo:.2f} USDT): {raggiunto}")
        if corrente:
            dalle = st.get("discesa_dalle")
            da = f", misurata dalle {_hm_iso(dalle)} UTC" if dalle and not dalle.startswith(giorno + "T00:0") else ""
            righe.append(f"* Discesa massima nel giorno (dal punto più alto del conto{da}): {st.get('discesa_max_giorno', 0.0):.2f} "
                         f"USDT")
            p0 = st.get("prezzo_inizio_giorno")
            if p0 and prezzo_fine:
                righe.append(f"* {self.c.simbolo} negli stessi orari, tenuto senza fare niente: da {p0:g} a {prezzo_fine:g} "
                             f"({(prezzo_fine / p0 - 1) * 100:+.2f}%)")
        b = bilancio(ops)
        if ops:
            dettaglio = (f" (prezzo {b['prezzo']:+.2f}, spese {-b['spese']:+.2f}, funding {b['funding']:+.2f})"
                         if b["con_dettaglio"] else "")
            durata = f"; durata mediana {b['durata_mediana']:.0f} min" if b["durata_mediana"] is not None else ""
            uscite = ", ".join(f"{k} {v}" for k, v in b["uscite"].items() if v)
            righe.append(f"* Operazioni chiuse: {b['n']} (vinte {b['vinte']}, perse {b['perse']}), netto {b['netto']:+.2f}{dettaglio}; "
                         f"uscite: {uscite}{durata}")
            perdita = [o for o in ops if (o.get("giorno_prima") or 0) < 0]
            guadagno = [o for o in ops if (o.get("giorno_prima") or 0) > 0]

            def media(xs, k):
                v = [o.get(k) for o in xs if o.get(k) is not None]
                return f"{sum(v) / len(v):.1f}" if v else "-"
            if any(o.get("giorno_prima") is not None for o in ops):
                    righe.append(f"* Aperture con il giorno in perdita: {len(perdita)} (leva media {media(perdita, 'leva')}, margine medio "
                             f"{media(perdita, 'margine')}, rischio medio {media(perdita, 'rischio_pct')}% del conto); con il "
                             f"giorno in guadagno: {len(guadagno)} (leva media {media(guadagno, 'leva')}, margine medio "
                             f"{media(guadagno, 'margine')}, rischio medio {media(guadagno, 'rischio_pct')}%)")
        else:
            righe.append("* Operazioni chiuse: nessuna")
        ini = st.get("inizio") or {}
        if conto_fine is not None and ini.get("conto"):
            righe.append(f"* Dall'inizio della prova ({ini.get('giorno')}, {ini['conto']:.0f} USDT): {conto_fine - ini['conto']:+.2f}")
        if g.get("chiamate"):
            esiti = ", ".join(f"{k} {v}" for k, v in sorted(g.get("esiti", {}).items()))
            righe.append(f"* Chiamate al modello: {g['chiamate']} (costo medio {g['costo'] / g['chiamate']:.3f} dollari, durata media "
                         f"{g.get('durata_tot', 0) / g['chiamate']:.0f} s e massima {g.get('durata_max', 0):.0f} s, token in uscita "
                         f"in media {g.get('uscita_tot', 0) / g['chiamate']:.0f}); esiti: {esiti}; cambi di approccio dichiarati "
                         f"{g.get('cambi', 0)}")
        if corrente and st.get("tetto_dalle"):
            righe.append(f"* Tetto di spesa finito alle {_hm_iso(st['tetto_dalle'])} UTC: nessuna chiamata fino a mezzanotte")
        righe += ["", "| # | aperta | eseguita | chiusa | lato | leva | valore | rischio allo stop | entrata | uscita | come | netto | R | "
                      "mancava al 3% | ore a mezzanotte | approccio |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for o in ops:
            valore = f"{o['quantita'] * o['entrata']:.0f}" if o.get("quantita") else "-"
            rischio = f"{o['rischio_pct']:.2f}%" if o.get("rischio_pct") is not None else "-"
            r = f"{o['r']:+.2f}" if o.get("r") is not None else "-"
            mancava = f"{o['mancava']:.2f}" if o.get("mancava") is not None else "-"
            ore = f"{o['ore_a_mezzanotte']:.1f}" if o.get("ore_a_mezzanotte") is not None else "-"
            uscita = f"{o['uscita']:.1f}" + (" (stimata)" if o.get("uscita_stimata") else "") if o.get("uscita") else "-"
            righe.append(f"| {o.get('n', '-')} | {_hm_iso(o.get('aperta'))} | {_hm_iso(o.get('eseguita'))} | {_hm_iso(o.get('chiusa'))} | "
                         f"{o['lato']} | {o['leva']:g} | {valore} | {rischio} | {o['entrata']:.1f} | {uscita} | {o.get('come', '-')} | "
                         f"{o['risultato']:+.2f} | {r} | {mancava} | {ore} | {o.get('approccio', '')} |")
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
    trader = Trader(conto, lambda *_: None, messaggi=CARTELLA_MESSAGGI)
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
