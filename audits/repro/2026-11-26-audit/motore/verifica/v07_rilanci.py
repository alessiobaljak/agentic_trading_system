# sola lettura: aperture lontane dalla chiusura del giorno prima, e onboardDate di exchangeInfo
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc
QUI = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore/verifica")
info = {x["symbol"]: x for x in json.load(open(QUI / "api" / "exchangeInfo.json"))["symbols"]}
pan = sc.pannello(); t0 = pan["t0"]; S = pan["simboli"]
O, C, V = pan["open"], pan["close"], pan["quote_volume"]
ok = np.isfinite(C)
salti = []
for j, s in enumerate(S):
    idx = np.flatnonzero(ok[:, j])
    for a, b in zip(idx[:-1], idx[1:]):
        r = O[b, j] / C[a, j] - 1
        if abs(r) > 0.20:
            onb = sc.data(int(info[s]["onboardDate"]) // 86_400_000) if s in info else "-"
            salti.append((s, sc.data(a + t0), sc.data(b + t0), int(b - a), round(C[a, j], 6), round(O[b, j], 6), round(100 * r, 1), onb,
                          round(float(np.nan_to_num(V[a, j])) / 1e6, 2)))
print("aperture lontane piu' del 20% dalla chiusura precedente:", len(salti))
for x in salti: print("  ", x)
j = S.index("LITUSDT")
for g in range(sc.giorno(2025, 12, 17), sc.giorno(2025, 12, 27)):
    i = g - t0
    print("LIT", sc.data(g), "open %.4f close %.4f vol %.2f mln" % (O[i, j], C[i, j], np.nan_to_num(V[i, j]) / 1e6))
