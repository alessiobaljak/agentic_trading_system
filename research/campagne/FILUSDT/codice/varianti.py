"""Le varianti della campagna FILUSDT, una funzione per ognuna (regole esatte registrate nel log).

Ogni funzione restituisce una ``quadro.Variante``. Le regole stanno anche in ``ipotesi.md``.
"""
from __future__ import annotations

import numpy as np

import quadro as q
from quadro import Variante


def _stop_atr(direzione: str, n_atr: int, k: float):
    def f(s):
        a = q.atr(s, n_atr)
        return s.c - k * a if direzione == "long" else s.c + k * a
    return f


# ---------------------------------------------------------------------------
# Controllo positivo degli strumenti (lezioni/metodo.md): NON e' una variante.
# ---------------------------------------------------------------------------

def controllo_positivo() -> Variante:
    """Lookahead dichiarato: entra long se la barra SUCCESSIVA chiude oltre l'1% sopra la sua apertura."""
    def ingresso(s):
        prossima_su = np.zeros(len(s.c), dtype=bool)
        prossima_su[:-1] = s.c[1:] > s.o[1:] * 1.01
        return prossima_su
    return Variante("FILUSDT-CONTROLLO", "4h", "long", ingresso, _stop_atr("long", 14, 2.0), barre_max=1,
                    descrizione="lookahead dichiarato: legge la barra dopo")
