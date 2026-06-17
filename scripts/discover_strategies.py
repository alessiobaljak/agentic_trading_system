"""
Scoperta autonoma di NUOVE strategie (il "cervello" che ne aggiunge altre).

Genera N strategie candidate (combinazioni di feature su indicatori, vedi
bot/strategies/generator.py) e le valida con lo STESSO gate delle 6 base:
walk-forward OUT-OF-SAMPLE, al netto di fee+funding. Le candidate che passano su
una crypto vengono:
  * aggiunte al registro validato (strategy_registry/validated) -> operabili dal bot
  * salvate come spec su discovered_strategies/specs -> il bot le ricostruisce
NON tocca le strategie esistenti né la copertura del GATE 1.

Le strategie sono DATA (spec), non codice eseguito: sicuro e scalabile a centinaia.

Uso:
    python -m scripts.discover_strategies --top 25 --generate 40 --windows 3
"""
from __future__ import annotations

import argparse
import os
import time
from datetime import date

from backtesting.data_loader import load_candles
from backtesting.engine import StrategyStats
from backtesting.optimizer import WalkForwardOptimizer
from bot.core.firebase_client import get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.strategies.generated import GeneratedStrategy
from bot.strategies.generator import generate_specs, mutate
from scripts.optimize import FRESH_DAYS, MIN_PASSES, top_symbols_by_volume

PF_THRESHOLD = 1.10
MIN_OOS_TRADES = 10


def evaluate_spec(opt: WalkForwardOptimizer, symbol: str, candles, frame, spec: dict):
    """Aggrega le performance del spec sulle SOLE finestre out-of-sample."""
    oos = StrategyStats(strategy=spec["id"])
    for (_ta, _tb, sa, sb) in opt._windows(len(candles)):
        test_c = candles[sa:sb]
        test_f = frame.iloc[sa:sb].reset_index(drop=True)
        st = opt.bt.run_strategy(GeneratedStrategy(spec), symbol, test_c, frame=test_f)
        oos.trades.extend(st.trades)
    pf = oos.profit_factor()
    pnl = oos.total_pnl_pct()
    passed = (len(oos.trades) >= MIN_OOS_TRADES and pf >= PF_THRESHOLD and pnl > 0)
    return {
        "pf": round(pf, 3), "pnl": round(pnl, 4),
        "trades": len(oos.trades), "win": round(oos.win_rate(), 3), "passed": passed,
    }


def merge_into_registry(fb, out: dict, passed_now: list[str]) -> list[str]:
    """Aggiunge SOLO le coppie generate che PASSANO (accumula pass_count) e pota
    quelle generate inutili/stantie, evitando crescita illimitata del documento.
    Ricalcola la lista validated PRESERVANDO i campi di copertura del GATE 1
    (universe/coverage/ready) che spettano a optimize.py."""
    doc = fb.get_doc("strategy_registry", "validated") or {}
    pairs = doc.get("pairs", {}) or {}
    now = time.time()
    # 1) upsert SOLO delle coppie passate (non sporco il registro con i fallimenti)
    for key in passed_now:
        e = out[key]
        rec = pairs.get(key, {"pass_count": 0})
        rec["pass_count"] = rec.get("pass_count", 0) + 1
        rec["last_params"] = e["params"]
        rec["last_pf"] = e["oos_pf"]
        rec["last_pnl_pct"] = e["oos_pnl_pct"]
        rec["last_trades"] = e["oos_trades"]
        rec["symbol"] = e["symbol"]
        rec["strategy"] = e["strategy"]
        rec["generated"] = True
        rec["last_seen_at"] = now
        rec["last_passed_at"] = now
        pairs[key] = rec
    # 2) potatura: scarta le coppie GENERATE senza valore (pass_count 0) o stantie
    #    e non validate. Le coppie BASE (optimize.py, senza flag generated) restano.
    stale_before = now - FRESH_DAYS * 86400 * 2
    pairs = {
        k: r for k, r in pairs.items()
        if not (r.get("generated") and (
            r.get("pass_count", 0) == 0
            or (r.get("pass_count", 0) < MIN_PASSES and r.get("last_seen_at", 0) < stale_before)
        ))
    }
    validated = sorted(
        k for k, r in pairs.items()
        if r.get("pass_count", 0) >= MIN_PASSES
        and (now - r.get("last_seen_at", 0)) < FRESH_DAYS * 86400
    )
    doc["pairs"] = pairs
    doc["validated"] = validated
    doc["updated_at"] = now
    fb.set_doc("strategy_registry", "validated", doc)
    return validated


def persist_specs(fb, specs_by_id: dict) -> None:
    doc = fb.get_doc("discovered_strategies", "specs") or {}
    specs = doc.get("specs", {}) or {}
    specs.update(specs_by_id)
    fb.set_doc("discovered_strategies", "specs", {"specs": specs, "updated_at": time.time()})


