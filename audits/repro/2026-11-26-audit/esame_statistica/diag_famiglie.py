"""Famiglie del mazzo di oggi e sensibilita' dello Sharpe corretto di G1 (sola lettura)."""
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
OUT = Path(__file__).parent
from research.programma6 import asticella as ast  # noqa: E402
from research.programma6 import terza as te  # noqa: E402

serie, soli = pickle.load(open(OUT / "mazzo.pkl", "rb"))
gr = pickle.load(open(OUT / "gruppi.pkl", "rb"))
mis = json.loads((REPO / "audits/repro/g1_parte2_2026-11-12_esito_misure.json").read_text())["misure"]["G1"]
G1 = (mis["sharpe"], mis["settimane"], mis["asimmetria"], mis["curtosi"])

fam = []
for g in gr:
    t = g["sharpe"] * math.sqrt(g["settimane"] / 52)
    fam.append({"n": len(g["membri"]), "sharpe": g["sharpe"], "settimane": g["settimane"], "t": t,
                "membri": g["membri"]})
fam = sorted(fam, key=lambda x: -x["sharpe"])
print("famiglie con Sharpe > 1,5:")
for f in fam:
    if f["sharpe"] > 1.5:
        print(f"  {f['sharpe']:+.2f} t {f['t']:+.1f} sett {f['settimane']} n {f['n']}: {', '.join(f['membri'][:12])}{' ...' if f['n'] > 12 else ''}")
g1f = next(f for f in fam if "57 G1" in f["membri"])
print("famiglia di G1:", g1f["n"], "membri, Sharpe", round(g1f["sharpe"], 3), "t", round(g1f["t"], 2))
print("  membri:", g1f["membri"])
# Sharpe dei membri della famiglia di G1
sm = sorted(((m, ast.sharpe(serie[m]), len(serie[m])) for m in g1f["membri"]), key=lambda x: -x[1])
print("  Sharpe dei membri:", [(m, round(s, 2), w) for m, s, w in sm])

sr_g, sr_v = ast.per_v(gr, soli, False), ast.per_v(gr, soli, True)
N = len(sr_g)


def dsr(v, n=None):
    return te.sharpe_corretto(*G1, v, 52, n_prove=n or N)


print(f"\nG1 oggi: N {N}, in V {len(sr_v)}, dev {np.std(sr_v, ddof=1):.4f} -> {dsr(sr_v):.4f}")
# V senza le famiglie con t > 3 (simmetrico all'aggiunta del 23 ottobre)
v_sim = [s for s, w in [(g['sharpe'], g['settimane']) for g in gr] + [(x, 300) for x in soli]
         if abs(s * math.sqrt(w / 52)) <= 3]
print(f"V simmetrico (|t| <= 3): {len(v_sim)} famiglie, dev {np.std(v_sim, ddof=1):.4f} -> G1 {dsr(v_sim):.4f}")
# V senza le famiglie di 157 e 161 (incasso quasi fisso)
v_no = [g["sharpe"] for g in gr if not any(m.startswith(("157 ", "161 ")) for m in g["membri"])
        and g["sharpe"] * math.sqrt(g["settimane"] / 52) >= -3] + [x for x in soli if x * math.sqrt(300 / 52) >= -3]
print(f"V senza 157 e 161: {len(v_no)}, dev {np.std(v_no, ddof=1):.4f} -> G1 {dsr(v_no):.4f}")
# V senza la famiglia di G1 stessa
v_nog1 = [g["sharpe"] for g in gr if "57 G1" not in g["membri"] and g["sharpe"] * math.sqrt(g["settimane"] / 52) >= -3] \
    + [x for x in soli if x * math.sqrt(300 / 52) >= -3]
print(f"V senza la famiglia di G1: {len(v_nog1)}, dev {np.std(v_nog1, ddof=1):.4f} -> G1 {dsr(v_nog1):.4f}")
# famiglie corte in V
print("\nfamiglie in V con meno di 104 settimane:")
for g in gr:
    t = g["sharpe"] * math.sqrt(g["settimane"] / 52)
    if g["settimane"] < 104 and t >= -3:
        print(f"  {g['sharpe']:+.2f} sett {g['settimane']} t {t:+.2f}: {g['membri']}")
# soli in V e fuori
print("\nsenza serie:", len(soli), "in V:", sum(1 for x in soli if x * math.sqrt(300 / 52) >= -3))
print("  valori:", sorted(round(x, 2) for x in soli))
json.dump({"famiglie": fam}, open(OUT / "famiglie.json", "w"), ensure_ascii=False, indent=0)
