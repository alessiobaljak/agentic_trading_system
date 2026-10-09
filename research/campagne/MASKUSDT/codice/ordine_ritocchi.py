"""Ordine dei ritocchi (regola 6): varianti testate, valutabili contro (a) e (b), non candidati,
famiglia sotto il massimo di ritocchi; ordinate per t contro la (b) dal piu' alto; a parita' la
registrata prima. Stampa la lista (solo id, famiglia, t contro la (b) e numero di ritocchi della famiglia)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registro  # noqa: E402

voci = registro.voci()
reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in voci if v["tipo"] == "risultato"}
ritocchi = {}
for v in voci:
    if v["tipo"] in ("registrazione", "scarto") and v.get("ritocco_di"):
        ritocchi[v["famiglia"]] = ritocchi.get(v["famiglia"], 0) + 1
lista = []
for ordine, (vid, r) in enumerate(reg.items()):
    if vid not in ris:
        continue
    e = ris[vid]
    a, b = e.get("baseline_a") or {}, e.get("baseline_b") or {}
    if not (a.get("valutabile") and b.get("valutabile")):
        continue
    if e.get("candidato"):
        continue
    if ritocchi.get(r["famiglia"], 0) >= 5:
        continue
    lista.append((-float(b["t"]), ordine, vid, r["famiglia"], float(b["t"]), ritocchi.get(r["famiglia"], 0)))
for _, _, vid, fam, t, k in sorted(lista)[:10]:
    print(vid, fam, round(t, 3), "ritocchi gia' fatti:", k)
print("testate:", len(reg), "budget restante:", 30 - len(reg))
