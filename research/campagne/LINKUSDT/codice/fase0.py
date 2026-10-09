"""Fase 0 punti 2-3: barre tolte dall'allineamento, buchi, funding, volume per anno, mesi illiquidi, impronte."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
from research.src import dati  # noqa: E402


def g(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli(ts_lista, passo):
    out = []
    for t in ts_lista:
        if out and t - out[-1][1] == passo:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [(g(a), g(b), (b - a) // passo + 1) for a, b in out]


rapporto = {}
for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]:
    s = C.serie(tf)
    passo = C.MS_TF[tf]
    c = s["candele"]
    buchi = []
    for a, b in zip(c, c[1:]):
        if b.ts > a.close_ts + 1:
            buchi.append((g(a.ts), g(b.ts), (b.ts - a.ts) // passo - 1))
    rapporto[tf] = {
        "barre_tenute": len(c),
        "prima": g(c[0].ts), "ultima": g(c[-1].ts),
        "n_tolte_last": s["n_tolte_last"], "tolte_last": intervalli(s["tolte_last"], passo),
        "n_tolte_mark": s["n_tolte_mark"], "tolte_mark": intervalli(s["tolte_mark"], passo),
        "buchi_dopo_allineamento": buchi,
        "n_volume_mancante": s["n_volume_mancante"],
    }

f = dati.carica_funding_dettaglio(C.SIMBOLO, C.INIZIO, C.FINE)
rapporto["funding"] = {"n": len(f), "primo": g(f[0][0]), "ultimo": g(f[-1][0]),
                       "intervalli": [(g(t), o) for t, o in dati.intervallo_funding(f)],
                       "intervalli_dalle_distanze": [(g(t), o) for t, o in dati.intervallo_funding([(a, r) for a, _, r in f])],
                       "tasso_medio_per_anno": {}}
per_anno = {}
for t, _, r in f:
    per_anno.setdefault(datetime.fromtimestamp(t / 1000, tz=timezone.utc).year, []).append(r)
rapporto["funding"]["tasso_medio_per_anno"] = {a: sum(v) / len(v) for a, v in sorted(per_anno.items())}

vol = C.volume_giornaliero_usdt()
per_anno_v, per_mese = {}, {}
for ts, v in vol.items():
    d = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
    per_anno_v.setdefault(d.year, []).append(v)
    per_mese.setdefault(f"{d.year:04d}-{d.month:02d}", []).append(v)
rapporto["volume_medio_giornaliero_usdt_per_anno"] = {a: sum(v) / len(v) for a, v in sorted(per_anno_v.items())}
rapporto["giorni_con_volume"] = len(vol)
rapporto["mesi_illiquidi"] = {m: sum(per_mese[m]) / len(per_mese[m]) for m in C.mesi_illiquidi()}

impronte = dati.registra_impronte(C.SIMBOLO)
rapporto["n_file_impronte"] = len(impronte)
out = C.CARTELLA_DATI / "fase0_rapporto.json"
out.write_text(json.dumps(rapporto, indent=1, default=str))
print(json.dumps(rapporto, indent=1, default=str)[:20000])
