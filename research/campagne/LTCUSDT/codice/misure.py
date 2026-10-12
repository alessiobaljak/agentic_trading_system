"""Misure di processo e riepilogo delle varianti, ricavati SOLO dal log (Consegna, sezione «Misure di processo»)."""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aggiungi_log import LOG  # noqa: E402


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


voci = [json.loads(r) for r in LOG.read_text(encoding="utf-8").splitlines() if r.strip()]
prima, ultima = t(voci[0]["data"]), t(voci[-1]["data"])
pause = [(t(v["pausa_da"]), t(v["pausa_a"])) for v in voci if v.get("tipo") == "nota" and "pausa_da" in v]
minuti_pausa = sum((b - a).total_seconds() / 60 for a, b in pause)
print("prima voce", voci[0]["data"], "ultima", voci[-1]["data"])
print("durata minuti", round((ultima - prima).total_seconds() / 60, 1), "senza pause", round((ultima - prima).total_seconds() / 60 - minuti_pausa, 1))
reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in voci if v.get("tipo") == "risultato"}
scarti = [v for v in voci if v.get("tipo") == "scarto"]
print("varianti testate", len(reg), "ritocchi", sum(1 for v in reg.values() if v.get("ritocco_di")),
      "famiglie", len({v["famiglia"] for v in reg.values()}), "scarti", len(scarti))
per_idea = {}
for i, v in reg.items():
    per_idea.setdefault(v["idea"], []).append(i)
for idea, ids in sorted(per_idea.items()):
    inizio = min(t(reg[i]["data"]) for i in ids)
    fine = max(t(ris[i]["data"]) for i in ids if i in ris)
    print(f"{idea}: varianti {ids} minuti {round((fine - inizio).total_seconds() / 60, 1)}")
righe = []
for i, v in reg.items():
    r = ris[i]
    e = r["esito_fase2"]
    righe.append((r["baseline_b"].get("t") or float("-inf"), i, r["metriche"]["trade"], r["metriche"]["profit_factor"],
                  r["metriche"]["r_medio"], r["baseline_a"].get("t"), e["netta_a"], e["netta_b"], e["candidato"],
                  r["percentile_caso"], r["previsione_corretta"]))
print("id trade PF R t_a t_b netta_a netta_b candidato percentile previsione")
for tb, i, n, pf, rm, ta, na, nb, c, pc, pr in sorted(righe, reverse=True):
    print(i, n, pf, rm, ta, round(tb, 3), na, nb, c, pc, pr)
print("candidati", sum(1 for x in righe if x[8]))
print("nette contro a e b con R non positivo", sum(1 for x in righe if x[6] and x[7] and not (x[4] and x[4] > 0)))
print("previsioni corrette", sum(1 for x in righe if x[10]), "su", len(righe))
tb = [x[0] for x in righe]
print("t contro b: media", round(sum(tb) / len(tb), 3), "sopra 1:", sum(1 for x in tb if x > 1), "sopra 2:", sum(1 for x in tb if x > 2))
print("percentile >= 90:", sum(1 for x in righe if x[9] is not None and x[9] >= 90))
