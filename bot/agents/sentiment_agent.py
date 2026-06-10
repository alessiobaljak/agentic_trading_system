"""
Sentiment Agent — LunarCrush (social volume + sentiment per crypto).

Degrada a None se la chiave non è configurata o la richiesta fallisce.
Il sentiment è normalizzato in [0,1] (0=molto bearish, 1=molto bullish).
"""
from __future__ import annotations

from typing import Optional

import requests

from bot.config import settings

LUNAR_BASE = "https://lunarcrush.com/api4/public"


class SentimentAgent:
    def __init__(self, api_key: str = settings.LUNARCRUSH_API_KEY, timeout: int = 10) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self._cache: dict[str, dict] = {}

    @staticmethod
    def _base_asset(symbol: str) -> str:
        """BTCUSDT -> BTC."""
        return symbol.replace(settings.QUOTE_ASSET, "").replace("USD", "") or symbol

    def get_sentiment(self, symbol: str) -> dict:
        """
        Ritorna {sentiment_score: float|None [0..1], social_volume: float|None}.
        """
        if not self.api_key:
            return {"sentiment_score": None, "social_volume": None}
        coin = self._base_asset(symbol)
        try:
            r = requests.get(
                f"{LUNAR_BASE}/coins/{coin}/v1",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
            r.raise_for_status()
            data = r.json().get("data", {})
            # LunarCrush "sentiment" è 1..5 -> normalizziamo a 0..1
            raw = data.get("sentiment")
            norm = None
            if raw is not None:
                norm = max(0.0, min(1.0, (float(raw) - 1.0) / 4.0))
            return {
                "sentiment_score": norm,
                "social_volume": data.get("social_volume") or data.get("interactions_24h"),
            }
        except Exception as exc:  # noqa: BLE001
            print(f"[sentiment_agent] {coin} fallito: {exc}")
            return {"sentiment_score": None, "social_volume": None}
