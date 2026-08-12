"""REGIME CON CONFIDENZA — l'etichetta piu' quanto e' netta.

Quattro etichette secche non distinguono un trend conclamato da uno che sta per
girare: la stessa parola descrive due situazioni opposte per rischio. La
confidenza misura la DISTANZA dalle soglie di decisione — vicino al confine
significa che una piccola variazione cambierebbe il regime, cioe' che l'etichetta
vale poco.

Due vincoli che questi test difendono.

1. L'ETICHETTA NON CAMBIA. `detect()` e' usata IDENTICA da backtest e live:
   qualunque divergenza romperebbe la parita' gate<->paper, che e' l'unica cosa
   che oggi funziona con precisione. `detect_detailed` la RIUSA, non la ricalcola.

2. LA CONFIDENZA NON TOCCA ANCORA NULLA. Il prompt di upgrade propone di legarla
   al size_multiplier; sarebbe la stessa mossa che ci e' costata cara, agire su un
   numero mai verificato. Prima si misura se predice l'esito — come gia' si fa per
   la confidenza dei segnali — e per renderlo possibile il valore viaggia su ogni
   trade chiuso.
"""
import pytest

from bot.agents.regime_detector import RegimeDetector
from bot.core.models import AssetSnapshot, IndicatorSnapshot, Regime


def _btc(*, ema_fast=100.0, ema_slow=100.0, atr=1.0, close=100.0, macd_hist=0.0):
    return AssetSnapshot(symbol="BTCUSDT", price=close, indicators={
        "1h": IndicatorSnapshot(timeframe="1h", ema_fast=ema_fast, ema_slow=ema_slow,
                                atr=atr, close=close, macd_hist=macd_hist)})


D = RegimeDetector()


# ---- 1) l'etichetta resta quella che opera --------------------------------- #
@pytest.mark.parametrize("kw", [
    dict(ema_fast=102.0, ema_slow=100.0, macd_hist=0.5),      # bull
    dict(ema_fast=98.0, ema_slow=100.0, macd_hist=-0.5),      # bear
    dict(ema_fast=100.05, ema_slow=100.0),                    # sideways
    dict(atr=5.0),                                            # high uncertainty
    dict(ema_fast=102.0, ema_slow=100.0, macd_hist=-0.5),     # EMA/momentum discordi
])
def test_detailed_never_disagrees_with_detect(kw):
    a = _btc(**kw)
    assert D.detect_detailed(a).primary is D.detect(a)


def test_detailed_agrees_also_with_fear_greed_in_play():
    a = _btc(ema_fast=100.05, ema_slow=100.0)
    for fng in (5, 50, 95):
        assert D.detect_detailed(a, fng).primary is D.detect(a, fng)


# ---- 2) la confidenza misura la distanza dalle soglie ---------------------- #
def test_a_clear_trend_is_more_confident_than_a_borderline_one():
    netto = D.detect_detailed(_btc(ema_fast=105.0, ema_slow=100.0, macd_hist=1.0))
    borderline = D.detect_detailed(_btc(ema_fast=100.45, ema_slow=100.0, macd_hist=0.01))
    assert netto.primary is borderline.primary is Regime.BULL_TRENDING
    assert netto.confidence > borderline.confidence


def test_extreme_volatility_is_more_confident_than_a_marginal_one():
    estrema = D.detect_detailed(_btc(atr=10.0))
    marginale = D.detect_detailed(_btc(atr=2.6))
    assert estrema.primary is marginale.primary is Regime.HIGH_UNCERTAINTY
    assert estrema.confidence > marginale.confidence


def test_sideways_is_more_confident_when_emas_are_closer():
    stretto = D.detect_detailed(_btc(ema_fast=100.001, ema_slow=100.0))
    largo = D.detect_detailed(_btc(ema_fast=100.35, ema_slow=100.0))
    assert stretto.primary is largo.primary is Regime.SIDEWAYS
    assert stretto.confidence > largo.confidence


def test_confidence_is_always_a_fraction():
    for kw in (dict(), dict(atr=99.0), dict(ema_fast=200.0, ema_slow=1.0, macd_hist=50.0)):
        assert 0.0 <= D.detect_detailed(_btc(**kw)).confidence <= 1.0


def test_missing_data_means_no_confidence_and_says_why():
    a = AssetSnapshot(symbol="BTCUSDT", price=100.0)
    r = D.detect_detailed(a)
    assert r.primary is Regime.HIGH_UNCERTAINTY
    assert r.confidence == 0.0
    assert r.conflicting and "insufficienti" in r.conflicting[0]


# ---- 3) segnali a favore e contro ------------------------------------------ #
def test_supporting_and_conflicting_signals_are_reported():
    r = D.detect_detailed(_btc(ema_fast=105.0, ema_slow=100.0, macd_hist=1.0), 50)
    assert any("EMA" in s for s in r.supporting)
    assert any("Fear&Greed neutro" in s for s in r.supporting)
    r2 = D.detect_detailed(_btc(ema_fast=105.0, ema_slow=100.0, macd_hist=1.0), 95)
    assert any("Fear&Greed estremo" in s for s in r2.conflicting)
    assert r2.confidence < r.confidence      # il conflitto abbassa la confidenza


def test_flat_momentum_in_a_trend_is_flagged_as_conflicting():
    r = D.detect_detailed(_btc(ema_fast=105.0, ema_slow=100.0, macd_hist=0.0))
    assert any("momentum" in c for c in r.conflicting)


def test_high_volatility_inside_a_trend_becomes_the_secondary_regime():
    """Un trend con volatilita' vicina alla soglia non e' un trend qualunque:
    il secondario lo qualifica senza cambiare l'etichetta che opera."""
    r = D.detect_detailed(_btc(ema_fast=105.0, ema_slow=100.0, macd_hist=1.0, atr=2.2))
    assert r.primary is Regime.BULL_TRENDING
    assert r.secondary is Regime.HIGH_UNCERTAINTY


def test_as_dict_has_the_shape_the_dashboard_reads():
    d = D.detect_detailed(_btc(ema_fast=105.0, ema_slow=100.0, macd_hist=1.0)).as_dict()
    assert set(d) == {"primary_regime", "confidence", "secondary_regime",
                      "supporting_signals", "conflicting_signals"}
    assert isinstance(d["primary_regime"], str)
