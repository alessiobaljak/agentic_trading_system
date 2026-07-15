"""
Caricamento dati storici per il backtesting (GATE 1).

Fonti OHLCV GRATUITE (nessuna chiave), provate in ordine con fallback automatico:
  1. Binance Futures klines  (storico completo, tutti i perpetual USDT)
  2. Bybit v5 linear klines   (fallback se Binance è geo-bloccata)
  3. OKX swap candles         (secondo fallback)
  4. Dati sintetici           (offline / CI senza rete)

CoinMetrics community è SOLO opt-in (prefer="coinmetrics"): è gratis ma molto
limitato (poche cripto, solo daily reference rate) e NON adatto a OHLCV intraday
su tutti i futures — per questo non è più una fonte primaria.

Restituisce sempre una lista di Candle ordinate per tempo.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Callable

import numpy as np
import requests

from bot.core.models import Candle

BINANCE_KLINES = "https://fapi.binance.com/fapi/v1/klines"
BINANCE_FUNDING = "https://fapi.binance.com/fapi/v1/fundingRate"
BYBIT_KLINES = "https://api.bybit.com/v5/market/kline"
OKX_CANDLES = "https://www.okx.com/api/v5/market/history-candles"
COINMETRICS = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"

_FUNDING_CACHE: dict[str, float | None] = {}


def funding_rate_for(symbol: str) -> float | None:
    """Tasso di funding per-8h REALE della coin: media dello storico funding di
    Binance Futures (best-effort, cache per-processo). None se non raggiungibile
    (offline/geo-blocco) -> chi lo usa ricade sul default. Cattura lo SKEW reale di
    una coin (es. funding cronicamente positivo -> i long pagano di piu')."""
    if symbol in _FUNDING_CACHE:
        return _FUNDING_CACHE[symbol]
    rate: float | None = None
    try:
        r = requests.get(BINANCE_FUNDING, params={"symbol": symbol, "limit": 1000}, timeout=15)
        r.raise_for_status()
        rows = r.json()
        vals = [float(x["fundingRate"]) for x in rows if x.get("fundingRate") is not None]
        if vals:
            rate = sum(vals) / len(vals)
    except Exception:  # noqa: BLE001
        rate = None
    _FUNDING_CACHE[symbol] = rate
    return rate


def _candle(ts_ms: int, o, h, l, c, v) -> Candle:
    return Candle(
        open_time=datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc),
        open=float(o), high=float(h), low=float(l), close=float(c), volume=float(v),
    )


# --------------------------------------------------------------------------- #
# Binance (primario)                                                           #
# --------------------------------------------------------------------------- #
def _binance(symbol: str, interval: str, start_ms: int, end_ms: int) -> list[Candle]:
    out: list[Candle] = []
    cursor = start_ms
    try:
        while cursor < end_ms:
            r = requests.get(BINANCE_KLINES, params={
                "symbol": symbol, "interval": interval,
                "startTime": cursor, "endTime": end_ms, "limit": 1500,
            }, timeout=20)
            r.raise_for_status()
            batch = r.json()
            if not isinstance(batch, list) or not batch:
                break
            for k in batch:
                out.append(_candle(k[0], k[1], k[2], k[3], k[4], k[5]))
            cursor = batch[-1][0] + 1
            if len(batch) < 1500:
                break
        return out
    except Exception as exc:  # noqa: BLE001
        print(f"[backtest] Binance non disponibile ({str(exc)[:80]})")
        return out


# --------------------------------------------------------------------------- #
# Bybit (fallback 1)                                                           #
# --------------------------------------------------------------------------- #
_BYBIT_INTERVAL = {"1m": "1", "3m": "3", "5m": "5", "15m": "15", "30m": "30",
                   "1h": "60", "2h": "120", "4h": "240", "1d": "D"}


