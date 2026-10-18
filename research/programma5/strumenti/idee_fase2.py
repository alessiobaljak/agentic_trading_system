"""Programma 5, fase 2: il calcolo nel motore a minuti di un'idea J che e' **esattamente** una cella di esplorazione
(E-101, E-103), presa nel verso «segue» o «contro».

Una variante e' ``{"cella": "<nome della cella>", "verso": "segue" | "contro"}``. La condizione d'ingresso, la direzione,
la durata e la pausa sono quelle della cella (``esplora_fase2.celle_moneta`` o ``esplora_calendario.celle``), calcolate
sulle barre orarie del periodo; i trade si simulano sulle candele da 1 minuto con i costi del programma e lo scarto doppio
su tutti i trade (prudente), il funding e il caso (``motore5.caso``). Le celle G1 sono trade coperti con BTC
(``idee_ore._coperto``).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.esplora_calendario import celle as celle_calendario
from research.programma5.strumenti.esplora_fase2 import BTC, avanti, celle_moneta, sfoltisci
from research.programma5.strumenti.idee_ore import _coperto, _sim
from research.programma5.strumenti.ore import barre


def _prepara(s: str, periodo: str, idea: str) -> dict:
    """Le barre della moneta e di BTC come in ``esplora_fase2.pannello`` (stesse colonne), per un'idea."""
    P = {}
    for x in {s, BTC}:
        b = barre(x, periodo, idea).copy()
        b["periodo"] = b["periodo"].eq(True)
        b["funding_cum"] = b["funding_cum"].ffill().fillna(0.0)
        b["lc"] = np.log(b["close"])
        b["r1"] = b["lc"].diff()
        b["sigma"] = b["r1"].rolling(720, min_periods=500).std()
        for w in (1, 4, 24):
            b[f"z{w}"] = (b["lc"] - b["lc"].shift(w)) / (b["sigma"].shift(w) * np.sqrt(w))
        b["premio"] = m5.premio(x, periodo, idea).reindex(b.index)
        P[x] = b
    ore = np.arange(min(b.index.min() for b in P.values()), max(b.index.max() for b in P.values()) + 1)
    for x in P:
        P[x] = P[x].reindex(ore)
        P[x]["periodo"] = P[x]["periodo"].eq(True)
        P[x]["funding_cum"] = P[x]["funding_cum"].ffill().fillna(0.0)
    if s != BTC:
        b, rb = P[s], P[BTC]["r1"]
        m = dict(window=720, min_periods=500)
        cov = (b["r1"] * rb).rolling(**m).mean() - b["r1"].rolling(**m).mean() * rb.rolling(**m).mean()
        b["beta"] = cov / rb.rolling(**m).var(ddof=0)
        b["sigma_e"] = (b["r1"] - b["beta"].shift(1) * rb).rolling(**m).std()
    return P


def _trova(nome: str, s: str, P: dict):
    b, btc = P[s], P[BTC]
    if nome.startswith("W"):
        for n, fam, h, pausa, cond, d in celle_calendario(b):
            if n == nome:
                return fam, h, pausa, cond, d
    else:
        finti = {h: {s: avanti(b, h), BTC: avanti(btc, h)} for h in (1, 4, 12, 24, 72, 168)}
        for n, fam, h, pausa, cond, d, _ in celle_moneta(s, b, btc, finti):
            if n == nome:
                return fam, h, pausa, cond, d
    return None


