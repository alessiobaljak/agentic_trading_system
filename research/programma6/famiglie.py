"""Programma 6: le famiglie di strategie a indicatori, con le loro griglie piccole scritte prima (METODO.md, sezione 2).

Ogni famiglia e' una funzione ``segnali(barre, **valori) -> dict`` (array booleani ``long``, ``short`` e facoltativi
``esci_long``, ``esci_short``, letti alla chiusura della barra) piu' una griglia di valori, e le regole d'uscita (stop,
obiettivo, stop che segue, tempo) che fanno parte della griglia. Tutte le famiglie operano long e short in modo
simmetrico; i filtri di tendenza usano la media esponenziale a 200 barre.
"""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# indicatori
# ---------------------------------------------------------------------------

def ema(x: pd.Series, n: int) -> pd.Series:
    return x.ewm(span=n, adjust=False, min_periods=n).mean()


def rsi(c: pd.Series, n: int) -> pd.Series:
    d = c.diff()
    su = d.clip(lower=0).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    giu = (-d.clip(upper=0)).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()
    return 100 - 100 / (1 + su / giu.replace(0, np.nan))


def atr_s(b: pd.DataFrame, n: int) -> pd.Series:
    pc = b["close"].shift(1)
    tr = pd.concat([b["high"] - b["low"], (b["high"] - pc).abs(), (b["low"] - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def adx(b: pd.DataFrame, n: int = 14) -> pd.Series:
    su = b["high"].diff()
    giu = -b["low"].diff()
    pdm = su.where((su > giu) & (su > 0), 0.0)
    mdm = giu.where((giu > su) & (giu > 0), 0.0)
    a = atr_s(b, n)
    pdi = 100 * pdm.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean() / a
    mdi = 100 * mdm.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean() / a
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def incrocia_su(a: pd.Series, b) -> np.ndarray:
    b = b if isinstance(b, pd.Series) else pd.Series(b, index=a.index)
    return ((a > b) & (a.shift(1) <= b.shift(1))).to_numpy()


def incrocia_giu(a: pd.Series, b) -> np.ndarray:
    b = b if isinstance(b, pd.Series) else pd.Series(b, index=a.index)
    return ((a < b) & (a.shift(1) >= b.shift(1))).to_numpy()


def _tendenza(c: pd.Series, filtro: str):
    if filtro == "nessuno":
        return np.ones(len(c), bool), np.ones(len(c), bool)
    e = ema(c, 200)
    return (c > e).to_numpy(), (c < e).to_numpy()


# ---------------------------------------------------------------------------
# famiglie
# ---------------------------------------------------------------------------

def rottura(b, N: int, filtro: str):
    """Rottura del canale di Donchian: chiusura sopra il massimo (sotto il minimo) delle N barre prima."""
    c = b["close"]
    mx = b["high"].rolling(N).max().shift(1)
    mn = b["low"].rolling(N).min().shift(1)
    su, giu = _tendenza(c, filtro)
    return {"long": ((c > mx).to_numpy() & su), "short": ((c < mn).to_numpy() & giu)}


def incrocio(b, veloce: int, lenta: int):
    """Incrocio di due medie esponenziali; si esce all'incrocio opposto."""
    c = b["close"]
    f, s = ema(c, veloce), ema(c, lenta)
    su, giu = incrocia_su(f, s), incrocia_giu(f, s)
    return {"long": su, "short": giu, "esci_long": giu, "esci_short": su}


def supertrend(b, periodo: int, molt: float):
    """Supertrend: si entra quando cambia verso, si esce al cambio opposto."""
    h, l, c = b["high"].to_numpy(), b["low"].to_numpy(), b["close"].to_numpy()
    a = atr_s(b, periodo).to_numpy()
    mezzo = (h + l) / 2
    su_b, giu_b = mezzo - molt * a, mezzo + molt * a
    n = len(c)
    verso = np.zeros(n, np.int8)
    fin_su, fin_giu = np.full(n, np.nan), np.full(n, np.nan)
    for i in range(1, n):
        if not np.isfinite(a[i]):
            continue
        fin_su[i] = su_b[i] if not np.isfinite(fin_su[i - 1]) or c[i - 1] < fin_su[i - 1] else max(su_b[i], fin_su[i - 1])
        fin_giu[i] = giu_b[i] if not np.isfinite(fin_giu[i - 1]) or c[i - 1] > fin_giu[i - 1] else min(giu_b[i], fin_giu[i - 1])
        if c[i] > (fin_giu[i - 1] if np.isfinite(fin_giu[i - 1]) else np.inf):
            verso[i] = 1
        elif c[i] < (fin_su[i - 1] if np.isfinite(fin_su[i - 1]) else -np.inf):
            verso[i] = -1
        else:
            verso[i] = verso[i - 1]
    cambio_su = (verso == 1) & (np.roll(verso, 1) != 1)
    cambio_giu = (verso == -1) & (np.roll(verso, 1) != -1)
    cambio_su[0] = cambio_giu[0] = False
    return {"long": cambio_su, "short": cambio_giu, "esci_long": cambio_giu, "esci_short": cambio_su}


def rsi_ritorno(b, n: int, soglia: int, filtro: str):
    """RSI agli estremi nel verso della tendenza: long se RSI < soglia sopra la media a 200, short se RSI > 100 − soglia
    sotto; si esce quando l'RSI torna a 50."""
    c = b["close"]
    r = rsi(c, n)
    su, giu = _tendenza(c, filtro)
    return {"long": (r < soglia).to_numpy() & su, "short": (r > 100 - soglia).to_numpy() & giu,
            "esci_long": (r > 50).to_numpy(), "esci_short": (r < 50).to_numpy()}


def bollinger_ritorno(b, n: int, k: float, filtro: str):
    """Chiusura fuori dalla banda di Bollinger nel verso della tendenza; si esce alla media centrale."""
    c = b["close"]
    m = c.rolling(n).mean()
    s = c.rolling(n).std()
    su, giu = _tendenza(c, filtro)
    return {"long": (c < m - k * s).to_numpy() & su, "short": (c > m + k * s).to_numpy() & giu,
            "esci_long": (c > m).to_numpy(), "esci_short": (c < m).to_numpy()}


def compressione(b, n: int, quota: float):
    """Bande di Bollinger strette (larghezza nel quota più basso delle 500 barre prima) e poi chiusura fuori dalla banda:
    si segue la rottura."""
    c = b["close"]
    m = c.rolling(n).mean()
    s = c.rolling(n).std()
    larg = (4 * s / m)
    stretta = (larg.shift(1) <= larg.shift(1).rolling(500, min_periods=200).quantile(quota)).to_numpy()
    return {"long": stretta & (c > m + 2 * s).to_numpy(), "short": stretta & (c < m - 2 * s).to_numpy()}


def macd_adx(b, veloce: int, lenta: int, adx_min: int):
    """L'istogramma del MACD passa lo zero con un ADX sopra la soglia (mercato in tendenza); si esce al passaggio
    opposto."""
    c = b["close"]
    linea = ema(c, veloce) - ema(c, lenta)
    isto = linea - ema(linea, 9)
    forte = (adx(b) > adx_min).to_numpy()
    su, giu = incrocia_su(isto, 0.0), incrocia_giu(isto, 0.0)
    return {"long": su & forte, "short": giu & forte, "esci_long": giu, "esci_short": su}


def keltner(b, n: int, k: float, filtro: str):
    """Chiusura oltre il canale di Keltner (media a n ± k ATR): si segue la rottura."""
    c = b["close"]
    m = ema(c, n)
    a = atr_s(b, n)
    su, giu = _tendenza(c, filtro)
    return {"long": (c > m + k * a).to_numpy() & su, "short": (c < m - k * a).to_numpy() & giu}


def rsi_spinta(b, n: int, livello: int, filtro: str):
    """L'RSI passa sopra il livello (sotto 100 − livello): spinta nel verso della tendenza."""
    c = b["close"]
    r = rsi(c, n)
    su, giu = _tendenza(c, filtro)
    return {"long": incrocia_su(r, float(livello)) & su, "short": incrocia_giu(r, float(100 - livello)) & giu}


# ---------------------------------------------------------------------------
# le griglie (scritte prima del calcolo; METODO.md, sezione 2)
# ---------------------------------------------------------------------------

USCITE_TENDENZA = [{"stop_k": s, "tp_k": 0.0, "trail_k": t, "max_barre": 0} for s, t in ((2, 2), (2, 3), (3, 3))]
USCITE_RITORNO = [{"stop_k": s, "tp_k": tp, "trail_k": 0.0, "max_barre": mb} for s, tp, mb in
                  ((1.5, 1.5, 48), (2, 2, 48), (2, 3, 96))]

FAMIGLIE = {
    "rottura": (rottura, {"N": [20, 55, 100], "filtro": ["nessuno", "ema200"]}, USCITE_TENDENZA),
    "incrocio": (incrocio, {"veloce": [10, 20], "lenta": [50, 100]}, USCITE_TENDENZA),
    "supertrend": (supertrend, {"periodo": [10, 20], "molt": [2.0, 3.0]}, USCITE_TENDENZA),
    "rsi_ritorno": (rsi_ritorno, {"n": [7, 14], "soglia": [20, 30], "filtro": ["nessuno", "ema200"]}, USCITE_RITORNO),
    "bollinger_ritorno": (bollinger_ritorno, {"n": [20], "k": [2.0, 2.5], "filtro": ["nessuno", "ema200"]},
                          USCITE_RITORNO),
    "compressione": (compressione, {"n": [20], "quota": [0.1, 0.2]}, USCITE_TENDENZA),
    "macd_adx": (macd_adx, {"veloce": [12], "lenta": [26], "adx_min": [20, 30]}, USCITE_TENDENZA),
    "keltner": (keltner, {"n": [20, 50], "k": [2.0, 3.0], "filtro": ["nessuno", "ema200"]}, USCITE_TENDENZA),
    "rsi_spinta": (rsi_spinta, {"n": [14], "livello": [60, 70], "filtro": ["nessuno", "ema200"]}, USCITE_TENDENZA),
}
TEMPI = ["15m", "1h", "4h"]
INGRESSI = [{"limite_k": 0.0, "validita": 1}, {"limite_k": 0.5, "validita": 4}]


def combinazioni(famiglia: str, tempi=None) -> list:
    """Tutte le combinazioni di una famiglia: valori dei segnali × uscite × tempo × ingresso (``tempi``: per la seconda
    prova, solo ``["1d"]``)."""
    _, griglia, uscite = FAMIGLIE[famiglia]
    chiavi = list(griglia)
    out = []
    for valori in itertools.product(*(griglia[k] for k in chiavi)):
        for iu, usc in enumerate(uscite):
            for tf in (tempi or TEMPI):
                for ii, ing in enumerate(INGRESSI):
                    out.append({"famiglia": famiglia, "segnali": dict(zip(chiavi, valori)), "uscita": usc,
                                "iu": iu, "tf": tf, "ingresso": ing, "ii": ii})
    return out
