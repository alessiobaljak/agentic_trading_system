"""Programma 6: quanto e' solida F5 (VENTIQUATTRESIMA.md)? Controlli descrittivi, non una prova e non cambiano F5: le due
meta' delle 100 monete, i due lati, costi doppi e tripli, tetto del 10% per moneta, senza le cinque monete piu' pesanti,
il cambio il giovedi' invece del lunedi'. Scrive `robustezza_F5.json` e una sezione in `robustezza_F2.md`.

Uso: python3 -m research.programma6.robustezza_F5
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
CINQUE = ("BTCUSDT", "ETHUSDT", "BNBUSDT", "TRXUSDT", "XMRUSDT")


def _f5(pan: dict, ps: dict, tetto: float = 0.0, senza=()) -> pd.DataFrame:
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    ct = np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan)
    U = ps["U"].copy()
    for s in senza:
        U[:, pan["simboli"].index(s)] = False
    W = vq.pesi_banda(ct, U, sig)
    if tetto:
        for k in range(W.shape[0]):
            for segno in (1, -1):
                lato = np.flatnonzero(np.sign(W[k]) == segno)
                if len(lato):
                    w = np.abs(W[k, lato])
                    for _ in range(20):          # tetto e ridistribuzione sulle altre
                        sopra = w > tetto
                        if not sopra.any():
                            break
                        resto = w[sopra].sum() - tetto * sopra.sum()
                        w[sopra] = tetto
                        libere = ~sopra & (w < tetto)
                        w[libere] += resto * w[libere] / w[libere].sum() if libere.any() else 0
                    W[k, lato] = segno * w / w.sum()
    df = te.conto(W, ps["R"], ps["F"], sc.costi_moneta(ps["simboli"]))
    df.index = ps["lunedi"]
    return df


def _numeri(x: pd.Series) -> dict:
    d = x[x.index >= se.INIZIO]
    anni = pd.to_datetime(d.index.to_numpy() * 86400, unit="s").year
    return {"settimane": int(len(d)), "annuo": float(d.mean() * 52), "sharpe": float(d.mean() / d.std(ddof=1) * math.sqrt(52)),
            "anni_positivi": f"{sum(1 for a in sorted(set(anni)) if d[anni == a].mean() > 0)}/{len(set(anni))}"}


def esegui() -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    base = _f5(pan, ps)
    out = {"F5 come da regole": _numeri(base["netto"])}
    out["solo il lato long (netto)"] = _numeri(base["long"])
    out["solo il lato short (netto)"] = _numeri(base["short"])
    out["costi doppi"] = _numeri(base["netto_doppio"])
    out["costi tripli"] = _numeri(base["lordo"] - 3 * base["spese"] - base["funding"])
    for nome, da, a in (("solo le prime 50 monete", 0, 50), ("solo dalla 51ª alla 100ª", 50, 100)):
        out[nome] = _numeri(_f5(pan, te.pannello_settimane(pan, log=lambda x: None, da=da, a=a, indicatori_si=False))["netto"])
    out["tetto del 10% per moneta"] = _numeri(_f5(pan, ps, tetto=0.10)["netto"])
    out["senza BTC, ETH, BNB, TRX, XMR"] = _numeri(_f5(pan, ps, senza=CINQUE)["netto"])
    # il cambio il giovedi': le settimane che partono il giovedi' (giorno dall'epoca multiplo di 7)
    originale = te.settimane
    try:
        def giovedi(pan_):
            g = np.arange(pan_["close"].shape[0]) + pan_["t0"]
            t = np.flatnonzero(g % 7 == 0)
            return t[(t >= 1) & (t + 7 <= len(g))]
        te.settimane = giovedi
        psg = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    finally:
        te.settimane = originale
    out["cambio il giovedì"] = _numeri(_f5(pan, psg)["netto"])
    out["ultimo_giorno"] = sc.data(pan["t0"] + pan["close"].shape[0] - 1)
    (QUI / "robustezza_F5.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    for k, v in esegui().items():
        print(k, v, flush=True)
