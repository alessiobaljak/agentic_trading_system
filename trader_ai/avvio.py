"""Il programma del trader AI sulla macchina (REGOLE.md, versione 3). Gira sempre; ogni 30 secondi:

1. legge saldo, posizione e prezzo dal conto demo SUO;
2. a mezzanotte UTC scrive il resoconto del giorno finito e riparte dal conto di quel momento;
3. se l'operazione aperta si è chiusa (stop, obiettivo, liquidazione) la scrive nella memoria e chiama subito il modello;
4. se c'è una posizione senza stop sul conto, rimette lo stop del piano (protezione dopo un riavvio o un ordine limite eseguito);
5. a +50 USDT dalla mezzanotte chiude tutto e si ferma fino alla mezzanotte dopo;
6. a ogni candela da 15 minuti chiusa chiama il modello (se il tetto di spesa lo permette) ed esegue la decisione accettata.

    python -m trader_ai.avvio controlla   # prova del collegamento: prezzo, saldo, posizione; nessun ordine, nessuna chiamata
    python -m trader_ai.avvio gira        # il servizio
"""
from __future__ import annotations

import json
import sys
import time
import traceback
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional

from trader_ai import sveglia
from trader_ai.conto_demo import ContoDemo, arrotonda, controlla_chiavi
from trader_ai.costi import Budget, costo_massimo
from trader_ai.giro import decidi
from trader_ai.limiti import Conto, Posizione, obiettivo_raggiunto
from trader_ai.messaggio import blocco_memoria, costruisci
from trader_ai.modello import Esito, chiama, crea_client

CARTELLA = Path(__file__).with_name("avanti")
CONFIG = Path(__file__).with_name("config.json")
INTERVALLI = ("5m", "15m", "30m")
PAUSA_S = 30


def mezzanotte_dopo(ora: datetime) -> datetime:
    return (ora + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)


