"""Le parti senza rete della prova 53: il lato della notizia e il conto con il segno."""
from datetime import date, timedelta

import pytest

from stock.prove import p053


def test_lato():
    assert p053.lato("Goldman Upgrades Acme To Buy") == 1
    assert p053.lato("Acme Downgraded To Neutral At Citi") == -1
    assert p053.lato("Acme: One Upgrade, One Downgrade Today") == 0
    assert p053.lato("Acme Reports Q3 Earnings") == 0


def test_conto_promozione_e_bocciatura():
    g = [date(2023, 1, 2) + timedelta(days=i) for i in range(30)]
    su = p053.Operazione("A", 1, g[0], 100.0, 1.0, g[20], 110.0, 1.0, 400.0, 1.0, 404.0, 1.0)
    giu = p053.Operazione("B", -1, g[0], 100.0, 1.0, g[20], 110.0, 1.0, 400.0, 1.0, 404.0, 1.0)
    a = p053.conto([su], g, costi=False)
    b = p053.conto([giu], g, costi=False)
    n, m = 50, 12                                                         # 5'000 dollari nel titolo, 12 SPY da 400
    assert a.loc[g[20]] == pytest.approx((n * 100 * 0.10 - m * 400 * 0.01) / 100_000)
    assert b.loc[g[20]] == pytest.approx(-(n * 100 * 0.10 - m * 400 * 0.01) / 100_000)
    assert p053.conto([su], g).loc[g[20]] < a.loc[g[20]]                  # i costi
