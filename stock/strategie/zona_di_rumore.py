"""Uscita dalla «zona di rumore» dell'apertura (`stock/prove/P002_zona_di_rumore.md`).

I livelli sono preparati prima per velocità; ognuno usa solo barre fino a quella della decisione
(la fascia σ usa i 14 giorni PRIMA di oggi; lo controlla `test_strategie.py`, tagliando il futuro).
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from stock.simulatore.motore import Ordine, Stato

NY = "America/New_York"
QUOTA = 0.98
GIORNI_FASCIA = 14
MINUTI_SEDUTA = 390
DECISIONI = tuple(29 + 30 * j for j in range(12))   # barre che finiscono alle 10:00, 10:30, ..., 15:30


def prepara(barre: pd.DataFrame, cal: pd.DataFrame, giorni_esclusi: set) -> dict:
    """`barre` = solo seduta (`ultima_mezzora.solo_seduta`), con le colonne di Alpaca (vwap, volume)."""
    t = barre.index.tz_convert(NY)
    giorni = np.array(t.date)
    n = len(barre)
    ap_ = barre["open"].to_numpy(float)
    ch_ = barre["close"].to_numpy(float)
    vw_ = barre["vwap"].to_numpy(float)
    vol_ = barre["volume"].to_numpy(float)
    alto = np.full(n, np.nan)
    basso = np.full(n, np.nan)
    vwap = np.full(n, np.nan)
    decisione = np.zeros(n, dtype=bool)
    uscita = np.zeros(n, dtype=bool)
    tagli = np.r_[0, np.where(giorni[1:] != giorni[:-1])[0] + 1, n]
    storia_m: list[np.ndarray] = []      # i movimenti m(d, k) delle sedute intere passate
    chiusura_ieri = None
    for a, b in zip(tagli[:-1], tagli[1:]):
        d = giorni[a]
        apertura_cal = cal.loc[d, "apertura"]
        chiusura_cal = cal.loc[d, "chiusura"]
        intera = (chiusura_cal - apertura_cal) == pd.Timedelta(minutes=MINUTI_SEDUTA)
        k = ((t[a:b] - apertura_cal).total_seconds() // 60).astype(int).to_numpy()
        prima_barra = len(k) > 0 and k[0] == 0
        m = np.full(MINUTI_SEDUTA, np.nan)
        if intera and prima_barra:
            m[k] = np.abs(ch_[a:b] / ap_[a] - 1)
        valido = (intera and prima_barra and chiusura_ieri is not None and d not in giorni_esclusi
                  and len(storia_m) >= GIORNI_FASCIA)
        if valido:
            pos = dict(zip(k, range(a, b)))
            if all(x in pos for x in DECISIONI) and (MINUTI_SEDUTA - 2) in pos and (MINUTI_SEDUTA - 1) in pos:
                sigma = np.nanmean(np.vstack(storia_m[-GIORNI_FASCIA:]), axis=0)
                su = max(ap_[a], chiusura_ieri)
                giu = min(ap_[a], chiusura_ieri)
                cum_pv = np.cumsum(vw_[a:b] * vol_[a:b])
                cum_v = np.cumsum(vol_[a:b])
                for x in DECISIONI:
                    i = pos[x]
                    alto[i] = su * (1 + sigma[x])
                    basso[i] = giu * (1 - sigma[x])
                    vwap[i] = cum_pv[i - a] / cum_v[i - a] if cum_v[i - a] > 0 else ch_[i]
                    decisione[i] = True
                uscita[pos[MINUTI_SEDUTA - 2]] = True
        if intera and prima_barra:
            storia_m.append(m)
        chiusura_ieri = ch_[b - 1]
    return {"alto": alto, "basso": basso, "vwap": vwap, "decisione": decisione, "uscita": uscita}


def strategia(seg: dict):
    alto, basso, vwap, decisione, uscita = (seg[k] for k in ("alto", "basso", "vwap", "decisione", "uscita"))

    def decidi(storia: pd.DataFrame, stato: Stato) -> list:
        i = len(storia) - 1
        pos = stato.azioni
        if uscita[i]:
            return [Ordine(-pos, "mercato", etichetta="fine giornata")] if pos else []
        if not decisione[i]:
            return []
        c = float(storia["close"].iat[-1])
        q = math.floor(QUOTA * stato.valore(c) / c)
        voluto = pos
        if pos == 0:
            if c > alto[i]:
                voluto = q
            elif c < basso[i]:
                voluto = -q
        elif pos > 0 and c < max(alto[i], vwap[i]):
            voluto = -q if c < basso[i] else 0
        elif pos < 0 and c > min(basso[i], vwap[i]):
            voluto = q if c > alto[i] else 0
        d = voluto - pos
        return [Ordine(d, "mercato", etichetta="decisione")] if d else []
    return decidi
