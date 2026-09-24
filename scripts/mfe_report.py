"""
DOVE ARRIVA DAVVERO IL PREZZO — distribuzione dell'escursione favorevole in unita' di R.

A cosa serve: decidere se una scala di TP e' raggiungibile per una coppia. R e' gia'
normalizzato sulla volatilita' (R = atr_mult x ATR), quindi la domanda non e' "quanto
e' volatile la coin" ma "quanto TENDE, in unita' della sua volatilita'". Questo report
risponde con i dati, invece di tarare la scala a intuito.

Il dato chiave e' `mfe_r`, registrato su ogni trade chiuso: il massimo raggiunto a
favore, in R. Da quell'unico numero si sa quali gradini AVREBBE colpito QUALUNQUE
scala — senza doverle provare una per una ne' sacrificare trade per esplorare.

Uso (sul VPS):
    .venv/bin/python -m scripts.mfe_report
    .venv/bin/python -m scripts.mfe_report --by pair --min-trades 5
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import median

from bot.core.firebase_client import get_firebase
from bot.execution.exit_logic import SCALE_LADDER_CANDIDATES
from bot.config import settings
from bot.learning.trade_logger import TradeLogger

# soglie su cui riportare la frazione di trade che le raggiunge
REACH = (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0)

#: quante candele a 15m guardare indietro per il livello strutturale (A5):
#: 96 = un giorno, 192 = due giorni. Il secondo si usa solo se il primo non trova
#: nessun massimo/minimo oltre l'ingresso.
BARRE_STRUTTURA = 96
BARRE_STRUTTURA_LUNGHE = 192
#: quanti giorni di candele caricare PRIMA dell'ingresso: 2 giorni di barre piu'
#: un margine per i buchi della serie.
GIORNI_PRIMA_INGRESSO = 3


def _pct(a: int, b: int) -> str:
    return f"{a / b * 100:4.0f}%" if b else "   —"


# --------------------------------------------------------------------------- #
# A5 — IL LIVELLO STRUTTURALE ALL'INGRESSO (24 set 2026)                         #
# --------------------------------------------------------------------------- #
# La voce A5 del backlog dice che i take profit «non guardano il grafico»: sono
# multipli della distanza dello stop (R), non un massimo o un minimo che il
# prezzo ha gia' toccato. Il numero che l'ha fatta emergere: 19 stop su 28 sono
# andati a favore ma sotto il primo gradino (1,5R), con mfe mediana 0,84R.
# Prima di cambiare le uscite si MISURA: il livello strutturale piu' vicino
# (massimo recente per un long, minimo per uno short) viene raggiunto piu'
# spesso del primo gradino? `mfe_r` risponde anche qui senza altri dati: basta
# sapere a quanti R sta il livello e confrontarlo col massimo raggiunto.
def livello_strutturale(candles, entry_ts: float, entry: float, stop: float,
                        direction, barre: int = BARRE_STRUTTURA,
                        barre_lunghe: int = BARRE_STRUTTURA_LUNGHE) -> dict | None:
    """Il livello strutturale piu' vicino all'ingresso, in prezzo e in R.

    Guarda le ultime `barre` candele CHIUSE prima di `entry_ts` (open_time <
    entry_ts): per un long il massimo dei high SOPRA l'ingresso, per uno short il
    minimo dei low SOTTO. Se in `barre` candele non c'e' niente oltre l'ingresso
    riprova con `barre_lunghe`; se ancora niente ritorna None (nessun livello:
    il prezzo e' gia' oltre tutto quello che ha visto negli ultimi due giorni).

    Ritorna None anche senza candele prima dell'ingresso o con R <= 0 (stop sul
    prezzo d'ingresso, o dalla parte sbagliata): sono trade che si SALTANO e si
    contano, non che si stimano. `direction` accetta "long"/"short" o l'enum.
    """
    try:
        entry = float(entry)
        stop = float(stop)
        entry_ts = float(entry_ts)
    except (TypeError, ValueError):
        return None
    r = abs(entry - stop)
    if r <= 0 or entry <= 0:
        return None
    lato = str(getattr(direction, "value", direction)).lower()
    long = lato.endswith("long")      # "long", Direction.LONG o "Direction.LONG"
    prima = [c for c in (candles or []) if c.open_time.timestamp() < entry_ts]
    if not prima:
        return None
    for n in (barre, barre_lunghe):
        finestra = prima[-n:]
        if long:
            oltre = [c.high for c in finestra if c.high > entry]
            livello = max(oltre) if oltre else None
        else:
            oltre = [c.low for c in finestra if c.low < entry]
            livello = min(oltre) if oltre else None
        if livello is not None:
            return {"livello": float(livello), "lvl_r": abs(livello - entry) / r, "barre": n}
    return None


def stop_originale(t: dict) -> float | None:
    """Lo stop ORIGINALE del trade, cioe' quello che definisce R.

    Il documento del trade chiuso non porta `orig_stop` (lo tiene solo la
    posizione aperta) e `stop_price` alla chiusura e' spesso GIA' spostato a
    break-even o dal profit-lock: usarlo darebbe R = 0 o un R piu' stretto del
    vero. Il referto `post_mortem.stop_pct` pero' e' calcolato da `orig_stop` al
    momento della chiusura, quindi da li' lo stop originale si ricostruisce.
    Ordine: orig_stop (se mai comparisse) > post_mortem.stop_pct > stop_price."""
    try:
        entry = float(t.get("entry_price") or 0)
    except (TypeError, ValueError):
        return None
    if entry <= 0:
        return None
    if t.get("orig_stop"):
        try:
            return float(t["orig_stop"])
        except (TypeError, ValueError):
            pass
    pm = t.get("post_mortem") or {}
    stop_pct = pm.get("stop_pct") if isinstance(pm, dict) else None
    if stop_pct:
        try:
            frac = float(stop_pct)
        except (TypeError, ValueError):
            frac = 0.0
        if frac > 0:
            lato = str(t.get("direction", "")).lower()
            return entry * (1 - frac) if lato.endswith("long") else entry * (1 + frac)
    if t.get("stop_price"):
        try:
            return float(t["stop_price"])
        except (TypeError, ValueError):
            return None
    return None


def primo_gradino(t: dict) -> float:
    """Il primo gradino della scala del trade: la sua (`scale_r_mults`) se
    registrata, altrimenti quella globale."""
    mults = t.get("scale_r_mults") or None
    try:
        if mults:
            return min(float(m) for m in mults)
    except (TypeError, ValueError):
        pass
    return float(min(settings.SCALE_OUT_R_MULTIPLES))


def _epoch(value) -> float:
    """Epoch da un campo temporale del trade (stringa ISO o numero); 0 se manca.
    Stessa regola di `scripts.gate_vs_paper._ts`, ripetuta qui per non importare
    l'intero motore di backtest in un report che altrimenti e' leggero."""
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return datetime.fromisoformat(str(value)).timestamp()
    except (TypeError, ValueError):
        return 0.0


def riassunto_strutturale(righe: list[dict]) -> dict:
    """Conta, sulle righe misurate, quante volte il prezzo ha raggiunto il primo
    gradino, il livello strutturale e il piu' vicino dei due. Ogni riga porta
    `r1`, `lvl_r`, `mfe_r`. Pura, cosi' si testa senza Firebase ne' candele."""
    n = len(righe)
    if not n:
        return {"n": 0, "mediana_lvl_r": None, "mediana_r1": None,
                "n_tp1": 0, "n_livello": 0, "n_min": 0,
                "pct_tp1": None, "pct_livello": None, "pct_min": None,
                "n_livello_sotto_tp1": 0}
    n_tp1 = sum(1 for r in righe if r["mfe_r"] >= r["r1"] - 1e-12)
    n_lvl = sum(1 for r in righe if r["mfe_r"] >= r["lvl_r"] - 1e-12)
    n_min = sum(1 for r in righe if r["mfe_r"] >= min(r["r1"], r["lvl_r"]) - 1e-12)
    return {
        "n": n,
        "mediana_lvl_r": median(r["lvl_r"] for r in righe),
        "mediana_r1": median(r["r1"] for r in righe),
        "n_tp1": n_tp1, "n_livello": n_lvl, "n_min": n_min,
        "pct_tp1": n_tp1 / n * 100, "pct_livello": n_lvl / n * 100,
        "pct_min": n_min / n * 100,
        # quante volte il livello sta PIU' VICINO del primo gradino: se e' raro, la
        # domanda A5 e' quasi vuota (il livello non cambierebbe niente)
        "n_livello_sotto_tp1": sum(1 for r in righe if r["lvl_r"] < r["r1"]),
    }


def lettura_strutturale(ri: dict) -> str:
    """La riga «Lettura:» in parole semplici, dal riassunto."""
    if not ri["n"]:
        return "nessun trade misurabile: niente da leggere."
    verso = ("piu'" if ri["pct_livello"] > ri["pct_tp1"]
             else "meno" if ri["pct_livello"] < ri["pct_tp1"] else "tanto")
    testo = (f"il livello strutturale sta in mediana a {ri['mediana_lvl_r']:.2f}R "
             f"(primo gradino mediano {ri['mediana_r1']:.2f}R) e viene raggiunto nel "
             f"{ri['pct_livello']:.0f}% dei trade contro il {ri['pct_tp1']:.0f}% del "
             f"primo gradino: {verso} spesso"
             + ("" if verso == "tanto" else " del TP1")
             + f". Prendendo il piu' vicino dei due si arriverebbe nel "
             f"{ri['pct_min']:.0f}% dei casi; il livello e' piu' vicino del TP1 in "
             f"{ri['n_livello_sotto_tp1']} trade su {ri['n']}.")
    if ri["n"] < 20:
        testo += f" Con {ri['n']} trade e' un indizio, non una misura."
    return testo


def banked_r(mfe: float, mults, fracs) -> float:
    """R incassati da una scala, dato il massimo raggiunto (MODELLO SEMPLIFICATO).

    Ipotesi dichiarate: i gradini con multiplo <= mfe si riempiono; la frazione residua
    esce a BREAK-EVEN (0R) se almeno un gradino si e' riempito, altrimenti il trade e'
    una perdita piena (-1R). E' CONSERVATIVO sul residuo (non gli attribuisce mai un
    guadagno) e serve solo a SCEGLIERE LE CANDIDATE: la validazione vera la fa il gate,
    che simula il percorso completo con lo stop che si sposta."""
    filled = [(m, f) for m, f in zip(mults, fracs) if m <= mfe + 1e-12]
    if not filled:
        return -1.0
    banked = sum(m * f for m, f in filled)
    return banked            # il residuo esce a break-even -> non aggiunge nulla


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--by", choices=("strategy", "pair", "symbol"), default="strategy",
                    help="granularita' del raggruppamento")
    ap.add_argument("--min-trades", type=int, default=3,
                    help="gruppi con meno trade di cosi' non vengono mostrati")
    ap.add_argument("--limit", type=int, default=40, help="quanti gruppi mostrare")
    args = ap.parse_args()

    fb = get_firebase()
    trades = TradeLogger(fb).all_since(0.0)
    if not trades:
        print("[mfe] nessun trade chiuso trovato.")
        return 1

    usable = [t for t in trades if t.get("mfe_r") is not None]
    print(f"[mfe] trade chiusi: {len(trades)} · con mfe_r registrato: {len(usable)}")
    if not usable:
        print("[mfe] Nessun trade porta ancora `mfe_r`: il campo si popola sui trade")
        print("      chiusi DOPO l'aggiornamento del bot. Riprova tra qualche chiusura.")
        return 1
    print(f"[mfe] scala globale attuale: {tuple(settings.SCALE_OUT_R_MULTIPLES)} "
          f"quote {tuple(settings.SCALE_OUT_FRACTIONS)}\n")

    def key(t: dict) -> str:
        if args.by == "strategy":
            return t.get("strategy", "?")
        if args.by == "symbol":
            return t.get("symbol", "?")
        return f"{t.get('symbol', '?')}|{t.get('strategy', '?')}"

    groups: dict[str, list[float]] = defaultdict(list)
    for t in usable:
        try:
            groups[key(t)].append(float(t["mfe_r"]))
        except (TypeError, ValueError):
            continue

    rows = [(k, v) for k, v in groups.items() if len(v) >= args.min_trades]
    rows.sort(key=lambda kv: -len(kv[1]))
    shown = sum(len(v) for _, v in rows)
    if shown < len(usable):
        print(f"[mfe] {len(usable) - shown} trade su {len(usable)} sono in gruppi sotto "
              f"--min-trades {args.min_trades} e NON compaiono nelle righe per gruppo "
              f"(compaiono solo nel TOTALE).")
    # TOTALE sempre in testa: con i trade sparsi su molti gruppi le righe per gruppo
    # sono tutte sotto soglia e l'aggregato e' l'unico numero con una statistica.
    # Va letto per primo: dice se l'edge c'e', prima di chiedersi DOVE sia.
    all_vals = [v for vals in groups.values() for v in vals]
    rows = [("TOTALE (tutti i trade)", all_vals)] + rows

    # --- 1) quanto lontano arriva il prezzo -------------------------------- #
    head = "gruppo".ljust(34) + "n".rjust(4) + "  mediana" + \
        "".join(f"  ≥{r:g}R".rjust(7) for r in REACH)
    print(head)
    print("-" * len(head))
    for k, vals in rows[: args.limit]:
        vals_sorted = sorted(vals)
        med = vals_sorted[len(vals_sorted) // 2]
        line = k[:33].ljust(34) + str(len(vals)).rjust(4) + f"{med:9.2f}"
        for r in REACH:
            line += _pct(sum(1 for v in vals if v >= r), len(vals)).rjust(7)
        print(line)

    # --- 2) quale scala avrebbe incassato di piu' -------------------------- #
    fracs = tuple(settings.SCALE_OUT_FRACTIONS)
    # ---- GLI STOP, DIVISI PER COME SONO MORTI ---------------------------------
    # Domanda del proprietario (21 set 2026): «alcune posizioni erano in positivo
    # per due o tre ore, non hanno toccato il primo take profit, e poi stop loss.
    # Siamo entrati proprio sbagliati, o ci siamo avvicinati e il TP andava tarato
    # piu' basso?». Sono due morti diverse e si curano in modo diverso: la prima
    # e' un problema di INGRESSO (la strategia sbaglia direzione), la seconda di
    # USCITA (il primo gradino e' troppo lontano, o la protezione scatta tardi).
    # `mfe_r` le distingue senza altri dati: sotto 0,25R non e' mai andata a
    # favore; fra 0,25R e il primo gradino ci e' andata e non e' bastato.
    stop = [t for t in usable if str(t.get("exit_reason", "")) in ("stop_loss", "ExitReason.STOP_LOSS")]
    if stop:
        primo = float(settings.SCALE_OUT_R_MULTIPLES[0])
        sbagliati = [t for t in stop if float(t["mfe_r"]) < 0.25]
        quasi = [t for t in stop if 0.25 <= float(t["mfe_r"]) < primo]
        oltre = [t for t in stop if float(t["mfe_r"]) >= primo]
        print(f"\nSTOP LOSS divisi per come sono morti ({len(stop)} su {len(usable)} trade):")
        print(f"  sbagliati dall'inizio (mfe < 0.25R) .......... {len(sbagliati):>3} "
              f"{_pct(len(sbagliati), len(stop))}   -> problema di INGRESSO")
        print(f"  andati a favore ma sotto il 1° gradino ....... {len(quasi):>3} "
              f"{_pct(len(quasi), len(stop))}   -> problema di USCITA")
        print(f"  oltre il 1° gradino e poi stop ............... {len(oltre):>3} "
              f"{_pct(len(oltre), len(stop))}   -> protezione del profitto")
        if quasi:
            q = sorted(float(t["mfe_r"]) for t in quasi)
            med = q[len(q) // 2]
            print(f"  fra i «quasi»: mfe mediana {med:.2f}R, massima {q[-1]:.2f}R; "
                  f"con un primo gradino a {med:.2f}R meta' di loro avrebbe incassato")
        print("  (il primo gradino qui e' quello GLOBALE; per coppia vale la sua scala)")

    print(f"\nR medi incassati per scala (modello semplificato, quote {fracs}):")
    head2 = "gruppo".ljust(34) + "n".rjust(4) + \
        "".join(f"  {'/'.join(f'{m:g}' for m in c)}".rjust(14) for c in SCALE_LADDER_CANDIDATES)
    print(head2)
    print("-" * len(head2))
    for k, vals in rows[: args.limit]:
        line = k[:33].ljust(34) + str(len(vals)).rjust(4)
        scores = [sum(banked_r(v, c, fracs) for v in vals) / len(vals)
                  for c in SCALE_LADDER_CANDIDATES]
        best = max(range(len(scores)), key=lambda i: scores[i])
        for i, sc in enumerate(scores):
            cell = f"{sc:+.3f}" + (" *" if i == best else "  ")
            line += cell.rjust(14)
        print(line)

    print("\n(*) scala col miglior R medio in questo gruppo, secondo il modello")
    print("    semplificato: gradini raggiunti = incassati, residuo a break-even.")
    print("    Serve a SCEGLIERE le candidate — la validazione vera la fa il GATE,")
    print("    che simula il percorso completo con lo stop che si sposta.")
    print("    Campioni piccoli non decidono nulla: guardare la colonna n.")

    # --- 3) il livello strutturale all'ingresso (A5) ------------------------ #
    # Best-effort: e' una misura in piu', non deve rompere il report sopra se la
    # rete o le candele mancano.
    try:
        sezione_strutturale(usable, righe_max=args.limit)
    except Exception as exc:  # noqa: BLE001
        print(f"\n[mfe] sezione livello strutturale saltata: {exc}")
    return 0


def _carica_candele_per_coin(trades: list[dict]) -> dict[str, list]:
    """UNA chiamata a `load_candles` per coin, con la finestra che copre tutti i
    suoi trade: da 3 giorni prima del primo ingresso al giorno dopo l'ultima
    uscita. Il «giorno dopo» serve perche' `load_candles` taglia a `end` alle
    00:00 UTC: con end = giorno dell'uscita un trade aperto e chiuso lo stesso
    giorno resterebbe senza le sue ultime 24 ore di candele. Solo dati reali:
    su una serie finta il livello sarebbe finto."""
    from backtesting.data_loader import load_candles

    finestre: dict[str, list[float]] = {}
    for t in trades:
        sym = t.get("symbol")
        e_ts = _epoch(t.get("entry_time") or t.get("entry_ts"))
        x_ts = _epoch(t.get("exit_ts") or t.get("exit_time")) or e_ts
        if not sym or not e_ts:
            continue
        f = finestre.setdefault(sym, [e_ts, x_ts])
        f[0], f[1] = min(f[0], e_ts), max(f[1], x_ts)

    domani = datetime.now(timezone.utc) + timedelta(days=1)
    out: dict[str, list] = {}
    for sym, (e_ts, x_ts) in finestre.items():
        start = (datetime.fromtimestamp(e_ts, tz=timezone.utc)
                 - timedelta(days=GIORNI_PRIMA_INGRESSO)).strftime("%Y-%m-%d")
        end_dt = min(datetime.fromtimestamp(x_ts, tz=timezone.utc) + timedelta(days=1), domani)
        try:
            out[sym] = load_candles(sym, "15m", start, end_dt.strftime("%Y-%m-%d"),
                                    prefer="auto", allow_synthetic=False) or []
        except Exception as exc:  # noqa: BLE001
            print(f"[mfe] {sym}: candele non caricate ({exc}) -> trade saltati")
            out[sym] = []
    return out


def sezione_strutturale(usable: list[dict], righe_max: int = 40) -> dict:
    """Stampa la sezione «LIVELLO STRUTTURALE all'ingresso (A5)» e ritorna il
    riassunto (per chi la chiama da codice). Un trade senza candele, senza stop
    o senza livello si salta e si conta: fail-open, mai una stima al suo posto."""
    print("\nLIVELLO STRUTTURALE all'ingresso (A5, passo 1: misurare)")
    print("  livello = massimo (long) / minimo (short) delle ultime 96 candele a 15m")
    print("  oltre il prezzo d'ingresso (192 se in 96 non c'e' niente), in R dello stop.")
    candele = _carica_candele_per_coin(usable)

    righe: list[dict] = []
    saltati: dict[str, int] = defaultdict(int)
    for t in usable:
        e_ts = _epoch(t.get("entry_time") or t.get("entry_ts"))
        try:
            entry = float(t.get("entry_price") or 0)
            mfe_r = float(t["mfe_r"])
        except (TypeError, ValueError, KeyError):
            saltati["senza prezzo/mfe"] += 1
            continue
        if not e_ts or entry <= 0 or not t.get("direction"):
            saltati["senza data/prezzo/direzione"] += 1
            continue
        stop = stop_originale(t)
        if stop is None or abs(entry - stop) <= 0:
            saltati["senza stop (o stop = ingresso)"] += 1
            continue
        cs = candele.get(t.get("symbol"), [])
        if not cs:
            saltati["senza candele"] += 1
            continue
        liv = livello_strutturale(cs, e_ts, entry, stop, t["direction"])
        if liv is None:
            saltati["livello assente (prezzo gia' oltre tutto, o nessuna candela prima)"] += 1
            continue
        righe.append({
            "ts": e_ts, "symbol": t.get("symbol", "?"), "strategy": t.get("strategy", "?"),
            "direction": str(t["direction"]).lower().split(".")[-1], "r1": primo_gradino(t),
            "lvl_r": liv["lvl_r"], "mfe_r": mfe_r, "barre": liv["barre"],
        })

    righe.sort(key=lambda r: r["ts"])
    if righe:
        head = ("coin".ljust(12) + "strategia".ljust(24) + "dir".ljust(6) + "r1".rjust(6)
                + "lvl_r".rjust(7) + "mfe_r".rjust(7) + "  TP1?" + "  liv?" + "  min?")
        print("\n" + head)
        print("-" * len(head))
        for r in righe[-righe_max:]:
            tp1 = r["mfe_r"] >= r["r1"] - 1e-12
            lv = r["mfe_r"] >= r["lvl_r"] - 1e-12
            print(r["symbol"][:11].ljust(12) + r["strategy"][:23].ljust(24)
                  + r["direction"][:5].ljust(6) + f"{r['r1']:6.2f}" + f"{r['lvl_r']:7.2f}"
                  + f"{r['mfe_r']:7.2f}"
                  + ("   si " if tp1 else "   no ") + ("   si " if lv else "   no ")
                  + ("   si " if (tp1 or lv) else "   no "))
        if len(righe) > righe_max:
            print(f"(mostrati i {righe_max} piu' recenti su {len(righe)})")

    ri = riassunto_strutturale(righe)
    n_salt = sum(saltati.values())
    print(f"\n  trade misurati: {ri['n']} · saltati: {n_salt}"
          + (" (" + ", ".join(f"{k}: {v}" for k, v in saltati.items()) + ")" if n_salt else ""))
    if ri["n"]:
        print(f"  livello strutturale mediano: {ri['mediana_lvl_r']:.2f}R "
              f"(primo gradino mediano {ri['mediana_r1']:.2f}R)")
        print(f"  raggiunto il primo gradino (TP1) ........ {ri['n_tp1']:>3} {_pct(ri['n_tp1'], ri['n'])}")
        print(f"  raggiunto il livello strutturale ........ {ri['n_livello']:>3} {_pct(ri['n_livello'], ri['n'])}")
        print(f"  raggiunto il piu' vicino dei due ........ {ri['n_min']:>3} {_pct(ri['n_min'], ri['n'])}")
    print(f"  Lettura: {lettura_strutturale(ri)}")
    return {**ri, "saltati": dict(saltati)}


if __name__ == "__main__":
    raise SystemExit(main())
