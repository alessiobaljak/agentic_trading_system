"""Pezzi comuni della campagna SOLUSDT: serie, parametri, filtro di liquidita', banco di prova.

Scelte fissate in Fase 0 (fase0_dati.md), PRIMA di ogni test, uguali per tutte le varianti:

* Serie: last price a 15 minuti e mark price a 15 minuti, ridotte alla loro
  INTERSEZIONE (barre presenti in entrambe); i timeframe da 30m a 1d si costruiscono
  da queste con ``aggrega_candele`` (solo gruppi completi), cosi' last e mark restano
  allineati barra per barra. Lo stop scatta sul last (``candele_stop=None``).
* Funding: i settlement storici veri (``carica_funding``).
* Mesi sotto la liquidita' minima (2020-09, 2020-10, 2020-12): nessun ingresso su
  segnali di barre di quei mesi (il mese e' quello dell'apertura della barra di
  segnale); filtro uguale per conta_trade, test e baseline (a), e le stesse barre
  vanno fra le vietate della baseline (b).
* Parametri del motore da config/parametri.yaml e dalla scheda (slippage 0,01%).

Il banco di prova (``Variante``) prende tre funzioni CAUSALI calcolate una volta sulla
serie che gli si passa (ogni valore alla barra i usa solo le barre 0..i):
``segnale(i)`` (stop e target, senza condizione d'ingresso, None se non calcolabile),
``condizione(i)`` (la condizione d'ingresso dell'ipotesi, filtri compresi) e
``esci(i, i_ingresso)`` (True = "chiudi" all'apertura della barra dopo). La strategia
ricava l'indice della barra dal ts dell'ultima barra chiusa.
"""
from __future__ import annotations

import math
import pickle
import sys
from dataclasses import dataclass, replace
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, Segnale  # noqa: E402

SIMBOLO = "SOLUSDT"
INIZIO = date(2020, 9, 1)
FINE = date(2023, 12, 31)
FINE_COSTRUZIONE_TS = 1672444799999
INIZIO_VALIDAZIONE_TS = 1672444800000
MESI_ESCLUSI = {(2020, 9), (2020, 10), (2020, 12)}
TRADE_MINIMI_COSTRUZIONE = 70
CACHE = dati.RADICE_DEFAULT / "data" / "insample" / SIMBOLO / "cache"
TIMEFRAME = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]

PARAMETRI = Parametri(
    commissione_per_lato=0.0005,
    slippage_per_lato=0.0001,
    rischio_per_trade=0.01,
    leva_max=2.0,
    modalita_margine="isolated",
    tasso_margine_mantenimento=0.025,
    margine_minimo_da_liquidazione=0.8,
    capitale_iniziale=1000.0,
    riempimento_intrabarra="stop_prima",
    moltiplicatore_costi=1.0,
    ritardo_barre=0,
)


def ms_tf(tf: str) -> int:
    return dati.durata_intervallo(tf)


def anno_mese(ts: int) -> Tuple[int, int]:
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    return d.year, d.month


def _prepara_cache() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    last = dati.carica_candele(SIMBOLO, "15m", INIZIO, FINE)
    mark = dati.carica_candele(SIMBOLO, "15m", INIZIO, FINE, tipo="markPriceKlines")
    comuni = {c.ts for c in last} & {c.ts for c in mark}
    last = [c for c in last if c.ts in comuni]
    mark = [c for c in mark if c.ts in comuni]
    btc = dati.carica_candele("BTCUSDT", "15m", date(2020, 1, 1), FINE)
    funding = dati.carica_funding(SIMBOLO, INIZIO, FINE)
    for tf in TIMEFRAME:
        if tf == "15m":
            l, m, b = last, mark, btc
        else:
            l, m, b = (dati.aggrega_candele(last, tf), dati.aggrega_candele(mark, tf), dati.aggrega_candele(btc, tf))
        with open(CACHE / f"{tf}.pkl", "wb") as f:
            pickle.dump({"last": l, "mark": m, "btc": b}, f)
    with open(CACHE / "funding.pkl", "wb") as f:
        pickle.dump(funding, f)


