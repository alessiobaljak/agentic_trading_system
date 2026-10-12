"""Tabella compatta delle verifiche (Fase 4 e 5) nel log."""
import json

from comune import voci_log

reg = {}
for v in voci_log():
    if v.get("tipo") == "registrazione" and v.get("tipo_test") == "verifica":
        reg[v["id"]] = v
    elif v.get("tipo") == "risultato" and v["id"] in reg:
        r = reg[v["id"]]
        if not v.get("conta", True):
            print(f"{v['id']:18s} {r['verifica'][:60]:60s} NON CONTA: {v.get('commento')}")
            continue
        b, a = v.get("baseline_b", {}), v.get("baseline_a", {})
        print(f"{v['id']:18s} {r['verifica'][:60]:60s} trade {v['trade']} R {v['r_medio']} t_a {a.get('t')} "
              f"t_b {b.get('t')} netta_b {b.get('netta')} b {b.get('media')} senza3 {v.get('r_medio_senza_3_migliori')}")
    elif v.get("tipo") == "nota" and str(v.get("argomento", "")).startswith("esito della Fase 4"):
        print(v["argomento"], "->", v["passa_la_fase_4"], json.dumps(v["esiti"], ensure_ascii=False))
