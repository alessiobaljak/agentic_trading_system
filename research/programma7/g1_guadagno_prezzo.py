"""Migliorare G1, voce 7 (`MIGLIORARE_G1.md`): da dove viene il guadagno di prezzo di G1. Solo una misura, nessuna regola nuova.

Per ogni giorno, con i pesi di G1 (`revisione_g1n/nucleo.py`) e il rendimento da un'apertura all'altra:
* il guadagno di prezzo del lato comprato (somma dei pesi positivi per il rendimento) e del lato venduto (pesi negativi);
* gli stessi due rispetto alla media dell'universo del giorno (i due lati valgono 1 e 1, quindi la media del mercato si annulla):
  quanto le monete comprate fanno meglio della media, e quanto le vendute fanno peggio;
* per fascia di grandezza: il posto della moneta nell'universo del lunedì, per volume mediano dei 30 giorni (1-10, 11-50, 51-100).

Due periodi: il passato della prova (dal 4 gennaio 2021 al 4 ottobre 2026) e i giorni del paper (dal 24 ottobre 2026 all'ultimo giorno
del pannello). Il funding non c'è: è un'altra voce (3), e nel pannello di ottobre-novembre è stimato.

Uso: python3 -m research.programma7.g1_guadagno_prezzo
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as nu

QUI = Path(__file__).parent
OUT = QUI / "risultati_g1_guadagno_prezzo.json"
FASCE = ((1, 10), (11, 50), (51, 100))


def posti_universo(pan: dict, idx: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Il posto (1 = il volume mediano piu' alto) di ogni moneta nell'universo del suo lunedi'; 0 fuori dall'universo."""
    V = pan["quote_volume"]
    giorni = idx + pan["t0"]
    lun = giorni - ((giorni + 3) % 7) - pan["t0"]
    out = np.zeros(U.shape, dtype=np.int64)
    cache = {}
    for k, m in enumerate(lun):
        if m not in cache:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                med = np.nan_to_num(np.nanmedian(V[max(0, m - 30):m], axis=0), nan=0.0)
            cache[m] = med
        dentro = np.flatnonzero(U[k])
        ordine = dentro[np.argsort(-cache[m][dentro], kind="stable")]
        out[k, ordine] = np.arange(1, len(ordine) + 1)
    return out


def scomponi(W, R, U, posto, giorni) -> dict:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        media = np.nanmean(np.where(U, R, np.nan), axis=1)
    media = np.nan_to_num(media)
    L, S = np.where(W > 0, W, 0.0), np.where(W < 0, W, 0.0)
    d = pd.DataFrame({
        "totale": (W * R).sum(1),
        "comprato": (L * R).sum(1), "venduto": (S * R).sum(1),
        "comprato_sopra_la_media": (L * (R - media[:, None])).sum(1),
        "venduto_sotto_la_media": (S * (R - media[:, None])).sum(1),
        "mercato": media,
    }, index=giorni)
    for a, b in FASCE:
        m = (posto >= a) & (posto <= b)
        d[f"comprato_{a}_{b}"] = (np.where(m, L, 0.0) * R).sum(1)
        d[f"venduto_{a}_{b}"] = (np.where(m, S, 0.0) * R).sum(1)
        d[f"comprato_sopra_la_media_{a}_{b}"] = (np.where(m, L, 0.0) * (R - media[:, None])).sum(1)
        d[f"venduto_sotto_la_media_{a}_{b}"] = (np.where(m, S, 0.0) * (R - media[:, None])).sum(1)
        d[f"peso_comprato_{a}_{b}"] = np.where(m, L, 0.0).sum(1)
        d[f"peso_venduto_{a}_{b}"] = -np.where(m, S, 0.0).sum(1)
    return d


def riassunto(d: pd.DataFrame, annuo: bool) -> dict:
    pesi = [c for c in d.columns if c.startswith("peso_")]
    somme = [c for c in d.columns if c not in pesi]
    k = 365 / len(d) if annuo else 1.0
    out = {c: float(d[c].sum() * k) for c in somme}
    out.update({c: float(d[c].mean()) for c in pesi})
    out["giorni"] = int(len(d))
    return out


def main():
    pan = sc.pannello()
    ultimo = pan["t0"] + pan["close"].shape[0] - 1
    periodi = {"passato": (sc.giorno(2021, 1, 4), sc.giorno(2026, 10, 5), True),
               "paper": (sc.giorno(2026, 10, 24), ultimo + 1, False)}
    out = {"ultimo_giorno_del_pannello": sc.data(int(ultimo))}
    for nome, (da, a, annuo) in periodi.items():
        giorni = np.arange(da, a, dtype=np.int64)
        idx = giorni - pan["t0"]
        R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]
        U = nu.universo_giorni(pan, idx)
        W, _, _ = nu.pesi(pan, idx, U, fisso=(1.0, 1.0))
        posto = posti_universo(pan, idx, U)
        d = scomponi(W, R, U, posto, giorni)
        out[nome] = {"tutto": riassunto(d, annuo), "in": "all'anno" if annuo else "somma dei giorni"}
        if annuo:
            anni = pd.to_datetime(d.index.to_numpy() * 86400, unit="s").year
            out[nome]["per_anno"] = {int(y): riassunto(d[anni == y], True) for y in sorted(set(anni))}
        else:
            out[nome]["giorni"] = {sc.data(int(g)): {c: round(float(v), 5) for c, v in r.items() if not c.startswith("peso_")}
                                   for g, r in d.iterrows()}
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    for nome in periodi:
        t = out[nome]["tutto"]
        print(nome, out[nome]["in"], {k: round(v, 4) for k, v in t.items()})


if __name__ == "__main__":
    main()