@dataclass
class Serie:
    tf: str
    last: List[Candela]
    mark: List[Candela]
    btc: Dict[int, Candela]  # BTCUSDT per ts (riferimento di mercato)
    funding: List[Tuple[int, float]]


def _versione_caricatore() -> str:
    """Impronta di src/dati.py: se il caricatore cambia (es. CHANGELOG 2026-10-08), la cache si rifà."""
    return dati.impronta_file(Path(dati.__file__))


def carica(tf: str, periodo: str = "costruzione") -> Serie:
    """Serie del timeframe: 'costruzione' (fino alla fine della costruzione) o 'validazione' (tutto)."""
    versione = CACHE / "versione_caricatore.txt"
    aggiornata = versione.is_file() and versione.read_text().strip() == _versione_caricatore()
    if not aggiornata or not (CACHE / f"{tf}.pkl").is_file() or not (CACHE / "funding.pkl").is_file():
        _prepara_cache()
        versione.write_text(_versione_caricatore() + "\n")
    with open(CACHE / f"{tf}.pkl", "rb") as f:
        d = pickle.load(f)
    with open(CACHE / "funding.pkl", "rb") as f:
        funding = pickle.load(f)
    last, mark = d["last"], d["mark"]
    if periodo == "costruzione":
        last = [c for c in last if c.close_ts <= FINE_COSTRUZIONE_TS]
        mark = [c for c in mark if c.close_ts <= FINE_COSTRUZIONE_TS]
        funding = [(t, r) for t, r in funding if t <= FINE_COSTRUZIONE_TS]
    elif periodo != "validazione":
        raise ValueError(periodo)
    return Serie(tf, last, mark, {c.ts: c for c in d["btc"]}, funding)


def mesi_esclusi_barre(candele: Sequence[Candela]) -> np.ndarray:
    """True alle barre di segnale nei mesi sotto la liquidita' minima."""
    return np.array([anno_mese(c.ts) in MESI_ESCLUSI for c in candele], dtype=bool)


def come_intervalli(maschera: np.ndarray) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    i, n = 0, len(maschera)
    while i < n:
        if maschera[i]:
            j = i
            while j < n and maschera[j]:
                j += 1
            out.append((i, j))
            i = j
        else:
            i += 1
    return out


# --------------------------------------------------------------------------- #
# Indicatori causali (ogni valore alla barra i usa solo le barre 0..i)
# --------------------------------------------------------------------------- #

def arr(candele: Sequence[Candela], campo: str) -> np.ndarray:
    return np.array([getattr(c, campo) for c in candele], dtype=float)


