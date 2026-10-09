"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che legge la barra dopo.

Deve battere nettamente la (b) e crollare col ritardo di una barra. Scrive risultati/controllo.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from varianti import CONTROLLO  # noqa: E402

out = {}
for nome, par in (("senza_ritardo", comune.PARAMETRI), ("ritardo_1", comune.parametri_con(ritardo_barre=1))):
    ris = comune.valuta(CONTROLLO, "costruzione", parametri=par)
    out[nome] = comune.per_log(ris)
    b = ris["baseline_b"]
    print(nome, "trade", ris["metriche"]["trade"], "r_medio", ris["metriche"]["r_medio"],
          "b media", b.get("media"), "t_b", b.get("t"), "netta_b", b.get("netta"),
          "t_a", ris["baseline_a"].get("t"), flush=True)
(comune.CARTELLA / "risultati").mkdir(exist_ok=True)
(comune.CARTELLA / "risultati" / "controllo.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
