"""Compone le voci `risultato` del log dagli esiti salvati e le aggiunge al log.

Uso: python risultato.py <file.json>   (lista di {"nome", "id", "previsione_corretta", "commento"}
     e, per le verifiche, "file" se diverso dal nome)
Senza argomenti dopo il file stampa solo la sintesi. I campi seguono la sezione 6.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
import scrivi_log  # noqa: E402


def voce(spec):
    file = spec.get("file", spec["nome"])
    ris = json.loads((q.CARTELLA_DATI / "risultati" / f"{file}.json").read_text())
    m = ris["metriche"]
    out = {
        "id": spec["id"], "tipo": "risultato",
        "metriche": m,
        "blocco": ris.get("blocco"),
        "baseline_a": ris.get("baseline_a"),
        "baseline_b": ris.get("baseline_b"),
        "percentile_caso": ris.get("percentile_caso"),
        "buy_and_hold_per_anno": ris.get("buy_and_hold_per_anno"),
        "valutabile": ris.get("valutabile"),
        "candidato_fase_2": ris.get("candidato"),
        "previsione_corretta": spec["previsione_corretta"],
        "commento": spec["commento"],
    }
    for k in ("verifica", "periodo"):
        if k in spec:
            out[k] = spec[k]
    return out


if __name__ == "__main__":
    specs = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    voci = [voce(s) for s in specs]
    print("voci aggiunte:", scrivi_log.aggiungi(voci))
