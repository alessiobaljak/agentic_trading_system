"""Misure di processo della consegna (Consegna, protocollo 4.5), dal log e da ipotesi.md. Sola lettura.

Uso: python misure.py   (scrive uscite/misure.json e stampa)
"""
import json
import re
from datetime import datetime

import comune as C
import registro


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


voci = registro.voci()
date = [t(v["data"]) for v in voci if "data" in v]
prima, ultima = min(date), max(date)
pause = [(t(v["pausa_da"]), t(v["pausa_a"])) for v in voci if "pausa_da" in v and "pausa_a" in v]
min_pause = sum((b - a).total_seconds() for a, b in pause) / 60

per_idea = {}
for v in voci:
    idea = v.get("idea")
    if not idea:
        continue
    if v["tipo"] in ("registrazione", "scarto"):
        per_idea.setdefault(idea, {"ids": set(), "inizio": None, "fine": None, "varianti": 0, "scarti": 0})
        d = per_idea[idea]
        d["ids"].add(v["id"])
        d["inizio"] = min(d["inizio"], t(v["data"])) if d["inizio"] else t(v["data"])
        d["fine"] = max(d["fine"], t(v["data"])) if d["fine"] else t(v["data"])
        if v["tipo"] == "scarto":
            d["scarti"] += 1
        else:
            d["varianti"] += 1
for v in voci:
    if v["tipo"] == "risultato":
        for d in per_idea.values():
            if v["id"] in d["ids"]:
                d["fine"] = max(d["fine"], t(v["data"]))

testo = (C.CARTELLA / "ipotesi.md").read_text(encoding="utf-8")
spiegazioni = {}
for blocco in re.split(r"\n## ", testo)[1:]:
    m = re.match(r"(I-\d+)", blocco)
    if not m:
        continue
    tab = blocco.split("**Spiegazioni concorrenti.**")[1].split("**Ipotesi.**")[0] if "**Spiegazioni concorrenti.**" in blocco else ""
    spiegazioni[m.group(1)] = len(re.findall(r"^\| \d+ \|", tab, flags=re.M))

with open(C.USCITE / "riepilogo.json", encoding="utf-8") as f:
    riep = json.load(f)
righe = riep["righe"]
out = {
    "prima_voce": prima.isoformat() + "Z", "ultima_voce": ultima.isoformat() + "Z",
    "durata_minuti_con_pause": round((ultima - prima).total_seconds() / 60, 1),
    "pause_minuti": round(min_pause, 1),
    "durata_minuti_senza_pause": round((ultima - prima).total_seconds() / 60 - min_pause, 1),
    "per_idea": {k: {"minuti": round((d["fine"] - d["inizio"]).total_seconds() / 60, 1), "varianti_testate": d["varianti"],
                     "scarti": d["scarti"], "spiegazioni_concorrenti": spiegazioni.get(k)}
                 for k, d in sorted(per_idea.items())},
    "candidati_fase2_da_idee_nuove": [r["id"] for r in righe if r["candidato"] and not r["ritocco_di"]],
    "candidati_fase2_da_ritocchi": [r["id"] for r in righe if r["candidato"] and r["ritocco_di"]],
    "netti_a_e_b_con_r_non_positivo": riep["netti_a_e_b_con_r_non_positivo"],
    "varianti": riep["varianti_testate"], "ritocchi": riep["ritocchi"], "famiglie": riep["famiglie"], "scarti": riep["scarti"],
}
with open(C.USCITE / "misure.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
C.stampa(json.dumps(out, ensure_ascii=False, indent=1))
