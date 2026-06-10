"""Risk management: hard limits hardcoded + parametri regolabili + gate finale."""
from bot.risk.hard_limits import (
    MAX_LEVERAGE,
    MAX_RISK_PER_TRADE,
    DAILY_LOSS_LIMIT,
    CONSECUTIVE_SL_PAUSE,
    HIGH_VOL_SIGMA,
    MACRO_FLAT_HOURS,
)
from bot.risk.risk_manager import RiskManager

__all__ = [
    "MAX_LEVERAGE",
    "MAX_RISK_PER_TRADE",
    "DAILY_LOSS_LIMIT",
    "CONSECUTIVE_SL_PAUSE",
    "HIGH_VOL_SIGMA",
    "MACRO_FLAT_HOURS",
    "RiskManager",
]
