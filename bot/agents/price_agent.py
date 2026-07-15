"""
Price & Futures Agent.

Recupera da Binance Futures (USDⓈ-M):
  * candele multi-timeframe (1m/5m/15m/1h)
  * mark price, funding rate, open interest, volume 24h
  * calcola tutti gli indicatori (via bot.core.indicators)

Modalità di accesso:
  * REST (klines, premiumIndex, ticker) — usato qui, robusto e testabile.
  * Il WebSocket (mark price / liquidation stream) è descritto in docs/ e può
    essere aggiunto come ottimizzazione: l'interfaccia resta la stessa.

Degradazione: se la rete o le API non sono disponibili ritorna None, il bot
salta il ciclo invece di crashare.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional

import requests

from bot.config import settings
from bot.core.indicators import compute_snapshot
from bot.core.models import AssetSnapshot, Candle, IndicatorSnapshot

FAPI_BASE = "https://testnet.binancefuture.com" if settings.BINANCE_TESTNET else "https://fapi.binance.com"


class PriceAgent:
    def __init__(self, base_url: str = FAPI_BASE, timeout: int = 10) -> None:
        self.base = base_url
        self.timeout = timeout
        self._session = requests.Session()

    def _get(self, path: str, params: dict) -> Optional[object]:
        """GET con UN retry su rate-limit (429/418: Binance chiede di rallentare).
        A 200 coin per ciclo il weight e' vicino al limite: senza retry una
        risposta 429 diventa una coin silenziosamente muta per il ciclo."""
        for attempt in (0, 1):
            try:
                r = self._session.get(f"{self.base}{path}", params=params, timeout=self.timeout)
                if r.status_code in (429, 418) and attempt == 0:
                    wait = float(r.headers.get("Retry-After", 2) or 2)
                    time.sleep(min(wait, 10.0))
                    continue
                r.raise_for_status()
                return r.json()
            except Exception as exc:  # noqa: BLE001
                if attempt == 0:
                    time.sleep(0.5)
                    continue
                print(f"[price_agent] GET {path} fallito: {exc}")
                return None
        return None

    # ---- universo futures ----
    def list_perpetual_symbols(self) -> list[str]:
        """Tutti i perpetual *USDT TRADING (universo scanner)."""
        data = self._get("/fapi/v1/exchangeInfo", {})
        if not data:
            return []
        out = []
        for s in data.get("symbols", []):
            if (s.get("contractType") == "PERPETUAL"
                    and s.get("quoteAsset") == settings.QUOTE_ASSET
                    and s.get("status") == "TRADING"):
                out.append(s["symbol"])
        return out

    def list_perpetual_symbols_by_volume(self) -> list[str]:
        """Perpetual USDT ORDINATI per volume 24h (decrescente). Una sola chiamata
        extra (/ticker/24hr senza symbol = tutti i ticker) per coprire la parte
        LIQUIDA del mercato (incluse le memecoin grosse), non i primi N a caso.
        Se il ranking fallisce, ricade sull'ordine grezzo."""
        perps = set(self.list_perpetual_symbols())
        if not perps:
            return []
        tickers = self._get("/fapi/v1/ticker/24hr", {})
        if not isinstance(tickers, list):
            return sorted(perps)
        ranked: list[tuple[str, float]] = []
        for t in tickers:
            sym = t.get("symbol")
            if sym in perps:
                try:
                    ranked.append((sym, float(t.get("quoteVolume", 0.0))))
                except (TypeError, ValueError):
                    continue
        ranked.sort(key=lambda x: x[1], reverse=True)
        return [s for s, _ in ranked] or sorted(perps)

    # ---- candele ----
    def get_candles(self, symbol: str, interval: str, limit: int = 200) -> list[Candle]:
        data = self._get("/fapi/v1/klines",
                         {"symbol": symbol, "interval": interval, "limit": limit})
        if not data:
            return []
        candles = []
        for k in data:
            candles.append(Candle(
                open_time=datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc),
                open=float(k[1]), high=float(k[2]), low=float(k[3]),
                close=float(k[4]), volume=float(k[5]),
                close_time=datetime.fromtimestamp(k[6] / 1000, tz=timezone.utc),
            ))
        return candles

    # ---- funding / mark / ticker ----
    def get_premium(self, symbol: str) -> dict:
        data = self._get("/fapi/v1/premiumIndex", {"symbol": symbol}) or {}
        return data if isinstance(data, dict) else {}

    def get_ticker_24h(self, symbol: str) -> dict:
        data = self._get("/fapi/v1/ticker/24hr", {"symbol": symbol}) or {}
        return data if isinstance(data, dict) else {}

    def get_mark_price(self, symbol: str) -> Optional[float]:
        """Solo il mark price corrente (1 richiesta). Usato per gestire le
        posizioni aperte a ogni tick senza ricostruire lo snapshot completo,
        così SL/TP/trailing reagiscono al prezzo VIVO e non a uno vecchio di 15m."""
        premium = self.get_premium(symbol)
        mp = premium.get("markPrice")
        try:
            return float(mp) if mp is not None else None
        except (TypeError, ValueError):
            return None

    def get_open_interest(self, symbol: str) -> Optional[float]:
        data = self._get("/fapi/v1/openInterest", {"symbol": symbol})
        if data and isinstance(data, dict) and "openInterest" in data:
            return float(data["openInterest"])
        return None

    # ---- snapshot completo ----
    def build_snapshot(self, symbol: str) -> Optional[AssetSnapshot]:
        indicators: dict[str, IndicatorSnapshot] = {}
        price = None
        now = datetime.now(timezone.utc)
        for tf in settings.TIMEFRAMES:
            candles = self.get_candles(symbol, tf, limit=200)
            if not candles:
                continue
            # PARITA' col backtest: indicatori SOLO su candele CHIUSE. L'ultima
            # kline di Binance e' quella in formazione: includerla fa "repaintare"
            # RSI/MACD/BB e soprattutto confronta il volume PARZIALE della barra
            # corrente con la SMA di barre piene (filtri volume quasi sempre falsi
            # a inizio barra). Il PREZZO invece resta l'ultimo disponibile (vivo).
            price = candles[-1].close
            closed = candles[:-1] if (candles[-1].close_time and
                                      candles[-1].close_time > now) else candles
            if not closed:
                continue
            indicators[tf] = compute_snapshot(closed, tf)
        if price is None:
            return None
        # senza il timeframe PRIMARIO le strategie sarebbero mute in silenzio
        # (.ind(tf) -> None su ogni segnale): meglio nessuno snapshot che uno zoppo.
        if settings.ORCHESTRATOR_TIMEFRAME not in indicators:
            return None

        premium = self.get_premium(symbol)
        ticker = self.get_ticker_24h(symbol)
        return AssetSnapshot(
            symbol=symbol,
            price=price,
            mark_price=float(premium["markPrice"]) if premium.get("markPrice") else None,
            funding_rate=float(premium["lastFundingRate"]) if premium.get("lastFundingRate") else None,
            open_interest=self.get_open_interest(symbol),
            volume_24h=float(ticker["quoteVolume"]) if ticker.get("quoteVolume") else None,
            indicators=indicators,
        )