def per_moneta_cella(idea, varianti, s, periodo):
    df = m5.minuti(s, periodo, idea)
    if df.empty:
        return {}
    P = _prepara(s, periodo, idea)
    fund = m5.funding(s)
    b = P[s].loc[P[s].index.isin(barre(s, periodo, idea).index)]
    out = {}
    for n, v in varianti.items():
        if v["cella"].startswith("G1") and s == BTC:
            continue
        trovata = _trova(v["cella"], s, P)
        if trovata is None:
            continue
        fam, h, pausa, cond, d = trovata
        cond = pd.Series(cond, index=P[s].index).reindex(b.index).fillna(False).to_numpy(bool)
        segno = 1 if v["verso"] == "segue" else -1
        direz = int(segno * d[0])
        if fam != "G1":
            out[n] = _sim(df, s, b, cond, direz, h, pausa, fund)
            continue
        # G1: coperto con BTC (long o short la moneta per 1, BTC al contrario per beta)
        w = int(v["cella"].split()[1][1:])
        beta = P[s]["beta"].shift(w).reindex(b.index).to_numpy()
        nel = b["periodo"].to_numpy(bool)
        ev = sfoltisci(cond & nel & np.isfinite(beta), pausa)
        pos = (b.index.to_numpy()[ev] + 1) * 60 - 1 - int(df.index[0])
        dentro = (pos >= 0) & (pos < len(df))
        dfb = m5.minuti(BTC, periodo, idea)
        fund_b = m5.funding(BTC)
        if direz < 0:
            raise NotImplementedError("G1 short la moneta: non serve finora")
        t = _coperto(df, dfb, s, pos[dentro], beta[ev][dentro], 60 * h, fund, fund_b)
        if t.empty:
            out[n] = (t, t)
            continue
        rng = np.random.default_rng(2026)
        mese = pd.to_datetime(df.index.to_numpy() * 60, unit="s").to_period("M").astype(str).to_numpy()
        validi = df["periodo"].to_numpy() & np.isfinite(df["open"].to_numpy(float))
        per_mese = {x: np.flatnonzero(validi & (mese == x)) for x in np.unique(mese[validi])}
        casi = []
        for r in range(20):
            dec = np.array([rng.choice(per_mese[x]) for x in mese[t["decisione"].to_numpy()]])
            c = _coperto(df, dfb, s, dec, t["beta"].to_numpy(), 60 * h, fund, fund_b)
            c["ripetizione"] = r
            casi.append(c)
        out[n] = (t, pd.concat(casi, ignore_index=True))
    return out


def per_moneta_rete(idea, varianti, s, periodo):
    """Le reti di ordini limite di E-102 nel motore a minuti. Variante: ``{"tipo": "R" | "S", "lato": "acquisto" |
    "vendita", "k": ..., "H": ..., "m": ... (solo S)}``. R: uscita a mercato dopo H minuti (``motore5.simula_limite``);
    S: uscita a limite a m·σ (``scalping.simula_doppio``)."""
    from research.programma5.strumenti.scalping import caso_doppio, simula_doppio
    df = m5.minuti(s, periodo, idea)
    if df.empty:
        return {}
    b = barre(s, periodo, idea)
    fund = m5.funding(s)
    nel = b["periodo"].eq(True).to_numpy()
    P = b["close"].shift(1).to_numpy()
    S = np.log(b["close"]).diff().rolling(720, min_periods=500).std().shift(1).to_numpy()
    inizi = b.index.to_numpy() * 60 - int(df.index[0])
    ok = nel & (inizi >= 0) & (inizi + 60 <= len(df)) & np.isfinite(P) & np.isfinite(S)
    out = {}
    for n, v in varianti.items():
        d = 1 if v["lato"] == "acquisto" else -1
        livelli = P * np.exp(-d * v["k"] * S)
        direz = np.full(int(ok.sum()), d, dtype=int)
        if v["tipo"] == "R":
            t = m5.simula_limite(df, s, inizi[ok], livelli[ok], direz, validita=60, tenuta=v["H"], fund=fund)
            out[n] = (t, m5.caso_limite(df, s, t, v["H"], fund) if not t.empty else t)
        else:
            t = simula_doppio(df, s, inizi[ok], livelli[ok], S[ok], direz, v["m"], 60, v["H"], fund)
            out[n] = (t, caso_doppio(df, s, t, v["m"], v["H"], fund) if not t.empty else t)
    return out
