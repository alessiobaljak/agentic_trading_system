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
from backtesting.engine import (StrategyStats, gate_verdict, max_drawdown, pf_by_regime,
                                pf_without_top, t_stat)
from backtesting.optimizer import WalkForwardOptimizer
from backtesting.parallel import n_workers, parallel_map
from bot.config import settings
from bot.core.firebase_client import decode_pairs, encode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.strategies.generated import GeneratedStrategy
from bot.ai.hypotheses import propose as ai_propose
from bot.ai.universe_filter import filter_universe as ai_filter_universe
from bot.strategies.generator import generate_specs, mutate
from scripts.optimize import (FRESH_DAYS, MIN_PASSES, NEW_DATA_MIN_S, _min_history,
                              drifted_from_paper, top_symbols_by_volume)

# stato pesante per-worker (optimizer + specs + parametri), costruito una volta per
# processo dall'initializer. Vedi _disc_init / _disc_one (parallelizzazione discovery).
_W: dict = {}


def mutation_seeds(fb, existing: dict, limit: int = 10) -> list[dict]:
    """Le spec da cui vale la pena evolvere: i QUASI-PASSAGGI del run precedente.

    Una candidata fermata da UN SOLO criterio e per poco e' l'informazione piu'
    preziosa che un run produce: dice che in quella zona dello spazio delle
    strategie c'e' qualcosa, e che manca poco. Mutare li' e' una ricerca guidata;
    generare candidate a caso e' ricominciare da zero a ogni giro, che e' esattamente
    cio' che il sistema faceva.

    Fail-open in ogni punto: nessuna autopsia, autopsia illeggibile o quasi-passaggi
    su strategie BASE (che non sono spec mutabili) -> lista vuota, e il chiamante
    torna al comportamento precedente.
    """
    near: list = []
    try:
        # PRIMA l'autopsia della discovery: e' l'unica che contiene spec generate,
        # cioe' le uniche mutabili. Quella dell'optimizer parla di strategie BASE,
        # che non sono spec — leggerla da sola darebbe sempre lista vuota.
        for doc_id in ("discover", "current"):
            near.extend(((fb.get_doc("gate_autopsy", doc_id) or {})
                         .get("near_misses") or []))
    except Exception:  # noqa: BLE001
        return []
    out: list[dict] = []
    for n in near:
        key = str(n.get("key", ""))
        if "|" not in key:
            continue
        gid = key.split("|", 1)[1]
        spec = existing.get(gid)
        if spec is not None and spec not in out:
            out.append(spec)
        if len(out) >= limit:
            break
    return out


def _publish_discover_autopsy(fb, evaluated: int, passed: int, binding: dict,
                              involved: dict, near: list, top_near: int = 40) -> dict:
    """Scrive l'autopsia della discovery, che e' dove sta il grosso del volume:
    l'optimizer valuta ~1500 coppie per run, la discovery oltre ventimila.

    Documento SEPARATO da quello dell'optimizer: sono due imbuti diversi (strategie
    classiche con grid search contro spec generate senza train) e mediarli
    nasconderebbe proprio la differenza che interessa. Best-effort: una diagnosi
    non salvata non deve far fallire un run di validazione.
    """
    near = sorted(near, key=lambda n: -(n.get("shortfall") or -9))[:top_near]
    rep = {"updated_at": time.time(), "evaluated": evaluated, "passed": passed,
           "diagnosed": int(sum(binding.values())),
           "binding": dict(sorted(binding.items(), key=lambda kv: -kv[1])),
           "involved": dict(sorted(involved.items(), key=lambda kv: -kv[1])),
           "near_misses": near, "near_miss_count": len(near)}
    try:
        fb.set_doc("gate_autopsy", "discover", rep)
    except Exception as exc:  # noqa: BLE001
        print(f"[autopsy] non salvata ({exc})")
    if rep["diagnosed"]:
        top = " · ".join(f"{k} {v}" for k, v in list(rep["binding"].items())[:5])
        print(f"[autopsy] {passed}/{evaluated} passate · muoiono su: {top}")
        print(f"[autopsy] quasi-passaggi (semi per le mutazioni del prossimo run): "
              f"{len(near)}")
    return rep


