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
from bot.execution.exit_logic import SCALE_LADDER_CANDIDATES, ladder_from_mfe
from bot.ai.universe_filter import filter_universe as ai_filter_universe
from bot.strategies.generator import generate_specs, mutate
from scripts.optimize import (FRESH_DAYS, MIN_PASSES, _min_history,
                              coin_in_maturazione, drifted_from_paper, judge_window,
                              publish_timeline, conferme_da_proteggere, scrivi_registro,
                              slim_registry, top_symbols_by_volume)

# stato pesante per-worker (optimizer + specs + parametri), costruito una volta per
# processo dall'initializer. Vedi _disc_init / _disc_one (parallelizzazione discovery).
_W: dict = {}


def specs_da_rivalutare(existing: dict, reg: dict, cap: int) -> tuple[list[dict], dict]:
    """Quali spec gia' note si ri-valutano in questo run, e con che priorita'.

    IL DIFETTO CHE CORREGGE, in una riga: il taglio buttava fuori proprio le coppie
    piu' vicine alla validazione.

    Una coppia generata prende una conferma SOLO ripassando il gate (`judge_window`
    e' chiamato, nella discovery, unicamente sulle coppie che passano). Quindi una
    spec che non viene ri-valutata non e' "in attesa": e' ferma per sempre, e il
    calendario delle conferme continua a stampare per lei una data che nessuno
    onorera'.

    La versione precedente proteggeva dal taglio le sole spec GIA' VALIDATE, e le
    validate sono zero da quando il registro esiste. Tutto il resto entrava
    nell'ordine in cui era stato scoperto e veniva tagliato a `cap`: le spec piu'
    vecchie dentro, le piu' recenti fuori — un criterio che con le conferme non
    c'entra niente. Una coppia a 2 passaggi su 3 poteva restare fuori dal taglio e
    non arrivare mai al terzo, senza che nessun contatore lo dicesse.

    E' la terza volta che un tetto pensato per limitare i TEMPI finisce per
    sacrificare l'unica cosa che il sistema sta producendo (le altre due: il tetto
    sulle coppie del registro il 31 agosto, e la quota morta per le generate senza
    conferme). Il criterio ora e' esplicito: **prima le conferme, poi l'anzianita'**.

    Le spec con almeno una conferma passano SEMPRE, anche a costo di sforare il cap:
    sono poche (una manciata di centinaia contro migliaia di candidate nuove) e sono
    l'unica cosa che il gate ha prodotto in tre settimane. Sacrificarle per stare nei
    tempi vuol dire non arrivare mai in fondo, che non e' un risparmio.

    Ritorna la lista di spec e un dizionario di diagnostica, che finisce su Firestore
    e da li' nel rapporto: senza, la differenza fra "il taglio morde" e "il taglio
    non morde" resta invisibile esattamente come lo era prima.
    """
    pairs = decode_pairs(reg.get("pairs"))
    # quante conferme ha gia' ogni spec. Una spec puo' vivere su piu' coin: conta la
    # coppia piu' avanti, perche' e' quella che il taglio rischia di buttare via.
    conferme: dict[str, int] = {}
    for k, r in pairs.items():
        if not r.get("generated") or "|" not in k:
            continue
        gid = k.split("|", 1)[1]
        conferme[gid] = max(conferme.get(gid, 0), int(r.get("pass_count", 0) or 0))

    # `sorted` e' stabile: a parita' di conferme resta l'ordine di scoperta, cioe'
    # esattamente il comportamento precedente per tutta la coda senza conferme.
    ordinate = sorted(existing.items(), key=lambda kv: -conferme.get(kv[0], 0))
    con_conferme = [s for gid, s in ordinate if conferme.get(gid, 0) > 0]
    senza = [s for gid, s in ordinate if conferme.get(gid, 0) == 0]
    scelte = con_conferme + senza[: max(0, cap - len(con_conferme))]
    diag = {
        "reeval_cap": cap,
        "n_specs_note": len(existing),
        "n_specs_rivalutate": len(scelte),
        "n_specs_con_conferme": len(con_conferme),
        "n_specs_tagliate": max(0, len(existing) - len(scelte)),
    }
    return scelte, diag


