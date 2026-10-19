"""Programma 6: il motore dei backtest delle strategie a indicatori (METODO.md, sezione 3).

Una barra alla volta, senza dati futuri:
* i segnali si leggono alla **chiusura** della barra i e si opera dalla barra i+1;
* ingresso **a mercato** all'apertura di i+1 (commissione a mercato e scarto), oppure **ordine limite** a
  ``chiusura_i ∓ limite_k·ATR_i`` valido ``validita`` barre, eseguito solo se il prezzo **attraversa** il livello (al
  livello, o all'apertura se l'apertura e' gia' oltre), commissione da limite e niente scarto;
* uscite: **stop** a ``stop_k·ATR`` dall'ingresso (a mercato: se l'apertura e' gia' oltre lo stop, all'apertura),
  **obiettivo** a ``tp_k·ATR`` (ordine limite), **stop che segue** la chiusura a ``trail_k·ATR``, **tempo** massimo,
  **segnale d'uscita** (a mercato all'apertura dopo); se nella stessa barra si toccano stop e obiettivo vale lo stop;
  nella barra in cui si esegue un ordine limite d'ingresso vale lo stop ma non l'obiettivo (non si sa l'ordine dei
  prezzi);
* funding: la differenza del funding cumulato fra la chiusura prima dell'ingresso e la chiusura della barra d'uscita.

Ogni trade torna con: barra d'ingresso, barra d'uscita, direzione, prezzi, distanza dello stop, motivo, costi (frazione
del valore), funding (frazione), e da questi il netto in frazione e in R (multipli del rischio iniziale).
"""
from __future__ import annotations

import numpy as np
from numba import njit

TAKER, MAKER = 0.0005, 0.0002
MOTIVI = ("stop", "obiettivo", "segue", "tempo", "segnale")


@njit(cache=True)
def _simula(o, h, l, c, atr, fcum, sl, ss, ul, us, stop_k, tp_k, trail_k, max_barre, limite_k, validita,
            taker, maker, slip):
    n = len(c)
    e_i = np.empty(n, np.int64)
    x_i = np.empty(n, np.int64)
    dirs = np.empty(n, np.int64)
    pe = np.empty(n)
    px = np.empty(n)
    dist = np.empty(n)
    mot = np.empty(n, np.int64)
    costo = np.empty(n)
    fund = np.empty(n)
    k = 0
    pos = 0
    ingresso = 0.0
    stop = 0.0
    tp = 0.0
    d_stop = 0.0
    j_in = 0
    c_in = 0.0
    lim_dir = 0
    lim_liv = 0.0
    lim_fino = -1
    lim_atr = 0.0
    for j in range(1, n):
        if not (c[j] == c[j]) or not (o[j] == o[j]):
            continue
        appena_limite = False
        # 1. ingresso
        if pos == 0:
            if lim_dir != 0 and j <= lim_fino:
                eseguito = False
                if lim_dir > 0 and l[j] < lim_liv:
                    ingresso = min(lim_liv, o[j])
                    eseguito = True
                elif lim_dir < 0 and h[j] > lim_liv:
                    ingresso = max(lim_liv, o[j])
                    eseguito = True
                if eseguito:
                    pos = lim_dir
                    d_stop = stop_k * lim_atr
                    stop = ingresso - pos * d_stop
                    tp = ingresso + pos * tp_k * lim_atr if tp_k > 0 else 0.0
                    j_in = j
                    c_in = maker
                    lim_dir = 0
                    appena_limite = True
            elif lim_dir != 0 and j > lim_fino:
                lim_dir = 0
            if pos == 0 and lim_dir == 0:
                a = atr[j - 1]
                segnale = 1 if sl[j - 1] else (-1 if ss[j - 1] else 0)
                if segnale != 0 and a == a and a > 0:
                    if limite_k > 0:
                        lim_dir = segnale
                        lim_liv = c[j - 1] - segnale * limite_k * a
                        lim_fino = j + validita - 1
                        lim_atr = a
                        # l'ordine vale gia' da questa barra
                        if segnale > 0 and l[j] < lim_liv:
                            ingresso = min(lim_liv, o[j])
                            pos = 1
                        elif segnale < 0 and h[j] > lim_liv:
                            ingresso = max(lim_liv, o[j])
                            pos = -1
                        if pos != 0:
                            d_stop = stop_k * a
                            stop = ingresso - pos * d_stop
                            tp = ingresso + pos * tp_k * a if tp_k > 0 else 0.0
                            j_in = j
                            c_in = maker
                            lim_dir = 0
                            appena_limite = True
                    else:
                        pos = segnale
                        ingresso = o[j]
                        d_stop = stop_k * a
                        stop = ingresso - pos * d_stop
                        tp = ingresso + pos * tp_k * a if tp_k > 0 else 0.0
                        j_in = j
                        c_in = taker + slip
        if pos == 0:
            continue
        # 2. uscita nella barra j (prezzi senza scarto: lo scarto e' nei costi)
        uscita = 0.0
        motivo = -1
        if j > j_in and ((pos > 0 and ul[j - 1]) or (pos < 0 and us[j - 1])):
            uscita = o[j]
            motivo = 4
        elif pos > 0 and l[j] <= stop:
            uscita = min(stop, o[j]) if j > j_in else stop
            motivo = 0
        elif pos < 0 and h[j] >= stop:
            uscita = max(stop, o[j]) if j > j_in else stop
            motivo = 0
        elif tp_k > 0 and not appena_limite and pos > 0 and h[j] >= tp:
            uscita = max(tp, o[j]) if j > j_in else tp
            motivo = 1
        elif tp_k > 0 and not appena_limite and pos < 0 and l[j] <= tp:
            uscita = min(tp, o[j]) if j > j_in else tp
            motivo = 1
        elif max_barre > 0 and j - j_in + 1 >= max_barre:
            uscita = c[j]
            motivo = 3
        if motivo >= 0:
            c_out = maker if motivo == 1 else taker + slip
            iniziale = ingresso - pos * d_stop
            mosso = (pos > 0 and stop > iniziale + 1e-12) or (pos < 0 and stop < iniziale - 1e-12)
            e_i[k] = j_in
            x_i[k] = j
            dirs[k] = pos
            pe[k] = ingresso
            px[k] = uscita
            dist[k] = d_stop
            mot[k] = 2 if (motivo == 0 and mosso) else motivo
            costo[k] = c_in + c_out
            fund[k] = pos * (fcum[j] - fcum[j_in - 1])
            k += 1
            pos = 0
            continue
        # 3. lo stop che segue, alla chiusura
        if trail_k > 0 and atr[j] == atr[j]:
            if pos > 0:
                stop = max(stop, c[j] - trail_k * atr[j])
            else:
                stop = min(stop, c[j] + trail_k * atr[j])
    return e_i[:k], x_i[:k], dirs[:k], pe[:k], px[:k], dist[:k], mot[:k], costo[:k], fund[:k]


