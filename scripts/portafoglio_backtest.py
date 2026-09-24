"""BACKTEST DI PORTAFOGLIO: le coppie validate INSIEME, sugli ultimi N giorni.

24 settembre 2026. Il gate valida una coppia (coin + strategia) alla volta, con
10.000$ fissi e il conto vuoto; il paper e' il primo posto in cui le ~59 coppie
validate girano insieme, con i limiti veri (5 posizioni, una per coin, il
cooldown, il tetto per coin al giorno). Le domande che il gate non puo' vedere
per costruzione:

  * quanti trade al giorno fa il portafoglio, e quante posizioni tiene aperte
    nello stesso momento;
  * quante di quelle spingono nella STESSA direzione (il 21 set tre short in
    fila hanno fatto -1,74% in quaranta minuti: backlog E4);
  * che giornate fa sommando tutto: quante in utile, quante in perdita, il
    drawdown della curva;
  * e cosa cambierebbe un TETTO DI RISCHIO PER DIREZIONE: la somma del rischio
    aperto sui long (o sugli short) non oltre una frazione dell'equity.

COME FA. Per ogni coin validata carica le candele una volta sola, rigira ogni
strategia validata su quella coin con i parametri del registro (`last_params`:
scala dei TP, breakeven), come farebbe il gate, e tiene i trade entrati negli
ultimi N giorni. Poi tutti i trade di tutte le coppie passano, in ordine di
tempo, da un conto solo (`bot/risk/portafoglio.simula`) — DUE volte: senza
tetto per direzione (com'era) e col tetto. La differenza fra le due e' il
what-if.

COSA NON E'. Non e' il paper: i trade sono quelli del backtest (uscita a barra
chiusa, costi modellati), e il rischio per trade e' l'1% dell'equity senza le
riduzioni per confidenza. Non e' un gate: non promuove e non boccia niente.
Si saltano, dicendolo: le strategie BASE (non generate: i loro parametri non
stanno nel registro delle spec), le spec con un timeframe diverso da quello
richiesto (caricare le loro candele raddoppierebbe il tempo, e il bot opera
comunque a ORCHESTRATOR_TIMEFRAME), le coin con poche candele.

SOLA LETTURA sul registro. Pubblica un riepilogo compatto in
`portfolio/backtest` (senza curva) in fail-open: se Firebase non c'e', il
report resta a schermo e il codice d'uscita non cambia.

Uso:
    .venv/bin/python -m scripts.portafoglio_backtest
    .venv/bin/python -m scripts.portafoglio_backtest --giorni 30 --tetto-direzione 0.02
"""
from __future__ import annotations

import argparse
import datetime as dt
import math
from collections import defaultdict

from backtesting.data_loader import load_candles
from backtesting.optimizer import WalkForwardOptimizer
from bot.config import settings, timeframe_hours
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.risk.portafoglio import MOTIVI, limiti_default, simula
from bot.strategies.generated import GeneratedStrategy
from scripts.optimize import coppie_validate

#: barre che il motore consuma prima di poter emettere segnali (window=200), con
#: un margine: lo stesso numero di gate_vs_paper, per non inventarne un altro.
WARMUP_BARRE = 260

#: sotto queste candele la coin non si rigira: sarebbe quasi tutto warmup
MIN_CANDELE = WARMUP_BARRE + 50


def _giorni_di_warmup(interval: str) -> int:
    return int(math.ceil(WARMUP_BARRE * timeframe_hours(interval) / 24.0)) + 1


def trade_in_dict(t, symbol: str, strategy: str) -> dict:
    """Da SimTrade al dict che `simula` legge. `stop_pct` sta in `feats` (dal
    24 set): senza, il trade verra' scartato e contato, non indovinato."""
    feats = getattr(t, "feats", None) or {}
    return {
        "symbol": symbol, "strategy": strategy,
        "direction": str(getattr(t, "direction", "long") or "long"),
        "entry_ts": float(getattr(t, "entry_ts", 0) or 0),
        "bars_held": int(getattr(t, "bars_held", 0) or 0),
        "pnl_pct": float(getattr(t, "pnl_pct", 0.0) or 0.0),
        "stop_pct": feats.get("stop_pct"),
    }


