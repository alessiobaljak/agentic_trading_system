"""GLI SPIKE: chi li vede, chi li prende, e quanto se ne porta a casa.

Domanda a cui risponde: quando bitcoin fa +10% in un giorno — cosa che succede
regolarmente — le nostre strategie fanno qualcosa? E il backtest se ne accorge?

Non e' una domanda oziosa. Un movimento raro e grande e' il caso in cui il
comportamento del sistema diverge di piu' dalla sua media, ed e' anche quello che le
metriche aggregate nascondono meglio: un profit factor calcolato su seicento trade
non dice niente su cosa succede nei tre giorni che contano.

COSA MISURA, in ordine:

  1. GLI EVENTI. Ogni finestra di `--hours` ore in cui il prezzo si e' mosso di
     almeno `--soglia` (in valore assoluto: gli spike al ribasso contano quanto
     quelli al rialzo). Si tengono solo eventi separati, per non contare tre volte
     lo stesso movimento.

  2. CHI ERA ACCESO. Ogni strategia dichiara in quali regimi opera. Uno spike alza
     l'ATR e fa scattare HIGH_UNCERTAINTY, dove momentum, trend_following e
     momentum_cross_asset sono SPENTE per costruzione. Questo passaggio lo rende
     visibile invece che deducibile leggendo il codice.

  3. IL REGIME, CALCOLATO IN DUE MODI. Il bot dal vivo classifica il mercato
     guardando SOLO bitcoin e applica quell'etichetta a tutte le coin
     (`refresh_regime` in bot/main.py). Il backtest lo calcola per ogni coin sui
     dati della coin stessa. Sono due cose diverse e possono dare regimi diversi
     sulla stessa barra — cioe' strategie accese nel gate e spente dal vivo, o
     viceversa. Qui si contano le barre in cui le due letture NON coincidono.

  4. I TRADE DENTRO L'EVENTO. Quanti se ne aprono, in che direzione, con che esito.

  5. QUANTI FINISCONO PER SCADENZA. Il motore chiude d'ufficio dopo 96 barre (24
     ore a 15m). Se un trade aperto su uno spike arriva quasi sempre a quel limite,
     il backtest sta TAGLIANDO la continuazione, e il numero che produce e' un
     limite inferiore di cio' che la strategia avrebbe fatto.

  6. QUANTO PESANO. Frazione del profitto totale del periodo che arriva dai trade
     aperti durante uno spike. Se e' alta, il gate — che con `pf_ex_top` toglie il
     5% di trade migliori e pretende che il resto regga — sta selezionando CONTRO
     proprio queste strategie.

Uso (sul VPS, dove c'e' la rete verso gli exchange):
    .venv/bin/python -m scripts.spike_response
    .venv/bin/python -m scripts.spike_response --soglia 0.08 --symbols BTCUSDT,ETHUSDT
"""
from __future__ import annotations

import argparse
import os
from collections import Counter, defaultdict

from backtesting.data_loader import load_candles
from backtesting.engine import HORIZON_BARS, Backtester
from bot.agents.regime_detector import RegimeDetector
from bot.config import settings, timeframe_hours
from bot.core.indicators import compute_indicator_frame
from bot.core.models import Candle


def trova_spike(candles: list[Candle], soglia: float, barre: int) -> list[dict]:
    """Finestre di `barre` barre con movimento >= soglia in valore assoluto.

    Si scorre in avanti e, trovato un evento, si SALTA oltre la sua fine: altrimenti
    un rialzo lungo due giorni verrebbe contato una volta per ogni barra, e la
    statistica direbbe "centinaia di spike" quando ce n'e' stato uno.
    """
    out: list[dict] = []
    i = 0
    n = len(candles)
    while i + barre < n:
        a, b = candles[i].close, candles[i + barre].close
        if a <= 0:
            i += 1
            continue
        var = (b - a) / a
        if abs(var) >= soglia:
            out.append({"i": i, "fine": i + barre, "var": var,
                        "quando": candles[i].open_time})
            i += barre                      # niente doppi conteggi
        else:
            i += 1
    return out


