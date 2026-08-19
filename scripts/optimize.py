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
    # COIN DELISTATA: la serie finisce mesi fa. Ha storia a sufficienza, quindi il
    # controllo qui sopra la lascia passare, e il gate la valida allegramente su un
    # mercato che non esiste piu' — con l'ultima posizione chiusa a un prezzo che nella
    # realta' si sarebbe eseguito in un book in liquidazione. Il controllo esisteva
    # (quality.looks_delisted) ma era cablato solo in backtesting/run.py, cioe' nel
    # report a mano: il job che alimenta il registro non lo chiamava.
    from backtesting.quality import looks_delisted
    if looks_delisted(candles, end, timeframe_hours(args.interval)):
        print(f"[optimize] {sym}: serie ferma al "
              f"{candles[-1].open_time:%Y-%m-%d} -> coin delistata, saltata")
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
            "oos_max_dd": r.oos_max_dd,
            # AUTOPSIA: dove muore. Senza, ogni run ripete ventimila esperimenti
            # e non ne conserva l'esito.
            "fail_criteria": list(r.fail_criteria), "fail_binding": r.fail_binding,
            "fail_shortfall": r.fail_shortfall, "near_miss": r.near_miss,
            "t_stat": r.t_stat,
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

    # L'AUTOPSIA PRIMA DEI PARAMETRI, e non e' un dettaglio d'ordine: la scrittura
    # dei parametri e' quella che puo' fallire per dimensione (vedi persist_params),
    # e quando e' fallita si e' portata via la diagnosi e l'aggiornamento del
    # registro — quattro ore di calcolo buttate perche' l'ULTIMO passo non e' andato.
    # Prima si mette al sicuro cio' che costa di piu' ricreare.
    publish_autopsy(fb, out)
    persist_params(fb, out, summary_passed)

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
# VIA ALTERNATIVA alla copertura: numero ASSOLUTO di coppie validate sufficiente a
# partire. Serve perche' con un gate severo la copertura percentuale non si
# raggiunge mai (misurato: 9 coppie passate su 1200 valutate -> 6.7% di copertura
# contro una soglia del 35%). Quello che serve per iniziare non e' coprire una
# fetta del mercato, e' avere abbastanza strategie validate da diversificare.
# 0 = disattivata (vale solo la copertura).
READY_MIN_PAIRS = int(os.getenv("OPTIMIZER_READY_MIN_PAIRS", "0"))
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


# Campi che qualcuno LEGGE davvero da strategy_params/current: i parametri (il bot),
# e le metriche mostrate per le coppie passate (snapshot e dashboard). Tutto il resto
# vive nel registro o serve solo dentro il processo che lo calcola.
PARAM_DOC_FIELDS = {
    "symbol", "strategy", "params", "passed",
    "oos_pf", "oos_pnl_pct", "oos_trades", "oos_win_rate",
    "oos_max_dd", "holdout", "regime_pf", "data_end", "trailing", "scale_r_mults",
}
# Firestore rifiuta un documento oltre 1 MiB. Si sta sotto con margine, perche' il
# limite vero e' su TUTTO il documento, non sul solo campo.
PARAM_DOC_MAX_BYTES = int(os.getenv("PARAM_DOC_MAX_BYTES", "900000"))


def slim_entries(out: dict, passed: list, max_bytes: int = PARAM_DOC_MAX_BYTES) -> dict:
    """Le entries da PERSISTERE, ridotte a cio' che qualcuno legge davvero.

    Il documento `strategy_params/current` contiene una voce per ogni coppia
    valutata: con duecento coin e otto strategie sono ~1500 voci, ed era gia' a
    ridosso del limite di 1 MiB di Firestore. Aggiungere cinque campi diagnostici
    per voce (l'autopsia) lo ha sfondato — e il crash e' arrivato DOPO quattro ore
    di calcolo, portandosi via diagnosi e aggiornamento del registro.

    Da qui due difese. La prima: si persiste solo cio' che ha un lettore. I campi
    dell'autopsia servono a costruire l'aggregato, che viene calcolato nello stesso
    processo e salvato altrove; tenerli anche qui era spreco puro.

    La seconda: se anche cosi' si sfora, si tengono le coppie PASSATE (le uniche di
    cui il bot legge i parametri) e si dichiara quante se ne sono lasciate indietro.
    Un documento troncato in silenzio si leggerebbe come "il registro e' questo".
    """
    slim = {k: {f: v for f, v in e.items() if f in PARAM_DOC_FIELDS}
            for k, e in out.items()}
    if len(encode_pairs(slim).encode("utf-8")) <= max_bytes:
        return slim
    keep = {k: slim[k] for k in passed if k in slim}
    print(f"[optimize] documento parametri oltre {max_bytes} byte: persistite le "
          f"{len(keep)} coppie PASSATE su {len(slim)} valutate (le altre non hanno "
          f"lettori: la diagnosi sta in gate_autopsy, la storia nel registro)")
    return keep


