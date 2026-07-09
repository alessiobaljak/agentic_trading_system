"""
PRIMO MATTONE — l'edge delle strategie validate REGGE nel periodo recente,
o è un miraggio che funzionava solo sui dati vecchi?

Per ogni coppia (coin, strategia) VALIDATA (stessi pair/parametri del bot, via
AdaptationEngine) fa girare la strategia coi suoi parametri finali su DUE periodi:
  * VECCHIO   : da --start a --split
  * RECENTE   : da --split a oggi   <-- la "linea di riferimento" per il monitor live
e confronta win-rate / profit factor / rendimento medio.

A cosa serve:
  1. dà l'ASPETTATIVA VERA e recente di ogni strategia (contro cui il paper misurerà);
  2. smaschera i MIRAGGI: validate che rendevano nel vecchio ma sono in perdita ORA.

Caveat onesto: i parametri finali sono stati scelti col walk-forward su TUTTO il
range, quindi non è un IS/OOS puro; misura la STABILITÀ/decadimento dell'edge nel
tempo — che è comunque il segnale piu' decisionale (ci interessa se funziona ORA).

Sola lettura, non tocca GATE 1 / registro. Uso sulla VPS:
    BACKTEST_ALLOW_SYNTHETIC=false .venv/bin/python -m scripts.edge_stability --limit 40 --split 2025-07-01
"""
from __future__ import annotations

import argparse

from backtesting.data_loader import load_candles
from backtesting.engine import Backtester
from bot.core.indicators import compute_indicator_frame
from bot.learning.adaptation import AdaptationEngine
from bot.strategies import get_all_strategies


def _metrics(stats) -> dict:
    n = len(stats.trades)
    return {
        "n": n,
        "wr": stats.win_rate() if n else 0.0,
        "pf": stats.profit_factor() if n else 0.0,
        "pnl": stats.total_pnl_pct() if n else 0.0,
    }


def _verdict(recent: dict, old: dict, min_recent: int) -> str:
    if recent["n"] < min_recent:
        return "? dati recenti scarsi"
    if recent["pf"] >= 1.15 and recent["pnl"] > 0:
        return "REGGE"
    if recent["pf"] < 1.0 or recent["pnl"] <= 0:
        # rendeva nel vecchio ma ORA perde -> miraggio/decadimento
        return "MIRAGGIO" if old["pf"] >= 1.2 else "in perdita"
    return "marginale"


def main() -> int:
    ap = argparse.ArgumentParser(description="Stabilità dell'edge: vecchio vs recente.")
    ap.add_argument("--limit", type=int, default=40, help="quante coin validate campionare")
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--split", default="2025-07-01", help="confine vecchio|recente")
    ap.add_argument("--interval", default="15m")
    ap.add_argument("--min-recent", type=int, default=20, help="min trade recenti per un verdetto")
    args = ap.parse_args()

    adaptation = AdaptationEngine()
    adaptation.load_params()
    adaptation.load_generated()
    coins = sorted(adaptation.validated_coins())[: args.limit]
    if not coins:
        print("Nessuna coin validata nel registro.")
        return 1

    interval_hours = {"15m": 0.25, "1h": 1.0, "5m": 1 / 12}.get(args.interval, 0.25)
    engine = Backtester(interval_hours=interval_hours)
    print(f"Analizzo {len(coins)} coin · vecchio [{args.start}..{args.split}) vs "
          f"recente [{args.split}..oggi)\n")

    rows = []
    for n, sym in enumerate(coins, 1):
        try:
            old_c = load_candles(sym, interval=args.interval, start=args.start,
                                 end=args.split, allow_synthetic=False)
            rec_c = load_candles(sym, interval=args.interval, start=args.split,
                                 allow_synthetic=False)
        except Exception as exc:  # noqa: BLE001
            print(f"  [{n}/{len(coins)}] {sym}: candele non caricate ({exc})")
            continue
        if len(old_c) < 300 or len(rec_c) < 300:
            print(f"  [{n}/{len(coins)}] {sym}: dati insufficienti, salto")
            continue
        of, rf = compute_indicator_frame(old_c), compute_indicator_frame(rec_c)
        strategies = get_all_strategies(adaptation.params_for(sym))
        strategies += adaptation.generated_strategies_for(sym)
        for strat in strategies:
            if not adaptation.is_enabled(sym, strat.name):
                continue
            old_m = _metrics(engine.run_strategy(strat, sym, old_c, frame=of))
            rec_m = _metrics(engine.run_strategy(strat, sym, rec_c, frame=rf))
            rows.append((sym, strat.name, old_m, rec_m,
                         _verdict(rec_m, old_m, args.min_recent)))
        print(f"  [{n}/{len(coins)}] {sym}: {len(rows)} coppie analizzate")

    if not rows:
        print("Nessuna coppia analizzata.")
        return 1

    # ordina: prima i miraggi / perdenti (recent pf crescente)
    rows.sort(key=lambda r: r[3]["pf"])
    print(f"\n{'coin':<13}{'strategia':<15}"
          f"{'VECCHIO pf/wr/n':>22}{'RECENTE pf/wr/n':>22}  verdetto")
    print("-" * 90)
    for sym, strat, o, r, v in rows:
        print(f"{sym:<13}{strat:<15}"
              f"{o['pf']:>7.2f}/{o['wr']*100:>3.0f}%/{o['n']:>5}"
              f"{r['pf']:>10.2f}/{r['wr']*100:>3.0f}%/{r['n']:>5}   {v}")

    # riepilogo
    from collections import Counter
    c = Counter(r[4] for r in rows)
    print(f"\n{'='*60}\nRIEPILOGO su {len(rows)} coppie validate:")
    for k in ["REGGE", "marginale", "in perdita", "MIRAGGIO", "? dati recenti scarsi"]:
        if c.get(k):
            print(f"  {k:<26} {c[k]}")
    holds = c.get("REGGE", 0)
    judged = sum(v for k, v in c.items() if not k.startswith("?"))
    if judged:
        print(f"\n-> {holds}/{judged} coppie giudicabili REGGONO nel recente "
              f"({holds/judged*100:.0f}%). Le altre sono candidate a essere frenate "
              f"dal monitor live.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
