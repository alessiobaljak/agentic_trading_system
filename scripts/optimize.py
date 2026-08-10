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
import os
import time
from datetime import date

import requests

from backtesting.data_loader import load_candles
from backtesting.optimizer import WalkForwardOptimizer
from backtesting.parallel import n_workers, parallel_map
from bot.config import settings, timeframe_hours
from bot.core.firebase_client import decode_pairs, encode_pairs, get_firebase


def _min_history(interval: str) -> int:
    """Minimo di CANDELE perche' una coin sia validabile, definito in GIORNI di
    storia (default 365) e convertito nel timeframe corrente. Cosi' il requisito
    NON si indebolisce cambiando timeframe (2500 candele fisse = 104 giorni a 1h
    ma solo 26 a 15m). OPTIMIZER_MIN_HISTORY (in candele) vince se impostato.

    Perche' 365 e non 180: con 180 giorni, tolti i 45 di holdout, restano 135 da
    dividere in 4 blocchi -> finestre da 34 giorni. Le "3 validazioni OOS
    indipendenti" diventano tre fette contigue dello stesso trimestre, per giunta
    spesso i primi mesi di una listing nuova (una fase di mercato sola, molto
    direzionale). E' il caso misurato su BIRBUSDT: 191 giorni di storia, passava il
    minimo per 11, PF 1.51 nel gate e 0.16 nel paper. Un anno porta le finestre a
    ~80 giorni e fa entrare almeno un cambio di regime."""
    env = os.getenv("OPTIMIZER_MIN_HISTORY")
    if env:
        return int(env)
    days = float(os.getenv("OPTIMIZER_MIN_HISTORY_DAYS", "365"))
    return int(days * 24.0 / timeframe_hours(interval))

FAPI = "https://fapi.binance.com"
OKX = "https://www.okx.com"

# stato pesante per-worker (optimizer + contesto BTC), costruito una volta per
# processo dall'initializer. Vedi _opt_init / _opt_one (parallelizzazione GATE 1).
_W: dict = {}


def _opt_init(args, end: str) -> None:
    """Costruisce lo stato del worker UNA volta: optimizer + contesto BTC cross-asset."""
    opt = WalkForwardOptimizer(n_windows=args.windows, max_combos=args.max_combos,
                               seed=int(time.time() * 1000) % 100000, interval=args.interval)
    btc_ctx = None
    try:
        btc_candles = load_candles("BTCUSDT", args.interval, args.start, end, prefer=args.source)
        if len(btc_candles) >= 200:
            btc_ctx = opt.bt.build_context("BTCUSDT", btc_candles)
    except Exception as exc:  # noqa: BLE001
        print(f"[optimize] contesto BTC non disponibile nel worker: {exc}")
    _W.update(opt=opt, btc_ctx=btc_ctx, args=args, end=end,
              min_history=_min_history(args.interval))


def _opt_one(sym: str) -> tuple[str, dict, list]:
    """Ottimizza un singolo simbolo (eseguito nei worker). Ritorna (sym, entries, passed)."""
    args, end = _W["args"], _W["end"]
    candles = load_candles(sym, args.interval, args.start, end, prefer=args.source)
    if len(candles) < _W["min_history"]:
        return (sym, {}, [])
    results = _W["opt"].optimize_symbol(sym, candles, context_by_ts=_W["btc_ctx"])
    entries: dict = {}
    passed: list = []
    for r in results:
        key = f"{sym}|{r.strategy}"
        entries[key] = {
            "symbol": sym, "strategy": r.strategy, "params": r.best_params,
            "oos_pf": r.oos_pf, "oos_pnl_pct": r.oos_pnl_pct,
            "oos_trades": r.oos_trades, "oos_win_rate": r.oos_win_rate,
            "passed": r.passed, "trailing": r.trailing,
            # holdout (dati mai visti dalla selezione), PF per-regime e fine dati:
            # alimentano il registro (verifica, filtro regime, pass onesto).
            "holdout": r.holdout, "regime_pf": r.regime_pf, "data_end": r.data_end,
        }
        if r.passed:
            passed.append(key)
    return (sym, entries, passed)


