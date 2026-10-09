"""Testa in serie un elenco di varianti gia' registrate (``prova.py test``) e scrive un riepilogo.

Uso: python research/campagne/MATICUSDT/codice/testa_tutte.py V01 V02 ...
Riepilogo in esiti/riepilogo.txt (una riga per variante).
"""
import json
import subprocess
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
ESITI = QUI.parent / "esiti"
for vid in sys.argv[1:]:
    p = subprocess.run([sys.executable, str(QUI / "prova.py"), "test", vid], capture_output=True, text=True)
    try:
        e = json.loads((ESITI / f"{vid}.json").read_text())
        m, a, b = e["metriche"], e.get("baseline_a", {}), e.get("baseline_b", {})
        riga = (f"{vid} n={m['trade']} r={m['r_medio']} r-3={m['r_medio_senza_3_migliori']} pf={m['profit_factor']} "
                f"a={a.get('media')} t_a={a.get('t')} netta_a={a.get('netta')} b={b.get('media')} t_b={b.get('t')} "
                f"netta_b={b.get('netta')} perc={e.get('percentile_caso')} cand={e.get('candidato')} "
                f"anni={json.dumps(m['r_medio_per_anno'])}")
    except Exception as ex:  # noqa: BLE001
        riga = f"{vid} ERRORE {ex} {p.stderr[-500:]}"
    with open(ESITI / "riepilogo.txt", "a") as f:
        f.write(riga + "\n")
print("fatto")