def sma(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        c = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def rolling_std(x: np.ndarray, n: int) -> np.ndarray:
    """Deviazione standard (ddof 0) delle ultime n barre, barra i compresa."""
    return pd.Series(x).rolling(n, min_periods=n).std(ddof=0).to_numpy()


def rolling_max(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).rolling(n, min_periods=n).max().to_numpy()


def rolling_min(x: np.ndarray, n: int) -> np.ndarray:
    return pd.Series(x).rolling(n, min_periods=n).min().to_numpy()


def ritardato(x: np.ndarray, k: int = 1) -> np.ndarray:
    """x spostato di k barre in avanti: alla barra i vale x[i-k] (NaN prima)."""
    out = np.full(len(x), np.nan)
    if k < len(x):
        out[k:] = x[:-k] if k > 0 else x
    return out


def atr(candele: Sequence[Candela], n: int) -> np.ndarray:
    """Average True Range di Wilder (media mobile di Wilder del true range)."""
    h, l, c = arr(candele, "high"), arr(candele, "low"), arr(candele, "close")
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(abs(h[1:] - c[:-1]), abs(l[1:] - c[:-1])))
    out = np.full(len(c), np.nan)
    if len(c) >= n:
        out[n - 1] = tr[:n].mean()
        for i in range(n, len(c)):
            out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def rsi(close: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder."""
    d = np.diff(close, prepend=np.nan)
    su = np.where(d > 0, d, 0.0)
    giu = np.where(d < 0, -d, 0.0)
    out = np.full(len(close), np.nan)
    if len(close) <= n:
        return out
    ms, mg = su[1:n + 1].mean(), giu[1:n + 1].mean()
    out[n] = 100.0 if mg == 0 else 100 - 100 / (1 + ms / mg)
    for i in range(n + 1, len(close)):
        ms = (ms * (n - 1) + su[i]) / n
        mg = (mg * (n - 1) + giu[i]) / n
        out[i] = 100.0 if mg == 0 else 100 - 100 / (1 + ms / mg)
    return out


def ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    a = 2 / (n + 1)
    inizio = None
    for i in range(len(x)):
        if np.isnan(x[i]):
            continue
        if inizio is None:
            inizio = i
            out[i] = x[i]
        else:
            out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


# --------------------------------------------------------------------------- #
# Banco di prova
# --------------------------------------------------------------------------- #

@dataclass
class Regole:
    """Le tre funzioni causali di una variante, gia' calcolate su una serie."""
    segnale: Callable[[int], Optional[Segnale]]
    condizione: Callable[[int], bool]
    esci: Callable[[int, int], bool]


# Una "costruttrice" prende la Serie e restituisce le Regole calcolate su di essa.
Costruttrice = Callable[[Serie], Regole]


def _strategia(serie: Serie, regole: Regole, ingressi: Optional[frozenset], modo: str):
    """modo: 'variante' (condizione), 'a' (ogni barra libera), 'casuale' (indici in ingressi)."""
    indice = {c.ts: k for k, c in enumerate(serie.last)}
    esclusi = mesi_esclusi_barre(serie.last)
    stato = {"ingresso": None}

    def strategia(storia, pos):
        i = indice[storia[-1].ts]
        if pos is not None:
            if stato["ingresso"] is None or stato["ingresso"][0] != pos.ts_entrata:
                stato["ingresso"] = (pos.ts_entrata, indice[pos.ts_entrata])
            if regole.esci(i, stato["ingresso"][1]):
                return "chiudi"
            return None
        if modo == "casuale":
            if i in ingressi:
                return regole.segnale(i)
            return None
        if esclusi[i]:
            return None
        if modo == "variante" and not regole.condizione(i):
            return None
        return regole.segnale(i)

    return strategia


def fabbrica(serie: Serie, costruttrice: Costruttrice, modo: str = "variante"):
    """La funzione SENZA argomenti che crea la strategia (per conta_trade e per il test)."""
    def crea():
        return _strategia(serie, costruttrice(serie), None, modo)
    return crea


def fabbrica_casuale(serie: Serie, costruttrice: Costruttrice):
    def crea_casuale(ingressi):
        return _strategia(serie, costruttrice(serie), frozenset(ingressi), "casuale")
    return crea_casuale


def fabbrica_segnale(serie: Serie, costruttrice: Costruttrice):
    indice = {c.ts: k for k, c in enumerate(serie.last)}

    def crea_segnale():
        regole = costruttrice(serie)
        return lambda storia: regole.segnale(indice[storia[-1].ts])
    return crea_segnale


def conta(tf: str, costruttrice: Costruttrice, parametri: Parametri = PARAMETRI) -> Dict[str, int]:
    s = carica(tf, "costruzione")
    return motore.conta_trade(s.last, fabbrica(s, costruttrice), FINE_COSTRUZIONE_TS, parametri,
                              candele_stop=None, candele_mark=s.mark, funding=s.funding)


def r_per_anno(trades) -> Dict[str, float]:
    per: Dict[int, List[float]] = {}
    for t in trades:
        per.setdefault(datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year, []).append(t.r)
    return {str(a): round(float(np.mean(v)), 4) for a, v in sorted(per.items())}


def n_per_anno(trades) -> Dict[str, int]:
    per: Dict[int, int] = {}
    for t in trades:
        a = datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year
        per[a] = per.get(a, 0) + 1
    return {str(a): v for a, v in sorted(per.items())}


def buy_and_hold_per_anno(candele: Sequence[Candela], parametri: Parametri) -> Dict[str, Dict[str, float]]:
    per: Dict[int, List[Candela]] = {}
    for c in candele:
        per.setdefault(datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc).year, []).append(c)
    return {str(a): {"long": round(motore.buy_and_hold(v, parametri, "long"), 4),
                     "short": round(motore.buy_and_hold(v, parametri, "short"), 4)} for a, v in sorted(per.items())}


