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

IL PERIODO DEL PAPER (H5 del backlog, 24 set 2026). Il paper perde dove il gate
prometteva, e due spiegazioni opposte danno lo stesso sintomo: il mercato e'
cambiato, o il paper esegue male. Nel run di default si stampa quindi anche il
PnL simulato giorno per giorno DA QUANDO IL PAPER ESISTE (`PAPER_START`, env,
default 2026-09-16), affiancato al PnL del paper letto da Firestore per giorno
di uscita in ORA ITALIANA (dal 28 set 2026, `bot/core/tempo.py`: lo stesso
giorno del controllo orario). Dal 30 set 2026 la riga «Lettura» di questo
periodo NON conclude piu' ne' «esecuzione» ne' «mercato»: quel confronto misura
anche la SELEZIONE. Le coppie di oggi sono state scelte anche su quei giorni (i
giorni di prova del gate sono gli ultimi 45), e il numero lo mostra: sugli
stessi giorni 16-24 set il simulato faceva -1.357 con le 160 coppie del 25 set
(ops 0232) e +8.465 con le 202 del 30 set (ops 0359). Cambia solo l'insieme di
coppie, quindi il segno del simulato non dice niente sul bot, ne' quando e'
positivo ne' quando e' negativo: la riga rimanda al FUORI CAMPIONE.

FUORI CAMPIONE (H5, 30 set 2026, si' del proprietario). E' la sezione che
separa le due spiegazioni. Per ogni coppia validata e simulata: i trade del
MOTORE entrati DOPO l'istante della validazione (`validated_at`; chi non ce
l'ha parte dal 25 set 12:00 UTC, vedi `VALIDATED_AT_DAL`), mai prima di
PAPER_START; accanto, i trade del PAPER sulle stesse coppie e dagli stessi
istanti fino alla fine dei dati del motore, senza esplorativi e senza uscite
manual/kill_switch/circuit_breaker. Poi R medio, vinti, mfe, primo gradino
toccato, la differenza motore - paper col suo margine d'errore (2 errori
standard), la stessa differenza sui soli SEGNALI in cui paper e motore sono
entrati insieme, e una lettura con una regola scritta PRIMA di vedere i numeri:
con almeno 80 trade del motore, motore <= 0 -> la promessa non regge fuori
campione, la prossima modifica va nel gate; motore > 0 e differenza oltre il
margine -> e' il percorso del bot; altrimenti si rilegge fra una settimana. I
tre bias che restano dentro (sopravvivenza, parametri riscelti, segnali saltati
dal paper) sono stampati, e sono anche contati. Nessun backtest in piu': sono
gli stessi trade simulati sopra; una sola lettura in piu' (il diario
`gate_history/lifecycle`, per contare le coppie rimosse).

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
import json
import math
import os
from collections import Counter, defaultdict
from statistics import mean, median, stdev

from backtesting.data_loader import load_candles
from backtesting.optimizer import WalkForwardOptimizer
from bot.config import settings, timeframe_hours
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.core.tempo import fuso, giorno_da_iso, giorno_locale
from bot.core.indicators import compute_indicator_frame
from bot.execution.exit_logic import breakeven_after_tp1, ladder_multiples, lock_keep
# R e «primo gradino toccato» del paper con le STESSE funzioni della deriva,
# e le stesse uscite esterne che la deriva scarta: una seconda definizione di R
# qui sarebbe la terza copia di una regola (30 set 2026).
from bot.learning.drift import _EXTERNAL as USCITE_ESTERNE
from bot.learning.drift import r_multiplo, tocca_tp1
from bot.learning.trade_logger import TradeLogger
from bot.risk.portafoglio import MOTIVI, limiti_default, simula
from bot.strategies.generated import GeneratedStrategy
from scripts.optimize import coppie_validate

#: da quando esiste il paper (H5, 24 set 2026). Env per spostarlo senza toccare
#: il codice; il default e' il giorno in cui il bot ha iniziato a operare.
PAPER_START = os.environ.get("PAPER_START", "2026-09-16")

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


