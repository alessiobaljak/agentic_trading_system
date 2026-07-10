"""Strategia — Momentum / Trend-Continuation.

Entra SULLA forza di un trend gia' in corso invece di evitarlo: trend forte (ADX),
prezzo sopra/sotto entrambe le EMA allineate, MACD in spinta, volume di conferma.
Cattura le coin che 'stanno correndo' (es. +6% con volume) — proprio i movimenti
che trend_following scarta perche' richiede RSI capato (<70).
"""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext, register_strategy


@register_strategy
class Momentum(Strategy):
    name = "momentum"
    active_regimes = {Regime.BULL_TRENDING, Regime.BEAR_TRENDING}
    description = "Trend-continuation: ADX forte + prezzo sopra/sotto EMA + MACD in spinta + volume."

    default_params = {
        "adx_min": 25.0,       # forza minima del trend (sotto = choppy, si salta)
        "vol_mult": 1.2,       # volume > vol_mult * media (partecipazione confermata)
        "atr_mult_stop": 1.5,
        "rr": 2.0,
    }
    param_grid = {
        "adx_min": [20.0, 25.0, 30.0],
        "vol_mult": [1.0, 1.2, 1.5],
        "rr": [1.5, 2.0, 2.5, 3.0],
        "atr_mult_stop": [1.0, 1.5, 2.0],
    }

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind(self._tf)
        if not i:
            return None
        if None in (i.ema_fast, i.ema_slow, i.adx, i.macd_hist, i.close):
            return None

        adx_min = self.p("adx_min")
        if i.adx < adx_min:
            return None  # niente trend forte -> non e' momentum, non entriamo

        vol_ok = (i.volume is not None and i.volume_sma not in (None, 0)
                  and i.volume > self.p("vol_mult") * i.volume_sma)
        if not vol_ok:
            return None

        am, rr = self.p("atr_mult_stop"), self.p("rr")
        # piu' forte il trend, piu' alta la confidenza (55..80)
        conf = 55 + min(25.0, i.adx - adx_min)

        # struttura rialzista: prezzo sopra entrambe le EMA, EMA allineate, MACD>0
        if i.close > i.ema_fast > i.ema_slow and i.macd_hist > 0:
            stop, target = self._atr_stop_target(asset, Direction.LONG, atr_mult_stop=am, rr=rr)
            return self._signal(asset, Direction.LONG, conf,
                                "Trend forte (ADX) + prezzo sopra EMA + MACD in spinta + volume",
                                stop, target)
        # struttura ribassista speculare
        if i.close < i.ema_fast < i.ema_slow and i.macd_hist < 0:
            stop, target = self._atr_stop_target(asset, Direction.SHORT, atr_mult_stop=am, rr=rr)
            return self._signal(asset, Direction.SHORT, conf,
                                "Trend forte (ADX) + prezzo sotto EMA + MACD negativo + volume",
                                stop, target)
        return None
