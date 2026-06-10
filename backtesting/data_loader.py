"""
Caricamento dati storici per il backtesting (GATE 1).

Priorità delle fonti (tutte gratuite):
  1. CoinMetrics community API (metriche/prezzi reference rate) — 2022..oggi
  2. Binance klines storici (fallback robusto, OHLCV)
  3. Dati sintetici deterministici (ultimo fallback, per test offline/CI)

Restituisce sempre una lista di Candle ordinate.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

import numpy as np
import requests

from bot.core.models import Candle

COINMETRICS = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
BINANCE_KLINES = "https://fapi.binance.com/fapi/v1/klines"


def _coinmetrics(asset: str, start: str, end: str) -> list[Candle]:
    """Prezzi reference rate giornalieri da CoinMetrics community (no key)."""
    try:
        r = requests.get(COINMETRICS, params={
            "assets": asset.lower(), "metrics": "ReferenceRateUSD",
            "frequency": "1d", "start_time": start, "end_time": end, "page_size": 10000,
        }, timeout=20)
        r.raise_for_status()
        data = r.json().get("data", [])
        candles = []
        for d in data:
            px = float(d["ReferenceRateUSD"])
            t = datetime.fromisoformat(d["time"].replace("Z", "+00:00"))
            candles.append(Candle(open_time=t, open=px, high=px, low=px, close=px, volume=0.0))
        return candles
    except Exception as exc:  # noqa: BLE001
        print(f"[backtest] CoinMetrics fallito per {asset}: {exc}")
        return []


def _binance(symbol: str, interval: str, start_ms: int, end_ms: int) -> list[Candle]:
    candles: list[Candle] = []
    cursor = start_ms
    try:
        while cursor < end_ms:
            r = requests.get(BINANCE_KLINES, params={
                "symbol": symbol, "interval": interval,
                "startTime": cursor, "endTime": end_ms, "limit": 1500,
            }, timeout=20)
            r.raise_for_status()
            batch = r.json()
            if not batch:
                break
            for k in batch:
                candles.append(Candle(
                    open_time=datetime.fromtimestamp(k[0] / 1000, tz=timezone.utc),
                    open=float(k[1]), high=float(k[2]), low=float(k[3]),
                    close=float(k[4]), volume=float(k[5]),
                ))
            cursor = batch[-1][0] + 1
            if len(batch) < 1500:
                break
        return candles
    except Exception as exc:  # noqa: BLE001
        print(f"[backtest] Binance klines fallito per {symbol}: {exc}")
        return candles


def _synthetic(start: datetime, end: datetime, interval_min: int = 60,
               seed: int = 7, start_px: float = 30000.0) -> list[Candle]:
    """Random walk deterministico con regimi alternati (per test offline)."""
    rng = np.random.default_rng(seed)
    n = int((end - start).total_seconds() / (interval_min * 60))
    candles = []
    px = start_px
    for k in range(max(n, 200)):
        # regime che cambia ogni ~300 step
        drift = 0.0008 if (k // 300) % 3 == 0 else (-0.0006 if (k // 300) % 3 == 1 else 0.0)
        ret = drift + rng.normal(0, 0.01)
        new = px * (1 + ret)
        hi = max(px, new) * (1 + abs(rng.normal(0, 0.003)))
        lo = min(px, new) * (1 - abs(rng.normal(0, 0.003)))
        candles.append(Candle(
            open_time=start + timedelta(minutes=interval_min * k),
            open=px, high=hi, low=lo, close=new, volume=float(rng.integers(500, 5000)),
        ))
        px = new
    return candles


def load_candles(
    symbol: str = "BTCUSDT",
    interval: str = "1h",
    start: str = "2022-01-01",
    end: str = "2026-01-01",
    prefer: str = "binance",
) -> list[Candle]:
    """
    Carica candele storiche. `prefer` in {coinmetrics, binance, synthetic}.
    Fa fallback automatico se la fonte preferita non restituisce dati.
    """
    start_dt = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)

    if prefer == "coinmetrics":
        c = _coinmetrics(symbol.replace("USDT", ""), start, end)
        if c:
            return c
    if prefer in ("coinmetrics", "binance"):
        c = _binance(symbol, interval, int(start_dt.timestamp() * 1000),
                     int(end_dt.timestamp() * 1000))
        if c:
            return c
    print("[backtest] uso dati sintetici (offline)")
    return _synthetic(start_dt, end_dt)
