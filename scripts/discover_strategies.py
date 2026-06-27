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
from backtesting.engine import StrategyStats, passes_gate
from backtesting.optimizer import WalkForwardOptimizer
from backtesting.parallel import n_workers, parallel_map
from bot.core.firebase_client import decode_pairs, encode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.strategies.generated import GeneratedStrategy
from bot.strategies.generator import generate_specs, mutate
from scripts.optimize import FRESH_DAYS, MIN_PASSES, top_symbols_by_volume

# stato pesante per-worker (optimizer + specs + parametri), costruito una volta per
# processo dall'initializer. Vedi _disc_init / _disc_one (parallelizzazione discovery).
_W: dict = {}


def _disc_init(args, end: str, specs: list) -> None:
    _W.update(opt=WalkForwardOptimizer(n_windows=args.windows), args=args, end=end,
              specs=specs, min_history=int(os.getenv("OPTIMIZER_MIN_HISTORY", "2500")))


def _disc_one(sym: str) -> tuple[str, dict, list, dict, int, list]:
    """Valuta TUTTE le spec su un simbolo (nei worker).
    Ritorna (sym, passed_entries, passed_keys, specs_passed, n_eval, summary)."""
    args, end, specs = _W["args"], _W["end"], _W["specs"]
    candles = load_candles(sym, args.interval, args.start, end, prefer=args.source)
    if len(candles) < _W["min_history"]:
        return (sym, {}, [], {}, 0, [])
    frame = compute_indicator_frame(candles)
    entries: dict = {}
    passed_keys: list = []
    specs_passed: dict = {}
    summary: list = []
    n_eval = 0
    for spec in specs:
        r = evaluate_spec(_W["opt"], sym, candles, frame, spec)
        n_eval += 1
        if r["passed"]:
            key = f"{sym}|{spec['id']}"
            entries[key] = {
                "symbol": sym, "strategy": spec["id"], "params": {}, "spec": spec,
                "oos_pf": r["pf"], "oos_pnl_pct": r["pnl"],
                "oos_trades": r["trades"], "oos_win_rate": r["win"], "passed": True,
            }
            passed_keys.append(key)
            specs_passed[spec["id"]] = spec
            summary.append({"symbol": sym, "id": spec["id"], "pf": r["pf"],
                            "pnl": r["pnl"], "desc": GeneratedStrategy(spec).description})
    return (sym, entries, passed_keys, specs_passed, n_eval, summary)


def evaluate_spec(opt: WalkForwardOptimizer, symbol: str, candles, frame, spec: dict):
    """Aggrega le performance del spec sulle SOLE finestre out-of-sample e applica
    il GATE 1 (PF, win-rate, ritorno minimo, consistenza per finestra)."""
    oos = StrategyStats(strategy=spec["id"])
    window_pnls: list[float] = []   # ritorno OOS per finestra (consistenza)
    for (_ta, _tb, sa, sb) in opt._windows(len(candles)):
        test_c = candles[sa:sb]
        test_f = frame.iloc[sa:sb].reset_index(drop=True)
        st = opt.bt.run_strategy(GeneratedStrategy(spec), symbol, test_c, frame=test_f)
        oos.trades.extend(st.trades)
        # consistenza: solo le finestre con trade (una finestra senza segnali non e'
        # una perdita -> non deve far fallire il gate).
        if st.trades:
            window_pnls.append(sum(t.pnl_pct for t in st.trades))
    pf = oos.profit_factor()
    pnl = oos.total_pnl_pct()
    passed = passes_gate(window_pnls, len(oos.trades), pf, oos.win_rate(), pnl)
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
    pairs = decode_pairs(doc.get("pairs"))
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
        rec["last_win_rate"] = e.get("oos_win_rate")
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
    # cap: limita il numero di coppie per non superare 1 MiB di documento. Tiene
    # le validate (>=3 pass) e le piu' promettenti (pass alto, viste di recente).
    max_pairs = int(os.getenv("OPTIMIZER_MAX_PAIRS", "3000"))
    if len(pairs) > max_pairs:
        ranked = sorted(
            pairs.items(),
            key=lambda kv: (kv[1].get("pass_count", 0) >= MIN_PASSES,
                            kv[1].get("pass_count", 0), kv[1].get("last_seen_at", 0)),
            reverse=True)
        pairs = dict(ranked[:max_pairs])
    validated = sorted(
        k for k, r in pairs.items()
        if r.get("pass_count", 0) >= MIN_PASSES
        and (now - r.get("last_seen_at", 0)) < FRESH_DAYS * 86400
    )
    # tiene COPERTURA/coins coerenti col nuovo set validato (incluse le generate),
    # cosi' Telegram e dashboard mostrano gli stessi numeri. Il denominatore
    # (universe_size) resta quello di optimize.
    validated_coins = sorted({pairs[k].get("symbol") or k.split("|", 1)[0] for k in validated})
    universe = max(doc.get("universe_size", 0) or 0, len(validated_coins)) or 1
    doc["pairs"] = encode_pairs(pairs)
    doc["validated"] = validated
    doc["coins_covered"] = len(validated_coins)
    doc["coins"] = validated_coins
    doc["universe_size"] = universe
    doc["coverage"] = round(len(validated_coins) / universe, 3)
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


