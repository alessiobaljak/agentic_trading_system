"""Il paper di N3 ed E4 eseguito dal bot (docs/backlog.md, P16): le due strategie a eventi del programma 6.

* **N3** (research/programma6/TRENTESIMA.md, TRENTADUESIMA.md; paper di ricerca, REGOLE.md sezione 11): ogni giorno alle
  00:05 UTC, per i perpetui USDT-M che sono monete (`f5.contratti_monete`) al **7° giorno di vita** (il giorno della prima
  candela + 7) e con volume il giorno prima: short la moneta e long il Bitcoin per lo stesso valore, al prezzo mark. Uscita
  di protezione se la moneta sale del **30%** sopra l'entrata (si guarda ogni ora con le candele a 1 ora: massimo ≥ entrata ×
  1,30 → uscita al livello con l'1% di scarto, il Bitcoin alla chiusura di quell'ora), altrimenti dopo **30 giorni** alle
  00:05 UTC al prezzo mark.
* **E4** (VENTISEIESIMA.md; REGOLE.md sezione 9): ogni ora si legge `/fapi/v1/fundingInfo` (l'intervallo del funding dei
  simboli con i parametri cambiati; chi non c'e' ha 8 ore); quando l'intervallo di una moneta scende rispetto all'ultimo visto
  (il primo giro fa solo da base), si aspetta il primo regolamento al passo piu' corto e il segno del suo funding (se zero,
  quello prima, come `ventiseiesima.eventi`); se positivo: short la moneta e long il Bitcoin all'apertura del giorno UTC dopo
  (alle 00:05 al mark) per **7 giorni**, se il giorno dell'evento ha volume. Senza uscita di protezione (la regola non ce
  l'ha).
* Il **5%** del capitale per operazione (stesso valore sulle due gambe), al massimo **20** aperte fra le due; costi come la
  ricerca (`ventunesima.COSTO_MONETA`, `COSTO_BTC`) e il funding vero di ogni regolamento per le due gambe; il rendimento
  di un'operazione chiusa e' quello della ricerca: (Bitcoin uscita/entrata − 1) − (moneta uscita/entrata − 1) − costi +
  funding della moneta − funding del Bitcoin.

Capitale virtuale di 10.000 dollari, nessun ordine vero: non usa le chiavi e non chiama mai gli indirizzi degli ordini.
Acceso solo dal file `ops/paper_eventi_acceso` (un interruttore suo, fuori dal kill switch del vecchio paper); lo stato sta
in `data/paper_eventi.json` sulla macchina e su RTDB in `/paper_eventi`. Il paper di ricerca resta quello che decide i
verdetti di N3 ed E4.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Callable

from bot.portafoglio.f5 import GIORNO_MS, _chiedi_http, contratti_monete, in_chiusura

RADICE = Path(__file__).resolve().parents[2]
INTERRUTTORE = RADICE / "ops" / "paper_eventi_acceso"
FILE_STATO = RADICE / "data" / "paper_eventi.json"
CAPITALE, QUOTA, MAX_APERTE = 10_000.0, 0.05, 20
TAKER = 0.0005
COSTO_MONETA, COSTO_BTC = 2 * (TAKER + 0.0010), 2 * (TAKER + 0.0001)      # come ventunesima
ETA, GIORNI_N3, STOP, SCARTO_STOP = 7, 30, 0.30, 0.01                    # come trentesima
GIORNI_E4, INTERVALLO_BASE = 7, 8
ORA_GIORNALIERO_S = 300          # 00:05 UTC
OGNI_ORA_S = 3600
ATTESA_DOPO_ERRORE_S = 1800
ATTESA_E4_MAX_MS = 2 * GIORNO_MS  # un cambio d'intervallo senza un regolamento al passo nuovo entro 2 giorni si lascia
ORA_MS = 3_600_000


def rendimento(p0: float, pc: float, b0: float, pb: float, fc: float, fb: float) -> float:
    """Short la moneta e long il Bitcoin (come `trentesima.operazione` e `ventunesima.rendimento`)."""
    return (pb / b0 - 1) - (pc / p0 - 1) - COSTO_MONETA - COSTO_BTC + fc - fb


def primo_passo_corto(regolamenti: list) -> tuple:
    """(ms, segno) del primo regolamento a un intervallo piu' corto del precedente, dai regolamenti in ordine di tempo
    [(ms, tasso)]; (None, 0) se non c'e' ancora. Il segno e' quello del suo funding, o del precedente se e' zero."""
    for k in range(2, len(regolamenti)):
        prima = round((regolamenti[k - 1][0] - regolamenti[k - 2][0]) / ORA_MS)
        dopo = round((regolamenti[k][0] - regolamenti[k - 1][0]) / ORA_MS)
        if 0 < dopo < prima:
            tasso = regolamenti[k][1] if regolamenti[k][1] != 0 else regolamenti[k - 1][1]
            return int(regolamenti[k][0]), (1 if tasso > 0 else (-1 if tasso < 0 else 0))
    return None, 0


class PaperEventi:
    def __init__(self, fb, chiedi: Callable = _chiedi_http, file_stato: Path = FILE_STATO,
                 interruttore: Path = INTERRUTTORE, pausa_s: float = 0.1) -> None:
        self.fb = fb
        self.chiedi = chiedi
        self.file_stato = Path(file_stato)
        self.interruttore = Path(interruttore)
        self.pausa_s = pausa_s
        self._ultimo_tentativo = 0.0

    # ---- stato ----
    def acceso(self) -> bool:
        # durante i test l'interruttore vero del repo non conta: il ciclo del bot nei test non deve chiamare Binance
        if self.interruttore == INTERRUTTORE and os.environ.get("PYTEST_CURRENT_TEST"):
            return False
        return self.interruttore.exists()

    def carica(self) -> dict:
        try:
            return json.loads(self.file_stato.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            st = self.fb.get_rtdb("/paper_eventi/stato_interno") if self.fb is not None else None
            return dict(st) if isinstance(st, dict) else {}

    def salva(self, st: dict) -> None:
        self.file_stato.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.file_stato.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.file_stato)
        if self.fb is not None:
            self.fb.set_rtdb("/paper_eventi/stato_interno", st)

    @staticmethod
    def nuovo(now: float) -> dict:
        # si parte dal giorno dopo: le entrate delle 00:05 di oggi sono gia' passate
        return {"inizio": now, "equity_realizzata": CAPITALE, "aperte": {}, "chiuse_n": 0, "chiuse_somma_r": 0.0,
                "intervalli": {}, "e4_base_fatta": False, "e4_attese": [], "e4_eventi": [],
                "ultimo_giorno": int(now // 86400), "ultimo_orario": 0.0}

    # ---- il giro ----
    def tick(self, now: float) -> None:
        if not self.acceso():
            return
        st = self.carica() or self.nuovo(now)
        if now - self._ultimo_tentativo < ATTESA_DOPO_ERRORE_S:
            return
        giorno = int(now // 86400)
        if giorno > int(st.get("ultimo_giorno", 0)) and now >= giorno * 86400 + ORA_GIORNALIERO_S:
            if not self.giornaliero(giorno, now, st):
                self._ultimo_tentativo = now
                return
        if now - float(st.get("ultimo_orario", 0)) >= OGNI_ORA_S:
            if not self.orario(now, st):
                self._ultimo_tentativo = now

    # ---- dati di Binance ----
    def _mark(self) -> dict:
        dati = self.chiedi("/fapi/v1/premiumIndex", {}) or []
        return {x["symbol"]: float(x["markPrice"]) for x in dati if isinstance(x, dict) and float(x.get("markPrice") or 0) > 0}

    def _regolamenti(self, simbolo: str, da_ms: int, limite: int = 1000) -> list:
        f = self.chiedi("/fapi/v1/fundingRate", {"symbol": simbolo, "startTime": int(da_ms), "limit": limite}) or []
        time.sleep(self.pausa_s)
        return sorted((int(x["fundingTime"]), float(x["fundingRate"])) for x in f)

    def _ore(self, simbolo: str, da_ms: int) -> list:
        k = self.chiedi("/fapi/v1/klines", {"symbol": simbolo, "interval": "1h", "startTime": int(da_ms), "limit": 1000}) or []
        time.sleep(self.pausa_s)
        return [(int(r[0]), float(r[2]), float(r[4])) for r in k]          # (apertura ms, massimo, chiusura)

    def _volume_del_giorno(self, simbolo: str, giorno: int) -> float:
        k = self.chiedi("/fapi/v1/klines", {"symbol": simbolo, "interval": "1d", "startTime": giorno * GIORNO_MS,
                                            "limit": 1}) or []
        time.sleep(self.pausa_s)
        return float(k[0][7]) if k and int(k[0][0]) // GIORNO_MS == giorno else 0.0

    # ---- operazioni ----
    def _funding(self, st: dict, now: float) -> None:
        """Il funding dei regolamenti dall'ultimo controllo, per le due gambe di ogni operazione aperta (tassi sommati,
        come la ricerca: lo short incassa quello della moneta, il long paga quello del Bitcoin)."""
        aperte = st.get("aperte") or {}
        if not aperte:
            return
        adesso_ms = int(now * 1000)
        da = min(int(p["funding_fino_ms"]) for p in aperte.values())
        btc = self._regolamenti("BTCUSDT", da + 1)
        for p in aperte.values():
            f0 = int(p["funding_fino_ms"])
            p["fb"] = float(p["fb"]) + sum(r for t, r in btc if f0 < t <= adesso_ms)
            p["fc"] = float(p["fc"]) + sum(r for t, r in self._regolamenti(p["simbolo"], f0 + 1) if f0 < t <= adesso_ms)
            p["funding_fino_ms"] = adesso_ms

    def apri(self, st: dict, tipo: str, simbolo: str, giorno: int, now: float, mark: dict) -> bool:
        aperte = st.setdefault("aperte", {})
        if len(aperte) >= MAX_APERTE or simbolo not in mark or "BTCUSDT" not in mark:
            return False
        if any(p["simbolo"] == simbolo and p["tipo"] == tipo for p in aperte.values()):
            return False
        ident = f"{tipo}-{simbolo}-{time.strftime('%Y%m%d', time.gmtime(giorno * 86400))}"
        adesso_ms = int(now * 1000)
        aperte[ident] = {"tipo": tipo, "simbolo": simbolo, "giorno_entrata": giorno, "entrata_ms": adesso_ms,
                         "p0": mark[simbolo], "b0": mark["BTCUSDT"], "quota": QUOTA * float(st["equity_realizzata"]),
                         "fc": 0.0, "fb": 0.0, "funding_fino_ms": adesso_ms,
                         "uscita_giorno": giorno + (GIORNI_N3 if tipo == "N3" else GIORNI_E4),
                         "ore_fino_ms": (adesso_ms // ORA_MS) * ORA_MS}
        print(f"[paper_eventi] aperta {ident}: short a {mark[simbolo]}, long BTC a {mark['BTCUSDT']}")
        return True

    def chiudi(self, st: dict, ident: str, pc: float, pb: float, motivo: str, now: float) -> float:
        p = st["aperte"].pop(ident)
        r = rendimento(float(p["p0"]), pc, float(p["b0"]), pb, float(p["fc"]), float(p["fb"]))
        usd = float(p["quota"]) * r
        st["equity_realizzata"] = float(st["equity_realizzata"]) + usd
        st["chiuse_n"] = int(st.get("chiuse_n", 0)) + 1
        st["chiuse_somma_r"] = float(st.get("chiuse_somma_r", 0.0)) + r
        if self.fb is not None:
            self.fb.set_rtdb(f"/paper_eventi/chiuse/{ident}", {
                "tipo": p["tipo"], "simbolo": p["simbolo"], "entrata": p["entrata_ms"], "uscita": int(now * 1000),
                "p0": p["p0"], "pc": pc, "b0": p["b0"], "pb": pb, "funding_moneta": p["fc"], "funding_btc": p["fb"],
                "rendimento": r, "dollari": usd, "motivo": motivo})
        print(f"[paper_eventi] chiusa {ident} ({motivo}): {100 * r:+.2f}% ({usd:+.2f} $)")
        return r

    # ---- ogni ora: E4 e le uscite di protezione di N3 ----
    def orario(self, now: float, st: dict) -> bool:
        mark = self._mark()
        info = self.chiedi("/fapi/v1/fundingInfo", {})
        if not mark or info is None:
            return False
        adesso_ms = int(now * 1000)
        attuali = {x["symbol"]: int(x["fundingIntervalHours"]) for x in info
                   if isinstance(x, dict) and x.get("fundingIntervalHours") is not None}
        prima = st.setdefault("intervalli", {})
        if st.get("e4_base_fatta"):
            scesi = [s for s, h in attuali.items() if h < int(prima.get(s, INTERVALLO_BASE))]
            if scesi:
                monete = contratti_monete(self.chiedi("/fapi/v1/exchangeInfo", {}) or {})
                in_attesa = {a["simbolo"] for a in st["e4_attese"]} | {e["simbolo"] for e in st["e4_eventi"]}
                for s in scesi:
                    if s in monete and s != "BTCUSDT" and s not in in_attesa:
                        st["e4_attese"].append({"simbolo": s, "dal_ms": adesso_ms, "ore": attuali[s]})
        for s in list(prima):
            if s not in attuali:
                prima[s] = INTERVALLO_BASE                 # tornato all'intervallo di serie
        prima.update(attuali)
        st["e4_base_fatta"] = True
        # le attese: il primo regolamento al passo piu' corto e il segno del funding
        restano = []
        for a in st["e4_attese"]:
            ms, segno = primo_passo_corto(self._regolamenti(a["simbolo"], int(a["dal_ms"]) - 2 * INTERVALLO_BASE * ORA_MS))
            if ms is None:
                if adesso_ms - int(a["dal_ms"]) < ATTESA_E4_MAX_MS:
                    restano.append(a)
                continue
            if segno > 0:
                st["e4_eventi"].append({"simbolo": a["simbolo"], "ms": ms, "giorno_entrata": ms // GIORNO_MS + 1})
                print(f"[paper_eventi] evento E4 {a['simbolo']}: intervallo {a['ore']} ore, funding positivo")
        st["e4_attese"] = restano
        # N3: l'uscita di protezione sulle candele a 1 ora
        for ident, p in list((st.get("aperte") or {}).items()):
            if p["tipo"] != "N3":
                continue
            livello = float(p["p0"]) * (1 + STOP)
            for t, massimo, _ in self._ore(p["simbolo"], int(p["ore_fino_ms"])):
                if massimo >= livello:
                    ore_btc = self._ore("BTCUSDT", t)
                    pb = ore_btc[0][2] if ore_btc else mark["BTCUSDT"]
                    self._funding(st, now)
                    self.chiudi(st, ident, livello * (1 + SCARTO_STOP), pb, "protezione +30%", now)
                    break
                p["ore_fino_ms"] = t
        self._funding(st, now)
        st["ultimo_orario"] = now
        self.salva(st)
        self._pubblica(st, mark, now)
        return True

    # ---- ogni giorno alle 00:05: uscite a tempo, entrate di E4 e di N3 ----
    def giornaliero(self, giorno: int, now: float, st: dict) -> bool:
        mark = self._mark()
        if not mark or "BTCUSDT" not in mark:
            return False
        self._funding(st, now)
        for ident, p in list((st.get("aperte") or {}).items()):
            if int(p["uscita_giorno"]) <= giorno:
                pc = mark.get(p["simbolo"])
                if pc is None:               # contratto tolto: l'ultimo prezzo noto e' l'entrata (lo si dice nel motivo)
                    pc = float(p["p0"])
                self.chiudi(st, ident, pc, mark["BTCUSDT"], "tempo" if p["simbolo"] in mark else "contratto senza prezzo", now)
        info = self.chiedi("/fapi/v1/exchangeInfo", {}) or {}
        # niente entrate su contratti che Binance chiude prima della fine della tenuta (non si potrebbe uscire al prezzo vero)
        chiude_e4 = in_chiusura(info, (giorno + GIORNI_E4 + 1) * GIORNO_MS)
        chiude_n3 = in_chiusura(info, (giorno + GIORNI_N3 + 1) * GIORNO_MS)
        restano = []
        for ev in st.get("e4_eventi") or []:
            if int(ev["giorno_entrata"]) > giorno:
                restano.append(ev)
            elif ev["simbolo"] in chiude_e4:
                print(f"[paper_eventi] E4 {ev['simbolo']} saltato: il contratto chiude prima della fine della tenuta")
            elif int(ev["giorno_entrata"]) == giorno and self._volume_del_giorno(ev["simbolo"], giorno - 1) > 0:
                self.apri(st, "E4", ev["simbolo"], giorno, now, mark)
            elif int(ev["giorno_entrata"]) < giorno:
                print(f"[paper_eventi] E4 {ev['simbolo']} saltato: entrata del giorno {ev['giorno_entrata']} gia' passata")
        st["e4_eventi"] = restano
        monete = contratti_monete(info)
        for s, g0 in sorted(monete.items()):
            if s != "BTCUSDT" and g0 + ETA == giorno and s not in chiude_n3 and self._volume_del_giorno(s, giorno - 1) > 0:
                self.apri(st, "N3", s, giorno, now, mark)
        st["ultimo_giorno"] = giorno
        self.salva(st)
        self._pubblica(st, mark, now)
        return True

    # ---- quello che si vede ----
    def equity(self, st: dict, mark: dict) -> float:
        e = float(st.get("equity_realizzata", CAPITALE))
        for p in (st.get("aperte") or {}).values():
            pc, pb = mark.get(p["simbolo"], float(p["p0"])), mark.get("BTCUSDT", float(p["b0"]))
            e += float(p["quota"]) * rendimento(float(p["p0"]), pc, float(p["b0"]), pb, float(p["fc"]), float(p["fb"]))
        return e

    def _pubblica(self, st: dict, mark: dict, now: float) -> None:
        if self.fb is None:
            return
        aperte = st.get("aperte") or {}
        e = self.equity(st, mark)
        n = int(st.get("chiuse_n", 0))
        self.fb.set_rtdb("/paper_eventi/stato", {
            "stato": "acceso", "equity": round(e, 2), "capitale": CAPITALE, "rendimento": e / CAPITALE - 1,
            "aperte_n3": sum(1 for p in aperte.values() if p["tipo"] == "N3"),
            "aperte_e4": sum(1 for p in aperte.values() if p["tipo"] == "E4"),
            "chiuse": n, "rendimento_medio": (float(st.get("chiuse_somma_r", 0.0)) / n) if n else None,
            "e4_in_attesa": len(st.get("e4_attese") or []) + len(st.get("e4_eventi") or []), "aggiornato": now})
        self.fb.set_rtdb("/paper_eventi/aperte", {
            i: {"tipo": p["tipo"], "simbolo": p["simbolo"], "entrata": p["entrata_ms"], "p0": p["p0"],
                "rendimento_ora": round(rendimento(float(p["p0"]), mark.get(p["simbolo"], float(p["p0"])), float(p["b0"]),
                                                   mark.get("BTCUSDT", float(p["b0"])), float(p["fc"]), float(p["fb"])), 5),
                "uscita_giorno": time.strftime("%Y-%m-%d", time.gmtime(int(p["uscita_giorno"]) * 86400))}
            for i, p in aperte.items()} or None)
