"""
A/B del modello di uscita: TP UNICO (attuale) vs SCALE-OUT su multipli di R.

Gira lo STESSO walk-forward optimizer del GATE 1, sugli STESSI dati e con lo
STESSO seed, due volte:
  A) baseline  -> SCALE_OUT_ENABLED = False   (modello attuale)
  B) scale-out -> SCALE_OUT_ENABLED = True    (50% a 1R, 30% a 2R, 20% a 3R + BE)
L'unica differenza tra i due run è il modello di uscita: così il confronto è
apples-to-apples e i numeri dicono se lo scale-out BATTE l'attuale.

NON tocca Firebase: nessuna scrittura sul registro live, nessun impatto sul bot.
Stampa un confronto e salva un report markdown.

Uso (sul VPS, dove load_candles vede Binance):
  python -m scripts.ab_scale_out --top 30
  python -m scripts.ab_scale_out --symbols BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT --windows 3
Opzioni utili: --interval (default = timeframe del bot), --start, --max-combos,
  --seed (fisso per riproducibilità), --out (path del report).
"""
from __future__ import annotations

import argparse
import gc
import os

from bot.config import settings, timeframe_hours
from backtesting.data_loader import load_candles
from backtesting.optimizer import WalkForwardOptimizer
from scripts.optimize import top_symbols_by_volume


def _min_history(interval: str) -> int:
    env = os.getenv("OPTIMIZER_MIN_HISTORY")
    if env:
        return int(env)
    days = float(os.getenv("OPTIMIZER_MIN_HISTORY_DAYS", "180"))
    return int(days * 24.0 / timeframe_hours(interval))


def _aggregate(rows: list, min_trades: int) -> dict:
    """rows = OptResult (coppie coin×strategia). Confronto sull'ECONOMIA OOS di
    TUTTE le coppie attive (li' si vede l'effetto del modello di uscita), non solo
    sul GATE pieno: quest'ultimo e' CUMULATIVO (piu' passate) e in una singola
    passata passa quasi nulla -> darebbe 0 vs 0, cieco."""
    active = [r for r in rows if r.oos_trades >= min_trades]
    soft = [r for r in active if r.oos_pf >= 1.10 and r.oos_pnl_pct > 0]
    strict = [r for r in rows if r.passed]
    coins_all = {r.symbol for r in rows}
    coins_soft = {r.symbol for r in soft}

    def _avg(vals):
        vals = list(vals)
        return sum(vals) / len(vals) if vals else 0.0

    return {
        "pairs_total": len(rows),
        "pairs_active": len(active),
        "total_trades": sum(r.oos_trades for r in rows),
        # economia OOS su tutte le coppie attive
        "total_oos_return": sum(r.oos_pnl_pct for r in active),
        "avg_oos_return": _avg(r.oos_pnl_pct for r in active),
        "avg_pf": _avg(r.oos_pf for r in active),
        "avg_winrate": _avg(r.oos_win_rate for r in active),
        "pct_positive": (sum(1 for r in active if r.oos_pnl_pct > 0) / len(active)) if active else 0.0,
        # "soft gate": coppie interessanti in questa passata (pf>=1.1 & ritorno>0)
        "soft_pass": len(soft),
        "soft_coins": len(coins_soft),
        "coins_total": len(coins_all),
        # gate PIENO (cumulativo su piu' passate): di norma 0 in una singola passata
        "strict_pass": len(strict),
    }


def _opt_symbol(sym, candles, btc_ctx, args, enabled: bool) -> list:
    """Walk-forward su UNA coin per UN modello di uscita. Optimizer FRESCO con seed
    fisso: baseline e scale-out vedono la STESSA sequenza RNG (stessi split/combo)."""
    settings.SCALE_OUT_ENABLED = enabled
    opt = WalkForwardOptimizer(
        n_windows=args.windows, max_combos=args.max_combos,
        seed=args.seed, interval=args.interval,
    )
    try:
        return opt.optimize_symbol(sym, candles, context_by_ts=btc_ctx)
    except Exception as exc:  # noqa: BLE001
        print(f"  {sym} ({'ON' if enabled else 'OFF'}) saltato: {str(exc)[:80]}")
        return []


