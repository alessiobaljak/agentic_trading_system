"""Riepilogo e controllo del log (sola lettura): varianti, scarti, famiglie, ordine dei ritocchi, misure di processo.

Uso: python riepilogo.py   (scrive uscite/riepilogo.json e stampa la tabella)
"""
import json
from datetime import datetime

import comune as C
import registro

voci = registro.voci()
reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in voci if v.get("tipo") == "risultato" and v["id"] in reg}
scarti = [v for v in voci if v.get("tipo") == "scarto"]

righe = []
problemi = []
attesa_n = 1
for v in voci:
    if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante":
        if v["variante_n"] != attesa_n:
            problemi.append(f"variante_n {v['variante_n']} invece di {attesa_n} per {v['id']}")
        attesa_n += 1
for vid, r in reg.items():
    x = ris.get(vid)
    if x is None:
        problemi.append(f"{vid}: registrazione senza risultato")
        continue
    if voci.index(x) < voci.index(r):
        problemi.append(f"{vid}: risultato prima della registrazione")
    a, b, m = x.get("baseline_a", {}), x.get("baseline_b", {}), x["metriche"]
    righe.append({
        "id": vid, "n": r["variante_n"], "nome": r["nome_in_ipotesi"], "idea": r["idea"], "famiglia": r["famiglia"],
        "ritocco_di": r.get("ritocco_di"), "tf": r["timeframe"], "dir": r["direzione"], "trade": m["trade"],
        "stimati": r["trade_stimati"], "r_medio": m["r_medio"], "pf": m["profit_factor"],
        "t_a": a.get("t"), "netta_a": a.get("netta"), "t_b": b.get("t"), "netta_b": b.get("netta"),
        "media_b": b.get("media"), "percentile": x.get("percentile_caso"), "valutabile": x.get("valutabile"),
        "candidato": x.get("candidato"), "blocco": x.get("blocco"), "n_blocchi_b": b.get("n_blocchi"),
        "senza3": m.get("r_medio_senza_3_migliori"), "per_anno": m.get("r_medio_per_anno"),
        "data_reg": r["data"], "data_ris": x["data"],
    })
    if m["trade"] != r["trade_stimati"]:
        problemi.append(f"{vid}: trade del test {m['trade']} diversi dalla stima {r['trade_stimati']}")

# ordine dei ritocchi: prima di ogni ritocco, la lista con i t contro la (b) dei risultati gia' scritti
ordine = []
for v in voci:
    if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante" and v.get("ritocco_di"):
        prima = [r for r in righe if r["data_ris"] <= v["data"] and r["id"] != v["id"]
                 and voci.index(ris[r["id"]]) < voci.index(v)]
        ritocchi_fam = {}
        for r in prima:
            if r["ritocco_di"]:
                ritocchi_fam[r["famiglia"]] = ritocchi_fam.get(r["famiglia"], 0) + 1
        lista = [r for r in prima if r["valutabile"] and not r["candidato"]
                 and ritocchi_fam.get(r["famiglia"], 0) < 5]
        lista.sort(key=lambda r: (-r["t_b"], r["n"]))
        attesa = lista[0]["id"] if lista else None
        ordine.append({"ritocco": v["id"], "ritocco_di": v["ritocco_di"], "primo_della_lista": attesa,
                       "lista": [(r["id"], round(r["t_b"], 3)) for r in lista[:5]]})
        if attesa != v["ritocco_di"]:
            problemi.append(f"{v['id']}: ritocco di {v['ritocco_di']} ma il primo della lista era {attesa}")
        if ritocchi_fam.get(v["famiglia"], 0) >= 5:
            problemi.append(f"{v['id']}: la famiglia {v['famiglia']} aveva gia' 5 ritocchi")

famiglie = sorted({r["famiglia"] for r in righe})
uscita = {
    "varianti_testate": len(righe),
    "ritocchi": sum(1 for r in righe if r["ritocco_di"]),
    "idee_nuove": sum(1 for r in righe if not r["ritocco_di"]),
    "famiglie": len(famiglie),
    "scarti": len(scarti),
    "candidati": [r["id"] for r in righe if r["candidato"]],
    "netti_a_e_b_con_r_non_positivo": [r["id"] for r in righe if r["netta_a"] and r["netta_b"] and r["r_medio"] <= 0],
    "ordine_ritocchi": ordine,
    "problemi": problemi,
    "righe": righe,
    "prima_voce": voci[0]["data"], "ultima_voce": voci[-1]["data"],
}
C.USCITE.mkdir(parents=True, exist_ok=True)
with open(C.USCITE / "riepilogo.json", "w", encoding="utf-8") as f:
    json.dump(uscita, f, ensure_ascii=False, indent=1, default=str)
for r in sorted(righe, key=lambda r: r["n"]):
    C.stampa(f"{r['n']:>2} {r['id']} {r['nome'][:28]:<28} {r['tf']:>3} {r['dir']:<5} tr={r['trade']:>4} "
             f"R={r['r_medio']:+.4f} t_a={r['t_a']:+.2f} t_b={r['t_b']:+.2f} cand={r['candidato']}")
C.stampa("varianti", uscita["varianti_testate"], "idee nuove", uscita["idee_nuove"], "ritocchi", uscita["ritocchi"],
         "famiglie", uscita["famiglie"], "scarti", uscita["scarti"])
C.stampa("candidati", uscita["candidati"], "netti con R non positivo", uscita["netti_a_e_b_con_r_non_positivo"])
for o in ordine:
    C.stampa("ordine:", o)
C.stampa("PROBLEMI:", problemi if problemi else "nessuno")