def _disc_init(args, end: str, specs: list) -> None:
    _W.update(opt=WalkForwardOptimizer(n_windows=args.windows, interval=args.interval),
              args=args, end=end, specs=specs, min_history=_min_history(args.interval))


def _disc_one(sym: str) -> tuple[str, dict, list, dict, int, list, dict]:
    """Valuta TUTTE le spec su un simbolo (nei worker).
    Ritorna (sym, passed_entries, passed_keys, specs_passed, n_eval, summary, diag).

    `diag` e' l'autopsia LOCALE: conteggi dei criteri che hanno fermato le spec e
    i pochi quasi-passaggi. Si aggregano numeri, non le migliaia di valutazioni
    bocciate — la diagnosi deve costare quanto un contatore, altrimenti non
    verrebbe fatta."""
    args, end, specs = _W["args"], _W["end"], _W["specs"]
    candles = load_candles(sym, args.interval, args.start, end, prefer=args.source)
    if len(candles) < _W["min_history"]:
        return (sym, {}, [], {}, 0, [], {})
    # coin DELISTATA: storia a sufficienza ma serie ferma a mesi fa. Vedi la nota
    # gemella in scripts/optimize.py: validare su un mercato che non esiste piu'.
    from backtesting.quality import looks_delisted
    from bot.config import timeframe_hours as _tfh
    if looks_delisted(candles, end, _tfh(args.interval)):
        print(f"[discover] {sym}: serie ferma al "
              f"{candles[-1].open_time:%Y-%m-%d} -> coin delistata, saltata")
        return (sym, {}, [], {}, 0, [], {})
    frame = compute_indicator_frame(candles)
    entries: dict = {}
    passed_keys: list = []
    specs_passed: dict = {}
    summary: list = []
    binding: dict = {}
    involved: dict = {}
    near: list = []
    n_eval = 0
    for spec in specs:
        r = evaluate_spec(_W["opt"], sym, candles, frame, spec)
        n_eval += 1
        if not r["passed"] and r.get("fail_criteria"):
            b = r.get("fail_binding") or "?"
            binding[b] = binding.get(b, 0) + 1
            for c in r["fail_criteria"]:
                involved[c] = involved.get(c, 0) + 1
            if r.get("near_miss"):
                near.append({"key": f"{sym}|{spec['id']}", "binding": b,
                             "shortfall": r.get("fail_shortfall"),
                             "pf": r["pf"], "trades": r["trades"],
                             "t_stat": r.get("t_stat")})
        if r["passed"]:
            key = f"{sym}|{spec['id']}"
            entries[key] = {
                "symbol": sym, "strategy": spec["id"], "params": {}, "spec": spec,
                "oos_pf": r["pf"], "oos_pnl_pct": r["pnl"],
                "oos_trades": r["trades"], "oos_win_rate": r["win"], "passed": True,
                # SENZA questi campi il registro perde: il pass onesto (data_end
                # assente faceva incrementare a OGNI run - il bug delle coppie a
                # 3 pass in un giorno), il veto di regime e la scala per-coppia.
                "holdout": r.get("holdout"), "regime_pf": r.get("regime_pf"),
                "oos_max_dd": r.get("max_dd"), "scale_r_mults": r.get("scale_r_mults"),
                "data_end": r.get("data_end", 0),
            }
            passed_keys.append(key)
            specs_passed[spec["id"]] = spec
            summary.append({"symbol": sym, "id": spec["id"], "pf": r["pf"],
                            "pnl": r["pnl"], "desc": GeneratedStrategy(spec).description})
    near.sort(key=lambda n: -(n.get("shortfall") or -9))
    return (sym, entries, passed_keys, specs_passed, n_eval, summary,
            {"binding": binding, "involved": involved, "near": near[:10]})


