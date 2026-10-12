"""Stampa i numeri principali di un esito (per scrivere il commento del risultato).

Uso: python sintesi.py NOME [etichetta]
"""
from __future__ import annotations

import json
import sys

import comune

if __name__ == "__main__":
    nome = sys.argv[1]
    etichetta = sys.argv[2] if len(sys.argv) > 2 else "test"
    e = json.loads((comune.CARTELLA_DATI / "esiti" / f"{nome}_{etichetta}.json").read_text())
    m = e.get("metriche", {})
    print(nome, etichetta, "trade", e["trade"], "valutabile", e.get("valutabile"), "candidato", e.get("candidato"))
    for k in ("r_medio", "r_mediano", "win_rate", "profit_factor", "r_medio_senza_3_migliori", "drawdown_max",
              "rendimento_totale", "costi_medi_r", "funding_totale_r", "stop_medio_pct", "quota_stop_oltre_6pct",
              "n_ridotti", "n_violazioni_liquidazione", "esiti"):
        print(" ", k, m.get(k))
    print("  r per anno", m.get("r_medio_per_anno"), "trade per anno", m.get("trade_per_anno"))
    a, b = e.get("baseline_a", {}), e.get("baseline_b", {})
    print("  (a) media", a.get("media"), "t", a.get("t"), "soglia", a.get("soglia"), "netta", a.get("netta"), "n", a.get("n_trade"))
    print("  (b) media", b.get("media"), "t", b.get("t"), "soglia", b.get("soglia"), "netta", b.get("netta"),
          "trade/sim", b.get("trade_per_simulazione_medio"), "vietate", b.get("quota_barre_vietate_totale"))
    print("  percentile", e.get("percentile_caso"), "blocco", e.get("blocco"), "durata media", e.get("durata_media_barre"))
    print("  buy and hold", e.get("buy_and_hold_per_anno"))
