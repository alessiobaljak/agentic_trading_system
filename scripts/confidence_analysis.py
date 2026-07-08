"""
LIVELLO 0 — la confidenza (o qualche feature per-segnale) predice l'esito del trade?

Prerequisito per qualsiasi sizing/leva DINAMICI: se nessuna feature disponibile
all'ingresso separa i vincitori dai perdenti, modulare la size non ha basi.

Cosa fa (SOLA LETTURA, non tocca GATE 1 / registro):
  * rigira le strategie VALIDATE (stessi pair e parametri del bot, via
    AdaptationEngine) sul backtest reale e raccoglie i trade con confidenza,
    pnl_pct, escursione avversa, regime, direzione, ora;
  * mostra la DISTRIBUZIONE della confidenza (attesa: ~costante -> nessun segnale);
  * per ogni feature disponibile riporta win-rate e pnl medio per bucket, e lo
    SPREAD tra bucket migliore e peggiore (quanto la feature separa l'esito).

Uso sulla VPS (dati Binance reali):
    BACKTEST_ALLOW_SYNTHETIC=false .venv/bin/python -m scripts.confidence_analysis --limit 30
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from statistics import mean

from backtesting.data_loader import load_candles
from backtesting.engine import Backtester
from bot.core.indicators import compute_indicator_frame
from bot.learning.adaptation import AdaptationEngine
from bot.strategies import get_all_strategies


def _bucket_report(title: str, trades: list, key) -> None:
    """Win-rate e pnl_pct medio per bucket + spread tra migliore e peggiore."""
    groups: dict = defaultdict(list)
    for t in trades:
        groups[key(t)].append(t)
    rows = []
    for k, ts in groups.items():
        if len(ts) < 20:  # ignora bucket troppo piccoli (rumore)
            continue
        wr = sum(1 for t in ts if t.is_win) / len(ts)
        pnl = mean(t.pnl_pct for t in ts)
        rows.append((str(k), len(ts), wr, pnl))
    if not rows:
        print(f"\n[{title}] nessun bucket con >= 20 trade.")
        return
    rows.sort(key=lambda r: r[2], reverse=True)
    print(f"\n[{title}]  {'bucket':<16} {'n':>6} {'win%':>6} {'pnl%_medio':>11}")
    for name, n, wr, pnl in rows:
        print(f"  {'':2}{name:<16} {n:>6} {wr*100:>5.1f}% {pnl*100:>10.3f}%")
    wr_spread = rows[0][2] - rows[-1][2]
    print(f"  -> SPREAD win-rate migliore vs peggiore: {wr_spread*100:.1f} punti "
          f"({'RILEVANTE' if wr_spread >= 0.08 else 'debole'})")


def main() -> int:
    ap = argparse.ArgumentParser(description="Livello 0: la confidenza/feature predice l'esito?")
    ap.add_argument("--limit", type=int, default=30, help="quante coin validate campionare")
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--interval", default="15m")
    args = ap.parse_args()

    adaptation = AdaptationEngine()
    adaptation.load_params()
    adaptation.load_generated()
    coins = sorted(adaptation.validated_coins())[: args.limit]
    if not coins:
        print("Nessuna coin validata nel registro. (Registro non caricato?)")
        return 1

    interval_hours = {"15m": 0.25, "1h": 1.0, "5m": 1 / 12}.get(args.interval, 0.25)
    engine = Backtester(interval_hours=interval_hours)
    print(f"Analizzo {len(coins)} coin validate su {args.interval} da {args.start}...")

    trades = []
    for n, sym in enumerate(coins, 1):
        try:
            candles = load_candles(sym, interval=args.interval, start=args.start,
                                   allow_synthetic=False)
        except Exception as exc:  # noqa: BLE001
            print(f"  [{n}/{len(coins)}] {sym}: candele non caricate ({exc})")
            continue
        if not candles or len(candles) < 300:
            print(f"  [{n}/{len(coins)}] {sym}: dati insufficienti, salto")
            continue
        frame = compute_indicator_frame(candles)
        strategies = get_all_strategies(adaptation.params_for(sym))
        strategies += adaptation.generated_strategies_for(sym)
        for strat in strategies:
            if not adaptation.is_enabled(sym, strat.name):
                continue
            stats = engine.run_strategy(strat, sym, candles, frame=frame)
            trades.extend(stats.trades)
        print(f"  [{n}/{len(coins)}] {sym}: {len(trades)} trade cumulati")

    if not trades:
        print("Nessun trade generato.")
        return 1

    # ---- quadro generale ----
    wr = sum(1 for t in trades if t.is_win) / len(trades)
    print(f"\n{'='*60}")
    print(f"TRADE TOTALI: {len(trades)}  ·  win-rate {wr*100:.1f}%  ·  "
          f"pnl%_medio {mean(t.pnl_pct for t in trades)*100:.3f}%")

    # ---- la confidenza varia? ----
    conf = Counter(round(t.confidence_at_entry) for t in trades)
    print(f"\n[CONFIDENZA] valori distinti e frequenza: {dict(sorted(conf.items()))}")
    if len(conf) <= 1:
        print("  -> COSTANTE: nessuna informazione per-segnale. Sizing per confidenza IMPOSSIBILE.")
    else:
        _bucket_report("CONFIDENZA vs esito", trades, lambda t: round(t.confidence_at_entry))

    # ---- feature disponibili: separano l'esito? ----
    _bucket_report("REGIME all'ingresso", trades, lambda t: t.regime_at_entry)
    _bucket_report("DIREZIONE", trades, lambda t: t.direction)
    _bucket_report("FASCIA ORARIA", trades, lambda t: f"{(t.hour_bucket // 6) * 6:02d}-{(t.hour_bucket // 6) * 6 + 5:02d}h")

    # escursione avversa in quartili: predice l'esito?
    advs = sorted(t.max_adverse_pct for t in trades)
    q = [advs[len(advs) // 4], advs[len(advs) // 2], advs[3 * len(advs) // 4]]

    def adv_bucket(t):
        a = t.max_adverse_pct
        if a <= q[0]:
            return "Q1_bassa"
        if a <= q[1]:
            return "Q2"
        if a <= q[2]:
            return "Q3"
        return "Q4_alta"

    _bucket_report("ESCURSIONE AVVERSA (quartili)", trades, adv_bucket)

    print(f"\n{'='*60}")
    print("Lettura: se NESSUNA feature ha uno spread win-rate 'RILEVANTE' (>= 8 punti),")
    print("il sizing dinamico non ha basi coi dati attuali -> serve prima costruire un")
    print("punteggio di confidenza REALE (Livello 0b: arricchire il record con gli")
    print("indicatori all'ingresso e ri-testare).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
