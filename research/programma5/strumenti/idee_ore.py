"""Programma 5: il calcolo nel motore a minuti delle idee promosse dalle esplorazioni a ore (I-010 ... I-016).

Gli eventi si decidono sulle barre di un'ora (``strumenti/ore.py``) come nelle esplorazioni; i trade si simulano sulle
candele da 1 minuto (``motore5.simula``, ``simula_limite``): decisione all'ultimo minuto dell'ora t, ingresso
all'apertura dell'ora t+1, uscita alla chiusura dell'ora t+h.
"""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.ore import barre

BTC = "BTCUSDT"


# ---------------------------------------------------------------------------
# misure sulle barre
# ---------------------------------------------------------------------------

def misure(b: pd.DataFrame) -> pd.DataFrame:
    b = b.copy()
    b["lc"] = np.log(b["close"])
    b["r1"] = b["lc"].diff()
    b["sigma"] = b["r1"].rolling(720, min_periods=500).std()
    return b


def z(b: pd.DataFrame, w: int) -> np.ndarray:
    return ((b["lc"] - b["lc"].shift(w)) / (b["sigma"].shift(w) * np.sqrt(w))).to_numpy()


def residuo(b: pd.DataFrame, btc: pd.DataFrame, w: int) -> tuple:
    """(z del residuo e_w, beta(t-w)) della moneta rispetto a BTC (scheda di I-013 e I-015)."""
    rb = btc["r1"].reindex(b.index)
    lcb = btc["lc"].reindex(b.index)
    m = dict(window=720, min_periods=500)
    cov = (b["r1"] * rb).rolling(**m).mean() - b["r1"].rolling(**m).mean() * rb.rolling(**m).mean()
    beta = cov / rb.rolling(**m).var(ddof=0)
    e1 = b["r1"] - beta.shift(1) * rb
    sig_e = e1.rolling(**m).std()
    ew = (b["lc"] - b["lc"].shift(w)) - beta.shift(w) * (lcb - lcb.shift(w))
    return (ew / (sig_e.shift(w) * np.sqrt(w))).to_numpy(), beta.shift(w).to_numpy()


def sfoltisci(cond: np.ndarray, pausa: int) -> np.ndarray:
    scelti, ultimo = [], -10 ** 12
    for t in np.flatnonzero(cond):
        if t - ultimo >= pausa:
            scelti.append(t)
            ultimo = t
    return np.asarray(scelti, dtype=np.int64)


def posizioni(df: pd.DataFrame, ore_ev: np.ndarray) -> np.ndarray:
    """Posizione nel DataFrame a minuti dell'ultimo minuto di ogni ora (la griglia a minuti e' senza buchi)."""
    m = (np.asarray(ore_ev, dtype=np.int64) + 1) * 60 - 1
    pos = m - int(df.index[0])
    ok = (pos >= 0) & (pos < len(df))
    return pos[ok]


def _sim(df, s, b, cond, d, h, pausa, fund):
    nel = b["periodo"].to_numpy(bool)
    ev = sfoltisci(np.asarray(cond, bool) & nel, pausa)
    pos = posizioni(df, b.index.to_numpy()[ev])
    uscita = m5.Uscita(minuti=60 * h)
    direz = np.full(len(pos), d, dtype=int)
    t = m5.simula(df, s, pos, direz, uscita, fund, esplosione=np.ones(len(pos), bool))
    c = m5.caso(df, s, t, uscita, fund) if not t.empty else t
    return t, c


# ---------------------------------------------------------------------------
# per moneta, per idea
# ---------------------------------------------------------------------------

def _dati(s, periodo, idea):
    df = m5.minuti(s, periodo, idea)
    if df.empty:
        return None, None, None
    return df, misure(barre(s, periodo, idea)), m5.funding(s)


def per_moneta_i010(idea, varianti, s, periodo):
    df, b, fund = _dati(s, periodo, idea)
    if df is None:
        return {}
    return {n: _sim(df, s, b, z(b, v["w"]) <= -v["k"], 1, v["h"], max(v["w"], v["h"]), fund)
            for n, v in varianti.items()}


