"""Stampa una sintesi leggibile degli esiti salvati (nomi dei file in risultati/)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402

for nome in sys.argv[1:]:
    r = json.loads((q.CARTELLA_DATI / "risultati" / f"{nome}.json").read_text())
    m = r.get("metriche", {})
    a, b = r.get("baseline_a", {}), r.get("baseline_b", {})
    print(json.dumps({
        "nome": nome, "trade": m.get("trade"), "r": m.get("r_medio"), "pf": m.get("profit_factor"),
        "r_anno": m.get("r_medio_per_anno"), "n_anno": m.get("trade_per_anno"),
        "senza3": m.get("r_medio_senza_3_migliori"), "dd": m.get("drawdown_max"), "win": m.get("win_rate"),
        "esiti": m.get("esiti"), "costo_r": m.get("costo_medio_r"), "durata": m.get("durata_media_barre"),
        "blocco": r.get("blocco"),
        "a": {k: a.get(k) for k in ("media", "t", "soglia", "netta", "valutabile", "n_blocchi")},
        "b": {k: b.get(k) for k in ("media", "t", "soglia", "netta", "valutabile", "n_blocchi")},
        "perc": r.get("percentile_caso"), "candidato": r.get("candidato")}, ensure_ascii=False))
