"""Stampa la tabella dei risultati di costruzione del log (una riga per variante)."""

import json

from research.campagne.GALAUSDT.codice import registro


def main():
    voci = [json.loads(r) for r in registro.LOG.read_text(encoding="utf-8").splitlines() if r.strip()]
    reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
    print("id tf dir trade R Rsenza3 t_a netta_a t_b netta_b media_b perc cand Rperanno")
    for v in voci:
        if v.get("tipo") != "risultato" or v["id"] not in reg or v.get("periodo") != "costruzione":
            continue
        r = reg[v["id"]]
        m, a, b = v["metriche"], v.get("baseline_a") or {}, v.get("baseline_b") or {}
        def f(x):
            return f"{x:.3f}" if isinstance(x, (int, float)) else str(x)
        print(v["id"][-3:], r["timeframe"], r["direzione"][0], m.get("trade"), f(m.get("r_medio")),
              f(m.get("r_medio_senza_3_migliori")), f(a.get("t")), a.get("netta"), f(b.get("t")), b.get("netta"),
              f(b.get("media")), f(v.get("percentile_caso")), v.get("candidato"),
              {k: round(x, 2) for k, x in m.get("r_medio_per_anno", {}).items()})


if __name__ == "__main__":
    main()
