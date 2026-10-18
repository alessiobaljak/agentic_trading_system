"""Riepilogo delle varianti dal log: una riga per variante, con registrazione e risultato.

Uso: python3 research/campagne/LINK6/codice/riepilogo.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402

voci = comune.voci()
reg = {v["id"]: v for v in voci if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
ris = {v["id"]: v for v in voci if v.get("tipo") == "risultato"}
scarti = [v for v in voci if v.get("tipo") == "scarto"]
print("id | n | tf | dir | trade | R medio | casuali | p-value | PF | R per anno | esito")
for vid, r in reg.items():
    s = r["specifica"]
    x = ris.get(vid)
    if not x:
        print(f"{vid} | {r['variante_n']} | {s['timeframe']} | {s['direzione']} | senza risultato")
        continue
    m = x["metriche"]
    anni = ", ".join(f"{a} {v:+.1f}" for a, v in m["r_per_anno"].items())
    print(f"{vid} | {r['variante_n']} | {s['timeframe']} | {s['direzione']} | {m['trade']} | {m['r_medio']:+.3f} | "
          f"{x['r_medio_entrate_casuali']:+.3f} | {m['p_value']} | {m['profit_factor']} | {anni} | {x['esito']}")
print(f"varianti che consumano un tentativo: {len(comune.varianti_registrate())} su {comune.VARIANTI_MASSIME}; "
      f"scarti: {len(scarti)}")
