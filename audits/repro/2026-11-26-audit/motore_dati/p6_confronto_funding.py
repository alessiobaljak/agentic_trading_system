import json, copy, numpy as np, pandas as pd
from pathlib import Path
from research.programma6 import seconda as sc
from research.programma6.paper import aggiorna as ag
QUI = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati")
uni = json.load(open(QUI / "universi_nov.json"))
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]
F_pan = pan["funding"].copy()
pan2 = {**pan, "funding": pan["funding"].copy()}
stimati = ag.applica_stima(pan2)
F_st = pan2["funding"]
info = {x["symbol"]: x["fundingIntervalHours"] for x in json.load(open(QUI / "api" / "fundingInfo.json"))}
oct1, nov1, fine = sc.giorno(2026, 10, 1), sc.giorno(2026, 11, 1), t0 + T - 1
righe = []
for s in uni["unione"]:
    if s not in pan["simboli"]: continue
    j = pan["simboli"].index(s)
    d = json.load(open(QUI / "api" / "funding_nov" / f"{s}.json"))
    if not d: continue
    df = pd.DataFrame(d); df["ts"] = df["fundingTime"].astype(np.int64); df["r"] = df["fundingRate"].astype(float)
    df = df.drop_duplicates("ts")
    df["g"] = (df["ts"] // 60000 - 1) // 1440
    vero = df.groupby("g")["r"].sum()
    for g in range(oct1, fine + 1):
        if g not in vero.index: continue
        righe.append({"s": s, "g": g, "vero": vero[g], "pannello": F_pan[g - t0, j], "stima": F_st[g - t0, j],
                      "int": info.get(s, 8), "close_ok": bool(np.isfinite(pan["close"][g - t0, j]))})
x = pd.DataFrame(righe)
x.to_csv(QUI / "confronto_funding.csv.gz", index=False)
for nome, sel in (("ottobre (file mensile)", x.g < nov1), ("novembre (dopo il file)", x.g >= nov1)):
    y = x[sel & x.close_ok]
    print(nome, "righe", len(y), "| pannello-vero: media ass %.6f max %.6f corr %.3f" % ((y.pannello - y.vero).abs().mean(), (y.pannello - y.vero).abs().max(), np.corrcoef(y.pannello, y.vero)[0, 1]),
          "| stima-vero: media ass %.6f max %.6f corr %.3f" % ((y.stima - y.vero).abs().mean(), (y.stima - y.vero).abs().max(), np.corrcoef(y.stima, y.vero)[0, 1]))
y = x[(x.g >= nov1) & x.close_ok]
for iv in (1, 4, 8):
    z = y[y.int == iv]
    if len(z): print(" intervallo", iv, "h: righe", len(z), "stima-vero media ass %.6f, media vero %.6f media stima %.6f" % ((z.stima - z.vero).abs().mean(), z.vero.mean(), z.stima.mean()))
print("giorni stimati da applica_stima, primo giorno (conteggio):", pd.Series(list(stimati.values())).value_counts().head(3).to_dict())
