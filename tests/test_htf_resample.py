"""La 1h nel backtest deve essere REALE (aggregata dal timeframe base), non un
alias della riga 15m: regime detector e trend_following leggono ind("1h")."""
from datetime import datetime, timedelta, timezone

from backtesting.engine import Backtester
from bot.core.indicators import compute_indicator_frame
from bot.core.models import Candle


def _candles_15m(n: int) -> list[Candle]:
    base = datetime(2024, 1, 1, tzinfo=timezone.utc)
    out, p = [], 100.0
    for k in range(n):
        p += 0.05 if k % 3 else -0.04
        out.append(Candle(open_time=base + timedelta(minutes=15 * k),
                          open=p, high=p + 0.5, low=p - 0.5, close=p + 0.1, volume=10))
    return out


def test_resample_aggregates_ohlcv():
    candles = _candles_15m(48)
    bt = Backtester(interval_hours=0.25)
    hc = bt._resample_1h(candles)
    assert len(hc) == 12
    assert hc[0].open == candles[0].open
    assert hc[0].close == candles[3].close
    assert hc[0].high == max(c.high for c in candles[:4])
    assert hc[0].low == min(c.low for c in candles[:4])
    assert hc[0].volume == sum(c.volume for c in candles[:4])


def test_h_idx_uses_only_closed_hour_bars():
    # niente look-ahead: la barra 15m usa solo l'ultima 1h GIA' CHIUSA.
    candles = _candles_15m(16)
    bt = Backtester(interval_hours=0.25)
    _, h_idx = bt._htf_for(candles)
    # le prime 3 barre 15m: l'ora 00 non e' ancora chiusa -> -1
    assert h_idx[0] == -1 and h_idx[2] == -1
    # la barra 00:45 chiude alle 01:00 -> l'ora 00 e' chiusa -> indice 0
    assert h_idx[3] == 0
    assert h_idx[7] == 1


def test_snapshot_1h_key_is_real_not_alias():
    candles = _candles_15m(48 * 8)
    bt = Backtester(interval_hours=0.25)
    frame = compute_indicator_frame(candles)
    htf = bt._htf_for(candles)
    snap = bt._snapshot_from_frame("X", frame, 300, htf=htf)
    i15, i1h = snap.indicators["15m"], snap.indicators["1h"]
    assert i1h.timeframe == "1h"
    assert i1h.atr != i15.atr, "la 1h deve venire dal resample, non essere un alias"


def test_at_1h_no_resample_keys_alias():
    # timeframe base gia' 1h: nessun resample, la "1h" e' la riga stessa.
    candles = _candles_15m(300)   # i timestamp non contano qui
    bt = Backtester(interval_hours=1.0)
    assert bt._htf_for(candles) is None
