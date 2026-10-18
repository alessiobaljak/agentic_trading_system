"""Programma 5: misure comuni sugli eventi (esplosioni del prezzo, interesse aperto), senza dati futuri."""
from __future__ import annotations

import numpy as np
import pandas as pd


def ritorno5(df: pd.DataFrame) -> np.ndarray:
    """ln(chiusura_t / chiusura_{t-5}); vuoto se manca uno dei 6 minuti."""
    c = df["close"].to_numpy(float)
    lc = np.log(c)
    r = np.full(len(c), np.nan)
    r[5:] = lc[5:] - lc[:-5]
    presenti = pd.Series(np.isfinite(c).astype(float)).rolling(6).sum().to_numpy()
    r[presenti < 6] = np.nan
    return r


def metro24(r5: np.ndarray) -> np.ndarray:
    """Mediana di |r5| nelle 1.440 finestre che finiscono nelle 24 ore prima del minuto (esclude il minuto stesso)."""
    return pd.Series(np.abs(r5)).rolling(1440, min_periods=1000).median().shift(1).to_numpy()


def eventi(condizione: np.ndarray, pausa: int) -> np.ndarray:
    """Le posizioni dove la condizione e' vera, con almeno ``pausa`` minuti fra un evento e il successivo."""
    scelti, ultimo = [], -10 ** 12
    for t in np.flatnonzero(condizione):
        if t - ultimo > pausa:
            scelti.append(t)
            ultimo = t
    return np.asarray(scelti, dtype=np.int64)


def variazione_oi(df: pd.DataFrame, met: pd.DataFrame, colonna: str = "sum_open_interest",
                  giorni_storia: int = 30) -> tuple:
    """Per ogni minuto di ``df``: la variazione relativa dell'interesse aperto fra le ultime due rilevazioni note
    (orario <= minuto) e il suo percentile fra le variazioni dei ``giorni_storia`` giorni prima (rilevazioni ogni 5
    minuti). Ritorna (variazione, percentile, presente)."""
    if met is None or met.empty or colonna not in met:
        n = len(df)
        return np.full(n, np.nan), np.full(n, np.nan), np.zeros(n, dtype=bool)
    oi = met[colonna].astype(float)
    # solo rilevazioni sulla griglia dei 5 minuti, una dopo l'altra (un buco interrompe la variazione)
    oi = oi[~oi.index.duplicated()].sort_index()
    salto = np.diff(oi.index.to_numpy(), prepend=-10)
    var = (oi / oi.shift(1) - 1).where(salto == 5)
    finestra = giorni_storia * 288
    pct = var.rolling(finestra, min_periods=finestra // 3).rank(pct=True)
    idx = df.index.to_numpy()
    pos = np.searchsorted(oi.index.to_numpy(), idx, side="right") - 1
    ok = pos >= 0
    v = np.full(len(idx), np.nan)
    p = np.full(len(idx), np.nan)
    v[ok] = var.to_numpy()[pos[ok]]
    p[ok] = pct.to_numpy()[pos[ok]]
    # il dato vale solo se la rilevazione e' recente (al massimo 10 minuti prima)
    recente = np.zeros(len(idx), dtype=bool)
    recente[ok] = (idx[ok] - oi.index.to_numpy()[pos[ok]]) <= 10
    v[~recente] = np.nan
    p[~recente] = np.nan
    return v, p, recente
