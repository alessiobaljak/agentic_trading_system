"""La lettura delle candele orarie della ricerca (`programma6.esecuzione.ore_di`): le barre del programma 6 dove ci sono, i file
mensili dell'archivio per le ore che le barre non coprono (correzione del 25 ottobre 2026, revisione della prova 105)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma6 import esecuzione as es


def _barre(ore, base):
    return pd.DataFrame({"minuto": np.asarray(ore) * 60, "open": base, "high": base + 1, "low": base - 1, "close": base})


def test_le_barre_si_completano_con_i_file_mensili(monkeypatch):
    barre = _barre([100, 101, 102], 10.0)
    zip_ = pd.DataFrame({"open": [5.0, 6.0, 99.0], "high": [6.0, 7.0, 99.0], "low": [4.0, 5.0, 99.0], "close": [5.5, 6.5, 99.0]},
                        index=[98, 99, 101])
    monkeypatch.setattr(es.d6, "barre", lambda s, tf: barre)
    monkeypatch.setattr(es.qa, "ore", lambda s: zip_)
    out = es.ore_di("XUSDT")
    assert list(out.index) == [98, 99, 100, 101, 102]
    assert out.loc[98, "open"] == 5.0 and out.loc[99, "close"] == 6.5      # le ore prima delle barre vengono dai file mensili
    assert out.loc[101, "open"] == 10.0                                    # dove ci sono tutte e due, valgono le barre


def test_senza_barre_i_file_mensili_e_senza_file_le_barre(monkeypatch):
    zip_ = pd.DataFrame({"open": [5.0], "high": [6.0], "low": [4.0], "close": [5.5]}, index=[7])
    monkeypatch.setattr(es.d6, "barre", lambda s, tf: pd.DataFrame())
    monkeypatch.setattr(es.qa, "ore", lambda s: zip_)
    assert es.ore_di("XUSDT").loc[7, "close"] == 5.5
    monkeypatch.setattr(es.d6, "barre", lambda s, tf: _barre([3], 2.0))
    monkeypatch.setattr(es.qa, "ore", lambda s: pd.DataFrame())
    out = es.ore_di("XUSDT")
    assert list(out.index) == [3] and out.loc[3, "open"] == 2.0
