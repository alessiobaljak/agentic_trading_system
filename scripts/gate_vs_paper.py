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
"""
from __future__ import annotations

import argparse
from datetime import date

from backtesting.data_loader import load_candles
from backtesting.engine import StrategyStats, max_drawdown
from backtesting.optimizer import WalkForwardOptimizer
from bot.config import settings
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
    ap.add_argument("--symbol", required=True)
    ap.add_argument("--strategy", required=True, help="es. gen_472f85b8 oppure breakout")
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
    args = ap.parse_args()

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
