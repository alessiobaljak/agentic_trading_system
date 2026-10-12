"""Fase 0 punti 2-3 di MATICUSDT: impronte, allineamento last/mark, buchi, funding, volume, mesi illiquidi.

Scrive ``campagne/MATICUSDT/impronte.json`` (impronte SHA-256 di tutti gli zip in-sample di
MATICUSDT e BTCUSDT) e ``campagne/MATICUSDT/fase0_misure.json`` (i numeri che
``fase0_dati.md`` riporta). Nessuna strategia, nessun rendimento.
"""
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from research.src import dati  # noqa: E402

TF = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
INIZIO, FINE = date(2020, 10, 1), date(2023, 12, 31)
CARTELLA = Path(__file__).resolve().parents[1]
SOGLIA = 20_000_000


def iso(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli(ts_lista, durata):
    """Comprime una lista di ts in intervalli contigui [(da, a, n)]."""
    out = []
    for t in ts_lista:
        if out and t == out[-1][1] + durata:
            out[-1][1] = t
            out[-1][2] += 1
        else:
            out.append([t, t, 1])
    return [{"da": iso(a), "a": iso(b), "barre": n} for a, b, n in out]


def buchi(candele, durata):
    """Buchi della serie: barre mancanti fra due barre consecutive (intervalli)."""
    out = []
    for p, q in zip(candele, candele[1:]):
        if q.ts > p.ts + durata:
            out.append({"dopo": iso(p.ts), "prima_di": iso(q.ts), "barre_mancanti": (q.ts - p.ts) // durata - 1})
    return out


misure = {"timeframe": {}}
for tf in TF:
    durata = dati.durata_intervallo(tf)
    s = dati.carica_serie_allineate("MATICUSDT", tf, INIZIO, FINE)
    last = dati.carica_candele("MATICUSDT", tf, INIZIO, FINE)
    mark = dati.carica_candele("MATICUSDT", tf, INIZIO, FINE, tipo="markPriceKlines")
    btc = dati.carica_candele("BTCUSDT", tf, INIZIO, FINE)
    attese = (dati.ms_da_data(FINE) + dati.MS_GIORNO - dati.ms_da_data(INIZIO)) // durata
    misure["timeframe"][tf] = {
        "barre_attese": attese,
        "barre_last": len(last),
        "barre_mark": len(mark),
        "barre_tenute": len(s["candele"]),
        "prima_barra": iso(s["candele"][0].ts),
        "ultima_barra": iso(s["candele"][-1].ts),
        "n_tolte_last": s["n_tolte_last"],
        "tolte_last": intervalli(s["tolte_last"], durata),
        "n_tolte_mark": s["n_tolte_mark"],
        "tolte_mark": intervalli(s["tolte_mark"], durata),
        "buchi_last": buchi(last, durata),
        "buchi_serie_tenuta": len(buchi(s["candele"], durata)),
        "n_volume_mancante": s["n_volume_mancante"],
        "barre_btc": len(btc),
        "buchi_btc": buchi(btc, durata),
    }

# Salti di prezzo sospetti (cambio di contratto): rapporto close/open successivo sul 1h
last1h = dati.carica_candele("MATICUSDT", "1h", INIZIO, FINE)
salti = []
for p, q in zip(last1h, last1h[1:]):
    r = q.open / p.close
    if r > 1.25 or r < 0.8:
        salti.append({"ts": iso(q.ts), "close_prima": p.close, "open_dopo": q.open})
misure["salti_apertura_oltre_20pct_1h"] = salti
misure["prezzo_min_max_1d"] = None

# Funding
righe = dati.carica_funding_dettaglio("MATICUSDT", INIZIO, FINE)
misure["funding"] = {
    "settlement": len(righe),
    "primo": iso(righe[0][0]),
    "ultimo": iso(righe[-1][0]),
    "intervalli_dichiarati": [(iso(t), o) for t, o in dati.intervallo_funding(righe)],
    "intervalli_da_distanza": [(iso(t), o) for t, o in dati.intervallo_funding([(t, x) for t, _o, x in righe])],
}

# Volume in USDT dai file 1d del last, su tutti i giorni
volumi = {}
for p in dati._percorsi_presenti("MATICUSDT", "klines", "1d", INIZIO, FINE, dati.RADICE_DEFAULT):
    for ts, v in dati.volume_usdt_da_zip(p).items():
        volumi.setdefault(ts, v)
per_mese = defaultdict(list)
per_anno = defaultdict(list)
for ts, v in sorted(volumi.items()):
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    if date(d.year, d.month, d.day) < INIZIO or date(d.year, d.month, d.day) > FINE:
        continue
    per_mese[f"{d.year}-{d.month:02d}"].append(v)
    per_anno[d.year].append(v)
media_mese = {m: sum(v) / len(v) for m, v in per_mese.items()}
misure["volume_medio_giornaliero_usdt_per_anno"] = {a: round(sum(v) / len(v)) for a, v in per_anno.items()}
misure["volume_medio_giornaliero_usdt_per_mese"] = {m: round(x) for m, x in media_mese.items()}
misure["giorni_con_volume"] = len(volumi)
misure["mesi_sotto_soglia"] = sorted(m for m, x in media_mese.items() if x < SOGLIA)

(CARTELLA / "fase0_misure.json").write_text(json.dumps(misure, indent=1, ensure_ascii=False), encoding="utf-8")

impronte = {"MATICUSDT": dati.calcola_impronte("MATICUSDT"), "BTCUSDT": dati.calcola_impronte("BTCUSDT")}
(CARTELLA / "impronte.json").write_text(json.dumps(impronte, indent=0, sort_keys=True), encoding="utf-8")
print("fatto", len(impronte["MATICUSDT"]), len(impronte["BTCUSDT"]))