def top_symbols_by_volume(n: int) -> list[str]:
    """
    Universo = perpetual USDT di BINANCE (dove il bot opera davvero).
    Prova il ranking dinamico per volume su Binance; se Binance non è raggiungibile
    (es. geo-block sui runner GitHub) usa una lista CURATA e ampia di perp Binance
    reali (major + alt + meme) — MAI OKX, che lista anche oro/azioni/coin non-Binance.
    """
    try:
        info = requests.get(f"{FAPI}/fapi/v1/exchangeInfo", timeout=20).json()
        perp = {
            s["symbol"] for s in info.get("symbols", [])
            if s.get("contractType") == "PERPETUAL" and s.get("quoteAsset") == "USDT"
            and s.get("status") == "TRADING"
        }
        tickers = requests.get(f"{FAPI}/fapi/v1/ticker/24hr", timeout=20).json()
        if isinstance(tickers, list) and perp:
            ranked = sorted((t for t in tickers if t.get("symbol") in perp),
                            key=lambda t: float(t.get("quoteVolume", 0)), reverse=True)
            if ranked:
                return [t["symbol"] for t in ranked[:n]]
    except Exception as exc:  # noqa: BLE001
        print(f"[optimize] ranking Binance non disponibile ({str(exc)[:60]}); uso lista curata")
    return BINANCE_PERPS[:n]


# Lista curata di perpetual USDT REALI su Binance (major + alt consolidate + meme
# liquide). Usata quando il ranking dinamico Binance non è raggiungibile.
BINANCE_PERPS = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT",
    "AVAXUSDT", "LINKUSDT", "DOTUSDT", "TRXUSDT", "LTCUSDT", "BCHUSDT", "NEARUSDT",
    "SUIUSDT", "APTUSDT", "ARBUSDT", "OPUSDT", "ATOMUSDT", "UNIUSDT", "INJUSDT",
    "TIAUSDT", "SEIUSDT", "FILUSDT", "ETCUSDT", "AAVEUSDT", "TONUSDT", "HBARUSDT",
    "ICPUSDT", "IMXUSDT", "STXUSDT", "GALAUSDT", "SANDUSDT", "WLDUSDT", "ENAUSDT",
    "JUPUSDT", "PYTHUSDT", "ORDIUSDT", "SHIBUSDT", "PEPEUSDT", "WIFUSDT", "BONKUSDT",
    "FLOKIUSDT", "RUNEUSDT", "ALGOUSDT", "FTMUSDT", "XLMUSDT", "VETUSDT", "EGLDUSDT",
    "AXSUSDT",
    # --- ampliamento universo (alt liquide consolidate, presenti anche su OKX) ---
    "FETUSDT", "RENDERUSDT", "GRTUSDT", "LDOUSDT", "MKRUSDT", "CRVUSDT", "COMPUSDT",
    "DYDXUSDT", "ENSUSDT", "MANAUSDT", "CHZUSDT", "FLOWUSDT", "EOSUSDT", "1INCHUSDT",
    "SUSHIUSDT", "YFIUSDT", "ZECUSDT", "DASHUSDT", "NEOUSDT", "IOTAUSDT", "WAVESUSDT",
    "APEUSDT", "GMTUSDT", "MINAUSDT", "PEOPLEUSDT", "ARUSDT", "KAVAUSDT", "SNXUSDT",
    "MASKUSDT", "ROSEUSDT",
]



