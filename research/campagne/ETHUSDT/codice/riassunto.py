"""Stampa in breve uno o piu' esiti di esegui.py (file in data/insample/ETHUSDT/lavoro/).

Uso: python research/campagne/ETHUSDT/codice/riassunto.py <id>_<azione> [...]
"""

import json
import sys
from pathlib import Path

LAVORO = Path(__file__).resolve().parents[4] / "research" / "data" / "insample" / "ETHUSDT" / "lavoro"


def f(x, n=3):
    return f"{x:.{n}f}" if isinstance(x, (int, float)) and not isinstance(x, bool) else str(x)


def main() -> None:
    for nome in sys.argv[1:]:
        d = json.loads((LAVORO / f"{nome}.json").read_text(encoding="utf-8"))
        e = d["esito"]
        print(f"== {nome} ({d.get('timeframe', '')}, {d.get('secondi', '')} s)")
        if d.get("azione") == "conta":
            print("  ", e)
            continue
        m = e["metriche"]
        print(f"   trade {m['trade']}  R medio {f(m['r_medio'])}  PF {f(m['profit_factor'], 2)}  "
              f"senza 3 migliori {f(m['r_medio_senza_3_migliori'])}  DD {f(m['drawdown_max'])}  "
              f"rend {f(m['rendimento_totale'])}  win {f(m['win_rate'], 2)}")
        print("   R per anno", {k: round(v, 3) for k, v in m["r_medio_per_anno"].items()}, "trade per anno", m["trade_per_anno"])
        if "esiti" in m:
            print("   esiti", m["esiti"], "ridotti", m.get("n_ridotti"), "violazioni", m.get("n_violazioni_liquidazione"))
        print("   blocco", e.get("blocco"))
        for k in ("baseline_a", "baseline_b"):
            if k in e:
                b = e[k]
                print(f"   {k}: media {f(b.get('media'))}  t {f(b.get('t'), 2)}  soglia {f(b.get('soglia'), 2)}  "
                      f"netta {b.get('netta')}  valutabile {b.get('valutabile')}  blocchi {b.get('n_blocchi')}"
                      + (f"  errore {b['errore']}" if "errore" in b else ""))
        if "baseline_b" in e and "trade_per_simulazione_medio" in e["baseline_b"]:
            b = e["baseline_b"]
            print(f"   (b): trade per simulazione {f(b['trade_per_simulazione_medio'], 1)}  durata media {b['durata_media_barre']}  "
                  f"barre vietate {f(b['quota_barre_vietate_segnale_non_valido'])}  scartati {f(b['segnali_scartati_per_simulazione_medio'], 2)}")
        print("   percentile caso", e.get("percentile_caso"), " candidato", e.get("candidato"), " valutabile", e.get("valutabile"))


if __name__ == "__main__":
    main()
