"""Misure di processo della consegna, ricavate dal log (sezione «Consegna» del protocollo).

Uso: python -m research.campagne.BCHUSDT.codice.misure
"""
import json
from datetime import datetime

from research.campagne.BCHUSDT.codice import registra


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def main():
    voci = [json.loads(r) for r in registra.LOG.read_text(encoding="utf-8").splitlines() if r.strip()]
    prima, ultima = t(voci[0]["data"]), t(voci[-1]["data"])
    pause = sum((t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds() for v in voci if v.get("pausa_da"))
    durata = (ultima - prima).total_seconds()
    print("voci", len(voci), "prima", voci[0]["data"], "ultima", voci[-1]["data"],
          "minuti", round(durata / 60, 1), "senza pause", round((durata - pause) / 60, 1))
    reg = [v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"]
    scarti = [v for v in voci if v["tipo"] == "scarto"]
    ris = {v["id"]: v for v in voci if v["tipo"] == "risultato"}
    rit = [v for v in reg if v.get("ritocco_di")]
    print("varianti", len(reg), "ritocchi", len(rit), "famiglie", len({v["famiglia"] for v in reg}),
          "scarti", len(scarti), "ritocchi scartati", sum(1 for v in scarti if v.get("ritocco_di")))
    per_idea = {}
    for v in reg:
        per_idea.setdefault(v["idea"], []).append(v)
    for idea, vs in sorted(per_idea.items()):
        inizio = min(t(v["data"]) for v in vs)
        fine = max(t(ris[v["id"]]["data"]) for v in vs if v["id"] in ris)
        print(idea, "varianti", len(vs), "minuti", round((fine - inizio).total_seconds() / 60, 1))
    cand_n = sum(1 for v in reg if ris.get(v["id"], {}).get("candidato") and not v.get("ritocco_di"))
    cand_r = sum(1 for v in reg if ris.get(v["id"], {}).get("candidato") and v.get("ritocco_di"))
    nette_neg = sum(1 for v in reg if ris.get(v["id"]) and ris[v["id"]].get("baseline_a", {}).get("netta")
                    and ris[v["id"]].get("baseline_b", {}).get("netta") and ris[v["id"]]["metriche"]["r_medio"] <= 0)
    print("candidati da idee nuove", cand_n, "da ritocchi", cand_r, "nette (a) e (b) con R <= 0", nette_neg)


if __name__ == "__main__":
    main()
