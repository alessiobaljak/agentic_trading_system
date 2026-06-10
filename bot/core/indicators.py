"""
Indicatori tecnici — implementazioni pure su pandas/numpy (nessuna dipendenza
esterna tipo TA-Lib, così gira ovunque). Tutte le funzioni accettano un
pandas.Series/DataFrame e restituiscono Series allineate per indice.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from bot.core.models import Candle, IndicatorSnapshot


def candles_to_df(candles: list[Candle]) -> pd.DataFrame:
    """Converte una lista di Candle in DataFrame OHLCV ordinato per tempo."""
    rows = [
        {
            "open_time": c.open_time,
            "open": c.open,
            "high": c.high,
            "low": c.low,
            "close": c.close,
            "volume": c.volume,
        }
        for c in candles
    ]
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("open_time").reset_index(drop=True)
    return df


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    # avg_loss == 0 con gain > 0 => nessuna perdita => RSI = 100
    out = out.where(~((avg_loss == 0) & (avg_gain > 0)), 100.0)
    # avg_gain == 0 e avg_loss == 0 (serie piatta) => RSI neutro 50
    return out.fillna(50.0)


def macd(
    series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    macd_line = ema(series, fast) - ema(series, slow)
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    return macd_line, signal_line, hist


def bollinger(series: pd.Series, period: int = 20, n_std: float = 2.0):
    mid = series.rolling(period).mean()
    std = series.rolling(period).std(ddof=0)
    upper = mid + n_std * std
    lower = mid - n_std * std
    return upper, mid, lower


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False).mean()


def vwap(df: pd.DataFrame) -> pd.Series:
    """VWAP intraday cumulativo sulle candele fornite."""
    typical = (df["high"] + df["low"] + df["close"]) / 3.0
    cum_vol = df["volume"].cumsum().replace(0, np.nan)
    return (typical * df["volume"]).cumsum() / cum_vol


def compute_indicator_frame(candles: list[Candle]) -> pd.DataFrame:
    """
    Calcola TUTTI gli indicatori sull'INTERA serie in una sola passata (vettoriale).
    Usato dal backtester per evitare di ricalcolare la finestra ad ogni barra.
    Ritorna un DataFrame con una riga per candela e una colonna per indicatore.
    """
    df = candles_to_df(candles)
    if df.empty:
        return df
    close = df["close"]
    macd_line, signal_line, hist = macd(close)
    bb_u, bb_m, bb_l = bollinger(close)
    df["ema_fast"] = ema(close, 9)
    df["ema_slow"] = ema(close, 21)
    df["rsi"] = rsi(close, 14)
    df["macd"] = macd_line
    df["macd_signal"] = signal_line
    df["macd_hist"] = hist
    df["bb_upper"] = bb_u
    df["bb_mid"] = bb_m
    df["bb_lower"] = bb_l
    df["atr"] = atr(df, 14)
    df["vwap"] = vwap(df)
    df["volume_sma"] = df["volume"].rolling(20).mean()
    return df


def snapshot_from_row(row, timeframe: str) -> IndicatorSnapshot:
    """Costruisce un IndicatorSnapshot da una riga di compute_indicator_frame."""
    def g(col):
        v = row.get(col)
        return None if v is None or pd.isna(v) else float(v)
    return IndicatorSnapshot(
        timeframe=timeframe,
        ema_fast=g("ema_fast"), ema_slow=g("ema_slow"), rsi=g("rsi"),
        macd=g("macd"), macd_signal=g("macd_signal"), macd_hist=g("macd_hist"),
        bb_upper=g("bb_upper"), bb_mid=g("bb_mid"), bb_lower=g("bb_lower"),
        atr=g("atr"), vwap=g("vwap"), close=g("close"),
        volume=g("volume"), volume_sma=g("volume_sma"),
    )


def compute_snapshot(candles: list[Candle], timeframe: str) -> IndicatorSnapshot:
    """
    Calcola TUTTI gli indicatori richiesti (EMA 9/21, RSI, MACD, Bollinger,
    ATR, VWAP, volume SMA) e restituisce l'ultimo valore in un IndicatorSnapshot.
    """
    df = candles_to_df(candles)
    snap = IndicatorSnapshot(timeframe=timeframe)
    if df.empty or len(df) < 2:
        return snap

    close = df["close"]
    macd_line, signal_line, hist = macd(close)
    bb_u, bb_m, bb_l = bollinger(close)

    def last(s: pd.Series):
        v = s.iloc[-1]
        return None if pd.isna(v) else float(v)

    snap.close = last(close)
    snap.volume = last(df["volume"])
    snap.ema_fast = last(ema(close, 9))
    snap.ema_slow = last(ema(close, 21))
    snap.rsi = last(rsi(close, 14))
    snap.macd = last(macd_line)
    snap.macd_signal = last(signal_line)
    snap.macd_hist = last(hist)
    snap.bb_upper = last(bb_u)
    snap.bb_mid = last(bb_m)
    snap.bb_lower = last(bb_l)
    snap.atr = last(atr(df, 14))
    snap.vwap = last(vwap(df))
    snap.volume_sma = last(df["volume"].rolling(20).mean())
    return snap
