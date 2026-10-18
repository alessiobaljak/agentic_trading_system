"""Programma 5, fase 3: la scelta che si adatta (REGOLE.md, sezione 8; scheda di M-001).

1. ``trade_candidate``: per ogni candidata (cella a una moneta delle esplorazioni, in un verso) i suoi trade sul periodo,
   con il netto dopo i costi (commissione a mercato e scarto doppio per lato, funding; per G1 anche la gamba di BTC).
2. ``aggregati``: per candidata e per mese **d'uscita**, le somme per gruppi di giorni che servono al t (additive fra i
   mesi: un giorno sta in un mese solo).
3. ``scegli_e_tieni``: a ogni inizio mese m, le K candidate migliori fra i trade **chiusi** nei L mesi prima (uscita prima
   dell'inizio di m), e i loro trade con ingresso nel mese m.
4. ``placebo``: lo stesso con il segno del lordo di ogni trade tirato a caso.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.esplora_calendario import celle as celle_calendario
from research.programma5.strumenti.esplora_fase2 import BTC, HH, avanti, celle_moneta, sfoltisci
from research.programma5.strumenti.ore import barre

MESE0 = (2020, 1)


def indice_mese(minuti: np.ndarray) -> np.ndarray:
    t = pd.to_datetime(np.asarray(minuti, dtype=np.int64) * 60, unit="s")
    return ((t.year - MESE0[0]) * 12 + (t.month - MESE0[1])).to_numpy()


def minuto_mese(k: int) -> int:
    a, m = MESE0[0] + (MESE0[1] - 1 + k) // 12, (MESE0[1] - 1 + k) % 12 + 1
    return int(datetime(a, m, 1, tzinfo=timezone.utc).timestamp() // 60)


def pannello(monete, periodo: str, idea: str):
    """Come ``esplora_fase2.pannello``, con l'idea passata al guardiano dei periodi."""
    grezze = {s: barre(s, periodo, idea) for s in monete}
    grezze = {s: b for s, b in grezze.items() if len(b)}
    ore = np.arange(min(b.index.min() for b in grezze.values()), max(b.index.max() for b in grezze.values()) + 1)
    P = {}
    for s, b in grezze.items():
        b = b.reindex(ore).copy()
        b["periodo"] = b["periodo"].eq(True)
        b["funding_cum"] = b["funding_cum"].ffill().fillna(0.0)
        b["lc"] = np.log(b["close"])
        b["r1"] = b["lc"].diff()
        b["sigma"] = b["r1"].rolling(720, min_periods=500).std()
        for w in (1, 4, 24):
            b[f"z{w}"] = (b["lc"] - b["lc"].shift(w)) / (b["sigma"].shift(w) * np.sqrt(w))
        b["premio"] = m5.premio(s, periodo, idea).reindex(ore)
        P[s] = b
    btc = P[BTC]
    for s in P:
        if s == BTC:
            continue
        b, rb = P[s], btc["r1"]
        m = dict(window=720, min_periods=500)
        cov = (b["r1"] * rb).rolling(**m).mean() - b["r1"].rolling(**m).mean() * rb.rolling(**m).mean()
        b["beta"] = cov / rb.rolling(**m).var(ddof=0)
        b["sigma_e"] = (b["r1"] - b["beta"].shift(1) * rb).rolling(**m).std()
    A = {h: {s: avanti(P[s], h) for s in P} for h in HH}
    for h in (3, 6, 7, 8, 96):
        A[h] = {s: avanti(P[s], h) for s in P}
    return ore, P, A


def costo(s: str) -> float:
    """Un giro a mercato con lo scarto doppio (REGOLE.md, sezione 8)."""
    return 2 * (m5.TAKER + 2 * m5.scarto(s))


def trade_candidate(monete, periodo: str, idea: str, log=print) -> dict:
    """{(cella, verso): DataFrame con moneta, entrata, uscita, lordo, costo, famiglia}."""
    ore, P, A = pannello(monete, periodo, idea)
    btc = P[BTC]
    raccolte: dict = {}
    for s in P:
        b = P[s]
        nel = b["periodo"].to_numpy(bool)
        c_s, c_b = costo(s), costo(BTC)
        sorgenti = [(n, f, h, p, c, d, v) for n, f, h, p, c, d, v in celle_moneta(s, b, btc, A)]
        sorgenti += [(n, f, h, p, c, d, None) for n, f, h, p, c, d in celle_calendario(b)]
        conta = 0
        for nome, fam, h, pausa, cond, d, valore in sorgenti:
            a = A[h][s] if valore is None else valore
            ev = sfoltisci(np.asarray(cond, bool) & nel & np.isfinite(a), pausa)
            if not len(ev):
                continue
            lordo = d[ev] * a[ev]
            cst = np.full(len(ev), c_s)
            if fam == "G1":
                w = int(nome.split()[1][1:])
                beta = b["beta"].shift(w).to_numpy()[ev]
                cst = cst + np.abs(np.nan_to_num(beta)) * c_b
            entrata = (ore[ev] + 1) * 60
            raccolte.setdefault(nome, [fam, []])[1].append(pd.DataFrame(
                {"moneta": s, "entrata": entrata, "uscita": entrata + 60 * h, "lordo": lordo, "costo": cst}))
            conta += len(ev)
        log(f"[meta {periodo}] {s}: {conta} eventi")
    out = {}
    for nome, (fam, parti) in raccolte.items():
        t = pd.concat(parti, ignore_index=True)
        t["famiglia"] = fam
        out[nome] = t
    return out


