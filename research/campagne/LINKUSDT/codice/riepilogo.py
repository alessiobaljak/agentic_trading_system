"""Tabella dei risultati di costruzione dal log (solo lettura del proprio log)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro as R  # noqa: E402

reg = {v["id"]: v for v in R.voci() if v["tipo"] == "registrazione"}
for v in R.voci():
    if v["tipo"] == "risultato" and v["id"] in reg:
        g = reg[v["id"]]
        m = v["metriche"]
        a, b = v["baseline_a"], v["baseline_b"]
        print(f'{v["id"]:16s} {g["timeframe"]:4s} {g["direzione"]:5s} n={m["trade"]:4d} R={m["r_medio"]:+.3f} '
              f'R-3={m["r_medio_senza_3_migliori"]:+.3f} ta={a.get("t"):+.2f} tb={b.get("t"):+.2f} '
              f'b={b.get("media"):+.3f} pct={v.get("percentile_caso")} anni={ {k: round(x, 2) for k, x in m["r_medio_per_anno"].items()} }')
    if v["tipo"] == "scarto":
        print(f'{v["id"]:16s} scarto {v["trade_stimati"]}')
