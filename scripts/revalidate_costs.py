"""RE-VALIDAZIONE a costi nuovi SENZA ri-ottimizzare.

Prende le coppie GIA' validate (coi LORO parametri) e ri-esegue il backtest
walk-forward OOS col MODELLO DI COSTO NUOVO (bot/core/costs.py). Tiene solo le
coppie che passano ancora il GATE 1 con costi onesti; scarta le altre. NON
ri-cerca entrata/uscita (i parametri restano quelli), verifica solo il PROFITTO
reale -> una passata, niente ricostruzione da zero (le strategie NON si perdono).

Dry-run di DEFAULT (mostra e basta). --apply scrive il registro ripulito.

Uso sulla VPS:
    BACKTEST_ALLOW_SYNTHETIC=false .venv/bin/python -m scripts.revalidate_costs           # dry-run
    BACKTEST_ALLOW_SYNTHETIC=false .venv/bin/python -m scripts.revalidate_costs --apply    # scrive
"""
from __future__ import annotations

import argparse
import time

from backtesting.data_loader import load_candles
from backtesting.engine import Backtester, StrategyStats, passes_gate
from bot.config import settings, timeframe_hours
from bot.core.firebase_client import decode_pairs, encode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.learning.adaptation import AdaptationEngine
from bot.strategies import get_all_strategies


def _windows(n: int, n_windows: int, warmup: int):
    """Stesse finestre walk-forward dell'optimizer: [(ta, tb, test_a, test_b), ...]."""
    blocks = n_windows + 1
    size = n // blocks
    if size <= warmup + 50:
        return []
    return [(w * size, (w + 1) * size, (w + 1) * size, min((w + 2) * size, n))
            for w in range(n_windows)]