def per_moneta_i011(idea, varianti, s, periodo):
    df, b, fund = _dati(s, periodo, idea)
    if df is None:
        return {}
    out = {}
    for n, v in varianti.items():
        N = v["N"] * 24
        mx = b["high"].rolling(N, min_periods=N - 12).max().shift(1).to_numpy()
        out[n] = _sim(df, s, b, b["close"].to_numpy() > mx, 1, v["h"], v["h"], fund)
    return out


def per_moneta_i012(idea, varianti, s, periodo):
    df, b, fund = _dati(s, periodo, idea)
    if df is None:
        return {}
    vr = (b["volume"] / b["volume"].rolling(720, min_periods=500).median().shift(1)).to_numpy()
    r1 = b["r1"].to_numpy()
    return {n: _sim(df, s, b, (vr >= v["k"]) & (r1 < 0), 1, v["h"], v["h"], fund) for n, v in varianti.items()}


_BTC_B: Dict[str, pd.DataFrame] = {}


def _btc(periodo, idea):
    chiave = f"{periodo}:{idea}"
    if chiave not in _BTC_B:
        _BTC_B[chiave] = misure(barre(BTC, periodo, idea))
    return _BTC_B[chiave]


def per_moneta_i013(idea, varianti, s, periodo):
    if s == BTC:
        return {}
    df, b, fund = _dati(s, periodo, idea)
    if df is None:
        return {}
    btc = _btc(periodo, idea)
    out = {}
    for n, v in varianti.items():
        ze, _ = residuo(b, btc, v["w"])
        cond = ze <= -v["k"] if v["lato"] == "giu" else ze >= v["k"]
        out[n] = _sim(df, s, b, cond, 1, v["h"], max(v["w"], v["h"]), fund)
    return out


def per_moneta_i014(idea, varianti, s, periodo):
    if s == BTC:
        return {}
    df, b, fund = _dati(s, periodo, idea)
    if df is None:
        return {}
    btc = _btc(periodo, idea)
    out = {}
    for n, v in varianti.items():
        zb = pd.Series(z(btc, v["w"]), index=btc.index).reindex(b.index).to_numpy()
        out[n] = _sim(df, s, b, zb >= v["k"], 1, v["h"], v["h"], fund)
    return out


# ---------------------------------------------------------------------------
# I-015: trade coperto con BTC
# ---------------------------------------------------------------------------

def _tempo(df: pd.DataFrame, s: str, pos: np.ndarray, d: int, minuti: int, fund) -> tuple:
    """Una gamba a mercato con uscita a tempo, allineata a ``pos`` (NaN dove il trade non si puo' fare): come
    ``motore5.simula`` senza stop, con lo scarto doppio. Ritorna (lordo, costo, funding)."""
    o, c = df["open"].to_numpy(float), df["close"].to_numpy(float)
    minuto = df.index.to_numpy()
    n = len(c)
    e = np.asarray(pos, dtype=np.int64) + 1
    fine = e + minuti - 1
    ok = (e >= 0) & (fine < n)
    lordo = np.full(len(e), np.nan)
    lordo[ok] = d * (c[fine[ok]] / o[e[ok]] - 1)
    costo = np.full(len(e), 2 * (m5.TAKER + 2 * m5.scarto(s)))
    fu = np.zeros(len(e))
    if fund is not None and len(fund):
        f_min = fund.index.to_numpy()
        cum = np.concatenate([[0.0], np.cumsum(fund["tasso"].to_numpy(float))])
        a = np.searchsorted(f_min, minuto[np.clip(e, 0, n - 1)], "right")
        b = np.searchsorted(f_min, minuto[np.clip(fine, 0, n - 1)], "right")
        fu = d * (cum[b] - cum[a])
    return lordo, costo, fu


