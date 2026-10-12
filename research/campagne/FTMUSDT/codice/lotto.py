"""In serie, per ogni ID: registra (conta i trade, scrive registrazione o scarto) e, se registrata, testa.
Uso: python lotto.py ID [ID...]. Le stampe vanno anche in data/insample/FTMUSDT/uscite/."""
import sys
import traceback

import run

for id_ in sys.argv[1:]:
    try:
        run.registra(id_)
        if any(v["id"] == id_ and v["tipo"] == "registrazione" for v in run.voci()):
            run.testa(id_)
    except BaseException:  # noqa: BLE001
        run.stampa(id_, "ERRORE " + traceback.format_exc())
run.stampa("lotto", "fine lotto " + " ".join(sys.argv[1:]))
