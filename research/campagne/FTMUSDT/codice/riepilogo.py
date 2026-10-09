"""Tabella compatta dal log: registrazioni, scarti e risultati delle varianti."""
import json

from comune import LOG

voci = [json.loads(r) for r in open(LOG, encoding="utf-8") if r.strip()]
reg = {v["id"]: v for v in voci if v["tipo"] in ("registrazione", "scarto")}
for v in voci:
    if v["tipo"] == "scarto":
        print(f"{v['id']} SCARTO {v['idea']} {v['timeframe']} {v['direzione']} trade={v['trade_stimati']}")
    if v["tipo"] == "risultato":
        r = reg.get(v["id"], {})
        m = v["metriche"]
        a, b = v.get("baseline_a", {}), v.get("baseline_b", {})
        anni = {k: round(x, 3) for k, x in m["r_medio_per_anno"].items()}

        def f(x):
            return f"{x:.2f}" if isinstance(x, (int, float)) else str(x)
        print(f"{v['id']} {r.get('idea')} {r.get('timeframe')} {r.get('direzione')} n={m['trade']} R={m['r_medio']:.3f} "
              f"PF={f(m['profit_factor'])} senza3={m['r_medio_senza_3_migliori']:.3f} anni={anni} "
              f"a: media={f(a.get('media'))} t={f(a.get('t'))} {a.get('netta')} | "
              f"b: media={f(b.get('media'))} t={f(b.get('t'))} sogl={f(b.get('soglia'))} {b.get('netta')} blocchi={b.get('n_blocchi')} "
              f"perc={f(v.get('percentile_caso'))} cand={v.get('candidato')} btc={v.get('mercato_btc', {}).get('correlazione_r_con_btc')}")
