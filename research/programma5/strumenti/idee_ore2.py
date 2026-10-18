"""Programma 5: il calcolo nel motore a minuti delle idee dopo la regola 6ter (I-017, I-019).

Riusa le misure di ``idee_ore`` (che resta com'era, con le impronte delle idee congelate prima) e aggiunge il premio
del perpetuo sullo spot (``motore5.premio``).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.idee_ore import (BTC, _btc, _coperto, _dati, _sim, residuo, sfoltisci, z)


def pct_premio(s: str, periodo: str, idea: str, b: pd.DataFrame) -> np.ndarray:
    """Percentile del premio dell'ora fra quelli delle 720 ore prima (compreso, almeno 500), come E-004."""
    pr = m5.premio(s, periodo, idea).reindex(b.index)
    return pr.rolling(720, min_periods=500).rank(pct=True).to_numpy()


def _limite(df, s, b, v, fund):
    nel = b["periodo"].to_numpy(bool)
    P = b["close"].shift(1).to_numpy()
    S = b["sigma"].shift(1).to_numpy()
    inizi = b.index.to_numpy() * 60 - int(df.index[0])
    ok = nel & (inizi >= 0) & (inizi + 60 <= len(df)) & np.isfinite(P) & np.isfinite(S)
    livelli = P * np.exp(-v["k"] * S)
    t = m5.simula_limite(df, s, inizi[ok], livelli[ok], np.ones(int(ok.sum()), int), validita=60, tenuta=v["H"],
                         fund=fund)
    return t, (m5.caso_limite(df, s, t, v["H"], fund) if not t.empty else t)


def per_moneta_i017(idea, varianti, s, periodo):
    """Il rimbalzo dopo i crolli: varianti di quattro tipi (scheda di I-017)."""
    df, b, fund = _dati(s, periodo, idea)
    if df is None:
        return {}
    pp = None
    out = {}
    for n, v in varianti.items():
        if v["tipo"] == "limite":
            out[n] = _limite(df, s, b, v, fund)
        elif v["tipo"] == "crollo":
            out[n] = _sim(df, s, b, z(b, v["w"]) <= -v["k"], 1, v["h"], max(v["w"], v["h"]), fund)
        elif v["tipo"] == "sconto":
            pp = pct_premio(s, periodo, idea, b) if pp is None else pp
            out[n] = _sim(df, s, b, (z(b, v["w"]) <= -v["k"]) & (pp <= 0.10), 1, v["h"], max(v["w"], v["h"]), fund)
        elif v["tipo"] == "premio_basso":
            pp = pct_premio(s, periodo, idea, b) if pp is None else pp
            out[n] = _sim(df, s, b, pp <= v["q"], 1, v["h"], v["h"], fund)
        else:
            raise ValueError(v["tipo"])
    return out


def per_moneta_i019(idea, varianti, s, periodo):
    """La salita propria coperta con BTC: long la moneta, short beta BTC (scheda di I-019)."""
    if s == BTC:
        return {}
    df, b, fund = _dati(s, periodo, idea)
    if df is None:
        return {}
    dfb = m5.minuti(BTC, periodo, idea)
    fund_b = m5.funding(BTC)
    btc = _btc(periodo, idea)
    nel = b["periodo"].to_numpy(bool)
    mese = pd.to_datetime(df.index.to_numpy() * 60, unit="s").to_period("M").astype(str).to_numpy()
    validi = df["periodo"].to_numpy() & np.isfinite(df["open"].to_numpy(float))
    per_mese = {m: np.flatnonzero(validi & (mese == m)) for m in np.unique(mese[validi])}
    out = {}
    for n, v in varianti.items():
        rng = np.random.default_rng(2026)
        ze, beta = residuo(b, btc, v["w"])
        ev = sfoltisci((ze >= v["k"]) & np.isfinite(beta) & nel, max(v["w"], v["h"]))
        pos = (b.index.to_numpy()[ev] + 1) * 60 - 1 - int(df.index[0])
        dentro = (pos >= 0) & (pos < len(df))
        t = _coperto(df, dfb, s, pos[dentro], beta[ev][dentro], 60 * v["h"], fund, fund_b)
        if t.empty:
            out[n] = (t, t)
            continue
        casi = []
        mesi_t = mese[t["decisione"].to_numpy()]
        for r in range(20):
            dec = np.array([rng.choice(per_mese[x]) for x in mesi_t])
            c = _coperto(df, dfb, s, dec, t["beta"].to_numpy(), 60 * v["h"], fund, fund_b)
            c["ripetizione"] = r
            casi.append(c)
        out[n] = (t, pd.concat(casi, ignore_index=True))
    return out
