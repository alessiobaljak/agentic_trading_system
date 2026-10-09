"""Strumenti comuni della campagna BNBUSDT: dati, parametri, varianti, baseline e metriche.

Qui non c'e' nessuna strategia: solo il modo uniforme di far girare una variante col
motore del protocollo (research/src), uguale per conteggio, test, baseline e verifiche.

Come e' fatta una variante (classe ``Variante``)
-----------------------------------------------
* ``prepara(candele)``: calcola una volta gli indicatori sull'intera serie passata,
  SOLO con operazioni causali (il valore all'indice i usa barre fino a i). Restituisce
  un dizionario di array allineati alle candele.
* ``condizione(ind, i)``: la condizione d'ingresso dell'ipotesi, alla chiusura della barra i.
* ``segnale(ind, i, candele)``: il Segnale (direzione, stop, target) che la variante
  emetterebbe alla barra i SENZA la condizione d'ingresso; None se non calcolabile
  (riscaldamento). E' lo stesso calcolo per variante, baseline (a) e baseline (b).
* ``uscita(ind, i, barre_in_posizione, pos, candele)``: True per chiudere all'apertura
  della barra dopo (uscita della variante, oltre a stop e target).
* filtri della variante: fanno parte di ``condizione`` (la (a) li toglie insieme alla
  condizione, sezione 8). Il filtro dei mesi sotto la liquidita' minima resta in tutte.

La strategia passata al motore legge gli array all'indice ``len(storia) - 1``: la
storia che il motore passa contiene solo le barre chiuse, quindi l'indice e' quello
della barra appena chiusa. Gli array sono calcolati sulla stessa lista di candele
passata al motore (lo controlla ``_controlla``).
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

import numpy as np

RADICE_REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE_REPO))

from research.src import dati, motore, statistica  # noqa: E402
from research.src.motore import Candela, Parametri, Segnale  # noqa: E402

SIMBOLO = "BNBUSDT"
INIZIO = date(2020, 2, 1)
FINE_COSTRUZIONE = date(2022, 10, 28)
FINE_IN_SAMPLE = date(2023, 12, 31)
PERIODI = dati.periodi_campagna(INIZIO)
FINE_COSTRUZIONE_TS = int(PERIODI["fine_costruzione_ts"])
INIZIO_VALIDAZIONE_TS = int(PERIODI["inizio_validazione_ts"])
assert PERIODI["fine_costruzione"] == FINE_COSTRUZIONE

SLIPPAGE = 0.0002  # scheda_moneta.md: fascia 0,02% per lato


def parametri(moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
              riempimento: str = "stop_prima") -> Parametri:
    """I parametri del motore da config/parametri.yaml e dalla scheda (sezione 7)."""
    return Parametri(
        commissione_per_lato=0.0005,
        slippage_per_lato=SLIPPAGE,
        rischio_per_trade=0.01,
        leva_max=2.0,
        modalita_margine="isolated",
        tasso_margine_mantenimento=0.025,
        margine_minimo_da_liquidazione=0.8,
        capitale_iniziale=1000.0,
        riempimento_intrabarra=riempimento,
        moltiplicatore_costi=moltiplicatore_costi,
        ritardo_barre=ritardo_barre,
    )


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------

MESI_ESCLUSI: List[Tuple[int, int]] = [(2020, 5), (2020, 6)]  # sotto la liquidita' minima: fase0_dati.md
_CACHE: Dict[Tuple[str, str], Dict[str, object]] = {}


def carica(tf: str, periodo: str = "costruzione") -> Dict[str, object]:
    """Last e mark allineati (carica_serie_allineate) e funding, per il periodo chiesto.

    ``periodo``: "costruzione" (fino al 2022-10-28) oppure "intero" (fino al 2023-12-31,
    solo per la validazione).
    """
    chiave = (tf, periodo)
    if chiave in _CACHE:
        return _CACHE[chiave]
    fine = FINE_COSTRUZIONE if periodo == "costruzione" else FINE_IN_SAMPLE
    if periodo not in ("costruzione", "intero"):
        raise ValueError(periodo)
    s = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, fine)
    funding = dati.carica_funding(SIMBOLO, INIZIO, fine)
    out = {"candele": s["candele"], "mark": s["candele_mark"], "funding": funding, "tf": tf,
           "periodo": periodo, "ms_barra": dati.durata_intervallo(tf),
           "n_tolte_last": s["n_tolte_last"], "n_tolte_mark": s["n_tolte_mark"]}
    _CACHE[chiave] = out
    return out


def carica_btc(tf: str, fine: date = FINE_COSTRUZIONE) -> List[Candela]:
    return dati.carica_candele("BTCUSDT", tf, INIZIO, fine)


def indici_esclusi_liquidita(candele: Sequence[Candela]) -> np.ndarray:
    """True per le barre di segnale che cadono in un mese sotto la liquidita' minima."""
    esclusi = set(MESI_ESCLUSI)
    out = np.zeros(len(candele), dtype=bool)
    if not esclusi:
        return out
    for i, c in enumerate(candele):
        d = datetime.fromtimestamp(c.ts / 1000, tz=timezone.utc)
        if (d.year, d.month) in esclusi:
            out[i] = True
    return out


