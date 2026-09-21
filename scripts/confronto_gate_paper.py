"""GATE CONTRO PAPER, TUTTO QUELLO CHE SI PUO' CONFRONTARE.

Domande del proprietario, 21 settembre 2026, dopo aver visto tre strategie
validate chiudere in perdita ogni singolo trade:

  1. i trade del paper sono gli STESSI che avrebbe fatto il gate — le soglie
     d'ingresso combaciano, o c'e' un errore da qualche parte?
  2. nel gate una serie di perdite cosi' lunga era mai successa?
  3. «voglio confrontare TUTTI i dati, non solo il win rate»: quante uscite al
     primo gradino, al secondo, al terzo; vincite e perdite consecutive; quanto
     lontano arriva il prezzo; quanto rende un trade.

IL WIN RATE DA SOLO MENTE, e il 21 settembre lo ha fatto davvero: la dashboard
mostrava «57%» (del backtest) accanto a quattro trade tutti persi (del paper), e
i due numeri sembravano lo stesso numero. Sotto scale-out e' per giunta la
statistica meno informativa che esista — un trade che tocca il primo gradino e
torna a pareggio e' una «vittoria» che vale 0,45R lordi, uno che corre fino
all'ultimo ne vale 3,35R, e il conto lo fa la CODA. Per questo qui si
confrontano i GRADINI raggiunti, non i vinti/persi.

COSA NON SI PUO' CONFRONTARE, e va detto invece di inventarlo:
  * il MOTIVO dell'uscita: il paper lo registra (`exit_reason`), il backtest no.
    Al suo posto si contano i gradini, ricavati da `mfe_r` con la STESSA
    funzione da entrambe le parti;
  * i COSTI: nel paper sono stimati col modello del gate, non misurati dai fill.
    Confrontarli direbbe solo che il modello e' uguale a se stesso;
  * il PnL in valore assoluto: il backtest somma variazioni di prezzo, il paper
    USDT. Si confrontano rapporti (PF) e medie per trade, mai due somme.

LA SECONDA HA UNA RISPOSTA NUMERICA e nessuno l'aveva mai cercata. Finora la
divergenza si misurava col profit factor, che e' una media: dice che il vissuto
e' peggiore della promessa, non se e' FUORI da cio' che la promessa prevede. Una
strategia che vince il 57% delle volte perde comunque, prima o poi, otto volte
di fila — e se le ha gia' fatte nella sua storia validata, vederle adesso non e'
la prova di un guasto.

E LA DOMANDA GIUSTA NON E' PER-STRATEGIA. I trade persi stanno su strategie e
coin diverse: quello che il proprietario ha vissuto e' la serie del PORTAFOGLIO,
non quella di una spec. Quindi i trade del gate di tutte le coppie che hanno
operato vengono messi in ordine di tempo — come li vivrebbe un conto solo — e la
serie si misura li' dentro.

Una cosa che questo script NON fa: dire che il campione basta. Se il paper ha
chiuso 11 trade, 11 e' un numero da cui non si conclude quasi niente; il senso
qui e' avere il METRO, cioe' sapere quale serie di perdite il gate considera
normale, prima di decidere se quella in corso lo e'.

SOLA LETTURA. Rigira il motore di backtest e legge i trade del paper: non
scrive su Firebase, non tocca il registro, non cambia niente di cio' che il bot
sta facendo adesso.

Uso:
    .venv/bin/python -m scripts.confronto_gate_paper
    .venv/bin/python -m scripts.confronto_gate_paper --coppie 4 --start 2024-01-01
"""
from __future__ import annotations

import argparse
import datetime as dt
from collections import defaultdict
from datetime import date

from backtesting.data_loader import load_candles
from backtesting.optimizer import WalkForwardOptimizer
from bot.config import settings, timeframe_hours
from bot.core.firebase_client import decode_pairs, get_firebase
from bot.core.indicators import compute_indicator_frame
from bot.execution.exit_logic import ladder_multiples
from bot.learning.trade_logger import TradeLogger
from bot.strategies.base import get_all_strategies
from bot.strategies.generated import GeneratedStrategy
# I MATTONI CONDIVISI con `gate_vs_paper`: le fasce di mfe devono essere
# calcolate dalla STESSA funzione da entrambe le parti. Due copie della stessa
# regola che si separano nel tempo sono il difetto piu' caro di questo
# progetto — ci e' gia' costato tre copie di `judge_window`.
from scripts.gate_vs_paper import _bucket_of


