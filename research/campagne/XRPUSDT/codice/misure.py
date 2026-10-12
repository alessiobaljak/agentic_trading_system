"""Misure di processo della consegna, ricavate dal log (e dalle spiegazioni concorrenti in ipotesi.md)."""
from collections import defaultdict
from datetime import datetime

from research.campagne.XRPUSDT.codice import quadro as q


def t(x):
    return datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")


log = q.leggi_log()
date = [t(v["data"]) for v in log]
durata = (max(date) - min(date)).total_seconds() / 60
pause = sum((t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds() / 60 for v in log if "pausa_da" in v)
print(f"prima voce {min(date)}, ultima {max(date)}: {durata:.0f} minuti, pause {pause:.0f}, senza pause {durata - pause:.0f}")
reg = {v["id"]: v for v in log if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in log if v.get("tipo") == "risultato" and v["id"] in reg}
per_idea = defaultdict(list)
for vid, r in reg.items():
    per_idea[r["idea"]].append((t(r["data"]), t(ris[vid]["data"])))
for idea in sorted(per_idea):
    a = min(x for x, _ in per_idea[idea])
    b = max(y for _, y in per_idea[idea])
    print(f"{idea}: {len(per_idea[idea])} varianti, {(b - a).total_seconds() / 60:.1f} minuti")
scarti = [v["id"] for v in log if v.get("tipo") == "scarto"]
print("scarti:", scarti)
print("varianti:", len(reg), "ritocchi:", sum(1 for r in reg.values() if r.get("ritocco_di")),
      "famiglie:", len({r["famiglia"] for r in reg.values()}))
cand = [v for v, r in ris.items() if r.get("candidato")]
print("candidati:", cand, "da ritocchi:", [v for v in cand if reg[v].get("ritocco_di")])
nette_neg = [v for v, r in ris.items() if r.get("baseline_a", {}).get("netta") and r.get("baseline_b", {}).get("netta")
             and r["metriche"]["r_medio"] <= 0]
print("nette contro (a) e (b) con R medio non positivo:", nette_neg)
