"""Confronto fra il funding nella cache della campagna e quello del caricatore attuale (solo lettura)."""
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402

nuovo = comune.dati.carica_funding(comune.SIMBOLO, comune.INIZIO, comune.FINE)
print("caricatore attuale: settlement", len(nuovo), "con millisecondi diversi da zero:",
      sum(1 for t, _ in nuovo if t % 1000 != 0))
p = comune.CACHE / "funding.pkl"
if p.is_file():
    with open(p, "rb") as f:
        vecchio = pickle.load(f)
    print("cache: settlement", len(vecchio), "con millisecondi diversi da zero:", sum(1 for t, _ in vecchio if t % 1000 != 0),
          "massimo scarto in ms:", max(t % 1000 for t, _ in vecchio))
    print("stessi tassi nello stesso ordine:", [r for _, r in vecchio] == [r for _, r in nuovo])
    print("stessi istanti al secondo:", [t // 1000 for t, _ in vecchio] == [t // 1000 for t, _ in nuovo])
v = comune.CACHE / "versione_caricatore.txt"
print("versione della cache registrata:", v.read_text().strip() if v.is_file() else None)
