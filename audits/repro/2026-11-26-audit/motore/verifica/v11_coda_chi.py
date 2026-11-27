import sys, os, time
import numpy as np
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc
pan = sc.pannello(); t0 = pan["t0"]; S = pan["simboli"]; C = pan["close"]
i23 = sc.giorno(2026, 11, 23) - t0
attive = [s for j, s in enumerate(S) if np.isfinite(C[i23, j])]
manca = [s for s in attive if not (sc.DATI / s / "giorni" / f"{s}-1d-2026-11-24.zip").exists()]
print("attive il 23 nov:", len(attive), "| senza il file del 24:", len(manca))
print("iniziali delle mancanti:", "".join(sorted(set(s[0] for s in manca))), "| prime:", manca[:8], "ultime:", manca[-5:])
# quando sono stati scritti i file del 24 (ora di modifica)
t = sorted(os.path.getmtime(sc.DATI / s / "giorni" / f"{s}-1d-2026-11-24.zip") for s in attive if s not in manca)
print("file del 24 scritti fra", time.strftime("%Y-%m-%d %H:%M", time.gmtime(t[0])), "e", time.strftime("%Y-%m-%d %H:%M", time.gmtime(t[-1])), "UTC")
