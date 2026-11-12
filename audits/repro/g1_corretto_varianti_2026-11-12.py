"""Audit G1 (12 nov 2026): Sharpe corretto (N = gruppi e N = 309, V con l'aggiunta) di G1 e di A a 280 USDT con l'ordine limite
piu' severo e tutto a mercato."""
import importlib.util, json, math, sys
from pathlib import Path
import numpy as np, pandas as pd
from research.programma6 import asticella as ast, terza as te, seconda as sc
from research.programma7.revisione_g1n import analisi as an
QUI = Path(__file__).parent
spec = importlib.util.spec_from_file_location("g1a", QUI / "g1_2026-11-12.py"); g1a = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], "corretto"]; spec.loader.exec_module(g1a)
b = g1a.basi()
prove = ast.le_prove()
serie = {n: ast.periodo(s) for n, s, _ in prove if s is not None}
serie.update({n: ast.periodo(s) for n, s in ast.serie_nuove().items()})
soli = [sr for _, s, sr in prove if s is None]
gr = ast.gruppi(serie, ast.TAGLIO); sr_g = ast.per_v(gr, soli, False); sr_v = ast.per_v(gr, soli, True)
def corr(x):
    w = an.settimane(pd.DataFrame({"n": x}))["n"]; v = w.to_numpy()
    sr = v.mean() / v.std(ddof=1) * math.sqrt(52); a = float(pd.Series(v).skew()); k = float(pd.Series(v).kurt() + 3)
    return {"sharpe": sr, "N_gruppi": te.sharpe_corretto(sr, len(v), a, k, sr_v, 52, n_prove=len(sr_g)),
            "N_309": te.sharpe_corretto(sr, len(v), a, k, sr_v, 52, n_prove=309), "t": sr * math.sqrt(len(v) / 52),
            "anni": {int(y): round(float(z), 3) for y, z in an.sintesi(pd.DataFrame({"netto": x}))["per_anno"].items()}}
out = {}
for oltre in (0.0, 0.0005, 0.001):
    d = an.conto("G1", b["W"], b["R"], b["F"], b["costo"], b["giorni"], b["simboli"], b["ore"], oltre)
    out[f"G1_oltre_{oltre}"] = corr(d["netto"])
    dA, _, _ = g1a.conto_A(b, oltre=oltre)
    out[f"A280_oltre_{oltre}"] = corr(dA["netto"])
    if oltre == 0.0:
        out["G1_tutto_a_mercato"] = corr(d["netto_mercato"]); out["A280_tutto_a_mercato"] = corr(dA["netto_mercato"])
for k, v in out.items():
    print(k, {a: (round(b_, 3) if isinstance(b_, float) else b_) for a, b_ in v.items()})
(QUI / "g1_corretto_varianti_2026-11-12_esito.json").write_text(json.dumps(out, indent=1, default=float))
