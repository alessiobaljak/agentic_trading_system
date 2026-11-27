"""Sensibilita' dello Sharpe corretto (probabilita' che non sia fortuna) e del t ai punti dell'audit. Sola lettura del repository."""
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

serie, soli = pickle.load(open(OUT / "mazzo.pkl", "rb"))
gr = pickle.load(open(OUT / "gruppi.pkl", "rb"))
P7 = REPO / "research/programma7"
P6 = REPO / "research/programma6"

mis = json.loads((REPO / "audits/repro/g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]
e168 = json.loads((P7 / "risultati_centosesta/esame.json").read_text())["esame"]
p28 = json.loads((REPO / "audits/repro/prova28_2026-11-11_esito.json").read_text())["misure"]["fino_al_2026-10-19_funding_vero"]["F5 + M7 + K2"]
K = ("sharpe", "settimane", "asimmetria", "curtosi")
cand = {"G1 (57)": tuple(mis["G1"][k] for k in K),
        "168 A": tuple(e168["A"]["intero"][k] for k in K), "168 B": tuple(e168["B"]["intero"][k] for k in K),
        "F5+M7+K2 (28)": tuple(p28[k] for k in K)}


def tv(sr, w):
    return sr * math.sqrt(w / 52)


fam = [(g["sharpe"], g["settimane"], g["membri"]) for g in gr]
N = len(fam) + len(soli)
v_oggi = [s for s, w, _ in fam if tv(s, w) >= -3] + [s for s in soli if tv(s, 300) >= -3]


def tutte(v, n=N, etichetta=""):
    r = {c: round(te.sharpe_corretto(*a, v, 52, n_prove=n), 3) for c, a in cand.items()}
    print(f"{etichetta:72s} N {n:3d} in V {len(v):3d} dev {np.std(v, ddof=1):.3f} | " + ", ".join(f"{c} {x:.3f}" for c, x in r.items()))
    return r


print("== mano: ricalcolo indipendente della formula per G1 (57) con N = 65 e dev 0,5667 e per 168 B oggi ==")


def dsr_mano(sr_a, n, sk, ku, dev_a, NN):
    g = 0.5772156649015329
    srw, sdw = sr_a / math.sqrt(52), dev_a / math.sqrt(52)
    sr0 = sdw * ((1 - g) * stats.norm.ppf(1 - 1 / NN) + g * stats.norm.ppf(1 - 1 / (NN * math.e)))
    den = math.sqrt(1 - sk * srw + (ku - 1) / 4 * srw ** 2)
    z = (srw - sr0) * math.sqrt(n - 1) / den
    return sr0 * math.sqrt(52), z, stats.norm.cdf(z)


print("G1 fino alla 57:", [round(x, 4) for x in dsr_mano(*cand["G1 (57)"], 0.5667, 65)])
print("168 B oggi     :", [round(x, 4) for x in dsr_mano(*cand["168 B"], 0.67749, 200)])
print("G1 oggi        :", [round(x, 4) for x in dsr_mano(*cand["G1 (57)"], float(np.std(v_oggi, ddof=1)), N)])

print("\n== scenari ==")
tutte(v_oggi, etichetta="oggi (aggiunta del 23 ottobre: fuori da V solo t < -3)")
v_sim = [s for s, w, _ in fam if abs(tv(s, w)) <= 3] + [s for s in soli if abs(tv(s, 300)) <= 3]
tutte(v_sim, etichetta="simmetrico: fuori da V anche t > +3")
cc = lambda m: any(x.startswith(("157 ", "161 ", "97 ")) for x in m)  # noqa: E731
v_nocc = [s for s, w, m in fam if tv(s, w) >= -3 and not cc(m)] + [s for s in soli if tv(s, 300) >= -3]
tutte(v_nocc, etichetta="senza la famiglia a incasso quasi fisso (97, 157, 161)")
g1fam = lambda m: "57 G1" in m  # noqa: E731
v_nog1 = [s for s, w, m in fam if tv(s, w) >= -3 and not g1fam(m)] + [s for s in soli if tv(s, 300) >= -3]
tutte(v_nog1, etichetta="senza la famiglia di G1 in V")
# Lo (2002): Sharpe annuo corretto per l'autocorrelazione delle settimane, sulla serie media di ogni famiglia
def lo_annuo(x, q=52, lag=8):
    """Sharpe annuo con la varianza di lungo periodo di Newey-West (pesi di Bartlett, sempre positiva): come Lo (2002) per
    le settimane legate; con settimane indipendenti e' lo Sharpe semplice."""
    x = pd.Series(x).dropna().to_numpy(float)
    n = len(x)
    u = x - x.mean()
    s = (u @ u) / n + 2 * sum((1 - k / (lag + 1)) * (u[k:] @ u[:-k]) / n for k in range(1, lag + 1))
    return x.mean() / math.sqrt(s) * math.sqrt(q) if s > 0 else 0.0


medie = []
for g in gr:
    m = pd.concat([serie[x] for x in g["membri"]], axis=1).mean(axis=1)
    medie.append((g, m))
v_lo = []
for g, m in medie:
    s_lo = lo_annuo(m)
    if tv(g["sharpe"], g["settimane"]) >= -3:
        v_lo.append(s_lo)
v_lo += [s for s in soli if tv(s, 300) >= -3]
tutte(v_lo, etichetta="V con lo Sharpe di Lo (8 ritardi) per ogni famiglia")
for g, m in medie:
    if cc(g["membri"]):
        print("  famiglia incasso fisso: Sharpe semplice", round(g["sharpe"], 2), "di Lo", round(lo_annuo(m), 2), "ac1", round(m.autocorr(1), 2))

# 151 e 153: t sulle settimane vere invece che sulle 300
extra = []
s151 = next(s for n, s in ast.senza_serie() if n == "151 WE")
e153 = json.loads((P7 / "risultati_novantunesima/esame.json").read_text())["varianti"]
vere = {"151 WE": (s151, 19), "153 A": (e153["A"]["sharpe"], e153["A"]["settimane"]), "153 B": (e153["B"]["sharpe"], e153["B"]["settimane"])}
dentro = [n for n, (s, w) in vere.items() if tv(s, w) >= -3]
print("\n151/153 con il t sulle settimane vere: entrerebbero in V", dentro, {n: round(tv(s, w), 2) for n, (s, w) in vere.items()})
v_vere = v_oggi + [vere[n][0] for n in dentro]
tutte(v_vere, etichetta="151 e 153 B in V (t sulle loro settimane)")

# soglia: quale Sharpe annuo serve per 0,80 oggi, 300 settimane, asimmetria 0,6, curtosi 5
dev = float(np.std(v_oggi, ddof=1))
for w in (300, 250, 156, 104):
    f = lambda s: te.sharpe_corretto(s, w, 0.6, 5.0, v_oggi, 52, n_prove=N) - 0.80  # noqa: E731
    s_req = optimize.brentq(f, 0.5, 6)
    print(f"Sharpe annuo che serve per 0,80 oggi con {w} settimane: {s_req:.2f} (t {tv(s_req, w):.2f}); con V simmetrico "
          f"{optimize.brentq(lambda s: te.sharpe_corretto(s, w, 0.6, 5.0, v_sim, 52, n_prove=N) - 0.80, 0.5, 6):.2f}")
print("E[max] per caso oggi (annuo):", round(dsr_mano(2.0, 300, 0, 3, dev, N)[0], 3))

# autocorrelazioni e t robusto (Newey-West, 4 e 8 ritardi) delle candidate dal mazzo
def nw_t(x, L):
    x = pd.Series(x).dropna().to_numpy(float)
    n = len(x)
    u = x - x.mean()
    g0 = (u @ u) / n
    s = g0 + 2 * sum((1 - k / (L + 1)) * (u[k:] @ u[:-k]) / n for k in range(1, L + 1))
    return x.mean() / math.sqrt(s / n)


print("\n== t semplice e t robusto alle settimane legate ==")
for n in ("57 G1", "168 B", "24 F5", "28 F5+M7+K2", "69 G11", "88 G1N", "161 A", "157 A", "159 A", "70 G12"):
    x = serie[n].dropna()
    print(f"{n:14s} sett {len(x)} ac1 {x.autocorr(1):+.2f} ac2 {x.autocorr(2):+.2f} ac4 {x.autocorr(4):+.2f} t {tv(ast.sharpe(x), len(x)):.2f} "
          f"NW4 {nw_t(x, 4):.2f} NW8 {nw_t(x, 8):.2f} NW26 {nw_t(x, 26):.2f} Lo-Sharpe {lo_annuo(x):.2f} (semplice {ast.sharpe(x):.2f})")