class Trader:
    def __init__(self, conto: ContoDemo, chiama_modello: Callable[[str, str], Esito], cartella: Path = CARTELLA,
                 ora: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> None:
        self.c, self.chiama, self.cartella, self.ora = conto, chiama_modello, Path(cartella), ora
        self.f_stato = self.cartella / "stato.json"
        self.diario = self.cartella / "diario.jsonl"
        self.budget = Budget(self.cartella / "spesa.json")

    # --- stato -----------------------------------------------------------------------------------------------------
    def carica(self) -> dict:
        try:
            return json.loads(self.f_stato.read_text())
        except FileNotFoundError:
            return {"operazioni": [], "note": [], "oi": []}

    def salva(self, st: dict) -> None:
        self.cartella.mkdir(parents=True, exist_ok=True)
        tmp = self.f_stato.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, ensure_ascii=False, indent=1))
        tmp.replace(self.f_stato)

    def evento(self, ora: datetime, cosa: str, **altro) -> None:
        self.cartella.mkdir(parents=True, exist_ok=True)
        with open(self.diario, "a") as f:
            f.write(json.dumps({"ora": ora.isoformat(), "evento": cosa, **altro}, ensure_ascii=False) + "\n")

    # --- un passo --------------------------------------------------------------------------------------------------
    def passo(self) -> None:
        ora = self.ora()
        st = self.carica()
        s = self.c.saldo()
        pos = self.c.posizione()
        m = self.c.mercato()
        prezzo = m["prezzo"]
        giorno = ora.strftime("%Y-%m-%d")

        if st.get("giorno") != giorno:                                    # mezzanotte UTC
            if st.get("giorno"):
                self.resoconto(st, st["giorno"])
            st.update(giorno=giorno, conto_mezzanotte=s["conto"], fermo_fino=None)
            self.evento(ora, "giorno nuovo", conto=s["conto"])

        chiusa = None
        aperta = st.get("aperta")
        if aperta and pos is None and not aperta.get("in_attesa"):         # l'operazione si è chiusa sul conto
            chiusa = self._registra_chiusura(st, aperta, s["conto"], prezzo, ora)
        if aperta and aperta.get("in_attesa") and pos is not None:         # ordine limite eseguito
            aperta.update(in_attesa=False, entrata=pos["entrata"])
        if pos is not None:
            self._protezione(st, pos, ora)

        st["oi"] = [x for x in st.get("oi", []) if x[0] > (ora - timedelta(hours=2)).timestamp()]
        st["oi"].append([ora.timestamp(), m["interesse_aperto"]])

        if st.get("fermo_fino") and ora < datetime.fromisoformat(st["fermo_fino"]):
            self.salva(st)
            return
        conto = self._conto(st, s, pos)
        if obiettivo_raggiunto(conto):
            self.c.chiudi(pos)
            st["aperta"] = None
            st["fermo_fino"] = mezzanotte_dopo(ora).isoformat()
            self.evento(ora, "obiettivo del giorno raggiunto: chiuso tutto, fermo fino a mezzanotte UTC",
                        conto=s["conto"], guadagno=round(s["conto"] - st["conto_mezzanotte"], 2))
            self.salva(st)
            return

        motivo = sveglia.motivo(ora, datetime.fromisoformat(st["ultima"]) if st.get("ultima") else None, chiusa)
        if motivo is None:
            self.salva(st)
            return
        ora_ms = int(ora.timestamp() * 1000)
        candele = {tf: self.c.candele(tf, ora_ms) for tf in INTERVALLI}
        mercato = {"prezzo": prezzo, "funding": m["funding"],
                   "minuti_al_prossimo_funding": round((m["prossimo_funding_ms"] - ora_ms) / 60000),
                   "interesse_aperto": m["interesse_aperto"], "interesse_aperto_var_1h_pct": self._oi_1h(st, ora)}
        memoria = blocco_memoria(st["operazioni"], st.get("approccio"), st["note"], st.get("ultimo_scarto"))
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
        if ris.accettata is not None:
            try:
                self._esegui(st, ris.accettata, pos, prezzo, s, ora)
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
        if a.get("chiusa_da_modello"):
            come = "chiusa dal modello"
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

    def _protezione(self, st: dict, pos: dict, ora: datetime) -> None:
        """Una posizione aperta deve avere lo stop sul conto: se manca, si rimette quello del piano (o, senza piano, uno al
        limite della liquidazione) e lo si scrive nel diario."""
        a = st.get("aperta")
        if not a:
            a = st["aperta"] = {"aperta": ora.isoformat(), "lato": pos["lato"], "leva": pos["leva"], "entrata": pos["entrata"],
                                "quantita": pos["quantita"], "stop": None, "obiettivo": None, "approccio": "",
                                "conto_prima": st.get("conto_mezzanotte", 0.0), "margine": None}
            self.evento(ora, "posizione trovata sul conto senza piano")
        tipi = {o.get("orderType") or o.get("type") for o in self.c.ordini_condizionati()}
        if "STOP_MARKET" in tipi:
            return
        stop = a.get("stop")
        if not stop:
            dist = 0.9 / max(pos["leva"], 1)
            stop = pos["entrata"] * (1 - dist if pos["lato"] == "lungo" else 1 + dist)
            a["stop"] = stop
        f = self.c.filtri()
        self.c.condizionato(pos["lato"], "STOP_MARKET", arrotonda(stop, f["passo_prezzo"]))
        if a.get("obiettivo") and "TAKE_PROFIT_MARKET" not in tipi:
            self.c.condizionato(pos["lato"], "TAKE_PROFIT_MARKET", arrotonda(a["obiettivo"], f["passo_prezzo"]))
        self.evento(ora, "stop rimesso sul conto", stop=stop)

    def _esegui(self, st: dict, r, pos: Optional[dict], prezzo: float, s: dict, ora: datetime) -> None:
        f = self.c.filtri()
        tick = f["passo_prezzo"]
        if r.azione in ("apri_lungo", "apri_corto"):
            lato = "lungo" if r.azione == "apri_lungo" else "corto"
            leva = int(r.leva)
            rif = r.prezzo_limite if r.tipo_ordine == "limite" else prezzo
            q = arrotonda(r.margine_usdt * leva / rif, f["passo_quantita"])
            if q < f["quantita_min"] or q * rif < max(f["valore_min"], 0):
                raise RuntimeError(f"quantità {q} sotto i minimi del simbolo")
            self.c.prepara(leva)
            limite = r.tipo_ordine == "limite"
            esito = self.c.apri(lato, q, "LIMIT" if limite else "MARKET", arrotonda(rif, tick) if limite else None)
            entrata = float(esito.get("avgPrice") or 0) or rif
            st["aperta"] = {"aperta": ora.isoformat(), "lato": lato, "leva": leva, "entrata": entrata, "quantita": q,
                            "stop": r.stop_prezzo, "obiettivo": r.obiettivo_prezzo, "approccio": r.approccio,
                            "conto_prima": s["conto"], "margine": r.margine_usdt, "in_attesa": limite}
            if not limite:                             # per un limite, stop e obiettivo arrivano quando è eseguito (_protezione)
                self.c.condizionato(lato, "STOP_MARKET", arrotonda(r.stop_prezzo, tick))
                if r.obiettivo_prezzo:
                    self.c.condizionato(lato, "TAKE_PROFIT_MARKET", arrotonda(r.obiettivo_prezzo, tick))
            self.evento(ora, "aperta", **{k: v for k, v in st["aperta"].items() if k != "conto_prima"})
        elif r.azione == "chiudi":
            a = st.get("aperta") or {}
            if pos is None:                            # solo un ordine limite in attesa: si annulla
                self.c.annulla_tutto()
                st["aperta"] = None
                self.evento(ora, "ordine limite annullato")
            else:
                a["chiusa_da_modello"] = True
                self.c.chiudi(pos)
                if a:
                    self._registra_chiusura(st, a, self.c.saldo()["conto"], prezzo, ora)
        elif r.azione == "modifica":
            a = st.get("aperta") or {}
            vecchi = self.c.ordini_condizionati() if pos is not None else []
            for campo, tipo, valore in (("stop", "STOP_MARKET", r.stop_prezzo),
                                        ("obiettivo", "TAKE_PROFIT_MARKET", r.obiettivo_prezzo)):
                if valore is None:
                    continue
                if pos is not None:                    # prima il nuovo, poi si tolgono i vecchi dello stesso tipo
                    self.c.condizionato(pos["lato"], tipo, arrotonda(valore, tick))
                    for o in vecchi:
                        if (o.get("orderType") or o.get("type")) == tipo:
                            self.c.annulla_condizionato(o["algoId"])
                a[campo] = valore
            self.evento(ora, "modificata", stop=a.get("stop"), obiettivo=a.get("obiettivo"))

    def resoconto(self, st: dict, giorno: str) -> Path:
        ops = [o for o in st["operazioni"] if o["chiusa"].startswith(giorno)]
        spesa = self.budget.speso(datetime.fromisoformat(giorno + "T12:00:00+00:00"))
        guadagno = sum(o["risultato"] for o in ops)
        righe = [f"# Trader AI, {giorno} (UTC)", "",
                 f"* Conto a mezzanotte: {st.get('conto_mezzanotte', 0):.2f} USDT; risultato delle operazioni chiuse: "
                 f"{guadagno:+.2f} USDT; obiettivo dei 50: {'sì' if st.get('fermo_fino') else 'no'}",
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


def main(argv: list) -> int:
    cfg = json.loads(CONFIG.read_text())
    chiave, segreto = controlla_chiavi()
    conto = ContoDemo(chiave, segreto, cfg["moneta"])
    comando = argv[1] if len(argv) > 1 else "controlla"
    if comando == "controlla":
        m, s, p = conto.mercato(), conto.saldo(), conto.posizione()
        print(f"[trader_ai] {cfg['moneta']} prezzo {m['prezzo']}; conto {s['conto']:.2f} USDT, disponibile "
              f"{s['disponibile']:.2f}; posizione {p}")
        return 0
    if comando != "gira":
        print("uso: python -m trader_ai.avvio controlla|gira")
        return 2
    client = crea_client()
    trader = Trader(conto, lambda system, utente: chiama(client, system, utente))
    print(f"[trader_ai] acceso su {cfg['moneta']}", flush=True)
    while True:
        try:
            trader.passo()
        except Exception:  # noqa: BLE001 - un errore non ferma il servizio: si scrive e si riprova
            print("[trader_ai] errore nel passo:\n" + traceback.format_exc()[-1500:], flush=True)
        time.sleep(PAUSA_S)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
