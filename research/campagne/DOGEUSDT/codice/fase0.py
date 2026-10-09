"""Fase 0, punti 2-3: impronte, barre tolte dall'allineamento, buchi, funding, volume, mesi illiquidi.

Scrive i numeri in data/insample/DOGEUSDT/fase0_numeri.json; fase0_dati.md li riporta.
"""
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
from quadro import dati  # noqa: E402


def g(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli(ts_lista, ms):
    """Comprime una lista di ts in intervalli contigui (inizio, fine, barre)."""
    out = []
    for t in ts_lista:
        if out and t == out[-1][1] + ms:
            out[-1][1] = t
            out[-1][2] += 1
        else:
            out.append([t, t, 1])
    return [(g(a), g(b), n) for a, b, n in out]


ris = {"impronte": dati.registra_impronte("DOGEUSDT"), "impronte_btc": dati.registra_impronte("BTCUSDT")}
ris["n_file"] = len(ris["impronte"])
ris["n_file_btc"] = len(ris["impronte_btc"])
per_tf = {}
for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]:
    s = dati.carica_serie_allineate("DOGEUSDT", tf, q.INIZIO, q.FINE)
    ms = q.TF_MS[tf]
    c = s["candele"]
    buchi = []
    for a, b in zip(c, c[1:]):
        if b.ts > a.close_ts + 1:
            buchi.append((g(a.ts), g(b.ts), (b.ts - a.ts) // ms - 1))
    per_tf[tf] = {
        "barre_tenute": len(c),
        "prima_barra": g(c[0].ts), "ultima_barra": g(c[-1].ts),
        "n_tolte_last": s["n_tolte_last"], "tolte_last": intervalli(s["tolte_last"], ms),
        "n_tolte_mark": s["n_tolte_mark"], "tolte_mark": intervalli(s["tolte_mark"], ms),
        "n_buchi_dopo_allineamento": len(buchi), "buchi": buchi[:40],
        "barre_costruzione": sum(1 for x in c if x.close_ts <= q.FINE_COSTR_TS),
        "n_volume_mancante": s["n_volume_mancante"],
    }
ris["per_timeframe"] = per_tf
f = dati.carica_funding_dettaglio("DOGEUSDT", q.INIZIO, q.FINE)
ris["funding"] = {"n": len(f), "primo": g(f[0][0]), "ultimo": g(f[-1][0]),
                  "intervalli": [(g(t), o) for t, o in dati.intervallo_funding(f)],
                  "intervalli_da_distanza": [(g(t), o) for t, o in dati.intervallo_funding([(t, r) for t, _, r in f])][:30],
                  "medio": sum(r for *_, r in f) / len(f),
                  "quota_sopra_0_0005": sum(1 for *_, r in f if r >= 0.0005) / len(f),
                  "quota_negativi": sum(1 for *_, r in f if r < 0) / len(f)}
# volume giornaliero in USDT da tutte le candele 1d del last
per_mese = {}
per_anno = {}
for anno, mese in dati.mesi_del_periodo(q.INIZIO, q.FINE):
    p = dati.percorso_mese("DOGEUSDT", "klines", "1d", anno, mese, dati.RADICE_DEFAULT)
    if not p.is_file():
        per_mese[f"{anno}-{mese:02d}"] = None
        continue
    vol = dati.volume_usdt_da_zip(p)
    per_mese[f"{anno}-{mese:02d}"] = {"giorni": len(vol), "medio": sum(vol.values()) / len(vol)}
    per_anno.setdefault(anno, []).extend(vol.values())
ris["volume_per_mese"] = per_mese
ris["volume_medio_per_anno"] = {a: sum(v) / len(v) for a, v in per_anno.items()}
ris["mesi_illiquidi"] = sorted(f"{a}-{m:02d}" for a, m in q.mesi_illiquidi())
ris["checksum_mancanti"] = list(dati.CHECKSUM_MANCANTI)
uscita = q.RADICE_REPO / "research" / "data" / "insample" / "DOGEUSDT" / "fase0_numeri.json"
uscita.write_text(json.dumps(ris, indent=1, ensure_ascii=False))
print("fatto")
