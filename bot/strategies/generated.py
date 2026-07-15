"""
Strategie GENERATE — il "cervello" che inventa nuove strategie.

Una strategia generata NON è codice nuovo: è una combinazione DICHIARATIVA di
"feature" (mattoncini booleani su indicatori), interpretata da un unico motore
verificato (`GeneratedStrategy`). Questo permette di crearne a decine/centinaia
in sicurezza (nessun codice arbitrario eseguito) e di validarle con lo STESSO
gate del backtest (walk-forward OOS, al netto dei costi) delle 6 strategie base.

Spec di una strategia (pura DATA, salvabile su Firebase):
    {
      "id": "gen_ab12cd34",
      "features": [
          {"kind": "rsi_extreme", "low": 30, "high": 70},
          {"kind": "bb_touch"}
      ],
      "volume_mult": 0.0,        # >0 = filtro volume (volume > volume_sma*mult)
      "atr_mult_stop": 1.5,
      "rr": 2.0
    }

Ogni feature vota una direzione: (long_ok, short_ok). La strategia entra LONG se
TUTTE le feature sono long_ok (e simmetrico per lo SHORT). Niente contraddizioni.
"""
from __future__ import annotations

import hashlib
import json
from typing import Optional

from bot.core.models import AssetSnapshot, Direction, IndicatorSnapshot, Regime, StrategySignal
from bot.strategies.base import Strategy, StrategyContext

ALL_REGIMES = {Regime.BULL_TRENDING, Regime.BEAR_TRENDING, Regime.SIDEWAYS, Regime.HIGH_UNCERTAINTY}


def _feat_rsi_extreme(i: IndicatorSnapshot, price: float, f: dict):
    if i.rsi is None:
        return None
    return (i.rsi <= f.get("low", 30.0), i.rsi >= f.get("high", 70.0))


def _feat_rsi_momentum(i: IndicatorSnapshot, price: float, f: dict):
    if i.rsi is None:
        return None
    mid = f.get("mid", 50.0)
    return (i.rsi >= mid, i.rsi <= mid)


def _feat_bb_touch(i: IndicatorSnapshot, price: float, f: dict):
    if None in (i.bb_upper, i.bb_lower):
        return None
    return (price <= i.bb_lower, price >= i.bb_upper)


def _feat_bb_break(i: IndicatorSnapshot, price: float, f: dict):
    if None in (i.bb_upper, i.bb_lower):
        return None
    return (price >= i.bb_upper, price <= i.bb_lower)


def _feat_vwap_momentum(i: IndicatorSnapshot, price: float, f: dict):
    if i.vwap is None:
        return None
    return (price > i.vwap, price < i.vwap)


def _feat_vwap_reversion(i: IndicatorSnapshot, price: float, f: dict):
    if i.vwap is None:
        return None
    return (price < i.vwap, price > i.vwap)


def _feat_ema_cross(i: IndicatorSnapshot, price: float, f: dict):
    if None in (i.ema_fast, i.ema_slow):
        return None
    return (i.ema_fast > i.ema_slow, i.ema_fast < i.ema_slow)


def _feat_macd_cross(i: IndicatorSnapshot, price: float, f: dict):
    if None in (i.macd, i.macd_signal):
        return None
    return (i.macd > i.macd_signal, i.macd < i.macd_signal)


def _feat_macd_hist(i: IndicatorSnapshot, price: float, f: dict):
    if i.macd_hist is None:
        return None
    return (i.macd_hist > 0, i.macd_hist < 0)


def _feat_price_ema(i: IndicatorSnapshot, price: float, f: dict):
    if i.ema_slow is None:
        return None
    return (price > i.ema_slow, price < i.ema_slow)


def _feat_macd_zero(i: IndicatorSnapshot, price: float, f: dict):
    if i.macd is None:
        return None
    return (i.macd > 0, i.macd < 0)


def _feat_price_bb_mid(i: IndicatorSnapshot, price: float, f: dict):
    if i.bb_mid is None:
        return None
    return (price > i.bb_mid, price < i.bb_mid)


def _feat_stoch_extreme(i: IndicatorSnapshot, price: float, f: dict):
    if i.stoch_k is None:
        return None
    return (i.stoch_k <= f.get("low", 20.0), i.stoch_k >= f.get("high", 80.0))


