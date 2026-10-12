"""Tabella in markdown di tutte le varianti testate e degli scarti, dai campi del log (solo lettura).

Uso: python3 -u tabella_varianti.py
"""
import json

from comune import CARTELLA_GRUPPO


def f(x, n=3):
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",")


if __name__ == "__main__":
    voci = [json.loads(x) for x in (CARTELLA_GRUPPO / "log.jsonl").read_text().splitlines() if x.strip()]
    ris = {v["id"]: v for v in voci if v["tipo"] == "risultato"}
    print("| n. | id | variante | tf | dir. | ritocco di | trade | R medio dopo i costi | t contro (b) | t contro (a) "
          "| soglia | blocchi | R senza i 30 migliori | R per anno (2020/21/22/23) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for v in voci:
        if v["tipo"] == "registrazione":
            r = ris[v["id"]]
            m = r["metriche"]
            anni = " / ".join(f(m["r_medio_per_anno"].get(a), 2) for a in ("2020", "2021", "2022", "2023"))
            print(f"| {v['variante_n']} | {v['id']} | {v['variante_nome']} | {v['timeframe']} | {v['direzione']} | "
                  f"{v.get('ritocco_di') or '—'} | {m['trade']} | {f(m['r_medio'])} | {f(r['baseline_b']['t'], 2)} | "
                  f"{f(r['baseline_a']['t'], 2)} | {f(r['baseline_b']['soglia'], 2)} | {r['n_blocchi']} | "
                  f"{f(m.get('r_medio_senza_30_migliori'))} | {anni} |")
    print()
    print("| scarto | variante | trade stimati | motivo |")
    print("|---|---|---|---|")
    for v in voci:
        if v["tipo"] == "scarto":
            print(f"| {v['id']} | {v['variante_nome']} | {v['trade_stimati']} | {v['motivo_scarto']} |")