def _merge_discover_shards(fb, args) -> int:
    """Riunisce gli shard di discovery e aggiorna il registro UNA volta sola."""
    run_id = os.getenv("GITHUB_RUN_ID", "")
    combined_out: dict = {}
    passed_keys: list[str] = []
    combined_specs: dict = {}
    n_eval = 0
    used = 0
    for i in range(args.num_shards):
        d = fb.get_doc("discover_shards", str(i)) or {}
        if not d:
            print(f"[merge] shard {i}: assente, salto")
            continue
        if run_id and d.get("run_id") and d.get("run_id") != run_id:
            print(f"[merge] shard {i}: run_id diverso (stantio), salto")
            continue
        combined_out.update(d.get("passed_entries", {}) or {})
        passed_keys.extend(d.get("passed_keys", []) or [])
        combined_specs.update(d.get("specs", {}) or {})
        n_eval += int(d.get("n_eval", 0) or 0)
        used += 1
    print(f"[merge] {used}/{args.num_shards} shard uniti: {len(passed_keys)} coppie passate")
    if combined_specs:
        persist_specs(fb, combined_specs)
    validated = merge_into_registry(fb, combined_out, passed_keys)
    summary = [{"symbol": e["symbol"], "id": e["strategy"], "pf": e["oos_pf"],
                "pnl": e["oos_pnl_pct"], "desc": GeneratedStrategy(e["spec"]).description}
               for e in combined_out.values()]
    fb.set_doc("strategy_params", "discovered_last_run", {
        "updated_at": time.time(), "n_eval": n_eval, "n_passed": len(passed_keys),
        "passed": [{"symbol": s["symbol"], "id": s["id"], "pf": s["pf"], "pnl": s["pnl"]}
                   for s in summary],
    })
    print(f"[merge] coppie validate totali nel registro (base+generate): {len(validated)}")
    _notify(summary, n_eval, len(combined_specs), args.num_shards)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Scoperta autonoma di nuove strategie.")
    ap.add_argument("--top", type=int, default=25, help="numero di crypto su cui validare")
    ap.add_argument("--generate", type=int, default=40, help="strategie candidate da generare")
    ap.add_argument("--windows", type=int, default=3)
    ap.add_argument("--seed", type=int, default=int(time.time()) % 100000,
                    help="seed generazione (varia per esplorare strategie diverse a ogni run)")
    ap.add_argument("--interval", default="1h")
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--end", default=None,
                    help="fine finestra dati (default: oggi). Far avanzare la finestra "
                         "rende la ri-validazione VERA su dati nuovi a ogni run.")
    ap.add_argument("--source", default="auto")
    ap.add_argument("--reeval-cap", type=int, default=80,
                    help="max strategie già scoperte da ri-validare per run (bound sui tempi)")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--num-shards", type=int, default=1)
    ap.add_argument("--merge", action="store_true",
                    help="modalita' MERGE: riunisce gli shard di discovery nel registro")
    args = ap.parse_args()
    end = args.end or date.today().isoformat()

    fb = get_firebase()
    if args.merge:
        return _merge_discover_shards(fb, args)

    # 1) candidate NUOVE  2) RI-VALUTA le scoperte precedenti (così accumulano i
    # pass e diventano operabili)  3) mutazioni per evolvere attorno alle vincenti.
    specs = generate_specs(args.generate, seed=args.seed)
    existing = (fb.get_doc("discovered_strategies", "specs") or {}).get("specs", {}) or {}
    # PRIORITÀ: ri-valida SEMPRE le generate GIÀ VALIDATE (in ogni shard), così non
    # scadono per freshness e non vengono "cancellate" dal registro. Poi riempi col
    # resto fino al cap.
    reg = fb.get_doc("strategy_registry", "validated") or {}
    validated_gen = {k.split("|", 1)[1] for k in (reg.get("validated") or []) if "|gen_" in k}
    priority = [existing[g] for g in validated_gen if g in existing]
    rest = [s for gid, s in existing.items() if gid not in validated_gen]
    existing_list = priority + rest[: max(0, args.reeval_cap - len(priority))]
    specs.extend(existing_list)
    for i, base in enumerate(existing_list[:10]):
        specs.append(mutate(base, seed=args.seed + i + 1))
    # de-dup per id
    specs = list({s["id"]: s for s in specs}.values())
    print(f"[discover] {len(specs)} candidate ({len(priority)} validate ri-validate + "
          f"{len(existing_list) - len(priority)} altre) seed={args.seed} {args.start}->{end}")

    full_symbols = top_symbols_by_volume(args.top)
    # SHARDING: ogni shard valida le candidate su una fetta dell'universo; il merge
    # riunisce. Così copriamo l'INTERO universo restando nel timeout.
    symbols = full_symbols[args.shard::args.num_shards] if args.num_shards > 1 else full_symbols
    print(f"[discover] shard {args.shard}/{args.num_shards}: {len(symbols)}/{len(full_symbols)} coin")
    out: dict[str, dict] = {}
    passed_summary: list[dict] = []
    passed_keys: list[str] = []
    specs_to_save: dict = {}
    n_eval = 0

    # PARALLELO: ogni simbolo valuta tutte le spec, indipendente dagli altri ->
    # distribuito su tutti i core del runner. Fallback sequenziale se BACKTEST_WORKERS=1.
    workers = n_workers()
    print(f"[discover] {len(symbols)} coin x {len(specs)} spec su {workers} worker (core)")
    for sym, entries, p_keys, p_specs, n_ev, summary in parallel_map(
        _disc_one, symbols, workers=workers, initializer=_disc_init, initargs=(args, end, specs)
    ):
        n_eval += n_ev
        out.update(entries)
        passed_keys.extend(p_keys)
        specs_to_save.update(p_specs)
        passed_summary.extend(summary)
        if p_keys:
            print(f"[discover] {sym}: {len(p_keys)} coppie passate ✅")

    # SHARD: scrive il proprio risultato; il merge riunisce e aggiorna il registro.
    if args.num_shards > 1:
        fb.set_doc("discover_shards", str(args.shard), {
            "run_id": os.getenv("GITHUB_RUN_ID", ""),
            "passed_entries": {k: out[k] for k in passed_keys},
            "passed_keys": passed_keys, "specs": specs_to_save,
            "n_eval": n_eval, "updated_at": time.time(),
        })
        print(f"[discover] shard {args.shard} scritto: {len(passed_keys)} coppie passate. "
              f"Il merge aggiornera' il registro.")
        return 0

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
