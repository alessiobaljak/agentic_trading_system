"""Tabella dei risultati dal log: una riga per variante testata, e l'ordine dei ritocchi (regola 6)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registro  # noqa: E402

voci = registro.voci()
reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione"}
ris = {v["id"]: v for v in voci if v.get("tipo") == "risultato" and v["id"] in reg and reg[v["id"]].get("tipo_test") == "variante"}


def f(x, n=3):
    try:
        return f"{float(x):.{n}f}"
    except (TypeError, ValueError):
        return str(x)


print("id | tf | dir | trade | R | R-3 | PF | t_a | netta_a | t_b | netta_b | media_b | perc | candidato | R per anno")
for i, r in ris.items():
    m = r["metriche"]
    a, b = r.get("baseline_a", {}), r.get("baseline_b", {})
    print(" | ".join([i, reg[i]["timeframe"], reg[i]["direzione"], str(m["trade"]), f(m["r_medio"]), f(m["r_medio_senza_3_migliori"]),
                      f(m["profit_factor"], 2), f(a.get("t"), 2), str(a.get("netta")), f(b.get("t"), 2), str(b.get("netta")),
                      f(b.get("media")), f(r.get("percentile_caso"), 1), str(r.get("candidato")),
                      str({k: round(v, 3) for k, v in m["r_medio_per_anno"].items()})]))

# ordine dei ritocchi: valutabili, non candidati, famiglia sotto il massimo di ritocchi
ritocchi = {}
for i, v in reg.items():
    if v.get("ritocco_di"):
        ritocchi[v["famiglia"]] = ritocchi.get(v["famiglia"], 0) + 1
for v in voci:
    if v.get("tipo") == "scarto" and v.get("ritocco_di"):
        ritocchi[v["famiglia"]] = ritocchi.get(v["famiglia"], 0) + 1
lista = []
for i, r in ris.items():
    if not r.get("valutabile") or r.get("candidato"):
        continue
    fam = reg[i]["famiglia"]
    if ritocchi.get(fam, 0) >= 5:
        continue
    lista.append((-float(r["baseline_b"]["t"]), reg[i]["data"], i, fam))
lista.sort()
print("\nordine dei ritocchi (t contro la (b), dal piu' alto):")
for t, _, i, fam in lista:
    print(i, "famiglia", fam, "t_b", round(-t, 3), "ritocchi gia' fatti", ritocchi.get(fam, 0))
print("\nvarianti testate:", len(ris), "registrazioni variante:", sum(1 for v in reg.values() if v.get("tipo_test") == "variante"))