def persist_params(fb, out: dict, passed: list) -> bool:
    """Salva i parametri per il bot. NON deve poter far fallire il run.

    entries/passed sono CODIFICATI come stringa JSON: Firestore indicizza UN campo
    invece di ogni sottocampo di ogni coppia (200 coin x 9 strategie sfondano il
    limite di 40k voci d'indice -> "INDEX_ENTRIES_COUNT_LIMIT_EXCEEDED").

    Se la scrittura fallisce comunque, si logga e si prosegue: il bot continuera' coi
    parametri precedenti — degradato, non fermo — mentre far cadere il processo qui
    significherebbe buttare ore di validazione gia' fatta.
    """
    try:
        fb.set_doc("strategy_params", "current", {
            "updated_at": time.time(),
            "entries": encode_pairs(slim_entries(out, passed)),
            "passed": encode_pairs(passed),
        })
        return True
    except Exception as exc:  # noqa: BLE001
        print(f"[optimize] parametri NON salvati ({str(exc)[:160]}). Il registro e "
              f"l'autopsia sono al sicuro; il bot resta sui parametri precedenti.")
        return False


# Cio' che serve alla CONTABILITA' del registro: senza questi campi si perdono i
# passaggi accumulati, cioe' settimane di attesa. Tutto il resto e' descrittivo.
REGISTRY_CORE_FIELDS = {"pass_count", "last_pass_data_end", "fail_count",
                        "symbol", "strategy", "last_seen_at", "last_params",
                        "scale_r_mults", "drift_seen_at",
                        # senza questi due la finestra di giudizio si riaprirebbe da
                        # capo a ogni alleggerimento, e i verdetti non arriverebbero mai
                        "window_start", "passed_in_window"}


def slim_registry(pairs: dict, validated: list,
                  max_bytes: int = PARAM_DOC_MAX_BYTES) -> str:
    """Il registro codificato, alleggerito SOLO se necessario.

    Il registro cresce con le coppie tracciate (1200 e oltre) e ognuna porta con se'
    holdout, PF per regime e metriche descrittive. E' lo stesso limite di 1 MiB che
    ha fatto cadere il documento dei parametri, e qui costerebbe molto di piu': in
    quel documento ci sono i PASSAGGI ACCUMULATI, cioe' settimane di attesa.

    Quando si sfora si tolgono i campi descrittivi alle coppie NON validate — non a
    quelle validate, che il bot e la dashboard leggono — e la contabilita' resta
    intatta per tutte. Se non basta ancora, meglio provarci comunque e lasciare che
    sia Firestore a rifiutare: troncare il registro significherebbe cancellare
    passaggi veri, e quello non e' un compromesso accettabile.
    """
    enc = encode_pairs(pairs)
    if len(enc.encode("utf-8")) <= max_bytes:
        return enc
    keep = set(validated)
    slim = {k: (r if k in keep else
                {f: v for f, v in r.items() if f in REGISTRY_CORE_FIELDS})
            for k, r in pairs.items()}
    enc2 = encode_pairs(slim)
    print(f"[registry] oltre {max_bytes} byte: tolti i campi descrittivi alle "
          f"{len(pairs) - len(keep)} coppie non validate "
          f"({len(enc.encode('utf-8'))} -> {len(enc2.encode('utf-8'))} byte). "
          f"I passaggi accumulati restano intatti.")
    return enc2


