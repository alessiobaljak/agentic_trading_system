"""
Sentiment Agent — fonte GRATUITA e senza chiave: CoinGecko.

CoinGecko espone per ogni coin `sentiment_votes_up_percentage` (voto della
community 0-100), che usiamo come proxy di sentiment normalizzato in [0,1].
Niente API key, niente piano a pagamento.

LunarCrush resta supportato come fonte OPZIONALE: se `LUNARCRUSH_API_KEY` è
presente e risponde, ha la precedenza; altrimenti si usa CoinGecko.

Degrada a None se nessuna fonte risponde (il bot funziona comunque).
"""
from __future__ import annotations

import time
from typing import Optional

import requests

from bot.config import settings

COINGECKO = "https://api.coingecko.com/api/v3"
LUNAR_BASE = "https://lunarcrush.com/api4/public"

# Mappa base-asset -> id CoinGecko per i principali futures USDT.
_CG_IDS: dict[str, str] = {
    "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana", "BNB": "binancecoin",
    "XRP": "ripple", "ADA": "cardano", "DOGE": "dogecoin", "AVAX": "avalanche-2",
    "DOT": "polkadot", "LINK": "chainlink", "MATIC": "matic-network", "POL": "polygon-ecosystem-token",
    "LTC": "litecoin", "TRX": "tron", "BCH": "bitcoin-cash", "ATOM": "cosmos",
    "NEAR": "near", "APT": "aptos", "ARB": "arbitrum", "OP": "optimism",
    "SUI": "sui", "INJ": "injective-protocol", "TIA": "celestia", "SEI": "sei-network",
    "FIL": "filecoin", "ETC": "ethereum-classic", "UNI": "uniswap", "AAVE": "aave",
    "RNDR": "render-token", "FET": "fetch-ai", "PEPE": "pepe", "WIF": "dogwifcoin",
    "SHIB": "shiba-inu", "TON": "the-open-network", "HBAR": "hedera-hashgraph",
}


class SentimentAgent:
    def __init__(self, api_key: str = settings.LUNARCRUSH_API_KEY,
                 timeout: int = 10, cache_ttl: int = 1800) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self._cache: dict[str, tuple[float, dict]] = {}

    @staticmethod
    def _base_asset(symbol: str) -> str:
        return symbol.replace(settings.QUOTE_ASSET, "").replace("USD", "") or symbol

    def _coingecko_id(self, symbol: str) -> Optional[str]:
        return _CG_IDS.get(self._base_asset(symbol).upper())

    # ------------------------------------------------------------------ #
    def get_sentiment(self, symbol: str) -> dict:
        """Ritorna {sentiment_score: float|None [0..1], social_volume: float|None}."""
        now = time.time()
        cached = self._cache.get(symbol)
        if cached and now - cached[0] < self.cache_ttl:
            return cached[1]

        result = self._from_lunarcrush(symbol) or self._from_coingecko(symbol) \
            or {"sentiment_score": None, "social_volume": None}
        self._cache[symbol] = (now, result)
        return result

    # ---- CoinGecko (gratis, primario) ----
    def _from_coingecko(self, symbol: str) -> Optional[dict]:
        cid = self._coingecko_id(symbol)
        if not cid:
            return None
        try:
            r = requests.get(
                f"{COINGECKO}/coins/{cid}",
                params={"localization": "false", "tickers": "false",
                        "market_data": "true", "community_data": "false",
                        "developer_data": "false", "sparkline": "false"},
                timeout=self.timeout,
            )
            if r.status_code != 200:
                return None
            data = r.json()
            up = data.get("sentiment_votes_up_percentage")
            score = max(0.0, min(1.0, float(up) / 100.0)) if up is not None else None
            vol = (data.get("market_data", {}) or {}).get("total_volume", {}).get("usd")
            return {"sentiment_score": score, "social_volume": vol}
        except Exception as exc:  # noqa: BLE001
            print(f"[sentiment_agent] CoinGecko {cid} fallito: {exc}")
            return None

    # ---- LunarCrush (opzionale, se chiave valida) ----
    def _from_lunarcrush(self, symbol: str) -> Optional[dict]:
        if not self.api_key:
            return None
        coin = self._base_asset(symbol)
        try:
            r = requests.get(
                f"{LUNAR_BASE}/coins/{coin}/v1",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=self.timeout,
            )
            if r.status_code != 200:
                return None  # es. 402 piano a pagamento -> cadi su CoinGecko
            data = r.json().get("data", {})
            raw = data.get("sentiment")
            norm = max(0.0, min(1.0, (float(raw) - 1.0) / 4.0)) if raw is not None else None
            return {"sentiment_score": norm,
                    "social_volume": data.get("social_volume") or data.get("interactions_24h")}
        except Exception:  # noqa: BLE001
            return None