def trade_in_dict(t, symbol: str, strategy: str, scala=None,
                  fine_ts: float | None = None, secondi_barra: float = 0.0) -> dict:
    """Da SimTrade al dict che `simula` legge. `stop_pct` sta in `feats` (dal
    24 set): senza, il trade verra' scartato e contato, non indovinato.

    Dal 30 set 2026 porta anche cio' che serve al FUORI CAMPIONE, con gli
    stessi nomi del trade del paper, cosi' `tocca_tp1` della deriva vale per
    tutti e due: `mfe_r`, `scale_r_mults` (la scala con cui il motore l'ha
    girato; None = scala globale, come fa `scale_ladder`) e `fine_dati`: il
    trade esce sull'ultima candela, cioe' e' ancora aperto e il motore lo ha
    chiuso al prezzo di fine dati. Il paper conta solo trade chiusi, quindi
    quelli restano fuori dal confronto (non da `simula`)."""
    feats = getattr(t, "feats", None) or {}
    entry_ts = float(getattr(t, "entry_ts", 0) or 0)
    bars = int(getattr(t, "bars_held", 0) or 0)
    fine = bool(fine_ts is not None and secondi_barra > 0
                and entry_ts + bars * secondi_barra >= fine_ts - secondi_barra / 2)
    return {
        "symbol": symbol, "strategy": strategy,
        "direction": str(getattr(t, "direction", "long") or "long"),
        "entry_ts": entry_ts,
        "bars_held": bars,
        "pnl_pct": float(getattr(t, "pnl_pct", 0.0) or 0.0),
        "stop_pct": feats.get("stop_pct"),
        "mfe_r": float(getattr(t, "mfe_r", 0.0) or 0.0),
        "scale_r_mults": list(scala) if scala else None,
        "fine_dati": fine,
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
    # l'ultima candela: chi esce li' e' ancora aperto (FUORI CAMPIONE, 30 set)
    secondi_barra = timeframe_hours(args.interval) * 3600.0
    try:
        fine_ts = float(candles[-1].open_time.timestamp())
    except (AttributeError, TypeError, ValueError):
        fine_ts = None
    trades: list[dict] = []
    for strategy, g in da_fare:
        st = bt.run_strategy(g, symbol, candles, frame=frame)
        scala = ladder_multiples(getattr(g, "params", None))
        trades.extend(trade_in_dict(t, symbol, strategy, scala=scala, fine_ts=fine_ts,
                                    secondi_barra=secondi_barra) for t in st.trades
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


# --------------------------------------------------------------------------- #
# H5: IL PERIODO DEL PAPER — il simulato perde anche lui, dal 16 set?          #
# --------------------------------------------------------------------------- #
def _giorno_uscita(t: dict) -> str | None:
    """Il giorno in ORA ITALIANA (YYYY-MM-DD, `bot/core/tempo.py`) in cui il
    trade del paper e' uscito. Dal 28 set 2026: prima era UTC, e il giorno
    del report non era il giorno del proprietario.

    `exit_ts` (epoch, scritto dal TradeLogger) ha la precedenza; se manca si
    prova `exit_time` (ISO, naive = UTC). Un trade senza nessuno dei due non ha
    un giorno e viene saltato: meglio un trade in meno che uno messo nel
    giorno sbagliato."""
    ts = t.get("exit_ts")
    if isinstance(ts, (int, float)) and ts > 0:
        return giorno_locale(float(ts))
    return giorno_da_iso(t.get("exit_time"))


#: nome vecchio, tenuto per chi lo importa
_giorno_utc_uscita = _giorno_uscita


def pnl_paper_per_giorno(trades: list[dict]) -> dict[str, float]:
    """PnL del paper (USDT, campo `pnl`) sommato per giorno di uscita in ora
    italiana (TUTTI i trade chiusi: esplorativi e uscite esterne compresi, e'
    il conto).

    Il giorno e' quello dell'USCITA, come in `simula` (che accredita il PnL alla
    chiusura, nello stesso fuso): cosi' le due colonne della tabella contano
    allo stesso modo. Funzione pura sui dict di Firestore: i test la nutrono
    con trade sintetici."""
    per_giorno: dict[str, float] = defaultdict(float)
    for t in trades:
        g = _giorno_uscita(t)
        if g is None:
            continue
        try:
            per_giorno[g] += float(t.get("pnl", 0) or 0)
        except (TypeError, ValueError):
            continue
    return {g: round(v, 2) for g, v in sorted(per_giorno.items())}


def _trade_paper(fb, dal_ts: float) -> list[dict] | None:
    """I trade del paper usciti dal `dal_ts` in poi. None se Firebase non c'e'
    o la lettura fallisce (fail-open: la sezione si stampa lo stesso, senza la
    colonna del paper, e lo dice)."""
    try:
        if not fb.is_live:
            return None
        return [t for t in TradeLogger(fb).all_since(dal_ts) if isinstance(t, dict)]
    except Exception:  # noqa: BLE001 — una lettura fallita non deve fermare il report
        return None


def lettura_periodo_paper(sim_tot: float, paper_tot: float | None, dal: str) -> str:
    """La riga «Lettura:» del periodo del paper.

    Le unita' non coincidono (il simulato parte dai 10.000$ del gate con l'1%
    di rischio, il paper dal suo conto e dalle sue size): si confrontano i
    SEGNI e i giorni, mai le due somme come se fossero la stessa cosa. E il
    simulato dal 16 set dipende dalla selezione: l'holdout del gate sono gli
    ultimi 45 giorni, cioe' proprio questi.

    30 set 2026: con simulato in utile e paper in perdita la riga diceva «il
    divario e' esecuzione/parita', non il mercato». Non lo poteva dire: sugli
    stessi giorni 16-24 set il simulato faceva -1.357 con le coppie del 25 set
    (ops 0232) e +8.465 con quelle del 30 (ops 0359), quindi quel segno dipende
    da QUALI coppie sono validate oggi, cioe' dalla selezione. Ora lo dice e
    rimanda alla sezione FUORI CAMPIONE, l'unica che separa le due cose.

    Lo stesso vale col simulato in perdita (30 set, revisione): la riga diceva
    «e' il mercato, non l'esecuzione», ma il -1.357 del 25 set e' proprio un
    simulato in perdita diventato +8.465 cambiando solo le coppie. La proposta
    approvata chiede che questa riga smetta di concludere dal simulato: ora dice
    cosa si vede e rimanda, in tutti i rami. Senza, lo stesso report dava due
    cause diverse per la stessa perdita («mercato» qui, «selezione» sotto)."""
    avviso = ("questo confronto misura anche la SELEZIONE, perche' le coppie di oggi sono "
              "state scelte anche su questi giorni (i giorni di prova del gate sono gli "
              "ultimi 45); esecuzione e selezione si separano nella sezione FUORI CAMPIONE")
    if paper_tot is None:
        return (f"dal {dal} il portafoglio simulato fa {sim_tot:+.2f}; il paper non e' "
                f"leggibile da qui (Firebase assente o nessun trade chiuso), quindi il "
                f"confronto non si fa; {avviso}.")
    if sim_tot <= 0:
        return (f"dal {dal} anche il portafoglio simulato perde ({sim_tot:+.2f}, paper "
                f"{paper_tot:+.2f}): con le coppie validate oggi questi giorni erano "
                f"difficili, ma il simulato cambia con le coppie scelte e non dice se il "
                f"bot esegue bene o male; {avviso}.")
    if paper_tot < 0:
        return (f"dal {dal} il portafoglio simulato fa {sim_tot:+.2f} e il paper "
                f"{paper_tot:+.2f}, ma da qui non si sa se il divario e' esecuzione o "
                f"selezione: {avviso}.")
    return (f"dal {dal} simulato {sim_tot:+.2f} e paper {paper_tot:+.2f}, tutti e due in "
            f"utile o pari: nessun divario da spiegare in questo periodo; {avviso}.")


def sezione_periodo_paper(sim: dict, trades_paper: list[dict] | None, dal: dt.date,
                          oggi: dt.date, inizio_run: dt.date) -> dict:
    """Stampa «PERIODO DEL PAPER» e ritorna il riepilogo (senza liste annidate)
    per Firebase. `sim` e' lo scenario SENZA limiti extra: e' il portafoglio
    come il gate lo immagina, senza i what-if. Se il run parte DOPO `dal`
    (es. `--giorni 3`) la tabella copre solo i giorni simulati e lo dice."""
    da = max(dal, inizio_run)
    if da > oggi:
        print(f"\n  PERIODO DEL PAPER: {dal} e' nel futuro, niente da confrontare.")
        return {"dal": dal.isoformat(), "giorni": 0}
    giorni = [(da + dt.timedelta(days=i)).isoformat() for i in range((oggi - da).days + 1)]
    sim_g = {g: float(sim["pnl_per_giorno"].get(g, 0.0)) for g in giorni}
    paper_g = pnl_paper_per_giorno(trades_paper) if trades_paper is not None else None

    print("\n" + "=" * 74)
    print(f"PERIODO DEL PAPER (dal {da}, PAPER_START={PAPER_START}, giornate in ora "
          f"italiana): simulato senza limiti extra · paper")
    print("=" * 74)
    if inizio_run > dal:
        print(f"  NB il run parte dal {inizio_run}, dopo PAPER_START: i giorni prima mancano.")
    print(f"  {'giorno':<12}{'simulato':>12}{'paper':>12}")
    for g in giorni:
        p = "n.d." if paper_g is None else f"{paper_g.get(g, 0.0):+.2f}"
        print(f"  {g:<12}{sim_g[g]:>+12.2f}{p:>12}")
    sim_tot = sum(sim_g.values())
    utile = sum(1 for v in sim_g.values() if v > 0)
    perdita = sum(1 for v in sim_g.values() if v < 0)
    riga = (f"  totale{'':<6}{sim_tot:>+12.2f}")
    paper_tot = None
    if paper_g is not None:
        paper_tot = round(sum(v for g, v in paper_g.items() if g in sim_g), 2)
        riga += f"{paper_tot:>+12.2f}"
        n_paper = len([t for t in trades_paper if _giorno_uscita(t) in sim_g])
        riga += f"   ({n_paper} trade del paper usciti nel periodo)"
    print(riga)
    print(f"  giorni simulati in utile / in perdita: {utile} / {perdita} su {len(giorni)}")
    testo = lettura_periodo_paper(sim_tot, paper_tot, da.isoformat())
    print(f"  Lettura: {testo}")
    return {"dal": da.isoformat(), "giorni": len(giorni),
            "simulato_totale": round(sim_tot, 2), "paper_totale": paper_tot,
            "giorni_utile": utile, "giorni_perdita": perdita, "lettura": testo}


# --------------------------------------------------------------------------- #
# H5, 30 set 2026: FUORI CAMPIONE — il motore dopo la validazione contro il     #
# paper, sulle stesse coppie e dagli stessi istanti                             #
# --------------------------------------------------------------------------- #
#: da quando OGNI via di promozione scrive `validated_at` (30 set 2026,
#: revisione). Il campo e' nato il 21 set (commit «vite delle strategie»), ma
#: allora lo scrivevano solo le promozioni di optimize (le coppie base) e, dal 24
#: set, le varianti retroattive: la discovery ha cominciato a scriverlo per le
#: GENERATE promosse normalmente solo col commit 425d808, arrivato sulla macchina
#: il 25 set alle 08:33 UTC (ops 0243, stesso commit). Il giro partito alle 06:09
#: di quel giorno girava col codice vecchio, e un giro della discovery dura al
#: piu' ~3 ore (2h49 il 28 set, il piu' lungo nei log ops): alle 12:00 UTC ogni
#: promozione senza data era gia' avvenuta. Prima di questa correzione il
#: pavimento era il 21 set, e le ~100 generate promosse la sera del 24 (validate
#: da 59 a 134, ops 0188 e 0217) contavano come «fuori campione» giorni che
#: erano dentro i dati che le avevano promosse, e in cui il paper non poteva
#: ancora operarle: il motore si gonfiava proprio verso «esecuzione». Prudente
#: (le vere validate prima del 21 set perdono i giorni dal 21 al 25), non esatto.
VALIDATED_AT_DAL = dt.datetime(2026, 9, 25, 12, tzinfo=dt.timezone.utc).timestamp()

#: sotto questi trade del motore fuori campione non si decide niente. E' il
#: numero della proposta approvata («il motore fuori campione puo' avere meno di
#: 80 trade e il 7 ott non si decide», 30 set) e del suo calcolo di potenza.
#: Simulazione del 30 set (dispersione 1,07R per trade): con 80 trade e un motore
#: vero a +0,18R, cioe' la promessa in campione che regge, la regola direbbe
#: «selezione» per caso il 6,6% delle volte (1,9% con 150); senza minimo, come
#: prima della revisione, bastavano 2 trade.
MIN_TRADE_MOTORE = 80

#: sotto questa differenza motore - paper (in R) i due lati «fanno quasi uguale»:
#: piu' trade non cambierebbero il verdetto, e il conto dei trade «che servono»
#: esploderebbe (milioni) senza voler dire niente
QUASI_UGUALE_R = 0.05

#: tolleranza dell'abbinamento trade del paper <-> trade del motore, in barre:
#: la stessa di `confronto_gate_paper._accoppia` e di ops 0304 (il segnale nasce
#: a barra chiusa, il bot entra dopo), cosi' «stessi segnali» e' lo stesso metro
TOL_ABBINAMENTO_BARRE = 2

#: la regola della «Lettura», scritta il 30 set PRIMA di vedere i numeri e
#: stampata nel report: se la si cambia dopo aver letto un esito, non e' piu'
#: una regola. Riscritta lo stesso giorno, prima della prima lettura (1 ott), in
#: parole semplici e con cio' che la proposta approvata diceva gia': il minimo di
#: 80 trade del motore e la rilettura del 14 ott.
REGOLA_FUORI_CAMPIONE = (
    "DECISIONE IL 7 OTT (regola del 30 set): con almeno 80 trade del motore, motore <= 0 "
    "-> il problema e' la scelta delle coppie, la prossima modifica va nel gate; motore > 0 "
    "e sopra il paper oltre il margine -> il problema e' il bot, la prossima modifica va su "
    "ingressi e uscite; altrimenti si rilegge il 14 ott.")

#: oltre questi giorni di validazione distinti, i piu' vecchi si sommano in uno
#: (la riga deve restare corta anche fra tre mesi)
GIORNI_VALIDAZIONE_MAX = 8


def _num(v) -> float:
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def _num_o_none(v) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _ts_iso(raw) -> float:
    """Un istante (epoch) da un campo del paper: numero, datetime o stringa ISO
    (naive = UTC, come `giorno_da_iso`). 0 se illeggibile."""
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return float(raw) if raw > 0 else 0.0
    if isinstance(raw, dt.datetime):
        d = raw
    else:
        if not raw:
            return 0.0
        try:
            d = dt.datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            return 0.0
    if d.tzinfo is None:
        d = d.replace(tzinfo=dt.timezone.utc)
    return d.timestamp()


def _ts_ingresso_paper(t: dict) -> float:
    """L'istante d'ingresso di un trade del paper (epoch, da `entry_time`). 0 se
    illeggibile: il trade resta fuori, meglio uno in meno che uno contato prima
    della validazione."""
    return _ts_iso(t.get("entry_time"))


def _ts_uscita_paper(t: dict) -> float:
    """L'istante d'uscita: `exit_ts` (epoch, scritto dal TradeLogger) o, se
    manca, `exit_time`. 0 se non c'e' nessuno dei due."""
    ts = _num(t.get("exit_ts"))
    return ts if ts > 0 else _ts_iso(t.get("exit_time"))


def inizio_fuori_campione(rec: dict, pavimento: float) -> tuple[float | None, str]:
    """Da quale istante i trade di una coppia sono FUORI CAMPIONE, e perche'.

    `validated_at` se c'e', altrimenti il 25 set 12:00 UTC (`VALIDATED_AT_DAL`:
    fino a li' le generate promosse dalla discovery non avevano la data); mai
    prima di `pavimento` (l'inizio del paper, o del run se parte dopo).
    Ritorna (istante, origine) con origine «validated_at» o «senza_data».

    LE AZZERATE DEL 27 SET (J13, `sessione_azzerata_at`): la coppia e' ripartita
    da zero passaggi, e una validata oggi li ha ripresi dopo. La promozione
    riscrive `validated_at` (`_segna_promozione`), quindi si conta da li': e'
    anche l'istante in cui paper e motore girano la stessa regola della sessione.
    Se invece `validated_at` e' PRIMA dell'azzeramento non si sa quando e'
    tornata validata, e i giorni in cui ha ripreso i passaggi sarebbero dentro
    il campione: la coppia esce da tutti e due i lati (None, «azzerata_senza_data»)."""
    rec = rec if isinstance(rec, dict) else {}
    va = _num(rec.get("validated_at"))
    az = _num(rec.get("sessione_azzerata_at"))
    if az > 0 and va <= az:
        return None, "azzerata_senza_data"
    if va > 0:
        return max(va, pavimento), "validated_at"
    return max(VALIDATED_AT_DAL, pavimento), "senza_data"


def statistiche_lato(righe: list[tuple]) -> dict:
    """n, R medio, dev. standard, quota vinti, mfe mediana e quota che tocca il
    primo gradino, da righe (R, mfe_r o None, tocca_tp1 o None). Valori NON
    arrotondati: la differenza e l'errore standard si fanno su questi."""
    rs = [float(r) for r, _, _ in righe]
    mfes = [float(m) for _, m, _ in righe if m is not None]
    tp = [bool(x) for _, _, x in righe if x is not None]
    n = len(rs)
    return {
        "n": n,
        "r_medio": mean(rs) if rs else None,
        "dev_std": stdev(rs) if n >= 2 else None,
        "vinti": sum(1 for r in rs if r > 0) / n if n else None,
        "mfe_mediana": median(mfes) if mfes else None,
        "tocca_tp1": sum(tp) / len(tp) if tp else None,
    }


def errore_standard_differenza(a: dict, b: dict | None) -> float | None:
    """Errore standard della differenza fra due medie INDIPENDENTI:
    sqrt(s1^2/n1 + s2^2/n2). None se un lato ha meno di 2 trade (senza due
    trade non c'e' una dispersione, e un errore inventato e' peggio di nessuno)."""
    if not b or a.get("dev_std") is None or b.get("dev_std") is None:
        return None
    if a["n"] < 2 or b["n"] < 2:
        return None
    return math.sqrt(a["dev_std"] ** 2 / a["n"] + b["dev_std"] ** 2 / b["n"])


def trade_che_servono(n_tot: int, diff: float | None, es: float | None) -> int | None:
    """Quanti trade in tutto (motore + paper, nella stessa proporzione di oggi)
    servirebbero perche' QUESTA differenza arrivi a 2 errori standard: l'errore
    scende con la radice del campione, quindi n x (2 e.s. / differenza)^2.
    None se la differenza non e' positiva: nessun campione la renderebbe
    «esecuzione»."""
    if diff is None or es is None or diff <= 0 or n_tot <= 0:
        return None
    return int(math.ceil(n_tot * (2.0 * es / diff) ** 2))


def statistiche_abbinate(coppie: list[tuple[float, float]]) -> dict:
    """«STESSI SEGNALI» (30 set 2026, revisione): (R del motore, R del paper) sui
    trade in cui paper e motore sono entrati insieme. La differenza qui e' solo
    il modo in cui il bot esegue (prezzi, uscite, tempi), senza la scelta dei
    segnali; confronto accoppiato, quindi l'errore standard e' quello delle
    differenze trade per trade, sd(d)/sqrt(n)."""
    n = len(coppie)
    d = [m - p for m, p in coppie]
    return {"n": n,
            "motore_r": mean(m for m, _ in coppie) if n else None,
            "paper_r": mean(p for _, p in coppie) if n else None,
            "differenza": mean(d) if n else None,
            "errore_standard": stdev(d) / math.sqrt(n) if n >= 2 else None}


def abbina_segnali(motore_per_coppia: dict, segnali_paper: list[tuple],
                   tol: float) -> tuple[list[tuple[float, float]], int]:
    """Per ogni trade del paper (coppia, ingresso, R) il trade del motore della
    STESSA coppia, non ancora usato, piu' vicino nel tempo entro `tol` secondi: la
    regola di `confronto_gate_paper._accoppia` (un trade del motore si usa una
    volta sola), che pero' non restituisce l'R dei due lati.

    `motore_per_coppia`: coppia -> lista di [ingresso, R, usato]; il flag `usato`
    viene scritto qui, e quelli rimasti False sono i segnali del motore che il
    paper non ha aperto. Ritorna le coppie (R motore, R paper) e quanti trade del
    paper non hanno un segnale del motore vicino."""
    abbinati: list[tuple[float, float]] = []
    senza = 0
    for k, te, r_p in sorted(segnali_paper, key=lambda x: (x[1], x[0])):
        migliore = None
        for riga in motore_per_coppia.get(k, ()):
            if riga[2]:
                continue
            d = abs(riga[0] - te)
            if d <= tol and (migliore is None or d < abs(migliore[0] - te)):
                migliore = riga
        if migliore is None:
            senza += 1
            continue
        migliore[2] = True
        abbinati.append((migliore[1], r_p))
    return abbinati, senza


def _scala(v) -> tuple | None:
    try:
        return tuple(round(float(x), 4) for x in v)
    except (TypeError, ValueError):
        return None


def config_diversa(t: dict, params: dict | None) -> bool | None:
    """BIAS (b), la parte che si conta (30 set 2026, revisione). True se il trade
    del paper ha girato con una scala dei TP, un break-even o un keep DIVERSI da
    quelli con cui il motore lo rigira oggi: il motore usa i `last_params` di
    oggi, che la discovery riscrive a ogni passaggio anche per le validate, il
    paper quelli del momento (o, per il keep, quello imparato). La differenza fra
    due regole d'uscita finirebbe nel conto dell'«esecuzione».

    Scala e break-even contano solo con lo scale-out acceso (spento, non cambiano
    niente). None se il trade non porta nessuno dei tre campi: «non lo so» non e'
    «uguale»."""
    noto = diversa = False
    if settings.SCALE_OUT_ENABLED and "scale_r_mults" in t:
        sp = _scala(t.get("scale_r_mults") or settings.SCALE_OUT_R_MULTIPLES)
        if sp is not None:
            noto = True
            diversa |= sp != _scala(ladder_multiples(params) or settings.SCALE_OUT_R_MULTIPLES)
    if settings.SCALE_OUT_ENABLED and "sl_to_breakeven" in t:
        be = t.get("sl_to_breakeven")
        be = settings.SCALE_OUT_SL_TO_BREAKEVEN if be is None else bool(be)
        noto = True
        diversa |= be != breakeven_after_tp1(params)
    kp = _num_o_none(t.get("profit_lock_keep"))
    if kp is not None:
        ko = lock_keep(params)
        ko = float(settings.PROFIT_LOCK_KEEP) if ko is None else ko
        noto = True
        diversa |= abs(kp - ko) > 1e-6
    return diversa if noto else None


def _fmt_r(v) -> str:
    """Un R col segno: 2 decimali, 3 sotto 0,01 in valore assoluto. Senza, un
    motore a +0,001R si stampava «+0.00» e la regola («motore <= 0 -> gate»)
    sembrava contraddire la Lettura (30 set 2026, revisione)."""
    if v is None:
        return "n.d."
    return f"{v:+.3f}" if 0 < abs(v) < 0.01 else f"{v:+.2f}"


def lettura_fuori_campione(m: dict, p: dict | None, diff: float | None,
                           es: float | None) -> str:
    """La regola del 30 set, in parole, con l'azione che ne segue.

    Revisione del 30 set, prima della prima lettura: (1) nessun verdetto sotto
    MIN_TRADE_MOTORE trade del motore, come diceva la proposta: prima «selezione»
    usciva gia' con 2 trade; (2) il margine della riga «selezione» (2 errori
    standard della media del motore) si chiama «margine» come quello della
    differenza; (3) motore <= 0 non separa il gate da un mercato cambiato dopo la
    validazione, e lo si dice (l'azione della regola resta il gate); (4) se
    valgono insieme motore <= 0 e una differenza oltre il margine, si dicono
    tutte e due invece di fermarsi al primo ramo; (5) una differenza quasi nulla
    non e' «campione piccolo», e' nessun divario.

    Scartato: dire «selezione» solo se motore + margine <= 0. Il confronto giusto
    per «la promessa non regge» e' con la promessa (+0,18R in campione), non con
    lo zero: con quella soglia un motore vero a 0, cioe' la promessa sparita del
    tutto, darebbe «selezione» solo ~2% delle volte."""
    if p is None:
        return "non si decide: il paper non e' leggibile da qui (Firebase assente)."
    if m["n"] < MIN_TRADE_MOTORE:
        return (f"non si decide: il motore ha solo {m['n']} trade dopo la validazione, ne "
                f"servono almeno {MIN_TRADE_MOTORE} (regola del 30 set); si rilegge fra una "
                f"settimana.")
    confronto = (f"differenza {_fmt_r(diff)}R, margine ±{2.0 * es:.2f}R"
                 if diff is not None and es is not None else "")
    # «diff > 0» prima del margine: con dispersione zero (margine 0) una
    # differenza nulla passerebbe «>= margine» e direbbe esecuzione senza divario
    oltre = bool(confronto) and diff > 0 and diff >= 2.0 * es
    if m["r_medio"] <= 0:
        margine_m = 2.0 * m["dev_std"] / math.sqrt(m["n"])
        testo = (f"la promessa non regge dopo la validazione: motore {_fmt_r(m['r_medio'])}R "
                 f"(margine ±{margine_m:.2f}R) su {m['n']} trade. O il gate sceglie coppie "
                 f"buone solo nei giorni su cui le ha provate, o il mercato e' cambiato: "
                 f"questa misura da sola non li separa. Per la regola la prossima modifica "
                 f"va nel gate")
        if oltre:
            testo += (f"; in piu' il paper fa peggio del motore oltre il margine "
                      f"({confronto}): c'e' anche un problema del bot")
        return testo + "."
    if not confronto:
        return ("non si decide: il paper ha meno di 2 trade dopo la validazione, niente "
                "margine d'errore; si rilegge fra una settimana.")
    if diff <= 0:
        return ("non si decide: fuori campione il paper non fa peggio del motore, non c'e' "
                "un divario del bot da spiegare; si rilegge fra una settimana.")
    if oltre:
        return (f"e' esecuzione: sulle stesse coppie il paper rende meno del motore oltre "
                f"il margine ({confronto}); le righe «stessi segnali» e «non aperti» dicono "
                f"se pesano le uscite o i segnali che il bot sceglie. Per la regola la "
                f"prossima modifica va su ingressi e uscite.")
    if diff < QUASI_UGUALE_R:
        return (f"non si decide: motore e paper fanno quasi uguale ({confronto}), piu' "
                f"trade difficilmente cambieranno il verdetto; si rilegge fra una settimana.")
    n_oggi = m["n"] + p["n"]
    serve = trade_che_servono(n_oggi, diff, es)
    if serve is None or serve > 10 * n_oggi:
        return (f"non si decide: la differenza e' piccola rispetto al margine ({confronto}), "
                f"servirebbero piu' di 10 volte i trade di oggi; si rilegge fra una settimana.")
    return (f"non si decide: la differenza sta dentro il margine ({confronto}); servono "
            f"circa {serve} trade in tutto (oggi {n_oggi}) se resta questa; si rilegge fra "
            f"una settimana.")


def _per_giorno_validazione(giorni: Counter) -> str:
    """«21/09 3 · 22/09 5 · ...», i piu' vecchi sommati oltre GIORNI_VALIDAZIONE_MAX."""
    ordinati = sorted(giorni.items())
    if not ordinati:
        return "nessuna con data"
    parti = []
    if len(ordinati) > GIORNI_VALIDAZIONE_MAX:
        vecchi = ordinati[:len(ordinati) - GIORNI_VALIDAZIONE_MAX + 1]
        ordinati = ordinati[len(vecchi):]
        g = vecchi[-1][0]
        parti.append(f"fino al {g[8:10]}/{g[5:7]} {sum(n for _, n in vecchi)}")
    parti.extend(f"{g[8:10]}/{g[5:7]} {n}" for g, n in ordinati)
    return " · ".join(parti)


def fuori_campione(motore: list[dict], paper: list[dict] | None, pairs: dict,
                   chiavi, pavimento: float, fine: float | None = None,
                   secondi_barra: float = 900.0) -> dict:
    """IL CONFRONTO. Funzione pura: trade del motore (i dict di `trade_in_dict`),
    trade del paper (dict di Firestore, None = non leggibile), registro
    (`pairs`), le coppie da confrontare (`chiavi`: validate E simulate, perche'
    il paper di una coppia che il motore non ha girato non ha un lato di
    fronte) e il `pavimento` (inizio del paper o del run).

    Motore: R = pnl_pct / stop_pct, la stessa di `simula` (senza stop il trade
    si conta e si salta); fuori chi esce sull'ultima candela (ancora aperto).
    Paper: R = `drift.r_multiplo` (lo stop ORIGINALE, niente ripiego sullo stop
    di chiusura, spesso gia' a pareggio); fuori gli esplorativi (un
    quasi-passaggio non ha una promessa) e le uscite esterne, contati.

    Revisione del 30 set 2026:
      * `fine`: la fine dei dati del motore (le candele arrivano alla mezzanotte
        UTC del run, esclusa). Il motore non vede niente dopo, quindi dal lato
        paper escono, contati, i trade entrati dopo e quelli usciti dopo (il loro
        gemello del motore sarebbe «ancora aperto»). None = nessun taglio.
      * «stessi segnali»: il confronto non accoppiato mescola il modo in cui il
        bot esegue con QUALI segnali prende (una posizione per coin, 5
        posizioni, tetti): se prende meno segnali proprio sulle coppie buone, la
        differenza cresce anche con un'esecuzione perfetta. Qui si abbina ogni
        trade del paper al trade del motore sullo stesso segnale (`abbina_segnali`)
        e si stampano a parte le due parti. La regola resta quella approvata:
        tutte e due sono percorso del bot, non gate.
      * bias (b) contato: i trade del paper con scala/break-even/keep diversi da
        quelli di oggi (`config_diversa`)."""
    chiavi = list(chiavi)
    inizio: dict[str, float] = {}
    origini: Counter = Counter()
    giorni_val: Counter = Counter()
    azzerate_contate = 0
    for k in chiavi:
        rec = pairs.get(k) if isinstance(pairs.get(k), dict) else {}
        t0, origine = inizio_fuori_campione(rec, pavimento)
        origini[origine] += 1
        if origine == "validated_at":
            giorni_val[giorno_locale(_num(rec.get("validated_at")))] += 1
            if _num(rec.get("sessione_azzerata_at")) > 0:
                azzerate_contate += 1
        if t0 is not None:
            inizio[k] = t0

    righe_m: list[tuple] = []
    coppie_m: set = set()
    motore_per_coppia: dict[str, list[list]] = defaultdict(list)
    fine_dati = senza_stop = 0
    for t in motore:
        k = f"{t.get('symbol')}|{t.get('strategy')}"
        t0 = inizio.get(k)
        if t0 is None or _num(t.get("entry_ts")) < t0:
            continue
        if t.get("fine_dati"):
            fine_dati += 1
            continue
        stop = _num(t.get("stop_pct"))
        if stop <= 0:
            senza_stop += 1
            continue
        r = _num(t.get("pnl_pct")) / stop
        righe_m.append((r, _num_o_none(t.get("mfe_r")), tocca_tp1(t)))
        motore_per_coppia[k].append([_num(t.get("entry_ts")), r, False])
        coppie_m.add(k)

    righe_p: list[tuple] | None = None
    segnali_p: list[tuple] = []
    coppie_p: set = set()
    esplorativi = esterne = senza_r = oltre_fine = 0
    config_note = config_diverse = 0
    r_senza_diverse: list[float] = []
    if paper is not None:
        righe_p = []
        for t in paper:
            if not isinstance(t, dict):
                continue
            k = f"{t.get('symbol')}|{t.get('strategy')}"
            t0 = inizio.get(k)
            ingresso = _ts_ingresso_paper(t)
            if t0 is None or ingresso < t0:
                continue
            if t.get("esplorativa"):
                esplorativi += 1
                continue
            if str(t.get("exit_reason", "")) in USCITE_ESTERNE:
                esterne += 1
                continue
            if fine is not None and (ingresso >= fine or _ts_uscita_paper(t) > fine):
                oltre_fine += 1
                continue
            r = r_multiplo(t)
            if r is None:
                senza_r += 1
                continue
            righe_p.append((r, _num_o_none(t.get("mfe_r")), tocca_tp1(t)))
            segnali_p.append((k, ingresso, r))
            coppie_p.add(k)
            diversa = config_diversa(t, (pairs.get(k) or {}).get("last_params"))
            if diversa is not None:
                config_note += 1
                config_diverse += int(diversa)
            if not diversa:
                r_senza_diverse.append(r)

    m = statistiche_lato(righe_m)
    p = statistiche_lato(righe_p) if righe_p is not None else None
    diff = (m["r_medio"] - p["r_medio"]
            if p and m["r_medio"] is not None and p["r_medio"] is not None else None)
    es = errore_standard_differenza(m, p)
    stessi = non_aperti = None
    senza_segnale = 0
    if paper is not None:
        abbinati, senza_segnale = abbina_segnali(motore_per_coppia, segnali_p,
                                                 TOL_ABBINAMENTO_BARRE * secondi_barra)
        stessi = statistiche_abbinate(abbinati)
        rs_na = [r for righe in motore_per_coppia.values() for _, r, usato in righe if not usato]
        non_aperti = {"n": len(rs_na), "r_medio": mean(rs_na) if rs_na else None}
    return {
        "coppie": len(chiavi), "coppie_con_motore": len(coppie_m),
        "coppie_con_paper": len(coppie_p),
        "senza_data": origini["senza_data"], "con_data": origini["validated_at"],
        "validate_per_giorno": _per_giorno_validazione(giorni_val),
        "azzerate_contate": azzerate_contate,
        "azzerate_escluse": origini["azzerata_senza_data"],
        "motore": m, "paper": p,
        "motore_fine_dati": fine_dati, "motore_senza_stop": senza_stop,
        "paper_esplorativi": esplorativi, "paper_uscite_esterne": esterne,
        "paper_oltre_fine": oltre_fine, "paper_senza_r": senza_r,
        "differenza": diff, "errore_standard": es,
        "stessi_segnali": stessi, "motore_non_aperti": non_aperti,
        "paper_senza_segnale": senza_segnale,
        "paper_config_note": config_note, "paper_config_diverse": config_diverse,
        "paper_r_senza_config_diverse": mean(r_senza_diverse) if r_senza_diverse else None,
        "servono_trade": trade_che_servono(m["n"] + (p["n"] if p else 0), diff, es),
        "lettura": lettura_fuori_campione(m, p, diff, es),
    }


def rimosse_dal(diario, dal_ts: float) -> int | None:
    """BIAS DI SOPRAVVIVENZA, la parte che si conta: quante validate sono state
    RIMOSSE dal registro dal `dal_ts` in poi (eventi «rimossa» del diario
    `gate_history/lifecycle`, scritti da `optimize.registra_vite`). None se il
    diario non si legge: «non lo so» non e' zero."""
    if not isinstance(diario, dict):
        return None
    eventi = diario.get("events")
    if isinstance(eventi, str):
        try:
            eventi = json.loads(eventi)
        except ValueError:
            return None
    if not isinstance(eventi, list):
        return None
    return sum(1 for e in eventi if isinstance(e, dict) and e.get("tipo") == "rimossa"
               and _num(e.get("at")) >= dal_ts)


def paper_fuori_registro(paper: list[dict] | None, validate, dal_ts: float) -> dict | None:
    """Il pezzo che il motore NON PUO' vedere: i trade del paper (senza
    esplorativi e uscite esterne, entrati dal `dal_ts`) su coppie che oggi non
    sono piu' validate — rimosse, azzerate il 27 set, sostituite da una figlia.
    Il motore rigira solo le validate di oggi, quindi questi trade mancano per
    costruzione dal suo lato. None se il paper non si legge."""
    if paper is None:
        return None
    validate = set(validate)
    rs: list[float] = []
    coppie: set = set()
    senza_r = 0
    for t in paper:
        if not isinstance(t, dict) or t.get("esplorativa"):
            continue
        if str(t.get("exit_reason", "")) in USCITE_ESTERNE:
            continue
        k = f"{t.get('symbol')}|{t.get('strategy')}"
        if k in validate or _ts_ingresso_paper(t) < dal_ts:
            continue
        r = r_multiplo(t)
        if r is None:
            senza_r += 1
            continue
        rs.append(r)
        coppie.add(k)
    return {"n": len(rs), "r_medio": mean(rs) if rs else None, "coppie": len(coppie),
            "senza_r": senza_r}


def _diario_vite(fb) -> dict | None:
    """Il diario delle validate, UNA lettura. Fail-open: senza, il conto delle
    rimosse dice «n.d.» e il resto del report non cambia. Chiamata posizionale:
    i client finti dei test spesso hanno solo `get_doc(coll, doc)`."""
    try:
        doc = fb.get_doc("gate_history", "lifecycle")
    except Exception:  # noqa: BLE001 — una lettura fallita non deve fermare il report
        return None
    return doc if isinstance(doc, dict) else None


def _r(v, fmt: str = "{:+.2f}") -> str:
    return "n.d." if v is None else fmt.format(v)


def _margine(es: float | None) -> str:
    return "n.d." if es is None else f"±{2 * es:.2f}R"


def _riga_lato(nome: str, s: dict | None, extra: str = "") -> str:
    if s is None:
        return f"  {nome:<8}{'n.d.':>6}   (paper non leggibile)"
    return (f"  {nome:<8}{s['n']:>6}{_fmt_r(s['r_medio']):>9}{_r(s['vinti'], '{:.0%}'):>7}"
            f"{_r(s['mfe_mediana'], '{:.2f}R'):>8}{_r(s['tocca_tp1'], '{:.0%}'):>11}{extra}")


def stampa_fuori_campione(fc: dict, dal: str, rimosse: int | None,
                          fuori_reg: dict | None) -> None:
    """La sezione a schermo. Deve restare sotto ~3 KB: l'agente ops taglia
    oltre 20.000 caratteri tenendo testa e coda, e questa sta nella coda.

    30 set 2026, revisione: il proprietario la legge dal telefono. Prima la
    domanda a cui risponde, poi cosa si conta e cosa vuol dire R, colonne con
    nomi semplici, un solo nome («margine») per i due errori, la regola con
    l'azione e le date; niente nomi di campi o di collezioni."""
    print("\n" + "=" * 74)
    print("FUORI CAMPIONE (H5): le coppie validate guadagnano anche DOPO essere state scelte?")
    print("=" * 74)
    print("  Domanda: il paper perde perche' il bot esegue male (esecuzione) o perche' il gate "
          "sceglie coppie buone solo nei giorni su cui le ha provate (selezione)?")
    print(f"  Contano solo i trade nati dopo la validazione di ogni coppia, mai prima del {dal}: "
          f"giorni che il gate non aveva visto. R = esito in multipli del rischio (-1R = stop "
          f"pieno); «max R» = il massimo toccato (mediana); «1° target» = quota che arriva al "
          f"primo gradino.")
    print(f"  coppie confrontate {fc['coppie']} · con trade del motore {fc['coppie_con_motore']} "
          f"· con trade del paper {fc['coppie_con_paper']}")
    print(f"  senza data di validazione (validate prima del 25 set: contate dal 25 set, 14:00 "
          f"italiane) {fc['senza_data']} · con data: {fc['validate_per_giorno']}")
    if fc["azzerate_contate"] or fc["azzerate_escluse"]:
        print(f"  azzerate il 27 set: {fc['azzerate_contate']} contate da quando sono tornate "
              f"validate, {fc['azzerate_escluse']} fuori da tutti e due i lati (nessuna data dopo)")
    print(f"  {'':<8}{'trade':>6}{'R medio':>9}{'vinti':>7}{'max R':>8}{'1° target':>11}")
    print(_riga_lato("motore", fc["motore"]))
    p = fc["paper"]
    print(_riga_lato("paper", p, f"   ({fc['paper_senza_r']} senza R)" if p else ""))
    if fc["differenza"] is not None:
        print(f"  motore - paper {_fmt_r(fc['differenza'])}R, margine d'errore "
              f"{_margine(fc['errore_standard'])} (dentro il margine puo' essere caso)")
    ss = fc.get("stessi_segnali")
    if ss and ss["n"]:
        print(f"  stessi segnali (paper e motore entrano insieme): {ss['n']} trade · motore "
              f"{_fmt_r(ss['motore_r'])}R · paper {_fmt_r(ss['paper_r'])}R · differenza "
              f"{_fmt_r(ss['differenza'])}R, margine {_margine(ss['errore_standard'])}")
    na = fc.get("motore_non_aperti")
    if na is not None:
        print(f"  non aperti: {na['n']} segnali del motore che il paper non ha preso, R medio "
              f"{_fmt_r(na['r_medio'])} · trade del paper senza un segnale del motore "
              f"{fc['paper_senza_segnale']}")
    print(f"  Lettura: {fc['lettura']}")
    print(f"  {REGOLA_FUORI_CAMPIONE}")
    print(f"  fuori dal confronto: paper {fc['paper_esplorativi']} esplorativi, "
          f"{fc['paper_uscite_esterne']} chiusi a mano o d'emergenza, {fc['paper_oltre_fine']} "
          f"oltre la fine dei dati del motore; motore {fc['motore_fine_dati']} ancora aperti a "
          f"fine dati, {fc['motore_senza_stop']} senza stop")
    print(f"  bias (a) validate rimosse dal {dal}: {'n.d.' if rimosse is None else rimosse}. "
          f"Chi resta ha ripassato il gate anche dopo la validazione: il motore qui e' ottimista.")
    if fuori_reg and fuori_reg["n"]:
        print(f"    il paper su {fuori_reg['coppie']} coppie non piu' validate (rimosse, azzerate, "
              f"sostituite) fa {fuori_reg['n']} trade, R medio {_fmt_r(fuori_reg['r_medio'])}: "
              f"il motore non le vede")
    riga_b = (f"  bias (b) {fc['paper_config_diverse']} trade del paper su "
              f"{fc['paper_config_note']} hanno girato con scala, break-even o keep diversi "
              f"da quelli con cui il motore li rigira oggi")
    if fc["paper_config_diverse"] and fc["paper_r_senza_config_diverse"] is not None:
        riga_b += f"; senza di loro il paper fa {_fmt_r(fc['paper_r_senza_config_diverse'])}R"
    print(riga_b + ".")
    print("  bias (c) il paper salta i segnali con la coin gia' aperta e ai tetti di "
          "portafoglio, il motore no: e' la riga «non aperti».")


def riepilogo_fuori_campione(fc: dict, dal: str, rimosse: int | None,
                             fuori_reg: dict | None) -> dict:
    """Per `portfolio/backtest` (campo `fuori_campione`): numeri arrotondati,
    niente liste (Firestore rifiuta le liste annidate, ops 0184)."""
    def arr(v):
        if isinstance(v, dict):
            return {k: arr(x) for k, x in v.items()}
        return round(v, 4) if isinstance(v, float) else v

    out = {k: arr(v) for k, v in fc.items()}
    out["dal"] = dal
    out["rimosse_dal_inizio_paper"] = rimosse
    out["paper_fuori_registro"] = arr(fuori_reg)
    out["regola"] = REGOLA_FUORI_CAMPIONE
    return out


def sezione_fuori_campione(motore: list[dict], paper: list[dict] | None, pairs: dict,
                           simulate, validate, pavimento: float, dal_ts: float,
                           diario, fine: float | None = None,
                           secondi_barra: float = 900.0) -> dict:
    """Calcola, stampa e ritorna il riepilogo per Firebase."""
    dal = dt.datetime.fromtimestamp(pavimento, dt.timezone.utc).date().isoformat()
    fc = fuori_campione(motore, paper, pairs, simulate, pavimento, fine=fine,
                        secondi_barra=secondi_barra)
    rimosse = rimosse_dal(diario, dal_ts)
    fuori_reg = paper_fuori_registro(paper, validate, dal_ts)
    stampa_fuori_campione(fc, dal, rimosse, fuori_reg)
    return riepilogo_fuori_campione(fc, dal, rimosse, fuori_reg)


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
                    help="perdita di portafoglio nel giorno (ora italiana), frazione dell'equity di "
                         "inizio giornata, oltre cui non si apre piu' (0 = spento)")
    ap.add_argument("--netto-r", type=float, default=2.0,
                    help="massimo |rischio long - rischio short| aperto, in multipli del "
                         "rischio per trade (0 = spento)")
    ap.add_argument("--source", default="auto")
    ap.add_argument("--equity", type=float, default=10_000.0,
                    help="equity di partenza (default: i 10.000$ del gate)")
    args = ap.parse_args(argv)

    # «oggi» e' il giorno del proprietario (ora italiana, 28 set 2026): la
    # tabella del periodo del paper finisce nella giornata che lui sta leggendo
    ora = dt.datetime.now(fuso())
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

    # H5: nel run di default, il periodo del paper giorno per giorno, accanto
    # al paper vero. Con --dal la tabella sopra fa gia' lo stesso lavoro.
    # Subito dopo, il FUORI CAMPIONE (30 set 2026): stessi trade del paper (una
    # lettura sola), stessi trade del motore (nessun backtest in piu'). Sta qui,
    # nella coda dell'output, perche' l'agente ops oltre 20.000 caratteri tiene
    # testa e coda e taglia il mezzo.
    periodo_paper: dict = {}
    fuori: dict = {}
    if args.dal is None:
        try:
            dal_paper = dt.date.fromisoformat(PAPER_START)
        except ValueError:
            dal_paper = None
            print(f"\n  PERIODO DEL PAPER: PAPER_START={PAPER_START!r} non e' una data, salto.")
        if dal_paper is not None:
            dal_ts = dt.datetime.combine(dal_paper, dt.time(), dt.timezone.utc).timestamp()
            paper = _trade_paper(fb, dal_ts)
            periodo_paper = sezione_periodo_paper(
                sims[0], paper, dal_paper, ora.date(),
                dt.datetime.fromtimestamp(inizio_ts, dt.timezone.utc).date())
            # le coppie davvero girate dal motore: il paper di una coppia saltata
            # (base, altro timeframe, poche candele) non avrebbe un lato di fronte
            chiavi_saltate = {k for k, _ in saltate}
            simulate = [k for k in validate if k not in chiavi_saltate]
            # la fine dei dati del motore: `trades_della_coin` carica le candele
            # fino a OGGI escluso, cioe' alla mezzanotte UTC; il paper si taglia
            # allo stesso istante (30 set 2026, revisione: prima contava anche le
            # ~6 ore fra la mezzanotte e il run, che il motore non vede)
            fine_motore = dt.datetime.combine(dt.datetime.now(dt.timezone.utc).date(),
                                              dt.time(), dt.timezone.utc).timestamp()
            try:
                fuori = sezione_fuori_campione(
                    trades, paper, pairs, simulate, validate,
                    max(dal_ts, inizio_ts), dal_ts, _diario_vite(fb),
                    fine=fine_motore, secondi_barra=secondi_barra)
            except Exception as exc:  # noqa: BLE001 — una sezione rotta non deve fermare il report
                print(f"\n  FUORI CAMPIONE: saltata per un errore ({str(exc)[:120]}).")

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
        "periodo_paper": periodo_paper,
        "fuori_campione": fuori,
        "nota": "backtest, non paper: rischio 1%/trade fisso, trade del motore",
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