def autopsy(out: dict, top_near: int = 40) -> dict:
    """DOVE MUOIONO LE CANDIDATE. Il conto dei criteri che le fermano.

    Il gate rispondeva si'/no. Con oltre ventimila valutazioni per run questo
    significa ripetere ventimila esperimenti senza conservarne l'esito: se non
    passa niente non si sa se muoiono per pochi trade, per PF sotto i costi, per
    l'holdout o per la robustezza. E senza saperlo l'unica reazione possibile e'
    abbassare le soglie a caso — cioe' validare rumore.

    Due letture, diverse e complementari:
      * `binding` — il criterio messo PEGGIO per ciascuna candidata. Dice dove sta
        il collo di bottiglia dell'intera ricerca.
      * `involved` — quante volte ogni criterio compare, anche non da solo. Un
        criterio che appare quasi sempre e' una condizione strutturale del mercato
        su cui stiamo lavorando, non un filtro che seleziona.

    `near_misses` sono le candidate fermate da UN SOLO criterio e per poco: sono i
    semi da mutare al giro dopo. Cercare attorno a un quasi-passaggio e' una
    ricerca informata; estrarre nuove candidate a caso non lo e'.
    """
    from collections import Counter
    binding: Counter = Counter()
    involved: Counter = Counter()
    near: list[dict] = []
    passed = 0
    for key, e in out.items():
        if e.get("passed"):
            passed += 1
            continue
        crits = e.get("fail_criteria") or []
        if not crits:
            continue                       # non passata ma senza diagnosi: non inventarla
        binding[e.get("fail_binding") or "?"] += 1
        for c in crits:
            involved[c] += 1
        if e.get("near_miss"):
            near.append({"key": key, "binding": e.get("fail_binding"),
                         "shortfall": e.get("fail_shortfall"),
                         "pf": e.get("oos_pf"), "trades": e.get("oos_trades"),
                         "t_stat": e.get("t_stat")})
    near.sort(key=lambda n: -(n.get("shortfall") or -9))
    return {
        "updated_at": time.time(),
        "evaluated": len(out), "passed": passed,
        "diagnosed": int(sum(binding.values())),
        "binding": dict(binding.most_common()),
        "involved": dict(involved.most_common()),
        "near_misses": near[:top_near],
        "near_miss_count": len(near),
    }


def publish_autopsy(fb, out: dict) -> dict:
    """Scrive l'autopsia e la riassume a schermo. Best-effort: una diagnosi non
    salvata non deve far fallire un run di validazione."""
    rep = autopsy(out)
    try:
        fb.set_doc("gate_autopsy", "current", rep)
    except Exception as exc:  # noqa: BLE001
        print(f"[autopsy] non salvata ({exc})")
    if rep["diagnosed"]:
        top = " · ".join(f"{k} {v}" for k, v in list(rep["binding"].items())[:5])
        print(f"[autopsy] {rep['passed']}/{rep['evaluated']} passate · muoiono su: {top}")
        print(f"[autopsy] quasi-passaggi (un solo criterio, di poco): "
              f"{rep['near_miss_count']}")
    return rep


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


