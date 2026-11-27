import json, numpy as np
from research.programma6 import seconda as sc
QUI = "/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati"
info = {x["symbol"]: x for x in json.load(open(QUI + "/api/exchangeInfo.json"))["symbols"]}
pan = sc.pannello(); t0 = pan["t0"]; C, O = pan["close"], pan["open"]
ok = np.isfinite(C)
for j, s in enumerate(pan["simboli"]):
    okj = np.flatnonzero(ok[:, j])
    if len(okj) < 2: continue
    for t in okj[1:][np.diff(okj) > 2]:
        p = okj[okj < t][-1]
        rap = O[t, j] / C[p, j]
        ob = info.get(s, {}).get("onboardDate")
        print(f"{s:14s} buco {sc.data(p+t0)} -> {sc.data(t+t0)} ({t-p-1} giorni) prezzo dopo/prima {rap:8.3g}  onboard oggi {sc.data(int(ob)//86400000) if ob else '-'}  tipo {info.get(s,{}).get('underlyingType','-')}")
# simboli il cui onboardDate di oggi e' molto dopo la prima candela del pannello (contratto rinato)
print("--- onboardDate di exchangeInfo molto dopo la prima candela del pannello (stesso nome, contratto nuovo?)")
for j, s in enumerate(pan["simboli"]):
    if s not in info: continue
    okj = np.flatnonzero(ok[:, j])
    if not len(okj): continue
    ob = int(info[s]["onboardDate"]) // 86400000
    if ob - (okj[0] + t0) > 30:
        print(f"  {s:14s} prima candela {sc.data(okj[0]+t0)}  onboard {sc.data(ob)}  tipo {info[s]['underlyingType']}/{info[s]['contractType']} stato {info[s]['status']}")
