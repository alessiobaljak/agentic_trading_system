"""GATE vs PAPER sulla STESSA coppia: da dove arrivano i profitti, e si ripetono?

Il gate promette un PF sulla storia; il paper misura il presente. Quando i due
divergono la domanda non e' "quanto" ma "DOVE": sotto scale-out il profitto non
e' distribuito uniformemente sui vincitori — un trade che si ferma al primo
gradino incassa una briciola (0.3 x 1.5R = 0.45R lordi, residuo a break-even),
mentre uno che corre fino all'ultimo ne incassa 3.35R. Il conto lo fa la CODA.

Questo script mette le due distribuzioni di `mfe_r` una accanto all'altra e
ripartisce il PnL per fascia, cosi' si vede se la coda del backtest esiste anche
nel vissuto o se e' li' che il vantaggio evapora.

SOLA LETTURA: legge la spec e i trade da Firestore e non scrive NULLA. In
particolare NON chiama update_registry — rieseguire `scripts.optimize` su un solo
simbolo ricalcolerebbe la copertura su un universo di 1 coin e corromperebbe il
registro.

Uso (sul VPS):
    .venv/bin/python -m scripts.gate_vs_paper --symbol BIRBUSDT --strategy gen_472f85b8
    .venv/bin/python -m scripts.gate_vs_paper --symbol BIRBUSDT --strategy gen_472f85b8 --ladder 1,2,3
    .venv/bin/python -m scripts.gate_vs_paper --symbol X --strategy Y --entry-timing

MODALITA' REPLAY (confronto trade-per-trade sul periodo davvero operato):
    .venv/bin/python -m scripts.gate_vs_paper --trades-file trades_backup_20260811.json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict
from datetime import date
from statistics import median

from backtesting.data_loader import load_candles
from backtesting.engine import StrategyStats, max_drawdown
from backtesting.optimizer import WalkForwardOptimizer
from bot.config import settings, timeframe_hours
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.execution.exit_logic import ladder_multiples
from bot.learning.trade_logger import TradeLogger
from bot.strategies.base import get_all_strategies
from bot.strategies.generated import GeneratedStrategy

REACH = (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0)


def _bucket_labels(mults: tuple) -> list[str]:
    """Fasce di arrivo del prezzo, dal primo gradino all'ultimo."""
    out = [f"< {mults[0]:g}R (nessun gradino)"]
    for a, b in zip(mults, mults[1:]):
        out.append(f"{a:g}R–{b:g}R")
    out.append(f">= {mults[-1]:g}R (corsa piena)")
    return out


def _bucket_of(mfe: float, mults: tuple) -> int:
    for i, m in enumerate(mults):
        if mfe < m:
            return i
    return len(mults)


