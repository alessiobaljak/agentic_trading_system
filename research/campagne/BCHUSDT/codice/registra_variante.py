"""Registra una variante: verifica di causalita', conta dei trade (una volta sola), registrazione o scarto.

Uso: python -m research.campagne.BCHUSDT.codice.registra_variante <file_json>

Il file contiene una voce (o una lista di voci) con i campi della registrazione
(sezione 6) tranne ``trade_stimati`` e ``variante_n``, che li mette questo script:
* rifiuta un ``id`` gia' presente nel log come registrazione o scarto (la conta si fa
  una volta sola per variante, sezione 8);
* rifiuta una variante i cui indicatori non sono causali;
* conta i trade con ``conta_trade`` sulle regole esatte di ``varianti.VARIANTI[id]``;
* sotto il minimo di costruzione scrive uno ``scarto`` (nessun budget); altrimenti la
  ``registrazione`` con ``variante_n`` progressivo.
"""
import json
import sys
from pathlib import Path

from research.campagne.BCHUSDT.codice import comune, registra, varianti


def voci_log():
    if not registra.LOG.exists():
        return []
    return [json.loads(r) for r in registra.LOG.read_text(encoding="utf-8").splitlines() if r.strip()]


def main():
    contenuto = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    for voce in (contenuto if isinstance(contenuto, list) else [contenuto]):
        log = voci_log()
        vid = voce["id"]
        if any(v.get("id") == vid and v["tipo"] in ("registrazione", "scarto") for v in log):
            print(vid, "gia' registrata o scartata: non si conta di nuovo")
            continue
        v = varianti.VARIANTI[vid]()
        serie = comune.carica(v.tf, "costruzione")
        diff = comune.verifica_causalita(v, serie)
        if diff:
            print(vid, "NON CAUSALE:", diff[:5])
            continue
        conteggio = comune.conta(v)
        n = conteggio["trade"]
        voce = dict(voce)
        voce["trade_stimati"] = n
        voce["conta_trade"] = conteggio
        if n < comune.TRADE_MINIMI["costruzione"]:
            voce["tipo"] = "scarto"
            voce["motivo"] = f"trade stimati {n} sotto il minimo di costruzione ({comune.TRADE_MINIMI['costruzione']})"
            voce.pop("variante_n", None)
        else:
            voce["tipo"] = "registrazione"
            voce["tipo_test"] = "variante"
            voce["variante_n"] = 1 + sum(1 for x in log if x["tipo"] == "registrazione"
                                         and x.get("tipo_test") == "variante")
        scritta = registra.aggiungi(voce)
        print(scritta["data"], vid, scritta["tipo"], "trade stimati", n, "variante_n", scritta.get("variante_n"))


if __name__ == "__main__":
    main()
