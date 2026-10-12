"""Mattoni comuni delle varianti: stop e target in ATR, uscita a tempo, controllo positivo.

Ogni variante della campagna e' una sottoclasse di ``VarianteATR`` (o un oggetto con la
stessa interfaccia, vedi ``quadro.py``): stop a ``k_stop`` ATR dall'ultimo close,
target a ``rr`` volte la distanza dello stop (None = nessun target), uscita a tempo
dopo ``barre_max`` barre (None = nessuna). La condizione d'ingresso e' della variante.
"""
from __future__ import annotations

import math

import numpy as np

from indicatori import atr, colonne
from research.src.motore import Segnale


class VarianteATR:
    tf = "1h"
    direzione = "long"
    n_atr = 14
    k_stop = 2.0
    rr = 2.0
    barre_max = None
    riscaldamento = 0  # barre minime richieste dagli indicatori della condizione

    def prepara(self, candele, per):
        o, h, l, c = colonne(candele)
        st = {"o": o, "h": h, "l": l, "c": c, "atr": atr(h, l, c, self.n_atr), "candele": candele, "per": per}
        self.prepara_condizione(st)
        return st

    def prepara_condizione(self, st):
        pass

    def pronta(self, st, i):
        return i >= self.riscaldamento and not math.isnan(st["atr"][i])

    def segnale(self, st, i):
        if not self.pronta(st, i):
            return None
        c = st["c"][i]
        d = self.k_stop * st["atr"][i]
        if not (d > 0):
            return None
        if self.direzione == "long":
            return Segnale("long", c - d, c + self.rr * d if self.rr else None)
        return Segnale("short", c + d, c - self.rr * d if self.rr else None)

    def condizione(self, st, i):
        raise NotImplementedError

    def uscita(self, st, i, pos, k):
        if self.barre_max is not None and k >= self.barre_max:
            return "chiudi"
        return None


class ControlloPositivo(VarianteATR):
    """Lookahead DICHIARATO (lezioni/metodo.md): entra se la barra SUCCESSIVA chiude nella direzione.

    Legge di proposito la candela i+1 dall'elenco completo del periodo: non e' una strategia,
    e' la prova che gli strumenti vedono un vantaggio vero e che il ritardo di una barra lo uccide.
    """
    tf = "1h"
    direzione = "long"
    k_stop = 2.0
    rr = 2.0
    barre_max = 1

    def condizione(self, st, i):
        cs = st["candele"]
        if i + 1 >= len(cs):
            return False
        return cs[i + 1].close > cs[i + 1].open
