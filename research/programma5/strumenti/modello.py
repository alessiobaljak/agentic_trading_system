"""Programma 5, fase 4: il modello che mette insieme i segnali (scheda di K-001).

``dataset`` costruisce, per ogni decisione giornaliera (chiusura dell'ora 23:00 UTC) e ogni moneta, i 20 segnali messi in
scala fra le monete e l'obiettivo (rendimento delle 24 ore dopo meno la media del giorno); ``ridge`` stima i pesi;
``portafoglio_da_previsioni`` fa i trade (long le 4 previsioni piu' alte, short le 4 piu' basse) con
``portafoglio.gambe``.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti import portafoglio as pf
from research.programma5.strumenti.esplora_fase2 import BTC, avanti
from research.programma5.strumenti.libro import libro

SEGNALI = ["z1", "z4", "z24", "r72", "r168", "dal_massimo", "dal_minimo", "res24", "res168", "volume", "acquisti",
           "premio", "dpremio", "funding", "doi", "ls_tutti", "ls_grandi", "imb2", "imb5", "liquidita", "vol_rel"]


def _pct(x: pd.Series, finestra: int = 720, minimo: int = 500) -> pd.Series:
    return x.rolling(finestra, min_periods=minimo).rank(pct=True)


def segnali_moneta(b: pd.DataFrame, btc: pd.DataFrame, lb: pd.DataFrame, premio: pd.Series) -> pd.DataFrame:
    """I segnali di una moneta a ogni ora (noti alla fine dell'ora)."""
    lc, sg = b["lc"], b["sigma"]
    out = pd.DataFrame(index=b.index)
    for w in (1, 4, 24):
        out[f"z{w}"] = (lc - lc.shift(w)) / (sg.shift(w) * np.sqrt(w))
    for w, nome in ((72, "r72"), (168, "r168")):
        out[nome] = (lc - lc.shift(w)) / (sg.shift(w) * np.sqrt(w))
    out["dal_massimo"] = lc - np.log(b["high"].rolling(720, min_periods=500).max())
    out["dal_minimo"] = lc - np.log(b["low"].rolling(720, min_periods=500).min())
    if "beta" in b:
        lcb = btc["lc"].reindex(b.index)
        for w, nome in ((24, "res24"), (168, "res168")):
            e = (lc - lc.shift(w)) - b["beta"].shift(w) * (lcb - lcb.shift(w))
            out[nome] = e / (sg.shift(w) * np.sqrt(w))
    else:
        out["res24"], out["res168"] = 0.0, 0.0
    v24 = b["volume"].rolling(24).sum()
    out["volume"] = np.log(v24 / v24.rolling(720, min_periods=500).median().shift(24))
    out["acquisti"] = _pct(b["buy"].rolling(24).sum() / b["volume"].rolling(24).sum())
    pr = premio.reindex(b.index)
    out["premio"] = _pct(pr)
    out["dpremio"] = pr - pr.shift(24)
    sett = b["funding_8h"].where(b["regolamento"].eq(True)).dropna()
    pf8 = pd.Series(np.nan, index=b.index)
    pf8.loc[sett.index] = sett.rolling(270, min_periods=90).rank(pct=True).to_numpy()
    out["funding"] = pf8.ffill()
    loi = np.log(b["oi"].where(b["oi"] > 0))
    out["doi"] = loi - loi.shift(24)
    out["ls_tutti"] = _pct(b["ls_tutti"])
    out["ls_grandi"] = _pct(b["ls_grandi_pos"])
    L = lb.reindex(b.index) if len(lb) else pd.DataFrame(index=b.index)
    for k in (2, 5):
        out[f"imb{k}"] = L[f"imb{k}_media"].rolling(24, min_periods=20).mean() if f"imb{k}_media" in L else np.nan
    if "liq1_media" in L:
        out["liquidita"] = np.log(L["liq1_media"] / L["liq1_media"].rolling(720, min_periods=500).median().shift(1))
    else:
        out["liquidita"] = np.nan
    out["vol_rel"] = np.log(b["r1"].rolling(24, min_periods=20).std() / sg)
    return out[SEGNALI]


def in_scala(X: np.ndarray) -> np.ndarray:
    """Ogni segnale in scala fra le monete per ogni decisione (asse 0 decisioni, 1 monete, 2 segnali), tagliato a ±3,
    mancante = 0."""
    with np.errstate(all="ignore"):
        media = np.nanmean(X, axis=1, keepdims=True)
        sd = np.nanstd(X, axis=1, keepdims=True)
        Z = (X - media) / np.where(sd > 0, sd, np.nan)
    Z = np.clip(Z, -3, 3)
    return np.where(np.isfinite(Z), Z, 0.0)


def dataset(monete, periodo: str, idea: str):
    ore, P = pf.pannello(monete, periodo, idea)
    # come esplora_fase2.pannello: beta per i residui
    from research.programma5.strumenti import motore5 as m5
    btc = P[BTC]
    monete = [s for s in monete if s in P]
    fine = ore + 1
    nel = P[BTC]["periodo"].to_numpy()
    dec = np.flatnonzero(((fine % 24) == 0) & nel)
    X = np.full((len(dec), len(monete), len(SEGNALI)), np.nan)
    R = np.full((len(dec), len(monete)), np.nan)
    A24 = {}
    for j, s in enumerate(monete):
        b = P[s]
        b["z1"] = (b["lc"] - b["lc"].shift(1)) / b["sigma"].shift(1)
        lb = libro(s, periodo, idea)
        premio = m5.premio(s, periodo, idea)
        seg = segnali_moneta(b, btc, lb, premio)
        X[:, j, :] = seg.to_numpy()[dec]
        a = avanti(b, 24)
        A24[s] = a
        R[:, j] = a[dec]
    with np.errstate(all="ignore"):
        Y = np.clip(R - np.nanmean(R, axis=1, keepdims=True), -0.2, 0.2)
    return ore, dec, monete, in_scala(X), Y, A24


def ridge(Z: np.ndarray, Y: np.ndarray, lam: float) -> np.ndarray:
    ok = np.isfinite(Y)
    A = Z[ok]
    y = Y[ok]
    return np.linalg.solve(A.T @ A + lam * np.eye(A.shape[1]), A.T @ y)


def portafoglio_da_previsioni(ore, dec, monete, Z, pesi, A24, quanti: int = 4, minimo: int = 16, rng=None):
    pred = Z @ pesi                                     # decisioni x monete
    n_ore = len(ore)
    punti = {}
    for j, s in enumerate(monete):
        v = np.full(n_ore, np.nan)
        v[dec] = pred[:, j]
        punti[s] = v
    return pf.gambe(ore, punti, A24, dec, quanti, minimo, 1, rng=rng)
