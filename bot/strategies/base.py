"""
Interfaccia base astratta delle strategie + registry per auto-discovery.

Ogni strategia:
  * eredita da `Strategy`
  * dichiara `name` e `active_regimes` (in quali regimi è abilitata)
  * implementa `generate_signal()` che ritorna un StrategySignal o None
  * è registrata con `@register_strategy`

L'orchestratore e il regime detector decidono quali strategie attivare.
Il learning loop assegna pesi per strategia × regime.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Type

from bot.core.models import AssetSnapshot, Direction, Regime, StrategySignal


class StrategyContext:
    """
    Contesto opzionale passato alle strategie che hanno bisogno di info
    cross-asset (es. Momentum Cross-Asset usa lo snapshot di BTC).
    """

    def __init__(
        self,
        all_assets: Optional[dict[str, AssetSnapshot]] = None,
        regime: Optional[Regime] = None,
    ) -> None:
        self.all_assets: dict[str, AssetSnapshot] = all_assets or {}
        self.regime = regime


class Strategy(ABC):
    """Classe base astratta. NON istanziabile direttamente."""

    #: nome univoco (usato come chiave nei pesi e nei log)
    name: str = "base"
    #: regimi in cui la strategia è abilitata
    active_regimes: set[Regime] = set()
    #: descrizione human-readable
    description: str = ""

    def is_active_in(self, regime: Optional[Regime]) -> bool:
        if regime is None:
            return True
        return regime in self.active_regimes

    @abstractmethod
    def generate_signal(
        self, asset: AssetSnapshot, ctx: Optional[StrategyContext] = None
    ) -> Optional[StrategySignal]:
        """Ritorna un segnale o None se non ci sono condizioni d'ingresso."""
        raise NotImplementedError

    # --- helper condivisi ---
    def _signal(
        self,
        asset: AssetSnapshot,
        direction: Direction,
        confidence: float,
        reasoning: str,
        stop: Optional[float] = None,
        target: Optional[float] = None,
    ) -> StrategySignal:
        return StrategySignal(
            strategy=self.name,
            symbol=asset.symbol,
            direction=direction,
            confidence=max(0.0, min(100.0, confidence)),
            reasoning=reasoning,
            suggested_stop=stop,
            suggested_target=target,
            regime=asset.regime,
        )

    @staticmethod
    def _atr_stop_target(
        asset: AssetSnapshot, direction: Direction, timeframe: str = "15m",
        atr_mult_stop: float = 1.5, rr: float = 2.0,
    ) -> tuple[Optional[float], Optional[float]]:
        """Calcola SL/TP ATR-based con un dato risk:reward."""
        ind = asset.ind(timeframe)
        if ind is None or ind.atr is None:
            return None, None
        price = asset.price
        risk = atr_mult_stop * ind.atr
        if direction == Direction.LONG:
            return price - risk, price + rr * risk
        return price + risk, price - rr * risk


# --------------------------------------------------------------------------- #
# Registry                                                                     #
# --------------------------------------------------------------------------- #
STRATEGY_REGISTRY: dict[str, Type[Strategy]] = {}


def register_strategy(cls: Type[Strategy]) -> Type[Strategy]:
    """Decoratore: registra la strategia nel registry globale."""
    if cls.name in STRATEGY_REGISTRY:
        raise ValueError(f"Strategia duplicata: {cls.name}")
    STRATEGY_REGISTRY[cls.name] = cls
    return cls


def get_all_strategies() -> list[Strategy]:
    """Istanzia tutte le strategie registrate."""
    return [cls() for cls in STRATEGY_REGISTRY.values()]
