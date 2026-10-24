"""Programma 8 (lo spot): i pezzi della prima prova."""
from __future__ import annotations

import numpy as np

from research.programma8 import prima as p8


def test_solo_long_e_paniere():
    W = np.array([[0.5, -0.5, 0.5, -0.5]])
    assert (p8.solo_long(W) == np.array([[0.5, 0, 0.5, 0]])).all()
    U = np.ones((1, 25), dtype=bool)
    sig = np.ones((1, 25))
    sig[0, 0] = 2.0
    Wb = p8.pesi_paniere(U, sig)
    assert abs(Wb.sum() - 1) < 1e-12 and Wb[0, 0] < Wb[0, 1]
