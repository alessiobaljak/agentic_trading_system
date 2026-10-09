"""Misure di processo per la consegna, ricavate dal log (Consegna, «Misure di processo»)."""
import json
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
reg = [v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"]
ris = {v["id"]: v for v in voci if v["tipo"] == "risultato"}
idee = {}
for v in reg:
    idee.setdefault(v["idea"], []).append(v)
per_idea = {}
for idea, vs in sorted(idee.items()):
    primo = min(t(v["data"]) for v in vs)
    ultimo = max(t(ris[v["id"]]["data"]) for v in vs if v["id"] in ris)
    per_idea[idea] = {"varianti": len(vs), "ritocchi": sum(1 for v in vs if v.get("ritocco_di")),
                      "minuti": round((ultimo - primo).total_seconds() / 60, 1)}
scarti = [v["id"] for v in voci if v["tipo"] == "scarto"]
cand_idee = [v["id"] for v in reg if not v.get("ritocco_di") and ris.get(v["id"], {}).get("candidato")]
cand_rit = [v["id"] for v in reg if v.get("ritocco_di") and ris.get(v["id"], {}).get("candidato")]
nette_r_neg = [v["id"] for v in reg if (ris.get(v["id"], {}).get("baseline_a") or {}).get("netta")
               and (ris.get(v["id"], {}).get("baseline_b") or {}).get("netta")
               and ris[v["id"]]["metriche"]["r_medio"] <= 0]
print(json.dumps({
    "prima_voce": voci[0]["data"], "ultima_voce": voci[-1]["data"],
    "durata_minuti": round((fine - inizio).total_seconds() / 60, 1), "pause_minuti": round(pause / 60, 1),
    "durata_senza_pause_minuti": round(((fine - inizio).total_seconds() - pause) / 60, 1),
    "varianti_testate": len(reg), "ritocchi": sum(1 for v in reg if v.get("ritocco_di")),
    "famiglie": len({v["famiglia"] for v in reg}), "idee": len(idee), "scarti": scarti,
    "candidati_da_idee_nuove": cand_idee, "candidati_da_ritocchi": cand_rit,
    "nette_a_e_b_con_r_non_positivo": nette_r_neg, "per_idea": per_idea}, indent=1, ensure_ascii=False))
