"""Riga di comando del banco di prova.

  python esegui_test.py conta <ID>                  conta_trade (una volta sola, prima della registrazione)
  python esegui_test.py testa <ID> [costruzione|validazione] [ritardo] [costi2]
                                                    test con baseline (a) e (b); scrive la bozza del
                                                    risultato in data/insample/SOLUSDT/bozze/ris_<ID>.json
Opzioni aggiuntive: tf=<timeframe> (timeframe adiacente), intrabarra (regola opposta).
"""
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
from varianti import VARIANTI  # noqa: E402

BOZZE = comune.dati.RADICE_DEFAULT / "data" / "insample" / comune.SIMBOLO / "bozze"


def main(argv):
    if argv[0] == "conta":
        for vid in argv[1:]:
            tf, costruttrice = VARIANTI[vid][0], VARIANTI[vid][1]
            ris = {"id": vid, "timeframe": tf, "conta_trade": comune.conta(tf, costruttrice)}
            BOZZE.mkdir(parents=True, exist_ok=True)
            (BOZZE / f"conta_{vid}.json").write_text(json.dumps(ris))
            print(json.dumps(ris))
        return
    comando, vid = argv[0], argv[1]
    opzioni = argv[2:]
    tf, costruttrice = VARIANTI[vid][0], VARIANTI[vid][1]
    costruttrice_a = VARIANTI[vid][2] if len(VARIANTI[vid]) > 2 else None
    for o in opzioni:
        if o.startswith("tf="):
            tf = o[3:]
    t0 = time.time()
    if comando == "conta":
        print(json.dumps({"id": vid, "timeframe": tf, "conta_trade": comune.conta(tf, costruttrice)}))
    elif comando == "testa":
        periodo = "validazione" if "validazione" in opzioni else "costruzione"
        par = comune.PARAMETRI
        if "ritardo" in opzioni:
            par = replace(par, ritardo_barre=1)
        if "costi2" in opzioni:
            par = replace(par, moltiplicatore_costi=2.0)
        if "intrabarra" in opzioni:
            par = replace(par, riempimento_intrabarra="target_prima")
        ris = comune.valuta(tf, costruttrice, periodo, par, costruttrice_a=costruttrice_a)
        uscita = comune.pulito(ris)
        uscita["opzioni"] = opzioni
        nome = "ris_" + vid + "".join("_" + o.replace("=", "") for o in opzioni) + ".json"
        BOZZE.mkdir(parents=True, exist_ok=True)
        (BOZZE / nome).write_text(json.dumps(uscita, ensure_ascii=False, indent=1, default=str))
        print(json.dumps(uscita, ensure_ascii=False, default=str))
    print("secondi:", round(time.time() - t0, 1))


if __name__ == "__main__":
    main(sys.argv[1:])
