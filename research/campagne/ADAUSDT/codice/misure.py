"""Misure di processo della consegna, ricavate solo dal log."""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registro  # noqa: E402

voci = registro.voci_presenti()


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


inizio, fine = t(voci[0]["data"]), t(voci[-1]["data"])
pause = sum((t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds() for v in voci if v.get("pausa_da"))
idee = {}
for v in voci:
    if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante":
        idee.setdefault(v["idea"], {"ids": [], "prima": t(v["data"])})["ids"].append(v["id"])
for idea, d in idee.items():
    ultimi = [t(v["data"]) for v in voci if v["tipo"] == "risultato" and v["id"] in d["ids"]]
    d["minuti"] = round((max(ultimi) - d["prima"]).total_seconds() / 60, 1)
out = {"prima_voce": voci[0]["data"], "ultima_voce": voci[-1]["data"],
       "durata_minuti": round((fine - inizio).total_seconds() / 60, 1),
       "durata_senza_pause_minuti": round(((fine - inizio).total_seconds() - pause) / 60, 1),
       "varianti": sum(1 for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"),
       "ritocchi": sum(1 for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante" and v.get("ritocco_di")),
       "scarti": sum(1 for v in voci if v["tipo"] == "scarto"),
       "idee": {k: {"varianti": d["ids"], "minuti": d["minuti"]} for k, d in sorted(idee.items())}}
print(json.dumps(out, indent=1, default=str))
