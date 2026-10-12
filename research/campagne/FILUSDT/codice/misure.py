"""Misure di processo per la consegna (Consegna del Passo 3), ricavate dal log e da ipotesi.md.

Uso: python misure.py   -> stampa le misure in JSON e le scrive in data/insample/FILUSDT/misure.json
"""
from __future__ import annotations

import json
import re
from datetime import datetime

import comune
import registro


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def main():
    voci = registro.voci()
    prima, ultima = t(voci[0]["data"]), t(voci[-1]["data"])
    pause = 0.0
    for v in voci:
        if v.get("pausa_da") and v.get("pausa_a"):
            pause += (t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds()
    reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione"}
    ris = {v["id"]: v for v in voci if v["tipo"] == "risultato"}
    varianti = [v for v in reg.values() if v.get("tipo_test") == "variante"]
    per_idea = {}
    for v in varianti:
        per_idea.setdefault(v["idea"], []).append(v["id"])
    minuti_idea = {}
    for idea, ids in sorted(per_idea.items()):
        inizio = min(t(reg[i]["data"]) for i in ids)
        fine = max(t(ris[i]["data"]) for i in ids if i in ris)
        minuti_idea[idea] = round((fine - inizio).total_seconds() / 60, 1)
    # spiegazioni concorrenti per idea: righe numerate dentro il punto 4 di ogni idea
    testo = (comune.CARTELLA_CAMPAGNA / "ipotesi.md").read_text()
    spiegazioni = {}
    for blocco in re.split(r"\n## ", testo)[1:]:
        m = re.match(r"(I-\d+)", blocco)
        if not m:
            continue
        parte = blocco.split("4. **Spiegazioni concorrenti", 1)
        if len(parte) < 2:
            continue
        p4 = parte[1].split("\n5. ", 1)[0]
        spiegazioni[m.group(1)] = len(re.findall(r"\n   \d+\. ", p4))
    candidati_fase2 = [v["id"] for v in ris.values() if v.get("candidato") and v["id"] in reg
                       and reg[v["id"]].get("tipo_test") == "variante"]
    da_ritocco = [i for i in candidati_fase2 if reg[i].get("ritocco_di")]
    netti_r_non_positivo = [v["id"] for v in ris.values() if v["id"] in reg and reg[v["id"]].get("tipo_test") == "variante"
                            and (v.get("baseline_a") or {}).get("netta") and (v.get("baseline_b") or {}).get("netta")
                            and (v.get("metriche") or {}).get("r_medio", 1) <= 0]
    out = {
        "prima_voce": voci[0]["data"], "ultima_voce": voci[-1]["data"],
        "durata_minuti_con_pause": round((ultima - prima).total_seconds() / 60, 1),
        "durata_minuti_senza_pause": round(((ultima - prima).total_seconds() - pause) / 60, 1),
        "varianti_testate": len(varianti),
        "ritocchi": sum(1 for v in varianti if v.get("ritocco_di")),
        "famiglie": len({v["famiglia"] for v in varianti}),
        "scarti": sum(1 for v in voci if v["tipo"] == "scarto"),
        "minuti_per_idea": minuti_idea,
        "spiegazioni_concorrenti_per_idea": spiegazioni,
        "candidati_fase2_idee_nuove": [i for i in candidati_fase2 if i not in da_ritocco],
        "candidati_fase2_ritocchi": da_ritocco,
        "netti_con_r_non_positivo": netti_r_non_positivo,
    }
    (comune.CARTELLA_DATI / "misure.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