def _confronto_json(c: Dict[str, object]) -> Dict[str, object]:
    chiavi = ("t", "soglia", "netta", "valutabile", "differenza", "errore_standard", "errore_minimo",
              "errore_candidato", "n_blocchi", "p_value", "baseline_media", "baseline_errore_standard")
    out = {}
    for k in chiavi:
        v = c.get(k)
        if isinstance(v, float):
            v = None if math.isinf(v) or math.isnan(v) else round(v, 5)
        out[k] = v
    return out


def valuta(tf: str, costruttrice: Costruttrice, periodo: str = "costruzione", parametri: Parametri = PARAMETRI,
           n_simulazioni: int = 200, costruttrice_a: Optional[Costruttrice] = None) -> Dict[str, object]:
    """Test di una variante con le baseline (a) e (b) (sezione 8) sul periodo indicato.

    In 'validazione' la serie va dall'inizio della costruzione alla fine della validazione
    (indicatori caldi) e contano solo i trade ENTRATI dopo la fine della costruzione; la (a)
    e la (b) si calcolano sulle sole barre di validazione (le barre di costruzione sono
    vietate alla (b); per la (a) contano i suoi trade entrati in validazione).
    """
    s = carica(tf, periodo)
    ris = motore.esegui(s.last, None, s.mark, s.funding, fabbrica(s, costruttrice)(), parametri)
    trades = ris.trades
    if periodo == "validazione":
        trades = [t for t in trades if t.ts_entrata > FINE_COSTRUZIONE_TS]
    trades = sorted(trades, key=lambda t: t.ts_uscita)
    out: Dict[str, object] = {"timeframe": tf, "periodo": periodo, "n_trade": len(trades)}
    if not trades:
        return out
    r = [t.r for t in trades]
    vinti = sum(t.pnl for t in trades if t.pnl > 0)
    persi = -sum(t.pnl for t in trades if t.pnl < 0)
    migliori = sorted(r, reverse=True)[3:]
    # curva del capitale dai rendimenti dei trade (pnl / capitale all'ingresso), partendo dal
    # capitale iniziale: in costruzione coincide con capitale + somma dei pnl (una posizione alla
    # volta); in validazione non dipende dal capitale lasciato dalla costruzione.
    curva = [(trades[0].ts_entrata, parametri.capitale_iniziale)]
    cap = parametri.capitale_iniziale
    for t in trades:
        cap *= 1 + t.pnl_pct
        curva.append((t.ts_uscita, cap))
    out["metriche"] = {
        "profit_factor": round(vinti / persi, 4) if persi > 0 else None,
        "trade": len(trades),
        "r_medio": round(float(np.mean(r)), 4),
        "r_medio_per_anno": r_per_anno(trades),
        "trade_per_anno": n_per_anno(trades),
        "r_medio_senza_3_migliori": round(float(np.mean(migliori)), 4) if migliori else None,
        "drawdown_max": round(-motore.drawdown_massimo(curva), 4),
        "rendimento_totale": round((cap - parametri.capitale_iniziale) / parametri.capitale_iniziale, 4),
        "win_rate": round(sum(1 for t in trades if t.pnl > 0) / len(trades), 4),
        "esiti": {e: sum(1 for t in trades if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
        "ridotti_tetto_leva": sum(1 for t in trades if t.ridotto),
        "violazioni_liquidazione": sum(1 for t in trades if t.violazione_liquidazione),
        "stop_medio_pct": round(float(np.mean([abs(t.entrata - t.stop) / t.entrata for t in trades])) * 100, 3),
        "stop_oltre_6pct": sum(1 for t in trades if abs(t.entrata - t.stop) / t.entrata > 0.06),
        "durata_media_barre": motore.durata_media_barre(trades, ms_tf(tf)),
        "costi_medi_r": round(float(np.mean([(t.commissioni + t.slippage_costo + t.funding_pagato) / t.rischio_iniziale for t in trades])), 4),
        "buchi_dati": ris.n_buchi_dati,
        "segnali_non_validi": ris.n_segnali_non_validi,
    }
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # baseline (a): senza condizione d'ingresso, entra a ogni barra libera
    ca = costruttrice_a or costruttrice
    ris_a = motore.esegui(s.last, None, s.mark, s.funding, fabbrica(s, ca, modo="a")(), parametri)
    tr_a = ris_a.trades
    if periodo == "validazione":
        tr_a = [t for t in tr_a if t.ts_entrata > FINE_COSTRUZIONE_TS]
    tr_a = sorted(tr_a, key=lambda t: t.ts_uscita)
    if len(tr_a) >= 2:
        blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in tr_a], [t.ts_uscita for t in tr_a])
        base_a = statistica.baseline_da_trade([t.r for t in tr_a], blocco_a, n=2000, seme=0)
        conf_a = statistica.contro_baseline(r, blocco, base_a, n=2000, seme=0)
        out["baseline_a"] = {"media": round(base_a["media"], 5), "n_trade": base_a["n_trade"], "blocco_a": blocco_a,
                             "n_blocchi_a": base_a["n_blocchi"], **_confronto_json(conf_a)}
    else:
        out["baseline_a"] = {"valutabile": False, "n_trade": len(tr_a), "t": None, "netta": False}

    # baseline (b): entrate casuali con la stessa uscita
    vietate_segnale = motore.barre_vietate_segnale_non_valido(s.last, fabbrica_segnale(s, costruttrice), parametri)
    escl = mesi_esclusi_barre(s.last)
    if periodo == "validazione":
        escl = escl | np.array([c.ts <= FINE_COSTRUZIONE_TS for c in s.last])
    vietate = vietate_segnale + come_intervalli(escl)
    n_vietate_segnale = sum(b - a for a, b in vietate_segnale)
    durata = motore.durata_media_barre(trades, ms_tf(tf))
    try:
        base_b = motore.simula_baseline_casuale(s.last, fabbrica_casuale(s, costruttrice), len(trades), durata, parametri,
                                                candele_stop=None, candele_mark=s.mark, funding=s.funding,
                                                barre_vietate=vietate, n_simulazioni=n_simulazioni, primo_seme=0)
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "t": None, "netta": False, "errore": str(e)}
        out["candidato"] = False
        return out
    if periodo == "validazione":
        pass  # la (b) di validazione ha ingressi solo in validazione: i trade casuali entrano tutti dopo
    conf_b = statistica.contro_baseline(r, blocco, base_b, n=2000, seme=0)
    out["baseline_b"] = {"media": round(base_b["media"], 5), "n_simulazioni": base_b["n_simulazioni"],
                         "trade_per_simulazione_medio": round(float(np.mean(base_b["trade_per_simulazione"])), 1),
                         "barre_vietate_segnale_non_valido_quota": round(n_vietate_segnale / len(s.last), 4),
                         "segnali_scartati_per_simulazione_medio": round(float(np.mean(base_b["segnali_non_validi_per_simulazione"])) + float(np.mean(base_b["segnali_senza_barra_per_simulazione"])), 2),
                         "simulazioni_vuote": base_b["simulazioni_vuote"],
                         **_confronto_json(conf_b)}
    out["percentile_caso"] = round(statistica.percentile_del_candidato(float(np.mean(r)), base_b["valori"]), 1)
    if periodo == "costruzione":
        out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(s.last, parametri)
    else:
        out["buy_and_hold_per_anno"] = buy_and_hold_per_anno([c for c in s.last if c.ts > FINE_COSTRUZIONE_TS], parametri)
    a, b = out["baseline_a"], out["baseline_b"]
    out["candidato"] = bool(a.get("netta") and b.get("netta") and out["metriche"]["r_medio"] > 0)
    out["_trades"] = trades
    out["_base_b_valori"] = base_b["valori"]
    return out


def pulito(d: Dict[str, object]) -> Dict[str, object]:
    return {k: v for k, v in d.items() if not k.startswith("_")}
