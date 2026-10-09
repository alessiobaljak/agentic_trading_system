"""Fase 0, punti 2-3: impronte, barre tolte dall'allineamento, buchi, funding, volume, mesi illiquidi.

Scrive codice/mesi_esclusi.json, impronte.json e un riassunto in data/insample/ETCUSDT/uscite/fase0.json
(da cui si compila a mano fase0_dati.md).
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

SIMBOLO = "ETCUSDT"
CART = Path(__file__).resolve().parent.parent
USCITE = Path(__file__).resolve().parents[3] / "data" / "insample" / SIMBOLO / "uscite"
USCITE.mkdir(parents=True, exist_ok=True)
TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)
SOGLIA = 20_000_000


def g(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli_ts(lista, passo):
    """Comprime ts consecutivi in intervalli (inizio, fine, quante barre)."""
    out = []
    for ts in lista:
        if out and ts - out[-1][1] == passo:
            out[-1][1] = ts
            out[-1][2] += 1
        else:
            out.append([ts, ts, 1])
    return [(g(a), g(b), n) for a, b, n in out]


ris = {}

# impronte
imp = dati.calcola_impronte(SIMBOLO)
imp_btc = dati.calcola_impronte("BTCUSDT")
with open(CART / "impronte.json", "w", encoding="utf-8") as f:
    json.dump({"ETCUSDT": imp, "BTCUSDT": imp_btc}, f, indent=0, sort_keys=True)
ris["n_file_etc"] = len(imp)
ris["n_file_btc"] = len(imp_btc)
ris["impronta_file_impronte"] = dati.impronta_file(CART / "impronte.json")

# allineamento e buchi per timeframe
ris["timeframe"] = {}
for tf in TF:
    passo = dati.durata_intervallo(tf)
    al = dati.carica_serie_allineate(SIMBOLO, tf, INIZIO, FINE)
    c = al["candele"]
    buchi = []
    for a, b in zip(c, c[1:]):
        if b.ts > a.close_ts + 1:
            buchi.append((g(a.ts), g(b.ts), (b.ts - a.ts) // passo - 1))
    ris["timeframe"][tf] = {
        "barre": len(c),
        "prima": g(c[0].ts) if c else None,
        "ultima": g(c[-1].ts) if c else None,
        "n_tolte_last": al["n_tolte_last"],
        "tolte_last": intervalli_ts(al["tolte_last"], passo),
        "n_tolte_mark": al["n_tolte_mark"],
        "tolte_mark": intervalli_ts(al["tolte_mark"], passo),
        "n_buchi_dopo_allineamento": len(buchi),
        "buchi": buchi[:60],
        "n_volume_mancante": al["n_volume_mancante"],
    }
    btc = dati.carica_candele("BTCUSDT", tf, INIZIO, FINE)
    ris["timeframe"][tf]["btc_barre"] = len(btc)
    ris["timeframe"][tf]["btc_prima"] = g(btc[0].ts) if btc else None

# funding
fd = dati.carica_funding_dettaglio(SIMBOLO, INIZIO, FINE)
ris["funding"] = {
    "n": len(fd),
    "primo": g(fd[0][0]),
    "ultimo": g(fd[-1][0]),
    "intervalli": [(g(t), o) for t, o in dati.intervallo_funding(fd)],
    "intervalli_da_distanza": [(g(t), o) for t, o in dati.intervallo_funding([(t, r) for t, _, r in fd])][:40],
    "tasso_medio_per_anno": {},
}
for anno in (2020, 2021, 2022, 2023):
    v = [r for t, _, r in fd if datetime.fromtimestamp(t / 1000, tz=timezone.utc).year == anno]
    ris["funding"]["tasso_medio_per_anno"][anno] = sum(v) / len(v) if v else None

# volume in USDT dai file 1d del last, tutti i giorni
vol = {}
for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
    p = dati.percorso_mese(SIMBOLO, "klines", "1d", anno, mese, dati.RADICE_DEFAULT)
    if p.is_file():
        vol.update(dati.volume_usdt_da_zip(p))
per_mese = {}
per_anno = {}
for ts, v in sorted(vol.items()):
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    if d.date() > FINE:
        continue
    per_mese.setdefault(d.strftime("%Y-%m"), []).append(v)
    per_anno.setdefault(d.year, []).append(v)
medie_mese = {m: sum(v) / len(v) for m, v in per_mese.items()}
esclusi = sorted(m for m, v in medie_mese.items() if v < SOGLIA)
ris["volume_medio_giornaliero_per_anno"] = {a: sum(v) / len(v) for a, v in per_anno.items()}
ris["giorni_per_anno"] = {a: len(v) for a, v in per_anno.items()}
ris["volume_medio_giornaliero_per_mese"] = medie_mese
ris["mesi_esclusi"] = esclusi
with open(Path(__file__).resolve().parent / "mesi_esclusi.json", "w", encoding="utf-8") as f:
    json.dump({"soglia_usdt_giorno": SOGLIA, "fonte": "file 1d del last, colonna quote_volume (volume_usdt_da_zip), media su tutti i giorni del mese",
               "mesi_esclusi": esclusi}, f, indent=1)
ris["checksum_mancanti"] = list(dati.CHECKSUM_MANCANTI)

with open(USCITE / "fase0.json", "w", encoding="utf-8") as f:
    json.dump(ris, f, indent=1, default=str)
print(json.dumps({k: v for k, v in ris.items() if k != "timeframe"}, indent=1, default=str))
for tf, v in ris["timeframe"].items():
    print(tf, {k: v[k] for k in ("barre", "prima", "n_tolte_last", "n_tolte_mark", "n_buchi_dopo_allineamento", "btc_barre")})