def analizza(symbol: str, candles: list[Candle], btc: list[Candle],
             args) -> dict:
    ore = timeframe_hours(args.interval)
    barre = max(1, int(round(args.hours / ore)))
    eventi = trova_spike(candles, args.soglia, barre)
    if not eventi:
        return {"symbol": symbol, "eventi": 0}

    bt = Backtester(window=200, interval_hours=ore)
    frame = compute_indicator_frame(candles)
    snaps, regimi = bt._prepared(symbol, frame, candles)

    # IL REGIME COME LO VEDE IL BOT DAL VIVO: da bitcoin, per tutti. Si allinea per
    # timestamp perche' le serie possono avere lunghezze diverse (coin quotate dopo).
    rd = RegimeDetector()
    reg_btc: dict = {}
    if btc:
        bframe = compute_indicator_frame(btc)
        bsnaps, _ = bt._prepared("BTCUSDT", bframe, btc)
        for s, c in zip(bsnaps, btc):
            reg_btc[c.open_time] = rd.detect(s)

    # --- 1) chi era acceso, e le due letture del regime concordano? ------------ #
    acceso: Counter = Counter()
    regime_evento: Counter = Counter()
    discordi = confrontate = 0
    for e in eventi:
        j = min(e["fine"], len(regimi) - 1)
        if j < 0:
            continue
        r = regimi[j]
        regime_evento[r.value] += 1
        for s in bt.strategies:
            if s.is_active_in(r):
                acceso[s.name] += 1
        rb = reg_btc.get(candles[j].open_time)
        if rb is not None:
            confrontate += 1
            if rb != r:
                discordi += 1

    # --- 2) i trade dentro gli eventi ----------------------------------------- #
    finestre = [(e["i"], min(e["fine"] + barre, len(candles) - 1)) for e in eventi]

    def dentro(idx: int) -> bool:
        return any(a <= idx <= b for a, b in finestre)

    per_strategia: dict = defaultdict(lambda: {"trade": 0, "pnl": 0.0, "vinti": 0,
                                               "scaduti": 0})
    tot_pnl = tot_pnl_spike = 0.0
    orizzonte = HORIZON_BARS   # il taglio d'ufficio del motore
    for s in bt.strategies:
        st = bt.run_strategy(s, symbol, candles, frame=frame)
        for t in st.trades:
            tot_pnl += t.pnl_pct
            # indice della barra d'ingresso, dal timestamp registrato nel trade
            idx = int((t.entry_ts - candles[0].open_time.timestamp()) / (ore * 3600))
            if not dentro(idx):
                continue
            r = per_strategia[s.name]
            r["trade"] += 1
            r["pnl"] += t.pnl_pct
            r["vinti"] += int(t.is_win)
            tot_pnl_spike += t.pnl_pct
            # SCADUTO = chiuso d'ufficio all'orizzonte invece che per stop o target.
            # Non e' un dettaglio: se i trade sugli spike scadono quasi sempre, il
            # backtest sta TRONCANDO la continuazione del movimento, e il numero che
            # produce e' un limite inferiore di cio' che la strategia avrebbe fatto.
            if int(getattr(t, "bars_held", 0) or 0) >= orizzonte:
                r["scaduti"] += 1

    # COPERTURA: che frazione della serie sta dentro una finestra di evento. Senza
    # questo numero la percentuale qui sotto puo' saturare senza che si veda: se gli
    # eventi coprono quasi tutto, "il 100% del profitto arriva dagli spike" e' una
    # tautologia — tutti i trade sono dentro un evento — e non dice piu' niente sulla
    # concentrazione. E' il tipo di conclusione che sembra un risultato ed e' un
    # artefatto della soglia scelta.
    coperte = len({i for a, b in finestre for i in range(a, b + 1)})
    return {
        "symbol": symbol, "eventi": len(eventi),
        "copertura": coperte / max(1, len(candles)),
        "primo": eventi[0]["quando"], "ultimo": eventi[-1]["quando"],
        "regime_evento": dict(regime_evento.most_common()),
        "acceso": dict(acceso.most_common()),
        "discordi": discordi, "confrontate": confrontate,
        "per_strategia": {k: v for k, v in per_strategia.items() if v["trade"]},
        "tot_pnl": tot_pnl, "tot_pnl_spike": tot_pnl_spike,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default="BTCUSDT,ETHUSDT,SOLUSDT")
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--soglia", type=float, default=0.10,
                    help="movimento minimo, in frazione (0.10 = 10%%)")
    ap.add_argument("--hours", type=float, default=24.0,
                    help="in quante ore dev'essere avvenuto")
    ap.add_argument("--source", default="binance")
    args = ap.parse_args()

    simboli = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    os.environ.setdefault("BACKTEST_ALLOW_SYNTHETIC", "false")

    btc = load_candles("BTCUSDT", args.interval, args.start, None,
                       prefer=args.source, allow_synthetic=False)
    if not btc:
        print("[spike] nessuna fonte dati raggiungibile: non invento numeri, mi fermo")
        return 1

    print(f"[spike] soglia {args.soglia * 100:.0f}% in {args.hours:.0f}h · "
          f"timeframe {args.interval} · da {args.start}")
    print(f"[spike] ORIZZONTE del motore: {HORIZON_BARS} barre "
          f"({HORIZON_BARS * timeframe_hours(args.interval):.0f}h) — oltre, il trade "
          f"e' chiuso d'ufficio\n")

    for sym in simboli:
        candles = btc if sym == "BTCUSDT" else load_candles(
            sym, args.interval, args.start, None, prefer=args.source,
            allow_synthetic=False)
        if len(candles) < 500:
            print(f"[spike] {sym}: storia insufficiente, salto")
            continue
        r = analizza(sym, candles, btc, args)
        print(f"=== {sym} ===")
        if not r["eventi"]:
            print("  nessuno spike sopra soglia nel periodo\n")
            continue
        print(f"  eventi: {r['eventi']} (dal {r['primo']:%d %b %Y} al {r['ultimo']:%d %b %Y})")
        print("  regime al momento dello spike: " +
              " · ".join(f"{k} {v}" for k, v in r["regime_evento"].items()))

        # CHI ERA SPENTO e' l'informazione piu' importante: dice che il sistema non
        # aveva nemmeno la possibilita' di rispondere.
        tutte = {s.name for s in Backtester(window=200).strategies}
        spente = sorted(tutte - set(r["acceso"]))
        if spente:
            print(f"  MAI ACCESE durante gli spike: {', '.join(spente)}")
        print("  accese (su quanti eventi): " +
              " · ".join(f"{k} {v}/{r['eventi']}" for k, v in r["acceso"].items()))

        if r["confrontate"]:
            pct = r["discordi"] / r["confrontate"] * 100
            print(f"  REGIME GATE vs LIVE: discordano su {r['discordi']}/"
                  f"{r['confrontate']} eventi ({pct:.0f}%). Il gate usa il regime "
                  f"della coin, il bot dal vivo quello di bitcoin per tutte.")

        if not r["per_strategia"]:
            print("  TRADE APERTI DURANTE GLI SPIKE: nessuno.\n")
            continue
        print("  trade aperti durante gli spike:")
        for k, v in sorted(r["per_strategia"].items(), key=lambda kv: -kv[1]["pnl"]):
            wr = v["vinti"] / v["trade"] * 100
            print(f"    {k:<22} {v['trade']:>4} trade · {v['pnl'] * 100:>+7.1f}% · "
                  f"win {wr:>4.0f}% · {v['scaduti']} chiusi per scadenza")
        cop = float(r.get("copertura") or 0) * 100
        if r["tot_pnl"]:
            q = r["tot_pnl_spike"] / r["tot_pnl"] * 100
            print(f"  QUANTO PESANO: {q:.0f}% del profitto totale del periodo arriva "
                  f"da questi trade,\n  che coprono il {cop:.0f}% delle barre.")
            if cop > 50:
                print(f"    -> ATTENZIONE: con gli eventi che coprono il {cop:.0f}% "
                      f"della serie, la percentuale\n       qui sopra non misura la "
                      f"concentrazione — misura la soglia scelta. Rilanciare\n"
                      f"       con --soglia piu' alta o --hours piu' corto prima di "
                      f"concluderne qualcosa.")
            elif q > 30:
                print("    -> sopra il 30% con una copertura bassa: il profitto e' "
                      "davvero concentrato\n       negli eventi, e il gate — che con "
                      "pf_ex_top toglie il 5% di trade migliori\n       e pretende che "
                      "il resto regga — sta selezionando CONTRO queste strategie.")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