def _coperto(df, dfb, s, pos, beta, minuti, fund, fund_b) -> pd.DataFrame:
    """Long la moneta per 1, short BTC per beta, alle stesse posizioni (stesso minuto: le griglie si allineano per
    minuto); per unita' di valore della moneta."""
    pos = np.asarray(pos, dtype=np.int64)
    pos_b = df.index.to_numpy()[pos] - int(dfb.index[0])
    ok = (pos_b >= 0) & (pos_b < len(dfb))
    la, ca, fa = _tempo(df, s, pos, 1, minuti, fund)
    lb, cb, fb = np.full(len(pos), np.nan), np.zeros(len(pos)), np.zeros(len(pos))
    lb[ok], cb[ok], fb[ok] = _tempo(dfb, BTC, pos_b[ok], -1, minuti, fund_b)
    lordo = la + beta * lb
    costo = ca + beta * cb
    fu = fa + beta * fb
    t = pd.DataFrame({"simbolo": s, "decisione": pos, "minuto": df.index.to_numpy()[pos], "direzione": 1,
                      "lordo": lordo, "costo": costo, "funding": fu, "netto": lordo - costo - fu,
                      "netto_doppio": lordo - 2 * costo - fu, "motivo": "tempo", "beta": beta})
    return t[np.isfinite(t["lordo"]) & np.isfinite(t["beta"])].reset_index(drop=True)


def per_moneta_i015(idea, varianti, s, periodo):
    if s == BTC:
        return {}
    df, b, fund = _dati(s, periodo, idea)
    if df is None:
        return {}
    dfb = m5.minuti(BTC, periodo, idea)
    fund_b = m5.funding(BTC)
    btc = _btc(periodo, idea)
    nel = b["periodo"].to_numpy(bool)
    out = {}
    mese = pd.to_datetime(df.index.to_numpy() * 60, unit="s").to_period("M").astype(str).to_numpy()
    validi = df["periodo"].to_numpy() & np.isfinite(df["open"].to_numpy(float))
    per_mese = {m: np.flatnonzero(validi & (mese == m)) for m in np.unique(mese[validi])}
    for n, v in varianti.items():
        rng = np.random.default_rng(2026)
        ze, beta = residuo(b, btc, v["w"])
        cond = (ze <= -v["k"]) & np.isfinite(beta)
        ev = sfoltisci(cond & nel, max(v["w"], v["h"]))
        m = (b.index.to_numpy()[ev] + 1) * 60 - 1
        pos = m - int(df.index[0])
        dentro = (pos >= 0) & (pos < len(df))
        t = _coperto(df, dfb, s, pos[dentro], beta[ev][dentro], 60 * v["h"], fund, fund_b)
        if t.empty:
            out[n] = (t, t)
            continue
        # il caso: stesse due gambe e stesso beta a un minuto qualunque dello stesso mese
        casi = []
        mesi_t = mese[t["decisione"].to_numpy()]
        for r in range(20):
            dec = np.array([rng.choice(per_mese[x]) for x in mesi_t])
            c = _coperto(df, dfb, s, dec, t["beta"].to_numpy(), 60 * v["h"], fund, fund_b)
            c["ripetizione"] = r
            casi.append(c)
        out[n] = (t, pd.concat(casi, ignore_index=True))
    return out


# ---------------------------------------------------------------------------
# I-016: reti d'acquisto con ordini limite
# ---------------------------------------------------------------------------

def per_moneta_i016(idea, varianti, s, periodo):
    df, b, fund = _dati(s, periodo, idea)
    if df is None:
        return {}
    nel = b["periodo"].to_numpy(bool)
    P = b["close"].shift(1).to_numpy()
    S = b["sigma"].shift(1).to_numpy()
    ore = b.index.to_numpy()
    inizi_tutti = ore * 60 - int(df.index[0])          # primo minuto di ogni ora
    ok_ora = nel & (inizi_tutti >= 0) & (inizi_tutti + 60 <= len(df)) & np.isfinite(P) & np.isfinite(S)
    out = {}
    for n, v in varianti.items():
        livelli = P * np.exp(-v["k"] * S)
        inizi = inizi_tutti[ok_ora]
        t = m5.simula_limite(df, s, inizi, livelli[ok_ora], np.ones(len(inizi), int), validita=60,
                             tenuta=v["H"], fund=fund)
        out[n] = (t, m5.caso_limite(df, s, t, v["H"], fund) if not t.empty else t)
    return out
