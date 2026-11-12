"""Audit G1 (12 nov 2026), catalogo voce 14: tutti gli ordini a mercato all'apertura delle 01:00 (un'ora dopo la decisione), con il
movimento dalle 00:00 alle 01:00 col suo segno (favorevole o contro), per G1 e per A a 280 USDT."""
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from research.programma7.revisione_g1n import analisi as an, nucleo as nu
QUI = Path(__file__).parent
spec = importlib.util.spec_from_file_location("g1a", QUI / "g1_2026-11-12.py"); g1a = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], "ritardo"]; spec.loader.exec_module(g1a)
b = g1a.basi()
def spese_ritardo(D):
    sp = np.zeros(D.shape[0])
    for j in np.flatnonzero(np.abs(D).sum(axis=0) > 0):
        o_ = b["ore"].get(b["simboli"][j]) or {}
        for k in np.flatnonzero(np.abs(D[:, j]) > 1e-12):
            dw = D[k, j]; h = int(b["giorni"][k]) * 24
            mov = 0.0
            if h in o_ and h + 1 in o_ and np.isfinite(o_[h][0]) and np.isfinite(o_[h + 1][0]):
                mov = o_[h + 1][0] / o_[h][0] - 1
            sp[k] += abs(dw) * b["costo"][j] + dw * mov
    return sp
out = {}
lordo, _, fund, D = nu.variazioni(b["W"], b["R"], b["F"], b["costo"])
d = pd.DataFrame({"netto": lordo - fund - spese_ritardo(D)}, index=b["giorni"])
out["G1_tutto_a_mercato_alle_01"] = g1a.sint(d)
dA, X, DA = g1a.conto_A(b)
dA["netto"] = dA["lordo"] - dA["funding"] - spese_ritardo(DA)
out["A280_tutto_a_mercato_alle_01"] = g1a.sint(dA)
for k, v in out.items():
    print(k, round(v["sharpe"], 3), round(v["annuo"], 3), round(v["discesa"], 3), {y: round(z, 3) for y, z in v["per_anno"].items()})
(QUI / "g1_ritardo_2026-11-12_esito.json").write_text(json.dumps(out, indent=1, default=float))