def _notify(passed: list[dict], n_eval: int, n_specs: int, n_coins: int) -> None:
    token, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    lines = [f"🧠 <b>Scoperta strategie</b>: {n_specs} candidate × {n_coins} crypto "
             f"= {n_eval} valutazioni"]
    if passed:
        lines.append(f"✅ {len(passed)} coppie nuove passate (OOS, netto costi):")
        for p in sorted(passed, key=lambda x: x["pnl"], reverse=True)[:10]:
            lines.append(f"• {p['symbol']} <code>{p['id']}</code> "
                         f"pf={p['pf']} pnl={p['pnl']*100:+.0f}% — {p['desc']}")
    else:
        lines.append("Nessuna candidata ha passato in questo run (normale: il gate è severo).")
    text = "\n".join(lines)
    if not (token and chat):
        print("[discover] (telegram non configurato)\n" + text)
        return
    try:
        import requests
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      json={"chat_id": chat, "text": text, "parse_mode": "HTML"}, timeout=8)
    except Exception as exc:  # noqa: BLE001
        print(f"[discover] telegram fallito: {exc}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Scoperta autonoma di nuove strategie.")
    ap.add_argument("--top", type=int, default=25, help="numero di crypto su cui validare")
    ap.add_argument("--generate", type=int, default=40, help="strategie candidate da generare")
    ap.add_argument("--windows", type=int, default=3)
    ap.add_argument("--seed", type=int, default=int(time.time()) % 100000,
                    help="seed generazione (varia per esplorare strategie diverse a ogni run)")
    ap.add_argument("--interval", default="1h")
    ap.add_argument("--start", default="2024-01-01")
    ap.add_argument("--end", default=None,
                    help="fine finestra dati (default: oggi). Far avanzare la finestra "
                         "rende la ri-validazione VERA su dati nuovi a ogni run.")
    ap.add_argument("--source", default="auto")
    ap.add_argument("--reeval-cap", type=int, default=80,
                    help="max strategie già scoperte da ri-validare per run (bound sui tempi)")
    args = ap.parse_args()
    end = args.end or date.today().isoformat()

    fb = get_firebase()
    opt = WalkForwardOptimizer(n_windows=args.windows)

    # 1) candidate NUOVE  2) RI-VALUTA le scoperte precedenti (così accumulano i
    # pass e diventano operabili)  3) mutazioni per evolvere attorno alle vincenti.
    specs = generate_specs(args.generate, seed=args.seed)
    existing = (fb.get_doc("discovered_strategies", "specs") or {}).get("specs", {}) or {}
    existing_list = list(existing.values())[: args.reeval_cap]
    specs.extend(existing_list)
    for i, base in enumerate(existing_list[:10]):
        specs.append(mutate(base, seed=args.seed + i + 1))
    # de-dup per id
    specs = list({s["id"]: s for s in specs}.values())
    print(f"[discover] {len(specs)} candidate ({len(existing_list)} ri-validate) "
          f"seed={args.seed} finestra {args.start}->{end}")

    symbols = top_symbols_by_volume(args.top)
    min_history = int(os.getenv("OPTIMIZER_MIN_HISTORY", "2500"))
    out: dict[str, dict] = {}
    passed_summary: list[dict] = []
    passed_keys: list[str] = []
    specs_to_save: dict = {}
    n_eval = 0

    for sym in symbols:
        candles = load_candles(sym, args.interval, args.start, end, prefer=args.source)
        if len(candles) < min_history:
            print(f"[discover] {sym}: storia insufficiente, salto")
            continue
        frame = compute_indicator_frame(candles)
        print(f"\n[discover] === {sym} ===")
        for spec in specs:
            r = evaluate_spec(opt, sym, candles, frame, spec)
            n_eval += 1
            key = f"{sym}|{spec['id']}"
            out[key] = {
                "symbol": sym, "strategy": spec["id"], "params": {}, "spec": spec,
                "oos_pf": r["pf"], "oos_pnl_pct": r["pnl"],
                "oos_trades": r["trades"], "oos_win_rate": r["win"], "passed": r["passed"],
            }
            if r["passed"]:
                flag = "✅"
                passed_keys.append(key)
                specs_to_save[spec["id"]] = spec
                gs = GeneratedStrategy(spec)
                passed_summary.append({"symbol": sym, "id": spec["id"], "pf": r["pf"],
                                       "pnl": r["pnl"], "desc": gs.description})
                print(f"  {flag} {spec['id']} pf={r['pf']} pnl={r['pnl']*100:+.1f}% "
                      f"trades={r['trades']}  {gs.description}")

    # persisti: spec scoperte + merge nel registro validato
    if specs_to_save:
        persist_specs(fb, specs_to_save)
    validated = merge_into_registry(fb, out, passed_keys)
    # riepilogo COMPATTO (niente spec/entry per ogni coppia: sforerebbe il limite
    # di 1 MiB di Firestore). Le spec complete stanno in discovered_strategies/specs.
    fb.set_doc("strategy_params", "discovered_last_run", {
        "updated_at": time.time(),
        "n_eval": n_eval,
        "n_passed": len(passed_keys),
        "passed": [{"symbol": out[k]["symbol"], "id": out[k]["strategy"],
                    "pf": out[k]["oos_pf"], "pnl": out[k]["oos_pnl_pct"]}
                   for k in passed_keys],
    })

    print("\n" + "=" * 60)
    print(f"[discover] {n_eval} valutazioni, {len(passed_keys)} coppie nuove passate in QUESTO run.")
    print(f"[discover] coppie validate totali nel registro (base+generate): {len(validated)}")
    print("=" * 60)
    _notify(passed_summary, n_eval, len(specs), len(symbols))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
