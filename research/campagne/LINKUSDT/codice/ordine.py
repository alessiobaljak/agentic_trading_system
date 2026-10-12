"""L'ordine dei ritocchi della regola 6, calcolato dal log.

Entrano le varianti testate valutabili contro la (a) e la (b), che non sono candidati, e la cui
famiglia ha meno di 5 ritocchi. Ordine: t contro la (b) dal piu' alto; a parita' vale la registrata prima.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro as R  # noqa: E402


def ordine():
    voci = R.voci()
    reg = {}
    for k, v in enumerate(voci):
        if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante":
            reg[v["id"]] = (k, v)
    ritocchi_per_famiglia = {}
    for k, v in reg.values():
        if v.get("ritocco_di"):
            ritocchi_per_famiglia[v["famiglia"]] = ritocchi_per_famiglia.get(v["famiglia"], 0) + 1
    for v in voci:  # anche i ritocchi scartati contano fra i ritocchi della famiglia
        if v["tipo"] == "scarto" and v.get("ritocco_di"):
            ritocchi_per_famiglia[v["famiglia"]] = ritocchi_per_famiglia.get(v["famiglia"], 0) + 1
    lista = []
    for v in voci:
        if v["tipo"] != "risultato" or v["id"] not in reg:
            continue
        k, r = reg[v["id"]]
        a, b = v["baseline_a"], v["baseline_b"]
        if not (a.get("valutabile") and b.get("valutabile")) or v.get("candidato"):
            continue
        if ritocchi_per_famiglia.get(r["famiglia"], 0) >= 5:
            continue
        lista.append((-float(b["t"]), k, v["id"], float(b["t"]), r["famiglia"]))
    lista.sort()
    return [(vid, t, fam) for _, _, vid, t, fam in lista]


if __name__ == "__main__":
    for vid, t, fam in ordine():
        print(f"{vid:18s} t_b={t:+.3f} famiglia={fam}")
