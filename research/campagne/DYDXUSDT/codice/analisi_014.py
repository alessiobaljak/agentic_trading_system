"""Fase 3 per DYDXUSDT-014: R dei trade per livello della quota di acquisti dei taker alla barra del segnale."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402

CARTELLA = Path(__file__).resolve().parent.parent
d = json.loads((CARTELLA / "risultati" / "DYDXUSDT-014.json").read_text())
ctx = comune.contesto("1d")
q = comune.quota_acquisti_taker(ctx)
righe = []
for t in d["trades"]:
    i = ctx.indice_di(t["ts_entrata"]) - 1
    righe.append((q[i], t["r"]))
righe.sort()
qq = np.array([x for x, _ in righe])
rr = np.array([y for _, y in righe])
out = {"quantili_quota": [float(x) for x in np.quantile(qq, [0, 0.25, 0.5, 0.75, 1])]}
for k, (a, b) in enumerate([(0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0)]):
    sl = slice(int(a * len(rr)), int(b * len(rr)))
    out[f"quartile_{k + 1}"] = [int(len(rr[sl])), float(rr[sl].mean()), float(qq[sl].max())]
print(json.dumps(out))