def simula(b, atr, segnali: dict, stop_k: float, tp_k: float = 0.0, trail_k: float = 0.0, max_barre: int = 0,
           limite_k: float = 0.0, validita: int = 1, slip: float = 0.0002) -> dict:
    """``b``: barre (open, high, low, close, funding_cum, minuto); ``segnali``: array booleani ``long``, ``short`` e
    facoltativi ``esci_long``, ``esci_short``. Ritorna i trade come dizionario di array, con ``netto`` (frazione) e ``R``."""
    n = len(b)
    falso = np.zeros(n, np.bool_)
    out = _simula(b["open"].to_numpy(float), b["high"].to_numpy(float), b["low"].to_numpy(float),
                  b["close"].to_numpy(float), np.asarray(atr, float), b["funding_cum"].to_numpy(float),
                  np.asarray(segnali.get("long", falso), np.bool_), np.asarray(segnali.get("short", falso), np.bool_),
                  np.asarray(segnali.get("esci_long", falso), np.bool_),
                  np.asarray(segnali.get("esci_short", falso), np.bool_),
                  float(stop_k), float(tp_k), float(trail_k), int(max_barre), float(limite_k), int(validita),
                  TAKER, MAKER, float(slip))
    nomi = ("ingresso_i", "uscita_i", "direzione", "prezzo_in", "prezzo_out", "distanza_stop", "motivo", "costo",
            "funding")
    t = dict(zip(nomi, out))
    lordo = t["direzione"] * (t["prezzo_out"] / t["prezzo_in"] - 1)
    t["lordo"] = lordo
    t["netto"] = lordo - t["costo"] - t["funding"]
    t["netto_doppio"] = lordo - 2 * t["costo"] - t["funding"]
    frazione_stop = t["distanza_stop"] / t["prezzo_in"]
    t["frazione_stop"] = frazione_stop
    t["R"] = np.where(frazione_stop > 0, t["netto"] / frazione_stop, np.nan)
    minuti = b["minuto"].to_numpy()
    t["minuto_in"] = minuti[t["ingresso_i"]] if len(t["ingresso_i"]) else np.array([], np.int64)
    t["minuto_out"] = minuti[t["uscita_i"]] if len(t["uscita_i"]) else np.array([], np.int64)
    return t


def atr(b, n: int = 14) -> np.ndarray:
    """ATR di Wilder sulle barre."""
    h, l, c = (b[k].to_numpy(float) for k in ("high", "low", "close"))
    pc = np.concatenate([[np.nan], c[:-1]])
    tr = np.nanmax(np.vstack([h - l, np.abs(h - pc), np.abs(l - pc)]), axis=0)
    import pandas as pd
    return pd.Series(tr).ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean().to_numpy()