def _fmt(a: dict) -> str:
    return (
        f"  coppie attive     : {a['pairs_active']}/{a['pairs_total']} "
        f"(>= trade OOS min)\n"
        f"  ritorno OOS totale: {a['total_oos_return']*100:.1f}%  "
        f"(medio {a['avg_oos_return']*100:.2f}%/coppia)\n"
        f"  PF medio          : {a['avg_pf']:.3f}\n"
        f"  win rate medio    : {a['avg_winrate']*100:.1f}%\n"
        f"  coppie positive   : {a['pct_positive']*100:.1f}%  (ritorno OOS > 0)\n"
        f"  soft-pass         : {a['soft_pass']} su {a['soft_coins']}/{a['coins_total']} coin "
        f"(pf>=1.1 & ritorno>0)\n"
        f"  strict-pass (gate pieno, cumulativo): {a['strict_pass']}\n"
        f"  trade OOS totali  : {a['total_trades']}"
    )


def _delta_line(name: str, base, test, pct=False, dp=3) -> str:
    d = test - base
    arrow = "▲" if d > 0 else ("▼" if d < 0 else "=")
    if pct:
        return f"  {name:<22} {base*100:7.1f}%  ->  {test*100:7.1f}%   {arrow} {d*100:+.1f} pt"
    return f"  {name:<22} {base:9.{dp}f}  ->  {test:9.{dp}f}   {arrow} {d:+.{dp}f}"


