"""Fase 4: verifiche di un candidato sui dati di costruzione (protocollo, Fase 4).

Uso: python -m research.campagne.GALAUSDT.codice.fase4 <ID>
Ogni verifica si registra nel log PRIMA di eseguirla (tipo_test verifica, verifica_di) e il suo
risultato si scrive dopo, in una voce separata. Criteri: quelli scritti nel protocollo.
"""

import copy
import json
import math
import sys

import numpy as np

from research.campagne.GALAUSDT.codice import comune, registro
from research.campagne.GALAUSDT.codice.catalogo import CATALOGO, crea_variante

TRADE_MINIMI = 70


def _registra(vid, nome, descrizione, criterio, trade_stimati=None, parametri=None):
    voce = {"id": f"{vid}-V-{nome}", "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": vid,
            "periodo": "costruzione", "verifica": nome, "descrizione": descrizione, "criterio_successo": criterio}
    if trade_stimati is not None:
        voce["trade_stimati"] = trade_stimati
    if parametri is not None:
        voce["parametri"] = parametri
    registro.aggiungi(voce)


def _risultato(vid, nome, dati):
    registro.aggiungi(dict({"id": f"{vid}-V-{nome}", "tipo": "risultato", "periodo": "costruzione"}, **dati))


def _sintesi(r):
    m, b = r["metriche"], r.get("baseline_b", {})
    return {"trade": m.get("trade"), "r_medio": m.get("r_medio"), "t_b": b.get("t"), "netta_b": b.get("netta"),
            "valutabile_b": b.get("valutabile"), "media_b": b.get("media"),
            "r_medio_per_anno": m.get("r_medio_per_anno"), "trade_per_anno": m.get("trade_per_anno"),
            "r_medio_senza_3_migliori": m.get("r_medio_senza_3_migliori"),
            "n_violazioni_liquidazione": m.get("n_violazioni_liquidazione"), "n_ridotti": m.get("n_ridotti")}


def spostati(valore):
    if isinstance(valore, bool):
        return []
    if isinstance(valore, int):
        giu = math.floor(0.8 * valore + 0.5)
        su = math.floor(1.2 * valore + 0.5)
        if giu == valore:
            giu = valore - 1
        if su == valore:
            su = valore + 1
        return [giu, su]
    return [0.8 * valore, 1.2 * valore]


