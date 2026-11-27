"""Diagnostica del mazzo dell'esame (sola lettura del repository). Scrive solo nella cartella di questo script."""
import json
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
OUT = Path(__file__).parent

from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import terza as te  # noqa: E402

t0 = time.time()
serie, soli = ast.mazzo()
print(f"mazzo: {len(serie)} serie, {len(soli)} senza serie, {time.time()-t0:.0f}s", flush=True)
pickle.dump((serie, soli), open(OUT / "mazzo.pkl", "wb"))

righe = []
for n, s in serie.items():
    idx = s.index.to_numpy()
    passi = np.diff(idx)
    righe.append({"nome": n, "settimane": int(len(s)), "non_zero": int((s != 0).sum()),
                  "primo": int(idx[0]) if len(idx) else None, "ultimo": int(idx[-1]) if len(idx) else None,
                  "passo_min": int(passi.min()) if len(passi) else None, "passo_max": int(passi.max()) if len(passi) else None,
                  "lunedi_ok": bool(((idx + 3) % 7 == 0).all()) if len(idx) else None,
                  "nan": int(s.isna().sum()),
                  "sharpe": ast.sharpe(s), "t": ast.sharpe(s) * math.sqrt(len(s.dropna()) / 52),
                  "ac1": float(s.autocorr(1)) if len(s) > 3 else None})
d = pd.DataFrame(righe)
d.to_csv(OUT / "serie_mazzo.csv", index=False)
print("serie con passo > 7 (indice non denso):")
print(d[d["passo_max"] > 7][["nome", "settimane", "non_zero", "passo_max"]].to_string())
print("serie non sul lunedi':", d[~d["lunedi_ok"].astype(bool)]["nome"].tolist())
print("serie con meno di 52 settimane:")
print(d[d["settimane"] < 52][["nome", "settimane", "sharpe", "t"]].to_string())
print("serie con |Sharpe| > 3:")
print(d[d["sharpe"].abs() > 3][["nome", "settimane", "sharpe", "t", "ac1"]].to_string())

t0 = time.time()
gr = ast.gruppi(serie, ast.TAGLIO)
print(f"gruppi: {len(gr)} ({time.time()-t0:.0f}s)", flush=True)
pickle.dump(gr, open(OUT / "gruppi.pkl", "wb"))
sr_g, sr_v = ast.per_v(gr, soli, False), ast.per_v(gr, soli, True)
print("famiglie N", len(sr_g), "in V", len(sr_v), "dev V", np.std(sr_v, ddof=1))