def judge_window(rec: dict, data_end: float, passed_now: bool,
                 min_new_data_s: float = NEW_DATA_MIN_S) -> dict:
    """UN VERDETTO PER FINESTRA, non per run. Modifica `rec` sul posto.

    IL DIFETTO CHE CORREGGE. Due regole giuste prese singolarmente, su orologi
    incompatibili: un pass conta solo dopo una settimana di dati nuovi, ma il purge
    scattava dopo due bocciature CONSECUTIVE, contate a ogni run. Col timer ogni tre
    ore, fra una conferma e la successiva passano 56 run: per sopravvivere una coppia
    avrebbe dovuto passare il gate ~28 volte in sette giorni, con un tasso misurato
    dello 0.027%. Nessuna ce la faceva. Il registro non poteva accumulare tre
    conferme PER COSTRUZIONE — ed e' il motivo per cui in tre settimane le validate
    sono sempre state zero, e per cui la popolazione a 1 pass si rinnovava
    completamente ogni pochi giorni invece di crescere.

    LA REGOLA ORA. La finestra e' l'unita' di evidenza:
      * passa almeno una volta nella finestra -> UNA conferma;
      * non passa mai in tutta la finestra    -> UN fallimento;
      * dentro la finestra non succede niente: rivalutare gli stessi dati non e'
        una prova nuova, ne' a favore ne' contro.

    Il pass onesto non serve piu' come controllo separato: e' la finestra stessa a
    garantire che due conferme distino una settimana di dati.

    NB il primo avvistamento e' un'eccezione voluta: una coppia che passa appena
    scoperta prende subito la sua prima conferma, come prima. Farle aspettare una
    settimana per il PRIMO pass ritarderebbe tutto senza aggiungere evidenza — non
    c'e' nessuna conferma precedente da cui distanziarsi.
    """
    # FAIL-CLOSED: senza data_end non si giudica. Nessun percorso deve poter
    # incrementare un contatore "gratis" dimenticando un campo.
    if data_end <= 0:
        return rec
    if passed_now:
        rec["passed_in_window"] = True

    start = float(rec.get("window_start", 0) or 0)
    if start <= 0:                      # nessuna finestra aperta: se ne apre una
        rec["window_start"] = data_end
        # La conferma immediata vale SOLO per una coppia mai vista prima. Una che ha
        # gia' dei passaggi ma non ha la finestra e' una coppia PRE-ESISTENTE alla
        # regola, incontrata per la prima volta dopo il cambio: darle un pass qui
        # sarebbe una conferma regalata, senza un solo dato nuovo — esattamente il
        # difetto che la finestra esiste per impedire, rientrato dalla porta della
        # migrazione. Le si apre la finestra e si aspetta come tutte le altre.
        if passed_now and int(rec.get("pass_count", 0) or 0) == 0:
            rec["pass_count"] = 1
            rec["last_pass_data_end"] = data_end
            rec["fail_count"] = 0
            rec["passed_in_window"] = False
        return rec

    if data_end - start < min_new_data_s:
        return rec                      # finestra ancora aperta: nessun verdetto

    if rec.get("passed_in_window"):
        rec["pass_count"] = int(rec.get("pass_count", 0) or 0) + 1
        rec["last_pass_data_end"] = data_end
        rec["fail_count"] = 0
    else:
        rec["fail_count"] = int(rec.get("fail_count", 0) or 0) + 1
    rec["window_start"] = data_end      # la finestra successiva parte da qui
    rec["passed_in_window"] = False
    return rec


# quanti punti di storia tenere: 240 punti a due passate ogni tre ore sono circa
# quindici giorni. Il documento resta sotto i 50 KB, molto lontano dal limite di
# 1 MiB che ci ha gia' fatto cadere un run da quattro ore.
TIMELINE_POINTS = int(os.getenv("GATE_TIMELINE_POINTS", "240"))


