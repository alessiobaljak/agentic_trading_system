"""Indicatori CAUSALI per le varianti di TRBUSDT: il valore all'indice i usa solo le barre 0..i.

Tutti restituiscono array numpy lunghi quanto le candele, con NaN dove il valore non si puo'
ancora calcolare (riscaldamento). Nessuno guarda avanti: niente centrature, niente shift negativi.
"""

from __future__ import annotations

import numpy as np


def colonne(candele):
    o = np.array([c.open for c in candele], dtype=float)
    h = np.array([c.high for c in candele], dtype=float)
    l = np.array([c.low for c in candele], dtype=float)
    c = np.array([c.close for c in candele], dtype=float)
    v = np.array([x.volume for x in candele], dtype=float)
    ts = np.array([x.ts for x in candele], dtype=np.int64)
    return o, h, l, c, v, ts


def sma(x, n):
    out = np.full(len(x), np.nan)
    if len(x) < n:
        return out
    cs = np.cumsum(np.insert(x, 0, 0.0))
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def rolling_max(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.max(x[i - n + 1:i + 1])
    return out


def rolling_min(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.min(x[i - n + 1:i + 1])
    return out


def rolling_std(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.std(x[i - n + 1:i + 1], ddof=1)
    return out


def rolling_median(x, n):
    out = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)):
        out[i] = np.median(x[i - n + 1:i + 1])
    return out


def atr(h, l, c, n=14):
    """ATR di Wilder: media mobile esponenziale (alfa 1/n) del true range, partenza dalla media semplice."""
    tr = np.empty(len(c))
    tr[0] = h[0] - l[0]
    prev = c[:-1]
    tr[1:] = np.maximum(h[1:] - l[1:], np.maximum(np.abs(h[1:] - prev), np.abs(l[1:] - prev)))
    out = np.full(len(c), np.nan)
    if len(c) < n:
        return out
    out[n - 1] = tr[:n].mean()
    for i in range(n, len(c)):
        out[i] = out[i - 1] + (tr[i] - out[i - 1]) / n
    return out


def rsi(c, n):
    """RSI di Wilder."""
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return out
    d = np.diff(c)
    su = np.where(d > 0, d, 0.0)
    giu = np.where(d < 0, -d, 0.0)
    m_su = su[:n].mean()
    m_giu = giu[:n].mean()
    def val(a, b):
        if b == 0:
            return 100.0 if a > 0 else 50.0
        return 100.0 - 100.0 / (1.0 + a / b)
    out[n] = val(m_su, m_giu)
    for i in range(n + 1, len(c)):
        m_su = (m_su * (n - 1) + su[i - 1]) / n
        m_giu = (m_giu * (n - 1) + giu[i - 1]) / n
        out[i] = val(m_su, m_giu)
    return out


def rendimento(c, n):
    """Rendimento delle ultime n barre: c[i] / c[i-n] - 1."""
    out = np.full(len(c), np.nan)
    out[n:] = c[n:] / c[:-n] - 1.0
    return out
