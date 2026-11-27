"""Controprova indipendente: rifaccio il mazzo e le famiglie con il codice del repository (sola lettura) e salvo qui."""
import math
import pickle
import sys
import time
from pathlib import Path

import numpy as np

REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
OUT = Path(__file__).parent
from research.programma6 import asticella as ast  # noqa: E402

t0 = time.time()
serie, soli = ast.mazzo()
print("serie", len(serie), "senza serie", len(soli), f"{time.time()-t0:.0f}s", flush=True)
gr = ast.gruppi(serie, ast.TAGLIO)
print("gruppi con serie", len(gr), f"{time.time()-t0:.0f}s", flush=True)
sr_g = ast.per_v(gr, soli, False)
sr_v = ast.per_v(gr, soli, True)
print("famiglie", len(sr_g), "in V", len(sr_v), "dev V", round(float(np.std(sr_v, ddof=1)), 4))
nomi_soli = ast.senza_serie()
pickle.dump({"serie": serie, "soli": soli, "gr": gr, "nomi_soli": nomi_soli}, open(OUT / "mio_mazzo.pkl", "wb"))
print("fatto", f"{time.time()-t0:.0f}s")