def _bybit(symbol: str, interval: str, start_ms: int, end_ms: int) -> list[Candle]:
    bi = _BYBIT_INTERVAL.get(interval, "60")
    out: list[Candle] = []
    cursor = end_ms
    try:
        while cursor > start_ms:
            r = requests.get(BYBIT_KLINES, params={
                "category": "linear", "symbol": symbol, "interval": bi,
                "start": start_ms, "end": cursor, "limit": 1000,
            }, timeout=20)
            r.raise_for_status()
            lst = r.json().get("result", {}).get("list", [])
            if not lst:
                break
            for k in lst:  # [start, o, h, l, c, vol, turnover] — newest first
                ts = int(k[0])
                if ts >= start_ms:
                    out.append(_candle(ts, k[1], k[2], k[3], k[4], k[5]))
            oldest = int(lst[-1][0])
            if oldest >= cursor:
                break
            cursor = oldest - 1
            if len(lst) < 1000:
                break
        out.sort(key=lambda c: c.open_time)
        return out
    except Exception as exc:  # noqa: BLE001
        print(f"[backtest] Bybit non disponibile ({str(exc)[:80]})")
        return out


# --------------------------------------------------------------------------- #
# OKX (fallback 2)                                                             #
# --------------------------------------------------------------------------- #
_OKX_BAR = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1H", "2h": "2H", "4h": "4H", "1d": "1D"}


def _okx(symbol: str, interval: str, start_ms: int, end_ms: int) -> list[Candle]:
    bar = _OKX_BAR.get(interval, "1H")
    base = symbol[:-4] if symbol.endswith("USDT") else symbol
    inst = f"{base}-USDT-SWAP"
    out: list[Candle] = []
    after = end_ms
    try:
        while after > start_ms:
            r = requests.get(OKX_CANDLES, params={
                "instId": inst, "bar": bar, "after": after, "limit": 100,
            }, timeout=20)
            r.raise_for_status()
            data = r.json().get("data", [])
            if not data:
                break
            for k in data:  # [ts, o, h, l, c, vol, ...] — newest first
                ts = int(k[0])
                if ts >= start_ms:
                    out.append(_candle(ts, k[1], k[2], k[3], k[4], k[5]))
            oldest = int(data[-1][0])
            if oldest >= after:
                break
            after = oldest
            if len(data) < 100:
                break
        out.sort(key=lambda c: c.open_time)
        return out
    except Exception as exc:  # noqa: BLE001
        print(f"[backtest] OKX non disponibile ({str(exc)[:80]})")
        return out


# --------------------------------------------------------------------------- #
# CoinMetrics community (opt-in, limitato)                                     #
# --------------------------------------------------------------------------- #
def _coinmetrics(symbol: str, start: str, end: str) -> list[Candle]:
    asset = (symbol[:-4] if symbol.endswith("USDT") else symbol).lower()
    try:
        r = requests.get(COINMETRICS, params={
            "assets": asset, "metrics": "ReferenceRateUSD", "frequency": "1d",
            "start_time": start, "end_time": end, "page_size": 10000,
        }, timeout=20)
        r.raise_for_status()
        out = []
        for d in r.json().get("data", []):
            px = float(d["ReferenceRateUSD"])
            t = datetime.fromisoformat(d["time"].replace("Z", "+00:00"))
            out.append(Candle(open_time=t, open=px, high=px, low=px, close=px, volume=0.0))
        return out
    except Exception as exc:  # noqa: BLE001
        print(f"[backtest] CoinMetrics non disponibile ({str(exc)[:80]})")
        return []


# --------------------------------------------------------------------------- #
# Sintetico (offline / CI)                                                     #
# --------------------------------------------------------------------------- #
def _synthetic(start: datetime, end: datetime, interval_min: int = 60,
               seed: int = 7, start_px: float = 30000.0,
               symbol: str | None = None) -> list[Candle]:
    # seed derivato dal simbolo: così le coin NON condividono la stessa serie finta
    # (un seed fisso rendeva ogni coin identica -> "robusta su N" fasullo).
    if symbol:
        seed = (seed + sum(ord(ch) for ch in symbol) * 2654435761) % (2 ** 32)
    rng = np.random.default_rng(seed)
    n = int((end - start).total_seconds() / (interval_min * 60))
    candles = []
    px = start_px
    for k in range(max(n, 200)):
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


# --------------------------------------------------------------------------- #
# Cache su disco delle candele REALI                                           #
# --------------------------------------------------------------------------- #
# Ri-scaricare 2022->oggi a 15m per ~200 coin e' il collo di bottiglia (rete):
# ~90 chiamate klines per coin. La cache su disco fa si' che un secondo giro, uno
# shard, o una RIPRESA dopo interruzione leggano dal disco invece che dalla rete.
# NON riduce cicli/finestre/combo: cambia solo QUANTO velocemente arrivano i dati.
_CACHE_DIR = os.getenv("BACKTEST_CACHE_DIR", os.path.join(".cache", "candles"))
_CACHE_ENABLED = os.getenv("BACKTEST_CACHE_CANDLES", "true").lower() == "true"


