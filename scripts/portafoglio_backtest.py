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
  * e cosa cambierebbero TRE limiti di portafoglio, accesi uno sull'altro: il
    tetto di rischio per direzione (quello che il bot ha gia',
    MAX_DIRECTIONAL_RISK_PCT), uno stop giornaliero di portafoglio e un tetto
    al netto direzionale in R (questi due il bot NON li ha: sono what-if).

COME FA. Per ogni coin validata carica le candele una volta sola, rigira ogni
strategia validata su quella coin con i parametri del registro (`last_params`:
scala dei TP, breakeven), come farebbe il gate, e tiene i trade entrati negli
ultimi N giorni. Poi tutti i trade di tutte le coppie passano, in ordine di
tempo, da un conto solo (`bot/risk/portafoglio.simula`) — QUATTRO volte, con i
limiti cumulativi: senza limiti extra · tetto direzione · + stop giornaliero ·
+ netto in R. La differenza fra le colonne e' il what-if di ogni limite.

Stampa anche due misure che servono a decidere, non a limitare: il win rate
dopo k perdite di fila per strategia (il freno di serie ha senso?) e il
diversification ratio delle giornate (il portafoglio e' una scommessa sola?).

COSA NON E'. Non e' il paper: i trade sono quelli del backtest (uscita a barra
chiusa, costi modellati), e il rischio per trade e' l'1% dell'equity senza le
riduzioni per confidenza. Non e' un gate: non promuove e non boccia niente.
Si saltano, dicendolo: le strategie BASE (non generate: i loro parametri non
stanno nel registro delle spec), le spec con un timeframe diverso da quello
richiesto (caricare le loro candele raddoppierebbe il tempo, e il bot opera
comunque a ORCHESTRATOR_TIMEFRAME), le coin con poche candele.

SOLA LETTURA sul registro. Pubblica un riepilogo compatto in
`portfolio/backtest` (senza curva) in fail-open: se Firebase non c'e', il
report resta a schermo e il codice d'uscita non cambia. Il riepilogo non deve
contenere liste dentro liste: Firestore le rifiuta («invalid nested entity»,
ops/results/0184 del 24 set, quando i giorni peggiori erano tuple).

Uso:
    .venv/bin/python -m scripts.portafoglio_backtest
    .venv/bin/python -m scripts.portafoglio_backtest --giorni 30 --tetto-direzione 0.02
    .venv/bin/python -m scripts.portafoglio_backtest --dal 2026-09-16   # dall'inizio del paper
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

#: le quattro colonne del what-if, nell'ordine in cui i limiti si accendono
#: (cumulativi: ogni colonna ha anche i limiti delle precedenti)
COLONNE = ("senza_extra", "tetto_direzione", "piu_stop_giorno", "piu_netto_r")


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
LARGO = 15  # larghezza di ogni colonna numerica


def _riga(nome: str, valori: list, fmt: str = "{}") -> None:
    print(f"  {nome:<36}" + "".join(f"{fmt.format(v):>{LARGO}}" for v in valori))


def stampa_tabella(sims: list[dict], intestazioni: list[str]) -> None:
    """Una riga per misura, una colonna per scenario (quattro, cumulativi)."""
    print(f"  {'':<36}" + "".join(f"{h:>{LARGO}}" for h in intestazioni))
    print("  " + "-" * (36 + LARGO * len(sims)))
    _riga("trade aperti", [s["n_aperti"] for s in sims])
    for m in MOTIVI:
        if any(s["saltati"].get(m) for s in sims):
            _riga(f"  saltati: {m}", [s["saltati"].get(m, 0) for s in sims])
    _riga("  di cui short fermati dal tetto dir.", [s["saltati_direzione"]["short"] for s in sims])
    _riga("  di cui long fermati dal tetto dir.", [s["saltati_direzione"]["long"] for s in sims])
    _riga("  giorni fermati dallo stop giorno", [s["giorni_fermati"] for s in sims])
    _riga("trade al giorno (min/media/max)", [_tag(s["trade_al_giorno"]) for s in sims])
    _riga("posizioni contemporanee (max/media)",
          [_pc(s["posizioni_contemporanee"]) for s in sims])
    _riga("stessa direzione, max contemporanee", [s["stessa_direzione_max"] for s in sims])
    _riga("quota altre aperte, stessa direzione",
          [s["quota_contemporanee_stessa_direzione"] for s in sims], "{:.0%}")
    _riga("long: n / PnL", [_dirz(s["per_direzione"]["long"]) for s in sims])
    _riga("short: n / PnL", [_dirz(s["per_direzione"]["short"]) for s in sims])
    _riga("giorni in utile / in perdita",
          [f"{s['giorni_utile']} / {s['giorni_perdita']}" for s in sims])
    _riga("diversification ratio", [_dr(s["diversification_ratio"]) for s in sims])
    _riga("PnL totale", [s["pnl_totale"] for s in sims], "{:+.2f}")
    _riga("equity finale", [s["equity_finale"] for s in sims], "{:.2f}")
    _riga("max drawdown", [s["max_drawdown_pct"] for s in sims], "{:.2f}%")


def _tag(d: dict) -> str:
    return f"{d['min']}/{d['media']:.1f}/{d['max']}"


def _pc(d: dict) -> str:
    return f"{d['max']}/{d['media']:.1f}"


def _dirz(d: dict) -> str:
    return f"{d['n']} / {d['pnl']:+.0f}"


def _dr(v) -> str:
    return "n.d." if v is None else f"{v:.2f}"


def giorni_peggiori(sims: list[dict], n: int = 5) -> list[dict]:
    """I giorni peggiori del portafoglio SENZA limiti extra (la prima
    simulazione), con accanto lo stesso giorno in ogni altra colonna: e' il
    confronto che dice se un limite avrebbe tolto le giornate brutte o solo
    limato le altre. Dict per riga, non tuple: Firestore rifiuta le liste
    annidate (24 set)."""
    base = sims[0]
    peggiori = sorted(base["pnl_per_giorno"].items(), key=lambda kv: kv[1])[:n]
    return [{"giorno": g, "pnl": v,
             "altri": [s["pnl_per_giorno"].get(g, 0.0) for s in sims[1:]]}
            for g, v in peggiori]


def stampa_wr_condizionato(sim: dict) -> None:
    """La domanda: dopo k perdite di fila la strategia vince meno? Se no, il
    freno di serie (4 perdite -> size a meta') non ha un fondamento nei dati."""
    wc = sim["wr_condizionato"]
    inc = wc["incondizionato"]
    print(f"\n  win rate dopo k perdite di fila (per strategia, sui {inc['n']} trade "
          f"candidati; incondizionato {inc['wr']:.1%})")
    print(f"  {'k':>3}{'n':>8}{'WR':>9}{'diff':>10}{'t':>8}")
    for k, d in wc["dopo_k"].items():
        print(f"  {k:>3}{d['n']:>8}{d['wr']:>9.1%}{d['diff_punti']:>+9.1f}p{d['t']:>8.2f}")
    d4 = wc["dopo_k"].get("4", {"n": 0, "wr": 0.0, "t": 0.0})
    print(f"  dopo 4 perdite: WR {d4['wr']:.1%} su {d4['n']} "
          f"(incondizionato {inc['wr']:.1%}, t {d4['t']:.2f})")


def lettura_diversification(sim: dict) -> str:
    dr = sim["diversification_ratio"]
    if dr is None:
        return "diversification ratio non definito (meno di due giorni o coppie piatte)."
    n = sim["n_coppie_aperte"]
    if dr >= 0.8:
        giudizio = "le coppie si muovono quasi insieme: e' quasi una scommessa sola"
    elif dr >= 0.5:
        giudizio = "le coppie si compensano in parte"
    else:
        giudizio = "le coppie si compensano molto fra loro"
    return (f"diversification ratio {dr:.2f} su {n} coppie che hanno chiuso trade "
            f"(1 = una scommessa sola, 0 = si annullano): {giudizio}.")


def lettura(sims: list[dict], nomi: list[str]) -> str:
    """Una riga in parole semplici per ogni limite acceso: cosa fa e cosa costa,
    rispetto alla colonna prima (i limiti sono cumulativi)."""
    frasi = []
    for prima, dopo, nome in zip(sims, sims[1:], nomi[1:]):
        fermati = prima["n_aperti"] - dopo["n_aperti"]
        if fermati <= 0:
            frasi.append(f"{nome}: non salta nessun trade in piu', non cambia niente")
            continue
        frasi.append(
            f"{nome}: salta {fermati} trade in piu'; il PnL passa da "
            f"{prima['pnl_totale']:+.0f} a {dopo['pnl_totale']:+.0f}, il drawdown da "
            f"{prima['max_drawdown_pct']:.2f}% a {dopo['max_drawdown_pct']:.2f}%")
    return "; ".join(frasi) + "." if frasi else "un solo scenario: niente da confrontare."


def contiene_liste_annidate(v, dentro_lista: bool = False) -> bool:
    """True se da qualche parte c'e' una lista (o tupla) dentro una lista, anche
    passando da un dict: e' quello che Firestore rifiuta come «nested entity»
    (ops/results/0184). Ricorsiva, cosi' il controllo vale per tutto il doc."""
    if isinstance(v, (list, tuple)):
        if dentro_lista:
            return True
        return any(contiene_liste_annidate(x, True) for x in v)
    if isinstance(v, dict):
        return any(contiene_liste_annidate(x, dentro_lista) for x in v.values())
    return False


def riepilogo_compatto(sim: dict) -> dict:
    """Per Firebase: tutto tranne la curva e il PnL giorno per giorno (che sono
    la parte pesante e si rigenerano lanciando il comando). I giorni peggiori
    sono dict {giorno, pnl}, non tuple: una lista di tuple e' una lista di
    liste per Firestore, che la rifiutava e il doc non si pubblicava mai (24
    set)."""
    fuori = {k: v for k, v in sim.items() if k not in ("curva", "pnl_per_giorno", "limiti")}
    fuori["giorni_peggiori"] = [
        {"giorno": g, "pnl": v}
        for g, v in sorted(sim["pnl_per_giorno"].items(), key=lambda kv: kv[1])[:5]]
    return fuori


def pubblica(fb, doc: dict) -> None:
    try:
        if contiene_liste_annidate(doc):
            print("\n[firebase] riepilogo con liste annidate: non lo pubblico (Firestore lo rifiuta).")
            return
        if not fb.is_live:
            print("\n[firebase] non connesso: report solo a schermo.")
            return
        fb.set_doc("portfolio", "backtest", doc)
        print("\n[firebase] pubblicato portfolio/backtest.")
    except Exception as exc:  # noqa: BLE001 — la pubblicazione non deve mai rompere il report
        print(f"\n[firebase] pubblicazione saltata ({exc}).")


def _data(s: str) -> dt.date:
    try:
        return dt.date.fromisoformat(s)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"data non valida {s!r}: serve YYYY-MM-DD") from exc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="le coppie validate insieme sugli ultimi N giorni, con i limiti di "
                    "portafoglio accesi uno sull'altro (direzione, stop giorno, netto in R)")
    quando = ap.add_mutually_exclusive_group()
    quando.add_argument("--giorni", type=int, default=None,
                        help="ultimi N giorni (default 60)")
    quando.add_argument("--dal", type=_data, default=None,
                        help="dal giorno YYYY-MM-DD (es. 2026-09-16, inizio del paper) a oggi; "
                             "stampa anche il PnL giorno per giorno")
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--tetto-direzione", type=float,
                    default=limiti_default()["tetto_direzione"],
                    help="frazione dell'equity di rischio aperto per direzione, nuovo trade "
                         "compreso (0 = spento)")
    ap.add_argument("--tetto-giorno", type=float, default=0.03,
                    help="perdita di portafoglio nel giorno UTC, frazione dell'equity di "
                         "inizio giornata, oltre cui non si apre piu' (0 = spento)")
    ap.add_argument("--netto-r", type=float, default=2.0,
                    help="massimo |rischio long - rischio short| aperto, in multipli del "
                         "rischio per trade (0 = spento)")
    ap.add_argument("--source", default="auto")
    ap.add_argument("--equity", type=float, default=10_000.0,
                    help="equity di partenza (default: i 10.000$ del gate)")
    args = ap.parse_args(argv)

    ora = dt.datetime.now(dt.timezone.utc)
    if args.dal is not None:
        # --dal: dal giorno dato a oggi, cosi' si confronta col paper giorno per giorno
        args.giorni = max((ora.date() - args.dal).days, 1)
        inizio_ts = dt.datetime.combine(args.dal, dt.time(), dt.timezone.utc).timestamp()
    else:
        if args.giorni is None:
            args.giorni = 60
        inizio_ts = (ora - dt.timedelta(days=args.giorni)).replace(
            hour=0, minute=0, second=0, microsecond=0).timestamp()

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

    limiti = limiti_default()
    print("=" * 74)
    print(f"PORTAFOGLIO: {len(validate)} coppie validate su {len(per_coin)} coin, "
          f"dal {dt.datetime.fromtimestamp(inizio_ts, dt.timezone.utc).date()} "
          f"({args.giorni} giorni) a {args.interval}")
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
    # i quattro scenari, cumulativi: ogni colonna aggiunge un limite alla precedente
    scenari = [
        {**limiti, "tetto_direzione": 0.0, "tetto_giorno": 0.0, "netto_r_max": 0.0},
        {**limiti, "tetto_direzione": args.tetto_direzione, "tetto_giorno": 0.0, "netto_r_max": 0.0},
        {**limiti, "tetto_direzione": args.tetto_direzione, "tetto_giorno": args.tetto_giorno,
         "netto_r_max": 0.0},
        {**limiti, "tetto_direzione": args.tetto_direzione, "tetto_giorno": args.tetto_giorno,
         "netto_r_max": args.netto_r},
    ]
    intestazioni = ["senza limiti", f"tetto dir {args.tetto_direzione * 100:.0f}%",
                    f"+ stop gg {args.tetto_giorno * 100:.0f}%", f"+ netto {args.netto_r:.0f}R"]
    sims = [simula(trades, args.equity, lim, secondi_barra=secondi_barra, periodo=periodo)
            for lim in scenari]

    print("\n" + "=" * 74)
    print("LE COPPIE INSIEME, IN ORDINE DI TEMPO: i limiti di portafoglio, uno sull'altro")
    print("=" * 74)
    stampa_tabella(sims, intestazioni)

    print("\n  i 5 giorni peggiori (senza limiti → le altre colonne)")
    for r in giorni_peggiori(sims):
        print(f"    {r['giorno']}  {r['pnl']:>+9.2f}  →  "
              + "  ".join(f"{v:>+9.2f}" for v in r["altri"]))

    if args.dal is not None:
        # giorno per giorno dal --dal: e' la riga da mettere accanto al paper
        print(f"\n  PnL giorno per giorno dal {args.dal} (stesse colonne)")
        giorni = [(args.dal + dt.timedelta(days=i)).isoformat() for i in range(args.giorni + 1)]
        for g in giorni:
            print(f"    {g}  " + "  ".join(f"{s['pnl_per_giorno'].get(g, 0.0):>+9.2f}" for s in sims))

    stampa_wr_condizionato(sims[0])
    print(f"\n  {lettura_diversification(sims[0])}")

    testo = lettura(sims, intestazioni)
    print(f"\nLettura: {testo}")

    pubblica(fb, {
        "updated_at": ora.isoformat(),
        "giorni": args.giorni, "dal": dt.datetime.fromtimestamp(inizio_ts, dt.timezone.utc).date().isoformat(),
        "interval": args.interval, "equity0": args.equity,
        "coppie_simulate": n_simulate, "coppie_saltate": len(saltate),
        "n_trade": len(trades),
        "tetto_direzione": args.tetto_direzione, "tetto_giorno": args.tetto_giorno,
        "netto_r": args.netto_r,
        "limiti": limiti,
        "scenari": {nome: riepilogo_compatto(s) for nome, s in zip(COLONNE, sims)},
        "lettura": testo,
        "lettura_diversification": lettura_diversification(sims[0]),
        "nota": "backtest, non paper: rischio 1%/trade fisso, trade del motore",
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