def trades_della_coin(symbol: str, strategie: list[tuple[str, dict]], specs: dict,
                      args, inizio_ts: float, bt) -> tuple[list[dict], list[tuple[str, str]], int]:
    """Rigira tutte le strategie validate su UNA coin, con le candele caricate
    una volta sola. Ritorna (trade dal giorno `inizio_ts`, coppie saltate con
    motivo, numero di candele)."""
    saltate: list[tuple[str, str]] = []
    da_fare: list[tuple[str, GeneratedStrategy]] = []
    for strategy, rec in strategie:
        if not strategy.startswith("gen_"):
            saltate.append((strategy, "strategia base, non generata"))
            continue
        spec = specs.get(strategy)
        if not isinstance(spec, dict):
            saltate.append((strategy, "spec non piu' nel registro"))
            continue
        tf = spec.get("timeframe") or settings.ORCHESTRATOR_TIMEFRAME
        if tf != args.interval:
            saltate.append((strategy, f"timeframe {tf}, richiesto {args.interval}"))
            continue
        g = GeneratedStrategy(spec)
        # i parametri CON CUI la coppia e' stata validata (scala TP, breakeven):
        # senza, si rigirerebbe una strategia diversa da quella che il bot opera.
        g.params = {**(getattr(g, "params", {}) or {}), **(rec.get("last_params") or {})}
        da_fare.append((strategy, g))
    if not da_fare:
        return [], saltate, 0

    giorni = args.giorni + _giorni_di_warmup(args.interval)
    oggi = dt.datetime.now(dt.timezone.utc).date()
    start = (oggi - dt.timedelta(days=giorni)).isoformat()
    # MAI dati sintetici: un portafoglio misurato su prezzi inventati avrebbe
    # l'aria di una risposta e sarebbe rumore.
    candles = load_candles(symbol, args.interval, start, oggi.isoformat(),
                           prefer=args.source, allow_synthetic=False)
    if len(candles) < MIN_CANDELE:
        return [], saltate + [(s, f"solo {len(candles)} candele") for s, _ in da_fare], len(candles)
    frame = compute_indicator_frame(candles)
    trades: list[dict] = []
    for strategy, g in da_fare:
        st = bt.run_strategy(g, symbol, candles, frame=frame)
        trades.extend(trade_in_dict(t, symbol, strategy) for t in st.trades
                      if float(getattr(t, "entry_ts", 0) or 0) >= inizio_ts)
    return trades, saltate, len(candles)


# --------------------------------------------------------------------------- #
# STAMPA                                                                       #
# --------------------------------------------------------------------------- #
def _riga(nome: str, a, b, fmt: str = "{}") -> None:
    print(f"  {nome:<34}{fmt.format(a):>16}{fmt.format(b):>16}")


def stampa_tabella(senza: dict, con: dict, tetto: float) -> None:
    print(f"  {'':<34}{'senza tetto':>16}{f'tetto {tetto * 100:.0f}%/dir':>16}")
    print("  " + "-" * 66)
    _riga("trade aperti", senza["n_aperti"], con["n_aperti"])
    for m in MOTIVI:
        if senza["saltati"].get(m) or con["saltati"].get(m):
            _riga(f"  saltati: {m}", senza["saltati"].get(m, 0), con["saltati"].get(m, 0))
    _riga("  di cui short fermati dal tetto", senza["saltati_direzione"]["short"],
          con["saltati_direzione"]["short"])
    _riga("  di cui long fermati dal tetto", senza["saltati_direzione"]["long"],
          con["saltati_direzione"]["long"])
    _riga("trade al giorno (min/media/max)",
          _tag(senza["trade_al_giorno"]), _tag(con["trade_al_giorno"]))
    _riga("posizioni contemporanee (max/media)",
          _pc(senza["posizioni_contemporanee"]), _pc(con["posizioni_contemporanee"]))
    _riga("stessa direzione, max contemporanee",
          senza["stessa_direzione_max"], con["stessa_direzione_max"])
    _riga("quota altre aperte, stessa direzione",
          senza["quota_contemporanee_stessa_direzione"],
          con["quota_contemporanee_stessa_direzione"], "{:.0%}")
    _riga("long: n / PnL", _dirz(senza["per_direzione"]["long"]),
          _dirz(con["per_direzione"]["long"]))
    _riga("short: n / PnL", _dirz(senza["per_direzione"]["short"]),
          _dirz(con["per_direzione"]["short"]))
    _riga("giorni in utile / in perdita",
          f"{senza['giorni_utile']} / {senza['giorni_perdita']}",
          f"{con['giorni_utile']} / {con['giorni_perdita']}")
    _riga("PnL totale", senza["pnl_totale"], con["pnl_totale"], "{:+.2f}")
    _riga("equity finale", senza["equity_finale"], con["equity_finale"], "{:.2f}")
    _riga("max drawdown", senza["max_drawdown_pct"], con["max_drawdown_pct"], "{:.2f}%")


