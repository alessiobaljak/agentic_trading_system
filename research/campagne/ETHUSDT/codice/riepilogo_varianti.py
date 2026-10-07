"""Riepilogo delle varianti dal log (solo lettura): tabella in markdown per la consegna e json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
from log import leggi  # noqa: E402

voci = leggi()
reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in voci if v.get("tipo") == "risultato" and v["id"] in reg}
scarti = [v for v in voci if v.get("tipo") == "scarto"]

righe = ["| Id | Idea | Timeframe | Dir. | Trade | Profit factor | R medio | Win rate | Percentile fra 200 casuali | Differenza vs casuale (err. std.) | Netta | R medio per anno |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
tab = []
for id_v in sorted(reg):
    r, g = reg[id_v], ris.get(id_v)
    if g is None:
        continue
    m, c = g["metriche"], g["confronto_baseline"]
    b, nb = c.get("baseline_b_casuale", {}), c.get("netto_vs_b") or {}
    per_anno = ", ".join(f"{a}: {v['r_medio']:+.3f} ({v['n']})" for a, v in m.get("r_per_anno", {}).items())
    righe.append(f"| {id_v.split('-')[1]} | {r['idea']} {r['nome_idea']} | {r['timeframe']} | {r['direzione']} | {m['n_trade']} | {m['profit_factor']} | {m['r_medio']:+.3f} | {m['win_rate']:.2f} | {b.get('percentile_del_candidato')} | {nb.get('differenza')} ({nb.get('errore_standard')}) | {'si' if nb.get('netta') and nb.get('segno', 0) > 0 else 'no'} | {per_anno} |")
    tab.append({"id": id_v, "idea": r["idea"], "nome": r["nome_idea"], "timeframe": r["timeframe"], "direzione": r["direzione"],
                "variante_n": r["variante_n"], "n_trade": m["n_trade"], "profit_factor": m["profit_factor"], "r_medio": m["r_medio"],
                "win_rate": m["win_rate"], "rendimento_totale": m["rendimento_totale"], "drawdown_max": m["drawdown_max"],
                "percentile_caso": b.get("percentile_del_candidato"), "differenza_vs_caso": nb.get("differenza"), "errore_standard": nb.get("errore_standard"),
                "netta": bool(nb.get("netta")) and nb.get("segno", 0) > 0, "r_per_anno": m.get("r_per_anno"), "esiti": m.get("esiti"),
                "n_stop_oltre_6pct": m.get("n_stop_oltre_6pct"), "n_ridotti": m.get("n_ridotti"), "n_violazioni_liquidazione": m.get("n_violazioni_liquidazione"),
                "funding_totale": m.get("funding_totale"), "costi_totali": m.get("costi_totali"), "pnl_lordo_prezzo": m.get("pnl_lordo_prezzo"), "pnl_netto": m.get("pnl_netto"),
                "previsione": r["previsione"], "esito_fase2": g["esito_fase2"], "trade_stimati": r["trade_stimati"]})

righe_s = ["| Idea | Dir. | Timeframe | Trade stimati | Motivo |", "|---|---|---|---|---|"]
for v in scarti:
    righe_s.append(f"| {v['idea']} {v['nome_idea']} | {v['direzione']} | {v['timeframe']} | {v['stima']['trade_stimati']} | {v['motivo'].split(':')[0]} |")

testo = "\n".join(righe) + "\n\n### Varianti scartate prima del test (stima dei trade sotto 100, nessun budget)\n\n" + "\n".join(righe_s) + "\n"
(QUI.parent / "risultati" / "riepilogo_varianti.md").write_text(testo, encoding="utf-8")
(QUI.parent / "risultati" / "riepilogo_varianti.json").write_text(json.dumps(tab, indent=1, ensure_ascii=False), encoding="utf-8")
print("varianti:", len(tab), "scarti:", len(scarti), "budget usato:", max(t["variante_n"] for t in tab))
print("profit factor sopra 1:", [(t["id"], t["profit_factor"]) for t in tab if isinstance(t["profit_factor"], (int, float)) and t["profit_factor"] > 1])
print("percentile >= 90:", [(t["id"], t["percentile_caso"], t["differenza_vs_caso"], t["errore_standard"]) for t in tab if (t["percentile_caso"] or 0) >= 90])
for t in tab:
    if (t["percentile_caso"] or 0) >= 90 or (isinstance(t["profit_factor"], float) and t["profit_factor"] > 1):
        print(t["id"], t["idea"], t["direzione"], "r_per_anno", t["r_per_anno"], "esiti", t["esiti"], "stop>6%", t["n_stop_oltre_6pct"], "costi", t["costi_totali"], "lordo", t["pnl_lordo_prezzo"], "netto", t["pnl_netto"])
