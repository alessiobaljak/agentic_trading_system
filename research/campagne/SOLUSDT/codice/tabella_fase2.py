"""Tabella in Markdown dei risultati di Fase 2 letti dal log (per consegna.md e lezioni_moneta.md)."""
import json

righe = []
reg = {}
corr = {}
voci = [json.loads(l) for l in open("research/campagne/SOLUSDT/log.jsonl", encoding="utf-8")]
for d in voci:  # prima le correzioni: possono stare dopo il risultato che correggono
    if d.get("tipo") == "correzione":
        corr.update(d.get("valori_corretti", {}))
for d in voci:
    if d.get("tipo") == "registrazione" and d.get("tipo_test") == "variante":
        reg[d["id"]] = d
    if d.get("tipo") == "risultato" and "metriche" in d and d["id"] in reg:
        r = reg[d["id"]]; m = d["metriche"]; b = d.get("baseline_b_entrate_casuali", {}); a = d.get("baseline_a_barre_qualsiasi", {})
        btc = corr.get(d["id"], d.get("solo_btc", {}))
        anni = " / ".join(f"{k}: {v[1]:+.2f} ({v[0]})" for k, v in m["r_medio_per_anno"].items() if v[0] >= 10)
        nb = b.get("nettamente_vs_mediana", {})
        righe.append((r["variante_n"], d["variante"], r["idea"], r["timeframe"], r["direzione"], m["trade"], m["profit_factor"], m["r_medio"], m["r_mediano"], m["win_rate"],
                      anni, b.get("percentile_candidato"), nb.get("differenza"), nb.get("margine"), b.get("p_value_vs_mediana"), btc.get("r_residuo_medio"), d.get("senza_3_migliori", {}).get("r_medio")))
righe.sort()
print("| n | Variante | Idea | TF | Dir. | Trade | PF | R medio | R mediano | Win | R medio per anno (trade) | Percentile vs caso | Diff. vs caso ± margine | p | R residuo BTC | R senza 3 migliori |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for x in righe:
    print(f"| {x[0]} | {x[1]} | {x[2]} | {x[3]} | {x[4]} | {x[5]} | {x[6]} | {x[7]:+.3f} | {x[8]:+.3f} | {x[9]:.2f} | {x[10]} | {x[11]} | {x[12]:+.3f} ± {x[13]:.3f} | {x[14]} | {x[15]:+.3f} | {x[16]:+.3f} |")
