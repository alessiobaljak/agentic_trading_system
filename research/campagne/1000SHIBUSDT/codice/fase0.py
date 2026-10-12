"""Fase 0, punto 3: descrizione dei dati (buchi, barre tolte, funding, volume, liquidita').

Scrive il resoconto in data/insample/1000SHIBUSDT/fase0.json e lo stampa. Nessun
risultato di strategia: solo fatti sui dati, su tutto l'in-sample fino al 2023-12-31.
"""
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
from research.src import dati  # noqa: E402

FINE = date(2023, 12, 31)


def giorno(ts):
    return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def intervalli(ts_lista, passo):
    """Raggruppa ts consecutivi (distanza = passo) in intervalli [primo, ultimo]."""
    out = []
    for t in ts_lista:
        if out and t - out[-1][1] == passo:
            out[-1][1] = t
        else:
            out.append([t, t])
    return [(giorno(a), giorno(b), (b - a) // passo + 1) for a, b in out]


def main():
    res = {}
    for tf in ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]:
        s = dati.carica_serie_allineate(q.SIMBOLO, tf, q.INIZIO, FINE)
        c = s["candele"]
        passo = q.MS[tf]
        buchi = [(giorno(a.close_ts + 1), giorno(b.ts), (b.ts - a.close_ts - 1) // passo)
                 for a, b in zip(c, c[1:]) if b.ts > a.close_ts + 1]
        rng = np.array([(x.high - x.low) / x.close for x in c])
        atr = q.atr(c, 14) / q.arr(c, "close")
        res[tf] = {
            "barre_tenute": len(c), "prima_barra": giorno(c[0].ts), "ultima_barra": giorno(c[-1].ts),
            "n_tolte_last": s["n_tolte_last"], "n_tolte_mark": s["n_tolte_mark"],
            "tolte_last": intervalli(s["tolte_last"], passo)[:30],
            "tolte_mark": intervalli(s["tolte_mark"], passo)[:30],
            "buchi_nella_serie_tenuta": buchi[:30], "n_buchi": len(buchi),
            "n_volume_mancante": s["n_volume_mancante"],
            "ampiezza_mediana_barra": round(float(np.median(rng)), 5),
            "atr14_mediano_su_prezzo": round(float(np.nanmedian(atr)), 5),
        }
        print(tf, json.dumps({k: v for k, v in res[tf].items() if not isinstance(v, list)}), flush=True)
    fr = dati.carica_funding_dettaglio(q.SIMBOLO, q.INIZIO, FINE)
    res["funding"] = {
        "n_settlement": len(fr), "primo": giorno(fr[0][0]), "ultimo": giorno(fr[-1][0]),
        "intervalli_dichiarati": [(giorno(t), o) for t, o in dati.intervallo_funding(fr)],
        "intervalli_dalle_distanze": [(giorno(t), o) for t, o in dati.intervallo_funding([(t, r) for t, _, r in fr])][:40],
        "tasso_mediano": float(np.median([r for _, _, r in fr])),
        "quota_negativi": round(float(np.mean([r < 0 for _, _, r in fr])), 4),
        "quota_almeno_0_0003": round(float(np.mean([r >= 0.0003 for _, _, r in fr])), 4),
    }
    medie = q.mesi_illiquidi(FINE)
    res["volume_medio_giornaliero_per_mese"] = {f"{a}-{m:02d}": round(v) for (a, m), v in medie.items()}
    per_anno = {}
    vol = {}
    for p in sorted((q.CARTELLA_DATI / "klines" / "1d").glob("*.zip")):
        for ts, v in dati.volume_usdt_da_zip(p).items():
            vol.setdefault(ts, v)
    for ts, v in vol.items():
        per_anno.setdefault(datetime.fromtimestamp(ts / 1000, tz=timezone.utc).year, []).append(v)
    res["volume_medio_giornaliero_per_anno"] = {a: round(float(np.mean(v))) for a, v in sorted(per_anno.items())}
    res["mesi_sotto_soglia"] = [k for k, v in res["volume_medio_giornaliero_per_mese"].items() if v < q.LIQUIDITA_MINIMA]
    res["giorni_1d_con_volume"] = len(vol)
    out = q.CARTELLA_DATI / "fase0.json"
    out.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps({k: res[k] for k in ("funding", "volume_medio_giornaliero_per_anno", "mesi_sotto_soglia",
                                          "giorni_1d_con_volume")}, ensure_ascii=False))
    print(json.dumps(res["volume_medio_giornaliero_per_mese"]))


if __name__ == "__main__":
    main()
