"""Scrive nel log la voce di risultato di una variante, dal file risultati/<chiave>.json piu'
previsione_corretta e commento presi da un file JSON {"V-01": {"previsione_corretta": .., "commento": ..}}.

Uso: python chiudi.py <file_commenti.json>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from log_campagna import aggiungi  # noqa: E402

commenti = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for chiave, extra in commenti.items():
    voce = json.loads((comune.CARTELLA / "risultati" / f"{chiave}.json").read_text(encoding="utf-8"))
    voce.update(extra)
    print(aggiungi(voce)["data"], voce["id"])
