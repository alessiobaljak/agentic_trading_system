"""SIZING E LEVA — due difetti che rendevano inerti due manopole.

1. RISCHIO. L'utente imposta `risk_per_trade` (es. 1%) e il sistema dimensiona la
   posizione perche' toccare lo stop costi esattamente quello. Ma subito dopo il
   cap per-posizione limita il nozionale, e con i valori reali (equity 1000, leva
   2, cap 10% -> nozionale 200) il cap morde SEMPRE: un rischio dell'1% su uno
   stop del 2% chiederebbe 500 di nozionale. Risultato: si rischia ~0.35% invece
   dell'1%, e la cifra oscilla con la volatilita' — piu' lo stop e' largo, MENO si
   rischia, l'opposto di come dovrebbe comportarsi un controllo del rischio.
   Il cap ha una ragione legittima (far coesistere piu' posizioni), quindi non si
   toglie: si rende VISIBILE il rischio effettivo, che finora nessuno vedeva.

2. LEVA. `round()` in Python arrotonda alla pari: round(2.5) == 2. Con leva base 2
   il massimo assoluto dell'allocazione e' esattamente 2.5, quindi il gradino 3x
   era irraggiungibile e il moltiplicatore poteva solo frenare, mai premiare.
"""
import pytest

from bot.config import settings
from bot.core.models import (
    AssetSnapshot, Direction, IndicatorSnapshot, OrchestratorDecision, Regime,
    RiskSettings,
)
from bot.risk.risk_manager import RiskManager


def _asset(price=100.0, atr=2.0, vol=3e8):
    return AssetSnapshot(
        symbol="BTCUSDT", price=price, regime=Regime.SIDEWAYS, volume_24h=vol,
        indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=atr, close=price)},
    )


def _decision(stop=98.0, target=106.0):
    return OrchestratorDecision(
        asset="BTCUSDT", strategy="s", direction=Direction.LONG,
        size_multiplier=1.0, confidence=60.0, reasoning="t",
        suggested_stop=stop, suggested_target=target,
    )


def _compute(monkeypatch, *, equity=1000.0, frac=0.10, lev=2.0, risk=0.01,
             stop=98.0, lev_mult=1.0, risk_mult=1.0):
    monkeypatch.setattr(settings, "MAX_POSITION_EQUITY_FRACTION", frac)
    return RiskManager().resolve_effective_params(
        _decision(stop=stop), RiskSettings(leverage=lev, risk_per_trade=risk),
        _asset(), account_equity=equity, volatility_sigma=1.0,
        risk_mult=risk_mult, lev_mult=lev_mult,
    )


# ---- 1) il rischio effettivo e' visibile ----------------------------------- #
def test_effective_risk_is_reported_when_the_cap_bites(monkeypatch):
    """Configurazione reale della VPS: equity 1000, leva 2, cap 10%, stop a -2%."""
    p = _compute(monkeypatch)
    assert p.capped_by_position_limit is True
    # nozionale bloccato a equity x leva x frac = 200
    assert p.notional == pytest.approx(200.0)
    # rischio VERO: 200 x 2% = 4 su 1000 = 0.4%, non l'1% richiesto
    assert p.risk_effective_pct == pytest.approx(0.004, rel=1e-6)
    assert p.risk_per_trade == pytest.approx(0.01)
    assert any("rischio effettivo" in n for n in p.notes)


def test_effective_risk_matches_the_request_when_the_cap_does_not_bite(monkeypatch):
    # cap largo: la size la decide il rischio, come da progetto
    p = _compute(monkeypatch, frac=1.0)
    assert p.capped_by_position_limit is False
    assert p.risk_effective_pct == pytest.approx(p.risk_per_trade, rel=1e-6)


def test_wider_stop_paradoxically_risks_less_under_the_cap(monkeypatch):
    """Il sintomo piu' insidioso: sotto il cap il nozionale e' fisso, quindi il
    rischio in dollari e' proporzionale alla DISTANZA dello stop. Uno stop largo
    (coin volatile) rischia di piu', uno stretto di meno — ma nessuno dei due
    rispetta l'impostazione, e la differenza fra le coppie non e' voluta."""
    stretto = _compute(monkeypatch, stop=99.0)     # -1%
    largo = _compute(monkeypatch, stop=96.0)       # -4%
    assert stretto.capped_by_position_limit and largo.capped_by_position_limit
    assert stretto.risk_effective_pct == pytest.approx(0.002, rel=1e-6)
    assert largo.risk_effective_pct == pytest.approx(0.008, rel=1e-6)
    # entrambi lontani dall'1% richiesto, in direzioni opposte
    assert stretto.risk_effective_pct < 0.01 < largo.risk_effective_pct * 2


def test_effective_risk_is_zero_safe_without_equity(monkeypatch):
    p = _compute(monkeypatch, equity=0.0)
    assert p.risk_effective_pct == 0.0


# ---- 2) la leva puo' finalmente salire ------------------------------------- #
def test_leverage_can_reach_the_step_up(monkeypatch):
    """Con base 2 e allocazione al massimo (1.25) si arriva a 2.5: prima
    round(2.5) tornava 2 e il 3x non era mai raggiungibile."""
    p = _compute(monkeypatch, lev=2.0, lev_mult=1.25)
    assert p.leverage == 3.0


def test_leverage_rounds_down_below_the_midpoint(monkeypatch):
    p = _compute(monkeypatch, lev=2.0, lev_mult=1.2)      # 2.4 -> 2
    assert p.leverage == 2.0


def test_leverage_never_below_one_nor_above_the_hard_cap(monkeypatch):
    assert _compute(monkeypatch, lev=1.0, lev_mult=0.1).leverage == 1.0
    assert _compute(monkeypatch, lev=5.0, lev_mult=1.3).leverage == 5.0


def test_leverage_stays_integer_for_the_exchange(monkeypatch):
    for m in (0.7, 0.83, 1.0, 1.17, 1.25):
        lev = _compute(monkeypatch, lev=3.0, lev_mult=m).leverage
        assert lev == int(lev), f"leva non intera con lev_mult={m}"
