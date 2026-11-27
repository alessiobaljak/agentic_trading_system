"""Controprova dei problemi 1, 3 e 4: famiglie in V, scenari, soglia. Sola lettura del repository."""
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats

REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
OUT = Path(__file__).parent
from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import terza as te  # noqa: E402

M = pickle.load(open(OUT / "mio_mazzo.pkl", "rb"))
serie, soli, gr, nomi_soli = M["serie"], M["soli"], M["gr"], M["nomi_soli"]
P7 = REPO / "research/programma7"


def tv(s, w):
    return s * math.sqrt(w / 52)


# --- candidate: misure dai file del repository
K = ("sharpe", "settimane", "asimmetria", "curtosi")
g57 = json.loads((P7 / "risultati_prima/esame.json").read_text())["intero"]
gmis = json.loads((REPO / "audits/repro/g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]["G1"]
e168 = json.loads((P7 / "risultati_centosesta/esame.json").read_text())
p28 = json.loads((REPO / "audits/repro/prova28_2026-11-11_esito.json").read_text())["misure"]["fino_al_2026-10-19_funding_vero"]["F5 + M7 + K2"]
cand = {"G1 (misura 12 nov)": tuple(gmis[k] for k in K), "G1 (esame 57)": tuple(g57[k] for k in K),
        "168 A": tuple(e168["esame"]["A"]["intero"][k] for k in K), "168 B": tuple(e168["esame"]["B"]["intero"][k] for k in K),
        "F5+M7+K2": tuple(p28[k] for k in K)}
print("168 nel file: A", round(e168["esame"]["A"]["sharpe_corretto"], 4), "B", round(e168["esame"]["B"]["sharpe_corretto"], 4),
      "famiglie", e168["famiglie"])

fam = [(g["sharpe"], g["settimane"], g["membri"]) for g in gr]
N = len(fam) + len(soli)
print("N", N, "famiglie con serie", len(fam), "senza serie", len(soli))
pos = [(round(s, 2), w, round(tv(s, w), 2), len(m), m[:4]) for s, w, m in fam if tv(s, w) > 3]
neg = [x for x in fam if tv(x[0], x[1]) < -3]
neg_soli = [s for s in soli if tv(s, 300) < -3]
print("famiglie con t > +3:", len(pos))
for p in sorted(pos, key=lambda x: -x[0]):
    print("   ", p)
print("famiglie con serie e t < -3:", len(neg), "| senza serie con t < -3 (su 300):", len(neg_soli))
v_oggi = [s for s, w, _ in fam if tv(s, w) >= -3] + [s for s in soli if tv(s, 300) >= -3]
print("in V oggi", len(v_oggi), "dev", round(np.std(v_oggi, ddof=1), 4))
# la 157 nel mazzo
for n in ("157 A", "157 B", "161 A", "161 B", "97 CC", "159 A", "159 B"):
    if n in serie:
        x = serie[n].dropna()
        print(f"   {n}: Sharpe {ast.sharpe(x):.2f} settimane {len(x)} ac1 {x.autocorr(1):.2f}")
fcc = next(g for g in gr if "157 A" in g["membri"])
print("famiglia della 157:", fcc["membri"], round(fcc["sharpe"], 3), fcc["settimane"])
fg1 = next(g for g in gr if "57 G1" in g["membri"])
print("famiglia di G1:", len(fg1["membri"]), "membri, Sharpe", round(fg1["sharpe"], 3), "t", round(tv(fg1["sharpe"], fg1["settimane"]), 2))
best = max(((ast.sharpe(serie[m].dropna()), m) for m in fg1["membri"]))
print("serie migliore della famiglia di G1:", round(best[0], 3), best[1])


def prob(v, n=N, tag=""):
    r = {c: te.sharpe_corretto(*a, v, 52, n_prove=n) for c, a in cand.items()}
    print(f"{tag:55s} N {n} V {len(v)} dev {np.std(v, ddof=1):.3f} | " + " ".join(f"{c}={x:.3f}" for c, x in r.items()))
    return r


prob(v_oggi, tag="oggi")
v_sym = [s for s, w, _ in fam if -3 <= tv(s, w) <= 3] + [s for s in soli if -3 <= tv(s, 300) <= 3]
prob(v_sym, tag="simmetrico |t|<=3")
cc = lambda m: any(x.startswith(("157 ", "161 ", "97 ")) for x in m)  # noqa: E731
v_nocc = [s for s, w, m in fam if tv(s, w) >= -3 and not cc(m)] + [s for s in soli if tv(s, 300) >= -3]
prob(v_nocc, tag="senza la famiglia 97/157/161")
# senza la sola 157: rifaccio i gruppi senza le serie 157 A e 157 B
serie_no157 = {k: v for k, v in serie.items() if not k.startswith("157 ")}
gr2 = ast.gruppi(serie_no157, ast.TAGLIO)
v2 = ast.per_v(gr2, soli, True)
n2 = len(ast.per_v(gr2, soli, False))
prob(v2, n=n2, tag="senza le serie 157 A/B (gruppi rifatti)")
# dispersione teorica sotto l'ipotesi nulla
dev_t = math.sqrt(52 / 299)
fake = [dev_t * z for z in (-1, 1)]  # varianza campionaria = dev_t^2 * 2 con 2 punti -> correggo
v_teo = list(np.array([-1.0, 1.0]) * dev_t / math.sqrt(2))
print("dev teorica", round(dev_t, 4), "controllo", round(np.std(v_teo, ddof=1), 4))
prob(v_teo, tag="dispersione teorica sqrt(52/299)")

# soglia di Sharpe per 0,80 (300 settimane): con le misure di asimmetria e curtosi di G1 (esame 57) e con 0,6 / 5
for asim, curt in ((g57["asimmetria"], g57["curtosi"]), (0.6, 5.0)):
    for v, tag in ((v_oggi, "oggi"), (v_sym, "simmetrico")):
        s = optimize.brentq(lambda s: te.sharpe_corretto(s, 300, asim, curt, v, 52, n_prove=N) - 0.80, 0.3, 6)
        print(f"Sharpe per 0,80 ({tag}, asim {asim:.2f}, curt {curt:.2f}): {s:.3f} (t {tv(s, 300):.2f})")
# fortuna da battere (sr0 annuo)
g = 0.5772156649
for v, n, tag in ((v_oggi, N, "oggi"), ([0], 65, "")):
    pass
sd = np.std(v_oggi, ddof=1)
sr0 = sd * ((1 - g) * stats.norm.ppf(1 - 1 / N) + g * stats.norm.ppf(1 - 1 / (N * math.e)))
print("fortuna da battere oggi (annua):", round(sr0, 3))
pickle.dump({"v_oggi": v_oggi, "v_sym": v_sym, "N": N, "cand": cand}, open(OUT / "scenari.pkl", "wb"))
