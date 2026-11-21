"""Le parti senza rete della prova 45: la copertura del giorno prima, il conto con l'uscita all'asta."""
from datetime import date

import numpy as np
import pandas as pd
import pytest

from stock.prove import p045

G = [date(2020, 3, d) for d in (2, 3, 4, 5)]


def test_vale_la_copertura_del_giorno_di_borsa_prima():
    gex = pd.Series([-1e9, 2e9, np.nan], index=[G[0], G[1], G[2]])
    assert p045.copertura_del_giorno_prima(gex, G) == {G[1]: -1e9, G[2]: 2e9}     # il 5 manca: il 4 non ha valore


def test_conto_senza_costi_e_con_i_costi():
    ops = {G[1]: (1, 300.0, 300.0, 303.0), G[2]: (-1, 300.0, 300.0, 297.0)}
    g, saltati = p045.conto(ops, G, costi=False)
    n = int(0.98 * 100_000 / 300)                                                # 326 azioni
    assert saltati == 0 and g[G[0]] == 0.0
    assert g[G[1]] == pytest.approx(n * 3.0 / 100_000)                          # comprato: +1%
    assert g[G[2]] > 0                                                           # venduto allo scoperto e sceso: guadagno
    gc, _ = p045.conto(ops, G)
    assert gc[G[1]] < g[G[1]]                                                    # scarto, slittamento e commissioni


def test_niente_leva():
    ops = {G[1]: (1, 300.0, 400.0, 401.0)}                                       # l'ingresso costa molto più del segnale
    g, saltati = p045.conto(ops, G)
    assert saltati == 1 and g[G[1]] == 0.0


def test_lordo_per_operazione():
    ops = {G[1]: (1, 300.0, 300.0, 303.0), G[2]: (-1, 300.0, 300.0, 297.0)}
    assert list(p045.lordo(ops, {G[1], G[2]})) == pytest.approx([0.01, 0.01])
