"""
Job autonomo di ottimizzazione strategie (test -> learn -> iterate).

Per ogni asset del paniere:
  * carica i dati storici (OKX/Binance/Bybit, gratis),
  * esegue il walk-forward optimizer (parametri migliori, validati out-of-sample),
  * scrive su Firebase `strategy_params/current` i parametri + l'esito OOS per
    ogni (asset, strategia), e quali coppie hanno "passato".

NESSUNA validazione manuale: il bot legge questi parametri e li applica; la
prossima esecuzione schedulata ri-ottimizza su dati freschi (i parametri migliori
cambiano nel tempo, per questo gira periodicamente).

Uso:
  python -m scripts.optimize --symbols BTCUSDT,ETHUSDT,SOLUSDT
"""
from __future__ import annotations

import argparse
import time

from backtesting.data_loader import load_candles
from backtesting.optimizer import WalkForwardOptimizer
from bot.core.firebase_client import get_firebase


def main() -> int:
    p = argparse.ArgumentParser(description="Ottimizzazione walk-forward autonoma")
    p.add_argument("--symbols", default="BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT")
    p.add_argument("--interval", default="1h")
    p.add_argument("--start", default="2023-01-01")
    p.add_argument("--end", default="2026-01-01")
    p.add_argument("--source", default="binance")
    p.add_argument("--windows", type=int, default=3)
    args = p.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    opt = WalkForwardOptimizer(n_windows=args.windows)
    fb = get_firebase()

    out: dict[str, dict] = {}
    summary_passed: list[str] = []

    for sym in symbols:
        print(f"\n[optimize] === {sym} ===")
        candles = load_candles(sym, args.interval, args.start, args.end, prefer=args.source)
        if len(candles) < 1000:
            print(f"[optimize] {sym}: dati insufficienti ({len(candles)}), salto")
            continue
        results = opt.optimize_symbol(sym, candles)
        for r in results:
            key = f"{sym}|{r.strategy}"
            out[key] = {
                "symbol": sym, "strategy": r.strategy, "params": r.best_params,
                "oos_pf": r.oos_pf, "oos_pnl_pct": r.oos_pnl_pct,
                "oos_trades": r.oos_trades, "oos_win_rate": r.oos_win_rate,
                "passed": r.passed,
            }
            flag = "✅" if r.passed else "  "
            print(f"  {flag} {r.strategy:22s} pf={r.oos_pf:4.2f} pnl={r.oos_pnl_pct*100:+7.1f}% "
                  f"trades={r.oos_trades:4d} params={r.best_params}")
            if r.passed:
                summary_passed.append(key)

    fb.set_doc("strategy_params", "current", {
        "updated_at": time.time(),
        "entries": out,
        "passed": summary_passed,
    })

    print("\n" + "=" * 60)
    print(f"[optimize] {len(out)} coppie (asset×strategia) valutate, "
          f"{len(summary_passed)} hanno passato out-of-sample:")
    for k in summary_passed:
        print(f"   ✅ {k}  -> {out[k]['params']}")
    print("[optimize] parametri scritti su Firebase strategy_params/current")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