def main() -> int:
    p = argparse.ArgumentParser(description="Ottimizzazione walk-forward autonoma")
    p.add_argument("--symbols", default="BTCUSDT,ETHUSDT,SOLUSDT,BNBUSDT,XRPUSDT")
    p.add_argument("--top", type=int, default=0,
                   help="se >0, ottimizza i top-N future per volume (ignora --symbols)")
    p.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    p.add_argument("--start", default="2022-01-01")
    p.add_argument("--end", default=None, help="default: oggi (finestra che avanza)")
    p.add_argument("--source", default="binance")
    p.add_argument("--windows", type=int, default=3)
    p.add_argument("--max-combos", type=int, default=12,
                   help="max combinazioni di parametri provate per strategia (0=tutte)")
    p.add_argument("--reset-registry", action="store_true",
                   help="azzera il registro validato prima di accumulare (ripartenza pulita)")
    p.add_argument("--shard", type=int, default=0, help="indice shard (parallelizzazione)")
    p.add_argument("--num-shards", type=int, default=1, help="numero totale di shard")
    p.add_argument("--merge", action="store_true",
                   help="modalita' MERGE: riunisce i risultati degli shard nel registro")
    args = p.parse_args()
    end = args.end or date.today().isoformat()

    fb = get_firebase()
    if args.merge:
        return _merge_shards(fb, args)

    full_symbols = []
    if args.top > 0:
        full_symbols = top_symbols_by_volume(args.top)
        print(f"[optimize] universo: top {args.top} per volume -> {len(full_symbols)} coin")
    if not full_symbols:
        full_symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    # SHARDING: ogni shard processa una fetta dell'universo (round-robin), il merge
    # le riunisce. Così l'intero universo è coperto restando nel timeout di GitHub.
    symbols = full_symbols[args.shard::args.num_shards] if args.num_shards > 1 else full_symbols
    print(f"[optimize] shard {args.shard}/{args.num_shards}: {len(symbols)}/{len(full_symbols)} coin")
    if args.reset_registry and args.num_shards <= 1:
        # pulizia TOTALE del GATE 1 (solo non-sharded; in sharded la fa il merge).
        fb.set_doc("strategy_registry", "validated", {})
        fb.set_doc("discovered_strategies", "specs", {"specs": {}})
        fb.set_doc("strategy_params", "current", {})
        print("[optimize] reset TOTALE: registro + strategie scoperte + ultimo run azzerati")

    out: dict[str, dict] = {}
    summary_passed: list[str] = []

    # PARALLELO: i simboli sono indipendenti -> li distribuiamo su tutti i core del
    # runner (process pool). Ogni worker costruisce il proprio optimizer + contesto
    # BTC una volta sola. Fallback sequenziale automatico se BACKTEST_WORKERS=1.
    workers = n_workers()
    print(f"[optimize] {len(symbols)} coin su {workers} worker (core)")
    for sym, entries, passed in parallel_map(
        _opt_one, symbols, workers=workers, initializer=_opt_init, initargs=(args, end)
    ):
        if not entries:
            print(f"[optimize] {sym}: storia insufficiente, saltato")
            continue
        out.update(entries)
        summary_passed.extend(passed)
        print(f"[optimize] {sym}: {len(entries)} coppie, {len(passed)} passate "
              f"{'✅' if passed else ''}")

    # SHARD: scrive il proprio risultato in un doc separato; il merge li riunisce.
    if args.num_shards > 1:
        fb.set_doc("optimize_shards", str(args.shard), {
            "run_id": os.getenv("GITHUB_RUN_ID", ""),
            "out": encode_pairs(out), "passed": encode_pairs(summary_passed),
            "updated_at": time.time(),
        })
        print(f"[optimize] shard {args.shard} scritto: {len(out)} coppie, "
              f"{len(summary_passed)} passate. Il merge aggiornera' il registro.")
        return 0

    # entries/passed CODIFICATI come stringa JSON: Firestore indicizza UN campo
    # invece di ogni sottocampo di ogni coppia (200 coin x 9 strat sfondano il
    # limite di 40k voci d'indice -> "INDEX_ENTRIES_COUNT_LIMIT_EXCEEDED").
    fb.set_doc("strategy_params", "current", {
        "updated_at": time.time(),
        "entries": encode_pairs(out),
        "passed": encode_pairs(summary_passed),
    })

    # --- registro di validazione cumulativo (robustezza nel tempo) ---
    reg = update_registry(fb, out, summary_passed)

    cov_pct = reg["coverage"] * 100
    gate_str = ("SUPERATO ✅" if reg["ready"]
                else f"in corso ({cov_pct:.0f}% < {READY_FRACTION*100:.0f}%)")
    print("\n" + "=" * 60)
    print(f"[optimize] {len(out)} coppie valutate, {len(summary_passed)} passate in QUESTO run.")
    print(f"[optimize] REGISTRO: {reg['coins_covered']}/{reg['universe_size']} crypto "
          f"({cov_pct:.0f}%) con strategia validata (>= {MIN_PASSES} pass). GATE 1 {gate_str}")
    reg_pairs = decode_pairs(reg["pairs"])   # 'pairs' e' codificato (stringa) nel registro
    for k in reg["validated"]:
        rec = reg_pairs.get(k, {})
        print(f"   ✅ {k}  passes={rec.get('pass_count')}  -> {rec.get('last_params')}")
    print("=" * 60)

    # --- report automatico su Telegram ---
    _notify_telegram(out, summary_passed, reg)
    return 0


