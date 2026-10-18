"""Programma 5: il calcolo delle idee decise una volta al giorno (I-004)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5


def estremi_giornalieri(valori: np.ndarray, giorni_prima: int = 90, minimo: int = 60, quota: float = 0.10) -> tuple:
    """Per ogni giorno: (alto, basso) se il valore e' sopra il quantile 1-quota (sotto il quantile quota) dei
    ``giorni_prima`` valori dei giorni prima (il giorno stesso escluso), con almeno ``minimo`` valori presenti."""
    n = len(valori)
    alto, basso = np.zeros(n, bool), np.zeros(n, bool)
    for i in range(n):
        if not np.isfinite(valori[i]):
            continue
        prima = valori[max(0, i - giorni_prima):i]
        prima = prima[np.isfinite(prima)]
        if len(prima) < minimo:
            continue
        alto[i] = valori[i] > np.quantile(prima, 1 - quota)
        basso[i] = valori[i] < np.quantile(prima, quota)
    return alto, basso


def per_moneta_i004(idea: str, varianti: dict, simbolo: str, periodo: str) -> dict:
    df = m5.minuti(simbolo, periodo, idea, storia_giorni=100)
    met = m5.metrics(simbolo, periodo, idea, storia_giorni=100)
    if df.empty or met.empty:
        return {}
    fund = m5.funding(simbolo)
    minuti = df.index.to_numpy()
    periodo_ok = df["periodo"].to_numpy()
    # una decisione al giorno: alla chiusura del minuto 00:00 UTC, con l'ultima rilevazione di orario <= 00:00
    mezzanotti = minuti[(minuti % 1440) == 0]
    mi = met.index.to_numpy()
    pos = np.searchsorted(mi, mezzanotti, "right") - 1
    recente = (pos >= 0) & ((mezzanotti - mi[np.clip(pos, 0, None)]) <= 30)
    serie = {}
    for col in ("count_long_short_ratio", "sum_toptrader_long_short_ratio"):
        v = np.where(recente, met[col].to_numpy(float)[np.clip(pos, 0, None)], np.nan)
        serie[col] = estremi_giornalieri(v)
    tutti_alto, tutti_basso = serie["count_long_short_ratio"]
    grandi_alto, grandi_basso = serie["sum_toptrader_long_short_ratio"]
    posizione = np.searchsorted(minuti, mezzanotti)
    nel = periodo_ok[posizione]
    out = {}
    for nome, v in varianti.items():
        if v["regola"] == "contro_tutti":
            lungo, corto = tutti_basso, tutti_alto
        elif v["regola"] == "con_grandi":
            lungo, corto = grandi_alto, grandi_basso
        else:   # grandi in un verso estremo, tutti i conti no
            lungo, corto = grandi_alto & ~tutti_alto, grandi_basso & ~tutti_basso
        scelti = nel & (lungo | corto) & ~(lungo & corto)
        dec = posizione[scelti].astype(np.int64)
        direz = np.where(lungo[scelti], 1, -1)
        uscita = m5.Uscita(minuti=1440)
        # dopo un ingresso, il successivo solo a trade chiuso (un giorno dopo): le decisioni sono gia' giornaliere
        t = m5.simula(df, simbolo, dec, direz, uscita, fund)
        out[nome] = (t, m5.caso(df, simbolo, t, uscita, fund) if not t.empty else t)
    return out