def publish_timeline(fb, pairs: dict, source: str,
                     evaluated: int = 0, passed: int = 0) -> None:
    """L'EVOLVERSI DELLE STRATEGIE, come serie storica.

    Il registro dice com'e' il mondo ADESSO: 2615 coppie, 224 a un passaggio, zero
    validate. Non dice se ieri erano 180 o 400, e quella e' l'unica differenza che
    conta — un fronte che cresce significa che la ricerca sta accumulando, uno che si
    rinnova ogni pochi giorni significa che le coppie entrano ed escono senza mai
    arrivare in fondo. E' esattamente il sintomo con cui si e' scoperto il difetto
    dei due orologi, e all'epoca lo si e' potuto vedere solo confrontando a mano
    schermate di giorni diversi.

    Un punto per passata, campi piccoli, coda tagliata: e' un grafico, non un
    archivio. Best-effort in ogni punto — la storia e' un di piu', non deve poter
    far fallire una validazione.
    """
    try:
        dist: dict[str, int] = {}
        for r in pairs.values():
            p = int(r.get("pass_count", 0) or 0)
            k = str(min(p, MIN_PASSES))          # tutto cio' che e' >= soglia e' "validata"
            dist[k] = dist.get(k, 0) + 1
        punto = {
            "at": round(time.time()),
            "src": source,
            "tracked": len(pairs),
            "dist": dist,
            "validated": dist.get(str(MIN_PASSES), 0),
            "evaluated": int(evaluated),
            "passed": int(passed),
        }
        doc = fb.get_doc("gate_history", "timeline") or {}
        punti = list(doc.get("points") or [])
        punti.append(punto)
        fb.set_doc("gate_history", "timeline", {
            "updated_at": time.time(),
            "min_passes": MIN_PASSES,
            "points": punti[-TIMELINE_POINTS:],
        })
    except Exception as exc:  # noqa: BLE001
        print(f"[timeline] non salvata ({exc})")


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
        # storia la promuove ancora: e' il paper ad avere l'ultima parola sul presente.
        #
        # MA IL CONTO RESTA QUELLO DELLA FINESTRA. Prima questo ramo saltava
        # `judge_window` e incrementava `fail_count` A OGNI RUN: col timer ogni tre ore
        # una coppia in deriva veniva purgata in SEI ORE, e la redenzione promessa dalla
        # docstring qui sopra ("se ripassa il gate su storia aggiornata il fail_count si
        # azzera") era irraggiungibile, perche' l'azzeramento avviene solo alla chiusura
        # di una finestra e la coppia non arrivava mai a vederne una. E' esattamente il
        # difetto dei due orologi che `judge_window` esiste per chiudere, rimasto vivo
        # su questo ramo. Ora la deriva fa cio' che deve: impedisce che LA FINESTRA
        # possa chiudersi con una conferma, e il verdetto arriva quando arriva per tutti.
        if key in drifted:
            rec["passed_in_window"] = False
            rec["drift_seen_at"] = time.time()
            judge_window(rec, float(e.get("data_end", 0) or 0), False)
            rec["symbol"], rec["strategy"] = e["symbol"], e["strategy"]
            rec["last_seen_at"] = time.time()
            pairs[key] = rec
            continue
        judge_window(rec, float(e.get("data_end", 0) or 0), key in passed_set)
        if key in passed_set:
            rec["last_params"] = e["params"]
            if e.get("holdout"):
                rec["holdout"] = e["holdout"]
            if e.get("regime_pf"):
                rec["regime_pf"] = e["regime_pf"]
            rec["last_pf"] = e["oos_pf"]
            rec["last_pnl_pct"] = e["oos_pnl_pct"]
            if e.get("oos_max_dd") is not None:
                rec["last_max_dd"] = e["oos_max_dd"]
            rec["last_trades"] = e["oos_trades"]
            rec["last_win_rate"] = e.get("oos_win_rate")
            tr = e.get("trailing") or {}
            rec["trailing_premature"] = tr.get("premature", 0)
            rec["trailing_protected"] = tr.get("protected", 0)
            rec["trailing_neutral"] = tr.get("neutral", 0)
            rec["last_passed_at"] = time.time()
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
    # PRONTI PER IL PAPER. La COPERTURA come criterio nasce da un'idea ragionevole
    # ("voglio poter operare su una fetta ampia del mercato") che pero' diventa
    # irraggiungibile quando il gate e' severo: se passa lo 0.75% delle coppie
    # valutate, chiedere il 35% dell'universo significa non partire mai.
    # READY_MIN_PAIRS e' la via alternativa: quello che serve davvero per iniziare
    # non e' coprire una percentuale del mercato, e' avere abbastanza strategie
    # validate da diversificare. Le due strade sono in OR, e i minimi assoluti
    # restano condizione necessaria in entrambi i casi.
    base_ok = universe >= MIN_UNIVERSE and len(covered) >= MIN_COVERED
    by_coverage = coverage >= READY_FRACTION
    by_count = READY_MIN_PAIRS > 0 and len(validated) >= READY_MIN_PAIRS
    ready = base_ok and (by_coverage or by_count)

    registry = {
        "updated_at": time.time(),
        "pairs": slim_registry(pairs, validated),
        "validated": validated,
        "coins_covered": len(covered),
        "coins": covered,
        "universe_size": universe,
        "universe_coins": current_coins,
        "coverage": round(coverage, 3),
        "ready": ready,
        "min_passes": MIN_PASSES,
        "ready_fraction": READY_FRACTION,
        "ready_min_pairs": READY_MIN_PAIRS,
        "ready_by": ("copertura" if by_coverage else "numero coppie") if ready else None,
        "min_universe": MIN_UNIVERSE,
        "min_covered": MIN_COVERED,
    }
    fb.set_doc("strategy_registry", "validated", registry)
    publish_timeline(fb, pairs, "optimize", len(out), len(passed_set))
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
