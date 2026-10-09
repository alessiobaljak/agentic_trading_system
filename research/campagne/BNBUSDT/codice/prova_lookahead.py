"""Ricerca di lookahead nel candidato BNBUSDT-043 (Fase 4, ritardo crollato).

Per 300 barre a caso della costruzione si ricalcolano gli indicatori sulla serie TRONCATA alla
barra i (candele[:i+1]) e si confrontano condizione, segnale e uscita con quelli calcolati sulla
serie intera. Se un indicatore usasse barre future, i valori alla barra i sarebbero diversi.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import verifiche  # noqa: E402

v = verifiche.fab()("lookahead")
d = C.carica("1h", "costruzione")
cand = d["candele"]
intero = v.prepara(cand)
rng = np.random.default_rng(0)
idx = sorted(rng.choice(np.arange(300, len(cand)), 300, replace=False).tolist())
# in piu' tutte le barre di segnale del candidato
segnali = [i for i in range(len(cand)) if v.condizione(intero, i)]
idx = sorted(set(idx) | set(segnali))
diversi = 0
for i in idx:
    tronco = v.prepara(cand[:i + 1])
    for k in ("atr", "rsi2", "sma200", "sma5", "esci"):
        a, b = float(intero[k][i]), float(tronco[k][i])
        if not (a == b or (np.isnan(a) and np.isnan(b)) or abs(a - b) <= 1e-9 * max(1.0, abs(a))):
            diversi += 1
            print("DIVERSO", i, k, a, b)
    if v.condizione(intero, i) != v.condizione(tronco, i):
        diversi += 1
        print("CONDIZIONE DIVERSA", i)
print(f"barre controllate {len(idx)} (di cui {len(segnali)} barre di segnale), differenze {diversi}")
