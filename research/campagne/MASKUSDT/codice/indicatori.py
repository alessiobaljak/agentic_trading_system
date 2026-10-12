"""Indicatori causali per le varianti: il valore alla barra i usa solo barre <= i (NaN nel riscaldamento)."""
from __future__ import annotations

import numpy as np


def colonne(candele):
    o = np.array([c.open for c in candele], dtype=float)
    h = np.array([c.high for c in candele], dtype=float)
    l = np.array([c.low for c in candele], dtype=float)
    c = np.array([c.close for c in candele], dtype=float)
    return o, h, l, c


def sma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) >= n:
        cs = np.cumsum(np.insert(x, 0, 0.0))
        out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def ema(x, n):
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    a = 2.0 / (n + 1)
    out[n - 1] = np.mean(x[:n])
    for i in range(n, len(x)):
        out[i] = a * x[i] + (1 - a) * out[i - 1]
    return out


def true_range(h, l, c):
    pc = np.roll(c, 1)
    pc[0] = c[0]
    return np.maximum(h - l, np.maximum(np.abs(h - pc), np.abs(l - pc)))


def atr(h, l, c, n):
    """ATR di Wilder: media mobile con lisciatura 1/n del true range."""
    tr = true_range(h, l, c)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    out[n] = np.mean(tr[1:n + 1])
    for i in range(n + 1, len(c)):
        out[i] = (out[i - 1] * (n - 1) + tr[i]) / n
    return out


def massimo_precedente(x, n):
    """Massimo delle n barre PRIMA della barra i (esclusa la barra i)."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = np.max(x[i - n:i])
    return out


def minimo_precedente(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        out[i] = np.min(x[i - n:i])
    return out


def rendimento(c, n):
    """Rendimento logaritmico delle ultime n barre: log(c[i] / c[i-n])."""
    out = np.full(len(c), np.nan)
    out[n:] = np.log(c[n:] / c[:-n])
    return out


def rsi(c, n):
    """RSI di Wilder."""
    d = np.diff(c, prepend=c[0])
    su = np.where(d > 0, d, 0.0)
    giu = np.where(d < 0, -d, 0.0)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    ms, mg = np.mean(su[1:n + 1]), np.mean(giu[1:n + 1])
    for i in range(n, len(c)):
        if i > n:
            ms = (ms * (n - 1) + su[i]) / n
            mg = (mg * (n - 1) + giu[i]) / n
        out[i] = 100.0 if mg == 0 else 100.0 - 100.0 / (1.0 + ms / mg)
    return out


def percentile_precedente(x, n, q):
    """q-esimo percentile (lineare) delle n barre PRIMA della barra i; NaN se nella finestra c'e' un NaN."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        w = x[i - n:i]
        if not np.isnan(w).any():
            out[i] = np.percentile(w, q)
    return out


def deviazione_precedente(x, n):
    """Deviazione standard (ddof=1) delle n barre PRIMA della barra i; NaN se nella finestra c'e' un NaN."""
    out = np.full(len(x), np.nan)
    for i in range(n, len(x)):
        w = x[i - n:i]
        if not np.isnan(w).any():
            out[i] = np.std(w, ddof=1)
    return out


def somma_mobile(x, n):
    """Somma delle n barre fino alla barra i compresa; NaN se ce n'e' uno nella finestra."""
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        w = x[i - n + 1:i + 1]
        if not np.isnan(w).any():
            out[i] = np.sum(w)
    return out


def deviazione_mobile(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.std(x[i - n + 1:i + 1], ddof=1)
    return out
