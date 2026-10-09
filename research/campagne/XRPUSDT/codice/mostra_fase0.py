"""Stampa compatta degli intervalli tolti e dei buchi per timeframe (da data/insample/XRPUSDT/fase0.json)."""
import json

from research.src import dati

d = json.loads((dati.RADICE_DEFAULT / "data" / "insample" / "XRPUSDT" / "fase0.json").read_text())
for tf, a in d["allineamento"].items():
    print("==", tf)
    print("  tolte_last:", "; ".join(f"{x[0]}..{x[1]} ({x[2]})" for x in a["intervalli_tolte_last"]))
    print("  tolte_mark:", "; ".join(f"{x[0]}..{x[1]} ({x[2]})" for x in a["intervalli_tolte_mark"]))
    print("  buchi:", "; ".join(f"{x[0]}..{x[1]} ({x[2]})" for x in a["buchi_dopo_allineamento"]))
