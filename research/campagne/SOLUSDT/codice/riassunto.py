"""Riassunto dei risultati delle varianti dal log (solo lettura)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro  # noqa: E402

voci = registro.voci()
reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione"}
for v in voci:
    if v.get("tipo") != "risultato":
        continue
    m, a, b = v["metriche"], v["baseline_a"], v["baseline_b"]
    r = reg.get(v["id"], {})
    print(f"{v['id']:<14} n{r.get('variante_n')} {r.get('timeframe'):>4} {r.get('direzione'):<5} tr {m.get('trade'):>4} "
          f"R {m.get('r_medio'):>7} s3 {m.get('r_medio_senza_3_migliori')} PF {m.get('profit_factor')} "
          f"a {a.get('media')} t_a {a.get('t')} | b {b.get('media')} t_b {b.get('t')} val {b.get('valutabile')} "
          f"pct {v.get('percentile_caso')} cand {v.get('candidato')} anni {m.get('r_medio_per_anno')}")
