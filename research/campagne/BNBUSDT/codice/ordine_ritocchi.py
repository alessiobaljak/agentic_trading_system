"""Ordine dei ritocchi (regola 6): varianti testate, valutabili, non candidate, famiglia sotto 5 ritocchi,
ordinate per t contro la (b) dal piu' alto (a parita' vale la registrata prima)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro  # noqa: E402

voci = registro.leggi()
reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in voci if v["tipo"] == "risultato" and v["id"] in reg}
ritocchi = {}
for r in reg.values():
    ritocchi[r["famiglia"]] = ritocchi.get(r["famiglia"], 0) + (1 if r.get("ritocco_di") else 0)
for v in voci:  # i ritocchi scartati contano fra i ritocchi della famiglia
    if v["tipo"] == "scarto" and v.get("ritocco_di"):
        ritocchi[v["famiglia"]] = ritocchi.get(v["famiglia"], 0) + 1
lista = []
for vid, r in reg.items():
    x = ris.get(vid)
    if x is None:
        print("SENZA RISULTATO", vid)
        continue
    t = x["baseline_b"].get("t")
    t = float("-inf") if t in (None, "-inf") else float(t)
    stato = "candidato" if x.get("candidato") else ("non valutabile" if not x.get("valutabile") else "")
    lista.append((t, r["variante_n"], vid, r.get("etichetta"), r["famiglia"], ritocchi.get(r["famiglia"], 0), stato,
                  x["metriche"]["r_medio"], x["baseline_a"].get("netta"), x["baseline_b"].get("netta")))
lista.sort(key=lambda z: (-z[0], z[1]))
print("varianti testate:", len(reg), "ritocchi:", sum(1 for r in reg.values() if r.get("ritocco_di")))
for z in lista:
    ammessa = (z[6] == "" and z[5] < 5)
    print(f"t_b={z[0]:+.3f} n={z[1]:>2} {z[2]} {z[3]:<10} famiglia={z[4]} ritocchi={z[5]} {z[6] or '-'} "
          f"R={z[7]:+.3f} netta_a={z[8]} netta_b={z[9]} {'IN LISTA' if ammessa else 'fuori'}")
