"""Controprova del problema 2: settimane legate di G1 e parenti, t robusto, settimane efficaci, probabilita' alla prova 57."""
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
OUT = Path(__file__).parent
from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import terza as te  # noqa: E402

M = pickle.load(open(OUT / "mio_mazzo.pkl", "rb"))
serie = M["serie"]
P7 = REPO / "research/programma7"


def nw_var(x, L):
    u = x - x.mean()
    n = len(u)
    s = (u @ u) / n
    for k in range(1, L + 1):
        s += 2 * (1 - k / (L + 1)) * (u[k:] @ u[:-k]) / n
    return s


def t_nw(x, L):
    return x.mean() / math.sqrt(nw_var(x, L) / len(x))


def ljung_box(x, h):
    n = len(x)
    u = x - x.mean()
    g0 = u @ u
    q = 0.0
    for k in range(1, h + 1):
        r = (u[k:] @ u[:-k]) / g0
        q += r * r / (n - k)
    q *= n * (n + 2)
    return q, 1 - stats.chi2.cdf(q, h)


def blocchi(x, b):
    m = len(x) // b
    y = x[:m * b].reshape(m, b).sum(axis=1)
    return y.mean() / (y.std(ddof=1) / math.sqrt(m))


# controllo: la serie del mazzo e' quella del file della prova 57
f = pd.read_csv(P7 / "risultati_prima/settimane_G1.csv.gz", index_col=0)["netto"]
x57 = ast.periodo(f).to_numpy(float)
xm = serie["57 G1"].dropna().to_numpy(float)
print("57 G1: settimane file", len(x57), "mazzo", len(xm), "differenza max", float(np.abs(x57 - xm).max()))

for nome in ("57 G1", "88 G1N", "69 G11", "24 F5", "168 B"):
    s = serie[nome].dropna()
    x = s.to_numpy(float)
    n = len(x)
    t0 = x.mean() / (x.std(ddof=1) / math.sqrt(n))
    ac = [pd.Series(x).autocorr(k) for k in (1, 2, 3)]
    q8, p8 = ljung_box(x, 8)
    riga = f"{nome:8s} n {n} t {t0:.2f} ac1-3 {ac[0]:.2f} {ac[1]:.2f} {ac[2]:.2f} LB8 p {p8:.4f} | NW " + \
        " ".join(f"{L}:{t_nw(x, L):.2f}" for L in (4, 5, 8, 13, 26)) + f" | blocchi4 {blocchi(x, 4):.2f} blocchi13 {blocchi(x, 13):.2f}"
    print(riga)
    if nome == "57 G1":
        d = pd.to_datetime(s.index.to_numpy() * 86400, unit="s")
        y = s[d.year >= 2022].to_numpy(float)
        print("   senza il 2021: n", len(y), "ac1-3", " ".join(f"{pd.Series(y).autocorr(k):.2f}" for k in (1, 2, 3)),
              "LB8 p", round(ljung_box(y, 8)[1], 4), "se~", round(1 / math.sqrt(len(y)), 3))
        # Newey-West con la varianza ddof=1 come il t semplice (per confronto pulito)
        v1 = x.var(ddof=1)
        for L in (4, 5, 8, 13, 26):
            neff = n * (x.var(ddof=0)) / nw_var(x, L)
            print(f"   ritardi {L}: settimane efficaci {neff:.0f}")
        g57 = json.loads((P7 / "risultati_prima/esame.json").read_text())
        b = g57["boot"]
        se = (b["alto"] - b["basso"]) / (2 * 1.96)
        print("   boot blocchi 4 della prova 57: t equivalente", round(b["media"] / se, 2))
        i = g57["intero"]
        fino57 = json.loads((REPO / "audits/repro/mazzo_2026-11-12_esito_fino57.json").read_text())["scenari"]["prove 1-57 senza la conferma 50"]
        dev = fino57["dev_V"]
        Nf = fino57["famiglie"]
        v = list(np.array([-1.0, 1.0]) * dev / math.sqrt(2))
        base = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], v, 52, n_prove=Nf)
        print(f"   prova 57 (N {Nf}, dev {dev}): con 300 settimane {base:.4f} (repo 0,9451)")
        for L in (4, 8, 13, 26):
            neff = n * (x.var(ddof=0)) / nw_var(x, L)
            print(f"   prova 57 con settimane efficaci ({L} ritardi, {neff:.0f}): "
                  f"{te.sharpe_corretto(i['sharpe'], int(round(neff)), i['asimmetria'], i['curtosi'], v, 52, n_prove=Nf):.3f}")
