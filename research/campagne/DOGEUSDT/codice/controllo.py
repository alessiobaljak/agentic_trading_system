"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che guarda la barra dopo.

Deve battere nettamente la (a) e la (b) senza ritardo e crollare con il ritardo di una barra.
Si registra come nota, prima e dopo; non consuma budget.
"""
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
import registro  # noqa: E402
from varianti import Controllo  # noqa: E402

registro.aggiungi({"tipo": "nota", "argomento": "controllo positivo degli strumenti: prima",
                   "regole": "1h long; ingresso se la barra DOPO il segnale chiude sopra la sua apertura di oltre 0,3% (sguardo nel futuro dichiarato); uscita dopo 1 barra; stop 2 ATR14",
                   "attesa": "batte nettamente la (a) e la (b) senza ritardo; con il ritardo di una barra il t contro la (b) ricalcolata crolla (sotto la meta' o negativo)"})
ris = {}
for nome, par in (("senza_ritardo", q.PARAMETRI), ("ritardo_1", replace(q.PARAMETRI, ritardo_barre=1))):
    out, _ = q.valuta(Controllo(), parametri=par)
    ris[nome] = {"trade": out["metriche"]["trade"], "r_medio": out["metriche"]["r_medio"],
                 "t_a": out["baseline_a"].get("t"), "netta_a": out["baseline_a"].get("netta"),
                 "t_b": out["baseline_b"].get("t"), "netta_b": out["baseline_b"].get("netta"),
                 "media_b": out["baseline_b"].get("media")}
    print(nome, ris[nome], flush=True)
ok = bool(ris["senza_ritardo"]["netta_a"] and ris["senza_ritardo"]["netta_b"]
          and ris["ritardo_1"]["t_b"] < 0.5 * ris["senza_ritardo"]["t_b"])
registro.aggiungi({"tipo": "nota", "argomento": "controllo positivo degli strumenti: dopo", "esiti": ris,
                   "superato": ok})
print("superato", ok)
