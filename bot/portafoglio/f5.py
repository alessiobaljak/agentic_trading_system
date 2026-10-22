"""Il paper di F5 eseguito dal bot (docs/backlog.md, P16).

F5 e' il funding fra monete con la banda (research/programma6/VENTIQUATTRESIMA.md; nel paper di ricerca dal 20 ottobre
2026, research/programma6/paper/REGOLE.md). Qui le stesse regole girano sulla macchina con i dati di Binance del momento:

* ogni **lunedi' alle 00:05 UTC**, con i dati fino alla domenica: l'universo delle 100 monete piu' scambiate (mediana del
  volume dei 30 giorni almeno 2 milioni di USDT, almeno 200 giorni di vita, la candela e il volume della domenica, contratti
  che sono monete), il segnale −funding dei 7 giorni, la volatilita' dei 30 giorni; long fra il 20% con il segnale piu' alto,
  short fra il 20% piu' basso, e si resta finche' non si esce oltre il 40% (la banda); pesi secondo l'inverso della
  volatilita', ogni lato al 100% del capitale;
* le operazioni sono **simulate**: al prezzo mark del momento, con commissione 0,05% e scarto (0,01% BTC, ETH, SOL; 0,02%
  le altre) su ogni variazione; le posizioni restano per la settimana e pagano o incassano il **funding vero** di ogni
  regolamento. Nessun ordine vero: questo modulo non usa le chiavi e non chiama mai gli indirizzi degli ordini;
* il primo lunedi' la banda parte dalle posizioni di F5 del paper di ricerca della settimana prima (`paper.json`), cosi'
  il bot tiene da subito le stesse monete della ricerca;
* acceso solo se esiste il file `ops/paper_f5_acceso` (un interruttore suo: lo STOP della dashboard ferma il vecchio paper,
  non questo); lo stato sta in `data/paper_f5.json` sulla macchina e su RTDB in `/paper_f5`.

Le funzioni pure (`universo`, `sigma_30`, `funding_7`, `pesi_banda`) rifanno quelle della ricerca (`terza.pannello_settimane`,
`ottava.sigma_30`, `sesta.funding_7`, `ventiquattresima.pesi_banda`); `tests/test_paper_f5.py` le confronta sugli stessi
dati. Una differenza voluta: qui il funding dei 7 giorni e' la somma esatta, nella ricerca la differenza di due somme
cumulate; alle parita' (molte monete al funding di base, 0,01% a regolamento) l'arrotondamento della ricerca decide l'ordine
e qualche moneta al bordo della banda puo' cambiare.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import requests

from research.programma6.esclusi import ESCLUSI

RADICE = Path(__file__).resolve().parents[2]
INTERRUTTORE = RADICE / "ops" / "paper_f5_acceso"
FILE_STATO = RADICE / "data" / "paper_f5.json"
PAPER_RICERCA = RADICE / "research" / "programma6" / "paper" / "paper.json"
FAPI = "https://fapi.binance.com"
CAPITALE = 10_000.0
N_UNIVERSO, STORIA_MIN, VOLUME_MIN, MIN_MONETE = 100, 200, 2e6, 20
ENTRA, RESTA = 0.20, 0.40
TAKER = 0.0005
SCARTO, SCARTO_ALTRE = {"BTCUSDT": 0.0001, "ETHUSDT": 0.0001, "SOLUSDT": 0.0001}, 0.0002
ORA_RIBILANCIO_S = 300          # lunedi' 00:05 UTC
OGNI_VALUTAZIONE_S = 3600
ATTESA_DOPO_ERRORE_S = 1800     # un ribilancio o una prova non riusciti si riprovano dopo 30 minuti, non a ogni giro
GIORNO_MS = 86_400_000


def scarto(simbolo: str) -> float:
    return SCARTO.get(simbolo, SCARTO_ALTRE)


def lunedi_di(giorno: int) -> int:
    """Il lunedi' (giorno dall'epoca) della settimana del giorno."""
    return giorno - ((giorno + 3) % 7)


def giorno_di_tenuta(funding_ms: int) -> int:
    """Il giorno a cui appartiene un regolamento del funding (come `seconda.funding_giorni`: quello delle 00:00 e' della
    domenica, cioe' del giorno prima)."""
    return (int(funding_ms) // 60_000 - 1) // 1440


# ---------------------------------------------------------------------------
# le regole di F5 (funzioni pure)
# ---------------------------------------------------------------------------

def universo(giornaliere: dict, primo: dict, lunedi: int, n: int = N_UNIVERSO) -> list:
    """Le monete dell'universo del lunedi'. ``giornaliere[s]`` = {giorno: (apertura, chiusura, volume in USDT)}, ``primo[s]``
    = il primo giorno di vita del contratto."""
    candidate = []
    for s, g in giornaliere.items():
        dom = g.get(lunedi - 1)
        lun = g.get(lunedi)
        if dom is None or lun is None or not np.isfinite(dom[1]) or not np.isfinite(lun[0]):
            continue
        if lunedi - primo.get(s, lunedi) < STORIA_MIN or not (dom[2] > 0):
            continue
        vol = [g[d][2] for d in range(lunedi - 30, lunedi) if d in g and np.isfinite(g[d][2])]
        med = float(np.median(vol)) if vol else 0.0
        if med >= VOLUME_MIN:
            candidate.append((s, med))
    candidate.sort(key=lambda x: -x[1])
    return [s for s, _ in candidate[:n]]


def sigma_30(chiusure: dict, lunedi: int) -> float:
    """Deviazione dei rendimenti giornalieri (chiusura su chiusura) dei 30 giorni prima del lunedi'; NaN con meno di 20."""
    r = []
    for d in range(lunedi - 30, lunedi):
        a, b = chiusure.get(d - 1), chiusure.get(d)
        if a is not None and b is not None and np.isfinite(a) and np.isfinite(b) and a > 0:
            r.append(b / a - 1)
    if len(r) < 20:
        return float("nan")
    sd = float(np.std(r, ddof=1))
    return sd if sd > 0 else float("nan")


def funding_7(funding_giorni: dict, lunedi: int) -> float:
    """La somma del funding dei 7 giorni di tenuta prima del lunedi'."""
    return float(sum(funding_giorni.get(d, 0.0) for d in range(lunedi - 7, lunedi)))


def pesi_banda(segnale: dict, sigma: dict, lunghi: set, corti: set) -> tuple:
    """Un passo di `ventiquattresima.pesi_banda`: (pesi, nuovi lunghi, nuovi corti). ``segnale`` e ``sigma`` solo per le
    monete dell'universo."""
    ok = [s for s in segnale if np.isfinite(segnale[s]) and np.isfinite(sigma.get(s, np.nan)) and sigma[s] > 0]
    if len(ok) < MIN_MONETE:
        return {}, set(), set()
    ok.sort()
    valori = np.array([segnale[s] for s in ok])
    ordine = valori.argsort(kind="mergesort")
    ranghi = np.empty(len(ok))
    # rango percentuale con le parita' alla media, come pandas.rank(pct=True)
    v_ord = valori[ordine]
    i = 0
    while i < len(ok):
        j = i
        while j + 1 < len(ok) and v_ord[j + 1] == v_ord[i]:
            j += 1
        ranghi[ordine[i: j + 1]] = (i + j) / 2 + 1
        i = j + 1
    rango = dict(zip(ok, ranghi / len(ok)))
    lunghi = {s for s in lunghi if rango.get(s, 0) >= 1 - RESTA} | {s for s, p in rango.items() if p > 1 - ENTRA}
    corti = {s for s in corti if rango.get(s, 1) <= RESTA} | {s for s, p in rango.items() if p <= ENTRA}
    pesi = {}
    for lato, segno in ((sorted(lunghi), 1.0), (sorted(corti), -1.0)):
        if lato:
            inv = np.array([1.0 / sigma[s] for s in lato])
            for s, w in zip(lato, inv / inv.sum()):
                pesi[s] = segno * float(w)
    return pesi, lunghi, corti


# ---------------------------------------------------------------------------
# il paper
# ---------------------------------------------------------------------------

def _chiedi_http(percorso: str, parametri: dict) -> Optional[object]:
    for prova in range(3):
        try:
            r = requests.get(f"{FAPI}{percorso}", params=parametri, timeout=15)
            if r.status_code in (418, 429):
                time.sleep(min(float(r.headers.get("Retry-After", 5) or 5), 30.0))
                continue
            r.raise_for_status()
            return r.json()
        except Exception as exc:  # noqa: BLE001
            if prova == 2:
                print(f"[paper_f5] GET {percorso} fallito: {exc}")
            time.sleep(1.0 + prova)
    return None


def contratti_monete(info: dict) -> dict:
    """Dai dati di exchangeInfo: {simbolo: giorno di vita} dei perpetui USDT-M in scambio che sono monete (niente indici,
    azioni, metalli: `underlyingType` COIN, niente TradFi, niente `ESCLUSI`)."""
    out = {}
    for x in (info or {}).get("symbols", []):
        if (x.get("contractType") == "PERPETUAL" and x.get("quoteAsset") == "USDT" and x.get("status") == "TRADING"
                and x.get("underlyingType", "COIN") == "COIN" and "TradFi" not in (x.get("underlyingSubType") or [])
                and x["symbol"] not in ESCLUSI):
            out[x["symbol"]] = int(x.get("onboardDate", 0)) // GIORNO_MS
    return out


class PaperF5:
    def __init__(self, fb, chiedi: Callable = _chiedi_http, file_stato: Path = FILE_STATO,
                 interruttore: Path = INTERRUTTORE, pausa_s: float = 0.1) -> None:
        self.fb = fb
        self.chiedi = chiedi
        self.file_stato = Path(file_stato)
        self.interruttore = Path(interruttore)
        self.pausa_s = pausa_s
        self.paper_ricerca = PAPER_RICERCA
        self._ultimo_tentativo = 0.0
        self._prova_fatta = False

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
            st = self.fb.get_rtdb("/paper_f5/stato_interno") if self.fb is not None else None
            return dict(st) if isinstance(st, dict) else {}

    def salva(self, st: dict) -> None:
        self.file_stato.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.file_stato.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.file_stato)
        if self.fb is not None:
            self.fb.set_rtdb("/paper_f5/stato_interno", st)

    # ---- il giro ----
    def tick(self, now: float) -> None:
        if not self.acceso():
            return
        st = self.carica()
        giorno = int(now // 86400)
        m = lunedi_di(giorno)
        dopo_le_5 = now >= m * 86400 + ORA_RIBILANCIO_S
        puo_provare = now - self._ultimo_tentativo >= ATTESA_DOPO_ERRORE_S
        if not st:
            # si parte solo di lunedi' (le settimane come il paper di ricerca)
            if giorno == m and dopo_le_5 and puo_provare:
                self._ultimo_tentativo = now
                self.ribilancia(m, now, {})
            elif self.fb is not None:
                self.fb.set_rtdb("/paper_f5/stato", {"stato": "in attesa del primo lunedi'", "aggiornato": now})
                if not self._prova_fatta and puo_provare:
                    self._ultimo_tentativo = now
                    self.prova(m, now)
            return
        if int(st.get("ultimo_lunedi", 0)) < m and dopo_le_5 and puo_provare:
            self._ultimo_tentativo = now
            self.ribilancia(m, now, st)
            st = self.carica()
        if now - float(st.get("ultima_valutazione", 0)) >= OGNI_VALUTAZIONE_S:
            self.valuta(now, st)

    def _prezzi_mark(self) -> dict:
        dati = self.chiedi("/fapi/v1/premiumIndex", {}) or []
        return {x["symbol"]: float(x["markPrice"]) for x in dati if isinstance(x, dict) and float(x.get("markPrice") or 0) > 0}

    def _contratti(self) -> dict:
        return contratti_monete(self.chiedi("/fapi/v1/exchangeInfo", {}) or {})

    def _giornaliere(self, simbolo: str) -> dict:
        k = self.chiedi("/fapi/v1/klines", {"symbol": simbolo, "interval": "1d", "limit": 40}) or []
        time.sleep(self.pausa_s)
        return {int(r[0]) // GIORNO_MS: (float(r[1]), float(r[4]), float(r[7])) for r in k}

    def _funding_giorni(self, simbolo: str, da_ms: int) -> dict:
        f = self.chiedi("/fapi/v1/fundingRate", {"symbol": simbolo, "startTime": da_ms, "limit": 1000}) or []
        time.sleep(self.pausa_s)
        out: dict = {}
        for x in f:
            d = giorno_di_tenuta(int(x["fundingTime"]))
            out[d] = out.get(d, 0.0) + float(x["fundingRate"])
        return out

    def _equity(self, st: dict, prezzi: dict) -> float:
        e = float(st.get("equity_rif", CAPITALE)) - float(st.get("funding_dal_rif", 0.0))
        for s, q in (st.get("quantita") or {}).items():
            p0 = float(st["prezzi_rif"][s])
            e += float(q) * (float(prezzi.get(s, p0)) - p0)
        return e

    def banda_di_partenza(self, m: int) -> dict:
        """Il primo lunedi' la banda parte dalle posizioni di F5 del paper di ricerca della settimana prima
        (research/programma6/paper/paper.json), cosi' il bot tiene le stesse monete della ricerca da subito; {} se il file
        non c'e' o non e' della settimana prima."""
        try:
            x = json.loads(self.paper_ricerca.read_text(encoding="utf-8"))["adesso"]["F5"]
            if x.get("lunedi") != time.strftime("%Y-%m-%d", time.gmtime((m - 7) * 86400)):
                return {}
            return {"lunghi": sorted(x.get("long") or {}), "corti": sorted(x.get("short") or {})}
        except Exception:  # noqa: BLE001
            return {}

    def ribilancia(self, m: int, now: float, st: dict) -> dict:
        r = self.pesi_del_lunedi(m, st if st else self.banda_di_partenza(m))
        prezzi = self._prezzi_mark() if r is not None else {}
        if r is None or not prezzi:
            print("[paper_f5] ribilancio rimandato di 30 minuti: dati di Binance non disponibili")
            return st
        pesi, lunghi, corti, n_uni = r
        if st:
            self._funding_regolati(st, prezzi)
        equity = self._equity(st, prezzi) if st else CAPITALE
        vecchie = {s: float(q) for s, q in (st.get("quantita") or {}).items()}
        nuove, costo = {}, 0.0
        for s in set(vecchie) | set(pesi):
            p = prezzi.get(s) or float((st.get("prezzi_rif") or {}).get(s, 0.0))
            if not p:
                continue
            q = pesi.get(s, 0.0) * equity / p
            costo += abs(q - vecchie.get(s, 0.0)) * p * (TAKER + scarto(s))
            if q:
                nuove[s] = q
        st = {**st, "inizio": st.get("inizio", m), "ultimo_lunedi": m, "equity_rif": equity - costo,
              "prezzi_rif": {s: prezzi.get(s) or float((st.get("prezzi_rif") or {}).get(s, 0.0)) for s in nuove},
              "quantita": nuove, "pesi": pesi, "lunghi": sorted(lunghi), "corti": sorted(corti), "funding_dal_rif": 0.0,
              "funding_fino_ms": int(now * 1000), "costi_totali": float(st.get("costi_totali", 0.0)) + costo,
              "funding_totale": float(st.get("funding_totale", 0.0)), "ultima_valutazione": now,
              "universo": n_uni}
        self.salva(st)
        data = time.strftime("%Y-%m-%d", time.gmtime(m * 86400))
        if self.fb is not None:
            self.fb.set_rtdb(f"/paper_f5/ribilanciamenti/{data}", {
                "lunedi": data, "universo": n_uni, "long": len(lunghi), "short": len(corti), "costo": costo,
                "equity_prima": equity, "equity_dopo": equity - costo, "eseguito": now})
            self.fb.set_rtdb("/paper_f5/posizioni", {s: round(w, 6) for s, w in pesi.items()})
        print(f"[paper_f5] ribilancio del {data}: universo {n_uni}, long {len(lunghi)}, short {len(corti)}, "
              f"costo {costo:.2f}, equity {equity - costo:.2f}")
        self._pubblica(st, prezzi, now)
        return st

    def pesi_del_lunedi(self, m: int, st: dict) -> tuple:
        """(pesi, lunghi, corti, numero di monete dell'universo) per il lunedi' m, con i dati di adesso; None se mancano."""
        contratti = self._contratti()
        if not contratti:
            return None
        giornaliere = {s: self._giornaliere(s) for s in contratti}
        uni = universo(giornaliere, contratti, m)
        segnale, sigma = {}, {}
        for s in uni:
            sg = sigma_30({d: v[1] for d, v in giornaliere[s].items()}, m)
            sigma[s] = sg
            segnale[s] = -funding_7(self._funding_giorni(s, (m - 8) * GIORNO_MS), m) if np.isfinite(sg) else float("nan")
        pesi, lunghi, corti = pesi_banda(segnale, sigma, set(st.get("lunghi") or []), set(st.get("corti") or []))
        return pesi, lunghi, corti, len(uni)

    def prova(self, m: int, now: float) -> None:
        """La prova a secco: i pesi del lunedi' di questa settimana con i dati di adesso, senza operare; serve a vedere
        prima del primo ribilancio che i dati arrivano e che i numeri hanno senso (/paper_f5/prova)."""
        r = self.pesi_del_lunedi(m, {})
        self._prova_fatta = r is not None
        if r is None or self.fb is None:
            print("[paper_f5] prova a secco non riuscita: exchangeInfo non disponibile")
            return
        pesi, lunghi, corti, n = r
        ordine = sorted(pesi.items(), key=lambda kv: -abs(kv[1]))
        self.fb.set_rtdb("/paper_f5/prova", {
            "lunedi": time.strftime("%Y-%m-%d", time.gmtime(m * 86400)), "universo": n, "long": len(lunghi),
            "short": len(corti), "pesi_maggiori": {s: round(w, 4) for s, w in ordine[:10]}, "eseguita": now})
        print(f"[paper_f5] prova a secco: universo {n}, long {len(lunghi)}, short {len(corti)}")

    def _funding_regolati(self, st: dict, prezzi: dict) -> None:
        """Il funding dei regolamenti dopo l'ultimo controllo, posizione per posizione (il long paga se e' positivo)."""
        da = int(st.get("funding_fino_ms", 0)) + 1
        fino, pagato = da, 0.0
        for s, q in (st.get("quantita") or {}).items():
            f = self.chiedi("/fapi/v1/fundingRate", {"symbol": s, "startTime": da, "limit": 1000}) or []
            time.sleep(self.pausa_s)
            for x in f:
                t = int(x["fundingTime"])
                mark = float(x.get("markPrice") or 0) or float(prezzi.get(s) or st["prezzi_rif"][s])
                pagato += float(q) * mark * float(x["fundingRate"])
                fino = max(fino, t)
        st["funding_dal_rif"] = float(st.get("funding_dal_rif", 0.0)) + pagato
        st["funding_totale"] = float(st.get("funding_totale", 0.0)) + pagato
        st["funding_fino_ms"] = fino

    def valuta(self, now: float, st: dict) -> dict:
        prezzi = self._prezzi_mark()
        if not prezzi:
            return st
        self._funding_regolati(st, prezzi)
        st["ultima_valutazione"] = now
        self.salva(st)
        self._pubblica(st, prezzi, now)
        return st

    def _pubblica(self, st: dict, prezzi: dict, now: float) -> None:
        if self.fb is None:
            return
        e = self._equity(st, prezzi)
        pesi = st.get("pesi") or {}
        self.fb.set_rtdb("/paper_f5/stato", {
            "stato": "acceso", "equity": round(e, 2), "capitale": CAPITALE, "rendimento": e / CAPITALE - 1,
            "long": sum(1 for w in pesi.values() if w > 0), "short": sum(1 for w in pesi.values() if w < 0),
            "ultimo_lunedi": time.strftime("%Y-%m-%d", time.gmtime(int(st.get("ultimo_lunedi", 0)) * 86400)),
            "costi_totali": round(float(st.get("costi_totali", 0.0)), 2),
            "funding_totale": round(float(st.get("funding_totale", 0.0)), 2), "aggiornato": now})
        self.fb.set_rtdb(f"/paper_f5/giorni/{time.strftime('%Y-%m-%d', time.gmtime(now))}", round(e, 2))