def _cache_file(symbol: str, interval: str, start: str, end: str) -> str:
    return os.path.join(_CACHE_DIR, f"{symbol}_{interval}_{start}_{end}.json")


def _cache_read(path: str) -> list[Candle] | None:
    try:
        with open(path) as f:
            rows = json.load(f)
        return [_candle(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows] or None
    except Exception:  # noqa: BLE001
        return None


def _cache_write(path: str, candles: list[Candle]) -> None:
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        rows = [[int(c.open_time.timestamp() * 1000), c.open, c.high, c.low, c.close, c.volume]
                for c in candles]
        tmp = f"{path}.tmp"
        with open(tmp, "w") as f:
            json.dump(rows, f)
        os.replace(tmp, path)   # scrittura atomica: niente file a metà se interrotti
    except Exception:  # noqa: BLE001
        pass


# --------------------------------------------------------------------------- #
# Loader con fallback                                                          #
# --------------------------------------------------------------------------- #
def load_candles(
    symbol: str = "BTCUSDT",
    interval: str = "1h",
    start: str = "2022-01-01",
    end: str | None = None,   # None => oggi (finestra che avanza)
    prefer: str = "binance",
    allow_synthetic: bool | None = None,
) -> list[Candle]:
    """
    Carica candele storiche reali con fallback automatico tra exchange gratuiti.
    `prefer`: binance | bybit | okx | coinmetrics | synthetic | auto.

    `allow_synthetic`: se False, quando NESSUNA fonte reale è raggiungibile ritorna
    [] invece dei dati sintetici. CRITICO per il GATE 1: validare su una serie finta
    (random walk) produce coppie "validate" fasulle. Default: env
    BACKTEST_ALLOW_SYNTHETIC (true), così i test restano invariati ma i job di
    validazione lo mettono a false.
    """
    if allow_synthetic is None:
        allow_synthetic = os.getenv("BACKTEST_ALLOW_SYNTHETIC", "true").lower() == "true"
    if end is None:
        end = datetime.now(timezone.utc).strftime("%Y-%m-%d")   # fino a OGGI
    start_dt = datetime.fromisoformat(start).replace(tzinfo=timezone.utc)
    end_dt = datetime.fromisoformat(end).replace(tzinfo=timezone.utc)
    sms, ems = int(start_dt.timestamp() * 1000), int(end_dt.timestamp() * 1000)

    if prefer == "synthetic":
        return _synthetic(start_dt, end_dt, symbol=symbol)
    if prefer == "coinmetrics":
        c = _coinmetrics(symbol, start, end)
        if c:
            return c

    # cache su disco: se abbiamo gia' questi dati REALI, niente rete.
    cache_path = _cache_file(symbol, interval, start, end)
    if _CACHE_ENABLED:
        cached = _cache_read(cache_path)
        if cached:
            print(f"[backtest] dati da cache: {len(cached)} candele ({symbol} {interval})")
            return cached

    # ordine di fallback tra exchange OHLCV gratuiti
    chain: list[tuple[str, Callable[[], list[Candle]]]] = [
        ("binance", lambda: _binance(symbol, interval, sms, ems)),
        ("bybit", lambda: _bybit(symbol, interval, sms, ems)),
        ("okx", lambda: _okx(symbol, interval, sms, ems)),
    ]
    # se l'utente ha indicato un exchange specifico, mettilo per primo
    if prefer in ("bybit", "okx", "binance"):
        chain.sort(key=lambda kv: kv[0] != prefer)

    for name, fn in chain:
        candles = fn()
        if candles:
            print(f"[backtest] dati da {name}: {len(candles)} candele")
            if _CACHE_ENABLED:
                _cache_write(cache_path, candles)   # salva per i giri/shard successivi
            return candles

    if not allow_synthetic:
        print(f"[backtest] {symbol}: nessuna fonte reale raggiungibile e sintetici "
              f"DISABILITATI -> skip (niente validazione su dati finti)")
        return []
    print("[backtest] nessuna fonte reale raggiungibile -> dati sintetici (offline)")
    return _synthetic(start_dt, end_dt, symbol=symbol)
