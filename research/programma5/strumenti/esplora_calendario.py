"""Programma 5, fase 2: sessioni, fine settimana e prezzo medio (E-103, piano.md)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti.esplora_fase2 import (BTC, avanti, pannello, promossa, riassumi_fase2,
                                                          sfoltisci)

SESSIONI = {"asia": (0, 8), "europa": (8, 14), "america": (14, 21), "sera": (21, 24)}
DOPO = {"asia": "europa", "europa": "america", "america": "sera", "sera": "asia"}


def celle(b: pd.DataFrame):
    ora = b.index.to_numpy()
    fine = (ora + 1) % 24                     # l'ora UTC in cui si decide (fine della barra)
    giorno = pd.to_datetime((ora + 1) * 3600, unit="s")
    lc = b["lc"]
    sg = b["sigma"]
    uno = np.ones(len(b))

    def zeta(w):
        return ((lc - lc.shift(w)) / (sg.shift(w) * np.sqrt(w))).to_numpy()

    lunedi = (fine == 0) & (giorno.dayofweek.to_numpy() == 0)
    z48 = zeta(48)
    for k in (1, 1.5, 2):
        for h in (24, 72):
            yield f"W1 k{k} su h{h}", "W1", h, h, lunedi & (z48 >= k), uno
            yield f"W1 k{k} giu h{h}", "W1", h, h, lunedi & (z48 <= -k), -uno
    for nome, (a, z) in SESSIONI.items():
        lung = z - a
        dopo = DOPO[nome]
        h = SESSIONI[dopo][1] - SESSIONI[dopo][0]
        zz = zeta(lung)
        quando = fine == (z % 24)
        for k in (1, 2):
            yield f"W2 {nome}->{dopo} k{k} su", "W2", h, h, quando & (zz >= k), uno
            yield f"W2 {nome}->{dopo} k{k} giu", "W2", h, h, quando & (zz <= -k), -uno
    z20 = zeta(20)
    z1 = zeta(1)
    for k in (1, 2):
        yield f"W3 giornata k{k} su", "W3", 4, 4, (fine == 20) & (z20 >= k), uno
        yield f"W3 giornata k{k} giu", "W3", 4, 4, (fine == 20) & (z20 <= -k), -uno
        yield f"W3 prima ora americana k{k} su", "W3", 6, 6, (fine == 15) & (z1 >= k), uno
        yield f"W3 prima ora americana k{k} giu", "W3", 6, 6, (fine == 15) & (z1 <= -k), -uno
    pv = (b["close"] * b["volume"]).rolling(24).sum() / b["volume"].rolling(24).sum()
    dev = ((lc - np.log(pv)) / (sg * np.sqrt(24))).to_numpy()
    for k in (1.5, 2.5):
        for h in (4, 24):
            yield f"W4 k{k} sopra h{h}", "W4", h, h, dev >= k, uno
            yield f"W4 k{k} sotto h{h}", "W4", h, h, dev <= -k, -uno
    domani = giorno + pd.Timedelta(days=1)
    ultimo = (fine == 0) & (domani.month.to_numpy() != giorno.month.to_numpy())
    yield "W5 fine mese", "W5", 96, 96, ultimo, uno
    yield "W5 giorno 15", "W5", 96, 96, (fine == 0) & (giorno.day.to_numpy() == 15), uno


def esplora(monete, periodo: str, log=print, monete_min: int = 10) -> dict:
    ore, P, A = pannello(monete, periodo)
    raccolte: dict = {}
    for s in monete:
        b = P[s]
        nel = b["periodo"].to_numpy(bool)
        mese = pd.to_datetime(b.index.to_numpy() * 3600, unit="s").to_period("M").astype(str).to_numpy()
        basi = {}
        for nome, fam, h, pausa, cond, d in celle(b):
            if h not in A:
                A[h] = {x: avanti(P[x], h) for x in monete}
            a = A[h][s]
            if h not in basi:
                ok = nel & np.isfinite(a)
                basi[h] = pd.Series(mese).map(pd.Series(a[ok]).groupby(mese[ok]).mean()).to_numpy(float)
            ev = sfoltisci(np.asarray(cond, bool) & nel & np.isfinite(a), pausa)
            raccolte.setdefault(nome, [fam, []])[1].append(pd.DataFrame(
                {"s": s, "minuto": b.index.to_numpy()[ev] * 60, "v": d[ev] * a[ev],
                 "x": d[ev] * (a[ev] - basi[h][ev])}))
        log(f"[calendario {periodo}] {s}")
    out = {}
    for nome, (fam, parti) in raccolte.items():
        parti = [p for p in parti if len(p)]
        righe = pd.concat(parti, ignore_index=True) if parti else pd.DataFrame(columns=["s", "minuto", "v", "x"])
        r = riassumi_fase2(righe)
        r["famiglia"] = fam
        r["promossa"] = bool(r["trade"]) and promossa(fam, r, monete_min=monete_min)
        out[nome] = r
    return out
