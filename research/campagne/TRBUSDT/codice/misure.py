"""Misure di processo e riepilogo per la consegna, ricavati SOLO dal log (nessun nuovo test).

Scrive data/insample/TRBUSDT/misure.json.
"""

import json
from datetime import datetime

import numpy as np

from research.campagne.TRBUSDT.codice import banco, registro


def ts(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


if __name__ == "__main__":
    voci = registro.voci()
    reg = [v for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"]
    ris = {v["id"]: v for v in voci if v.get("tipo") == "risultato"}
    scarti = [v for v in voci if v.get("tipo") == "scarto"]
    prima, ultima = ts(voci[0]["data"]), ts(voci[-1]["data"])
    pause = [(ts(v["pausa_da"]), ts(v["pausa_a"])) for v in voci if v.get("pausa_da")]
    durata = (ultima - prima).total_seconds() / 60
    durata_senza = durata - sum((b - a).total_seconds() / 60 for a, b in pause)
    per_idea = {}
    for r in reg:
        per_idea.setdefault(r["idea"], []).append(r)
    minuti = {}
    for idea, rs in per_idea.items():
        inizio = min(ts(r["data"]) for r in rs)
        fine = max(ts(ris[r["id"]]["data"]) for r in rs if r["id"] in ris)
        minuti[idea] = round((fine - inizio).total_seconds() / 60, 1)
    t_b = [float(ris[r["id"]]["t_b"]) for r in reg if r["id"] in ris and ris[r["id"]].get("valutabile")]
    righe = []
    for r in reg:
        x = ris[r["id"]]
        righe.append({"n": r["variante_n"], "id": r["id"], "tf": r["timeframe"], "dir": r["direzione"],
                      "ritocco_di": r.get("ritocco_di"), "trade": x["metriche"]["trade"],
                      "r_medio": round(x["metriche"]["r_medio"], 3), "media_b": round(x["baseline_b"]["media"], 3),
                      "t_a": round(float(x["baseline_a"]["confronto_t"]), 2), "t_b": round(float(x["t_b"]), 2),
                      "netta_a": x["netta_a"], "netta_b": x["netta_b"], "percentile": x["percentile_caso"],
                      "previsione_corretta": x["previsione_corretta"], "r_per_anno": x["metriche"]["r_medio_per_anno"],
                      "pf": round(x["metriche"]["profit_factor"], 2)})
    out = {
        "prima_voce": voci[0]["data"], "ultima_voce": voci[-1]["data"],
        "durata_minuti": round(durata, 1), "durata_minuti_senza_pause": round(durata_senza, 1), "pause": len(pause),
        "varianti": len(reg), "ritocchi": sum(1 for r in reg if r.get("ritocco_di")),
        "famiglie": len({r["famiglia"] for r in reg}), "idee_testate": len(per_idea),
        "scarti": len(scarti), "scarti_elenco": {s["id"]: s["trade_stimati"] for s in scarti},
        "minuti_per_idea": minuti,
        "candidati": sum(1 for r in reg if ris[r["id"]].get("candidato")),
        "nette_a_e_b_con_r_non_positivo": sum(1 for r in reg if ris[r["id"]]["netta_a"] and ris[r["id"]]["netta_b"]
                                              and ris[r["id"]]["metriche"]["r_medio"] <= 0),
        "nette_solo_a": sum(1 for r in reg if ris[r["id"]]["netta_a"]),
        "nette_solo_b": sum(1 for r in reg if ris[r["id"]]["netta_b"]),
        "previsioni_corrette": sum(1 for r in reg if ris[r["id"]]["previsione_corretta"]),
        "t_b_media": round(float(np.mean(t_b)), 3), "t_b_deviazione": round(float(np.std(t_b, ddof=1)), 3),
        "t_b_massimo": round(max(t_b), 3), "t_b_minimo": round(min(t_b), 3),
        "varianti_tabella": righe,
    }
    with open(banco.RADICE / "data" / "insample" / "TRBUSDT" / "misure.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps({k: v for k, v in out.items() if k != "varianti_tabella"}, indent=1, ensure_ascii=False))
