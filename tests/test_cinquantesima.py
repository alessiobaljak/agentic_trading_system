"""La simulazione di un'operazione della prova 112 (programma7/cinquantesima.py): protezione, uscita a tempo, dati finiti."""
import numpy as np
import pandas as pd

from research.programma7 import cinquantesima as lq


def _minuti(prezzi, inizio=1000):
    p = np.asarray(prezzi, dtype=float)
    return pd.DataFrame({"open": p, "high": p * 1.001, "low": p * 0.999, "close": p}, index=np.arange(inizio, inizio + len(p)))


def test_uscita_a_tempo():
    w = _minuti(np.linspace(100, 110, 400))
    op = lq.operazione(w, 1000, 240)
    assert op["motivo"] == "tempo"
    assert op["uscita_min"] == 1240
    assert op["px"] == w.loc[1240, "open"]
    assert op["p0"] == 100


def test_protezione_al_livello_meno_l_uno_per_cento():
    prezzi = [100.0] * 50 + [80.0] * 350
    op = lq.operazione(_minuti(prezzi), 1000, 240)
    assert op["motivo"] == "protezione"
    assert op["uscita_min"] == 1050
    assert abs(op["px"] - 100 * 0.85 * 0.99) < 1e-9


def test_dati_finiti_prima_dell_uscita():
    op = lq.operazione(_minuti([100.0] * 100), 1000, 240)
    assert op["motivo"] == "dati finiti"
    assert op["uscita_min"] == 1099


def test_entrata_senza_candela():
    assert lq.operazione(_minuti([100.0] * 100), 999, 240) is None