def evaluate_spec(opt: WalkForwardOptimizer, symbol: str, candles, frame, spec: dict):
    """Aggrega le performance del spec sulle SOLE finestre out-of-sample e applica
    il GATE 1 (PF, win-rate, ritorno minimo, consistenza per finestra).

    Le finestre sono calcolate sul CORPO (holdout escluso): le spec generate non
    hanno train, quindi qui l'OOS era l'unica difesa — e veniva riusato identico a
    ogni run da migliaia di candidate (la lotteria). L'holdout finale, mai visto
    dalla selezione, e' la verifica che mancava."""
    body, cut = opt.split_holdout(candles)

    def _run_oos(ladder=None) -> tuple:
        """(stats OOS, ritorni per finestra) con una scala di TP data."""
        st_all = StrategyStats(strategy=spec["id"])
        per_window: list[float] = []
        for (_ta, _tb, sa, sb) in opt._windows(len(body)):
            g = GeneratedStrategy(spec)
            if ladder:
                g.params = {**(getattr(g, "params", {}) or {}), "scale_r_mults": list(ladder)}
            st = opt.bt.run_strategy(g, symbol, body[sa:sb],
                                     frame=frame.iloc[sa:sb].reset_index(drop=True))
            st_all.trades.extend(st.trades)
            # consistenza: solo le finestre con trade (una finestra senza segnali non
            # e' una perdita -> non deve far fallire il gate).
            if st.trades:
                per_window.append(sum(t.pnl_pct for t in st.trades))
        return st_all, per_window

    # 1) PRESELEZIONE con la scala globale: serve solo a scartare in fretta le spec
    #    senza speranza, prima di spendere 4 backtest per la scelta della scala.
    oos, window_pnls = _run_oos()
    verdict = gate_verdict(window_pnls, len(oos.trades), oos.profit_factor(),
                           oos.win_rate(), oos.total_pnl_pct(),
                           max_dd=max_drawdown(oos.trades),
                           regime_pf=pf_by_regime(oos.trades),
                           pf_ex_top=pf_without_top(oos.trades))
    passed = verdict.ok

    # 2) SCALA DI TP PER-COPPIA anche per le GENERATE. Le classiche la scelgono nella
    #    grid search; le generate non hanno grid -> senza questo passo restavano per
    #    sempre sulla scala globale (e sono la maggioranza del registro).
    best_ladder = None
    if passed and settings.SCALE_OUT_ENABLED:
        from bot.execution.exit_logic import SCALE_LADDER_CANDIDATES
        best_metric = None
        for cand in SCALE_LADDER_CANDIDATES:
            st_c, _ = _run_oos(cand)
            metric = st_c.total_pnl_pct() - max_drawdown(st_c.trades)
            if best_metric is None or metric > best_metric:
                best_metric, best_ladder = metric, list(cand)

    # 3) METRICHE FINALI CON LA SCALA CHE VERRA' ESEGUITA. Prima i numeri spediti nel
    #    registro (last_pf, win, regime_pf) uscivano dal passo 1, cioe' dalla scala
    #    GLOBALE, mentre il bot operava la scala scelta al passo 2: per 95 coppie su
    #    184 erano due configurazioni diverse. Il registro pubblicizzava un PF che
    #    nessuno eseguiva, e il rilevatore di deriva confrontava il vissuto contro
    #    quel numero sbagliato.
    if best_ladder and list(best_ladder) != list(settings.SCALE_OUT_R_MULTIPLES):
        oos, window_pnls = _run_oos(best_ladder)
    pf = oos.profit_factor()
    pnl = oos.total_pnl_pct()
    reg_pf = pf_by_regime(oos.trades)
    # il verdetto si rifa' sulla configurazione vera: una scala scelta per il
    # (ritorno - drawdown) puo' comunque non superare gli altri criteri.
    if passed:
        verdict = gate_verdict(window_pnls, len(oos.trades), pf, oos.win_rate(), pnl,
                               max_dd=max_drawdown(oos.trades), regime_pf=reg_pf,
                               pf_ex_top=pf_without_top(oos.trades))
        passed = verdict.ok
    failed, binding = list(verdict.failed), verdict.binding
    shortfall, near = verdict.shortfall, verdict.near_miss()

    hold: dict = {}
    if passed and opt.holdout_bars > 0:
        g = GeneratedStrategy(spec)
        if best_ladder:
            g.params = {**(getattr(g, "params", {}) or {}), "scale_r_mults": best_ladder}
        hold = opt._holdout_check(g, symbol, candles, frame, cut)
        passed = bool(hold.get("ok"))
        if not passed:
            # supera tutto e cade sui dati mai visti: l'esito piu' informativo
            failed, binding, shortfall, near = ["holdout"], "holdout", 0.0, True
    return {
        "pf": round(pf, 3), "pnl": round(pnl, 4),
        "trades": len(oos.trades), "win": round(oos.win_rate(), 3), "passed": passed,
        "holdout": hold, "regime_pf": reg_pf,
        "max_dd": round(max_drawdown(oos.trades), 4),
        "scale_r_mults": best_ladder,
        "data_end": (candles[-1].open_time.timestamp() if candles else 0.0),
        "fail_criteria": failed, "fail_binding": binding,
        "fail_shortfall": shortfall, "near_miss": bool(near and not passed),
        # MISURATO, non usato per decidere: vedi t_stat in backtesting/engine.py
        "t_stat": round(t_stat(oos.trades), 3),
    }