# --------------------------------------------------------------------------- #
# LA MISURA: quanto dura la peggiore sfortuna che il gate ha gia' attraversato  #
# --------------------------------------------------------------------------- #
def serie_perdenti(esiti: list[bool]) -> list[int]:
    """Le lunghezze delle serie di perdite consecutive, in ordine di tempo.

    `esiti[i]` e' True se il trade i-esimo ha vinto. Una sola passata: contare
    le serie con due conteggi separati e' il modo classico di farli divergere
    sul caso di confine (la serie che arriva fino all'ultimo trade)."""
    fuori: list[int] = []
    corrente = 0
    for vinto in esiti:
        if vinto:
            if corrente:
                fuori.append(corrente)
            corrente = 0
        else:
            corrente += 1
    if corrente:
        fuori.append(corrente)
    return fuori


def quante_volte_almeno(esiti: list[bool], n: int) -> int:
    """Quante FINESTRE di `n` trade consecutivi sono state tutte perdenti.

    Non e' la stessa cosa del conteggio delle serie: una serie da 12 contiene
    due finestre da 11, e chi guarda il proprio conto le vive entrambe. E'
    questa la frequenza che risponde a «quanto spesso capita», perche' e' la
    stessa cosa che sta vivendo il paper adesso."""
    if n <= 0 or len(esiti) < n:
        return 0
    return sum(1 for i in range(len(esiti) - n + 1)
               if not any(esiti[i:i + n]))


def _finestre(nome: str, esiti: list[bool], paper_n: int) -> None:
    """Quanto spesso il gate ha attraversato una striscia lunga come quella in
    corso. E' il METRO: senza, ogni serie di perdite sembra un guasto.

    Si contano le FINESTRE, non le serie. Una serie da 12 contiene due finestre
    da 11 e chi guarda il proprio conto le vive entrambe: contare le serie
    darebbe 1 e farebbe sembrare l'evento piu' raro di quanto e'."""
    if not esiti or paper_n <= 0:
        return
    possibili = max(len(esiti) - paper_n + 1, 0)
    if not possibili:
        print(f"  {nome}: storia piu' corta di {paper_n} trade, non confrontabile")
        return
    q = quante_volte_almeno(esiti, paper_n)
    print(f"  {nome}: finestre di {paper_n} trade consecutivi TUTTI persi: "
          f"{q} su {possibili} ({q / possibili * 100:.1f}%)")


# --------------------------------------------------------------------------- #
# IL CONFRONTO COMPLETO: le stesse grandezze, calcolate allo stesso modo       #
# --------------------------------------------------------------------------- #
def gradini_raggiunti(mfes: list[float], mults: tuple) -> list[int]:
    """Quanti trade hanno toccato 0, 1, 2, 3 gradini.

    E' LA STATISTICA CHE SOSTITUISCE IL WIN RATE. Sotto scale-out «vinto» non
    dice quasi niente: chi tocca il primo gradino e torna a pareggio incassa
    0,45R lordi, chi arriva in fondo 3,35R, e sono entrambi «vittorie». Il
    numero di gradini invece si confronta davvero fra backtest e vissuto,
    perche' si ricava da `mfe_r`, che esiste da tutte e due le parti.

    L'indice della fascia E' il numero di gradini raggiunti: sotto il primo
    gradino -> 0, fra il primo e il secondo -> 1, e cosi' via."""
    conte = [0] * (len(mults) + 1)
    for m in mfes:
        conte[_bucket_of(m, mults)] += 1
    return conte


def _riga_gradini(nome: str, conte: list[int]) -> None:
    tot = sum(conte)
    if not tot:
        print(f"  {nome:<10}  nessun trade")
        return
    celle = "".join(f"{c / tot * 100:>8.0f}%" for c in conte)
    print(f"  {nome:<10}{tot:>6}{celle}")


