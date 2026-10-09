"""Misure di processo per la consegna, ricavate dal log; piu' la distanza degli stop del candidato."""
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import registro  # noqa: E402
import varianti as V  # noqa: E402


def t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


voci = registro.leggi()
prima, ultima = t(voci[0]["data"]), t(voci[-1]["data"])
pause = sum(((t(v["pausa_a"]) - t(v["pausa_da"])).total_seconds() for v in voci if "pausa_da" in v), 0.0)
print(f"durata log: {prima} -> {ultima} = {(ultima - prima).total_seconds() / 60:.0f} minuti; pause {pause / 60:.0f} minuti")
reg = [v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"]
ris = {v["id"]: v for v in voci if v["tipo"] == "risultato"}
idee = {}
for r in reg:
    idee.setdefault(r["idea"], []).append(r)
for idea, rr in sorted(idee.items()):
    inizio = min(t(r["data"]) for r in rr)
    fine = max(t(ris[r["id"]]["data"]) for r in rr if r["id"] in ris)
    print(f"{idea}: varianti {len(rr)} (ritocchi {sum(1 for r in rr if r.get('ritocco_di'))}), minuti {(fine - inizio).total_seconds() / 60:.1f}")
scarti = [v for v in voci if v["tipo"] == "scarto"]
print("scarti:", len(scarti), "varianti testate:", len(reg), "ritocchi:", sum(1 for r in reg if r.get("ritocco_di")),
      "famiglie:", len({r["famiglia"] for r in reg}))
cand = [r["id"] for r in reg if ris.get(r["id"], {}).get("candidato")]
print("candidati Fase 2:", cand, "di cui da ritocchi:", [c for c in cand if next(r for r in reg if r["id"] == c).get("ritocco_di")])
netta_non_pos = [r["id"] for r in reg if ris.get(r["id"], {}).get("baseline_a", {}).get("netta")
                 and ris[r["id"]].get("baseline_b", {}).get("netta") and ris[r["id"]]["metriche"]["r_medio"] <= 0]
print("nette contro (a) e (b) con R non positivo:", netta_non_pos)
rifiuti = [v["id"] for v in voci if v["tipo"] == "nota" and "rifiuto del guardiano" in v.get("testo", "").lower()]
print("note sui rifiuti del guardiano:", rifiuti)

# distanza dello stop dei trade del candidato in costruzione e validazione
v = V.i03("1h", "misure", max_barre=12, solo_fine_settimana=True)
for periodo in ("costruzione", "intero"):
    d = C.carica("1h", periodo)
    r = C.motore.esegui(d["candele"], None, d["mark"], d["funding"], C.fabbrica(v, d["candele"])(), C.parametri())
    tr = [x for x in r.trades if periodo == "costruzione" or x.ts_entrata >= C.INIZIO_VALIDAZIONE_TS]
    dist = np.array([abs(x.entrata - x.stop) / x.entrata for x in tr])
    print(f"{periodo}: {len(tr)} trade, distanza stop: mediana {np.median(dist):.4f}, massimo {dist.max():.4f}, "
          f"oltre 6%: {(dist > 0.06).sum()}, leva effettiva massima {max(x.leva_effettiva for x in tr):.2f}")
