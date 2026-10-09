"""Misure di processo della consegna, ricavate dal log (sola lettura)."""
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
pause = sum((t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds() for v in voci if "pausa_da" in v) / 60
reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in voci if v.get("tipo") == "risultato" and v["id"] in reg}
per_idea = {}
for id_, r in reg.items():
    d = per_idea.setdefault(r["idea"], {"prima": r["data"], "ultima": r["data"], "varianti": 0, "ritocchi": 0})
    d["prima"] = min(d["prima"], r["data"])
    d["ultima"] = max(d["ultima"], ris[id_]["data"])
    d["varianti"] += 1
    d["ritocchi"] += 1 if r.get("ritocco_di") else 0
out = {"durata_minuti": (fine - inizio).total_seconds() / 60, "pause_minuti": pause,
       "durata_senza_pause_minuti": (fine - inizio).total_seconds() / 60 - pause,
       "prima_voce": voci[0]["data"], "ultima_voce": voci[-1]["data"],
       "per_idea": {k: dict(v, minuti=(t(v["ultima"]) - t(v["prima"])).total_seconds() / 60) for k, v in sorted(per_idea.items())},
       "candidati_fase2_idee_nuove": [i for i, r in ris.items() if r.get("candidato") and not reg[i].get("ritocco_di")],
       "candidati_fase2_ritocchi": [i for i, r in ris.items() if r.get("candidato") and reg[i].get("ritocco_di")],
       "nette_a_e_b_con_r_non_positivo": [i for i, r in ris.items() if (r.get("baseline_a") or {}).get("netta")
                                          and (r.get("baseline_b") or {}).get("netta") and r["metriche"]["r_medio"] <= 0]}
print(json.dumps(out, ensure_ascii=False, indent=1))
