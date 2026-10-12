"""Fase 0, punto 3: buchi, barre tolte dall'allineamento last/mark, funding, volume per anno e per mese.

Scrive il riepilogo in research/data/insample/ADAUSDT/fase0.json (fuori da git) e lo stampa.
"""
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

RADICE = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RADICE))

from research.src import dati  # noqa: E402

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)


def g(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli(ts_lista, passo):
    """Raggruppa ts consecutivi (distanti un passo) in intervalli [primo, ultimo]."""
    out = []
    for t in ts_lista:
        if out and t - out[-1][1] == passo:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [(g(a), g(b), (b - a) // passo + 1) for a, b in out]


ris = {"timeframe": {}}
for tf in TF:
    passo = dati.durata_intervallo(tf)
    s = dati.carica_serie_allineate("ADAUSDT", tf, INIZIO, FINE)
    c = s["candele"]
    attese = (dati.ms_da_data(date(2024, 1, 1)) - dati.ms_da_data(INIZIO)) // passo
    buchi = []
    for a, b in zip(c, c[1:]):
        if b.ts > a.close_ts + 1:
            buchi.append((g(a.ts), g(b.ts), (b.ts - a.ts) // passo - 1))
    btc = dati.carica_candele("BTCUSDT", tf, INIZIO, FINE)
    ris["timeframe"][tf] = {
        "barre_tenute": len(c),
        "barre_attese_calendario": attese,
        "prima": g(c[0].ts), "ultima": g(c[-1].ts),
        "n_tolte_last": s["n_tolte_last"], "tolte_last": intervalli(s["tolte_last"], passo),
        "n_tolte_mark": s["n_tolte_mark"], "tolte_mark": intervalli(s["tolte_mark"], passo),
        "buchi_dopo_allineamento": buchi,
        "n_volume_mancante": s["n_volume_mancante"],
        "btc_barre": len(btc),
    }

# funding
fd = dati.carica_funding_dettaglio("ADAUSDT", INIZIO, FINE)
ris["funding"] = {
    "n_settlement": len(fd), "primo": g(fd[0][0]), "ultimo": g(fd[-1][0]),
    "intervalli_dichiarati": [(g(t), o) for t, o in dati.intervallo_funding(fd)],
    "intervalli_da_distanza": [(g(t), o) for t, o in dati.intervallo_funding([(t, r) for t, _, r in fd])],
    "tasso_medio_per_anno": {},
}
per_anno = defaultdict(list)
for t, _, r in fd:
    per_anno[datetime.fromtimestamp(t / 1000, tz=timezone.utc).year].append(r)
ris["funding"]["tasso_medio_per_anno"] = {a: sum(v) / len(v) for a, v in sorted(per_anno.items())}

# volume in USDT dai file 1d del last, tutti i giorni
vol = {}
for p in dati._percorsi_presenti("ADAUSDT", "klines", "1d", INIZIO, FINE, dati.RADICE_DEFAULT):
    for ts, v in dati.volume_usdt_da_zip(p).items():
        vol.setdefault(ts, v)
per_mese = defaultdict(list)
per_anno_v = defaultdict(list)
for ts, v in vol.items():
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    if date(d.year, d.month, d.day) > FINE:
        continue
    per_mese[f"{d.year}-{d.month:02d}"].append(v)
    per_anno_v[d.year].append(v)
ris["volume_medio_giorno_usdt_per_anno"] = {a: sum(v) / len(v) for a, v in sorted(per_anno_v.items())}
ris["volume_medio_giorno_usdt_per_mese"] = {m: sum(v) / len(v) for m, v in sorted(per_mese.items())}
ris["giorni_volume"] = len(vol)
ris["mesi_sotto_20M"] = [m for m, v in sorted(per_mese.items()) if sum(v) / len(v) < 20_000_000]

out = RADICE / "research" / "data" / "insample" / "ADAUSDT" / "fase0.json"
out.write_text(json.dumps(ris, indent=1, default=str), encoding="utf-8")
for tf, d in ris["timeframe"].items():
    print(tf, {k: v for k, v in d.items() if k not in ("tolte_last", "tolte_mark", "buchi_dopo_allineamento")},
          "tolte_last", d["tolte_last"][:6], "tolte_mark", d["tolte_mark"][:6], "buchi", len(d["buchi_dopo_allineamento"]))
print("funding", {k: v for k, v in ris["funding"].items()})
print("volume anno", ris["volume_medio_giorno_usdt_per_anno"])
print("mesi sotto 20M", ris["mesi_sotto_20M"])
print("giorni volume", ris["giorni_volume"])