def mutation_seeds(fb, existing: dict, limit: int = 10,
                   pairs: dict | None = None) -> list[dict]:
    """Le spec da cui vale la pena evolvere: i QUASI-PASSAGGI del run precedente,
    con precedenza a quelli sulle coin che NON copriamo ancora.

    Una candidata fermata da UN SOLO criterio e per poco e' l'informazione piu'
    preziosa che un run produce: dice che in quella zona dello spazio delle
    strategie c'e' qualcosa, e che manca poco. Mutare li' e' una ricerca guidata;
    generare candidate a caso e' ricominciare da zero a ogni giro.

    LA PRECEDENZA ALLA COPERTURA, e perche' esiste. L'obiettivo dichiarato dal
    proprietario e' «un sistema che non si ferma mai»: se una moneta non e' coperta,
    la ricerca deve andare a cercare una strategia per QUELLA. Senza questa regola i
    semi si prendevano nell'ordine in cui capitavano, quindi l'evoluzione tendeva a
    rinforzare le coin dove qualcosa gia' funziona — e la copertura, che e' il numero
    che decide quante monete il bot potra' operare, non si muoveva.

    Non e' teoria: al 14 settembre le coppie validate erano 7, tutte sulla STESSA
    moneta. Un'ottava strategia su quella moneta non aggiunge una moneta operabile;
    la prima su una moneta nuova si'.

    Le due meta' restano entrambe: prima i semi che estenderebbero la copertura, poi
    gli altri a riempire. Abbandonare del tutto le coin gia' coperte sarebbe l'errore
    opposto — una coin con una sola coppia validata e' fragile, e la seconda serve.

    Fail-open in ogni punto: nessuna autopsia, autopsia illeggibile, registro non
    passato o quasi-passaggi su strategie BASE (che non sono spec mutabili) -> si
    torna esattamente al comportamento precedente.
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

    # coin gia' coperte = hanno almeno una coppia VALIDATA. E' la definizione che
    # conta per «quante monete potremmo operare»: una coin con due conferme non e'
    # ancora operabile, quindi cercare li' estende comunque la copertura.
    coperte: set = set()
    for r in (pairs or {}).values():
        if int(r.get("pass_count", 0) or 0) >= MIN_PASSES and r.get("symbol"):
            coperte.add(r["symbol"])

    estendono: list[dict] = []
    resto: list[dict] = []
    visti: set = set()
    for n in near:
        key = str(n.get("key", ""))
        if "|" not in key:
            continue
        sym, gid = key.split("|", 1)
        spec = existing.get(gid)
        if spec is None or gid in visti:
            continue
        visti.add(gid)
        (resto if sym in coperte else estendono).append(spec)

    out = estendono[:limit] + resto[: max(0, limit - len(estendono))]
    if coperte and estendono:
        print(f"[discover] semi: {min(len(estendono), limit)} da coin NON coperte "
              f"(su {len(coperte)} gia' coperte)")
    return out[:limit]


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


def prove_dal_paper(fb) -> str:
    """Cosa il PAPER ha misurato, in forma leggibile da chi propone strategie.

    Fino al 19 settembre l'AI riceveva questo, e solo questo:

        «Timeframe operativo: 15m. Universo: crypto futures USDT-M su Binance.»

    Proponeva alla cieca. Non sapeva che il prezzo si ferma a meta' strada dal primo
    obiettivo, che le short perdevano e le long no, ne' su quale criterio muoiono le
    candidate. Avevamo costruito un sistema che misura tutto e poi non lo dice a chi
    deve inventare le soluzioni.

    Qui si mettono insieme SOLO FATTI MISURATI, con il loro campione accanto. Niente
    interpretazioni e niente istruzioni: un'ipotesi la deve formulare chi legge, e
    il gate resta l'unico che decide se vale. Un numero senza il suo campione
    sarebbe peggio di nessun numero — chi legge non saprebbe quanto pesarlo.

    Fail-open in ogni punto: qualunque pezzo manchi, si salta quella riga.
    """
    righe: list[str] = []

    try:
        drift = fb.get_doc("drift", "current") or {}
    except Exception:  # noqa: BLE001
        drift = {}
    glob = drift.get("global") or {}
    if glob.get("trades"):
        righe.append(
            f"PAPER (vissuto, {glob['trades']} trade chiusi): profit factor "
            f"{glob.get('live_pf')} contro {glob.get('expected_pf')} promesso dal gate.")
        if glob.get("mfe_median") is not None and glob.get("first_rung_r"):
            righe.append(
                f"Escursione favorevole mediana {glob['mfe_median']}R contro un primo "
                f"take-profit a {glob['first_rung_r']}R: il prezzo si ferma prima di "
                f"arrivare al primo incasso.")

    try:
        trades = fb.query_collection("trades", order_by="exit_ts") or []
    except Exception:  # noqa: BLE001
        trades = []
    if trades:
        for direzione in ("long", "short"):
            sel = [t for t in trades
                   if str(t.get("direction", "")).lower() == direzione]
            if sel:
                vinti = sum(1 for t in sel if float(t.get("pnl", 0) or 0) > 0)
                pnl = sum(float(t.get("pnl", 0) or 0) for t in sel)
                righe.append(f"Direzione {direzione}: {len(sel)} trade, {vinti} vinti, "
                             f"PnL {pnl:+.2f}.")

    try:
        aut = fb.get_doc("gate_autopsy", "current") or {}
    except Exception:  # noqa: BLE001
        aut = {}
    binding = aut.get("binding") or {}
    if binding and aut.get("evaluated"):
        top = " · ".join(f"{k} {v}" for k, v in list(binding.items())[:4])
        righe.append(f"GATE: su {aut['evaluated']} valutazioni ne passano "
                     f"{aut.get('passed', 0)}; muoiono soprattutto su {top}.")

    if not righe:
        return ""
    return ("Prove misurate finora (campioni piccoli: sono indizi, non leggi).\n"
            + "\n".join(f"- {r}" for r in righe))


def scala_dal_paper(fb, min_trades: int = 10):
    """La scala di TP suggerita da dove il prezzo e' DAVVERO arrivato nel paper.

    E' l'anello che mancava. Il paper misurava `mfe_r` su ogni trade chiuso, il
    rilevatore di deriva lo confrontava col primo gradino e scriveva «mfe mediana
    0,74R < primo TP 1,50R» su una coppia dopo l'altra — e il gate continuava a
    scegliere fra quattro scale scritte a mano, senza mai vedere quel numero.

    Si calcola sui trade di TUTTE le coppie insieme, di proposito: per coppia ce ne
    sono uno o due e un quantile su due numeri non significa niente, mentre «quanto
    lontano arriva il prezzo in unita' di rischio» e' soprattutto una proprieta'
    della scala temporale e del mercato, non della singola moneta.

    Fail-open: senza Firebase, senza trade o senza abbastanza campione ritorna None
    e il gate resta esattamente com'era.
    """
    try:
        trades = fb.query_collection("trades", order_by="exit_ts") or []
    except Exception as exc:  # noqa: BLE001
        print(f"[paper] misura mfe non disponibile ({str(exc)[:80]}) -> scale fisse")
        return None
    mfes = [t.get("mfe_r") for t in trades if t.get("mfe_r") is not None]
    scala = ladder_from_mfe(mfes, min_trades=min_trades)
    if scala:
        print(f"[paper] {len(mfes)} trade chiusi -> scala candidata dal vissuto: "
              f"{list(scala)} (si aggiunge alle {len(SCALE_LADDER_CANDIDATES)} fisse, "
              f"non le sostituisce: sceglie il gate)")
    elif mfes:
        print(f"[paper] solo {len(mfes)} trade con mfe (ne servono {min_trades}): "
              f"scale fisse")
    return scala


def candidate_ladders(scala_paper=None) -> tuple:
    """Le scale che il gate mettera' a confronto per una coppia.

    Le quattro fisse sempre; quella misurata dal paper in piu', se c'e' ed e'
    diversa. Mai al posto delle altre — una misura su pochi trade puo' PROPORRE,
    non decidere."""
    if not scala_paper:
        return SCALE_LADDER_CANDIDATES
    if tuple(scala_paper) in {tuple(c) for c in SCALE_LADDER_CANDIDATES}:
        return SCALE_LADDER_CANDIDATES
    return SCALE_LADDER_CANDIDATES + (tuple(scala_paper),)


def _disc_init(args, end: str, specs: list, scala_paper=None) -> None:
    _W.update(opt=WalkForwardOptimizer(n_windows=args.windows, interval=args.interval),
              args=args, end=end, specs=specs, min_history=_min_history(args.interval),
              scala_paper=scala_paper)


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
        r = evaluate_spec(_W["opt"], sym, candles, frame, spec,
                          scale_candidates=candidate_ladders(_W.get("scala_paper")))
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


def evaluate_spec(opt: WalkForwardOptimizer, symbol: str, candles, frame, spec: dict,
                  scale_candidates=None):
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
        best_metric = None
        # le candidate arrivano dal CHIAMANTE, non da uno stato globale: cosi'
        # `evaluate_spec` resta una funzione di cio' che riceve, e un test puo'
        # verificarla senza ricostruire lo stato dei worker
        for cand in (scale_candidates or SCALE_LADDER_CANDIDATES):
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


def merge_into_registry(fb, out: dict, passed_now: list[str],
                        evaluated_symbols: set | None = None) -> list[str]:
    """Aggiunge SOLO le coppie generate che PASSANO (accumula pass_count) e pota
    quelle generate inutili/stantie, evitando crescita illimitata del documento.
    Ricalcola la lista validated PRESERVANDO i campi di copertura del GATE 1
    (universe/coverage/ready) che spettano a optimize.py.

    `evaluated_symbols`: le coin che QUESTA passata ha davvero guardato. Serve a dare
    a `last_seen_at` un significato solo. Qui dentro si scrivono solo le coppie che
    passano, quindi finora il campo per le generate voleva dire "ultima volta che ha
    PASSATO", mentre per le coppie base (scritte da optimize.py su tutto cio' che
    valuta) vuol dire "ultima volta che e' stata GUARDATA". Un campo, due significati:
    e chi ci costruisce sopra un filtro — per esempio per escludere le coppie di coin
    uscite dall'universo — finisce per scambiare "non passa piu'" con "non esiste
    piu'". Sono due diagnosi opposte: la prima e' una strategia che ha smesso di
    funzionare, la seconda e' un pezzo di mercato che non guardiamo piu'.
    """
    doc = fb.get_doc("strategy_registry", "validated") or {}
    pairs = decode_pairs(doc.get("pairs"))
    now = time.time()
    # le coppie GENERATE sulle coin appena guardate sono state valutate, anche se non
    # hanno passato: il campo lo deve dire.
    if evaluated_symbols:
        for r in pairs.values():
            if r.get("generated") and r.get("symbol") in evaluated_symbols:
                r["last_seen_at"] = now
    drifted = drifted_from_paper(fb)   # evidenza dal paper: vale come fallimento
    # 1) upsert SOLO delle coppie passate (non sporco il registro con i fallimenti)
    for key in passed_now:
        e = out[key]
        rec = pairs.get(key, {"pass_count": 0})
        # UNA SOLA CONTABILITA' PER TUTTO IL REGISTRO. Qui c'era una copia a mano
        # della vecchia regola del "pass onesto" (differenza fra due data_end), che
        # optimize.py ha smesso di usare quando e' passato al verdetto per finestra.
        # Due regole diverse sullo stesso documento: le coppie generate — che sono la
        # maggioranza del registro — accumulavano conferme con un criterio, le base
        # con un altro, e nessuno dei due sapeva dell'altro. E' lo stesso schema che
        # ha gia' prodotto due difetti (due orologi, un campo letto al posto di un
        # altro): finche' esistono due copie della stessa regola, prima o poi
        # divergono. Ora c'e' `judge_window` e basta, per tutti.
        data_end = float(e.get("data_end", 0) or 0)
        if key in drifted:
            # smentita dal vivo: la finestra non puo' chiudersi con una conferma.
            # Un fallimento per FINESTRA, non per run (vedi la nota gemella in
            # scripts/optimize.py: contando a ogni run si purgava in sei ore).
            rec["passed_in_window"] = False
            rec["drift_seen_at"] = now
            judge_window(rec, data_end, False)
            rec["symbol"], rec["strategy"] = e["symbol"], e["strategy"]
            rec["generated"] = True
            rec["last_seen_at"] = now
            pairs[key] = rec
            continue
        # FAIL-CLOSED sul data_end: `judge_window` non giudica senza. Era il buco da
        # cui i run sharded (entries senza data_end) gonfiavano il conteggio.
        judge_window(rec, data_end, True)
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
    # 2) potatura: scarta le coppie GENERATE che non hanno niente da perdere.
    #
    # QUI SI CANCELLAVANO LE COPPIE A META' STRADA. La condizione era
    # `pass_count < MIN_PASSES and last_seen_at < 6 giorni fa`: cioe' una coppia a
    # 2 conferme su 3 veniva CANCELLATA sei giorni dopo che la sua coin era uscita
    # dall'universo — non per un verdetto, ma perche' nessuno la guardava piu'.
    # Le otto coppie ORCAUSDT a 2/3 sarebbero sparite il 19 settembre.
    #
    # E lo faceva dieci righe sopra al commento del tetto, che promette «le coppie
    # con almeno una conferma non si toccano MAI». Due regole sullo stesso
    # documento, in disaccordo, nello stesso file: e' la terza volta.
    #
    # Ora il criterio e' uno solo, `conferme_da_proteggere`, condiviso con la potatura delle
    # base e con la riaggiunta delle coin all'universo: chi ha una conferma presa da
    # meno di MIN_PASSES finestre non si cancella. Chi non ne prende una da tre
    # settimane esce, altrimenti il registro cresce senza limite — che e' il difetto
    # del 31 agosto visto dall'altro lato.
    #
    # Le VALIDATE non si potano mai da qui: sono quelle che il bot opera, e toglierle
    # in silenzio cambierebbe cosa fa il sistema senza che nessuno l'abbia deciso.
    def _da_tenere(r: dict) -> bool:
        if not r.get("generated"):
            return True                                   # le base le pota optimize
        if int(r.get("pass_count", 0) or 0) >= MIN_PASSES:
            return True                                   # validate: mai da qui
        return conferme_da_proteggere(r, now)

    pairs = {k: r for k, r in pairs.items() if _da_tenere(r)}
    # cap: limita il numero di coppie per non superare 1 MiB di documento.
    #
    # QUI IL 31 AGOSTO IL REGISTRO SI E' FERMATO DEL TUTTO, in silenzio. Le coppie
    # base non venivano mai potate e crescevano a ogni rotazione dell'universo (ogni
    # coin mai scansionata lascia 8 coppie per sempre). Quando hanno superato il
    # tetto da sole — 3041 su 3000 — `gen_budget` e' diventato ZERO, e la riga qui
    # sotto cancellava TUTTE le generate a ogni passata. La discovery trovava ottanta
    # candidate a giro, le scriveva, e la stessa funzione le buttava via subito dopo.
    # Nessun errore, nessun log: solo un registro che non poteva piu' accumulare
    # niente. Le 137 coppie a un passaggio del 27 agosto erano diventate 2.
    #
    # Due difese, perche' una sola non basta:
    #   1. le coppie con almeno una CONFERMA non si toccano mai. Ognuna costa una
    #      settimana di attesa: buttarle per far spazio significa buttare l'unica
    #      cosa che il sistema sta producendo. Se per tenerle si sfora il tetto, si
    #      sfora — a quel punto e' `slim_registry` a togliere i campi descrittivi, che
    #      e' un prezzo che si puo' pagare. Cancellare passaggi veri no.
    #
    # UNA SOLA REGOLA, non due. La prima versione di questa correzione riservava
    # anche una quota alle generate SENZA conferme, ed era codice morto: la potatura
    # qui sopra le toglie tutte (`pass_count == 0`), quindi quell'insieme e' sempre
    # vuoto. Un test lo ha mostrato subito. Meglio una difesa sola che si capisce
    # che due di cui una non fa niente.
    max_pairs = int(os.getenv("OPTIMIZER_MAX_PAIRS", "3000"))
    if len(pairs) > max_pairs:
        base = {k: r for k, r in pairs.items() if not r.get("generated")}
        gen = {k: r for k, r in pairs.items() if r.get("generated")}
        # INTOCCABILI: hanno gia' pagato il prezzo del tempo. Ognuna e' una
        # settimana di attesa, e sono l'unica cosa che il sistema sta producendo.
        con_pass = {k: r for k, r in gen.items()
                    if int(r.get("pass_count", 0) or 0) > 0}
        resto = {k: r for k, r in gen.items() if k not in con_pass}
        budget = max(0, max_pairs - len(base) - len(con_pass))
        if len(resto) > budget:
            ranked = sorted(resto.items(),
                            key=lambda kv: kv[1].get("last_seen_at", 0), reverse=True)
            resto = dict(ranked[:budget])
        if len(base) + len(con_pass) > max_pairs:
            print(f"[registry] tetto {max_pairs} sforato per tenere "
                  f"{len(con_pass)} coppie con conferme: e' voluto. Le "
                  f"{len(base)} base vanno potate da optimize.py, non da qui.")
        pairs = {**base, **con_pass, **resto}
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
    # ALLEGGERITO ANCHE QUI, e non e' un dettaglio: la discovery scrive il registro
    # DOPO optimize. Finche' questa riga usava `encode_pairs` grezzo, rigonfiava di
    # colpo tutto cio' che optimize aveva appena alleggerito — cioe' la rete c'era
    # ma l'ultimo a scrivere la toglieva.
    doc["pairs"] = slim_registry(pairs, validated)
    doc["validated"] = validated
    doc["coins_covered"] = len(validated_coins)
    doc["coins"] = validated_coins
    doc["universe_size"] = universe
    doc["coverage"] = round(len(validated_coins) / universe, 3)
    doc["updated_at"] = now
    scrivi_registro(fb, doc, pairs)
    publish_timeline(fb, pairs, "discover", len(out), len(passed_now))
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
    prove = prove_dal_paper(fb)
    if prove:
        print(f"[discover] prove del paper passate all'AI:\n{prove}")
    ai_specs = ai_propose(min(settings.AI_HYPOTHESES_PER_RUN, args.generate),
                          market_context=f"Timeframe operativo: {args.interval}. "
                                         f"Universo: crypto futures USDT-M su Binance."
                                         + (f"\n\n{prove}" if prove else ""))
    if ai_specs:
        print(f"[discover] {len(ai_specs)} ipotesi AI (motivate) + "
              f"{args.generate - len(ai_specs)} casuali")
    specs = ai_specs + generate_specs(max(0, args.generate - len(ai_specs)), seed=args.seed)
    existing = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
    reg = fb.get_doc("strategy_registry", "validated") or {}
    existing_list, diag_reeval = specs_da_rivalutare(existing, reg, args.reeval_cap)
    specs.extend(existing_list)
    # MUTAZIONE INFORMATA: si evolve attorno ai QUASI-PASSAGGI del run precedente
    # (una sola condizione mancata, e per poco), non attorno alle prime dieci spec
    # che capitano. E' la differenza fra cercare dove l'ultimo tentativo si e'
    # avvicinato e ricominciare da capo ogni volta. Fail-open: senza autopsia si
    # mutano le prime, come prima.
    # il registro serve a sapere quali coin sono GIA' coperte: i semi vanno
    # preferibilmente sulle altre, altrimenti l'evoluzione rinforza dove qualcosa
    # gia' funziona e il numero di monete operabili non si muove.
    seeds = mutation_seeds(fb, existing, pairs=decode_pairs(reg.get("pairs")))
    if seeds:
        print(f"[discover] {len(seeds)} semi dai quasi-passaggi del run precedente")
    bases = seeds or existing_list[:10]
    for i, base in enumerate(bases[:10]):
        specs.append(mutate(base, seed=args.seed + i + 1))
    # de-dup per id
    specs = list({s["id"]: s for s in specs}.values())
    print(f"[discover] {len(specs)} candidate "
          f"({diag_reeval['n_specs_con_conferme']} con conferme ri-validate + "
          f"{len(existing_list) - diag_reeval['n_specs_con_conferme']} altre, "
          f"{diag_reeval['n_specs_tagliate']} tagliate su "
          f"{diag_reeval['n_specs_note']} note) seed={args.seed} {args.start}->{end}")

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
    # L'UNIVERSO RUOTA, LA VALIDAZIONE NO. Il top-N per volume cambia ogni giorno —
    # fra l'8 e il 14 settembre ne e' uscito il 26% — ma una coppia ha bisogno di due
    # settimane con la SUA coin dentro. Quando la coin esce, la coppia non fallisce:
    # si ferma a meta' strada, perche' nella discovery una coppia prende la conferma
    # successiva solo ripassando, e chi non viene valutato non passa.
    #
    # E' successo a ORCAUSDT il 13 settembre, con OTTO coppie a 2 conferme su 3, il
    # giorno stesso in cui la loro finestra scadeva: un tentativo, uno solo, e poi il
    # sistema ha smesso di guardarle.
    #
    # La riaggiunta sta DOPO il filtro di proposito: una coin che ha gia' prodotto
    # conferme ha gia' dimostrato di essere informativa, e lasciarla escludere
    # rimetterebbe in piedi lo stesso buco da un'altra porta.
    if not getattr(args, "symbols", ""):
        maturazione, diag_mat = coin_in_maturazione(
            decode_pairs(reg.get("pairs")), time.time())
        riaggiunte = [s for s in maturazione if s not in set(full_symbols)]
        if riaggiunte:
            print(f"[discover] {len(riaggiunte)} coin riaggiunte: hanno una coppia in "
                  f"maturazione ma sono uscite dal top-{args.top} per volume "
                  f"({', '.join(riaggiunte[:12])}"
                  f"{' ...' if len(riaggiunte) > 12 else ''})")
            full_symbols = list(full_symbols) + riaggiunte
        # QUANTE NE RESTANO FUORI. La versione precedente lo prometteva in docstring
        # e non lo stampava: un tetto che morde in silenzio e' il difetto che la
        # riaggiunta esiste per chiudere, rientrato dalla porta del commento.
        print(f"[discover] maturazione: {diag_mat['intoccabili']} coin a un passo "
              f"dalla validazione (mai tagliate) + {diag_mat['coda_tenuta']} con una "
              f"conferma · {diag_mat['tagliate']} tagliate dalla coda")
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
        _disc_one, symbols, workers=workers, initializer=_disc_init,
        initargs=(args, end, specs, scala_dal_paper(fb))
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
    validated = merge_into_registry(fb, out, passed_keys,
                                    evaluated_symbols=set(symbols))
    # riepilogo COMPATTO (niente spec/entry per ogni coppia: sforerebbe il limite
    # di 1 MiB di Firestore). Le spec complete stanno in discovered_strategies/specs.
    fb.set_doc("strategy_params", "discovered_last_run", {
        "updated_at": time.time(),
        "n_eval": n_eval,
        "n_passed": len(passed_keys),
        # QUANTO MORDE IL TAGLIO. Senza questi numeri, "il registro non accumula" e
        # "meta' del registro non viene piu' guardata" sono indistinguibili da fuori.
        **diag_reeval,
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
