"""Misure di processo della consegna, dal log."""
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro as R  # noqa: E402


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


voci = R.voci()
inizio, fine = t(voci[0]["data"]), t(voci[-1]["data"])
pause = sum((t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds() for v in voci if "pausa_da" in v)
print("durata minuti", (fine - inizio).total_seconds() / 60, "pause minuti", pause / 60)
reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione"}
per_idea = {}
for v in voci:
    if v["tipo"] in ("registrazione", "scarto"):
        per_idea.setdefault(v["idea"], []).append(t(v["data"]))
    if v["tipo"] == "risultato" and v["id"] in reg:
        per_idea.setdefault(reg[v["id"]]["idea"], []).append(t(v["data"]))
for idea, ts in sorted(per_idea.items()):
    print(idea, "minuti", round((max(ts) - min(ts)).total_seconds() / 60, 1))
ris = [v for v in voci if v["tipo"] == "risultato"]
cand = [v["id"] for v in ris if v.get("candidato")]
netta_neg = [v["id"] for v in ris if v["baseline_a"].get("netta") and v["baseline_b"].get("netta") and v["metriche"]["r_medio"] <= 0]
netta_b = [v["id"] for v in ris if v["baseline_b"].get("netta")]
print("candidati", cand, "nette (a)+(b) con R<=0", netta_neg, "nette solo contro (b)", netta_b)
print("prev corrette", sum(1 for v in ris if v.get("previsione_corretta") is True), "sbagliate",
      sum(1 for v in ris if v.get("previsione_corretta") is False))
