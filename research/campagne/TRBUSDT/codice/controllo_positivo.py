"""Controllo positivo degli strumenti (lezioni/metodo.md): una strategia che legge DI PROPOSITO la
barra successiva deve battere nettamente il caso e crollare con il ritardo di una barra.

Long a 1h: alla chiusura della barra i, se la barra i+1 (futuro!) chiude sopra la sua apertura,
segnale long; stop a 1 ATR(14) sotto la chiusura della barra i; uscita "chiudi" alla chiusura
della barra d'ingresso. Non e' una variante e non consuma budget: si registra come nota.
"""

import json
import sys

import numpy as np

from research.src.motore import Segnale
from research.campagne.TRBUSDT.codice import banco
from research.campagne.TRBUSDT.codice import indicatori as ind


def variante():
    def prepara(candele):
        o, h, l, c, v, ts = ind.colonne(candele)
        return {"o": o, "c": c, "atr": ind.atr(h, l, c, 14), "ts": ts, "indice": {int(t): k for k, t in enumerate(ts)}}

    def condizione(ctx, i):
        if i + 1 >= len(ctx["c"]):
            return False
        return ctx["c"][i + 1] > ctx["o"][i + 1]  # LOOKAHEAD voluto

    def segnale(ctx, i):
        a = ctx["atr"][i]
        if not np.isfinite(a):
            return None
        return Segnale("long", ctx["c"][i] - a, None)

    def uscita(ctx, i, pos):
        return "chiudi" if ctx["ts"][i] >= pos.ts_entrata else None

    return banco.Variante("CONTROLLO", "1h", "long", prepara, condizione, segnale, uscita)


def main(fase):
    v = variante()
    if fase == "prima":
        print(json.dumps(banco.scrivi({
            "tipo": "nota", "argomento": "controllo positivo degli strumenti, registrazione (lezioni/metodo.md)",
            "testo": "Strategia con lookahead dichiarato: long a 1h se la barra successiva chiude sopra l'apertura, stop 1 ATR(14), uscita alla chiusura della barra d'ingresso. Previsione: batte nettamente la (a) e la (b) in costruzione con t contro la (b) molto alto (oltre 10); con il ritardo di una barra il t contro la (b) ricalcolata crolla sotto la meta' (vicino a zero). Non e' una variante: non consuma budget.",
            "trade_stimati": banco.conta(v)}), ensure_ascii=False))
        return
    senza = banco.valuta(v)
    con = banco.valuta(v, banco.parametri(ritardo_barre=1))
    esito = {"tipo": "nota", "argomento": "controllo positivo degli strumenti, esito",
             "senza_ritardo": {"trade": senza["n_trade"], "r_medio": senza["metriche"]["r_medio"],
                               "netta_a": senza["baseline_a_esito"]["netta"], "t_a": senza["baseline_a_esito"]["t"],
                               "netta_b": senza["baseline_b_esito"]["netta"], "t_b": senza["baseline_b_esito"]["t"],
                               "media_b": senza["baseline_b"]["media"]},
             "con_ritardo_1": {"trade": con["n_trade"], "r_medio": con["metriche"]["r_medio"],
                               "netta_b": con["baseline_b_esito"]["netta"], "t_b": con["baseline_b_esito"]["t"],
                               "media_b": con["baseline_b"]["media"]}}
    t0, t1 = float(senza["baseline_b_esito"]["t"]), float(con["baseline_b_esito"]["t"])
    esito["superato"] = bool(senza["baseline_b_esito"]["netta"] and senza["baseline_a_esito"]["netta"] and t1 < 0.5 * t0)
    print(json.dumps(banco.scrivi(esito), ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