def intervalli(maschera: np.ndarray) -> List[Tuple[int, int]]:
    """Da una maschera booleana agli intervalli [inizio, fine) dove e' True."""
    out = []
    i = 0
    n = len(maschera)
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


def array_ohlcv(candele: Sequence[Candela]) -> Dict[str, np.ndarray]:
    return {
        "open": np.array([c.open for c in candele], dtype=float),
        "high": np.array([c.high for c in candele], dtype=float),
        "low": np.array([c.low for c in candele], dtype=float),
        "close": np.array([c.close for c in candele], dtype=float),
        "volume": np.array([c.volume for c in candele], dtype=float),
        "ts": np.array([c.ts for c in candele], dtype=np.int64),
    }


# ---------------------------------------------------------------------------
# Indicatori causali (il valore all'indice i usa solo barre 0..i)
# ---------------------------------------------------------------------------


def sma(x: np.ndarray, n: int) -> np.ndarray:
    """Media mobile semplice; NaN solo nelle finestre che contengono un NaN.

    Correzione del 9 ott 2026 (voce di log BNBUSDT-N013): la versione con la somma
    cumulata propagava un NaN iniziale a tutta la serie (I-08 dava 0 trade).
    """
    from numpy.lib.stride_tricks import sliding_window_view
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        out[n - 1:] = sliding_window_view(np.asarray(x, dtype=float), n).mean(axis=1)
    return out


def ema(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    a = 2.0 / (n + 1)
    m = np.nan
    for i, v in enumerate(x):
        if math.isnan(v):
            out[i] = m
            continue
        m = v if math.isnan(m) else a * v + (1 - a) * m
        out[i] = m if i >= n - 1 else np.nan
    return out


def true_range(o: Dict[str, np.ndarray]) -> np.ndarray:
    h, l, c = o["high"], o["low"], o["close"]
    pc = np.roll(c, 1)
    pc[0] = c[0]
    return np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))


def atr(o: Dict[str, np.ndarray], n: int) -> np.ndarray:
    """ATR di Wilder (media esponenziale 1/n del true range), causale."""
    tr = true_range(o)
    out = np.full(len(tr), np.nan)
    if len(tr) < n:
        return out
    m = tr[:n].mean()
    out[n - 1] = m
    for i in range(n, len(tr)):
        m = m + (tr[i] - m) / n
        out[i] = m
    return out


