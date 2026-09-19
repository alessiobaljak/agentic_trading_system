"""
Diagnostica: cosa determina il NUMERO di trade al giorno, e in che DIREZIONE.

Ricostruisce dai trade chiusi (Firestore `trades`) le metriche che spiegano il
throughput, così si vede se il collo di bottiglia e' la liquidita' (posizioni
contemporanee al tetto) o i SEGNALI (poche aperture al giorno):

  * trade al giorno (min/media/max)
  * durata media di holding
  * posizioni CONTEMPORANEE: massimo e media pesata nel tempo (sweep entry/exit)
  * coin e strategie distinte coinvolte
  * DIREZIONE: long vs short, incrociata col regime all'apertura

L'ultimo blocco nasce da una domanda del proprietario (18 settembre) a cui nessun
report sapeva rispondere: «come e' possibile che in una giornata di rialzo abbiamo
aperto 4 posizioni su 5 short?». Il conteggio esisteva solo nella dashboard, a
occhio, e nessuno lo incrociava col regime ne' col PnL — cioe' mancava proprio il
pezzo che distingue «e' il disegno» da «ci sta costando».

Sola lettura. Uso sulla VPS:
    .venv/bin/python -m scripts.trade_stats
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean, median

from bot.core.firebase_client import get_firebase
from bot.core.models import Regime
from bot.orchestrator.orchestrator import Orchestrator


def _entry_ts(t: dict) -> float | None:
    """epoch dell'apertura da entry_time (ISO) o entry_ts se presente."""
    if t.get("entry_ts") is not None:
        try:
            return float(t["entry_ts"])
        except (TypeError, ValueError):
            pass
    iso = t.get("entry_time")
    if not iso:
        return None
    try:
        return datetime.fromisoformat(str(iso).replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _dir(t: dict) -> str:
    """'long' / 'short' / '?' — `direction` e' salvato come stringa dall'enum."""
    return str(t.get("direction", "?")).lower()


def _regime(t: dict):
    """Regime AL MOMENTO DELL'APERTURA. None se assente o non riconosciuto.

    Non si inventa un default: un trade senza regime registrato non e' un trade in
    mercato laterale, e contarlo come tale falserebbe proprio la riga che questo
    report esiste per produrre."""
    v = t.get("regime_at_entry")
    if not v:
        return None
    try:
        return Regime(str(v))
    except ValueError:
        return None


def direction_report(trades: list[dict]) -> dict:
    """long vs short: quanti, come vanno, e quanti sono CONTRO il trend.

    Il conteggio da solo non basta. Aprire controtrend NON e' un errore: e' una
    scelta esplicita del disegno — il trend modula la SIZE e non mette il veto
    (`Orchestrator.decide_all`), e meta' delle feature generate sono di ritorno
    alla media, che per costruzione vendono la forza. La domanda utile quindi non
    e' «quante short?» ma «quelle short stanno pagando?». Per questo accanto a
    ogni conteggio c'e' il PnL e la mediana di mfe_r.

    Il criterio di controtrend e' preso da `Orchestrator._trend_align` invece di
    essere riscritto qui: due definizioni di controtrend che divergono sarebbero
    peggio di nessuna — e' la classe di errore piu' cara di questo progetto.
    """
    per_dir: dict[str, dict] = {}
    for d in ("long", "short"):
        sel = [t for t in trades if _dir(t) == d]
        pnl = [float(t.get("pnl", 0.0) or 0.0) for t in sel]
        mfe = [float(t.get("mfe_r", 0.0) or 0.0) for t in sel]
        per_dir[d] = {
            "trade": len(sel),
            "vinti": sum(1 for p in pnl if p > 0),
            "pnl": round(sum(pnl), 2),
            "mfe_mediana": round(median(mfe), 2) if mfe else None,
        }

    # allineamento col trend: +1 in trend, -1 controtrend, 0 regime neutro
    align: dict[str, dict] = {k: {"trade": 0, "pnl": 0.0}
                              for k in ("in_trend", "contro", "neutro", "ignoto")}
    matrice: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for t in trades:
        d = _dir(t)
        if d not in ("long", "short"):
            continue
        reg = _regime(t)
        matrice[reg.value if reg else "ignoto"][d] += 1
        if reg is None:
            key = "ignoto"
        else:
            a = Orchestrator._trend_align(reg, d)
            key = "in_trend" if a > 0 else "contro" if a < 0 else "neutro"
        align[key]["trade"] += 1
        align[key]["pnl"] += float(t.get("pnl", 0.0) or 0.0)
    for v in align.values():
        v["pnl"] = round(v["pnl"], 2)

    return {"per_direzione": per_dir, "allineamento": align,
            "matrice": {k: dict(v) for k, v in matrice.items()}}


def print_direction_report(rep: dict) -> None:
    print("\nDIREZIONE — long vs short")
    print(f"{'':6} {'trade':>6} {'vinti':>7} {'PnL':>9} {'mfe mediana':>13}")
    for d, r in rep["per_direzione"].items():
        if not r["trade"]:
            continue
        quota = f"{r['vinti']}/{r['trade']}"
        mfe = f"{r['mfe_mediana']:.2f}R" if r["mfe_mediana"] is not None else "—"
        print(f"{d:6} {r['trade']:>6} {quota:>7} {r['pnl']:>9.2f} {mfe:>13}")

    if rep["matrice"]:
        print("\nRegime ALL'APERTURA x direzione:")
        for reg, riga in sorted(rep["matrice"].items()):
            voci = " · ".join(f"{d} {n}" for d, n in sorted(riga.items()))
            print(f"  {reg:18} {voci}")

    a = rep["allineamento"]
    print("\nRispetto al trend (stesso criterio dell'orchestratore):")
    for k, etichetta in (("in_trend", "in trend"), ("contro", "CONTROTREND"),
                         ("neutro", "regime neutro"), ("ignoto", "regime ignoto")):
        if a[k]["trade"]:
            print(f"  {etichetta:15} {a[k]['trade']:>3} trade · PnL {a[k]['pnl']:>8.2f}")
    print("\nLettura: il controtrend NON e' un errore — il trend modula la size, non")
    print("mette il veto, e le strategie di ritorno alla media vendono la forza per")
    print("costruzione. Conta il PnL della riga CONTROTREND, non il suo conteggio.")


def main() -> int:
    fb = get_firebase()
    trades = fb.query_collection("trades", order_by="exit_ts")
    if not trades:
        print("Nessun trade chiuso trovato.")
        return 0

    spans = []  # (entry_ts, exit_ts) validi
    per_day: dict[str, int] = defaultdict(int)
    coins, strategies = set(), set()
    for t in trades:
        ex = t.get("exit_ts")
        en = _entry_ts(t)
        coins.add(t.get("symbol", "?"))
        strategies.add(t.get("strategy", "?"))
        if ex is None:
            continue
        day = datetime.fromtimestamp(float(ex), timezone.utc).strftime("%Y-%m-%d")
        per_day[day] += 1
        if en is not None and ex > en:
            spans.append((en, float(ex)))

    # --- posizioni contemporanee: sweep degli eventi apertura/chiusura ---
    events = []
    for en, ex in spans:
        events.append((en, 1))
        events.append((ex, -1))
    events.sort()
    cur = max_conc = 0
    prev_t = None
    area = 0.0  # integrale (posizioni * secondi) per la media pesata nel tempo
    for ts, delta in events:
        if prev_t is not None:
            area += cur * (ts - prev_t)
        cur += delta
        max_conc = max(max_conc, cur)
        prev_t = ts
    total_span = (events[-1][0] - events[0][0]) if len(events) >= 2 else 0
    avg_conc = area / total_span if total_span > 0 else 0.0

    durations_h = [(ex - en) / 3600.0 for en, ex in spans]
    counts = list(per_day.values())

    print(f"\nTrade totali analizzati: {len(trades)}  ({len(spans)} con apertura nota)")
    print(f"Giorni coperti:          {len(per_day)}")
    print(f"Trade/giorno:            min {min(counts)} · media {mean(counts):.1f} · max {max(counts)}")
    # LA RIPARTIZIONE, non solo min/media/max. La media sulla settimana non si puo'
    # confrontare con gli "attesi" di `signal_frequency`: quella sonda fa girare le
    # coppie validate di OGGI su giorni in cui il registro ne aveva meno, e su giorni
    # in cui il paper non girava ancora. Il confronto onesto e' giorno contro giorno,
    # sugli ultimi — e senza questa riga non c'era modo di farlo.
    print("  per giorno (UTC): " + " · ".join(
        f"{g} {per_day[g]}" for g in sorted(per_day)))
    if durations_h:
        print(f"Durata media holding:    {mean(durations_h):.1f}h  (min {min(durations_h):.1f}h · max {max(durations_h):.1f}h)")
    print(f"Posizioni contemporanee: MAX {max_conc} · media nel tempo {avg_conc:.1f}")
    print(f"Coin distinte:           {len(coins)}")
    print(f"Strategie distinte:      {len(strategies)}")
    print("\nLettura: se MAX contemporanee << 10 (il tetto da margine), il numero di")
    print("trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.")

    print_direction_report(direction_report(trades))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
