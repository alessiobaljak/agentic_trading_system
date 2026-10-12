"""Scrive nel log la voce ``risultato`` di una variante dal suo file in ``esiti/``.

Uso: python research/campagne/MATICUSDT/codice/chiudi.py <ID log> <file esito> <si|no|parziale> "<commento>"
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import logga  # noqa: E402

vid, file, corretta, commento = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
e = json.loads((Path(__file__).resolve().parents[1] / "esiti" / file).read_text(encoding="utf-8"))
voce = {"id": vid, "tipo": "risultato"}
voce["metriche"] = e["metriche"]
for k in ("blocco", "baseline_a", "baseline_b", "percentile_caso", "buy_and_hold_per_anno", "valutabile", "candidato",
          "timeframe", "periodo", "moltiplicatore_costi", "ritardo_barre", "intrabarra"):
    if k in e:
        voce[k] = e[k]
voce["previsione_corretta"] = {"si": True, "no": False}.get(corretta, corretta)
voce["commento"] = commento
logga.aggiungi(voce)
print(vid, "candidato" if e.get("candidato") else "non candidato",
      "t_a", e.get("baseline_a", {}).get("t"), "t_b", e.get("baseline_b", {}).get("t"),
      "r", e["metriche"]["r_medio"], "n", e["metriche"]["trade"])