def _tag(d: dict) -> str:
    return f"{d['min']}/{d['media']:.1f}/{d['max']}"


def _pc(d: dict) -> str:
    return f"{d['max']}/{d['media']:.1f}"


def _dirz(d: dict) -> str:
    return f"{d['n']} / {d['pnl']:+.0f}"


def giorni_peggiori(senza: dict, con: dict, n: int = 5) -> list[tuple[str, float, float]]:
    """I giorni peggiori del portafoglio SENZA tetto, con accanto lo stesso
    giorno col tetto: e' il confronto che dice se il tetto avrebbe tolto le
    giornate brutte o solo limato le altre."""
    peggiori = sorted(senza["pnl_per_giorno"].items(), key=lambda kv: kv[1])[:n]
    return [(g, v, con["pnl_per_giorno"].get(g, 0.0)) for g, v in peggiori]


def lettura(senza: dict, con: dict, tetto: float) -> str:
    """Una riga in parole semplici: cosa fa il tetto e cosa costa."""
    if tetto <= 0:
        return "tetto per direzione spento: le due simulazioni coincidono."
    fermati = con["saltati"]["tetto_direzione"]
    s, l = con["saltati_direzione"]["short"], con["saltati_direzione"]["long"]
    if not fermati:
        return (f"con il tetto del {tetto * 100:.0f}% per direzione non si salta "
                f"nessun trade: negli ultimi giorni il portafoglio non e' mai "
                f"arrivato a {senza['stessa_direzione_max']} posizioni nella stessa "
                f"direzione col rischio pieno, quindi il tetto non cambia niente.")
    return (f"con il tetto del {tetto * 100:.0f}% per direzione si saltano {fermati} "
            f"trade ({s} short, {l} long); il PnL passa da {senza['pnl_totale']:+.0f} "
            f"a {con['pnl_totale']:+.0f}, il drawdown da {senza['max_drawdown_pct']:.2f}% "
            f"a {con['max_drawdown_pct']:.2f}%, le posizioni contemporanee nella stessa "
            f"direzione da {senza['stessa_direzione_max']} a {con['stessa_direzione_max']}.")


def riepilogo_compatto(sim: dict) -> dict:
    """Per Firebase: tutto tranne la curva e il PnL giorno per giorno (che sono
    la parte pesante e si rigenerano lanciando il comando)."""
    fuori = {k: v for k, v in sim.items() if k not in ("curva", "pnl_per_giorno", "limiti")}
    fuori["giorni_peggiori"] = sorted(sim["pnl_per_giorno"].items(), key=lambda kv: kv[1])[:5]
    return fuori


