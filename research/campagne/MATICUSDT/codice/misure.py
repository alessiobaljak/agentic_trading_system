"""Misure di processo della consegna, ricavate dal log (sezione «Consegna» del protocollo).

Scrive esiti/misure_processo.json: durata dalla prima all'ultima voce (con e senza pause), minuti
per idea dalla registrazione della prima variante all'ultimo risultato delle sue varianti, varianti
diventate candidati in Fase 2 (idee nuove / ritocchi), varianti nette contro (a) e (b) con R medio
non positivo.
"""
import json
from datetime import datetime
from pathlib import Path

CARTELLA = Path(__file__).resolve().parents[1]
voci = [json.loads(r) for r in (CARTELLA / "log.jsonl").read_text(encoding="utf-8").splitlines() if r.strip()]


def t(v):
    return datetime.strptime(v["data"], "%Y-%m-%dT%H:%M:%SZ")


prima, ultima = t(voci[0]), t(voci[-1])
pause = sum(((datetime.strptime(v["pausa_a"], "%Y-%m-%dT%H:%M:%SZ") - datetime.strptime(v["pausa_da"], "%Y-%m-%dT%H:%M:%SZ")).total_seconds()
             for v in voci if v.get("tipo") == "nota" and "pausa_da" in v), 0.0)
reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in voci if v["tipo"] == "risultato" and v["id"] in reg}
per_idea = {}
for vid, r in reg.items():
    per_idea.setdefault(r["idea"], []).append(vid)
minuti = {}
for idea, ids in sorted(per_idea.items()):
    inizio = min(t(reg[i]) for i in ids)
    fine = max(t(ris[i]) for i in ids if i in ris)
    minuti[idea] = round((fine - inizio).total_seconds() / 60, 1)
cand_nuove = [i for i, r in ris.items() if r.get("candidato") and reg[i].get("ritocco_di") is None]
cand_ritocchi = [i for i, r in ris.items() if r.get("candidato") and reg[i].get("ritocco_di") is not None]
nette_non_positive = [i for i, r in ris.items() if r.get("baseline_a", {}).get("netta") and r.get("baseline_b", {}).get("netta")
                      and (r["metriche"]["r_medio"] or 0) <= 0]
out = {"prima_voce": voci[0]["data"], "ultima_voce": voci[-1]["data"],
       "durata_minuti": round((ultima - prima).total_seconds() / 60, 1),
       "durata_minuti_senza_pause": round(((ultima - prima).total_seconds() - pause) / 60, 1),
       "minuti_per_idea": minuti, "varianti_testate": len(ris),
       "ritocchi": sum(1 for i in ris if reg[i].get("ritocco_di")),
       "candidati_fase2_idee_nuove": cand_nuove, "candidati_fase2_ritocchi": cand_ritocchi,
       "nette_a_e_b_con_r_non_positivo": nette_non_positive}
(CARTELLA / "esiti" / "misure_processo.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps(out, ensure_ascii=False))