def aggregati(netto: np.ndarray, uscita: np.ndarray, n_mesi: int) -> np.ndarray:
    """Per mese d'uscita: [N, S, somma S_g^2, somma S_g N_g, somma N_g^2, G] sui giorni g (S_g somma dei netti del giorno)."""
    out = np.zeros((n_mesi, 6))
    if not len(netto):
        return out
    giorno = uscita // 1440
    g, inv = np.unique(giorno, return_inverse=True)
    S = np.bincount(inv, weights=netto)
    N = np.bincount(inv).astype(float)
    mese_g = indice_mese(g * 1440)
    ok = (mese_g >= 0) & (mese_g < n_mesi)
    for col, val in enumerate((N, S, S * S, S * N, N * N, np.ones_like(N))):
        out[:, col] = np.bincount(mese_g[ok], weights=val[ok], minlength=n_mesi)[:n_mesi]
    return out


def t_da_aggregati(a: np.ndarray) -> tuple:
    """(n, media, t) da somme additive [N, S, S2, SN, N2, G]."""
    N, S, S2, SN, N2, G = a
    if N <= 0 or G < 3:
        return int(N), float("nan"), float("nan")
    m = S / N
    var = S2 - 2 * m * SN + m * m * N2
    se = np.sqrt(max(var, 0.0) * G / (G - 1)) / N
    return int(N), float(m), float(m / se) if se > 0 else float("nan")


def scegli_e_tieni(cand: dict, L: int, K: int, primo: int, ultimo: int, n_mesi: int, max_famiglia: int = 2,
                   min_trade: int = 30, t_min: float = 2.0, segni: dict = None) -> tuple:
    """(trade scelti, scelte per mese). ``cand``: {(cella, verso): DataFrame}; ``segni``: per il placebo, {chiave:
    array di ±1} che moltiplica il lordo."""
    chiavi = list(cand)
    netti, aggr = {}, np.zeros((len(chiavi), n_mesi, 6))
    for i, k in enumerate(chiavi):
        t = cand[k]
        lordo = t["lordo"].to_numpy() * (segni[k] if segni is not None else 1.0)
        netti[k] = lordo - t["costo"].to_numpy()
        aggr[i] = aggregati(netti[k], t["uscita"].to_numpy(), n_mesi)
    cum = np.concatenate([np.zeros((len(chiavi), 1, 6)), np.cumsum(aggr, axis=1)], axis=1)
    mesi_entrata = {k: indice_mese(cand[k]["entrata"].to_numpy()) for k in chiavi}
    scelti, scelte = [], {}
    for m in range(primo, ultimo + 1):
        da = max(0, m - L)
        righe = []
        for i, k in enumerate(chiavi):
            n, media, tt = t_da_aggregati(cum[i, m] - cum[i, da])
            if n >= min_trade and media > 0 and np.isfinite(tt) and tt >= t_min:
                righe.append((tt, k))
        righe.sort(reverse=True)
        presi, per_fam, celle = [], {}, set()
        for tt, k in righe:
            cella, verso = k
            fam = cand[k]["famiglia"].iat[0]
            if per_fam.get(fam, 0) >= max_famiglia or cella in celle:
                continue
            presi.append(k)
            per_fam[fam] = per_fam.get(fam, 0) + 1
            celle.add(cella)
            if len(presi) == K:
                break
        scelte[m] = presi
        for k in presi:
            sel = mesi_entrata[k] == m
            if sel.any():
                t = cand[k][sel]
                scelti.append(pd.DataFrame({"simbolo": t["moneta"].to_numpy(), "minuto": t["entrata"].to_numpy(),
                                            "uscita": t["uscita"].to_numpy(), "netto": netti[k][sel],
                                            "netto_doppio": netti[k][sel] - t["costo"].to_numpy(),
                                            "lordo": netti[k][sel] + t["costo"].to_numpy(),
                                            "costo": t["costo"].to_numpy(), "cella": k[0], "verso": k[1]}))
    return (pd.concat(scelti, ignore_index=True) if scelti else pd.DataFrame()), scelte


def con_versi(per_cella: dict) -> dict:
    """Da {cella: trade nel verso «segue»} a {(cella, verso): trade}: il verso «contro» ha il lordo cambiato di segno."""
    out = {}
    for cella, t in per_cella.items():
        out[(cella, "segue")] = t
        c = t.copy()
        c["lordo"] = -c["lordo"]
        out[(cella, "contro")] = c
    return out
