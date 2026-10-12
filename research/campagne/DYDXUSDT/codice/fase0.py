"""Fase 0, punti 2-3: buchi, barre tolte dall'allineamento, funding, volume per anno, mesi illiquidi.

Scrive il riepilogo in data/insample/DYDXUSDT/fase0_riepilogo.json (fuori da git): i numeri
vanno poi in fase0_dati.md.
"""
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from comune import dati, np  # noqa: E402

FINE = date(2023, 12, 31)
out = {}


def giorno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli_ts(lista, ms):
    """Comprime una lista ordinata di ts in intervalli contigui [da, a]."""
    gruppi = []
    for t in lista:
        if gruppi and t - gruppi[-1][1] == ms:
            gruppi[-1][1] = t
        else:
            gruppi.append([t, t])
    return [[giorno(a), giorno(b), int((b - a) // ms + 1)] for a, b in gruppi]


for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]:
    s = dati.carica_serie_allineate("DYDXUSDT", tf, comune.INIZIO, FINE)
    ms = comune.MS_TF[tf]
    cand = s["candele"]
    buchi = []
    for a, b in zip(cand, cand[1:]):
        if b.ts > a.close_ts + 1:
            buchi.append([giorno(a.ts), giorno(b.ts), int((b.ts - a.ts) // ms - 1)])
    ctx = comune.contesto(tf, comune.FINE_COSTRUZIONE)
    atrp = comune.atr(ctx, 14) / ctx.c
    atrp = atrp[np.isfinite(atrp)]
    out[tf] = {
        "atr14_su_close_mediano_costruzione": float(np.median(atrp)),
        "costo_giro_in_R_con_stop_2atr_mediano": 0.0014 / (2 * float(np.median(atrp))),
        "barre_tenute": len(cand),
        "prima": giorno(cand[0].ts) if cand else None,
        "ultima": giorno(cand[-1].ts) if cand else None,
        "tolte_last": s["n_tolte_last"],
        "tolte_last_intervalli": intervalli_ts(s["tolte_last"], ms),
        "tolte_mark": s["n_tolte_mark"],
        "tolte_mark_intervalli": intervalli_ts(s["tolte_mark"], ms),
        "buchi_dopo_allineamento": len(buchi),
        "buchi": buchi[:40],
        "volume_mancante": s["n_volume_mancante"],
    }
    print(tf, len(cand), s["n_tolte_last"], s["n_tolte_mark"], len(buchi), flush=True)

f = dati.carica_funding_dettaglio("DYDXUSDT", comune.INIZIO, FINE)
out["funding"] = {
    "settlement": len(f),
    "primo": giorno(f[0][0]),
    "ultimo": giorno(f[-1][0]),
    "intervalli_dichiarati": [[giorno(t), o] for t, o in dati.intervallo_funding(f)],
    "intervalli_da_distanze": [[giorno(t), o] for t, o in dati.intervallo_funding([(t, r) for t, _, r in f])][:30],
    "tasso_medio": float(np.mean([r for _, _, r in f])),
    "tasso_medio_per_anno": {},
    "quota_positivi": float(np.mean([r > 0 for _, _, r in f])),
}
per_anno = {}
for t, _, r in f:
    per_anno.setdefault(datetime.fromtimestamp(t / 1000, tz=timezone.utc).year, []).append(r)
out["funding"]["tasso_medio_per_anno"] = {str(a): float(np.mean(v)) for a, v in per_anno.items()}

medie = comune.volume_medio_mensile()
out["volume_medio_mensile_usdt"] = {f"{a}-{m:02d}": v for (a, m), v in medie.items()}
out["mesi_sotto_soglia"] = [f"{a}-{m:02d}" for (a, m), v in medie.items() if v < comune.LIQUIDITA_MINIMA]
vol_anno = {}
for anno, mese in dati.mesi_del_periodo(comune.INIZIO, FINE):
    p = dati.percorso_mese("DYDXUSDT", "klines", "1d", anno, mese)
    if p.is_file():
        for ts, v in dati.volume_usdt_da_zip(p).items():
            vol_anno.setdefault(datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year, []).append(v)
out["volume_medio_giornaliero_per_anno_usdt"] = {str(a): float(np.mean(v)) for a, v in vol_anno.items()}
out["giorni_1d_per_anno"] = {str(a): len(v) for a, v in vol_anno.items()}

btc = {}
for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]:
    b = dati.carica_candele("BTCUSDT", tf, comune.INIZIO, FINE)
    btc[tf] = {"barre": len(b), "prima": giorno(b[0].ts), "ultima": giorno(b[-1].ts)}
out["btc"] = btc

# primi mesi: il primo file disponibile del last 1d
d1 = dati.carica_candele("DYDXUSDT", "1d", comune.INIZIO, FINE)
out["primo_giorno_last_1d"] = giorno(d1[0].ts)
out["prezzo_primo_ultimo"] = [d1[0].open, d1[-1].close]

dest = comune.RADICE_REPO / "research" / "data" / "insample" / "DYDXUSDT" / "fase0_riepilogo.json"
dest.write_text(json.dumps(out, indent=1, ensure_ascii=False))
print("scritto", dest)