def _merge_shards(fb, args) -> int:
    """Riunisce i risultati degli shard (optimize_shards/*) e aggiorna il registro
    UNA volta sola (niente race tra job paralleli). La copertura GATE 1 è calcolata
    sull'unione dell'intero universo coperto dagli shard."""
    run_id = os.getenv("GITHUB_RUN_ID", "")
    combined_out: dict = {}
    combined_passed: list[str] = []
    used = 0
    for i in range(args.num_shards):
        d = fb.get_doc("optimize_shards", str(i)) or {}
        if not d:
            print(f"[merge] shard {i}: assente, salto")
            continue
        if run_id and d.get("run_id") and d.get("run_id") != run_id:
            print(f"[merge] shard {i}: run_id diverso (stantio), salto")
            continue
        combined_out.update(decode_pairs(d.get("out")))
        combined_passed.extend(decode_pairs(d.get("passed")) or [])
        used += 1
    print(f"[merge] {used}/{args.num_shards} shard uniti: {len(combined_out)} coppie, "
          f"{len(combined_passed)} passate")
    if args.reset_registry:
        fb.set_doc("strategy_registry", "validated", {})
        fb.set_doc("discovered_strategies", "specs", {"specs": {}})
        print("[merge] reset TOTALE del registro prima di applicare i risultati")
    fb.set_doc("strategy_params", "current", {
        "updated_at": time.time(),
        "entries": encode_pairs(combined_out), "passed": encode_pairs(combined_passed),
    })
    reg = update_registry(fb, combined_out, combined_passed)
    cov_pct = reg["coverage"] * 100
    print(f"[merge] REGISTRO: {reg['coins_covered']}/{reg['universe_size']} crypto "
          f"({cov_pct:.0f}%). GATE 1 {'SUPERATO ✅' if reg['ready'] else 'in corso'}")
    _notify_telegram(combined_out, combined_passed, reg)
    return 0


import os

# numero di run in cui una coppia deve passare l'OOS per essere "validata"
MIN_PASSES = int(os.getenv("OPTIMIZER_MIN_PASSES", "3"))
# GATE 1 in PERCENTUALE: pronto quando la frazione dei coin scansionati ORA che
# hanno almeno una strategia validata supera questa soglia. Si adatta se cambiano
# le crypto nell'universo (non un numero fisso). Regolabile via env.
READY_FRACTION = float(os.getenv("OPTIMIZER_READY_FRACTION", "0.60"))
# minimi di sicurezza: non dichiarare "ready" se l'universo è troppo piccolo o se
# le crypto validate in assoluto sono troppo poche.
MIN_UNIVERSE = int(os.getenv("OPTIMIZER_MIN_UNIVERSE", "10"))
MIN_COVERED = int(os.getenv("OPTIMIZER_MIN_COVERED", "5"))
# una coppia resta "validata" solo se rivista entro questi giorni (auto-pulizia:
# i coin usciti dall'universo decadono e il bot smette di operarli).
FRESH_DAYS = float(os.getenv("OPTIMIZER_FRESH_DAYS", "3"))
# un pass conta SOLO se dall'ultimo pass sono entrate almeno queste ore di dati
# nuovi: rivalutare gli stessi dati non e' una conferma indipendente.
# 24 ore erano troppo poche: con l'ottimizzatore che gira ogni 8h, tre pass
# potevano maturare in tre giorni su dati identici al 99%, e MIN_PASSES=3 non
# significava piu' nulla (BIRBUSDT aveva pass_count 3 su 191 giorni di storia).
# 168 ore = una settimana: su una finestra OOS da ~80 giorni e' circa il 9% di
# dati davvero nuovi per ogni conferma.
NEW_DATA_MIN_S = float(os.getenv("OPTIMIZER_NEW_DATA_MIN_HOURS", "168")) * 3600
# auto-purge: una coppia viene RIMOSSA dal registro dopo N run consecutivi in cui,
# pur essendo processata, non passa piu' il gate (costi/edge non piu' battuti).
PURGE_FAILS = int(os.getenv("OPTIMIZER_PURGE_FAILS", "2"))


