"""Programma 6, il paper: la stima del funding dall'indice del premio (research/programma6/paper/REGOLE.md)."""
import numpy as np
import pandas as pd
import pytest

pytest.importorskip("numba")

from research.programma6.paper import aggiorna as ag  # noqa: E402


def test_funding_dal_premio_con_la_formula_di_binance():
    g = 20000                                     # un giorno qualsiasi
    ore = np.arange(g * 24, g * 24 + 24)
    p = pd.Series(np.r_[np.full(8, 0.0001), np.full(8, 0.0010), np.full(8, -0.0002)], index=ore)
    f = ag.funding_da_premio(p)
    # 0,0001 + clip(0)=0,0001; 0,0010 + clip(-0,0009 -> -0,0005)=0,0005; -0,0002 + clip(0,0003)=0,0001
    assert f.index.tolist() == [g]
    assert f.iloc[0] == pytest.approx(0.0001 + 0.0005 + 0.0001)


def test_funding_dal_premio_vuoto():
    assert ag.funding_da_premio(pd.Series(dtype=float)).empty
