"""Test del modello di costo condiviso: spread di liquidità e funding con segno."""
from bot.core.costs import funding_fraction, liquidity_spread


def test_liquidity_spread_scales_with_volume():
    # più liquida = spread minore (monotono decrescente)
    assert liquidity_spread(300_000_000) < liquidity_spread(60_000_000)
    assert liquidity_spread(60_000_000) < liquidity_spread(20_000_000)
    assert liquidity_spread(20_000_000) < liquidity_spread(1_000_000)
    assert liquidity_spread(None) == liquidity_spread(0.0)


def test_funding_long_pays_short_receives_at_positive_rate():
    # tasso positivo: il LONG paga (costo > 0), lo SHORT incassa (costo < 0)
    assert funding_fraction(0.0001, 8.0, long=True) > 0
    assert funding_fraction(0.0001, 8.0, long=False) < 0
    # e sono simmetrici in modulo
    assert abs(funding_fraction(0.0001, 8.0, True) + funding_fraction(0.0001, 8.0, False)) < 1e-12


def test_funding_flips_sign_with_negative_rate():
    # tasso negativo: si inverte -> il LONG incassa, lo SHORT paga
    assert funding_fraction(-0.0002, 8.0, long=True) < 0
    assert funding_fraction(-0.0002, 8.0, long=False) > 0


def test_funding_proportional_to_hours():
    # 16h = due intervalli da 8h -> doppio di 8h
    a = funding_fraction(0.0001, 8.0, True)
    b = funding_fraction(0.0001, 16.0, True)
    assert abs(b - 2 * a) < 1e-12


def test_funding_none_rate_uses_default():
    # tasso mancante -> ricade sul default fornito (magnitudine), stesso segno
    assert funding_fraction(None, 8.0, True, default_rate=0.0003) > 0
    assert funding_fraction(None, 8.0, True, default_rate=0.0003) == funding_fraction(0.0003, 8.0, True)
