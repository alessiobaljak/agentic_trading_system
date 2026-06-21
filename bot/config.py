"""
Configurazione centrale del bot.

IMPORTANTE — separazione delle responsabilità:
  * Questo file contiene impostazioni operative e DEFAULT regolabili.
  * I LIMITI DI SICUREZZA HARDCODED (hard cap leverage/size, circuit breaker)
    NON stanno qui: vivono in `bot/risk/hard_limits.py`, non sono modificabili
    né da config, né da Firebase, né dall'LLM.
  * I parametri regolabili dall'utente (leverage, risk per trade) vivono su
    Firebase in `user_risk_settings`; i valori qui sotto sono solo i fallback
    usati se Firebase non è raggiungibile.
"""
from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _get_bool(key: str, default: bool) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_float(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


class Settings:
    """Impostazioni globali, lette una sola volta all'avvio."""

    # ---- Modalità ----
    # DRY_RUN True => paper trading, nessun ordine reale (GATE 2). Default sicuro.
    DRY_RUN: bool = _get_bool("DRY_RUN", True)

    # ---- Binance ----
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")
    BINANCE_TESTNET: bool = _get_bool("BINANCE_TESTNET", True)
    QUOTE_ASSET: str = "USDT"  # universo: tutti i perpetual *USDT

    # ---- Anthropic / Claude ----
    # NB: usiamo `or` (non il default di getenv) perché nei workflow GitHub una
    # variabile mappata a un secret inesistente arriva come STRINGA VUOTA, non
    # come assente — e una stringa vuota farebbe fallire l'API ("model: String
    # should have at least 1 character").
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL") or "claude-opus-4-8"

    # ---- Data agents ----
    LUNARCRUSH_API_KEY: str = os.getenv("LUNARCRUSH_API_KEY", "")
    COINGLASS_API_KEY: str = os.getenv("COINGLASS_API_KEY", "")
    NEWSAPI_KEY: str = os.getenv("NEWSAPI_KEY", "")

    # ---- Firebase ----
    FIREBASE_SERVICE_ACCOUNT: str = os.getenv("FIREBASE_SERVICE_ACCOUNT", "")
    FIREBASE_RTDB_URL: str = os.getenv("FIREBASE_RTDB_URL", "")

    # ---- Telegram ----
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

    # ---- Fallback parametri regolabili (i valori reali vengono da Firebase) ----
    # Questi sono usati solo se `user_risk_settings` non è raggiungibile.
    DEFAULT_LEVERAGE: float = 2.0
    DEFAULT_RISK_PER_TRADE: float = 0.01  # 1% del capitale

    # ---- Trading loop ----
    ORCHESTRATOR_TIMEFRAME: str = "15m"   # l'orchestratore gira ad ogni 15m chiusa
    SCAN_INTERVAL_HOURS: int = 4          # market scanner ogni 4h
    REGIME_INTERVAL_MINUTES: int = 60     # regime detector ogni ora
    MAX_OPEN_POSITIONS: int = 5           # 3-5 asset concentrati (cap posizioni APERTE)
    # su quante crypto (tra le più liquide scansionate) cercare un SEGNALE a ogni
    # ciclo. Disaccoppiato dal cap posizioni: valuti TUTTO il mercato liquido, apri max 5.
    SELECT_UNIVERSE: int = int(os.getenv("SELECT_UNIVERSE", "100"))
    # cooldown anti-whipsaw: ore di stop su una coin dopo uno STOP LOSS (no rientro)
    COOLDOWN_HOURS: float = float(os.getenv("COOLDOWN_HOURS", "4"))
    # adattamento real-time: dopo N stop consecutivi una STRATEGIA va in panchina
    # (il bot continua con le altre), per STRATEGY_COOLDOWN_HOURS.
    STRATEGY_LOSS_STREAK: int = int(os.getenv("STRATEGY_LOSS_STREAK", "3"))
    STRATEGY_COOLDOWN_HOURS: float = float(os.getenv("STRATEGY_COOLDOWN_HOURS", "8"))
    MAX_CORRELATED_POSITIONS: int = 3     # correlazione >0.85
    CORRELATION_THRESHOLD: float = 0.85

    # ---- Anti-overfitting ----
    # Frazione di capitale SEMPRE su configurazione baseline non adattata.
    BASELINE_CAPITAL_FRACTION: float = 0.20

    # ---- Learning ----
    LEARNING_LOOKBACK_DAYS: tuple[int, ...] = (30, 60, 90)
    MIN_TRADES_FOR_KELLY: int = 100       # Kelly suggerito dopo 100+ trade
    MIN_TRADES_PER_WEIGHT: int = 5        # minimo campione per fidarsi di un peso

    # ---- Timeframes raccolti dal price agent ----
    TIMEFRAMES: tuple[str, ...] = ("1m", "5m", "15m", "1h")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
