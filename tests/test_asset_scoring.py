"""ASSET SCORING — sei fattori spiegabili, e due grandezze che NON sono "piu' e' meglio".

Il punteggio dice quanto un asset e' adatto (0..1) e il dettaglio dice perche'.
Serve soprattutto a rendere leggibile la selezione: oggi non filtra nulla, ma
viene scritto a ogni scan cosi' nel tempo si potra' verificare se predice davvero
l'esito invece di darlo per scontato.

Due scelte che questi test difendono, perche' sono facili da rompere per
distrazione:

* FUNDING e VOLATILITA' hanno un OTTIMO, non una direzione. Un funding estremo e'
  un costo di mantenimento che erode ogni trade tenuto ore, non un'opportunita';
  una volatilita' altissima fa saltare gli stop per rumore. Trattarli come "piu'
  e' meglio" premierebbe esattamente gli asset piu' costosi da tradare.

* Le ESCLUSIONI sono inerti sotto BACKTEST_PARITY. Il gate non le modella:
  filtrare in live cio' che il gate ha validato ricrea la divergenza fra promesso
  ed eseguito che ci e' gia' costata cara.
"""
import pytest

from bot.agents.market_scanner import WEIGHTS, MarketScanner
from bot.config import settings
from bot.core.models import AssetSnapshot, IndicatorSnapshot

S = MarketScanner.__new__(MarketScanner)      # niente rete: serve solo _score


def _snap(*, price=100.0, vol24=3e8, funding=0.0, atr=1.5, rsi=50.0,
          ema_fast=100.0, ema_slow=100.0, volume=None, volume_sma=None, sent=None):
    return AssetSnapshot(
        symbol="XUSDT", price=price, volume_24h=vol24, funding_rate=funding,
        sentiment_score=sent,
        indicators={settings.ORCHESTRATOR_TIMEFRAME: IndicatorSnapshot(
            timeframe=settings.ORCHESTRATOR_TIMEFRAME, atr=atr, close=price, rsi=rsi,
            ema_fast=ema_fast, ema_slow=ema_slow, volume=volume, volume_sma=volume_sma)})


def test_weights_sum_to_one_so_the_score_is_a_fraction():
    assert sum(WEIGHTS.values()) == pytest.approx(1.0)


def test_score_and_components_stay_in_range():
    for kw in (dict(), dict(funding=0.01), dict(atr=50.0), dict(vol24=1e3),
               dict(ema_fast=200.0, ema_slow=1.0, rsi=99.0)):
        score, comp = S._score(_snap(**kw))
        assert 0.0 <= score <= 1.0
        assert all(0.0 <= v <= 1.0 for v in comp.values()), comp
        assert set(comp) == set(WEIGHTS)


# ---- funding: vicino a zero e' MEGLIO -------------------------------------- #
def test_extreme_funding_scores_worse_than_neutral_funding():
    neutro = S._score(_snap(funding=0.0))[1]["funding"]
    estremo = S._score(_snap(funding=0.003))[1]["funding"]
    assert neutro > estremo
    assert neutro == pytest.approx(1.0)


def test_funding_penalty_is_symmetric():
    a = S._score(_snap(funding=0.001))[1]["funding"]
    b = S._score(_snap(funding=-0.001))[1]["funding"]
    assert a == pytest.approx(b)


# ---- volatilita': una FASCIA, non una direzione ---------------------------- #
def test_volatility_has_an_optimum_not_a_direction():
    ideale = settings.ASSET_IDEAL_ATR_PCT
    buona = S._score(_snap(atr=100 * ideale))[1]["volatility"]
    troppa = S._score(_snap(atr=100 * ideale * 3))[1]["volatility"]
    poca = S._score(_snap(atr=100 * ideale * 0.05))[1]["volatility"]
    assert buona > troppa and buona > poca


# ---- volume: il RAPPORTO, non il valore assoluto --------------------------- #
def test_unusual_volume_beats_merely_large_volume():
    """Il volume assoluto premia sempre le stesse major; il rapporto col proprio
    passato dice se ORA sta succedendo qualcosa."""
    calmo = S._score(_snap(volume=100.0, volume_sma=100.0))[1]["volume"]
    attivo = S._score(_snap(volume=200.0, volume_sma=100.0))[1]["volume"]
    assert attivo > calmo


def test_volume_falls_back_to_absolute_when_the_average_is_missing():
    grande = S._score(_snap(vol24=5e8))[1]["volume"]
    piccolo = S._score(_snap(vol24=2e6))[1]["volume"]
    assert grande > piccolo


# ---- social assente = neutro, non penalita' -------------------------------- #
def test_missing_sentiment_is_neutral_not_a_silent_penalty():
    """Senza chiave LunarCrush il dato manca per TUTTI: valeva 0.3, cioe' una
    penalita' uguale ovunque che spostava il punteggio senza informare."""
    assert S._score(_snap(sent=None))[1]["social"] == pytest.approx(0.5)
    assert S._score(_snap(sent=0.9))[1]["social"] == pytest.approx(0.9)


# ---- liquidita' ------------------------------------------------------------ #
def test_liquid_assets_score_higher_on_liquidity():
    liquido = S._score(_snap(vol24=5e8))[1]["liquidity"]
    sottile = S._score(_snap(vol24=1e6))[1]["liquidity"]
    assert liquido > sottile


# ---- esclusioni strutturali ------------------------------------------------ #
def test_no_exclusions_for_a_healthy_asset():
    assert MarketScanner.exclusions(_snap()) == []


def test_unsustainable_funding_is_excluded():
    assert any("funding" in r for r in MarketScanner.exclusions(_snap(funding=0.01)))
    assert any("funding" in r for r in MarketScanner.exclusions(_snap(funding=-0.01)))


def test_repeated_stops_put_the_coin_in_quarantine(monkeypatch):
    monkeypatch.setattr(settings, "ASSET_BLACKLIST_STOPS", 3)
    assert MarketScanner.exclusions(_snap(), recent_stops=2) == []
    assert any("quarantena" in r for r in MarketScanner.exclusions(_snap(), recent_stops=3))


def test_volume_floor_is_disabled_by_default():
    """Questo sistema ha sostituito il filtro netto sul volume col modello di
    costo: un pavimento attivo di default taglierebbe l'universo validato."""
    assert settings.ASSET_MIN_VOLUME_24H == 0
    assert MarketScanner.exclusions(_snap(vol24=1e5)) == []


def test_volume_floor_works_when_switched_on(monkeypatch):
    monkeypatch.setattr(settings, "ASSET_MIN_VOLUME_24H", 1e8)
    assert any("volume" in r for r in MarketScanner.exclusions(_snap(vol24=1e6)))


def test_missing_funding_data_does_not_exclude():
    """Assenza di dato non e' un motivo di esclusione: sarebbe un blocco silenzioso
    ogni volta che l'API non risponde."""
    assert MarketScanner.exclusions(_snap(funding=None)) == []