def main() -> int:
    p = argparse.ArgumentParser(description="A/B TP unico vs scale-out su R")
    p.add_argument("--symbols", default="BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT")
    p.add_argument("--top", type=int, default=0, help="se >0, usa i top-N per volume")
    p.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    p.add_argument("--start", default="2022-01-01")
    p.add_argument("--end", default=None)
    p.add_argument("--source", default="binance")
    p.add_argument("--windows", type=int, default=3)
    p.add_argument("--max-combos", type=int, default=12, dest="max_combos")
    p.add_argument("--seed", type=int, default=12345, help="FISSO per entrambi i run (equità)")
    p.add_argument("--min-trades", type=int, default=None, dest="min_trades",
                   help="trade OOS minimi per considerare una coppia (default: GATE_MIN_TRADES)")
    p.add_argument("--out", default=None, help="path report markdown (default: scripts/ab_scale_out_report.md)")
    args = p.parse_args()

    min_trades = args.min_trades if args.min_trades is not None else settings.GATE_MIN_TRADES
    end = args.end
    symbols = top_symbols_by_volume(args.top) if args.top > 0 else \
        [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    print(f"[ab] universo: {len(symbols)} coin · interval {args.interval} · "
          f"windows {args.windows} · max_combos {args.max_combos} · seed {args.seed}")

    min_hist = _min_history(args.interval)

    # --- contesto BTC (per le strategie cross-asset), caricato UNA volta ---
    # tenuto in memoria per tutte le coin (come fa l'optimizer di produzione).
    btc_ctx = None
    tmp = WalkForwardOptimizer(n_windows=args.windows, max_combos=args.max_combos,
                               seed=args.seed, interval=args.interval)
    try:
        btc_candles = load_candles("BTCUSDT", args.interval, args.start, end, prefer=args.source)
        if len(btc_candles) >= 200:
            btc_ctx = tmp.bt.build_context("BTCUSDT", btc_candles)
        del btc_candles
        gc.collect()
    except Exception as exc:  # noqa: BLE001
        print(f"[ab] contesto BTC non disponibile ({str(exc)[:60]})")

    # --- una coin alla volta: carica -> baseline + scale-out -> LIBERA memoria ---
    # (stesso footprint della validazione vera; evita l'OOM sulla VPS)
    rows_base: list = []
    rows_test: list = []
    done = 0
    for i, sym in enumerate(symbols, 1):
        try:
            candles = load_candles(sym, args.interval, args.start, end, prefer=args.source)
        except Exception as exc:  # noqa: BLE001
            print(f"  {sym} errore caricamento: {str(exc)[:70]}")
            continue
        if len(candles) < min_hist:
            print(f"  {sym} storia insufficiente ({len(candles)}<{min_hist}), skip")
            del candles
            continue
        rows_base.extend(_opt_symbol(sym, candles, btc_ctx, args, enabled=False))
        rows_test.extend(_opt_symbol(sym, candles, btc_ctx, args, enabled=True))
        done += 1
        print(f"  {i}/{len(symbols)} {sym} ({len(candles)} candele) ✓")
        del candles
        gc.collect()

    settings.SCALE_OUT_ENABLED = False  # ripristina lo stato di default
    if done == 0:
        print("[ab] nessuna coin con storia sufficiente. Interrompo.")
        return 1
    print(f"[ab] processate {done} coin. Aggrego…")
    base = _aggregate(rows_base, min_trades)
    test = _aggregate(rows_test, min_trades)

    # --- confronto ---
    report = []
    report.append("=" * 66)
    report.append("A/B MODELLO DI USCITA — TP unico (baseline) vs SCALE-OUT su R")
    report.append("=" * 66)
    report.append(f"universo {len(symbols)} coin · interval {args.interval} · "
                  f"windows {args.windows} · seed {args.seed} · min_trades {min_trades}")
    report.append("Confronto sull'ECONOMIA OOS di TUTTE le coppie (una passata): "
                  "il gate pieno e' cumulativo e qui darebbe 0 vs 0.")
    report.append("")
    report.append("[A] BASELINE (TP unico)")
    report.append(_fmt(base))
    report.append("")
    report.append("[B] SCALE-OUT (50% 1R / 30% 2R / 20% 3R + break-even dopo TP1)")
    report.append(_fmt(test))
    report.append("")
    report.append("DELTA (B - A)  [meglio se ▲]")
    report.append(_delta_line("ritorno OOS totale", base["total_oos_return"], test["total_oos_return"], pct=True))
    report.append(_delta_line("PF medio", base["avg_pf"], test["avg_pf"]))
    report.append(_delta_line("win rate medio", base["avg_winrate"], test["avg_winrate"], pct=True))
    report.append(_delta_line("coppie positive", base["pct_positive"], test["pct_positive"], pct=True))
    report.append(_delta_line("soft-pass (n)", base["soft_pass"], test["soft_pass"], dp=0))
    report.append("")
    # verdetto: quante metriche chiave migliorano
    score = 0
    score += 1 if test["total_oos_return"] > base["total_oos_return"] else 0
    score += 1 if test["avg_pf"] >= base["avg_pf"] else 0
    score += 1 if test["pct_positive"] >= base["pct_positive"] else 0
    score += 1 if test["soft_pass"] >= base["soft_pass"] else 0
    if score >= 3 and test["total_oos_return"] > base["total_oos_return"]:
        report.append(f"VERDETTO: SCALE-OUT MEGLIO ({score}/4 metriche chiave a favore) "
                      "-> candidato standard; conferma con ri-validazione completa.")
    elif score <= 1:
        report.append(f"VERDETTO: SCALE-OUT PEGGIO ({score}/4) -> resta il TP unico, "
                      "oppure ritara i livelli R (SCALE_OUT_R_MULTIPLES/FRACTIONS).")
    else:
        report.append(f"VERDETTO: MISTO ({score}/4) -> dipende dalla priorita' "
                      "(ritorno vs PF/consistenza). Valutare ritaratura dei livelli R.")
    report.append("=" * 66)

    text = "\n".join(report)
    print("\n" + text)

    out = args.out or os.path.join(os.path.dirname(__file__), "ab_scale_out_report.md")
    try:
        with open(out, "w") as f:
            f.write("```\n" + text + "\n```\n")
        print(f"\n[ab] report salvato in {out}")
    except Exception as exc:  # noqa: BLE001
        print(f"[ab] impossibile scrivere il report: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
