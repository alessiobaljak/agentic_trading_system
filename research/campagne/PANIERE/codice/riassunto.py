"""Riassunto delle varianti dal log: una riga per variante, con i numeri che il protocollo chiede di riportare sempre.

Per ogni scarto: trade stimati e motivi. Per ogni risultato: trade, R medio, R medio senza i 30 migliori, R medio per
anno d'uscita, t contro la (b) e contro la (a) con soglia e «netta», numero di blocchi, blocco, effetto grappolo,
monete su cui gli ingressi della (b) non entrano e la loro quota, percentile fra le M(s), candidato. Scrive anche
lavoro/riassunto.json. Nessun calcolo d'esame: legge solo i campi scritti da gruppo.esame_di_gruppo.
"""

import json
import sys
from pathlib import Path

CODICE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODICE))

import registro  # noqa: E402


def num(x, cifre=3):
    return "—" if x is None else (f"{x:.{cifre}f}" if isinstance(x, float) else str(x))


def main():
    righe = []
    for v in registro.voci():
        if v["tipo"] == "scarto":
            righe.append({"id": v["id"], "variante": v.get("variante"), "esito": "scarto",
                          "trade_stimati": v.get("trade_stimati"), "motivi": v.get("motivi")})
        elif v["tipo"] == "risultato" and v.get("variante"):
            m = v.get("metriche", {})
            b = v.get("baseline_b", {})
            a = v.get("baseline_a", {})
            righe.append({
                "id": v["id"], "variante": v["variante"], "esito": "risultato",
                "trade": m.get("trade"), "r_medio": m.get("r_medio"),
                "r_medio_senza_migliori": m.get("r_medio_senza_30_migliori", m.get("r_medio_senza_migliori")),
                "r_medio_per_anno": m.get("r_medio_per_anno"),
                "t_b": b.get("t"), "soglia_b": b.get("soglia"), "netta_b": b.get("netta"), "media_b": b.get("media"),
                "valutabile_b": b.get("valutabile"),
                "t_a": a.get("t"), "soglia_a": a.get("soglia"), "netta_a": a.get("netta"), "media_a": a.get("media"),
                "valutabile_a": a.get("valutabile"),
                "n_blocchi": v.get("n_blocchi"), "blocco": v.get("blocco"),
                "effetto_grappolo": v.get("effetto_grappolo"),
                "monete_senza_ingressi_b": b.get("monete_senza_ingressi"),
                "quota_trade_senza_ingressi_b": b.get("quota_trade_candidato_senza_ingressi"),
                "percentile_caso": v.get("percentile_caso"), "candidato": v.get("candidato"),
                "valutabile": v.get("valutabile"), "motivi_non_valutabile": v.get("motivi_non_valutabile"),
            })
    (CODICE.parent / "lavoro" / "riassunto.json").write_text(json.dumps(righe, indent=1, ensure_ascii=False) + "\n",
                                                              encoding="utf-8")
    for r in righe:
        if r["esito"] == "scarto":
            print(r["id"], r["variante"], "SCARTO", r["trade_stimati"], r["motivi"])
            continue
        anni = ", ".join(f"{a}: {num(x, 2)}" for a, x in (r["r_medio_per_anno"] or {}).items()) \
            if isinstance(r["r_medio_per_anno"], dict) else r["r_medio_per_anno"]
        print(f"{r['id']} {r['variante']}: trade {r['trade']}, R {num(r['r_medio'])}, "
              f"senza migliori {num(r['r_medio_senza_migliori'])}, per anno [{anni}]; "
              f"(b) {num(r['media_b'])} t {num(r['t_b'], 2)} soglia {num(r['soglia_b'], 2)} netta {r['netta_b']}; "
              f"(a) {num(r['media_a'])} t {num(r['t_a'], 2)} netta {r['netta_a']}; blocchi {r['n_blocchi']} "
              f"(blocco {r['blocco']}); grappolo {num(r['effetto_grappolo'], 1)}; senza ingressi (b) "
              f"{r['monete_senza_ingressi_b']} quota {num(r['quota_trade_senza_ingressi_b'])}; percentile "
              f"{num(r['percentile_caso'], 1)}; valutabile {r['valutabile']}; candidato {r['candidato']}")


if __name__ == "__main__":
    main()
