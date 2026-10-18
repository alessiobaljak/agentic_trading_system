"""Programma 5, fase 4: l'esplorazione del libro degli ordini (E-201, piano.md)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti.esplora_fase2 import pannello, promossa, riassumi_fase2, sfoltisci
from research.programma5.strumenti.libro import libro


def pct(x: pd.Series) -> np.ndarray:
    return x.rolling(720, min_periods=500).rank(pct=True).to_numpy()


def celle(b: pd.DataFrame, lb: pd.DataFrame):
    uno = np.ones(len(b))
    L = lb.reindex(b.index)
    z1, z4 = b["z1"].to_numpy(), b["z4"].to_numpy()
    for k in (1, 2, 5):
        p = pct(L[f"imb{k}_media"])
        for h in (1, 4, 12, 24):
            yield f"D1 k{k} acquisti h{h}", "D1", h, h, p >= 0.95, uno
            yield f"D1 k{k} vendite h{h}", "D1", h, h, p <= 0.05, -uno
    for k in (1, 5):
        im = L[f"imb{k}_media"]
        for w in (1, 4):
            p = pct(im - im.shift(w))
            for h in (1, 4, 24):
                yield f"D2 k{k} w{w} acquisti h{h}", "D2", h, max(w, h), p >= 0.95, uno
                yield f"D2 k{k} w{w} vendite h{h}", "D2", h, max(w, h), p <= 0.05, -uno
    rap = (L["liq1_media"] / L["liq1_media"].rolling(720, min_periods=500).median().shift(1)).to_numpy()
    for nome, cond in (("sottile", rap <= 0.4), ("spesso", rap >= 2.5)):
        for h in (4, 12, 24):
            yield f"D3 {nome} su h{h}", "D3", h, h, cond & (z1 >= 2), uno
            yield f"D3 {nome} giu h{h}", "D3", h, h, cond & (z1 <= -2), -uno
    p2 = pct(L["imb2_media"])
    for h in (4, 24):
        yield f"D4 su contro libro h{h}", "D4", h, h, (z4 >= 2) & (p2 <= 0.10), uno
        yield f"D4 su con libro h{h}", "D4", h, h, (z4 >= 2) & (p2 >= 0.90), uno
        yield f"D4 giu contro libro h{h}", "D4", h, h, (z4 <= -2) & (p2 >= 0.90), -uno
        yield f"D4 giu con libro h{h}", "D4", h, h, (z4 <= -2) & (p2 <= 0.10), -uno
    p24 = pct(L["imb2_media"].rolling(24, min_periods=20).mean())
    for h in (24, 72):
        yield f"D5 acquisti h{h}", "D5", h, h, p24 >= 0.95, uno
        yield f"D5 vendite h{h}", "D5", h, h, p24 <= 0.05, -uno


def esplora(monete, periodo: str, log=print) -> dict:
    ore, P, A = pannello(monete, periodo)
    raccolte: dict = {}
    for s in monete:
        b = P[s]
        lb = libro(s, periodo)
        if lb.empty:
            continue
        nel = b["periodo"].to_numpy(bool)
        mese = pd.to_datetime(b.index.to_numpy() * 3600, unit="s").to_period("M").astype(str).to_numpy()
        basi = {}
        for nome, fam, h, pausa, cond, d in celle(b, lb):
            a = A[h][s]
            if h not in basi:
                ok = nel & np.isfinite(a)
                basi[h] = pd.Series(mese).map(pd.Series(a[ok]).groupby(mese[ok]).mean()).to_numpy(float)
            ev = sfoltisci(np.asarray(cond, bool) & nel & np.isfinite(a), pausa)
            raccolte.setdefault(nome, [fam, []])[1].append(pd.DataFrame(
                {"s": s, "minuto": b.index.to_numpy()[ev] * 60, "v": d[ev] * a[ev], "x": d[ev] * (a[ev] - basi[h][ev])}))
        log(f"[libro {periodo}] {s}")
    out = {}
    for nome, (fam, parti) in raccolte.items():
        parti = [p for p in parti if len(p)]
        righe = pd.concat(parti, ignore_index=True) if parti else pd.DataFrame(columns=["s", "minuto", "v", "x"])
        r = riassumi_fase2(righe)
        r["famiglia"] = fam
        r["promossa"] = bool(r["trade"]) and promossa(fam, r)
        out[nome] = r
    return out
