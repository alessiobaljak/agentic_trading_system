"""Le parti senza rete della prova 37b: il mese della crisi e le tre condizioni."""
from datetime import date, timedelta

import pandas as pd

from stock.prove import p037b


def _giorni(n, dal=date(2025, 3, 3)):
    out, d = [], dal
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def test_mese_della_crisi_e_quello_piu_agitato_non_quello_piu_in_perdita():
    g = _giorni(60)
    spy = pd.Series(-0.002, index=g)                                    # marzo: scende piano tutti i giorni
    for i, d in enumerate(g):
        if d.month == 4:
            spy.loc[d] = 0.06 if i % 2 else -0.06                       # aprile: giorni enormi che si alternano
    assert p037b.mese_della_crisi(spy) == (2025, 4)


def test_esame_tre_condizioni():
    g = _giorni(60)
    spy = pd.Series([0.01 if i % 2 else -0.009 for i in range(60)], index=g)
    for i, d in enumerate(g):
        if d.month == 4:
            spy.loc[d] = 0.06 if i % 2 else -0.06
    parte = pd.Series(-0.0001, index=g)
    for i, d in enumerate(g):
        if d.month == 4:
            parte.loc[d] = 0.01 if i % 3 else 0.0                       # guadagna nella crisi, costa poco negli altri giorni
    e = p037b.esame(parte, parte - 0.0001, spy)
    assert e["mese"] == (2025, 4) and e["c1"] and e["c2"]
    e2 = p037b.esame(pd.Series(-0.001, index=g), pd.Series(-0.002, index=g), spy)
    assert not e2["c1"] and not e2["c2"] and not e2["passa"]
