"""Stampa la stima dei trade (solo segnali) di tutte le varianti non ancora nel log."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import dati_btc as d
import strumenti as s
from varianti import VARIANTI

serie_cache = {}
for id_, v in VARIANTI.items():
    if len(sys.argv) > 1 and not any(id_.startswith(p) for p in sys.argv[1:]):
        continue
    serie = serie_cache.setdefault(v["tf"], s.Serie(v["tf"]))
    print(id_, v["tf"], v["direzione"], s.stima_trade(serie, v["entra"](serie), d.COSTRUZIONE, int(v["occupazione"])))
