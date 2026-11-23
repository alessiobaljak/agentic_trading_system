"""Le parti senza rete della prova 48: il giorno della scadenza, la finestra, il conto."""
from datetime import date, timedelta

import pandas as pd
import pytest

from stock.prove import p048


def feriali(dal, al, chiusi=()):
    d, out = dal, []
    while d <= al:
        if d.weekday() < 5 and d not in chiusi:
            out.append(d)
        d += timedelta(days=1)
    return out


def test_terzo_venerdi_e_venerdi_santo():
    assert p048.terzo_venerdi(2019, 4) == date(2019, 4, 19)
    cal = feriali(date(2019, 4, 1), date(2019, 4, 30), chiusi={date(2019, 4, 19)})         # venerdì santo: borsa chiusa
    assert p048.scadenze(cal) == [date(2019, 4, 18)]                                       # la scadenza va al giovedì
    assert p048.finestre_scadenza(cal) == [(date(2019, 4, 12), date(2019, 4, 18))]         # dal venerdì prima al giovedì


def test_lunedi_festivo_entrata_il_venerdi_prima():
    cal = feriali(date(2019, 2, 1), date(2019, 2, 28), chiusi={date(2019, 2, 18)})         # il terzo venerdì è il 15
    assert p048.finestre_scadenza(cal) == [(date(2019, 2, 8), date(2019, 2, 15))]


def test_conto_dentro_solo_nella_finestra():
    cal = feriali(date(2019, 4, 8), date(2019, 4, 26), chiusi={date(2019, 4, 19)})
    ch = pd.Series([100.0 + i for i in range(len(cal))], index=cal)
    fin = p048.finestre_scadenza(cal)
    g = p048.conto(ch, fin, costi=False)
    dentro = [d for d in g.index if g.loc[d] != 0]
    assert dentro == [date(2019, 4, d) for d in (15, 16, 17, 18)]                         # dal giorno dopo l'entrata alla scadenza
    assert g.loc[date(2019, 4, 15)] == pytest.approx(0.98 * (105.0 / 104.0 - 1))
    assert p048.conto(ch, fin).loc[date(2019, 4, 12)] < 0                                  # il giorno dell'entrata paga i costi
