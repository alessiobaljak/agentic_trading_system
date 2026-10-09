"""Fase 3: R dei trade di una variante divisi per condizioni note alla barra del segnale (costruzione).

    python research/campagne/DYDXUSDT/codice/analisi_filtri.py DYDXUSDT-013 4h

Condizioni: close sopra/sotto la media a 50 barre; rendimento delle 6 barre prima del segnale sopra/sotto 0;
volume della barra del segnale sopra/sotto la media delle 20 barre prima; ATR relativo sopra/sotto la sua
mediana; BTC sopra/sotto la sua media a 50 barre.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402

CARTELLA = Path(__file__).resolve().parent.parent
id_, tf = sys.argv[1], sys.argv[2]
d = json.loads((CARTELLA / "risultati" / f"{id_}.json").read_text())
ctx = comune.contesto(tf)
m50 = comune.sma(ctx.c, 50)
r6 = comune.rendimento(ctx.c, 6)
v = ctx.volume_usdt
v20 = np.full(ctx.n, np.nan)
for i in range(20, ctx.n):
    v20[i] = v[i - 20:i].mean()
atrp = comune.atr(ctx, 14) / ctx.c
med_atrp = np.nanmedian(atrp)
b = ctx.btc
bm50 = comune.sma(np.nan_to_num(b, nan=np.nanmean(b)), 50)
gruppi = {}
for t in d["trades"]:
    i = ctx.indice_di(t["ts_entrata"]) - 1  # barra del segnale
    cond = {
        "close_sopra_media50": bool(ctx.c[i] > m50[i]) if np.isfinite(m50[i]) else None,
        "rend6_positivo": bool(r6[i] > 0) if np.isfinite(r6[i]) else None,
        "volume_sopra_media20": bool(v[i] > v20[i]) if np.isfinite(v20[i]) else None,
        "atr_sopra_mediana": bool(atrp[i] > med_atrp) if np.isfinite(atrp[i]) else None,
        "btc_sopra_media50": bool(b[i] > bm50[i]) if np.isfinite(b[i]) else None,
    }
    for k, val in cond.items():
        gruppi.setdefault(k, {}).setdefault(str(val), []).append(t["r"])
out = {k: {s: [len(x), round(float(np.mean(x)), 3), round(float(np.mean(sorted(x)[:-3])) if len(x) > 3 else float("nan"), 3)]
           for s, x in g.items()} for k, g in gruppi.items()}
print(json.dumps({"id": id_, "formato": "[n, R medio, R medio senza i 3 migliori]", "gruppi": out}))
