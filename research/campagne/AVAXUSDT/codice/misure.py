"""Misure di processo della consegna, ricavate dal log (Consegna, PROTOCOLLO.md)."""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from log_campagna import ids_esistenti  # noqa: E402


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


voci = ids_esistenti()
date = [t(v["data"]) for v in voci]
inizio, fine = min(date), max(date)
pause = sum(((t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds() for v in voci if "pausa_da" in v), 0.0)
print("prima voce", inizio, "ultima voce", fine, "durata minuti", round((fine - inizio).total_seconds() / 60, 1),
      "senza pause", round(((fine - inizio).total_seconds() - pause) / 60, 1))
reg = [v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"]
ris = {v["id"]: v for v in voci if v["tipo"] == "risultato" and "metriche" in v}
per_idea = {}
for r in reg:
    per_idea.setdefault(r["idea"], []).append(r)
for idea, rr in sorted(per_idea.items()):
    primo = min(t(r["data"]) for r in rr)
    ultimo = max(t(ris[r["id"]]["data"]) for r in rr if r["id"] in ris)
    print(idea, "varianti", len(rr), "minuti", round((ultimo - primo).total_seconds() / 60, 1))
print("varianti", len(reg), "ritocchi", sum(1 for r in reg if r.get("ritocco_di")),
      "famiglie", len({r["famiglia"] for r in reg}))
cand_nuove = [r["id"] for r in reg if not r.get("ritocco_di") and ris[r["id"]].get("candidato")]
cand_rit = [r["id"] for r in reg if r.get("ritocco_di") and ris[r["id"]].get("candidato")]
print("candidati in Fase 2 da idee nuove", cand_nuove, "da ritocchi", cand_rit)
nette_r_non_pos = [r["id"] for r in reg if ris[r["id"]].get("baseline_a", {}).get("netta")
                   and ris[r["id"]].get("baseline_b", {}).get("netta") and ris[r["id"]]["metriche"]["r_medio"] <= 0]
print("nette contro (a) e (b) con R medio non positivo", nette_r_non_pos)
print("scarti", [v["id"] for v in voci if v["tipo"] == "scarto"])
