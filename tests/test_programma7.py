"""Programma 7 (trading ogni giorno): i pezzi della prima prova."""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma7 import prima as pr


def test_lunedi_e_universo_del_giorno():
    from research.programma6 import seconda as sc
    lun = sc.giorno(2026, 10, 19)
    giorni = np.arange(lun - 1, lun + 8)
    assert list(pr.lunedi_del_giorno(giorni)) == [lun - 7] + [lun] * 7 + [lun + 7]
    U = np.array([[True, False], [False, True], [True, True]])
    Ud = pr.universo_del_giorno(np.array([lun - 3, lun + 2, lun + 7]), np.array([lun - 7, lun, lun + 7]), U)
    assert (Ud == U).all()


def test_movimenti():
    W = np.array([[0.5, 0.0, -0.5], [0.5, 0.3, 0.0], [0.0, 0.3, 0.0], [0.0, 0.3, -0.2]])
    m = pr.movimenti(W)
    # entrate: 2 il primo giorno, poi la seconda moneta (giorno 2) e la terza di nuovo (giorno 4)
    assert (m["entrate"], m["uscite"]) == (4, 2)
    assert m["durata_media_giorni"] == (W != 0).sum() / 4
    assert m["giorni_con_operazioni"] == 3


def test_per_settimana_somma_i_giorni():
    from research.programma6 import seconda as sc
    lun = sc.giorno(2026, 10, 19)
    giorni = np.arange(lun, lun + 14)
    df = pd.DataFrame({c: np.ones(14) for c in pr.COLONNE} | {"monete": np.arange(14)})
    s = pr.per_settimana(df, giorni)
    assert list(s.index) == [lun, lun + 7] and (s["netto"] == 7).all() and list(s["monete"]) == [6, 13]
