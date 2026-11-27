"""Cartelle di risultati con file di dati (csv) che il mazzo non legge, e prefissi che il test non guarda. Sola lettura."""
import sys, re
from pathlib import Path
import pandas as pd
REPO = Path("/home/user/agentic_trading_system")
sys.path.insert(0, str(REPO))
from research.programma6 import asticella as ast
letti = set()
vero = pd.read_csv
def spia(f, *a, **k):
    letti.add(Path(f).resolve())
    return vero(f, *a, **k)
pd.read_csv = spia
ast.serie_nuove(); ast.senza_serie(); ast.le_prove()
pd.read_csv = vero
R = REPO / "research"
cartelle = sorted(list((R/"programma7").glob("risultati_*")) + list((R/"programma8").glob("risultati_*")) + list((R/"programma9").glob("risultati_*"))
                  + [R/"programma6"/f"risultati_{n}" for n in ("quarantanovesima","cinquantesima","cinquantunesima","cinquantaduesima","cinquantatreesima","cinquantaquattresima","cinquantacinquesima","cinquantaseiesima")])
cartelle_lette = {p.parent for p in letti}
PREF = ("settimane", "eventi", "operazioni", "giorni", "picchi", "mesi")
for c in cartelle:
    if not c.is_dir():
        continue
    csv = [f.name for f in c.iterdir() if f.is_file() and re.search(r"\.csv(\.gz)?$", f.name)]
    if not csv:
        continue
    if c.resolve() not in cartelle_lette:
        altri = [f for f in csv if not f.startswith(PREF)]
        print(f"NON LETTA {c.relative_to(R)}: {sorted(csv)[:6]}{' ...' if len(csv) > 6 else ''}  (fuori dai prefissi del test: {altri[:4]})")
