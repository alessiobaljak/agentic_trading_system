"""Esegue in serie il test della Fase 2 (o una verifica) per le varianti passate per nome.

Uso: python testa_lotto.py [--costi 2] [--ritardo 1] [--intrabarra target_prima] [--periodo validazione]
                           [--tag T] nome1 nome2 ...
Ogni esito va in data/insample/1000SHIBUSDT/risultati/<nome>[_tag].json; una riga di sintesi
per variante si aggiunge a risultati/avanzamento.txt (gli script in background non hanno
un'uscita leggibile: log, nota N005).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
import varianti  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("nomi", nargs="+")
ap.add_argument("--costi", type=float, default=1.0)
ap.add_argument("--ritardo", type=int, default=0)
ap.add_argument("--intrabarra", default="stop_prima")
ap.add_argument("--periodo", default="costruzione")
ap.add_argument("--tag", default="")
a = ap.parse_args()
AVANZAMENTO = q.CARTELLA_DATI / "risultati" / "avanzamento.txt"
AVANZAMENTO.parent.mkdir(parents=True, exist_ok=True)
for nome in a.nomi:
    v = varianti.VARIANTI[nome]
    par = q.parametri(moltiplicatore_costi=a.costi, ritardo_barre=a.ritardo, riempimento=a.intrabarra)
    ris = q.esame(v, par, periodo=a.periodo)
    trades = ris.pop("_trades", [])
    file = nome + (("_" + a.tag) if a.tag else "")
    q.salva(file, ris)
    q.salva(file + "_trade", trades)
    m = ris.get("metriche", {})
    riga = {"nome": file, "trade": m.get("trade"), "r_medio": m.get("r_medio"),
            "t_a": ris.get("baseline_a", {}).get("t"), "netta_a": ris.get("baseline_a", {}).get("netta"),
            "t_b": ris.get("baseline_b", {}).get("t"), "netta_b": ris.get("baseline_b", {}).get("netta"),
            "candidato": ris.get("candidato")}
    with open(AVANZAMENTO, "a", encoding="utf-8") as f:
        f.write(json.dumps(riga) + "\n")
    print(json.dumps(riga), flush=True)
