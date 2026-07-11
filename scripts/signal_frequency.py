"""
Diagnostica: quanti segnali AVREBBERO dovuto generare le strategie validate
negli ultimi giorni? Serve a capire se lo "zero trade" del live e' il mercato
tranquillo (corretto) o un bug che sopprime i segnali.

Per ogni coin validata fa girare le sue strategie validate (stessi params del
bot) sulle candele 1h recenti e conta i trade (ingressi). Sola lettura.

Uso sulla VPS:
    BACKTEST_ALLOW_SYNTHETIC=false .venv/bin/python -m scripts.signal_frequency --days 7
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date, timedelta

from backtesting.data_loader import load_candles
from backtesting.engine import Backtester
from bot.core.indicators import compute_indicator_frame
from bot.learning.adaptation import AdaptationEngine
from bot.strategies import get_all_strategies


def main() -> int:
    ap = argparse.ArgumentParser(description="Frequenza di segnali attesa (recente).")
    ap.add_argument("--days", type=int, default=7, help="giorni recenti da valutare")
    ap.add_argument("--limit", type=int, default=200, help="quante coin validate")
    ap.add_argument("--interval", default="1h")
    args = ap.parse_args()

    adaptation = AdaptationEngine()
    adaptation.load_params()
    adaptation.load_generated()
    coins = sorted(adaptation.validated_coins())[: args.limit]
    if not coins:
        print("Nessuna coin validata nel registro.")
        return 1

    # warmup: l'engine salta le prime 200 candele (indicatori). Su 1h = ~8 giorni.
    # Carico days + 12 giorni di buffer, cosi' i trade contati cadono negli ultimi `days`.
    warmup_days = 12
    start = (date.today() - timedelta(days=args.days + warmup_days)).isoformat()
    engine = Backtester(interval_hours={"15m": 0.25, "1h": 1.0}.get(args.interval, 1.0))
    print(f"Conto i trade attesi negli ultimi ~{args.days}g su {len(coins)} coin "
          f"({args.interval}, da {start})...\n")

    per_coin: dict[str, int] = defaultdict(int)
    per_strat: dict[str, int] = defaultdict(int)
    total = 0
    for n, sym in enumerate(coins, 1):
        try:
            candles = load_candles(sym, interval=args.interval, start=start, allow_synthetic=False)
        except Exception as exc:  # noqa: BLE001
            print(f"  {sym}: candele non caricate ({exc})")
            continue
        if len(candles) < 250:
            continue
        frame = compute_indicator_frame(candles)
        strategies = get_all_strategies(adaptation.params_for(sym))
        strategies += adaptation.generated_strategies_for(sym)
        for strat in strategies:
            if not adaptation.is_enabled(sym, strat.name):
                continue
            stats = engine.run_strategy(strat, sym, candles, frame=frame)
            k = len(stats.trades)
            if k:
                per_coin[sym] += k
                per_strat[strat.name] += k
                total += k

    print(f"{'='*56}")
    print(f"TRADE ATTESI negli ultimi ~{args.days} giorni: {total}  "
          f"(~{total/max(args.days,1):.1f}/giorno)")
    print(f"\nPer coin (attive):")
    for sym, k in sorted(per_coin.items(), key=lambda x: -x[1]):
        print(f"  {sym:<14} {k}")
    print(f"\nPer strategia:")
    for s, k in sorted(per_strat.items(), key=lambda x: -x[1]):
        print(f"  {s:<18} {k}")
    print(f"\nLettura: se questo totale e' ~0, il mercato e' tranquillo e lo zero-trade")
    print(f"del live e' CORRETTO. Se e' alto (molti/giorno) ma il live non apre, allora")
    print(f"c'e' qualcosa nel percorso live che sopprime i segnali -> bug da cacciare.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