def rolling_max(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    from numpy.lib.stride_tricks import sliding_window_view
    if len(x) >= n:
        out[n - 1:] = sliding_window_view(x, n).max(axis=1)
    return out


def rolling_min(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    from numpy.lib.stride_tricks import sliding_window_view
    if len(x) >= n:
        out[n - 1:] = sliding_window_view(x, n).min(axis=1)
    return out


def rolling_std(x: np.ndarray, n: int) -> np.ndarray:
    out = np.full(len(x), np.nan)
    from numpy.lib.stride_tricks import sliding_window_view
    if len(x) >= n:
        out[n - 1:] = sliding_window_view(x, n).std(axis=1, ddof=1)
    return out


def rsi(close: np.ndarray, n: int) -> np.ndarray:
    """RSI di Wilder, causale."""
    d = np.diff(close, prepend=close[0])
    su = np.where(d > 0, d, 0.0)
    giu = np.where(d < 0, -d, 0.0)
    out = np.full(len(close), np.nan)
    if len(close) <= n:
        return out
    ms, mg = su[1:n + 1].mean(), giu[1:n + 1].mean()
    for i in range(n, len(close)):
        if i > n:
            ms = (ms * (n - 1) + su[i]) / n
            mg = (mg * (n - 1) + giu[i]) / n
        out[i] = 100.0 if mg == 0 else 100.0 - 100.0 / (1 + ms / mg)
    return out


def ritardo(x: np.ndarray, k: int) -> np.ndarray:
    """x spostato di k barre nel passato: out[i] = x[i-k]."""
    out = np.full(len(x), np.nan)
    if k < len(x):
        out[k:] = x[:len(x) - k]
    return out


# ---------------------------------------------------------------------------
# Varianti
# ---------------------------------------------------------------------------


@dataclass
class Variante:
    id: str
    tf: str
    direzione: str
    prepara: Callable[[List[Candela]], Dict[str, np.ndarray]]
    condizione: Callable[[Dict[str, np.ndarray], int], bool]
    segnale: Callable[[Dict[str, np.ndarray], int, Sequence[Candela]], Optional[Segnale]]
    uscita: Callable[[Dict[str, np.ndarray], int, int, object, Sequence[Candela]], bool]
    descrizione: Dict[str, object] = field(default_factory=dict)


class _Contesto:
    """Indicatori calcolati una volta su una lista di candele, e il mappa ts -> indice."""

    def __init__(self, variante: Variante, candele: List[Candela]):
        self.candele = candele
        self.ind = variante.prepara(candele)
        self.indice_ts = {c.ts: i for i, c in enumerate(candele)}
        self.esclusi = indici_esclusi_liquidita(candele)


_CONTESTI: Dict[Tuple[str, int, int, int], _Contesto] = {}


def contesto(variante: Variante, candele: List[Candela]) -> _Contesto:
    chiave = (variante.id, id(candele), len(candele), candele[-1].ts if candele else 0)
    if chiave not in _CONTESTI:
        _CONTESTI[chiave] = _Contesto(variante, candele)
    return _CONTESTI[chiave]


def _controlla(ctx: _Contesto, storia) -> int:
    i = len(storia) - 1
    if storia[i].ts != ctx.candele[i].ts:
        raise RuntimeError("la storia del motore non coincide con le candele degli indicatori")
    return i


def _gestisci_posizione(v: Variante, ctx: _Contesto, i: int, pos) -> Optional[str]:
    k = ctx.indice_ts[pos.ts_entrata]
    barre = i - k + 1  # barre in posizione, compresa quella d'ingresso
    return "chiudi" if v.uscita(ctx.ind, i, barre, pos, ctx.candele) else None


def fabbrica(v: Variante, candele: List[Candela], con_condizione: bool = True):
    """La funzione SENZA argomenti che crea la strategia (per conta_trade ed esegui).

    Con ``con_condizione`` False e' la baseline (a): entra a ogni barra libera in cui
    il segnale si puo' calcolare (sempre fuori dai mesi sotto la liquidita' minima).
    """
    ctx = contesto(v, candele)

    def crea():
        def strategia(storia, pos):
            i = _controlla(ctx, storia)
            if pos is not None:
                return _gestisci_posizione(v, ctx, i, pos)
            if ctx.esclusi[i]:
                return None
            if con_condizione and not v.condizione(ctx.ind, i):
                return None
            return v.segnale(ctx.ind, i, ctx.candele)
        return strategia
    return crea


def fabbrica_casuale(v: Variante, candele: List[Candela]):
    """crea_casuale(ingressi) per simula_baseline_casuale: segnale della variante agli ingressi."""
    ctx = contesto(v, candele)

    def crea_casuale(ingressi):
        def strategia(storia, pos):
            i = _controlla(ctx, storia)
            if pos is not None:
                return _gestisci_posizione(v, ctx, i, pos)
            if i in ingressi:
                return v.segnale(ctx.ind, i, ctx.candele)
            return None
        return strategia
    return crea_casuale


def fabbrica_segnale(v: Variante, candele: List[Candela]):
    """crea_segnale() per barre_vietate_segnale_non_valido."""
    ctx = contesto(v, candele)

    def crea_segnale():
        def segnale(storia):
            i = _controlla(ctx, storia)
            return v.segnale(ctx.ind, i, ctx.candele)
        return segnale
    return crea_segnale


# ---------------------------------------------------------------------------
# Conteggio, test, baseline
# ---------------------------------------------------------------------------


def conta(v: Variante, tf: Optional[str] = None) -> Dict[str, int]:
    d = carica(tf or v.tf, "costruzione")
    return motore.conta_trade(d["candele"], fabbrica(v, d["candele"]), FINE_COSTRUZIONE_TS, parametri(),
                              candele_mark=d["mark"], funding=d["funding"])


def _r_ordinati(trades) -> np.ndarray:
    return np.array([t.r for t in sorted(trades, key=lambda t: t.ts_uscita)], dtype=float)


def _anno(ts: int) -> int:
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year


def _metriche_trade(trades, risultato=None) -> Dict[str, object]:
    ordinati = sorted(trades, key=lambda t: t.ts_uscita)
    r = np.array([t.r for t in ordinati], dtype=float)
    pnl = [t.pnl for t in ordinati]
    vinti = sum(p for p in pnl if p > 0)
    persi = -sum(p for p in pnl if p < 0)
    pf = vinti / persi if persi > 0 else (math.inf if vinti > 0 else 0.0)
    per_anno: Dict[int, List[float]] = {}
    for t in ordinati:
        per_anno.setdefault(_anno(t.ts_uscita), []).append(t.r)
    senza3 = np.sort(r)[:-3] if len(r) > 3 else np.array([])
    curva = [1000.0]
    for p in pnl:
        curva.append(curva[-1] + p)
    picco, dd = -math.inf, 0.0
    for c in curva:
        picco = max(picco, c)
        dd = max(dd, (picco - c) / picco if picco > 0 else 0.0)
    esiti: Dict[str, int] = {}
    for t in ordinati:
        esiti[t.esito] = esiti.get(t.esito, 0) + 1
    return {
        "profit_factor": pf,
        "trade": len(r),
        "r_medio": float(r.mean()) if len(r) else 0.0,
        "r_mediano": float(np.median(r)) if len(r) else 0.0,
        "win_rate": float((r > 0).mean()) if len(r) else 0.0,
        "r_medio_per_anno": {str(a): float(np.mean(v)) for a, v in sorted(per_anno.items())},
        "trade_per_anno": {str(a): len(v) for a, v in sorted(per_anno.items())},
        "r_medio_senza_3_migliori": float(senza3.mean()) if len(senza3) else None,
        "drawdown_max": -dd,
        "rendimento_totale": (curva[-1] - 1000.0) / 1000.0,
        "trade_ridotti": sum(1 for t in ordinati if t.ridotto),
        "violazioni_liquidazione": sum(1 for t in ordinati if t.violazione_liquidazione),
        "esiti": esiti,
        "costi_medi_r": float(np.mean([(t.commissioni + t.slippage_costo) / t.rischio_iniziale for t in ordinati])) if ordinati else 0.0,
        "funding_medio_r": float(np.mean([t.funding_pagato / t.rischio_iniziale for t in ordinati])) if ordinati else 0.0,
    }


def buy_and_hold_per_anno(candele: Sequence[Candela], da_ts: int = 0) -> Dict[str, Dict[str, float]]:
    p = parametri()
    per_anno: Dict[int, List[Candela]] = {}
    for c in candele:
        if c.ts >= da_ts:
            per_anno.setdefault(_anno(c.ts), []).append(c)
    return {str(a): {"long": motore.buy_and_hold(cs, p, "long"), "short": motore.buy_and_hold(cs, p, "short")}
            for a, cs in sorted(per_anno.items())}


def _riassunto_b(base: Dict[str, object], cb: Dict[str, object], vietate_quota: float) -> Dict[str, object]:
    tps = base.get("trade_per_simulazione", [])
    nv = base.get("segnali_non_validi_per_simulazione", [])
    return {
        "media": base["media"], "errore_standard": base["errore_standard"],
        "n_simulazioni": base["n_simulazioni"], "simulazioni_vuote": base.get("simulazioni_vuote", 0),
        "trade_per_simulazione_medio": float(np.mean(tps)) if len(tps) else 0.0,
        "segnali_scartati_per_simulazione_medio": float(np.mean(nv)) if len(nv) else 0.0,
        "barre_vietate_segnale_non_valido_quota": vietate_quota,
        "percentile_90": base["percentile_90"],
        "t": cb["t"], "soglia": cb["soglia"], "netta": cb["netta"], "valutabile": cb["valutabile"],
        "differenza": cb["differenza"], "errore_standard_differenza": cb["errore_standard"],
        "pavimento_errore": cb["errore_minimo"], "n_blocchi": cb["n_blocchi"], "p_value": cb["p_value"],
    }


def valuta(v: Variante, tf: Optional[str] = None, moltiplicatore_costi: float = 1.0, ritardo_barre: int = 0,
           riempimento: str = "stop_prima", periodo: str = "costruzione", con_a: bool = True,
           btc: bool = True, vieta_extra: Optional[Callable[[Dict[str, np.ndarray]], np.ndarray]] = None) -> Dict[str, object]:
    """Test completo di una variante su costruzione o validazione, con le baseline (a) e (b).

    periodo "costruzione": candele fino al 2022-10-28. periodo "validazione": serie
    intera, contano solo i trade entrati dal 2022-10-29; la (b) entra solo nelle barre
    di validazione e la (a) conta solo i suoi trade entrati in validazione.
    """
    tf = tf or v.tf
    serie = "costruzione" if periodo == "costruzione" else "intero"
    d = carica(tf, serie)
    candele, mark, funding = d["candele"], d["mark"], d["funding"]
    p = parametri(moltiplicatore_costi, ritardo_barre, riempimento)
    da_ts = INIZIO_VALIDAZIONE_TS if periodo == "validazione" else 0

    ris = motore.esegui(candele, None, mark, funding, fabbrica(v, candele)(), p)
    trades = [t for t in ris.trades if t.ts_entrata >= da_ts]
    out: Dict[str, object] = {"timeframe": tf, "periodo": periodo, "moltiplicatore_costi": moltiplicatore_costi,
                              "ritardo_barre": ritardo_barre, "riempimento": riempimento}
    m = _metriche_trade(trades)
    m["buchi_dati"] = ris.n_buchi_dati
    m["segnali_non_validi"] = ris.n_segnali_non_validi
    out["metriche"] = m
    out["buy_and_hold_per_anno"] = buy_and_hold_per_anno(candele, da_ts)
    if len(trades) < 2:
        out["non_valutabile"] = "meno di 2 trade"
        return out
    r = _r_ordinati(trades)
    blocco = statistica.lunghezza_blocco([t.ts_entrata for t in trades], [t.ts_uscita for t in trades])
    out["blocco"] = blocco

    # baseline (a)
    if con_a:
        ris_a = motore.esegui(candele, None, mark, funding, fabbrica(v, candele, con_condizione=False)(), p)
        trades_a = [t for t in ris_a.trades if t.ts_entrata >= da_ts]
        if len(trades_a) >= 2:
            blocco_a = statistica.lunghezza_blocco([t.ts_entrata for t in trades_a], [t.ts_uscita for t in trades_a])
            base_a = statistica.baseline_da_trade(_r_ordinati(trades_a), blocco_a, 2000, 0)
            ca = statistica.contro_baseline(r, blocco, base_a, 2000, 0)
            out["baseline_a"] = {"media": base_a["media"], "errore_standard": base_a["errore_standard"],
                                 "n_trade": base_a["n_trade"], "blocco_a": blocco_a, "n_blocchi_a": base_a["n_blocchi"],
                                 "t": ca["t"], "soglia": ca["soglia"], "netta": ca["netta"],
                                 "valutabile": ca["valutabile"] and base_a["valutabile"],
                                 "differenza": ca["differenza"], "errore_standard_differenza": ca["errore_standard"],
                                 "pavimento_errore": ca["errore_minimo"], "n_blocchi": ca["n_blocchi"]}
        else:
            out["baseline_a"] = {"valutabile": False, "netta": False, "t": "-inf", "n_trade": len(trades_a)}

    # baseline (b)
    vietate = motore.barre_vietate_segnale_non_valido(candele, fabbrica_segnale(v, candele), p)
    n_vietate_segnale = sum(b - a for a, b in vietate)
    ctx = contesto(v, candele)
    vietate = vietate + intervalli(ctx.esclusi)
    if vieta_extra is not None:  # solo per le prove dello scettico: (b) ristretta a certe barre
        extra = np.asarray(vieta_extra(ctx.ind), dtype=bool)
        vietate = vietate + intervalli(extra)
        out["barre_vietate_extra_quota"] = float(extra.mean())
    if da_ts:
        primo_val = next(i for i, c in enumerate(candele) if c.ts >= da_ts)
        vietate.append((0, primo_val))
    durata = motore.durata_media_barre(trades, d["ms_barra"])
    out["durata_media_barre"] = durata
    try:
        base_b = motore.simula_baseline_casuale(candele, fabbrica_casuale(v, candele), len(trades), durata, p,
                                                candele_mark=mark, funding=funding, barre_vietate=vietate,
                                                n_simulazioni=200, primo_seme=0)
        cb = statistica.contro_baseline(r, blocco, base_b, 2000, 0)
        out["baseline_b"] = _riassunto_b(base_b, cb, n_vietate_segnale / len(candele))
        out["percentile_caso"] = statistica.percentile_del_candidato(float(r.mean()), base_b["valori"])
    except ValueError as e:
        out["baseline_b"] = {"valutabile": False, "netta": False, "t": "-inf", "errore": str(e)}
    a_ok = (not con_a) or out["baseline_a"].get("valutabile", False)
    b_ok = out["baseline_b"].get("valutabile", False)
    out["valutabile"] = bool(a_ok and b_ok)
    out["candidato"] = bool(out["valutabile"] and (not con_a or out["baseline_a"]["netta"])
                            and out["baseline_b"]["netta"] and m["r_medio"] > 0)

    if btc:
        try:
            out["btc_stessa_finestra"] = confronto_btc(trades, tf, serie)
        except Exception as e:  # il riferimento di mercato non deve fermare il test
            out["btc_stessa_finestra"] = {"errore": str(e)}
    return out


def confronto_btc(trades, tf: str, serie: str) -> Dict[str, object]:
    """«E' solo il mercato?»: correlazione fra l'R dei trade e il rendimento di BTC nella stessa finestra."""
    fine = FINE_COSTRUZIONE if serie == "costruzione" else FINE_IN_SAMPLE
    btc = carica_btc(tf, fine)
    ts = np.array([c.ts for c in btc], dtype=np.int64)
    op = np.array([c.open for c in btc])
    cl = np.array([c.close for c in btc])
    rb, rr, rm = [], [], []
    for t in trades:
        a = np.searchsorted(ts, t.ts_entrata)
        b = np.searchsorted(ts, t.ts_uscita, side="right") - 1
        if a < len(ts) and b >= a:
            rb.append(cl[b] / op[a] - 1)
            rr.append(t.r)
            rm.append((t.uscita / t.entrata - 1) * (1 if t.direzione == "long" else -1))
    if len(rb) < 3:
        return {"n": len(rb)}
    return {"n": len(rb), "corr_r_btc": float(np.corrcoef(rr, rb)[0, 1]),
            "btc_medio_nella_finestra": float(np.mean(rb)),
            "corr_movimento_moneta_btc": float(np.corrcoef(rm, np.array(rb) * (1 if trades[0].direzione == "long" else -1))[0, 1])}


def compatto(res: Dict[str, object]) -> str:
    """Una riga leggibile del risultato, per lo schermo."""
    m = res["metriche"]
    a = res.get("baseline_a", {})
    b = res.get("baseline_b", {})
    return (f"n={m['trade']} R={m['r_medio']:.3f} PF={m['profit_factor']:.2f} "
            f"a: media={a.get('media', float('nan')) if isinstance(a.get('media'), float) else a.get('media')} t={a.get('t')} netta={a.get('netta')} | "
            f"b: media={b.get('media')} t={b.get('t')} netta={b.get('netta')} | perc={res.get('percentile_caso')} "
            f"anni={m['r_medio_per_anno']} senza3={m['r_medio_senza_3_migliori']}")
