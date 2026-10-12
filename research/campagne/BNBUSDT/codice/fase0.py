"""Fase 0, punti 2 e 3: allineamento last/mark, buchi, funding, volume, mesi sotto la liquidita' minima."""
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402
from research.src.dati import RADICE_DEFAULT  # noqa: E402

S = "BNBUSDT"
INIZIO = dati.date(2020, 2, 1)
FINE = dati.date(2023, 12, 31)
SOGLIA = 20_000_000


def g(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli_ts(lista, passo):
    """Raggruppa ts consecutivi (distanza = passo) in intervalli [primo, ultimo]."""
    out = []
    for t in lista:
        if out and t - out[-1][1] == passo:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [(g(a), g(b), (b - a) // passo + 1) for a, b in out]


rep = {"allineamento": {}, "buchi_last": {}}
for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]:
    passo = dati.durata_intervallo(tf)
    s = dati.carica_serie_allineate(S, tf, INIZIO, FINE)
    c = s["candele"]
    last = dati.carica_candele(S, tf, INIZIO, FINE)
    buchi = []
    for a, b in zip(last, last[1:]):
        if b.ts > a.close_ts + 1:
            buchi.append((g(a.ts), g(b.ts), (b.ts - a.ts) // passo - 1))
    rep["buchi_last"][tf] = {"n": len(buchi), "elenco": buchi[:20]}
    rep["allineamento"][tf] = {
        "barre_last": len(last), "barre_tenute": len(c),
        "n_tolte_last": s["n_tolte_last"], "n_tolte_mark": s["n_tolte_mark"],
        "intervalli_tolte_last": intervalli_ts(s["tolte_last"], passo)[:30],
        "intervalli_tolte_mark": intervalli_ts(s["tolte_mark"], passo)[:30],
        "prima": g(c[0].ts), "ultima": g(c[-1].ts),
    }

fd = dati.carica_funding_dettaglio(S, INIZIO, FINE)
rep["funding"] = {"n": len(fd), "primo": g(fd[0][0]), "ultimo": g(fd[-1][0]),
                  "intervalli": [(g(t), o) for t, o in dati.intervallo_funding(fd)],
                  "intervalli_da_distanza": [(g(t), o) for t, o in dati.intervallo_funding([(t, r) for t, _, r in fd])][:20]}

# volume giornaliero in USDT dai file 1d del last, tutti i giorni
vol = {}
cartella = RADICE_DEFAULT / "data" / "insample" / S / "klines" / "1d"
for p in sorted(cartella.glob("*.zip")):
    vol.update(dati.volume_usdt_da_zip(p))
per_mese = defaultdict(list)
per_anno = defaultdict(list)
for ts, v in vol.items():
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    if not (INIZIO <= d.date() <= FINE):
        continue
    per_mese[(d.year, d.month)].append(v)
    per_anno[d.year].append(v)
rep["volume_medio_giornaliero_usdt_per_anno"] = {a: sum(v) / len(v) for a, v in sorted(per_anno.items())}
rep["volume_medio_giornaliero_usdt_per_mese"] = {f"{a}-{m:02d}": sum(v) / len(v) for (a, m), v in sorted(per_mese.items())}
rep["mesi_sotto_soglia"] = [f"{a}-{m:02d}" for (a, m), v in sorted(per_mese.items()) if sum(v) / len(v) < SOGLIA]
rep["giorni_con_volume"] = len([1 for v in per_anno.values() for _ in v])

uscita = RADICE_DEFAULT / "data" / "insample" / S / "fase0_rapporto.json"
uscita.write_text(json.dumps(rep, indent=1, default=str), encoding="utf-8")
print(json.dumps(rep, indent=1, default=str)[:12000])
