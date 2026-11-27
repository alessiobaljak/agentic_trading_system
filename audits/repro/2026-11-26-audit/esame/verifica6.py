import json, math, pickle, sys
import numpy as np
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import terza as te
S = pickle.load(open("scenari.pkl", "rb")); cand = S["cand"]
f = json.load(open("/home/user/agentic_trading_system/audits/repro/mazzo_2026-11-12_esito_fino57.json"))["scenari"]["prove 1-57 senza la conferma 50"]
v = list(np.array([-1.0, 1.0]) * f["dev_V"] / math.sqrt(2))
for extra in (0, 30, 60, 100, 200):
    print(f"G1 alla 57 con N {65+extra}: {te.sharpe_corretto(*cand['G1 (misura 12 nov)'], v, 52, n_prove=65+extra):.3f}")
