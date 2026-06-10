"""
On-Chain Agent — Coinglass (OI, funding, liquidation) + Alternative.me (Fear & Greed).

Il Fear & Greed Index di Alternative.me è gratuito e senza chiave: è la fonte
principale qui. Coinglass richiede una chiave (open interest / liquidation heatmap)
e degrada a None se assente.
"""
from __future__ import annotations

from typing import Optional

import requests

from bot.config import settings

ALT_FNG = "https://api.alternative.me/fng/"
COINGLASS_BASE = "https://open-api-v3.coinglass.com/api"


class OnChainAgent:
    def __init__(self, coinglass_key: str = settings.COINGLASS_API_KEY, timeout: int = 10) -> None:
        self.coinglass_key = coinglass_key
        self.timeout = timeout

    def fear_greed(self) -> Optional[int]:
        """Fear & Greed Index 0-100 (0=extreme fear, 100=extreme greed)."""
        try:
            r = requests.get(ALT_FNG, params={"limit": 1}, timeout=self.timeout)
            r.raise_for_status()
            data = r.json().get("data", [])
            if data:
                return int(data[0]["value"])
        except Exception as exc:  # noqa: BLE001
            print(f"[onchain_agent] fear&greed fallito: {exc}")
        return None

    def open_interest(self, symbol: str) -> Optional[float]:
        """OI aggregato da Coinglass (richiede chiave)."""
        if not self.coinglass_key:
            return None
        coin = symbol.replace(settings.QUOTE_ASSET, "")
        try:
            r = requests.get(
                f"{COINGLASS_BASE}/futures/openInterest",
                headers={"coinglassSecret": self.coinglass_key},
                params={"symbol": coin},
                timeout=self.timeout,
            )
            r.raise_for_status()
            data = r.json().get("data", {})
            if isinstance(data, dict):
                return data.get("openInterest")
        except Exception as exc:  # noqa: BLE001
            print(f"[onchain_agent] OI {coin} fallito: {exc}")
        return None
