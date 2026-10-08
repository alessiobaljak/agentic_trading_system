"""Le varianti della campagna SOLUSDT: una costruttrice per id (regole in ipotesi.md).

Ogni costruttrice prende la Serie e restituisce le Regole (segnale, condizione, esci),
tutte CAUSALI salvo il controllo positivo, che legge la barra dopo di proposito.
``segnale(i)`` e' None finche' TUTTI gli indicatori della variante (anche quelli della
condizione) non sono calcolabili: e' il riscaldamento, che la (a) e la (b) rispettano.
"""
from __future__ import annotations

import math
from typing import Callable, Dict, Optional

import numpy as np

from comune import Regole, Segnale, Serie, arr, atr, ema, rolling_max, rolling_min, rolling_std, rsi, sma, ritardato


def _ok(*valori) -> bool:
    return all(v is not None and not (isinstance(v, float) and math.isnan(v)) for v in valori)


def segnale_atr(direzione: str, close: np.ndarray, a: np.ndarray, k_stop: float, k_target: Optional[float],
                pronto: np.ndarray) -> Callable[[int], Optional[Segnale]]:
    """Stop (e target) a k volte l'ATR dal close della barra di segnale."""
    lato = 1 if direzione == "long" else -1

    def segnale(i: int) -> Optional[Segnale]:
        if not pronto[i] or not _ok(a[i]) or a[i] <= 0:
            return None
        stop = close[i] - lato * k_stop * a[i]
        if stop <= 0:
            return None
        target = close[i] + lato * k_target * a[i] if k_target is not None else None
        return Segnale(direzione, stop, target)
    return segnale


def esci_dopo(n_barre: int) -> Callable[[int, int], bool]:
    """Chiude all'apertura della barra dopo la n-esima barra tenuta."""
    return lambda i, i_ing: i - i_ing + 1 >= n_barre


def pronto_da(n: int, *serie: np.ndarray) -> np.ndarray:
    ok = np.ones(n, dtype=bool)
    for s in serie:
        ok &= ~np.isnan(s)
    return ok


# --------------------------------------------------------------------------- #
# Controllo positivo degli strumenti (nota, non variante): legge la barra dopo
# --------------------------------------------------------------------------- #

def controllo_positivo(s: Serie) -> Regole:
    c = s.last
    close = arr(c, "close")
    a = atr(c, 14)
    n = len(c)
    pronto = pronto_da(n, a)
    pronto[-1] = False
    futuro = np.append(close[1:], np.nan)  # LOOKAHEAD DICHIARATO: il close della barra dopo
    cond = lambda i: i + 1 < n and futuro[i] > c[i + 1].open  # la barra dopo chiude sopra la sua apertura
    return Regole(segnale_atr("long", close, a, 2.0, None, pronto), cond, esci_dopo(1))


VARIANTI: Dict[str, tuple] = {
    "CONTROLLO": ("1h", controllo_positivo),
}
