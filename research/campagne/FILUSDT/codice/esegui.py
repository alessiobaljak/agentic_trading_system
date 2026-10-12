"""Esecuzione di conteggi e test della campagna FILUSDT.

Uso:
  python esegui.py conta NOME                      -> conta_trade sulle regole esatte (una volta per variante)
  python esegui.py test NOME [periodo] [costi] [ritardo] [riempimento] [etichetta]
                                                   -> test con baseline (a) e (b); esito in
                                                      data/insample/FILUSDT/esiti/<NOME>_<etichetta>.json
NOME e' una chiave di ``varianti.TUTTE``.
"""
from __future__ import annotations

import json
import sys
import time

import comune
import quadro
import varianti
from registro import _pulisci

CARTELLA_ESITI = comune.CARTELLA_DATI / "esiti"


def main(argv):
    modo, nome = argv[1], argv[2]
    v = varianti.TUTTE[nome]()
    CARTELLA_ESITI.mkdir(parents=True, exist_ok=True)
    periodo = argv[3] if len(argv) > 3 else "costruzione"
    costi = float(argv[4]) if len(argv) > 4 else 1.0
    ritardo = int(argv[5]) if len(argv) > 5 else 0
    riempimento = argv[6] if len(argv) > 6 else "stop_prima"
    etichetta = argv[7] if len(argv) > 7 else "test"
    if modo == "conta":
        c = quadro.conta(v, costi, ritardo, riempimento)
        print(json.dumps(c))
        suffisso = "" if etichetta == "test" else f"_{etichetta}"
        (CARTELLA_ESITI / f"{nome}_conta{suffisso}.json").write_text(json.dumps(c))
        return
    t0 = time.time()
    ris = quadro.esegui_test(v, periodo, costi, ritardo, riempimento)
    trades = ris.pop("_trades", [])
    ris["secondi"] = round(time.time() - t0, 1)
    ris["trade_dettaglio"] = [[t.ts_entrata, t.ts_uscita, round(t.r, 4), t.esito] for t in trades]
    (CARTELLA_ESITI / f"{nome}_{etichetta}.json").write_text(json.dumps(_pulisci(ris), indent=1))
    sintesi = {k: ris.get(k) for k in ("trade", "valutabile", "candidato", "percentile_caso", "blocco", "secondi")}
    m = ris.get("metriche", {})
    sintesi.update({"r_medio": m.get("r_medio"), "pf": m.get("profit_factor"),
                    "t_a": ris.get("baseline_a", {}).get("t"), "netta_a": ris.get("baseline_a", {}).get("netta"),
                    "t_b": ris.get("baseline_b", {}).get("t"), "netta_b": ris.get("baseline_b", {}).get("netta"),
                    "media_b": ris.get("baseline_b", {}).get("media")})
    print(json.dumps(_pulisci(sintesi)))


if __name__ == "__main__":
    main(sys.argv)
