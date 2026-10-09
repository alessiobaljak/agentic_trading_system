"""Riassunto leggibile dei file risultati/<chiave>.json. Uso: python riassunto.py V-01 [V-02 ...]"""
import json
import sys
from pathlib import Path

CART = Path(__file__).resolve().parents[1] / "risultati"
for k in sys.argv[1:]:
    r = json.loads((CART / f"{k}.json").read_text(encoding="utf-8"))
    m = r["metriche"]
    a, b = r.get("baseline_a", {}), r.get("baseline_b", {})
    print(f"== {k} {r['id']} trade {m['trade']} R {m['r_medio']} pf {m['profit_factor']} win {m['win_rate']} dd {m['drawdown_max']}")
    print("   R per anno", m["r_medio_per_anno"], "trade per anno", m["trade_per_anno"])
    print("   senza 3 migliori", m["r_medio_senza_3_migliori"], "costo medio R", m["costo_medio_r"],
          "stop mediano %", m["distanza_stop_mediana_pct"], "stop>6%", m["stop_oltre_6_per_cento"],
          "ridotti", m["trade_ridotti_leva"], "violazioni", m["violazioni_liquidazione"], "esiti", m["esiti"],
          "durata", m["durata_media_barre"])
    print("   (a) media", a.get("media"), "t", a.get("t"), "soglia", a.get("soglia"), "netta", a.get("netta"),
          "valutabile", a.get("valutabile"), "blocchi", a.get("n_blocchi"))
    print("   (b) media", b.get("media"), "t", b.get("t"), "soglia", b.get("soglia"), "netta", b.get("netta"),
          "valutabile", b.get("valutabile"), "blocchi", b.get("n_blocchi"), "vietate", b.get("quota_barre_vietate_segnale"),
          "trade/sim", b.get("trade_per_simulazione"))
    print("   blocco", r.get("blocco"), "percentile", r.get("percentile_caso"), "candidato", r.get("candidato"),
          "rendimento per anno", m["rendimento_per_anno"])
    print("   buy and hold", r.get("buy_and_hold_per_anno"))
