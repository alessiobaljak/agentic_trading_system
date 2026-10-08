"""Stima, registrazione e test di una o piu' varianti, nell'ordine del protocollo.

Per ogni variante: (1) conta_trade una volta sola (se la registrazione o lo scarto c'e'
gia' nel log, non si riconta); (2) sotto 70 trade -> voce `scarto`; altrimenti voce
`registrazione` scritta PRIMA del test; (3) test sui dati di costruzione; (4) voce
`risultato`. Uso: python prova.py V01 V02 ...   (in serie: gli id del log sono progressivi)
"""
import sys

import quadro
import varianti
from comune import SIMBOLO, aggiungi_log, voci_log
from registro import CRITERIO, REGISTRO

MINIMO = 70


def _gia(vid, tipi):
    return [v for v in voci_log() if v.get("id") == f"{SIMBOLO}-{vid}" and v.get("tipo") in tipi]


def _variante_n():
    return sum(1 for v in voci_log() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante") + 1


def prova(vid, ritocco_di=None, famiglia=None):
    v = varianti.TUTTE[vid]()
    meta = REGISTRO[vid]
    lid = f"{SIMBOLO}-{vid}"
    if _gia(vid, ("risultato", "scarto")):
        print(vid, "gia' fatta")
        return
    reg = _gia(vid, ("registrazione",))
    if not reg:
        conteggio = quadro.conta(v)
        n = conteggio["trade"]
        if n < MINIMO:
            aggiungi_log({"id": lid, "tipo": "scarto", "idea": meta["idea"], "fonte": meta["fonte"],
                          "meccanismo": meta["meccanismo"], "timeframe": v.tf, "direzione": v.direzione,
                          "parametri": meta["parametri"], "trade_stimati": n, "conteggio": conteggio,
                          "motivo": f"sotto i trade minimi di costruzione ({n} < {MINIMO}): non si testa, non consuma budget"})
            print(vid, "scarto", n)
            return
        aggiungi_log({"id": lid, "tipo": "registrazione", "tipo_test": "variante", "idea": meta["idea"],
                      "famiglia": famiglia or lid, "ritocco_di": ritocco_di, "fonte": meta["fonte"],
                      "meccanismo": meta["meccanismo"], "timeframe": v.tf, "direzione": v.direzione,
                      "parametri": meta["parametri"], "periodo": "costruzione",
                      "previsione": meta["previsione"]["testo"], "criterio_successo": CRITERIO,
                      "trade_stimati": n, "conteggio": conteggio, "variante_n": _variante_n()})
    else:
        n = reg[-1]["trade_stimati"]
    esito = quadro.valuta_costruzione(v)
    m = esito["metriche"]
    p = meta["previsione"]
    netta_b = bool(esito.get("baseline_b", {}).get("netta"))
    corretta = (p["r_min"] <= m["r_medio"] <= p["r_max"]) and (netta_b == p["netta_b"])
    commento = (f"trade {m['trade']} (stimati {n}); R medio {m['r_medio']}; "
                f"t contro (a) {esito.get('baseline_a', {}).get('t')}, contro (b) {esito.get('baseline_b', {}).get('t')}; "
                f"candidato: {'si' if esito.get('candidato') else 'no'}")
    voce = {"id": lid, "tipo": "risultato", **esito, "previsione_corretta": corretta, "commento": commento}
    aggiungi_log(voce)
    print(vid, commento, flush=True)


if __name__ == "__main__":
    for vid in sys.argv[1:]:
        prova(vid)
