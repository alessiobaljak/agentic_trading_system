"""Fase 0, punto 3: buchi, allineamento last/mark, funding, volume per anno e mesi sotto soglia.

Scrive il risultato in data/insample/BTCUSDT/fase0_analisi.json (fuori da git): i numeri
si riportano poi in fase0_dati.md.
"""
import json
from datetime import date, datetime, timezone

from comune import SIMBOLO, TIMEFRAME, CARTELLA, dati

INIZIO, FINE = date(2020, 1, 1), date(2023, 12, 31)
USCITA = CARTELLA.parents[1] / "data" / "insample" / SIMBOLO / "fase0_analisi.json"


def iso(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def buchi(candele, ms):
    out = []
    for a, b in zip(candele, candele[1:]):
        if b.ts != a.ts + ms:
            out.append({"dopo": iso(a.ts), "prima_di": iso(b.ts), "barre_mancanti": (b.ts - a.ts) // ms - 1})
    return out


rep = {"timeframe": {}}
for tf in TIMEFRAME:
    ms = dati.durata_intervallo(tf)
    last = dati.carica_candele(SIMBOLO, tf, INIZIO, FINE)
    mark = dati.carica_candele(SIMBOLO, tf, INIZIO, FINE, tipo="markPriceKlines")
    sl, sm = {c.ts for c in last}, {c.ts for c in mark}
    attese = (dati.ms_da_data(date(2024, 1, 1)) - dati.ms_da_data(INIZIO)) // ms
    solo_last = sorted(sl - sm)
    solo_mark = sorted(sm - sl)
    comuni = sorted(sl & sm)
    rep["timeframe"][tf] = {
        "barre_attese": attese, "barre_last": len(last), "barre_mark": len(mark), "barre_comuni": len(comuni),
        "buchi_last": buchi(last, ms)[:30], "n_buchi_last": len(buchi(last, ms)),
        "n_buchi_mark": len(buchi(mark, ms)),
        "tolte_perche_manca_il_mark": len(solo_last), "tolte_perche_manca_il_last": len(solo_mark),
        "esempi_tolte_mark": [iso(t) for t in solo_last[:10]],
        "prima": iso(last[0].ts) if last else None, "ultima": iso(last[-1].ts) if last else None,
        "barre_anomale_high_lt_low": sum(1 for c in last if c.high < c.low or c.open <= 0),
    }
    print(tf, rep["timeframe"][tf]["barre_last"], rep["timeframe"][tf]["barre_comuni"], flush=True)

# funding
righe = dati.carica_funding_dettaglio(SIMBOLO, INIZIO, FINE)
rep["funding"] = {
    "settlement": len(righe), "primo": iso(righe[0][0]), "ultimo": iso(righe[-1][0]),
    "intervalli_dichiarati": [(iso(t), o) for t, o in dati.intervallo_funding(righe)],
    "intervalli_da_distanza": [(iso(t), o) for t, o in dati.intervallo_funding([(t, r) for t, _o, r in righe])][:40],
    "tasso_medio_per_anno": {},
}
per_anno = {}
for t, _o, r in righe:
    per_anno.setdefault(datetime.fromtimestamp(t / 1000, tz=timezone.utc).year, []).append(r)
rep["funding"]["tasso_medio_per_anno"] = {a: sum(v) / len(v) for a, v in sorted(per_anno.items())}

# volume in USDT (quote_volume delle candele giornaliere)
qv = {}
for anno, mese in dati.mesi_del_periodo(INIZIO, FINE):
    p = dati.percorso_mese(SIMBOLO, "klines", "1d", anno, mese)
    for r in dati.righe_csv_da_zip(p):
        qv.setdefault(dati.normalizza_ts(r[0]), float(r[7]))
mesi, anni = {}, {}
for ts, v in qv.items():
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    mesi.setdefault(f"{d.year:04d}-{d.month:02d}", []).append(v)
    anni.setdefault(d.year, []).append(v)
rep["volume_medio_giornaliero_usdt_per_anno"] = {a: round(sum(v) / len(v)) for a, v in sorted(anni.items())}
rep["volume_minimo_mensile"] = min((sum(v) / len(v), m) for m, v in mesi.items())
rep["mesi_sotto_20_milioni"] = sorted(m for m, v in mesi.items() if sum(v) / len(v) < 20_000_000)
rep["impronte"] = len(dati.calcola_impronte(SIMBOLO))
USCITA.write_text(json.dumps(rep, indent=1, default=str))
print("fatto")
