"""Misure di processo della consegna (Passo 3, «Consegna», e regole del gruppo, sezione 8, punto 2), dal solo log.

Durata dalla prima all'ultima voce, con e senza le pause (voci con pausa_da e pausa_a); per ogni idea i minuti dalla
registrazione della sua prima variante all'ultimo risultato delle sue varianti (ritocchi compresi); varianti, ritocchi,
scarti, candidati per origine; varianti nette contro (a) e (b) con R medio non positivo; minuti di calcolo per variante
(dalla registrazione al risultato).
"""

import json
import sys
from datetime import datetime
from pathlib import Path

CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODICE))

import registro  # noqa: E402


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def main():
    voci = registro.voci()
    inizio, fine = t(voci[0]["data"]), t(voci[-1]["data"])
    pause = sum((t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds() for v in voci if "pausa_da" in v)
    reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"}
    ris = {v["id"]: v for v in voci if v["tipo"] == "risultato" and v["id"] in reg}
    scarti = [v for v in voci if v["tipo"] == "scarto"]
    per_idea = {}
    for i, r in reg.items():
        idea = r["idea"]
        per_idea.setdefault(idea, {"prima": r["data"], "ultima": r["data"]})
        if i in ris:
            per_idea[idea]["ultima"] = max(per_idea[idea]["ultima"], ris[i]["data"])
    minuti_idea = {k: round((t(v["ultima"]) - t(v["prima"])).total_seconds() / 60, 1) for k, v in per_idea.items()}
    calcolo = {r.get("variante"): round((t(ris[i]["data"]) - t(r["data"])).total_seconds() / 60, 1)
               for i, r in reg.items() if i in ris}
    candidati = [i for i, v in ris.items() if v.get("candidato")]
    nette_non_positive = [i for i, v in ris.items() if v.get("baseline_a", {}).get("netta")
                          and v.get("baseline_b", {}).get("netta") and (v.get("metriche", {}).get("r_medio") or 0) <= 0]
    esito = {
        "prima_voce": voci[0]["data"], "ultima_voce": voci[-1]["data"],
        "durata_ore": round((fine - inizio).total_seconds() / 3600, 2),
        "pause_ore": round(pause / 3600, 2),
        "durata_senza_pause_ore": round(((fine - inizio).total_seconds() - pause) / 3600, 2),
        "varianti_esaminate": len(ris),
        "di_cui_ritocchi": sum(1 for i in ris if reg[i].get("ritocco_di")),
        "scarti": len(scarti), "scarti_ritocchi": sum(1 for v in scarti if v.get("ritocco_di")),
        "famiglie_ritoccate": sorted({reg[i]["famiglia"] for i in ris if reg[i].get("ritocco_di")}),
        "candidati": candidati,
        "candidati_da_idee_nuove": [i for i in candidati if not reg[i].get("ritocco_di")],
        "candidati_da_ritocchi": [i for i in candidati if reg[i].get("ritocco_di")],
        "nette_contro_a_e_b_con_r_non_positivo": nette_non_positive,
        "minuti_per_idea": minuti_idea,
        "minuti_di_calcolo_per_variante": calcolo,
    }
    (CODICE.parent / "lavoro" / "misure.json").write_text(json.dumps(esito, indent=1, ensure_ascii=False) + "\n",
                                                          encoding="utf-8")
    print(json.dumps(esito, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
