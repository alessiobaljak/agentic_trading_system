"""Stampa un riassunto dei risultati del log (solo costruzione): una riga per variante.

Uso: python -m research.campagne.BCHUSDT.codice.riassunto
Ordina per t contro la (b) (l'ordine dei ritocchi della regola 6).
"""
import json

from research.campagne.BCHUSDT.codice import registra


def main():
    voci = [json.loads(r) for r in registra.LOG.read_text(encoding="utf-8").splitlines() if r.strip()]
    reg = {v["id"]: v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"}
    righe = []
    for v in voci:
        if v["tipo"] != "risultato" or v["id"] not in reg:
            continue
        b = v.get("baseline_b", {})
        a = v.get("baseline_a", {})
        t = b.get("t")
        t = float("-inf") if t in (None, "-inf") else float(t)
        m = v["metriche"]
        righe.append((t, v["id"], reg[v["id"]].get("famiglia"), reg[v["id"]]["timeframe"], reg[v["id"]]["direzione"],
                      m["trade"], round(m["r_medio"], 3), a.get("t"), a.get("netta"), b.get("netta"),
                      round(b.get("media", float("nan")), 3), m["r_medio_per_anno"], m.get("r_medio_senza_3_migliori")))
    for r in sorted(righe, key=lambda x: (-x[0], x[1])):
        print(r[1], r[2], r[3], r[4], "trade", r[5], "R", r[6], "b_media", r[10], "t_b", round(r[0], 2),
              "t_a", None if r[7] is None else round(float(r[7]), 2), "netta a/b", r[8], r[9], "per anno", r[11],
              "senza3", None if r[12] is None else round(r[12], 3))


if __name__ == "__main__":
    main()
