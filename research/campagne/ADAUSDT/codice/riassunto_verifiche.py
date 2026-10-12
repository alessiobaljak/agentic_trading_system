"""Stampa un riassunto delle verifiche della Fase 4 di una variante (dal file di uscita)."""
import json
import sys
from pathlib import Path

f = Path(__file__).resolve().parents[4] / "research" / "data" / "insample" / "ADAUSDT" / "uscita_verifiche.txt"
for riga in f.read_text().splitlines():
    v = json.loads(riga)
    if not v["id"].startswith(sys.argv[1]):
        continue
    for caso, e in v["esiti"].items():
        b = e.get("b", {})
        print(v["id"], v["verifica"], caso, "trade", e.get("trade"), "r", round(e["r_medio"], 4) if "r_medio" in e else None,
              "t_b", b.get("t"), "netta_b", b.get("netta"), "senza3", e.get("r_senza_3"), "viol", e.get("violazioni_liquidazione"))
