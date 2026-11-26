"""Le parti senza rete della prova 52: la quota dal giorno prima e il conto."""
from datetime import date

import pandas as pd
import pytest

from stock.prove import p052


def test_quota_dalla_curva_del_giorno_prima():
    cal = [date(2020, 1, d) for d in (6, 7, 8, 9)]
    normale = pd.Series([True, False, True], index=cal[:3])
    q = p052.quote(normale, cal)
    assert q.loc[date(2020, 1, 7)] == p052.QUOTA                 # il 6 era normale
    assert q.loc[date(2020, 1, 8)] == 0.0                         # il 7 rovesciata
    assert q.loc[date(2020, 1, 9)] == p052.QUOTA
    assert date(2020, 1, 6) not in q.index


def test_conto_dentro_dal_giorno_dopo_la_decisione():
    cal = [date(2020, 1, d) for d in (6, 7, 8, 9)]
    ch = pd.Series([10.0, 11.0, 12.0, 6.0], index=cal)
    q = pd.Series({date(2020, 1, 7): 0.98, date(2020, 1, 8): 0.98, date(2020, 1, 9): 0.0})
    g = p052.conto(ch, q, costi=False)
    assert g.loc[date(2020, 1, 7)] == 0.0                         # si entra alla chiusura del 7
    assert g.loc[date(2020, 1, 8)] == pytest.approx(0.98 * (12 / 11 - 1))
    assert g.loc[date(2020, 1, 9)] == pytest.approx(0.98 * (6 / 12 - 1))  # il crollo del 9 si prende: si esce solo alla chiusura
    assert p052.conto(ch, q).loc[date(2020, 1, 7)] < 0            # l'ingresso paga i costi