def _feat_stoch_momentum(i: IndicatorSnapshot, price: float, f: dict):
    if None in (i.stoch_k, i.stoch_d):
        return None
    return (i.stoch_k > i.stoch_d, i.stoch_k < i.stoch_d)


# nome feature -> (funzione, è_direzionale). Le non direzionali sono filtri.
FEATURE_LIBRARY = {
    "rsi_extreme": _feat_rsi_extreme,
    "rsi_momentum": _feat_rsi_momentum,
    "bb_touch": _feat_bb_touch,
    "bb_break": _feat_bb_break,
    "vwap_momentum": _feat_vwap_momentum,
    "vwap_reversion": _feat_vwap_reversion,
    "ema_cross": _feat_ema_cross,
    "macd_cross": _feat_macd_cross,
    "macd_hist": _feat_macd_hist,
    "price_ema": _feat_price_ema,
    "macd_zero": _feat_macd_zero,
    "price_bb_mid": _feat_price_bb_mid,
    "stoch_extreme": _feat_stoch_extreme,
    "stoch_momentum": _feat_stoch_momentum,
}


def spec_id(spec: dict) -> str:
    """Hash stabile della LOGICA (feature+soglie), così la stessa strategia ha
    sempre lo stesso id tra run (la validazione cumulativa funziona per nome).
    Include il TIMEFRAME: la stessa logica a 15m e a 1h sono strategie DIVERSE
    (SL/TP/durate diverse) — senza, una spec rigenerata dopo un cambio timeframe
    erediterebbe pesi e storia della gemella dell'era precedente."""
    from bot.config import settings
    payload = {
        "features": sorted((f.get("kind"), tuple(sorted((k, v) for k, v in f.items() if k != "kind")))
                           for f in spec.get("features", [])),
        "volume_mult": spec.get("volume_mult", 0.0),
        "min_adx": spec.get("min_adx", 0.0),
        "atr_mult_stop": spec.get("atr_mult_stop"),
        "rr": spec.get("rr"),
        "timeframe": settings.ORCHESTRATOR_TIMEFRAME,
    }
    h = hashlib.sha1(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:8]
    return f"gen_{h}"


class GeneratedStrategy(Strategy):
    """Interpreta una spec dichiarativa. Attiva in tutti i regimi: dove funziona
    lo decide il backtest, non una teoria a priori."""

    def __init__(self, spec: dict) -> None:
        super().__init__(spec.get("params"))
        self.spec = spec
        self.name = spec.get("id") or spec_id(spec)
        self.active_regimes = ALL_REGIMES
        self.description = self._describe()
        self._features = spec.get("features", [])
        self._volume_mult = float(spec.get("volume_mult", 0.0) or 0.0)
        self._min_adx = float(spec.get("min_adx", 0.0) or 0.0)
        self._atr_mult_stop = float(spec.get("atr_mult_stop", 1.5))
        self._rr = float(spec.get("rr", 2.0))

    def _describe(self) -> str:
        parts = []
        for f in self.spec.get("features", []):
            extra = " ".join(f"{k}={v}" for k, v in f.items() if k != "kind")
            parts.append(f"{f.get('kind')}{(' ' + extra) if extra else ''}")
        return " AND ".join(parts) or "vuota"

    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        i = asset.ind(self._tf)
        if i is None or not self._features:
            return None
        price = asset.price
        long_ok, short_ok = True, True
        for f in self._features:
            fn = FEATURE_LIBRARY.get(f.get("kind"))
            if fn is None:
                return None
            res = fn(i, price, f)
            if res is None:
                return None  # dati indicatore mancanti -> niente segnale
            long_ok = long_ok and res[0]
            short_ok = short_ok and res[1]

        # filtro volume opzionale (gate su entrambe le direzioni)
        if self._volume_mult > 0:
            if i.volume is None or i.volume_sma is None or i.volume <= i.volume_sma * self._volume_mult:
                return None
        # filtro ADX opzionale: opera solo se il trend è abbastanza forte
        if self._min_adx > 0:
            if i.adx is None or i.adx < self._min_adx:
                return None

        if long_ok == short_ok:
            return None  # nessuna direzione netta (o entrambe -> contraddittorio)
        direction = Direction.LONG if long_ok else Direction.SHORT
        stop, target = self._atr_stop_target(asset, direction, self._tf, self._atr_mult_stop, self._rr)
        return self._signal(asset, direction, confidence=60.0,
                            reasoning=f"[gen] {self.description}", stop=stop, target=target)
