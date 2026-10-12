"""Tabella compatta del log: registrazioni, scarti e risultati delle varianti."""
from comune import voci_log

for v in voci_log():
    t = v.get("tipo")
    if t == "scarto":
        print(f"{v['id']:14s} SCARTO  trade {v['trade_stimati']}")
    elif t == "registrazione":
        print(f"{v['id']:14s} REG n={v.get('variante_n')} {v.get('tipo_test')} stimati {v['trade_stimati']} {v['timeframe']} {v['direzione']}")
    elif t == "risultato" and "metriche" in v:
        m = v["metriche"]
        a, b = v.get("baseline_a", {}), v.get("baseline_b", {})
        print(f"{v['id']:14s} RIS trade {m['trade']} R {m['r_medio']} senza3 {m['r_medio_senza_3_migliori']} "
              f"per anno {m['r_medio_per_anno']} | a {a.get('media')} t {a.get('t')} | b {b.get('media')} t {b.get('t')} "
              f"val {v.get('valutabile')} perc {v.get('percentile_caso')} cand {v.get('candidato')} prev {v.get('previsione_corretta')}")
