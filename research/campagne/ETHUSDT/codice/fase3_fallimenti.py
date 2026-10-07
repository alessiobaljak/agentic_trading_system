"""Fase 3: studio dei fallimenti di una variante che ha battuto le baseline, sui dati di costruzione.

Uso: python3 fase3_fallimenti.py <ID della variante>
Legge i trade salvati da fase2_test.py in risultati/<ID>_costruzione.json e li spezza per:
anno, esito (stop, target, segnale, durata), banda di volatilita' all'ingresso (ATR/prezzo in
terzili), ora UTC d'ingresso, giorno della settimana, segno del rendimento di BTC nelle 24 ore
precedenti, dimensione del movimento che ha generato il segnale. Scrive un riassunto in
risultati/<ID>_fallimenti.json e una voce `nota` nel log. Nessun filtro nasce qui: un filtro
e' una nuova variante, registrata prima del test e costruita solo su questi dati.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
import comune  # noqa: E402
import strategie  # noqa: E402
from log import aggiungi  # noqa: E402


def gruppo(trades, chiave):
    per = defaultdict(list)
    for t in trades:
        per[chiave(t)].append(t["r"])
    return {str(k): {"n": len(v), "r_medio": round(float(np.mean(v)), 3), "win_rate": round(float(np.mean([x > 0 for x in v])), 2)}
            for k, v in sorted(per.items(), key=lambda kv: str(kv[0]))}


def main(id_variante: str):
    dati_var = json.loads((QUI.parent / "risultati" / f"{id_variante}_costruzione.json").read_text(encoding="utf-8"))
    codice, nome_dir = dati_var["variante"].split("-", 2)[0] + "-" + dati_var["variante"].split("-", 2)[1], dati_var["variante"].split("-", 2)[2]
    idea = strategie.IDEE[codice]
    s = comune.serie(idea.timeframe, comune.INIZIO_DATI, comune.FINE_COSTRUZIONE, con_btc=True)
    atr_rel = comune.atr(s, 14) / s.close
    ts_di = {int(t): i for i, t in enumerate(s.ts)}
    barre_24h = max(1, comune.MS_GIORNO // (int(s.ts[1] - s.ts[0])))
    r_btc_24h = comune.rendimento_a(s.btc_close, barre_24h)
    r_eth_24h = comune.rendimento_a(s.close, barre_24h)
    terzili = np.nanpercentile(atr_rel, [33.3, 66.7])
    trades = dati_var["trades"]
    for t in trades:
        i = ts_di.get(int(t["ts_entrata"]))
        d = datetime.fromtimestamp(t["ts_entrata"] / 1000, tz=timezone.utc)
        t["anno"], t["ora"], t["giorno_sett"] = d.year, d.hour, d.weekday()
        t["durata_barre"] = (t["ts_uscita"] - t["ts_entrata"]) // int(s.ts[1] - s.ts[0])
        if i is not None and i > 0:
            a = atr_rel[i - 1]
            t["banda_vol"] = "bassa" if a < terzili[0] else ("alta" if a > terzili[1] else "media")
            t["btc_24h"] = "su" if r_btc_24h[i - 1] > 0 else "giu"
            t["eth_24h"] = "su" if r_eth_24h[i - 1] > 0 else "giu"
        else:
            t["banda_vol"] = t["btc_24h"] = t["eth_24h"] = "?"
    out = {
        "variante": dati_var["variante"], "n": len(trades),
        "per_anno": gruppo(trades, lambda t: t["anno"]),
        "per_esito": gruppo(trades, lambda t: t["esito"]),
        "per_banda_volatilita": gruppo(trades, lambda t: t["banda_vol"]),
        "per_ora_utc": gruppo(trades, lambda t: t["ora"]) if idea.timeframe in ("15m", "30m", "1h", "2h", "4h") else None,
        "per_giorno_settimana": gruppo(trades, lambda t: t["giorno_sett"]),
        "per_btc_24h_prima": gruppo(trades, lambda t: t["btc_24h"]),
        "per_eth_24h_prima": gruppo(trades, lambda t: t["eth_24h"]),
        "per_durata": gruppo(trades, lambda t: min(int(t["durata_barre"]), 8)),
        "peggiori_10": sorted(({"ts": datetime.fromtimestamp(t["ts_entrata"] / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M"), "r": round(t["r"], 2), "esito": t["esito"]} for t in trades), key=lambda x: x["r"])[:10],
    }
    (QUI.parent / "risultati" / f"{id_variante}_fallimenti.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    aggiungi({"id": None, "tipo": "nota", "oggetto": f"Fase 3, studio dei fallimenti di {id_variante} ({dati_var['variante']})",
              "riassunto": {k: v for k, v in out.items() if k in ("per_anno", "per_esito", "per_banda_volatilita", "per_btc_24h_prima", "per_eth_24h_prima")},
              "file": f"risultati/{id_variante}_fallimenti.json"})
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
