"""Ordine dei ritocchi (regola 6): varianti valutabili, non candidate, famiglia sotto 5 ritocchi, per t contro la (b)."""
from collections import Counter

from research.campagne.XRPUSDT.codice import quadro as q

log = q.leggi_log()
reg = {v["id"]: v for v in log if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in log if v.get("tipo") == "risultato" and v["id"] in reg}
ritocchi = Counter(r["famiglia"] for r in reg.values() if r.get("ritocco_di"))
ritocchi.update(v["famiglia"] for v in log if v.get("tipo") == "scarto" and v.get("ritocco_di"))
lista = []
for vid, r in ris.items():
    fam = reg[vid]["famiglia"]
    if not r.get("valutabile") or r.get("candidato") or ritocchi[fam] >= 5:
        continue
    lista.append((-float(r["t_contro_b"]), reg[vid]["variante_n"], vid, fam))
lista.sort()
print("varianti usate:", len(reg), "ritocchi per famiglia:", dict(ritocchi))
for t, n, vid, fam in lista[:10]:
    print(f"{vid} t={-t:.2f} n={n} famiglia={fam}")
print("non valutabili:", [v for v, r in ris.items() if not r.get("valutabile")])
print("candidati:", [v for v, r in ris.items() if r.get("candidato")])
