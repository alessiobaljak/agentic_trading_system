"""Misure di processo della consegna, ricavate dal log (Consegna, PROTOCOLLO.md)."""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registro  # noqa: E402


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


voci = registro.voci()
inizio, fine = t(voci[0]["data"]), t(voci[-1]["data"])
pause = sum((t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds() for v in voci if "pausa_da" in v)
print("prima voce", voci[0]["data"], "ultima", voci[-1]["data"])
print("durata minuti", (fine - inizio).total_seconds() / 60, "senza pause", ((fine - inizio).total_seconds() - pause) / 60)
reg = {v["id"]: v for v in voci if v.get("tipo") in ("registrazione", "scarto") and v.get("idea") and v.get("tipo_test", "variante") == "variante"}
per_idea = {}
for i, v in reg.items():
    per_idea.setdefault(v["idea"], []).append(i)
for idea, ids in sorted(per_idea.items()):
    prime = [t(v["data"]) for v in voci if v.get("id") in ids and v.get("tipo") in ("registrazione", "scarto")]
    ultime = [t(v["data"]) for v in voci if v.get("id") in ids and v.get("tipo") in ("risultato", "scarto")]
    print(idea, ids, "minuti", round((max(ultime) - min(prime)).total_seconds() / 60, 1))
ris = [v for v in voci if v.get("tipo") == "risultato" and "baseline_b" in v and v["id"] in reg]
print("candidati fase 2:", [v["id"] for v in ris if v.get("candidato")])
print("nette su a e b con R <= 0:", [v["id"] for v in ris if v["baseline_a"].get("netta") and v["baseline_b"].get("netta") and v["metriche"]["r_medio"] <= 0])
