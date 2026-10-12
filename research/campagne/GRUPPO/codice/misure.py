"""Misure di processo della consegna (protocollo, Consegna; regole.md, sezione 8, punto 2), dal log e da ipotesi.md.

Uso: python3 -u misure.py   (stampa un JSON). Solo conteggi e tempi: nessun calcolo d'esame.
"""
import json
import re
from datetime import datetime

from comune import CARTELLA_GRUPPO


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    voci = [json.loads(x) for x in (CARTELLA_GRUPPO / "log.jsonl").read_text().splitlines() if x.strip()]
    date = [t(v["data"]) for v in voci]
    durata = (max(date) - min(date)).total_seconds() / 60
    pause = [(t(v["pausa_da"]), t(v["pausa_a"])) for v in voci if "pausa_da" in v and "pausa_a" in v]
    minuti_pause = sum((b - a).total_seconds() / 60 for a, b in pause)
    reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione"}
    ris = {v["id"]: v for v in voci if v["tipo"] == "risultato"}
    scarti = [v for v in voci if v["tipo"] == "scarto"]
    per_idea = {}
    for i, v in reg.items():
        d = per_idea.setdefault(v["idea"], {"inizio": t(v["data"]), "fine": None, "varianti": 0, "ritocchi": 0})
        d["inizio"] = min(d["inizio"], t(v["data"]))
        d["varianti"] += 1
        d["ritocchi"] += 1 if v.get("ritocco_di") else 0
        if i in ris:
            f = t(ris[i]["data"])
            d["fine"] = f if d["fine"] is None or f > d["fine"] else d["fine"]
    testo = (CARTELLA_GRUPPO / "ipotesi.md").read_text()
    spiegazioni = {}
    for blocco in re.split(r"\n## ", testo)[1:]:
        m = re.match(r"(I-\d+)", blocco)
        if m:
            parte = blocco.split("**4-5.")[1].split("**6.")[0] if "**4-5." in blocco else ""
            spiegazioni[m.group(1)] = len(re.findall(r"^\d+\. ", parte, re.M))
    calcolo = {}
    for f in sorted((CARTELLA_GRUPPO / "lavoro").glob("lotto_*.out")):
        ultimo = None
        for riga in f.read_text().splitlines():
            m = re.match(r"(GRUPPO-\d+) ", riga)
            if m:
                ultimo = m.group(1)
            m = re.search(r"esame fatto in (\d+) s", riga)
            if m and ultimo:
                calcolo[ultimo] = round(int(m.group(1)) / 60, 1)
    for ident, nome in (("GRUPPO-012", "esame_012.out"), ("GRUPPO-014", "esame_014.out")):
        m = re.search(r"secondi: (\d+)", (CARTELLA_GRUPPO / "lavoro" / nome).read_text())
        if m:
            calcolo[ident] = round(int(m.group(1)) / 60, 1)
    candidati = [i for i, v in ris.items() if v.get("candidato")]
    nette_r_non_pos = [i for i, v in ris.items() if (v.get("baseline_a") or {}).get("netta")
                       and (v.get("baseline_b") or {}).get("netta") and v["metriche"]["r_medio"] <= 0]
    print(json.dumps({
        "prima_voce": str(min(date)), "ultima_voce": str(max(date)),
        "durata_minuti": round(durata), "pause_minuti": round(minuti_pause), "durata_senza_pause_minuti": round(durata - minuti_pause),
        "varianti_testate": len(reg), "ritocchi": sum(1 for v in reg.values() if v.get("ritocco_di")),
        "famiglie": len({v["famiglia"] for v in reg.values()}), "scarti": len(scarti),
        "per_idea": {k: {"minuti": round((v["fine"] - v["inizio"]).total_seconds() / 60) if v["fine"] else None,
                          "varianti": v["varianti"], "ritocchi": v["ritocchi"], "spiegazioni_concorrenti": spiegazioni.get(k)}
                     for k, v in sorted(per_idea.items())},
        "spiegazioni_idee_scartate": {k: n for k, n in spiegazioni.items() if k not in per_idea},
        "candidati_fase2": candidati, "nette_con_r_non_positivo": nette_r_non_pos,
        "minuti_di_calcolo_per_variante": calcolo,
    }, ensure_ascii=False, indent=1))