def drifted_from_paper(fb) -> set:
    """Coppie che il PAPER ha visto contraddire la promessa del gate.

    E' l'anello di ritorno: il gate valida sulla storia, il paper vive il presente
    e, quando il vissuto smentisce, quell'evidenza pesa qui — non come "riottimizza
    sui trade paper" (li consumerebbe come training set) ma come FALLIMENTO, alla
    pari di una bocciatura sulle finestre. Due fallimenti consecutivi -> auto-purge.
    Se invece la coppia ripassa il gate su storia AGGIORNATA (che ora include il
    periodo vissuto dal paper), il fail_count si azzera e la coppia si redime."""
    try:
        from bot.learning.drift import drifted_keys
        return set(drifted_keys(fb.get_doc("drift", "current") or {}))
    except Exception as exc:  # noqa: BLE001
        print(f"[registry] deriva non leggibile ({exc}): la ignoro")
        return set()


def update_registry(fb, out: dict, passed_now: list[str]) -> dict:
    """
    Accumula nel tempo: ogni run incrementa il pass_count delle coppie che passano.
    Una coppia è VALIDATA con pass_count >= MIN_PASSES. Il modello è "ready" quando
    ci sono strategie validate su >= READY_COINS crypto distinte.
    """
    doc = fb.get_doc("strategy_registry", "validated") or {}
    pairs: dict = decode_pairs(doc.get("pairs"))
    passed_set = set(passed_now)
    drifted = drifted_from_paper(fb)
    if drifted:
        print(f"[registry] {len(drifted)} coppie in deriva dal paper: contano come "
              f"fallimento anche se hanno ripassato le finestre")

    for key, e in out.items():
        rec = pairs.get(key, {"pass_count": 0})
        # una coppia SMENTITA DAL VIVO non puo' accumulare un pass, nemmeno se la
        # storia la promuove ancora: e' il paper ad avere l'ultima parola sul presente
        if key in drifted:
            rec["fail_count"] = rec.get("fail_count", 0) + 1
            rec["drift_seen_at"] = time.time()
            rec["symbol"], rec["strategy"] = e["symbol"], e["strategy"]
            rec["last_seen_at"] = time.time()
            pairs[key] = rec
            continue
        if key in passed_set:
            # PASS ONESTO: incrementa solo se ci sono dati NUOVI dall'ultimo pass.
            # Senza questa regola MIN_PASSES contava rivalutazioni degli stessi
            # dati, non conferme indipendenti (il difetto che gonfiava il registro).
            data_end = float(e.get("data_end", 0) or 0)
            prev_end = float(rec.get("last_pass_data_end", 0) or 0)
            # FAIL-CLOSED: senza data_end il pass NON conta (nessun percorso deve
            # poter incrementare "gratis" dimenticando il campo).
            if data_end > 0 and (prev_end <= 0 or data_end - prev_end >= NEW_DATA_MIN_S):
                rec["pass_count"] = rec.get("pass_count", 0) + 1
                rec["last_pass_data_end"] = data_end
            rec["fail_count"] = 0                      # ripassata -> azzera i fallimenti
            rec["last_params"] = e["params"]
            if e.get("holdout"):
                rec["holdout"] = e["holdout"]
            if e.get("regime_pf"):
                rec["regime_pf"] = e["regime_pf"]
            rec["last_pf"] = e["oos_pf"]
            rec["last_pnl_pct"] = e["oos_pnl_pct"]
            rec["last_trades"] = e["oos_trades"]
            rec["last_win_rate"] = e.get("oos_win_rate")
            tr = e.get("trailing") or {}
            rec["trailing_premature"] = tr.get("premature", 0)
            rec["trailing_protected"] = tr.get("protected", 0)
            rec["trailing_neutral"] = tr.get("neutral", 0)
            rec["last_passed_at"] = time.time()
        else:
            # PROCESSATA ma NON passata: conta i fallimenti consecutivi (auto-purge)
            rec["fail_count"] = rec.get("fail_count", 0) + 1
        rec["symbol"] = e["symbol"]
        rec["strategy"] = e["strategy"]
        rec["last_seen_at"] = time.time()
        pairs[key] = rec

    # AUTO-PURGE: rimuove le coppie che falliscono il gate per PURGE_FAILS run
    # CONSECUTIVI (non piu' il cricchetto che solo aggiunge). Cosi' il registro si
    # auto-pulisce: chi smette di battere i costi/edge esce da solo, senza script
    # manuali. 1 fallimento non basta (rumore/dati): serve la conferma.
    purged = [k for k, r in pairs.items() if r.get("fail_count", 0) >= PURGE_FAILS]
    for k in purged:
        del pairs[k]
    if purged:
        print(f"[registry] AUTO-PURGE: rimosse {len(purged)} coppie "
              f"(fallite {PURGE_FAILS}+ run di fila)")

    validated = sorted(
        k for k, r in pairs.items()
        if r.get("pass_count", 0) >= MIN_PASSES
        and (time.time() - r.get("last_seen_at", 0)) < FRESH_DAYS * 86400
    )
    validated_coins = {pairs[k]["symbol"] for k in validated}

    # COPERTURA = tutte le coin che hanno almeno una strategia validata (coerente
    # col dashboard), NON solo quelle che capitano nel top-80 di oggi. Denominatore:
    # l'universo scansionato in questo run (o le coin validate, se piu' grande).
    current_coins = sorted({e["symbol"] for e in out.values()})
    covered = sorted(validated_coins)
    universe = max(len(current_coins), len(covered)) or 1
    coverage = len(covered) / universe
    ready = (coverage >= READY_FRACTION
             and universe >= MIN_UNIVERSE
             and len(covered) >= MIN_COVERED)

    registry = {
        "updated_at": time.time(),
        "pairs": encode_pairs(pairs),
        "validated": validated,
        "coins_covered": len(covered),
        "coins": covered,
        "universe_size": universe,
        "universe_coins": current_coins,
        "coverage": round(coverage, 3),
        "ready": ready,
        "min_passes": MIN_PASSES,
        "ready_fraction": READY_FRACTION,
        "min_universe": MIN_UNIVERSE,
        "min_covered": MIN_COVERED,
    }
    fb.set_doc("strategy_registry", "validated", registry)
    return registry


