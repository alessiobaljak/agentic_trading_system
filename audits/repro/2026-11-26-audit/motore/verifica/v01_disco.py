# sola lettura: com'e' fatto il disco dei dati e il pannello
import os, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc
D = sc.DATI
print("pannello:", sc.PANNELLO.exists(), round(sc.PANNELLO.stat().st_size/1e6,1), "MB", pd.Timestamp(sc.PANNELLO.stat().st_mtime, unit="s"))
cart = sorted(p.name for p in D.iterdir() if p.is_dir())
print("cartelle in p6g:", len(cart))
for s in ("BTCUSDT", "TRXUSDT", "BEUSDT", "LITUSDT"):
    p = D / s
    if not p.exists():
        print(s, "assente"); continue
    sub = sorted(x.name for x in p.iterdir())
    print(s, "sottocartelle:", sub)
    for k in sub:
        f = sorted(x.name for x in (p / k).iterdir())
        print("   ", k, len(f), f[:2], "...", f[-3:])
