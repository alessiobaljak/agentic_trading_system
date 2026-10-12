"""Misure di processo per la consegna, ricavate dal log e da ipotesi.md."""
import json
import re
from datetime import datetime

from comune import CARTELLA, LOG

voci = [json.loads(r) for r in open(LOG, encoding="utf-8") if r.strip()]


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


reg = [v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"]
scarti = [v for v in voci if v["tipo"] == "scarto"]
ris = {v["id"]: v for v in voci if v["tipo"] == "risultato"}
ritocchi = [v for v in reg if v.get("ritocco_di")]
famiglie = sorted({v["famiglia"] for v in reg})
pause = [v for v in voci if v["tipo"] == "nota" and "pausa_da" in v]
durata = (t(voci[-1]["data"]) - t(voci[0]["data"])).total_seconds() / 60
durata_pause = sum((t(p["pausa_a"]) - t(p["pausa_da"])).total_seconds() / 60 for p in pause)
print(f"voci nel log: {len(voci)}; prima {voci[0]['data']}, ultima {voci[-1]['data']}")
print(f"durata: {durata:.0f} minuti con le pause, {durata - durata_pause:.0f} senza (pause: {len(pause)})")
print(f"varianti testate: {len(reg)} (variante_n massimo {max(v['variante_n'] for v in reg)}); ritocchi: {len(ritocchi)}; "
      f"famiglie: {len(famiglie)}; scarti: {len(scarti)}")
cand = [i for i, r in ris.items() if r.get("candidato")]
netta_ab_r_neg = [i for i, r in ris.items() if r.get("baseline_a", {}).get("netta") and r.get("baseline_b", {}).get("netta")
                  and r["metriche"]["r_medio"] <= 0]
solo_b = [i for i, r in ris.items() if r.get("baseline_b", {}).get("netta")]
print(f"candidati: {cand}; nette contro (a) e (b) con R non positivo: {netta_ab_r_neg}; nette solo contro la (b): {solo_b}")
print("previsioni corrette:", sum(1 for r in ris.values() if r.get("previsione_corretta")), "su", len(ris))
testo = (CARTELLA / "ipotesi.md").read_text(encoding="utf-8")
blocchi = re.split(r"\n## (I-\d\d) ", testo)
spiegazioni = {}
for k in range(1, len(blocchi), 2):
    spiegazioni[blocchi[k]] = 8 + len(set(re.findall(r"\* C(\d+) \*\*", blocchi[k + 1])))
per_idea = {}
for v in reg + scarti:
    per_idea.setdefault(v["idea"], []).append(v)
for idea in sorted(per_idea):
    vs = per_idea[idea]
    inizio = min(t(v["data"]) for v in vs)
    fine = max([t(ris[v["id"]]["data"]) for v in vs if v["id"] in ris] + [t(v["data"]) for v in vs])
    n_test = sum(1 for v in vs if v["tipo"] == "registrazione")
    print(f"{idea}: varianti testate {n_test}, scarti {len(vs) - n_test}, minuti dalla prima registrazione "
          f"all'ultimo risultato {(fine - inizio).total_seconds() / 60:.0f}, spiegazioni concorrenti {spiegazioni.get(idea)}")
