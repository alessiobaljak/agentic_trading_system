"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che guarda di proposito la barra
dopo deve battere nettamente il caso e crollare con il ritardo di una barra. Uso: python controllo_positivo.py prima|dopo"""
import json
import sys
from dataclasses import replace

from comune import PARAMETRI, aggiungi_log
import quadro
import varianti as V

if sys.argv[1] == "prima":
    aggiungi_log({"id": "FTMUSDT-N-CONTROLLO", "tipo": "nota",
                  "testo": "Controllo positivo degli strumenti, PRIMA: strategia che guarda di proposito la barra dopo "
                           "(long se close(i+1) > open(i+1)), 1h, stop 2 ATR(24), uscita a tempo dopo 1 barra, con le "
                           "baseline (a) e (b) del quadro comune. Atteso: netta contro (a) e (b); col ritardo di una barra "
                           "il t contro la (b) ricalcolata crolla sotto la meta' (vicino a zero). Non e' una variante, non "
                           "consuma budget."})
else:
    var = V.controllo_positivo()
    out = quadro.test_costruzione(var)
    out_r = quadro.test_costruzione(var, replace(PARAMETRI, ritardo_barre=1))
    sintesi = {
        "senza_ritardo": {"r_medio": out["metriche"]["r_medio"], "trade": out["metriche"]["trade"],
                          "t_a": out["baseline_a"].get("t"), "netta_a": out["baseline_a"].get("netta"),
                          "t_b": out["baseline_b"].get("t"), "netta_b": out["baseline_b"].get("netta")},
        "ritardo_1": {"r_medio": out_r["metriche"]["r_medio"], "trade": out_r["metriche"]["trade"],
                      "t_b": out_r["baseline_b"].get("t"), "netta_b": out_r["baseline_b"].get("netta")},
    }
    passa = bool(sintesi["senza_ritardo"]["netta_a"] and sintesi["senza_ritardo"]["netta_b"]
                 and sintesi["ritardo_1"]["t_b"] < 0.5 * sintesi["senza_ritardo"]["t_b"])
    aggiungi_log({"id": "FTMUSDT-N-CONTROLLO-ESITO", "tipo": "nota", "testo": "Controllo positivo degli strumenti, DOPO.",
                  "esito": sintesi, "passa": passa})
    print(json.dumps(sintesi, indent=1), "passa:", passa)