def pubblica(fb, doc: dict) -> None:
    try:
        if not fb.is_live:
            print("\n[firebase] non connesso: report solo a schermo.")
            return
        fb.set_doc("portfolio", "backtest", doc)
        print("\n[firebase] pubblicato portfolio/backtest.")
    except Exception as exc:  # noqa: BLE001 — la pubblicazione non deve mai rompere il report
        print(f"\n[firebase] pubblicazione saltata ({exc}).")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="le coppie validate insieme sugli ultimi N giorni, con e senza tetto per direzione")
    ap.add_argument("--giorni", type=int, default=60)
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--tetto-direzione", type=float,
                    default=limiti_default()["tetto_direzione"],
                    help="frazione dell'equity di rischio aperto per direzione (0 = spento)")
    ap.add_argument("--source", default="auto")
    ap.add_argument("--equity", type=float, default=10_000.0,
                    help="equity di partenza (default: i 10.000$ del gate)")
    args = ap.parse_args(argv)

    fb = get_firebase()
    pairs = decode_pairs((fb.get_doc("strategy_registry", "validated") or {}).get("pairs"))
    validate = coppie_validate(pairs)
    if not validate:
        print("[portafoglio] il registro delle coppie validate e' vuoto: niente da simulare.")
        return 0
    specs = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))

    per_coin: dict[str, list[tuple[str, dict]]] = defaultdict(list)
    for key in validate:
        sym, _, strat = key.partition("|")
        per_coin[sym].append((strat, pairs.get(key) or {}))

    ora = dt.datetime.now(dt.timezone.utc)
    inizio_ts = (ora - dt.timedelta(days=args.giorni)).replace(
        hour=0, minute=0, second=0, microsecond=0).timestamp()
    limiti = limiti_default()
    print("=" * 74)
    print(f"PORTAFOGLIO: {len(validate)} coppie validate su {len(per_coin)} coin, "
          f"ultimi {args.giorni} giorni a {args.interval}")
    print(f"  limiti del bot: max {limiti['max_posizioni']} posizioni · una per coin · "
          f"tetto coin/giorno {limiti['tetto_coin_giorno'] * 100:.1f}% · "
          f"cooldown {limiti['cooldown_ore']:.2f} h · rischio {limiti['rischio_per_trade'] * 100:.0f}%/trade")
    print("=" * 74)

    bt = WalkForwardOptimizer(n_windows=1, interval=args.interval).bt
    trades: list[dict] = []
    saltate: list[tuple[str, str]] = []
    n_simulate = 0
    for i, sym in enumerate(sorted(per_coin), 1):
        try:
            tr, sk, n_c = trades_della_coin(sym, per_coin[sym], specs, args, inizio_ts, bt)
        except Exception as exc:  # noqa: BLE001 — una coin rotta non deve fermare le altre
            sk, tr, n_c = [(s, f"errore: {exc}") for s, _ in per_coin[sym]], [], 0
        fatte = len(per_coin[sym]) - len(sk)
        n_simulate += fatte
        saltate.extend((f"{sym}|{s}", m) for s, m in sk)
        trades.extend(tr)
        print(f"  [{i:>2}/{len(per_coin)}] {sym:<14} {n_c:>6} candele · "
              f"{fatte} strategie · {len(tr):>4} trade", flush=True)

    print(f"\ncoppie simulate {n_simulate} · saltate {len(saltate)} · "
          f"trade candidati {len(trades)}")
    for key, m in saltate:
        print(f"    saltata {key}: {m}")
    if not trades:
        print("[portafoglio] nessun trade negli ultimi giorni: niente da simulare.")
        return 0

    secondi_barra = timeframe_hours(args.interval) * 3600.0
    periodo = (inizio_ts, ora.timestamp())
    senza = simula(trades, args.equity, {**limiti, "tetto_direzione": 0.0},
                   secondi_barra=secondi_barra, periodo=periodo)
    con = simula(trades, args.equity, {**limiti, "tetto_direzione": args.tetto_direzione},
                 secondi_barra=secondi_barra, periodo=periodo)

    print("\n" + "=" * 74)
    print("LE COPPIE INSIEME, IN ORDINE DI TEMPO: senza e con tetto per direzione")
    print("=" * 74)
    stampa_tabella(senza, con, args.tetto_direzione)

    print("\n  i 5 giorni peggiori (senza tetto → con tetto)")
    for g, v, v2 in giorni_peggiori(senza, con):
        print(f"    {g}  {v:>+9.2f}  →  {v2:>+9.2f}")

    print(f"\nLettura: {lettura(senza, con, args.tetto_direzione)}")

    pubblica(fb, {
        "updated_at": ora.isoformat(),
        "giorni": args.giorni, "interval": args.interval, "equity0": args.equity,
        "coppie_simulate": n_simulate, "coppie_saltate": len(saltate),
        "n_trade": len(trades), "tetto_direzione": args.tetto_direzione,
        "limiti": limiti,
        "senza_tetto": riepilogo_compatto(senza),
        "con_tetto": riepilogo_compatto(con),
        "lettura": lettura(senza, con, args.tetto_direzione),
        "nota": "backtest, non paper: rischio 1%/trade fisso, trade del motore",
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
