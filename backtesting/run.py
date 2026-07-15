"""
CLI del backtest (GATE 1) — multi-asset.

Esempi:
  python -m backtesting.run --symbols BTCUSDT,ETHUSDT,SOLUSDT --start 2022-01-01 --end 2026-01-01
  python -m backtesting.run --source synthetic     # offline / CI

Gira ogni strategia su OGNI asset del paniere e AGGREGA i risultati per strategia
(così il verdetto non dipende da un singolo coin). Se il GATE non è superato esce
con codice 1 (utile in CI per bloccare la pipeline).
"""
from __future__ import annotations

import argparse
import sys

from backtesting.data_loader import load_candles
from backtesting.engine import Backtester, StrategyStats
from backtesting.report import write_excel, write_html
from bot.config import settings, timeframe_hours


def main() -> int:
    p = argparse.ArgumentParser(description="Backtest GATE 1 (multi-asset)")
    p.add_argument("--symbols", default="BTCUSDT",
                   help="lista separata da virgole, es: BTCUSDT,ETHUSDT,SOLUSDT")
    p.add_argument("--symbol", default=None, help="(retrocompat) singolo simbolo")
    p.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    p.add_argument("--start", default="2022-01-01")
    p.add_argument("--end", default=None, help="default: oggi")
    p.add_argument("--source", default="binance",
                   choices=["binance", "bybit", "okx", "coinmetrics", "synthetic"])
    p.add_argument("--capital", type=float, default=10_000.0)
    args = p.parse_args()

    symbols = [args.symbol] if args.symbol else [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    bt = Backtester(capital=args.capital, interval_hours=timeframe_hours(args.interval))

    # stats aggregate per strategia (trade uniti su tutti gli asset)
    aggregated: dict[str, StrategyStats] = {}
    per_symbol_loaded = 0

    for sym in symbols:
        print(f"[backtest] === {sym} {args.interval} {args.start}->{args.end} (source={args.source}) ===")
        candles = load_candles(sym, args.interval, args.start, args.end, prefer=args.source)
        if len(candles) < bt.window + 10:
            print(f"[backtest] {sym}: dati insufficienti ({len(candles)}), salto")
            continue
        per_symbol_loaded += 1
        stats = bt.run(sym, candles)
        for name, s in stats.items():
            agg = aggregated.setdefault(name, StrategyStats(strategy=name))
            agg.trades.extend(s.trades)
        # riepilogo per-asset
        for name, s in stats.items():
            if s.trades:
                print(f"    {name:22s} {sym:10s} trades={len(s.trades):4d} "
                      f"pf={s.profit_factor():4.2f} pnl={s.total_pnl_pct()*100:+6.1f}%")

    if per_symbol_loaded == 0:
        print("[backtest] nessun asset caricato — impossibile produrre un verdetto")
        return 1

    print(f"\n[backtest] === AGGREGATO su {per_symbol_loaded} asset ===")
    for name, s in aggregated.items():
        print(f"  {name:24s} trades={len(s.trades):4d} "
              f"win={s.win_rate()*100:5.1f}% pf={s.profit_factor():4.2f} "
              f"pnl={s.total_pnl_pct()*100:+7.1f}%")

    weights = bt.validate_learning(aggregated)
    verdict = bt.verdict(aggregated)

    html = write_html(aggregated, verdict, weights)
    xlsx = write_excel(aggregated)
    print(f"[backtest] report HTML: {html}")
    if xlsx:
        print(f"[backtest] Excel: {xlsx}")
    print(f"[backtest] VERDETTO ({per_symbol_loaded} asset): {verdict['message']}")

    return 0 if verdict["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
