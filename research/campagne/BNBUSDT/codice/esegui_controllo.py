"""Controllo positivo degli strumenti: senza ritardo e con ritardo di una barra."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import registro  # noqa: E402
import varianti  # noqa: E402

v = varianti.controllo_positivo()
t0 = time.time()
r0 = C.valuta(v)
r1 = C.valuta(v, ritardo_barre=1)
print(C.compatto(r0))
print(C.compatto(r1))
print("secondi", time.time() - t0)
registro.aggiungi({"id": "BNBUSDT-N008", "tipo": "nota", "controllo_positivo": "dopo",
                   "testo": "Esito del controllo positivo degli strumenti (registrato in BNBUSDT-N007).",
                   "senza_ritardo": {"metriche": r0["metriche"], "baseline_a": r0.get("baseline_a"),
                                     "baseline_b": r0.get("baseline_b"), "percentile_caso": r0.get("percentile_caso")},
                   "ritardo_una_barra": {"metriche": r1["metriche"], "baseline_a": r1.get("baseline_a"),
                                         "baseline_b": r1.get("baseline_b"), "percentile_caso": r1.get("percentile_caso")}})
