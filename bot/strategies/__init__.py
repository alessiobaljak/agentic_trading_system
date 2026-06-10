"""
Strategy engine — architettura espandibile.

Per aggiungere la strategia #9, #10, ...: crea un nuovo file in questa cartella
con una sottoclasse di `Strategy`, decorala con `@register_strategy`, e importala
qui sotto. Nient'altro va toccato nel resto del sistema.
"""
from bot.strategies.base import Strategy, register_strategy, STRATEGY_REGISTRY, get_all_strategies

# Import delle 8 strategie per popolare il registry.
from bot.strategies.trend_following import TrendFollowing          # noqa: F401
from bot.strategies.mean_reversion import MeanReversion            # noqa: F401
from bot.strategies.breakout import Breakout                       # noqa: F401
from bot.strategies.funding_arbitrage import FundingArbitrage      # noqa: F401
from bot.strategies.vwap_reversion import VwapReversion            # noqa: F401
from bot.strategies.momentum_cross_asset import MomentumCrossAsset # noqa: F401
from bot.strategies.liquidity_grab import LiquidityGrab            # noqa: F401
from bot.strategies.grid_trading import GridTrading                # noqa: F401

__all__ = [
    "Strategy",
    "register_strategy",
    "STRATEGY_REGISTRY",
    "get_all_strategies",
]
