"""Misure di processo della consegna, ricavate dal log (sezione «Consegna» del protocollo)."""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402

voci = [json.loads(r) for r in (q.CARTELLA_CAMPAGNA / "log.jsonl").read_text(encoding="utf-8").splitlines() if r.strip()]


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


prima, ultima = t(voci[0]["data"]), t(voci[-1]["data"])
pause = sum(((t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds() for v in voci if "pausa_da" in v), 0.0)
print("voci", len(voci), "prima", voci[0]["data"], "ultima", voci[-1]["data"],
      "minuti", round((ultima - prima).total_seconds() / 60, 1), "pause_minuti", round(pause / 60, 1))
reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in voci if v["tipo"] == "risultato" and v["id"] in reg}
per_idea = {}
for i, v in reg.items():
    per_idea.setdefault(v["idea"], []).append(i)
for idea, ids in sorted(per_idea.items()):
    inizio = min(t(reg[i]["data"]) for i in ids)
    fine = max(t(ris[i]["data"]) for i in ids if i in ris)
    print(idea, "varianti", len(ids), "minuti", round((fine - inizio).total_seconds() / 60, 1))
cand = [i for i in ris if ris[i].get("candidato_fase_2")]
nette_r_neg = [i for i in ris if ris[i]["baseline_a"].get("netta") and ris[i]["baseline_b"].get("netta")
               and ris[i]["metriche"]["r_medio"] <= 0]
print("varianti", len(reg), "ritocchi", sum(1 for v in reg.values() if v.get("ritocco_di")),
      "famiglie", len({v["famiglia"] for v in reg.values()}))
print("candidati", cand, "di cui ritocchi", [i for i in cand if reg[i].get("ritocco_di")])
print("nette con R non positivo", nette_r_neg)
print("scarti", sum(1 for v in voci if v["tipo"] == "scarto"))
