"""Programma 5, fase 2: i fattori fra monete (E-114, piano.md), con il portafoglio long-short di ``esplora_fase2``."""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti.esplora_fase2 import (BTC, classifica, decisioni, pannello, promossa,
                                                          riassumi_fase2)


def caratteri(P: dict, monete) -> dict:
    out = {"G7": {}, "G8": {}, "G9": {}, "G10": {}, "G11": {}, "G12": {}}
    m = dict(window=720, min_periods=500)
    for s in monete:
        b = P[s]
        out["G7"][s] = b["sigma"].to_numpy()
        if s != BTC:
            out["G8"][s] = b["beta"].to_numpy()
        r24 = b["lc"] - b["lc"].shift(24)
        out["G9"][s] = r24.rolling(**m).max().to_numpy()
        qv = (b["volume"] * b["close"]).where(lambda x: x > 0)
        out["G10"][s] = (b["r1"].abs() / qv).rolling(**m).mean().to_numpy()
        out["G11"][s] = (b["lc"] - np.log(b["high"].rolling(**m).max())).to_numpy()
        out["G12"][s] = b["r1"].rolling(**m).skew().to_numpy()
    return out


def esplora(monete, periodo: str, log=print, minimo: int = 40, quanti: int = 10, monete_min: int = 20) -> dict:
    ore, P, A = pannello(monete, periodo)
    nel = P[BTC]["periodo"].to_numpy()
    car = caratteri(P, monete)
    out = {}
    for fam, punteggio in car.items():
        for h in (24, 72):
            dec = decisioni(ore, nel, h)
            righe, contributi = classifica(ore, punteggio, {s: A[h][s] for s in punteggio}, dec, minimo, quanti)
            r = riassumi_fase2(righe, contributi)
            r["famiglia"] = fam
            r["promossa"] = bool(r["trade"]) and promossa(fam, r, monete_min=monete_min)
            out[f"{fam} h{h}"] = r
        log(f"[fattori {periodo}] {fam}")
    return out
