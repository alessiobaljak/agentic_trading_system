"""Programma 5: scalping con ordini limite in entrata e in uscita (E-005, idea I-020).

L'ingresso e' un ordine limite eseguito solo ad attraversamento (come ``motore5.simula_limite``); subito dopo si mette
l'ordine d'uscita a limite a ``livello·exp(d·m·σ)``, eseguibile dal minuto dopo l'ingresso e solo ad attraversamento;
se non si esegue entro ``tenuta`` minuti, si esce a mercato alla chiusura del minuto ``tenuta`` (commissione a mercato e
scarto doppio). Costi: 0,02% per ogni lato a limite.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.idee_ore import _dati


def _cumfund(df: pd.DataFrame, fund: Optional[pd.DataFrame]) -> np.ndarray:
    minuto = df.index.to_numpy()
    if fund is None or not len(fund):
        return np.zeros(len(minuto))
    cum = np.concatenate([[0.0], np.cumsum(fund["tasso"].to_numpy(float))])
    return cum[np.searchsorted(fund.index.to_numpy(), minuto, "right")]


def _uscita(h, l, c, j, e, prezzo_in, T, d):
    """(minuto d'uscita, prezzo, a_limite)."""
    finestra = (h[j + 1: e + 1] > T) if d > 0 else (l[j + 1: e + 1] < T)
    if finestra.any():
        return j + 1 + int(np.argmax(finestra)), T, True
    return e, c[e], False


def simula_doppio(df: pd.DataFrame, simbolo: str, inizi: np.ndarray, livelli: np.ndarray, sigma: np.ndarray,
                  direzioni: np.ndarray, m: float, validita: int, tenuta: int,
                  fund: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Trade con ingresso e uscita a limite. ``sigma[k]``: la σ con cui si mette il target dell'ordine k."""
    h, l, c = (df[k].to_numpy(float) for k in ("high", "low", "close"))
    minuto = df.index.to_numpy()
    n = len(c)
    F = _cumfund(df, fund)
    sc = m5.scarto(simbolo)
    righe, libero_da = [], -1
    for t0, livello, sg, d in zip(inizi, livelli, sigma, direzioni):
        t0 = int(t0)
        if t0 < libero_da or not (np.isfinite(livello) and np.isfinite(sg)) or t0 + validita > n:
            continue
        fin = slice(t0, t0 + validita)
        tocca = (l[fin] < livello) if d > 0 else (h[fin] > livello)
        if not tocca.any():
            continue
        j = t0 + int(np.argmax(tocca))
        e = j + tenuta
        if e >= n or not np.isfinite(c[e]):
            continue
        T = livello * np.exp(d * m * sg)
        i, prezzo, a_limite = _uscita(h, l, c, j, e, livello, T, d)
        costo = 2 * m5.MAKER if a_limite else m5.MAKER + m5.TAKER + 2 * sc
        lordo = d * (prezzo / livello - 1)
        fu = d * (F[i] - F[j])
        righe.append({"simbolo": simbolo, "decisione": j, "minuto": int(minuto[j]), "direzione": int(d),
                      "lordo": lordo, "costo": costo, "funding": fu, "netto": lordo - costo - fu,
                      "netto_doppio": lordo - 2 * costo - fu, "motivo": "target" if a_limite else "tempo",
                      "sigma": sg})
        libero_da = i + 1
    return pd.DataFrame(righe)


def caso_doppio(df: pd.DataFrame, simbolo: str, trade: pd.DataFrame, m: float, tenuta: int, fund=None,
                ripetizioni: int = 20, seme: int = 2026) -> pd.DataFrame:
    """Il caso: ingresso all'apertura di un minuto qualunque della stessa moneta e dello stesso mese (con il costo da
    ordine limite), stessa direzione, stesso target in σ (la σ del trade) e stessa tenuta."""
    if trade.empty:
        return trade
    rng = np.random.default_rng(seme)
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    minuto = df.index.to_numpy()
    n = len(c)
    F = _cumfund(df, fund)
    sc = m5.scarto(simbolo)
    mese = pd.to_datetime(minuto * 60, unit="s").to_period("M").astype(str).to_numpy()
    validi = df["periodo"].to_numpy() & np.isfinite(o)
    validi[max(0, n - tenuta - 2):] = False
    per_mese = {x: np.flatnonzero(validi & (mese == x)) for x in np.unique(mese[validi])}
    mesi_t = mese[trade["decisione"].to_numpy()]
    d_t, s_t = trade["direzione"].to_numpy(), trade["sigma"].to_numpy(float)
    out = []
    for r in range(ripetizioni):
        for k, x in enumerate(mesi_t):
            if x not in per_mese or not len(per_mese[x]):
                continue
            j = int(rng.choice(per_mese[x]))
            e = j + tenuta
            if not np.isfinite(c[e]):
                continue
            d, p0 = d_t[k], o[j]
            T = p0 * np.exp(d * m * s_t[k])
            i, prezzo, a_limite = _uscita(h, l, c, j, e, p0, T, d)
            costo = 2 * m5.MAKER if a_limite else m5.MAKER + m5.TAKER + 2 * sc
            lordo = d * (prezzo / p0 - 1)
            fu = d * (F[i] - F[j])
            out.append({"simbolo": simbolo, "decisione": j, "minuto": int(minuto[j]), "direzione": int(d),
                        "lordo": lordo, "costo": costo, "funding": fu, "netto": lordo - costo - fu,
                        "netto_doppio": lordo - 2 * costo - fu, "motivo": "target" if a_limite else "tempo",
                        "ripetizione": r})
    return pd.DataFrame(out)


def per_moneta_i020(idea, varianti, s, periodo):
    """Reti d'acquisto a k·σ sotto il prezzo con uscita a limite a m·σ sopra l'ingresso (scheda di I-020)."""
    df, b, fund = _dati(s, periodo, idea)
    if df is None:
        return {}
    nel = b["periodo"].to_numpy(bool)
    P = b["close"].shift(1).to_numpy()
    S = b["sigma"].shift(1).to_numpy()
    inizi = b.index.to_numpy() * 60 - int(df.index[0])
    ok = nel & (inizi >= 0) & (inizi + 60 <= len(df)) & np.isfinite(P) & np.isfinite(S)
    out = {}
    for n, v in varianti.items():
        livelli = P * np.exp(-v["k"] * S)
        t = simula_doppio(df, s, inizi[ok], livelli[ok], S[ok], np.ones(int(ok.sum()), int), v["m"], 60, v["H"], fund)
        out[n] = (t, caso_doppio(df, s, t, v["m"], v["H"], fund) if not t.empty else t)
    return out
