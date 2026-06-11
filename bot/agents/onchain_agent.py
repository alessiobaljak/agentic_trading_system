"""
On-Chain / Derivatives Agent — fonti GRATUITE e senza chiave.

  * Open Interest, Funding, Long/Short ratio -> Binance public futures data
    (endpoint pubblici di fapi.binance.com, NESSUNA chiave necessaria).
  * Fear & Greed Index -> Alternative.me (gratis, senza chiave).

Coinglass resta supportato come fonte OPZIONALE (se `COINGLASS_API_KEY` è
presente), ma NON è più necessario: i dati equivalenti arrivano da Binance.
"""
from __future__ import annotations

from typing import Optional

import requests

from bot.config import settings

ALT_FNG = "https://api.alternative.me/fng/"
# dati pubblici futures Binance (mainnet, validi anche se il bot opera su testnet)
FAPI = "https://fapi.binance.com"
COINGLASS_BASE = "https://open-api-v3.coinglass.com/api"


class OnChainAgent:
    def __init__(self, coinglass_key: str = settings.COINGLASS_API_KEY, timeout: int = 10) -> None:
        self.coinglass_key = coinglass_key
        self.timeout = timeout

    def _get(self, url: str, params: dict) -> Optional[object]:
        try:
            r = requests.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except Exception as exc:  # noqa: BLE001
            print(f"[onchain_agent] GET {url} fallito: {exc}")
            return None

    # ---- Fear & Greed (gratis) ----
    def fear_greed(self) -> Optional[int]:
        data = self._get(ALT_FNG, {"limit": 1})
        try:
            if data and data.get("data"):
                return int(data["data"][0]["value"])
        except Exception:  # noqa: BLE001
            pass
        return None

    # ---- Open Interest (Binance public, gratis) ----
    def open_interest(self, symbol: str) -> Optional[float]:
        data = self._get(f"{FAPI}/fapi/v1/openInterest", {"symbol": symbol})
        if isinstance(data, dict) and data.get("openInterest") is not None:
            return float(data["openInterest"])
        # fallback opzionale Coinglass
        return self._coinglass_oi(symbol)

    # ---- Funding rate (Binance public, gratis) ----
    def funding_rate(self, symbol: str) -> Optional[float]:
        data = self._get(f"{FAPI}/fapi/v1/premiumIndex", {"symbol": symbol})
        if isinstance(data, dict) and data.get("lastFundingRate") is not None:
            return float(data["lastFundingRate"])
        return None

    # ---- Long/Short account ratio (Binance public, gratis) ----
    def long_short_ratio(self, symbol: str, period: str = "1h") -> Optional[float]:
        data = self._get(f"{FAPI}/futures/data/globalLongShortAccountRatio",
                         {"symbol": symbol, "period": period, "limit": 1})
        if isinstance(data, list) and data:
            try:
                return float(data[-1]["longShortRatio"])
            except Exception:  # noqa: BLE001
                return None
        return None

    # ---- Coinglass (opzionale) ----
    def _coinglass_oi(self, symbol: str) -> Optional[float]:
        if not self.coinglass_key:
            return None
        coin = symbol.replace(settings.QUOTE_ASSET, "")
        data = self._get(f"{COINGLASS_BASE}/futures/openInterest",
                         {"symbol": coin})  # header non passato: best-effort
        if isinstance(data, dict):
            d = data.get("data")
            if isinstance(d, dict):
                return d.get("openInterest")
        return None
