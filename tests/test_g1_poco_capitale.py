"""Il conto vero simulato della prova 148 (G1 con 250 euro, research/programma7/OTTANTASEIESIMA.md): i minimi di Binance, le chiusure
«solo riduzione» e le 10 monete di peso piu' grande per lato."""
import numpy as np
import pytest

from research.programma7 import ottantaseiesima as p

VMIN = np.array([5.0, 5.0, 50.0])
PASSO = np.array([0.0, 0.0, 0.001])
QMIN = np.array([0.0, 0.0, 0.001])


def _conto(W, R=None, O=None, cap=280.0, **kw):
    W = np.asarray(W, float)
    R = np.zeros_like(W) if R is None else np.asarray(R, float)
    O = np.ones_like(W) if O is None else np.asarray(O, float)
    return p.conto_vero(W, R, O, cap, VMIN, PASSO, QMIN, **kw)


def test_senza_minimi_tiene_i_pesi():
    W = [[0.5, -0.5, 0.0], [0.01, -0.5, 0.0]]
    X, D, st = _conto(W, minimi=False)
    assert np.allclose(X, W)
    assert st["ordini_saltati"] == 0


def test_ordine_sotto_il_minimo_saltato_anche_in_chiusura():
    W = [[0.5, -0.01, 0.0], [0.0, -0.01, 0.0]]       # 0,01 × 280 = 2,8 USDT: sotto i 5
    X, D, st = _conto(W)
    assert X[0].tolist() == pytest.approx([0.5, 0.0, 0.0])
    # chiudere 140 USDT si puo'; la seconda moneta non si apre mai
    assert X[1].tolist() == pytest.approx([0.0, 0.0, 0.0])
    # una posizione di 3 USDT (sotto il minimo) che va chiusa: il bot di oggi la lascia, con le chiusure permesse si chiude
    W2 = [[0.02, 0, 0], [0.01, 0, 0], [0.0, 0, 0]]
    R2 = [[-0.5, 0, 0], [0, 0, 0], [0, 0, 0]]        # 5,6 USDT aperti, il prezzo dimezza: 2,8 USDT
    X, _, st = _conto(W2, R=R2)
    assert X[2, 0] == pytest.approx(2.8 / 280)
    assert st["posizioni_rimaste_giorno"] == 1
    X, _, _ = _conto(W2, R=R2, chiusure=True)
    assert X[1, 0] == pytest.approx(2.8 / 280) and X[2, 0] == 0.0


def test_passo_della_quantita_del_bitcoin():
    O = [[1.0, 1.0, 75_600.0]]
    X, D, _ = _conto([[0.0, 0.0, 0.2]], O=O)            # 56 USDT voluti: meno di un passo (75,6 USDT)
    assert X[0, 2] == 0.0
    X, D, _ = _conto([[0.0, 0.0, 0.6]], O=O)            # 168 USDT voluti: due passi, 151,2 USDT
    assert X[0, 2] * 280 == pytest.approx(151.2)


def test_meno_monete_per_lato():
    W = np.array([[0.4, 0.3, 0.2, 0.1, -0.6, -0.4]])
    B = p.meno_monete(W, 2)
    assert B[0].tolist() == pytest.approx([4 / 7, 3 / 7, 0, 0, -0.6, -0.4])
