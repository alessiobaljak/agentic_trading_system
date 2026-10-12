"""Fase 5: riepilogo delle 30 varianti dal log (t contro la (b), R medio, conteggi per famiglia)."""

import json

import numpy as np

from research.campagne.GALAUSDT.codice import registro


def main():
    voci = [json.loads(r) for r in registro.LOG.read_text(encoding="utf-8").splitlines() if r.strip()]
    reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
    ris = {v["id"]: v for v in voci if v.get("tipo") == "risultato" and v["id"] in reg}
    t = np.array([float(ris[i]["baseline_b"]["t"]) for i in reg if i in ris])
    r = np.array([float(ris[i]["metriche"]["r_medio"]) - float(ris[i]["baseline_b"]["media"]) for i in reg if i in ris])
    out = {
        "varianti": len(reg), "con_risultato": len(ris),
        "ritocchi": sum(1 for v in reg.values() if v.get("ritocco_di")),
        "famiglie": len({v.get("famiglia") for v in reg.values()}),
        "t_b_media": float(t.mean()), "t_b_dev_std": float(t.std(ddof=1)),
        "t_b_positivi": int((t > 0).sum()), "t_b_sopra_1": int((t > 1).sum()), "t_b_sopra_soglia": int(sum(
            1 for i in ris if ris[i]["baseline_b"].get("netta"))),
        "differenza_r_contro_b_media": float(r.mean()),
        "netta_a_e_b": [i for i in ris if ris[i].get("batte_a_e_b")],
        "netta_a_e_b_con_r_non_positivo": [i for i in ris if ris[i].get("batte_a_e_b") and ris[i]["metriche"]["r_medio"] <= 0],
        "candidati": [i for i in ris if ris[i].get("candidato")],
        "per_timeframe": {},
    }
    for i in ris:
        tf = reg[i]["timeframe"]
        out["per_timeframe"].setdefault(tf, []).append(round(float(ris[i]["baseline_b"]["t"]), 2))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
