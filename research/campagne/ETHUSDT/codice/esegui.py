"""Esegue un'azione su una variante e scrive l'esito in data/insample/ETHUSDT/lavoro/.

Uso: python research/campagne/ETHUSDT/codice/esegui.py <modulo> <id> <azione>

Azioni:
* ``conta``: solo ``conta_trade`` (Fase 1, punto 7), da fare UNA volta, prima della registrazione;
* ``costruzione``: il giro di Fase 2 sul periodo di costruzione (candidato, (a), (b), (c));
* ``ritardo``: candidato e (b) con l'ingresso ritardato di una barra;
* ``costi_doppi``: candidato e (b) con i costi moltiplicati per 2;
* ``intrabarra_opposta``: candidato e (b) con il target prima dello stop.

Il modulo deve avere ``VARIANTI = {id: (Classe, parametri, timeframe)}``. Nessun
risultato viene scritto nel log da qui: le voci del log si scrivono a parte.
"""

import importlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
from registro import pulisci  # noqa: E402


def main() -> None:
    modulo, ident, azione = sys.argv[1], sys.argv[2], sys.argv[3]
    V, kw, tf = importlib.import_module(modulo).VARIANTI[ident]
    inizio = time.time()
    if azione == "conta":
        esito = comune.conta(V, kw, tf)
    elif azione == "costruzione":
        esito = comune.valuta(V, kw, tf)
    elif azione == "ritardo":
        esito = comune.valuta(V, kw, tf, comune.parametri(ritardo_barre=1), con_a=False)
    elif azione == "costi_doppi":
        esito = comune.valuta(V, kw, tf, comune.parametri(moltiplicatore_costi=2.0), con_a=False)
    elif azione == "intrabarra_opposta":
        esito = comune.valuta(V, kw, tf, comune.parametri(riempimento_intrabarra="target_prima"), con_a=False)
    else:
        raise ValueError(azione)
    esito = {"id": ident, "azione": azione, "timeframe": tf, "parametri": kw,
             "secondi": round(time.time() - inizio, 1), "esito": esito}
    uscita = comune.LAVORO / f"{ident}_{azione}.json"
    uscita.parent.mkdir(parents=True, exist_ok=True)
    uscita.write_text(json.dumps(pulisci(esito), indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("scritto", uscita.name, "in", esito["secondi"], "s")


if __name__ == "__main__":
    main()
