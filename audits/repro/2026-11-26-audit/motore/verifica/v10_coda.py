import sys
from collections import Counter
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc
f = sc.giorni_parziali_in_coda
def arr(n):  # una matrice di chiusure con n[k] monete con prezzo nel giorno k
    m = max(n); c = np.full((len(n), m), np.nan)
    for k, x in enumerate(n): c[k, :x] = 1.0
    return c
for n in ([715, 715, 603], [715, 715, 603, 550], [715, 715, 603, 600], [715, 715, 300, 280], [10, 10, 5, 2], [10, 10, 5, 5], [715, 715, 643, 600]):
    print(n, "->", f(arr(n)))
# file giornalieri sul disco per gli ultimi giorni
cont = Counter()
for p in sc.DATI.iterdir():
    if not p.is_dir(): continue
    g = p / "giorni"
    if not g.exists(): continue
    for d in ("2026-11-20", "2026-11-21", "2026-11-22", "2026-11-23", "2026-11-24", "2026-11-25"):
        if (g / f"{p.name}-1d-{d}.zip").exists(): cont[d] += 1
print("simboli con il file giornaliero sul disco:", dict(sorted(cont.items())))
