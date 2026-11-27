"""Le settimane di G1 sono legate fra loro? Effetto sul t e sulla probabilita' che non sia fortuna (sola lettura)."""
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
from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import terza as te  # noqa: E402

serie, soli = pickle.load(open(OUT / "mazzo.pkl", "rb"))
g1 = serie["57 G1"].dropna()
x = g1.to_numpy(float)
n = len(x)
print("G1 settimane", n, "primo", sc.data(int(g1.index[0])), "ultimo", sc.data(int(g1.index[-1])))
acf = [g1.autocorr(k) for k in range(1, 13)]
print("autocorrelazioni 1-12:", [round(a, 3) for a in acf], "errore tipico ~", round(1 / math.sqrt(n), 3))
q = n * (n + 2) * sum(a * a / (n - k) for k, a in enumerate(acf[:8], 1))
print(f"Ljung-Box 8 ritardi: Q {q:.1f}, p {1 - stats.chi2.cdf(q, 8):.4f}")
date = pd.to_datetime(g1.index.to_numpy() * 86400, unit="s")
g1b = g1[date.year >= 2022]
print("senza il 2021: ac1", round(g1b.autocorr(1), 3), "ac2", round(g1b.autocorr(2), 3), "ac3", round(g1b.autocorr(3), 3))
# rendimenti a 4 settimane non sovrapposti: Sharpe annuo
for k in (1, 2, 4, 13):
    blocchi = x[: n // k * k].reshape(-1, k).sum(axis=1)
    print(f"Sharpe annuo da blocchi di {k:2d} settimane non sovrapposti: {blocchi.mean() / blocchi.std(ddof=1) * math.sqrt(52 / k):.2f} "
          f"(blocchi {len(blocchi)}, t {blocchi.mean() / blocchi.std(ddof=1) * math.sqrt(len(blocchi)):.2f})")


def lrv_ratio(v, L):
    u = v - v.mean()
    g0 = (u @ u) / len(v)
    s = g0 + 2 * sum((1 - k / (L + 1)) * (u[k:] @ u[:-k]) / len(v) for k in range(1, L + 1))
    return s / g0


mis = json.loads((REPO / "audits/repro/g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]["G1"]
sr, sk, ku = mis["sharpe"], mis["asimmetria"], mis["curtosi"]


def dsr_t(sr_a, T, sk, ku, dev_a, NN):
    g = 0.5772156649015329
    srw, sdw = sr_a / math.sqrt(52), dev_a / math.sqrt(52)
    sr0 = sdw * ((1 - g) * stats.norm.ppf(1 - 1 / NN) + g * stats.norm.ppf(1 - 1 / (NN * math.e)))
    den = math.sqrt(1 - sk * srw + (ku - 1) / 4 * srw ** 2)
    return stats.norm.cdf((srw - sr0) * math.sqrt(T - 1) / den)


for L in (4, 8, 13, 26):
    r = lrv_ratio(x, L)
    Teff = n / r
    print(f"Bartlett {L:2d}: varianza di lungo periodo / semplice {r:.2f}; settimane efficaci {Teff:.0f}; t {sr * math.sqrt(n / 52) / math.sqrt(r):.2f}; "
          f"probabilita' alla 57 (N 65, dev 0,5667) {dsr_t(sr, Teff, sk, ku, 0.5667, 65):.3f} invece di {dsr_t(sr, n, sk, ku, 0.5667, 65):.3f}; "
          f"oggi (N 200, dev 0,6776) {dsr_t(sr, Teff, sk, ku, 0.6776, 200):.3f} invece di {dsr_t(sr, n, sk, ku, 0.6776, 200):.3f}")

# le altre in produzione
for nome in ("24 F5", "69 G11", "88 G1N", "168 B", "28 F5+M7+K2"):
    v = serie[nome].dropna().to_numpy(float)
    s = v.mean() / v.std(ddof=1) * math.sqrt(52)
    print(nome, "ac1", round(pd.Series(v).autocorr(1), 2), "t", round(s * math.sqrt(len(v) / 52), 2),
          "t Bartlett 8 / 13 / 26:", [round(s * math.sqrt(len(v) / 52) / math.sqrt(lrv_ratio(v, L)), 2) for L in (8, 13, 26)])

# famiglie del mazzo: quante hanno ac1 sopra 2 errori tipici
gr = pickle.load(open(OUT / "gruppi.pkl", "rb"))
alte = []
for g in gr:
    m = pd.concat([serie[k] for k in g["membri"]], axis=1).mean(axis=1).dropna()
    if len(m) >= 52:
        a = m.autocorr(1)
        if a > 2 / math.sqrt(len(m)):
            alte.append((round(a, 2), round(g["sharpe"], 2), len(g["membri"]), g["membri"][:3]))
print("famiglie con ac1 oltre 2 errori tipici:", len(alte), "su", len(gr))
for a in sorted(alte, reverse=True)[:12]:
    print("  ", a)
