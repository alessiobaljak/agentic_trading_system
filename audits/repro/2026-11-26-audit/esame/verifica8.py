"""Controprova del problema 8: 68 G10 senza le settimane ferme; serie della 149 con settimane vuote (NaN) in `gruppi`."""
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
OUT = Path(__file__).parent
from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import terza as te  # noqa: E402

M = pickle.load(open(OUT / "mio_mazzo.pkl", "rb"))
S = pickle.load(open(OUT / "scenari.pkl", "rb"))
serie, soli, gr, cand = M["serie"], M["soli"], M["gr"], S["cand"]
fg1 = next(g for g in gr if "57 G1" in g["membri"])
print("nella famiglia di G1:", {n: n in fg1["membri"] for n in ("24 F5", "28 K2", "28 F5+M7+K2", "56 F9")})

# (a) G10
g10 = serie["68 G10"]
idx = g10.index.to_numpy()
print("68 G10: settimane", len(g10), "salto massimo (giorni)", int(np.diff(idx).max()), "Sharpe", round(ast.sharpe(g10), 3),
      "t", round(ast.sharpe(g10) * math.sqrt(len(g10) / 52), 2))
tutte = np.arange(idx.min(), ast.sc.giorno(2026, 10, 5) + 1, 7)
g10z = ast.periodo(g10.reindex(tutte).fillna(0.0))
print("   con gli zeri: settimane", len(g10z), "Sharpe", round(ast.sharpe(g10z), 3), "t", round(ast.sharpe(g10z) * math.sqrt(len(g10z) / 52), 2))
fam10 = next(g for g in gr if "68 G10" in g["membri"])
print("   famiglia della G10:", fam10["membri"], round(fam10["sharpe"], 3), fam10["settimane"])

# (b) NaN nelle serie
con_nan = {n: int(s.isna().sum()) for n, s in serie.items() if s.isna().any()}
print("serie con settimane vuote:", len(con_nan), con_nan)
a, b = serie.get("149 APTUSDT_1d_A"), serie.get("149 SOLUSDT_1d_A")
if a is None:
    print([n for n in serie if n.startswith("149 ")][:12])
else:
    c = a.index.intersection(b.index)
    x, y = a.loc[c], b.loc[c]
    ok = (x.abs() > 0) | (y.abs() > 0)
    print("APT_1d_A con SOL_1d_A: come nel codice", np.corrcoef(x[ok], y[ok])[0, 1],
          "senza NaN", round(float(pd.concat([x[ok], y[ok]], axis=1).dropna().corr().iloc[0, 1]), 3))


def gruppi_senza_nan(serie_d, taglio):
    nomi = list(serie_d)
    n = len(nomi)
    R = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            a, b = serie_d[nomi[i]], serie_d[nomi[j]]
            c = a.index.intersection(b.index)
            x, y = a.loc[c], b.loc[c]
            ok = ((x.abs() > 0) | (y.abs() > 0)) & x.notna() & y.notna()
            rho = float(np.corrcoef(x[ok], y[ok])[0, 1]) if ok.sum() >= ast.MIN_COMUNI and x[ok].std() > 0 and y[ok].std() > 0 else 0.0
            R[i, j] = R[j, i] = rho if np.isfinite(rho) else 0.0
    np.fill_diagonal(R, 1.0)
    D = np.sqrt(np.clip((1 - R) / 2, 0, None))
    Z = linkage(squareform(D, checks=False), method="average")
    et = fcluster(Z, t=math.sqrt((1 - taglio) / 2), criterion="distance")
    out = []
    for g in sorted(set(et)):
        membri = [nomi[i] for i in np.flatnonzero(et == g)]
        media = pd.concat([serie_d[m] for m in membri], axis=1).mean(axis=1)
        out.append({"membri": membri, "sharpe": ast.sharpe(media), "settimane": int(media.notna().sum())})
    return out


for tag, sd, fun in (("gruppi senza NaN", serie, gruppi_senza_nan), ("G10 con gli zeri", {**serie, "68 G10": g10z}, ast.gruppi),
                     ("tutte e due", {**serie, "68 G10": g10z}, gruppi_senza_nan)):
    g2 = fun(sd, ast.TAGLIO)
    fam, v = ast.per_v(g2, soli, False), ast.per_v(g2, soli, True)
    p = te.sharpe_corretto(*cand["G1 (misura 12 nov)"], v, 52, n_prove=len(fam))
    f149 = [g["membri"] for g in g2 if any(m in con_nan for m in g["membri"]) and len(g["membri"]) > 1]
    print(f"{tag:18s} famiglie {len(fam)} in V {len(v)} dev {np.std(v, ddof=1):.4f} G1 {p:.4f} | famiglie con serie a NaN e altri membri: {f149}")
