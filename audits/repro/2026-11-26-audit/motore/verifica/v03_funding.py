# sola lettura: funding vero (interfaccia, scaricato dal revisore e ricontrollato su 6 monete) contro pannello e applica_stima
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc
from research.programma6.paper import aggiorna as ag
LORO = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati")
OUT = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore/verifica")
uni = json.load(open(LORO / "universi_nov.json"))["unione"]
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]; fine = t0 + T - 1
print("pannello: primo", sc.data(t0), "ultimo", sc.data(fine), "monete", len(pan["simboli"]))
n_ok = np.isfinite(pan["close"]).sum(axis=1)
print("monete con prezzo negli ultimi 6 giorni:", [(sc.data(t0 + T - 6 + k), int(n_ok[T - 6 + k])) for k in range(6)])
F_pan = pan["funding"].copy()
p2 = {**pan, "funding": pan["funding"].copy()}
st = ag.applica_stima(p2); F_st = p2["funding"]
print("applica_stima: monete stimate", len(st), "primo giorno stimato (conteggio):", pd.Series(list(st.values())).value_counts().to_dict())
oct1, oct31, nov1 = sc.giorno(2026, 10, 1), sc.giorno(2026, 10, 31), sc.giorno(2026, 11, 1)
righe = []
for s in uni:
    j = pan["simboli"].index(s)
    d = json.load(open(LORO / "api" / "funding_nov" / f"{s}.json"))
    if not d:
        continue
    df = pd.DataFrame(d).drop_duplicates("fundingTime")
    ts = df["fundingTime"].astype(np.int64).to_numpy()
    g = (ts // 60000 - 1) // 1440
    v = pd.Series(df["fundingRate"].astype(float).to_numpy(), index=g).groupby(level=0).sum()
    for gg in range(oct1, fine + 1):
        if not np.isfinite(pan["close"][gg - t0, j]):
            continue
        righe.append((s, gg, v.get(gg, 0.0), F_pan[gg - t0, j], F_st[gg - t0, j]))
x = pd.DataFrame(righe, columns=["s", "g", "vero", "pan", "stima"])
x.to_csv(OUT / "v03_funding.csv.gz", index=False)
ott = x[(x.g < oct31)]
print("ottobre 1-30: righe", len(ott), "pannello==vero (1e-12):", int((ott.pan - ott.vero).abs().lt(1e-12).sum()),
      "max diff", float((ott.pan - ott.vero).abs().max()))
o31 = x[x.g == oct31]
print("31 ottobre: righe", len(o31), "pannello==vero:", int((o31.pan - o31.vero).abs().lt(1e-12).sum()),
      "media |pan-vero|", round(float((o31.pan - o31.vero).abs().mean()), 6), "| stima==pannello sul 31:", int((o31.stima - o31.pan).abs().lt(1e-15).sum()))
print("   TRX 31 ott:", o31[o31.s == "TRXUSDT"][["vero", "pan", "stima"]].to_dict("records"))
nov = x[(x.g >= nov1) & (x.g <= sc.giorno(2026, 11, 23))]
for nome in ("pan", "stima"):
    e = (nov[nome] - nov.vero)
    print(f"1-23 nov [{nome}]: righe {len(nov)} media |err| {e.abs().mean():.6f} corr {np.corrcoef(nov[nome], nov.vero)[0,1]:.3f}")
print("1-23 nov: quota giorni-moneta al tasso di base 0,0003 (vero):", round(float(np.isclose(nov.vero, 0.0003, atol=1e-9).mean()), 3))
