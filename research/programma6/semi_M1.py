"""Programma 6, controllo descrittivo (non conta come prova, idea 8 della coda di `research/REGISTRO.md`): quanto del
risultato di M1 dipende dal seme del modello? Gli alberi di M1 con early stopping tengono da parte il 10% delle righe a caso
quando le righe sono piu' di 10.000: il seme cambia quali. Stessa regola di `QUATTORDICESIMA.md`, semi 1-5 oltre al 2026,
sugli stessi dati della prova (senza le correzioni del 20 ottobre, per confrontare con il numero della prova).

Uso: python3 -m research.programma6.semi_M1
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import terza as te

QUI = Path(__file__).parent
SEMI = (2026, 1, 2, 3, 4, 5)


def esegui(log=print) -> dict:
    from sklearn.ensemble import HistGradientBoostingRegressor
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None)
    lun_idx = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun_idx)
    X, _, Y = q.tabella_settimanale(pan, ps, ps["U"])
    originale = q._modello
    out = {}
    try:
        for seme in SEMI:
            q._modello = lambda tipo, s=seme: HistGradientBoostingRegressor(
                max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=200, l2_regularization=1.0,
                random_state=s)
            P, _ = q.previsioni("M1", X, Y, ps["U"], ps["lunedi"], 6, lambda x: None)
            ct = np.where(np.isfinite(sig), P, np.nan)
            Wt = te.pesi_portafoglio(ct, ps["U"], np.nan_to_num(1.0 / sig), True)
            df = te.conto(Wt, ps["R"], ps["F"], sc.costi_moneta(ps["simboli"]))
            df.index = ps["lunedi"]
            d = df[df.index >= q.INIZIO]["netto"]
            out[str(seme)] = {"sharpe": float(d.mean() / d.std(ddof=1) * math.sqrt(52)), "annuo": float(d.mean() * 52)}
            log(f"[semi] {seme}: {out[str(seme)]}")
    finally:
        q._modello = originale
    v = np.array([x["sharpe"] for x in out.values()])
    out["riassunto"] = {"media": float(v.mean()), "minimo": float(v.min()), "massimo": float(v.max()),
                        "ultimo_giorno": sc.data(pan["t0"] + pan["close"].shape[0] - 1)}
    (QUI / "semi_M1.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SEMI FINITO", flush=True)
