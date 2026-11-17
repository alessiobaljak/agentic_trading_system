"""Le parti nuove della prova 38: il segnale dello stesso mese dell'anno prima e i comunicati."""
from datetime import date

import pandas as pd

from stock.prove import p038


def prezzi_giornalieri() -> tuple[list[date], pd.Series]:
    """Prezzi giornalieri da gennaio 2016 a febbraio 2017: 100, salvo febbraio 2016 che chiude a 110 (marzo 2016 torna a 100)."""
    giorni = [d.date() for d in pd.bdate_range("2016-01-04", "2017-02-28")]
    r = pd.Series(100.0, index=giorni)
    for d in giorni:
        if date(2016, 2, 1) <= d <= date(2016, 2, 29):
            r.loc[d] = 110.0
    fini = sorted({max(x for x in giorni if (x.year, x.month) == (d.year, d.month)) for d in giorni})
    return fini, r


def test_segnale_e_il_mese_dell_anno_prima():
    fini, r = prezzi_giornalieri()
    k = fini.index(date(2017, 1, 31))                  # decisione a fine gennaio 2017, si tiene febbraio 2017
    v = p038.segnali(fini, k, {"X", "Y"}, {"X": r})
    assert set(v) == {"X"} and abs(v["X"] - 0.10) < 1e-12          # febbraio 2016: da 100 a 110
    k2 = fini.index(date(2017, 2, 28))
    assert abs(p038.segnali(fini, k2, {"X"}, {"X": r})["X"] - (100 / 110 - 1)) < 1e-12     # marzo 2016: da 110 a 100


def test_mese_con_comunicato():
    c = {"A": {(2016, 2), (2016, 5)}}
    assert p038.mese_con_comunicato(c, "A", 2016, 2) and not p038.mese_con_comunicato(c, "A", 2016, 3)
    assert not p038.mese_con_comunicato(c, "B", 2016, 2)