def _notify_telegram(out: dict, passed: list[str], reg: dict) -> None:
    try:
        from bot.execution.notifier import TelegramNotifier
        notifier = TelegramNotifier()
        top = sorted((out[k] for k in passed), key=lambda e: e["oos_pnl_pct"], reverse=True)[:8]
        cov_pct = reg["coverage"] * 100
        lines = ["🧠 <b>Ottimizzazione completata</b>",
                 f"{len(passed)}/{len(out)} coppie passate in questo run (netto fee).",
                 f"📚 GATE 1: <b>{reg['coins_covered']}/{reg['universe_size']} crypto "
                 f"({cov_pct:.0f}%)</b> con strategia validata "
                 f"(obiettivo {reg['ready_fraction']*100:.0f}%).",
                 "🌐 Universo scansionato: " + ", ".join(reg.get("universe_coins", [])[:14]), ""]
        if top:
            lines.append("<b>Migliori in questo run:</b>")
            for e in top:
                lines.append(f"• {e['symbol']} · {e['strategy']} · pf {e['oos_pf']:.2f} · "
                             f"{e['oos_pnl_pct']*100:+.0f}%")
        if reg["ready"]:
            lines += ["", "🎯 <b>GATE 1 SUPERATO</b>: modello validato su abbastanza crypto. "
                      "Si può passare al PAPER TRADING."]
        notifier.send("\n".join(lines))
    except Exception as exc:  # noqa: BLE001
        print(f"[optimize] notifica Telegram saltata: {exc}")


if __name__ == "__main__":
    raise SystemExit(main())
