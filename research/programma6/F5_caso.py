"""Programma 6, controllo descrittivo di F5 (VENTIQUATTRESIMA.md) contro il caso: lo stesso portafoglio con la banda, ma il
segnale di ogni moneta dato a un'altra moneta (una permutazione fissa delle monete per tutta la storia, che tiene la
persistenza del segnale e rompe il legame con i rendimenti), 200 volte, seme 2026. Se F5 viene dal segnale, il caso fa
intorno a zero. Uso: python3 -m research.programma6.F5_caso
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
N = 200


def sharpe(df) -> float:
    d = df[df.index >= se.INIZIO]["netto"]
    return float(d.mean() / d.std(ddof=1) * math.sqrt(52))


def esegui() -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    ct = np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan)
    costo = sc.costi_moneta(ps["simboli"])
    rng = np.random.default_rng(2026)
    vero = sharpe(_conto(ct, ps, sig, costo))
    casi = []
    for _ in range(N):
        perm = rng.permutation(ct.shape[1])
        casi.append(sharpe(_conto(ct[:, perm], ps, sig, costo)))
    casi = np.array(casi)
    out = {"F5": vero, "caso_media": float(casi.mean()), "caso_massimo": float(casi.max()),
           "caso_95": float(np.percentile(casi, 95)), "sopra_F5": int((casi >= vero).sum()), "ripetizioni": N}
    (QUI / "F5_caso.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


def _conto(ct, ps, sig, costo):
    df = te.conto(vq.pesi_banda(ct, ps["U"], sig), ps["R"], ps["F"], costo)
    df.index = ps["lunedi"]
    return df


if __name__ == "__main__":
    print(esegui(), flush=True)
