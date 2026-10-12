"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che legge DI PROPOSITO
la barra successiva (lookahead dichiarato) deve battere nettamente il caso e crollare con il
ritardo di una barra. Non e' una variante: si registra come nota, prima e dopo.

Regola: 1h, long; alla chiusura della barra i entra se la barra i+1 (futura!) chiude sopra la
sua apertura; stop al 3% sotto il close della barra i, nessun target; esce all'apertura della
barra dopo quella d'ingresso (una barra in posizione).

Uso: python controllo_positivo.py prima | dopo
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

import quadro  # noqa: E402
from aggiungi_log import aggiungi  # noqa: E402
from indicatori import serie  # noqa: E402
from research.src.motore import Segnale  # noqa: E402

USCITA = quadro.CARTELLA_DATI / "risultati" / "controllo_positivo.json"


class Lookahead(quadro.Variante):
    id = "controllo-positivo"
    tf = "1h"
    direzione = "long"

    def prepara(self, candele):
        s = serie(candele)
        futuro_su = np.zeros(len(candele), dtype=bool)
        futuro_su[:-1] = s["close"][1:] > s["open"][1:]  # LOOKAHEAD VOLUTO
        return {"close": s["close"], "futuro_su": futuro_su}

    def entra(self, i, ind):
        return bool(ind["futuro_su"][i])

    def segnale(self, i, ind):
        return Segnale("long", stop=ind["close"][i] * 0.97)

    def esci(self, i, ind, pos):
        return quadro.tempo_in_barre(i, ind, pos) >= 1


if __name__ == "__main__":
    fase = sys.argv[1]
    if fase == "prima":
        aggiungi([{"id": "LTCUSDT-N007", "tipo": "nota", "argomento": "controllo positivo degli strumenti: registrazione",
                   "regola": "1h long; entra alla chiusura della barra i se la barra i+1 (futura) chiude sopra l'apertura; stop 3% sotto il close di i; nessun target; esce all'apertura della barra dopo quella d'ingresso",
                   "previsione": "batte nettamente la (a) e la (b) con t molto alto (oltre 10); con il ritardo di una barra il t contro la (b) crolla vicino a zero",
                   "criterio": "se non batte nettamente la (b) senza ritardo, o se col ritardo il t resta oltre la meta' di quello senza ritardo, gli strumenti non funzionano e nessun risultato della campagna vale"}])
    elif fase == "dopo":
        v = Lookahead()
        senza = quadro.giudica(v)
        con = quadro.giudica(v, ritardo_barre=1)
        USCITA.parent.mkdir(parents=True, exist_ok=True)
        USCITA.write_text(json.dumps({"senza_ritardo": senza, "ritardo_1": con}, default=str, indent=1), encoding="utf-8")
        sintesi = {}
        for nome, r in (("senza_ritardo", senza), ("ritardo_1", con)):
            sintesi[nome] = {"trade": r["metriche"]["trade"], "r_medio": r["metriche"]["r_medio"],
                             "t_a": r["baseline_a"].get("t"), "netta_a": r["baseline_a"].get("netta"),
                             "media_b": r["baseline_b"].get("media"), "t_b": r["baseline_b"].get("t"),
                             "netta_b": r["baseline_b"].get("netta"), "percentile_caso": r["percentile_caso"]}
        t0, t1 = sintesi["senza_ritardo"]["t_b"], sintesi["ritardo_1"]["t_b"]
        superato = bool(sintesi["senza_ritardo"]["netta_b"]) and t1 is not None and t0 is not None and t1 < 0.5 * t0
        aggiungi([{"id": "LTCUSDT-N008", "tipo": "nota", "argomento": "controllo positivo degli strumenti: risultato",
                   "rimanda_a": "LTCUSDT-N007", "sintesi": sintesi, "superato": superato}])
        print(json.dumps(sintesi, indent=1), "superato:", superato)