def _distribution(name: str, mfes: list[float]) -> None:
    if not mfes:
        print(f"{name:<26}  nessun trade")
        return
    s = sorted(mfes)
    med = s[len(s) // 2]
    line = f"{name:<26}{len(s):>5}{med:>9.2f}"
    for r in REACH:
        line += f"{sum(1 for v in s if v >= r) / len(s) * 100:>6.0f}%"
    print(line)


def _contribution(name: str, rows: list[tuple[float, float]], mults: tuple) -> None:
    """Ripartisce trade e PnL per fascia di mfe: mostra QUALE fascia fa il risultato.

    rows = [(mfe_r, pnl_in_unita_omogenee)]. Le unita' non devono coincidere tra
    gate e paper (il gate somma variazioni di prezzo, il paper USDT): qui conta la
    quota percentuale, che e' confrontabile.
    """
    if not rows:
        return
    labels = _bucket_labels(mults)
    n = len(labels)
    cnt = [0] * n
    pnl = [0.0] * n
    for mfe, p in rows:
        b = _bucket_of(mfe, mults)
        cnt[b] += 1
        pnl[b] += p
    tot_pnl = sum(pnl)
    tot_n = sum(cnt)
    print(f"\n{name} — chi fa il risultato (fasce sulla scala {'/'.join(f'{m:g}' for m in mults)}):")
    print(f"  {'fascia':<26}{'trade':>7}{'% trade':>9}{'PnL':>12}{'% del PnL':>11}")
    for i, lab in enumerate(labels):
        if not cnt[i]:
            continue
        # quota sul TOTALE NETTO: >100% significa che quella fascia da' sola piu'
        # del risultato finale, e le altre lo erodono. E' il caso interessante.
        quota = (pnl[i] / tot_pnl * 100) if abs(tot_pnl) > 1e-12 else float("nan")
        print(f"  {lab:<26}{cnt[i]:>7}{cnt[i] / tot_n * 100:>8.0f}%{pnl[i]:>12.3f}{quota:>10.0f}%")
    print(f"  {'TOTALE':<26}{tot_n:>7}{100:>8.0f}%{tot_pnl:>12.3f}{100:>10.0f}%")


# ---------------------------------------------------------------------------- #
# MODALITA' REPLAY — il confronto trade-per-trade richiesto dalla Fase 1.1      #
# ---------------------------------------------------------------------------- #
def _ts(value) -> float:
    """Epoch da un campo temporale del trade (ISO string o numero)."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return dt.datetime.fromisoformat(str(value)).timestamp()
    except (TypeError, ValueError):
        return 0.0


def _match(paper: list[dict], sim: list, tol_s: float) -> list[tuple]:
    """Accoppia ogni trade PAPER col segnale del GATE piu' vicino nel tempo.

    Ogni segnale del gate puo' essere usato una volta sola: senza questo vincolo
    piu' trade paper vicini fra loro si accopperebbero tutti allo stesso segnale e
    il conteggio dei "non accoppiati" perderebbe significato. Ritorna coppie
    (trade_paper, trade_gate|None) — il None e' un risultato, non un errore: dice
    che in quel momento il gate NON aveva un segnale.
    """
    used: set = set()
    out = []
    for p in sorted(paper, key=lambda t: _ts(t.get("entry_time"))):
        pt = _ts(p.get("entry_time"))
        best, best_d = None, None
        for idx, s in enumerate(sim):
            if idx in used:
                continue
            d = abs(float(getattr(s, "entry_ts", 0.0)) - pt)
            if d <= tol_s and (best_d is None or d < best_d):
                best, best_d = idx, d
        if best is None:
            out.append((p, None))
        else:
            used.add(best)
            out.append((p, sim[best]))
    return out


def _price_move(t: dict) -> float:
    """Variazione di PREZZO del trade paper, con segno per la direzione.

    E' la grandezza confrontabile col `pnl_pct` del gate, che e' anch'esso una
    variazione di prezzo senza leva. Il `pnl_pct` del ClosedTrade invece e' il
    ritorno sul MARGINE (leva inclusa): stesso nome, semantica diversa.
    """
    e, x = float(t.get("entry_price") or 0), float(t.get("exit_price") or 0)
    if e <= 0:
        return 0.0
    sign = -1.0 if str(t.get("direction", "")).lower() == "short" else 1.0
    return (x - e) / e * sign


def _replay_pair(key: str, ptrades: list[dict], args, specs: dict, pairs: dict) -> dict | None:
    """Rigira il GATE sulla finestra di calendario in cui il paper ha operato."""
    symbol, strategy = key.split("|", 1)
    t_in = [_ts(t.get("entry_time")) for t in ptrades if _ts(t.get("entry_time")) > 0]
    t_out = [_ts(t.get("exit_time")) for t in ptrades if _ts(t.get("exit_time")) > 0]
    if not t_in:
        return None
    tf_h = timeframe_hours(args.interval)
    # warmup: il motore ha bisogno di ~200 barre prima di poter emettere segnali,
    # altrimenti la finestra del paper resterebbe scoperta all'inizio.
    warm_s = 260 * tf_h * 3600
    start = dt.datetime.fromtimestamp(min(t_in) - warm_s, dt.timezone.utc).date().isoformat()
    end = dt.datetime.fromtimestamp(max(t_out or t_in) + 86400, dt.timezone.utc).date().isoformat()

    spec = specs.get(strategy)
    ladder = ladder_multiples((pairs.get(key) or {}).get("last_params") or {})

    def make():
        if spec is not None:
            g = GeneratedStrategy(spec)
            if ladder:
                g.params = {**(getattr(g, "params", {}) or {}), "scale_r_mults": list(ladder)}
            return g
        for s in get_all_strategies():
            if s.name == strategy:
                return s
        return None

    if make() is None:
        # Le spec generate vengono POTATE dal registro quando la coppia non passa
        # piu': se la coppia e' stata purgata, la sua definizione non esiste piu' e
        # il replay e' impossibile. Non e' un errore dello script — e' un dato che
        # non c'e', e va detto invece di essere aggirato indovinando i parametri.
        return {"key": key, "n_paper": len(ptrades),
                "skip": "definizione della strategia non piu' nel registro"}

    # MAI dati sintetici qui: se Binance non risponde, un backtest su serie
    # inventate produrrebbe un confronto dall'aria plausibile e privo di senso —
    # il modo peggiore di sbagliare, perche' non si vede.
    candles = load_candles(symbol, args.interval, start, end, prefer=args.source,
                           allow_synthetic=False)
    if len(candles) < 260:
        return {"key": key, "n_paper": len(ptrades), "skip": f"solo {len(candles)} candele"}
    frame = compute_indicator_frame(candles)
    opt = WalkForwardOptimizer(n_windows=1, interval=args.interval)
    # barre in cui il gate puo' DAVVERO emettere segnali: il motore ne consuma
    # `window` per il warmup degli indicatori. Con una finestra troppo corta uno
    # zero non significa "il gate non vedeva niente", significa "non ho guardato".
    usable = len(candles) - opt.bt.window
    if usable < 50:
        return {"key": key, "n_paper": len(ptrades),
                "skip": f"finestra troppo corta ({usable} barre dopo il warmup)"}
    st = opt.bt.run_strategy(make(), symbol, candles, frame=frame)
    lo, hi = min(t_in), max(t_out or t_in)
    sim = [s for s in st.trades if lo - tf_h * 3600 <= float(getattr(s, "entry_ts", 0)) <= hi]

    matched = _match(ptrades, sim, tol_s=2 * tf_h * 3600)
    both = [(p, s) for p, s in matched if s is not None]
    return {
        "key": key, "n_paper": len(ptrades), "n_gate": len(sim),
        "n_matched": len(both), "skip": None, "usable_bars": usable,
        "n_mfe_paper": sum(1 for p in ptrades if p.get("mfe_r") is not None),
        "d_entry": [abs(float(s.entry_price) - float(p["entry_price"]))
                    / float(p["entry_price"]) * 100
                    for p, s in both if float(p.get("entry_price") or 0) > 0],
        "d_time": [abs(float(s.entry_ts) - _ts(p.get("entry_time"))) for p, s in both],
        "mfe_paper": [float(p["mfe_r"]) for p in ptrades if p.get("mfe_r") is not None],
        "mfe_gate": [float(s.mfe_r) for s in sim],
        "move_paper": [_price_move(p) for p in ptrades],
        "move_gate": [float(s.pnl_pct) for s in sim],
    }


def _replay_report(rows: list[dict]) -> None:
    ok = [r for r in rows if not r.get("skip")]
    print("\n" + "=" * 96)
    print("CONFRONTO PAPER vs GATE sulla STESSA finestra di calendario")
    print("=" * 96)
    hdr = (f"{'coppia':<34}{'paper':>7}{'gate':>6}{'match':>7}"
           f"{'Δprezzo':>10}{'Δtempo':>10}{'mfe pap':>9}{'mfe gate':>10}")
    print(hdr)
    print("-" * len(hdr))
    for r in sorted(rows, key=lambda x: -x["n_paper"]):
        if r.get("skip"):
            print(f"{r['key'][:33]:<34}{r['n_paper']:>7}   —      —   [{r['skip']}]")
            continue
        de = f"{median(r['d_entry']):.3f}%" if r["d_entry"] else "—"
        dtm = f"{median(r['d_time']) / 60:.0f}m" if r["d_time"] else "—"
        mp = f"{median(r['mfe_paper']):.2f}R" if r["mfe_paper"] else "—"
        mg = f"{median(r['mfe_gate']):.2f}R" if r["mfe_gate"] else "—"
        print(f"{r['key'][:33]:<34}{r['n_paper']:>7}{r['n_gate']:>6}{r['n_matched']:>7}"
              f"{de:>10}{dtm:>10}{mp:>9}{mg:>10}")

    skipped = [r for r in rows if r.get("skip")]
    if skipped:
        from collections import Counter
        print(f"\nNON confrontabili: {len(skipped)}/{len(rows)} coppie "
              f"({sum(r['n_paper'] for r in skipped)} trade paper su "
              f"{sum(r['n_paper'] for r in rows)})")
        for motivo, n in Counter(r["skip"] for r in skipped).most_common():
            print(f"  · {n} coppie: {motivo}")
    if not ok:
        print("\nNessuna coppia confrontabile: il confronto Fase 1.1 non e'"
              "\neseguibile su questi dati. Non e' un risultato negativo, e' un"
              "\ndato mancante — vedi i motivi qui sopra.")
        return
    zero = [r for r in ok if r["n_gate"] == 0]
    if zero:
        print(f"\nATTENZIONE: su {len(zero)} coppie il gate non ha prodotto alcun"
              " segnale nella finestra.\n  Con finestre corte "
              f"({min(r['usable_bars'] for r in zero)}-"
              f"{max(r['usable_bars'] for r in zero)} barre utili) e parametri "
              "non piu' nel registro,\n  uno zero NON dimostra una divergenza di "
              "generazione: dimostra che il\n  campione non basta a dirlo.")
    tot_p = sum(r["n_paper"] for r in ok)
    tot_g = sum(r["n_gate"] for r in ok)
    tot_m = sum(r["n_matched"] for r in ok)
    d_entry = [x for r in ok for x in r["d_entry"]]
    d_time = [x for r in ok for x in r["d_time"]]
    mp = [x for r in ok for x in r["mfe_paper"]]
    mg = [x for r in ok for x in r["mfe_gate"]]
    vp = [x for r in ok for x in r["move_paper"]]
    vg = [x for r in ok for x in r["move_gate"]]

    print("\n--- TABELLA METRICA (aggregato) ---")
    print(f"{'METRICA':<34}{'PAPER':>14}{'GATE':>14}{'DELTA':>14}")
    def row(name, a, b, decimals=3, suffix=""):
        """Riga PAPER | GATE | DELTA. Il segno va messo nella format spec del
        NUMERO: applicarlo a una stringa gia' formattata solleva ValueError."""
        sa = f"{a:.{decimals}f}{suffix}" if a is not None else "—"
        sb = f"{b:.{decimals}f}{suffix}" if b is not None else "—"
        sd = (f"{b - a:+.{decimals}f}{suffix}"
              if (a is not None and b is not None) else "—")
        print(f"{name:<34}{sa:>14}{sb:>14}{sd:>14}")
    row("trade / segnali nella finestra", tot_p, tot_g, 0)
    row("mfe_r mediana", median(mp) if mp else None, median(mg) if mg else None,
        2, "R")
    row("variazione prezzo media", (sum(vp) / len(vp) * 100) if vp else None,
        (sum(vg) / len(vg) * 100) if vg else None, 3, "%")
    print(f"{'accoppiati (±2 barre)':<34}{tot_m:>14}{'':>14}"
          f"{f'{tot_m / tot_p * 100:.0f}% del paper' if tot_p else '—':>14}")
    if d_entry:
        print(f"{'scarto prezzo di ingresso':<34}{'':>14}{'':>14}"
              f"{f'mediana {median(d_entry):.3f}%':>14}")
    if d_time:
        print(f"{'scarto istante di ingresso':<34}{'':>14}{'':>14}"
              f"{f'mediana {median(d_time) / 60:.0f} min':>14}")

    print("\nCome si legge:")
    print("  · 'gate' molto > 'paper': il bot ha eseguito solo una parte dei segnali")
    print("    (margine esaurito, guardie di portafoglio, coppia non ancora validata).")
    print("  · pochi 'accoppiati': il paper ha operato quando il gate NON aveva un")
    print("    segnale — divergenza di GENERAZIONE, la piu' grave.")
    print("  · Δprezzo e Δtempo grandi: divergenza di ESECUZIONE (timing/fill).")
    print("  · mfe simili ma esiti diversi: divergenza nelle USCITE.")
    print("  · mfe del paper molto sotto quella del gate: nessuna delle tre — e' il")
    print("    mercato che non ha ripetuto la coda su cui il gate era stato validato.")


def _replay_mode(args) -> int:
    try:
        with open(args.trades_file, encoding="utf-8") as fh:
            trades = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[gvp] non riesco a leggere {args.trades_file}: {exc}")
        return 1
    if not isinstance(trades, list) or not trades:
        print(f"[gvp] {args.trades_file} non contiene una lista di trade")
        return 1

    by_pair: dict[str, list] = defaultdict(list)
    for t in trades:
        if isinstance(t, dict) and t.get("symbol") and t.get("strategy"):
            by_pair[f"{t['symbol']}|{t['strategy']}"].append(t)
    todo = {k: v for k, v in by_pair.items() if len(v) >= args.min_trades}
    print(f"[gvp] {len(trades)} trade · {len(by_pair)} coppie · "
          f"{len(todo)} con almeno {args.min_trades} trade")
    if not todo:
        print(f"[gvp] nessuna coppia sopra soglia: prova --min-trades 1")
        return 1

    fb = get_firebase()
    specs = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
    pairs = decode_pairs((fb.get_doc("strategy_registry", "validated") or {}).get("pairs"))
    # distingue "le spec non ci sono piu'" da "le sto cercando male": senza questa
    # riga un replay a vuoto sembra un bug dello script invece che un dato perso.
    wanted = {k.split("|", 1)[1] for k in todo if k.split("|", 1)[1].startswith("gen_")}
    print(f"[gvp] registro: {len(pairs)} coppie · spec generate disponibili: "
          f"{len(specs)} · servono per questo replay: {len(wanted)} "
          f"(presenti {len(wanted & set(specs))})")

    rows = []
    for i, (key, ts) in enumerate(sorted(todo.items(), key=lambda kv: -len(kv[1])), 1):
        print(f"[gvp] ({i}/{len(todo)}) {key} · {len(ts)} trade paper...")
        try:
            r = _replay_pair(key, ts, args, specs, pairs)
        except Exception as exc:  # noqa: BLE001
            r = {"key": key, "n_paper": len(ts), "skip": f"{type(exc).__name__}: {exc}"}
        if r:
            rows.append(r)
    _replay_report(rows)
    return 0


def _entry_timing_report(base: StrategyStats, rerun, strategy: str) -> None:
    """Quanto costa entrare al primo prezzo ESEGUIBILE invece che alla chiusura.

    Il segnale nasce alla chiusura della barra, ma il bot puo' eseguire solo dopo:
    conosce quella chiusura a barra chiusa, decide al confine dell'orologio e manda
    l'ordine al mark di quel momento. Il gate invece entra al prezzo di chiusura,
    che nessuno avrebbe potuto ottenere. Qui si rigirano le STESSE finestre con
    l'ingresso all'apertura della barra successiva e si misura la differenza.

    E' l'unica delle sei cause di disparita' ipotizzate dal prompt che sopravvive
    alla verifica: indicatori, costi, funding e uscite sono moduli condivisi.
    """
    from statistics import mean, median

    prev = settings.BACKTEST_ENTRY_NEXT_OPEN
    settings.BACKTEST_ENTRY_NEXT_OPEN = True
    try:
        shifted = rerun()
    finally:
        settings.BACKTEST_ENTRY_NEXT_OPEN = prev

    print("\n=== TIMING D'INGRESSO: chiusura barra vs apertura successiva ===")
    hdr = f"{'':22}{'n':>6}{'PF':>9}{'ritorno':>11}{'win':>7}{'per trade':>12}"
    print(hdr)
    print("-" * len(hdr))
    for name, st in (("entra al close(T)", base), ("entra a open(T+1)", shifted)):
        n = len(st.trades)
        per = (st.total_pnl_pct() / n * 100) if n else 0.0
        print(f"{name:22}{n:>6}{st.profit_factor():>9.3f}"
              f"{st.total_pnl_pct() * 100:>10.1f}%{st.win_rate() * 100:>6.0f}%{per:>11.3f}%")

    nb, ns = len(base.trades), len(shifted.trades)
    if not nb or not ns:
        print("  (campione vuoto: niente da confrontare)")
        return
    d_per = (shifted.total_pnl_pct() / ns - base.total_pnl_pct() / nb) * 100
    print(f"\n  DELTA per trade: {d_per:+.3f}%  ·  PF {base.profit_factor():.3f} -> "
          f"{shifted.profit_factor():.3f}")

    # scarto sui singoli ingressi: dice quanto si muove il prezzo fra la chiusura
    # e l'apertura dopo. Su crypto (mercato continuo) e' piccolo, ma non zero.
    pairs_ = [(b.entry_price, s.entry_price)
              for b, s in zip(base.trades, shifted.trades)]
    gaps = [abs(s - b) / b * 100 for b, s in pairs_ if b]
    if gaps:
        print(f"  scarto |open(T+1) - close(T)|: mediana {median(gaps):.4f}% · "
              f"media {mean(gaps):.4f}% · max {max(gaps):.3f}%")
    print("  [se il DELTA e' trascurabile, il timing NON spiega la disparita' e la"
          "\n   causa resta la selezione statistica; se e' grande, va corretto"
          "\n   attivando BACKTEST_ENTRY_NEXT_OPEN e RIVALIDANDO il registro.]")


def _build_strategy(fb, strategy: str, ladder):
    """La strategia ESATTA che il gate ha validato, con la scala della coppia."""
    if strategy.startswith("gen_"):
        specs = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
        spec = specs.get(strategy)
        if spec is None:
            raise SystemExit(f"[gvp] spec {strategy} non trovata in discovered_strategies/specs")
        print(f"[gvp] spec: features={[f.get('kind') for f in spec.get('features', [])]} "
              f"atr_mult_stop={spec.get('atr_mult_stop')} rr={spec.get('rr')} "
              f"min_adx={spec.get('min_adx')} volume_mult={spec.get('volume_mult')}")

        def make():
            g = GeneratedStrategy(spec)
            if ladder:
                g.params = {**(getattr(g, "params", {}) or {}), "scale_r_mults": list(ladder)}
            return g
        return make

    def make():
        for s in get_all_strategies({strategy: {"scale_r_mults": list(ladder)}} if ladder else None):
            if s.name == strategy:
                return s
        raise SystemExit(f"[gvp] strategia base {strategy} non trovata")
    return make


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", help="es. BIRBUSDT (non serve in modalita' replay)")
    ap.add_argument("--strategy", help="es. gen_472f85b8 oppure breakout")
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--end", default=None)
    ap.add_argument("--windows", type=int, default=3)
    ap.add_argument("--source", default="binance")
    ap.add_argument("--ladder", default=None,
                    help="scala di TP in R, es. 1.5,3,5. Default: quella del registro")
    ap.add_argument("--entry-timing", action="store_true",
                    help="misura l'effetto del timing d'ingresso: rigira le stesse "
                         "finestre entrando all'apertura della barra DOPO il segnale "
                         "(cioe' al primo prezzo eseguibile) e confronta")
    ap.add_argument("--trades-file",
                    help="MODALITA' REPLAY: file JSON di trade paper (export di "
                         "reset_paper). Rigira il gate sulla stessa finestra di "
                         "calendario e confronta trade per trade. Ignora --symbol")
    ap.add_argument("--min-trades", type=int, default=2,
                    help="modalita' replay: coppie con meno trade non vengono girate")
    args = ap.parse_args()

    if args.trades_file:
        return _replay_mode(args)
    if not args.symbol or not args.strategy:
        ap.error("servono --symbol e --strategy (oppure --trades-file)")

    fb = get_firebase()
    key = f"{args.symbol}|{args.strategy}"
    pairs = decode_pairs((fb.get_doc("strategy_registry", "validated") or {}).get("pairs"))
    rec = pairs.get(key) or {}

    if args.ladder:
        ladder = tuple(float(x) for x in args.ladder.split(","))
    else:
        # ladder_multiples -> None per le coppie senza scala nei params: quelle
        # operano (e sono state validate) con il default globale.
        ladder = tuple(ladder_multiples(rec.get("last_params") or {})
                       or settings.SCALE_OUT_R_MULTIPLES)
    print(f"[gvp] {key} · scala TP {'/'.join(f'{m:g}' for m in ladder)} "
          f"· quote {tuple(settings.SCALE_OUT_FRACTIONS)}")
    if rec:
        print(f"[gvp] registro: PF {rec.get('last_pf')} · {rec.get('last_trades')} trade "
              f"· win {float(rec.get('last_win_rate') or 0) * 100:.0f}% "
              f"· pnl {float(rec.get('last_pnl_pct') or 0) * 100:+.1f}% "
              f"· pass {rec.get('pass_count')}")

    make = _build_strategy(fb, args.strategy, ladder)

    end = args.end or date.today().isoformat()
    candles = load_candles(args.symbol, args.interval, args.start, end, prefer=args.source)
    if not candles:
        raise SystemExit("[gvp] nessuna candela caricata (Binance raggiungibile?)")
    print(f"[gvp] candele: {len(candles)} da {candles[0].open_time:%Y-%m-%d} "
          f"a {candles[-1].open_time:%Y-%m-%d}")

    frame = compute_indicator_frame(candles)
    opt = WalkForwardOptimizer(n_windows=args.windows, interval=args.interval)
    body, cut = opt.split_holdout(candles)

    def _oos_run() -> StrategyStats:
        """Le stesse finestre OOS su cui la coppia e' stata promossa."""
        st_all = StrategyStats(strategy=args.strategy)
        for (_ta, _tb, sa, sb) in opt._windows(len(body)):
            st = opt.bt.run_strategy(make(), args.symbol, body[sa:sb],
                                     frame=frame.iloc[sa:sb].reset_index(drop=True))
            st_all.trades.extend(st.trades)
        return st_all

    # --- GATE ------------------------------------------------------------------
    oos = _oos_run()

    # --- TIMING D'INGRESSO: quanto costa entrare al primo prezzo ESEGUIBILE? ----
    if args.entry_timing:
        _entry_timing_report(oos, _oos_run, args.strategy)

    # --- HOLDOUT: mai visto dalla selezione ------------------------------------
    hold = StrategyStats(strategy=args.strategy)
    if cut < len(candles):
        st = opt.bt.run_strategy(make(), args.symbol, candles[cut:],
                                 frame=frame.iloc[cut:].reset_index(drop=True))
        hold.trades.extend(st.trades)

    # --- PAPER: i trade davvero eseguiti ---------------------------------------
    paper = [t for t in TradeLogger(fb).all_since(0.0)
             if t.get("symbol") == args.symbol and t.get("strategy") == args.strategy
             and t.get("mfe_r") is not None]

    head = f"{'sorgente':<26}{'n':>5}{'mediana':>9}" + "".join(f"{'>=%gR' % r:>6}" for r in REACH)
    print("\n" + head)
    print("-" * len(head))
    _distribution("GATE finestre OOS", [t.mfe_r for t in oos.trades])
    _distribution("GATE holdout", [t.mfe_r for t in hold.trades])
    _distribution("PAPER (vissuto)", [float(t["mfe_r"]) for t in paper])

    if oos.trades:
        print(f"\nGATE OOS: PF {oos.profit_factor():.3f} · win {oos.win_rate() * 100:.0f}% "
              f"· ritorno {oos.total_pnl_pct() * 100:+.1f}% · maxDD {max_drawdown(oos.trades) * 100:.1f}%")
    if hold.trades:
        print(f"GATE holdout: PF {hold.profit_factor():.3f} · win {hold.win_rate() * 100:.0f}% "
              f"· ritorno {hold.total_pnl_pct() * 100:+.1f}%")
    if paper:
        pnl = sum(float(t.get("pnl", 0) or 0) for t in paper)
        wins = sum(1 for t in paper if float(t.get("pnl", 0) or 0) > 0)
        print(f"PAPER: {len(paper)} trade · win {wins / len(paper) * 100:.0f}% · PnL {pnl:+.2f} USDT")

    _contribution("GATE finestre OOS", [(t.mfe_r, t.pnl_pct) for t in oos.trades], ladder)
    _contribution("GATE holdout", [(t.mfe_r, t.pnl_pct) for t in hold.trades], ladder)
    _contribution("PAPER (vissuto)",
                  [(float(t["mfe_r"]), float(t.get("pnl", 0) or 0)) for t in paper], ladder)

    print("\nCome si legge: se nel GATE la fascia di CODA (l'ultima) porta la quota"
          "\ndominante del PnL e nel PAPER quella fascia e' vuota, il vantaggio"
          "\nvalidato non si sta ripetendo — e nessuna scala di TP puo' recuperarlo,"
          "\nperche' il prezzo non ci arriva. Campioni piccoli non decidono: guarda n.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
