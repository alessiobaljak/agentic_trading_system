from pathlib import Path
import collections
from research.programma6 import seconda as sc
from research.programma6.esclusi import ESCLUSI
D = sc.DATI
c = collections.Counter()
for p in D.iterdir():
    if not p.is_dir() or p.name in ESCLUSI: continue
    for g in ("2026-11-22", "2026-11-23", "2026-11-24", "2026-11-25"):
        if (p / "giorni" / f"{p.name}-1d-{g}.zip").exists(): c[g] += 1
print(dict(sorted(c.items())))
