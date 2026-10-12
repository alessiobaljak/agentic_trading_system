"""Tabella markdown delle varianti per consegna.md, dal log."""
import json

from comune import LOG

voci = [json.loads(r) for r in open(LOG, encoding="utf-8") if r.strip()]
reg = {v["id"]: v for v in voci if v["tipo"] in ("registrazione", "scarto")}
print("| id | idea | tf | dir. | ritocco di | trade | R medio | senza 3 migliori | R 2021 | R 2022 | (a) t | (b) media | (b) t | soglia | percentile |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")


def f(x, d=2):
    return f"{x:.{d}f}" if isinstance(x, (int, float)) else str(x)


for v in voci:
    if v["tipo"] == "scarto":
        print(f"| {v['id']} | {v['idea']} | {v['timeframe']} | {v['direzione']} | {v.get('ritocco_di') or ''} | "
              f"scarto ({v['trade_stimati']}) | | | | | | | | | |")
    if v["tipo"] == "risultato":
        r, m = reg[v["id"]], v["metriche"]
        a, b = v.get("baseline_a", {}), v.get("baseline_b", {})
        anni = m["r_medio_per_anno"]
        print(f"| {v['id']} | {r['idea']} | {r['timeframe']} | {r['direzione']} | {r.get('ritocco_di') or ''} | {m['trade']} | "
              f"{f(m['r_medio'], 3)} | {f(m['r_medio_senza_3_migliori'], 3)} | {f(anni.get('2021'), 3)} | {f(anni.get('2022'), 3)} | "
              f"{f(a.get('t'))} | {f(b.get('media'), 3)} | {f(b.get('t'))}{' (netta)' if b.get('netta') else ''} | "
              f"{f(b.get('soglia'))} | {f(v.get('percentile_caso'), 1)} |")
