import json, numpy as np, pandas as pd
from scipy.stats import rankdata
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as n
Q = "/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati"
uni = json.load(open(Q + "/universi_nov.json"))
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]
def vero_giorni(path):
    d = json.load(open(path)); df = pd.DataFrame(d)
    df["ts"] = df["fundingTime"].astype(np.int64); df["r"] = df["fundingRate"].astype(float)
    df = df.drop_duplicates("ts"); df["g"] = (df["ts"] // 60000 - 1) // 1440
    return df.groupby("g")["r"].sum()
fv = {s: vero_giorni(f"{Q}/api/funding_nov/{s}.json") for s in uni["unione"]}
extra = {s: vero_giorni(f"{Q}/api/fr_{s}.json") for s in ("BEUSDT", "SNXXUSDT", "MUUUSDT", "MVLLUSDT", "ZHONGJIUSDT")}
rc = n.ritorni_chiusura(pan["close"])
conta = {s: [0, 0, 0] for s in extra}
for g in range(sc.giorno(2026, 10, 12), t0 + T):
    i = g - t0
    lun = g - ((g + 3) % 7)
    u = uni["universi"].get(sc.data(lun))
    if u is None: continue
    sig = n.sigma30(rc, i)
    for s, f in extra.items():
        j = pan["simboli"].index(s)
        if not np.isfinite(sig[j]): continue
        nomi = [x for x in u if np.isfinite(sig[pan["simboli"].index(x)])] + [s]
        f7 = np.array([sum(( (fv[x] if x in fv else extra[x]).get(d, 0.0) for d in range(g - 7, g))) for x in nomi])
        p = rankdata(-np.round(f7, 12), method="average") / len(nomi)
        conta[s][0] += 1; conta[s][1] += p[-1] > 0.8; conta[s][2] += p[-1] <= 0.2
print("se fossero nell'universo, dal 12 ott al 23 nov: giorni guardati, giorni nel 20% da comprare, giorni nel 20% da vendere")
for s, c in conta.items(): print(" ", s, c)
