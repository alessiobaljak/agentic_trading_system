"""
Regime Detector — classifica il mercato ogni ora in:
  BULL_TRENDING / BEAR_TRENDING / SIDEWAYS / HIGH_UNCERTAINTY

Usa BTC come proxy del mercato (l'asset di riferimento) combinando:
  * direzione e separazione delle EMA 9/21 su 1h (trend)
  * pendenza/forza del trend (MACD histogram)
  * volatilità relativa (ATR/prezzo) per distinguere "high uncertainty"
  * coerenza con il Fear & Greed
"""
from __future__ import annotations

from typing import Optional

from bot.core.models import AssetSnapshot, Regime


class RegimeDetector:
    REF_SYMBOL = "BTCUSDT"
    HIGH_VOL_ATR_PCT = 0.025   # ATR/prezzo > 2.5% su 1h -> alta incertezza
    TREND_SEPARATION = 0.004   # |ema_fast-ema_slow|/prezzo > 0.4% -> trend chiaro

    def detect(self, btc: AssetSnapshot, fear_greed: Optional[int] = None) -> Regime:
        i = btc.ind("1h")
        if not i or None in (i.ema_fast, i.ema_slow, i.atr, i.close) or i.close == 0:
            return Regime.HIGH_UNCERTAINTY

        atr_pct = i.atr / i.close
        separation = abs(i.ema_fast - i.ema_slow) / i.close
        up = i.ema_fast > i.ema_slow
        momentum = i.macd_hist or 0.0

        # volatilità estrema -> incertezza, indipendentemente dalla direzione
        if atr_pct > self.HIGH_VOL_ATR_PCT:
            return Regime.HIGH_UNCERTAINTY

        # trend chiaro: EMA ben separate e momentum coerente
        if separation > self.TREND_SEPARATION:
            if up and momentum >= 0:
                return Regime.BULL_TRENDING
            if (not up) and momentum <= 0:
                return Regime.BEAR_TRENDING
            # EMA dicono una cosa, momentum un'altra -> incertezza
            return Regime.HIGH_UNCERTAINTY

        # EMA vicine, bassa volatilità -> mercato laterale
        # rifinitura col Fear & Greed: valori estremi suggeriscono incertezza
        if fear_greed is not None and (fear_greed <= 15 or fear_greed >= 85):
            return Regime.HIGH_UNCERTAINTY
        return Regime.SIDEWAYS
