"""Fase 0, punti 2-4: descrizione dei dati di MASKUSDT (nessuna strategia, nessun risultato).

Scrive in data/insample/MASKUSDT/fase0.json: per timeframe barre tenute e tolte
(con gli intervalli di date), buchi del last, funding (intervalli e copertura),
volume medio giornaliero in USDT per anno e per mese, mesi sotto la soglia,
ATR mediano in percentuale del prezzo (per stimare i costi in R prima delle previsioni).
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODICE))

import quadro  # noqa: E402
from indicatori import atr, colonne  # noqa: E402
from research.src import dati  # noqa: E402


def iso(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli(ts_list, ms):
    """Raggruppa ts consecutivi (passo ms) in intervalli [da, a]."""
    out = []
    for t in ts_list:
        if out and t - out[-1][1] == ms:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [(iso(a), iso(b), int((b - a) // ms + 1)) for a, b in out]


def main():
    res = {"tf": {}}
    vol_mese = quadro.mesi_illiquidi()
    res["volume_medio_giornaliero_usdt_per_mese"] = vol_mese
    per_anno = {}
    for m, v in vol_mese.items():
        per_anno.setdefault(m[:4], []).append(v)
    # media per anno sui giorni (non sui mesi): ricalcolo dai giorni
    volumi = {}
    for p in dati._percorsi_presenti("MASKUSDT", "klines", "1d", quadro.INIZIO, quadro.FINE, dati.RADICE_DEFAULT):
        for ts, v in dati.volume_usdt_da_zip(p).items():
            volumi.setdefault(ts, v)
    anni = {}
    for ts, v in volumi.items():
        anni.setdefault(iso(ts)[:4], []).append(v)
    res["volume_medio_giornaliero_usdt_per_anno"] = {a: float(np.mean(v)) for a, v in sorted(anni.items())}
    res["giorni_con_volume"] = len(volumi)
    res["mesi_sotto_soglia"] = [m for m, v in vol_mese.items() if v < quadro.SOGLIA_LIQUIDITA]
    f = dati.carica_funding_dettaglio("MASKUSDT", quadro.INIZIO, quadro.FINE)
    res["funding"] = {"n": len(f), "primo": iso(f[0][0]) if f else None, "ultimo": iso(f[-1][0]) if f else None,
                      "intervalli_dichiarati": [(iso(t), o) for t, o in dati.intervallo_funding(f)],
                      "intervalli_dalle_distanze": [(iso(t), o) for t, o in
                                                    dati.intervallo_funding([(t, r) for t, _, r in f])],
                      "tasso_mediano": float(np.median([r for _, _, r in f])) if f else None}
    for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]:
        ms = dati.durata_intervallo(tf)
        s = dati.carica_serie_allineate("MASKUSDT", tf, quadro.INIZIO, quadro.FINE)
        c = s["candele"]
        buchi = []
        for a, b in zip(c, c[1:]):
            if b.ts > a.close_ts + 1:
                buchi.append((iso(a.ts), iso(b.ts), int((b.ts - a.ts) // ms - 1)))
        o, h, l, cl = colonne(c)
        a14 = atr(h, l, cl, 14)
        cost = [x for x in a14 / cl if np.isfinite(x)]
        btc = dati.carica_candele("BTCUSDT", tf, quadro.INIZIO, quadro.FINE)
        ts_btc = {x.ts for x in btc}
        res["tf"][tf] = {
            "barre_tenute": len(c), "prima": iso(c[0].ts) if c else None, "ultima": iso(c[-1].ts) if c else None,
            "barre_costruzione": sum(1 for x in c if x.close_ts <= quadro.FINE_COSTRUZIONE_TS),
            "n_tolte_last": s["n_tolte_last"], "tolte_last": intervalli(s["tolte_last"], ms),
            "n_tolte_mark": s["n_tolte_mark"], "tolte_mark": intervalli(s["tolte_mark"], ms),
            "buchi_dopo_allineamento": buchi[:50], "n_buchi": len(buchi),
            "n_volume_mancante": s["n_volume_mancante"],
            "atr14_su_prezzo_mediana": float(np.median(cost)) if cost else None,
            "atr14_su_prezzo_p10_p90": [float(np.percentile(cost, 10)), float(np.percentile(cost, 90))] if cost else None,
            "btc_barre": len(btc), "barre_mask_senza_btc": sum(1 for x in c if x.ts not in ts_btc),
        }
        print(tf, "ok", flush=True)
    out = quadro.RADICE_REPO / "research" / "data" / "insample" / "MASKUSDT" / "fase0.json"
    out.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
