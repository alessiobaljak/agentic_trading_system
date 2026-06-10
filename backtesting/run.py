"""
CLI del backtest (GATE 1).

Esempi:
  python -m backtesting.run --symbol BTCUSDT --interval 1h --start 2022-01-01 --end 2026-01-01
  python -m backtesting.run --source synthetic     # offline / CI

Se il GATE non è superato esce con codice 1 (utile in CI per bloccare la pipeline).
"""
from __future__ import annotations

import argparse
import sys

from backtesting.data_loader import load_candles
from backtesting.engine import Backtester
from backtesting.report import write_excel, write_html


def main() -> int:
    p = argparse.ArgumentParser(description="Backtest GATE 1")
    p.add_argument("--symbol", default="BTCUSDT")
    p.add_argument("--interval", default="1h")
    p.add_argument("--start", default="2022-01-01")
    p.add_argument("--end", default="2026-01-01")
    p.add_argument("--source", default="binance",
                   choices=["binance", "coinmetrics", "synthetic"])
    p.add_argument("--capital", type=float, default=10_000.0)
    args = p.parse_args()

    print(f"[backtest] carico dati {args.symbol} {args.interval} {args.start}->{args.end} "
          f"(source={args.source})")
    candles = load_candles(args.symbol, args.interval, args.start, args.end,
                           prefer=args.source)
    print(f"[backtest] {len(candles)} candele caricate")

    bt = Backtester(capital=args.capital)
    all_stats = bt.run(args.symbol, candles)

    for name, stats in all_stats.items():
        print(f"  {name:24s} trades={len(stats.trades):4d} "
              f"win={stats.win_rate()*100:5.1f}% pf={stats.profit_factor():4.2f} "
              f"pnl={stats.total_pnl_pct()*100:+6.1f}%")

    weights = bt.validate_learning(all_stats)
    verdict = bt.verdict(all_stats)

    html = write_html(all_stats, verdict, weights)
    xlsx = write_excel(all_stats)
    print(f"[backtest] report HTML: {html}")
    if xlsx:
        print(f"[backtest] Excel: {xlsx}")
    print(f"[backtest] VERDETTO: {verdict['message']}")

    return 0 if verdict["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