def main(vid):
    base = crea_variante(vid)
    ris0 = comune.valuta(base, "costruzione")
    t0 = ris0["baseline_b"]["t"]
    esiti = {}

    # 1. robustezza: ogni parametro numerico +-20%, uno alla volta
    casi = []
    for k, v in base.p.items():
        if k == "k_target" and not v:
            continue  # nessun target: non e' un numero della regola
        if k == "atr_min_rel" and not v:
            continue
        for nuovo in spostati(v):
            casi.append((k, nuovo))
    risultati_rob = []
    for k, nuovo in casi:
        var = crea_variante(vid)
        var.p[k] = nuovo
        conteggio = comune.conta(var)["trade"]
        nome = f"robustezza-{k}-{nuovo:g}"
        _registra(vid, nome, f"robustezza: {k} da {base.p[k]} a {nuovo}",
                  "t contro la (b) ricalcolata positivo; conta se ha almeno 70 trade", conteggio, var.p)
        if conteggio < TRADE_MINIMI:
            _risultato(vid, nome, {"sotto_minimo": True, "trade": conteggio})
            risultati_rob.append({"caso": nome, "conta": False})
            continue
        r = comune.valuta(var, "costruzione", con_a=False)
        s = _sintesi(r)
        _risultato(vid, nome, s)
        risultati_rob.append({"caso": nome, "conta": True, "valutabile": bool(s["valutabile_b"]),
                              "t_b": s["t_b"], "netta_b": bool(s["netta_b"])})
    contano = [c for c in risultati_rob if c["conta"]]
    positivi = all(c["valutabile"] and c["t_b"] > 0 for c in contano)
    netti = sum(1 for c in contano if c["valutabile"] and c["netta_b"])
    esiti["robustezza"] = bool(len(contano) >= len(casi) / 2 and positivi and netti >= len(contano) / 2)
    esiti["robustezza_dettaglio"] = {"casi": len(casi), "contano": len(contano), "tutti_t_positivi": positivi,
                                     "netti": netti}

    # 2. timeframe adiacenti
    ordine = ["15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
    k = ordine.index(base.tf)
    adiacenti = [ordine[j] for j in (k - 1, k + 1) if 0 <= j < len(ordine)]
    tf_ok = True
    for tf in adiacenti:
        var = base.con_timeframe(tf)
        conteggio = comune.conta(var)["trade"]
        nome = f"timeframe-{tf}"
        _registra(vid, nome, f"timeframe adiacente {tf}, parametri in barre convertiti", "t contro la (b) positivo",
                  conteggio, var.p)
        if conteggio < TRADE_MINIMI:
            _risultato(vid, nome, {"sotto_minimo": True, "trade": conteggio})
            continue
        s = _sintesi(comune.valuta(var, "costruzione", con_a=False))
        _risultato(vid, nome, s)
        if not (s["valutabile_b"] and s["t_b"] > 0):
            tf_ok = False
    esiti["timeframe_adiacenti"] = tf_ok

    # 4-5. stabilita' temporale e trade estremi (dal test originale)
    m = ris0["metriche"]
    media_b = ris0["baseline_b"]["media"]
    _registra(vid, "stabilita-ed-estremi", "R per anno d'uscita e R senza i 3 trade migliori, contro la media della (b)",
              "R sopra la media (b) in piu' della meta' degli anni con almeno 10 trade; R senza i 3 migliori sopra la media (b)")
    anni = [a for a, n in m["trade_per_anno"].items() if n >= 10]
    sopra = [a for a in anni if m["r_medio_per_anno"][a] > media_b]
    esiti["stabilita_temporale"] = bool(len(sopra) > len(anni) / 2)
    esiti["trade_estremi"] = bool(m["r_medio_senza_3_migliori"] > media_b)
    _risultato(vid, "stabilita-ed-estremi", {"anni_con_10_trade": anni, "anni_sopra_b": sopra, "media_b": media_b,
                                             "r_medio_per_anno": m["r_medio_per_anno"],
                                             "r_medio_senza_3_migliori": m["r_medio_senza_3_migliori"],
                                             "stabilita_superata": esiti["stabilita_temporale"],
                                             "estremi_superata": esiti["trade_estremi"]})

    # 5. regola intra-barra opposta (si dichiara la differenza)
    _registra(vid, "intrabarra-opposta", "target prima dello stop nella stessa barra", "si dichiara la differenza")
    s = _sintesi(comune.valuta(base, "costruzione", intrabarra="target_prima", con_a=False))
    _risultato(vid, "intrabarra-opposta", dict(s, differenza_r=s["r_medio"] - m["r_medio"]))

    # 6. ritardo di una barra
    _registra(vid, "ritardo-1", "esecuzione ritardata di una barra, (b) ricalcolata col ritardo",
              "t contro la (b) positivo e almeno la meta' del t senza ritardo")
    s = _sintesi(comune.valuta(base, "costruzione", ritardo_barre=1, con_a=False))
    esiti["ritardo"] = bool(s["valutabile_b"] and s["t_b"] > 0 and s["t_b"] >= 0.5 * t0)
    _risultato(vid, "ritardo-1", dict(s, t_senza_ritardo=t0, superata=esiti["ritardo"]))

    # 7. liquidazione
    esiti["liquidazione"] = m.get("n_violazioni_liquidazione", 0) == 0

    # 8. costi doppi
    _registra(vid, "costi-doppi", "costi doppi, (b) ricalcolata a costi doppi",
              "batte nettamente la (b) a costi doppi e R medio a costi doppi positivo")
    s = _sintesi(comune.valuta(base, "costruzione", moltiplicatore_costi=2.0, con_a=False))
    esiti["costi_doppi"] = bool(s["netta_b"] and s["r_medio"] > 0)
    _risultato(vid, "costi-doppi", dict(s, superata=esiti["costi_doppi"]))

    tutte = all(v for k2, v in esiti.items() if not k2.endswith("dettaglio"))
    registro.aggiungi({"id": f"{vid}-FASE4", "tipo": "nota", "fase": "4", "verifica_di": vid,
                       "esiti": esiti, "candidato_sopravvive": tutte})
    print(json.dumps(registro._pulisci(esiti)), "sopravvive", tutte)


if __name__ == "__main__":
    main(sys.argv[1])
