"""
Diagnostica: cosa determina il NUMERO di trade al giorno.

Ricostruisce dai trade chiusi (Firestore `trades`) le metriche che spiegano il
throughput, così si vede se il collo di bottiglia e' la liquidita' (posizioni
contemporanee al tetto) o i SEGNALI (poche aperture al giorno):

  * trade al giorno (min/media/max)
  * durata media di holding
  * posizioni CONTEMPORANEE: massimo e media pesata nel tempo (sweep entry/exit)
  * coin e strategie distinte coinvolte

Sola lettura. Uso sulla VPS:
    .venv/bin/python -m scripts.trade_stats
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from statistics import mean

from bot.core.firebase_client import get_firebase


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
    if durations_h:
        print(f"Durata media holding:    {mean(durations_h):.1f}h  (min {min(durations_h):.1f}h · max {max(durations_h):.1f}h)")
    print(f"Posizioni contemporanee: MAX {max_conc} · media nel tempo {avg_conc:.1f}")
    print(f"Coin distinte:           {len(coins)}")
    print(f"Strategie distinte:      {len(strategies)}")
    print("\nLettura: se MAX contemporanee << 10 (il tetto da margine), il numero di")
    print("trade e' limitato dai SEGNALI, non dalla liquidita'. Trade/giorno ~= segnali/giorno.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