def merge_into_registry(fb, out: dict, passed_now: list[str]) -> list[str]:
    """Aggiunge SOLO le coppie generate che PASSANO (accumula pass_count) e pota
    quelle generate inutili/stantie, evitando crescita illimitata del documento.
    Ricalcola la lista validated PRESERVANDO i campi di copertura del GATE 1
    (universe/coverage/ready) che spettano a optimize.py."""
    doc = fb.get_doc("strategy_registry", "validated") or {}
    pairs = decode_pairs(doc.get("pairs"))
    now = time.time()
    drifted = drifted_from_paper(fb)   # evidenza dal paper: vale come fallimento
    # 1) upsert SOLO delle coppie passate (non sporco il registro con i fallimenti)
    for key in passed_now:
        e = out[key]
        rec = pairs.get(key, {"pass_count": 0})
        if key in drifted:      # smentita dal vivo -> nessun pass, conta come fallimento
            rec["fail_count"] = rec.get("fail_count", 0) + 1
            rec["drift_seen_at"] = now
            rec["symbol"], rec["strategy"] = e["symbol"], e["strategy"]
            rec["generated"] = True
            rec["last_seen_at"] = now
            pairs[key] = rec
            continue
        # PASS ONESTO (stessa regola di optimize): conta solo con dati nuovi
        data_end = float(e.get("data_end", 0) or 0)
        prev_end = float(rec.get("last_pass_data_end", 0) or 0)
        # FAIL-CLOSED: senza data_end il pass NON conta. Il fallback aperto era il
        # buco da cui i run sharded (entries senza data_end) gonfiavano il conteggio.
        if data_end > 0 and (prev_end <= 0 or data_end - prev_end >= NEW_DATA_MIN_S):
            rec["pass_count"] = rec.get("pass_count", 0) + 1
            rec["last_pass_data_end"] = data_end
        if e.get("holdout"):
            rec["holdout"] = e["holdout"]
        if e.get("regime_pf"):
            rec["regime_pf"] = e["regime_pf"]
        # NB: last_params si assegna PRIMA, poi si innesta la scala. Invertendo,
        # l'assegnazione cancellerebbe la scala appena salvata.
        rec["last_params"] = dict(e["params"] or {})
        # scala validata per questa coppia generata: viaggia in last_params, cosi'
        # params_for -> open_position la consegna al live come per le classiche
        if e.get("scale_r_mults"):
            rec["last_params"]["scale_r_mults"] = e["scale_r_mults"]
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
    # cap: limita il numero di coppie per non superare 1 MiB di documento.
    # SOLO sulle GENERATE: le coppie base sono il prodotto di optimize.py e la
    # discovery non deve MAI potarle (con --top alto le base da sole superano il
    # cap e perderebbero pass/fail_count silenziosamente).
    max_pairs = int(os.getenv("OPTIMIZER_MAX_PAIRS", "3000"))
    if len(pairs) > max_pairs:
        base = {k: r for k, r in pairs.items() if not r.get("generated")}
        gen = {k: r for k, r in pairs.items() if r.get("generated")}
        gen_budget = max(0, max_pairs - len(base))
        if len(gen) > gen_budget:
            ranked = sorted(
                gen.items(),
                key=lambda kv: (kv[1].get("pass_count", 0) >= MIN_PASSES,
                                kv[1].get("pass_count", 0), kv[1].get("last_seen_at", 0)),
                reverse=True)
            gen = dict(ranked[:gen_budget])
        pairs = {**base, **gen}
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
    specs = decode_pairs(doc.get("specs"))     # dict annidato -> stringa JSON (limite 40k indici)
    specs.update(specs_by_id)
    fb.set_doc("discovered_strategies", "specs",
               {"specs": encode_pairs(specs), "updated_at": time.time()})


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
        combined_out.update(decode_pairs(d.get("passed_entries")))
        passed_keys.extend(decode_pairs(d.get("passed_keys")) or [])
        combined_specs.update(decode_pairs(d.get("specs")))
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
    ap.add_argument("--symbols", default="",
                    help="lista esplicita di coin (CSV). Ha precedenza su --top: "
                         "serve alle conferme mirate su coppie gia' candidate")
    ap.add_argument("--generate", type=int, default=40, help="strategie candidate da generare")
    ap.add_argument("--windows", type=int, default=3)
    ap.add_argument("--seed", type=int, default=int(time.time()) % 100000,
                    help="seed generazione (varia per esplorare strategie diverse a ogni run)")
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
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
    # 1a) IPOTESI AI: poche spec con un meccanismo dichiarato, al posto di altrettante
    #     estrazioni casuali. Non e' un'aggiunta all'imbuto: SOSTITUISCE una quota di
    #     candidate casuali, perche' ogni candidata in piu' e' un'estrazione in piu'
    #     della lotteria del confronto multiplo. Senza AI la quota resta casuale e il
    #     comportamento e' identico a prima.
    ai_specs = ai_propose(min(settings.AI_HYPOTHESES_PER_RUN, args.generate),
                          market_context=f"Timeframe operativo: {args.interval}. "
                                         f"Universo: crypto futures USDT-M su Binance.")
    if ai_specs:
        print(f"[discover] {len(ai_specs)} ipotesi AI (motivate) + "
              f"{args.generate - len(ai_specs)} casuali")
    specs = ai_specs + generate_specs(max(0, args.generate - len(ai_specs)), seed=args.seed)
    existing = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
    # PRIORITÀ: ri-valida SEMPRE le generate GIÀ VALIDATE (in ogni shard), così non
    # scadono per freshness e non vengono "cancellate" dal registro. Poi riempi col
    # resto fino al cap.
    reg = fb.get_doc("strategy_registry", "validated") or {}
    validated_gen = {k.split("|", 1)[1] for k in (reg.get("validated") or []) if "|gen_" in k}
    priority = [existing[g] for g in validated_gen if g in existing]
    rest = [s for gid, s in existing.items() if gid not in validated_gen]
    existing_list = priority + rest[: max(0, args.reeval_cap - len(priority))]
    specs.extend(existing_list)
    # MUTAZIONE INFORMATA: si evolve attorno ai QUASI-PASSAGGI del run precedente
    # (una sola condizione mancata, e per poco), non attorno alle prime dieci spec
    # che capitano. E' la differenza fra cercare dove l'ultimo tentativo si e'
    # avvicinato e ricominciare da capo ogni volta. Fail-open: senza autopsia si
    # mutano le prime, come prima.
    seeds = mutation_seeds(fb, existing)
    if seeds:
        print(f"[discover] {len(seeds)} semi dai quasi-passaggi del run precedente")
    bases = seeds or existing_list[:10]
    for i, base in enumerate(bases[:10]):
        specs.append(mutate(base, seed=args.seed + i + 1))
    # de-dup per id
    specs = list({s["id"]: s for s in specs}.values())
    print(f"[discover] {len(specs)} candidate ({len(priority)} validate ri-validate + "
          f"{len(existing_list) - len(priority)} altre) seed={args.seed} {args.start}->{end}")

    # UNIVERSO RISTRETTO (--symbols): serve alle conferme mirate. Quando si sa gia'
    # quali coppie possono ancora arrivare a MIN_PASSES, ri-testare l'intero mercato
    # e' tempo speso su coppie che non potrebbero comunque validarsi.
    if getattr(args, "symbols", ""):
        full_symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
        print(f"[discover] universo RISTRETTO a {len(full_symbols)} coin (--symbols)")
    else:
        full_symbols = top_symbols_by_volume(args.top)
    # FILTRO DI CONTESTO: toglie dall'imbuto le coin su cui una validazione non
    # sarebbe informativa (storia dentro la sola fase di listing, illiquide,
    # prezzo guidato da eventi discreti). Fail-open: senza AI non toglie nulla.
    full_symbols, _excluded = ai_filter_universe(
        [{"symbol": s} for s in full_symbols])
    for _sym, _why in list(_excluded.items())[:10]:
        print(f"[discover]   escluso {_sym}: {_why}")
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
    diag_binding: dict = {}
    diag_involved: dict = {}
    diag_near: list = []
    for sym, entries, p_keys, p_specs, n_ev, summary, diag in parallel_map(
        _disc_one, symbols, workers=workers, initializer=_disc_init, initargs=(args, end, specs)
    ):
        n_eval += n_ev
        out.update(entries)
        passed_keys.extend(p_keys)
        specs_to_save.update(p_specs)
        passed_summary.extend(summary)
        for k, v in (diag.get("binding") or {}).items():
            diag_binding[k] = diag_binding.get(k, 0) + v
        for k, v in (diag.get("involved") or {}).items():
            diag_involved[k] = diag_involved.get(k, 0) + v
        diag_near.extend(diag.get("near") or [])
        if p_keys:
            print(f"[discover] {sym}: {len(p_keys)} coppie passate ✅")

    # Con gli shard ognuno vede una fetta dell'universo e sovrascriverebbe la
    # diagnosi degli altri: meglio nessuna autopsia che una parziale spacciata per
    # intera. Sulla VPS (non shardata) si pubblica sempre.
    if args.num_shards <= 1:
        _publish_discover_autopsy(fb, n_eval, len(passed_keys),
                                  diag_binding, diag_involved, diag_near)

    # SHARD: scrive il proprio risultato; il merge riunisce e aggiorna il registro.
    if args.num_shards > 1:
        fb.set_doc("discover_shards", str(args.shard), {
            "run_id": os.getenv("GITHUB_RUN_ID", ""),
            "passed_entries": encode_pairs({k: out[k] for k in passed_keys}),
            "passed_keys": encode_pairs(passed_keys),
            "specs": encode_pairs(specs_to_save),
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