def main() -> int:
    ap = argparse.ArgumentParser(description="Ri-valida le coppie esistenti coi costi nuovi.")
    ap.add_argument("--windows", type=int, default=3)
    ap.add_argument("--start", default="2022-01-01")
    # stesso timeframe del sistema: ri-validare un registro 15m su dati 1h
    # (o viceversa) non ha senso.
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--limit", type=int, default=0, help="0 = tutte le coin validate")
    ap.add_argument("--apply", action="store_true", help="scrive il registro (default: dry-run)")
    args = ap.parse_args()

    fb = get_firebase()
    adaptation = AdaptationEngine()
    adaptation.load_params()
    adaptation.load_generated()

    reg = fb.get_doc("strategy_registry", "validated") or {}
    old_pairs = decode_pairs(reg.get("pairs"))
    coins = sorted(adaptation.validated_coins())
    if args.limit:
        coins = coins[: args.limit]
    if not coins:
        print("Registro vuoto / nessuna coin validata.")
        return 1

    ih = timeframe_hours(args.interval)
    from backtesting.data_loader import funding_rate_for
    engine = Backtester(interval_hours=ih, funding_rate_provider=funding_rate_for)
    kept: dict[str, dict] = {}
    dropped: list[tuple[str, float, int]] = []
    print(f"Ri-valido {len(coins)} coin a costi nuovi ({args.interval}, da {args.start})...\n")

    for n_i, sym in enumerate(coins, 1):
        try:
            candles = load_candles(sym, interval=args.interval, start=args.start, allow_synthetic=False)
        except Exception as exc:  # noqa: BLE001
            print(f"  [{n_i}/{len(coins)}] {sym}: dati non caricati ({exc})")
            continue
        if len(candles) < 400:
            continue
        frame = compute_indicator_frame(candles)
        wins = _windows(len(candles), args.windows, engine.window)
        if not wins:
            continue
        strategies = get_all_strategies(adaptation.params_for(sym))
        strategies += adaptation.generated_strategies_for(sym)
        for strat in strategies:
            if not adaptation.is_enabled(sym, strat.name):   # SOLO coppie gia' validate
                continue
            key = f"{sym}|{strat.name}"
            agg = StrategyStats(strategy=strat.name)
            window_pnls: list[float] = []
            for (_ta, _tb, sa, sb) in wins:
                st = engine.run_strategy(strat, sym, candles[sa:sb],
                                         frame=frame.iloc[sa:sb].reset_index(drop=True))
                agg.trades.extend(st.trades)
                if st.trades:
                    window_pnls.append(sum(t.pnl_pct for t in st.trades))
            pf, wr, pnl = agg.profit_factor(), agg.win_rate(), agg.total_pnl_pct()
            if passes_gate(window_pnls, len(agg.trades), pf, wr, pnl):
                tc = agg.trailing_counts()
                rec = dict(old_pairs.get(key, {}))
                rec.update({
                    "symbol": sym, "strategy": strat.name,
                    "pass_count": max(int(rec.get("pass_count", 0)), 3),
                    "last_pf": round(pf, 3), "last_pnl_pct": round(pnl, 4),
                    "last_trades": len(agg.trades), "last_win_rate": round(wr, 3),
                    "last_passed_at": time.time(), "last_seen_at": time.time(),
                    # verdetto trailing (per il bot: se troppi 'premature' -> allentare)
                    "trailing_premature": tc["premature"],
                    "trailing_protected": tc["protected"],
                    "trailing_neutral": tc["neutral"],
                })
                kept[key] = rec
            else:
                dropped.append((key, round(pf, 3), len(agg.trades)))
        print(f"  [{n_i}/{len(coins)}] {sym}: {len(kept)} tenute cumul.")

    covered = sorted({r["symbol"] for r in kept.values()})
    print(f"\n{'='*60}")
    print(f"TENUTE: {len(kept)} coppie · SCARTATE: {len(dropped)} · coin coperte: {len(covered)}")
    print(f"(prima erano {len(old_pairs)} coppie nel registro)")
    # metrica DECISIVA per confrontare on/off del profit-lock: PnL OOS aggregato
    agg_pnl = sum(r.get("last_pnl_pct", 0) for r in kept.values())
    agg_tr = sum(r.get("last_trades", 0) for r in kept.values())
    print(f"PnL OOS AGGREGATO (somma coppie tenute): {agg_pnl*100:.0f}%  su {agg_tr} trade "
          f"-> confronta questo numero tra profit-lock ON e OFF")

    # riepilogo GLOBALE del trailing: il profit-lock aiuta o danneggia?
    prem = sum(r.get("trailing_premature", 0) for r in kept.values())
    prot = sum(r.get("trailing_protected", 0) for r in kept.values())
    neu = sum(r.get("trailing_neutral", 0) for r in kept.values())
    tot = prem + prot + neu
    if tot:
        print(f"\nTRAILING (su {tot} uscite trailing):")
        print(f"  prematuro (tagliato un vincitore): {prem}  ({prem/tot*100:.0f}%)")
        print(f"  protetto  (evitata una perdita):   {prot}  ({prot/tot*100:.0f}%)")
        print(f"  neutro:                            {neu}  ({neu/tot*100:.0f}%)")
        verdict = ("il profit-lock DANNEGGIA (piu' prematuri che protetti)" if prem > prot
                   else "il profit-lock AIUTA (piu' protetti che prematuri)")
        print(f"  -> {verdict}")
    if dropped:
        print("\nPrime scartate (PF sotto soglia coi costi nuovi):")
        for k, pf, nt in sorted(dropped, key=lambda x: x[1])[:25]:
            print(f"  {k:<30} pf={pf:<6} trade={nt}")

    if not args.apply:
        print("\n[DRY-RUN] niente scritto. Rilancia con --apply per applicare la pulizia.")
        return 0
    new_reg = dict(reg)
    new_reg.update({
        "updated_at": time.time(), "pairs": encode_pairs(kept),
        "validated": sorted(kept.keys()), "coins_covered": len(covered), "coins": covered,
    })
    fb.set_doc("strategy_registry", "validated", new_reg)
    print(f"\n[APPLICATO] registro ripulito: {len(kept)} coppie su {len(covered)} coin.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