def profilo(nome: str, mfes: list[float], pnls: list[float],
            esiti: list[bool], mults: tuple) -> dict:
    """Tutte le grandezze confrontabili di una delle due parti.

    `pnls` NON ha la stessa unita' fra gate e paper (il backtest somma
    variazioni di prezzo, il paper USDT). Per questo esce il PF, che e' un
    rapporto e quindi confrontabile, e il PnL MEDIO per trade nella sua unita'
    — mai due somme affiancate come se fossero la stessa cosa."""
    n = len(esiti)
    guadagni = sum(p for p in pnls if p > 0)
    perdite = -sum(p for p in pnls if p < 0)
    serie_p = serie_perdenti(esiti)
    serie_v = serie_perdenti([not e for e in esiti])
    return {
        "nome": nome, "n": n,
        "win": (sum(esiti) / n) if n else 0.0,
        "pf": (guadagni / perdite) if perdite > 0 else 0.0,
        "per_trade": (sum(pnls) / n) if n else 0.0,
        "mfe_med": sorted(mfes)[len(mfes) // 2] if mfes else 0.0,
        "perdite_max": max(serie_p) if serie_p else 0,
        "vincite_max": max(serie_v) if serie_v else 0,
        "gradini": gradini_raggiunti(mfes, mults),
    }


def stampa_confronto(gate: dict, paper: dict, mults: tuple) -> None:
    """Le due parti affiancate.

    Col paper a pochi trade il PF puo' essere 0 (nessun guadagno) o non
    calcolabile: si stampa un trattino invece di un numero che sembra una
    misura e non lo e'."""
    def _pf(d):
        return f"{d['pf']:.2f}" if d["n"] and d["pf"] > 0 else "—"

    hdr = f"  {'':<10}{'n':>6}{'win':>7}{'PF':>8}{'PnL/trade':>12}{'mfe med':>10}"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for d in (gate, paper):
        if not d["n"]:
            print(f"  {d['nome']:<10}  nessun trade")
            continue
        print(f"  {d['nome']:<10}{d['n']:>6}{d['win'] * 100:>6.0f}%{_pf(d):>8}"
              f"{d['per_trade']:>11.3f}{d['mfe_med']:>10.2f}R")

    etichette = "".join(f"{str(i) + ' TP':>9}" for i in range(len(mults) + 1))
    print()
    print(f"  gradini raggiunti (scala {'/'.join(f'{m:g}' for m in mults)})")
    print(f"  {'':<10}{'n':>6}{etichette}")
    _riga_gradini(gate["nome"], gate["gradini"])
    _riga_gradini(paper["nome"], paper["gradini"])

    print()
    print(f"  serie consecutive{'':<6}{'perdite':>10}{'vincite':>10}")
    for d in (gate, paper):
        print(f"  {d['nome']:<23}{d['perdite_max']:>10}{d['vincite_max']:>10}")


# --------------------------------------------------------------------------- #
# I TRADE DEL GATE, sulla stessa spec e la stessa scala che il bot opera        #
# --------------------------------------------------------------------------- #
def _costruisci(spec, strategy: str, ladder):
    if spec is not None:
        g = GeneratedStrategy(spec)
        if ladder:
            g.params = {**(getattr(g, "params", {}) or {}), "scale_r_mults": list(ladder)}
        return g
    for s in get_all_strategies():
        if s.name == strategy:
            return s
    return None


def trade_del_gate(symbol: str, strategy: str, spec, ladder, args):
    """Una passata sola su TUTTA la storia, non le finestre OOS.

    Le finestre OOS sono l'oggetto giusto per promuovere una coppia (pezzi di
    storia non usati per sceglierla). Per contare le serie di perdite servono
    invece i trade IN ORDINE, senza buchi: una serie spezzata dal confine fra
    due finestre verrebbe contata come due serie corte, e la risposta sarebbe
    sistematicamente ottimista."""
    make = lambda: _costruisci(spec, strategy, ladder)  # noqa: E731
    if make() is None:
        return None, "definizione della strategia non piu' nel registro"
    # MAI dati sintetici: una serie di perdite misurata su prezzi inventati
    # avrebbe l'aria di una risposta ed e' rumore.
    candles = load_candles(symbol, args.interval, args.start,
                           args.end or date.today().isoformat(),
                           prefer=args.source, allow_synthetic=False)
    if len(candles) < 300:
        return None, f"solo {len(candles)} candele"
    frame = compute_indicator_frame(candles)
    opt = WalkForwardOptimizer(n_windows=1, interval=args.interval)
    st = opt.bt.run_strategy(make(), symbol, candles, frame=frame)
    trades = sorted(st.trades, key=lambda t: float(getattr(t, "entry_ts", 0) or 0))
    return trades, None


# --------------------------------------------------------------------------- #
# PARITA': il paper entra dove entra il gate?                                  #
# --------------------------------------------------------------------------- #
def _ts(v) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def parita_ingressi(ptrades: list[dict], gtrades, tf_h: float) -> dict:
    """Quanti ingressi del paper trovano un ingresso del gate vicino nel tempo.

    Una corrispondenza non e' un timestamp identico: il segnale nasce a barra
    chiusa e il bot esegue dopo, quindi la tolleranza e' di due barre. Se un
    trade del paper non ha NESSUN ingresso del gate entro due barre, le due
    soglie non stanno vedendo la stessa cosa — ed e' il difetto che il
    proprietario sta cercando."""
    tol = 2 * tf_h * 3600
    t_gate = sorted(float(getattr(t, "entry_ts", 0) or 0) for t in gtrades)
    usati: set[int] = set()
    scarti_t: list[float] = []
    trovati = 0
    for p in ptrades:
        tp = _ts(p.get("entry_time"))
        if tp <= 0:
            continue
        migliore, delta = None, None
        for i, tg in enumerate(t_gate):
            if i in usati or tg <= 0:
                continue
            d = abs(tg - tp)
            if d <= tol and (delta is None or d < delta):
                migliore, delta = i, d
        if migliore is not None:
            usati.add(migliore)
            scarti_t.append(delta)
            trovati += 1
    return {"paper": len(ptrades), "trovati": trovati, "scarti_t": scarti_t}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", default=settings.ORCHESTRATOR_TIMEFRAME)
    ap.add_argument("--start", default="2022-01-01")
    ap.add_argument("--end", default=None)
    ap.add_argument("--source", default="binance")
    ap.add_argument("--coppie", type=int, default=8,
                    help="quante coppie rigirare, dalle piu' vissute in giu'")
    args = ap.parse_args()

    fb = get_firebase()
    tutti = [t for t in TradeLogger(fb).all_since(0.0)
             if t.get("symbol") and t.get("strategy")]
    per_coppia: dict[str, list[dict]] = defaultdict(list)
    for t in tutti:
        per_coppia[f"{t['symbol']}|{t['strategy']}"].append(t)
    if not per_coppia:
        print("[serie] il paper non ha ancora chiuso trade: niente da confrontare.")
        return 1

    n_paper = len(tutti)
    persi_paper = sum(1 for t in tutti if float(t.get("pnl", 0) or 0) <= 0)
    ordinati = sorted(tutti, key=lambda t: _ts(t.get("entry_time")))
    esiti_paper = [float(t.get("pnl", 0) or 0) > 0 for t in ordinati]
    serie_paper = serie_perdenti(esiti_paper)
    peggiore_paper = max(serie_paper) if serie_paper else 0

    print("=" * 74)
    print("SERIE DI PERDITE: quella in corso e' dentro il carattere del gate?")
    print("=" * 74)
    print(f"PAPER: {n_paper} trade chiusi · persi {persi_paper} · "
          f"serie di perdite piu' lunga finora: {peggiore_paper}")
    print(f"       coppie che hanno operato: {len(per_coppia)}\n")

    specs = decode_pairs((fb.get_doc("discovered_strategies", "specs") or {}).get("specs"))
    pairs = decode_pairs((fb.get_doc("strategy_registry", "validated") or {}).get("pairs"))
    tf_h = timeframe_hours(args.interval)

    scelte = sorted(per_coppia.items(), key=lambda kv: -len(kv[1]))[: args.coppie]
    tutti_gate: list = []
    saltate: list[tuple[str, str]] = []

    for key, ptr in scelte:
        symbol, strategy = key.split("|", 1)
        ladder = ladder_multiples((pairs.get(key) or {}).get("last_params") or {})
        mults = tuple(ladder) if ladder else tuple(settings.SCALE_OUT_R_MULTIPLES)
        scala = "/".join(f"{m:g}" for m in mults)
        print(f"── {key} · scala TP {scala}")

        gtrades, errore = trade_del_gate(symbol, strategy, specs.get(strategy),
                                         ladder, args)
        if errore:
            print(f"  GATE: non rigirabile ({errore})\n")
            saltate.append((key, errore))
            continue

        # I trade del paper IN ORDINE DI TEMPO: le serie consecutive non hanno
        # senso su una lista in ordine arbitrario, e Firestore non lo garantisce.
        ptr_ord = sorted(ptr, key=lambda t: _ts(t.get("entry_time")))
        p_mfe = [float(t["mfe_r"]) for t in ptr_ord if t.get("mfe_r") is not None]
        p_pnl = [float(t.get("pnl", 0) or 0) for t in ptr_ord]
        p_esiti = [p > 0 for p in p_pnl]

        prof_gate = profilo("GATE", [float(t.mfe_r) for t in gtrades],
                            [float(t.pnl_pct) for t in gtrades],
                            [bool(getattr(t, "is_win", False)) for t in gtrades],
                            mults)
        prof_paper = profilo("PAPER", p_mfe, p_pnl, p_esiti, mults)
        stampa_confronto(prof_gate, prof_paper, mults)

        # La serie in corso contro il metro del gate: quante volte il gate ha
        # attraversato una striscia lunga quanto questa.
        print()
        _finestre("GATE", [bool(getattr(t, "is_win", False)) for t in gtrades],
                  len(ptr_ord))

        par = parita_ingressi(ptr_ord, gtrades, tf_h)
        mancati = par["paper"] - par["trovati"]
        if par["scarti_t"]:
            med = sorted(par["scarti_t"])[len(par["scarti_t"]) // 2]
            dettaglio = f" · scarto mediano {med / 60:.0f} min"
        else:
            dettaglio = ""
        print(f"  INGRESSI: {par['trovati']}/{par['paper']} trade del paper hanno "
              f"un ingresso del gate entro 2 barre{dettaglio}")
        if mancati:
            print(f"     {mancati} SENZA riscontro: qui il paper e il gate non "
                  f"stanno guardando la stessa soglia")
        if len(p_mfe) < len(ptr_ord):
            print(f"     NB {len(ptr_ord) - len(p_mfe)} trade del paper senza "
                  f"`mfe_r`: esclusi dalle fasce, contati nel resto")
        tutti_gate.extend(gtrades)
        print()

    # ---- IL PORTAFOGLIO: e' la serie che il proprietario ha davvero vissuto --
    if tutti_gate:
        tutti_gate.sort(key=lambda t: float(getattr(t, "entry_ts", 0) or 0))
        esiti = [bool(getattr(t, "is_win", False)) for t in tutti_gate]
        primo = min(float(getattr(t, "entry_ts", 0) or 0) for t in tutti_gate)
        ultimo = max(float(getattr(t, "entry_ts", 0) or 0) for t in tutti_gate)
        print("=" * 74)
        print("TUTTE LE COPPIE INSIEME, IN ORDINE DI TEMPO")
        print("  e' il confronto giusto: i trade persi del paper stanno su "
              "strategie diverse,\n  e un conto solo li vive uno dopo l'altro, "
              "non separati per spec.")
        print("=" * 74)
        if primo > 0:
            print(f"  periodo: {dt.datetime.fromtimestamp(primo, dt.timezone.utc):%Y-%m-%d}"
                  f" → {dt.datetime.fromtimestamp(ultimo, dt.timezone.utc):%Y-%m-%d}")
        serie_g = serie_perdenti(esiti)
        print(f"  GATE: {len(esiti)} trade · vinti {sum(esiti)} "
              f"({sum(esiti) / len(esiti) * 100:.0f}%) · serie di perdite piu' "
              f"lunga: {max(serie_g) if serie_g else 0} · vincite di fila piu' "
              f"lunga: {max(serie_perdenti([not e for e in esiti]), default=0)}")
        _finestre("GATE", esiti, n_paper)
        _finestre("GATE", esiti, peggiore_paper)
        print(f"  PAPER: {n_paper} trade · persi {persi_paper} · serie di "
              f"perdite piu' lunga: {peggiore_paper}")

    if saltate:
        print(f"\n[serie] non rigirate: {len(saltate)}")
        for key, err in saltate:
            print(f"    {key}: {err}")

    print("\n" + "=" * 74)
    print("Come si legge. Se il gate ha GIA' attraversato serie lunghe quanto")
    print("quella in corso, quello che vediamo e' dentro il suo carattere e il")
    print("campione non basta per dire altro. Se non ci e' mai andato vicino,")
    print("allora la differenza non e' sfortuna e va cercata nel come operiamo.")
    print("Questo comando MISURA e basta: non scrive niente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
