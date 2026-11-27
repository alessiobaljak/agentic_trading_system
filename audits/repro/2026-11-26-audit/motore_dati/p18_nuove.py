import json, numpy as np
from pathlib import Path
from research.programma6 import seconda as sc
from research.programma6.esclusi import ESCLUSI
Q = "/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati"
info = json.load(open(Q + "/api/exchangeInfo.json"))["symbols"]
pan = sc.pannello(); sim = set(pan["simboli"]); cartelle = {p.name for p in sc.DATI.iterdir() if p.is_dir()}
nov1 = sc.giorno(2026, 10, 1)
for x in sorted(info, key=lambda x: int(x["onboardDate"])):
    ob = int(x["onboardDate"]) // 86400000
    if ob < nov1 or not x["symbol"].endswith("USDT") or x["contractType"] not in ("PERPETUAL", "TRADIFI_PERPETUAL"): continue
    s = x["symbol"]
    print(f"{s:14s} onboard {sc.data(ob)} tipo {x['underlyingType']:9s}/{x['contractType']:18s} stato {x['status']:15s} nel pannello {s in sim}  cartella {s in cartelle}  in ESCLUSI {s in ESCLUSI}")
