"""Indicatori causali (il valore all'indice i usa solo le barre 0..i), con numpy e pandas."""
import numpy as np
import pandas as pd


def ema(x, n):
    return pd.Series(x).ewm(span=n, adjust=False, min_periods=n).mean().to_numpy()


def sma(x, n):
    return pd.Series(x).rolling(n, min_periods=n).mean().to_numpy()


def somma(x, n):
    return pd.Series(x).rolling(n, min_periods=n).sum().to_numpy()


def dev_std(x, n):
    return pd.Series(x).rolling(n, min_periods=n).std(ddof=0).to_numpy()


def massimo(x, n):
    """Massimo delle ultime n barre, barra corrente compresa."""
    return pd.Series(x).rolling(n, min_periods=n).max().to_numpy()


def minimo(x, n):
    return pd.Series(x).rolling(n, min_periods=n).min().to_numpy()


def precedente(x, k=1):
    """x spostato di k barre in avanti nel tempo: all'indice i vale x[i-k] (NaN all'inizio)."""
    out = np.full(len(x), np.nan)
    if k < len(x):
        out[k:] = np.asarray(x, dtype=float)[: len(x) - k]
    return out


def true_range(h, l, c):
    cp = precedente(c, 1)
    tr = np.maximum(h - l, np.maximum(np.abs(h - cp), np.abs(l - cp)))
    tr[0] = h[0] - l[0]
    return tr


def atr(h, l, c, n):
    """Media semplice del true range sulle ultime n barre."""
    return sma(true_range(h, l, c), n)


def rsi(c, n):
    """RSI di Wilder (media esponenziale con alfa 1/n)."""
    d = np.diff(np.asarray(c, dtype=float), prepend=np.nan)
    su = pd.Series(np.where(d > 0, d, 0.0))
    giu = pd.Series(np.where(d < 0, -d, 0.0))
    su[0] = np.nan
    giu[0] = np.nan
    ms = su.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    mg = giu.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = ms / mg
    out = (100 - 100 / (1 + rs)).to_numpy()
    out[(mg.to_numpy() == 0) & np.isfinite(ms.to_numpy())] = 100.0
    return out


def rendimento(c, k):
    """Rendimento semplice sulle ultime k barre: c[i] / c[i-k] - 1."""
    return np.asarray(c, dtype=float) / precedente(c, k) - 1
