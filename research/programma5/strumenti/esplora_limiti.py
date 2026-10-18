"""Programma 5, fase 2: le esplorazioni con ordini limite (le reti di E-002 con uscita a mercato e quelle di E-005 con
uscita a limite) su un periodo e un elenco di monete qualunque, con le stesse definizioni."""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.esplora_fase2 import riassumi_fase2
from research.programma5.strumenti.ore import barre


def per_moneta(s: str, periodo: str) -> dict:
    df = m5.minuti(s, periodo, storia_giorni=35)
    fund = m5.funding(s)
    b = barre(s, periodo)
    minuto = df.index.to_numpy()
    o, h, l, c = (df[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    nel = df["periodo"].to_numpy(bool)
    n = len(c)
    F = np.zeros(n)
    if len(fund):
        cum = np.concatenate([[0.0], np.cumsum(fund["tasso"].to_numpy(float))])
        F = cum[np.searchsorted(fund.index.to_numpy(), minuto, "right")]
    sc = m5.scarto(s)
    sig = np.log(b["close"]).diff().rolling(720, min_periods=500).std()
    off = int((60 - minuto[0] % 60) % 60)
    nh = (n - off) // 60
    ore = (minuto[off] // 60) + np.arange(nh)
    P = b["close"].shift(1).reindex(ore).to_numpy(float)
    S = sig.shift(1).reindex(ore).to_numpy(float)
    L2 = l[off: off + nh * 60].reshape(nh, 60)
    H2 = h[off: off + nh * 60].reshape(nh, 60)
    ora_nel = nel[off: off + nh * 60].reshape(nh, 60)[:, 0]
    mese = pd.to_datetime(minuto * 60, unit="s").to_period("M").astype(str).to_numpy()
    out = {}
    for HH in (15, 60, 240, 1440):
        fwd = np.full(n, np.nan)
        fwd[: n - HH] = c[HH:] / o[: n - HH] - 1 - (F[HH:] - F[: n - HH])
        ok = nel & np.isfinite(fwd)
        base = pd.Series(mese).map(pd.Series(fwd[ok]).groupby(mese[ok]).mean()).to_numpy(float)
        for k in (2, 3, 4, 6):
            for lato, d in (("acquisto", 1), ("vendita", -1)):
                livello = P * np.exp(-d * k * S)
                tocca = (L2 < livello[:, None]) if d > 0 else (H2 > livello[:, None])
                riga_ok = tocca.any(axis=1) & np.isfinite(livello) & ora_nel
                col = tocca.argmax(axis=1)
                # E-002: uscita a mercato dopo HH minuti (lordo, senza costi)
                righe, libero = [], -1
                for r in np.flatnonzero(riga_ok):
                    if ore[r] < libero:
                        continue
                    j = off + r * 60 + col[r]
                    e = j + HH
                    if e >= n or not np.isfinite(c[e]):
                        continue
                    v = d * (c[e] / livello[r] - 1) - d * (F[e] - F[j])
                    righe.append((s, int(minuto[j]), v, v - d * base[j]))
                    libero = minuto[e] // 60 + 1
                out[f"R {lato} k{k} H{HH}"] = righe
                if HH == 1440:
                    continue
                # E-005: uscita a limite a m·σ (netto, costi compresi)
                for mm in (0.5, 1, 2):
                    righe, libero = [], -1
                    for r in np.flatnonzero(riga_ok):
                        if ore[r] < libero:
                            continue
                        j = off + r * 60 + col[r]
                        e = j + HH
                        if e >= n or not np.isfinite(c[e]):
                            continue
                        L = livello[r]
                        T = L * np.exp(d * mm * S[r])
                        fin = (h[j + 1: e + 1] > T) if d > 0 else (l[j + 1: e + 1] < T)
                        if fin.any():
                            i = j + 1 + int(np.argmax(fin))
                            prezzo, costo = T, 2 * m5.MAKER
                        else:
                            i, prezzo, costo = e, c[e], m5.MAKER + m5.TAKER + 2 * sc
                        v = d * (prezzo / L - 1) - d * (F[i] - F[j]) - costo
                        righe.append((s, int(minuto[j]), v, v - d * base[j], v - costo))
                        libero = minuto[i] // 60 + 1
                    out[f"S {lato} k{k} m{mm} H{HH}"] = righe
    return out


def esplora(monete, periodo: str, log=print) -> dict:
    raccolte: dict = {}
    for s in monete:
        ris = per_moneta(s, periodo)
        for nome, righe in ris.items():
            raccolte.setdefault(nome, []).extend(righe)
        log(f"[limiti {periodo}] {s}: {sum(len(r) for r in ris.values())} trade")
    out = {}
    for nome, righe in raccolte.items():
        colonne = ["s", "minuto", "v", "x"] + (["doppio"] if nome.startswith("S ") else [])
        df = pd.DataFrame(righe, columns=colonne)
        r = riassumi_fase2(df)
        if nome.startswith("S ") and len(df):
            r["doppio"] = float(df["doppio"].mean())
        out[nome] = r
    return out


def promossa(nome: str, r: dict, monete_min: int = 10) -> bool:
    """Le reti con uscita a mercato (R): lordo >= 0,25% e contro il caso >= 0,20%; con uscita a limite (S): netto >=
    0,05% e netto a costi doppi > 0. Poi: t >= 3, positivo in ogni semestre con almeno 20 trade, su almeno il 70% delle
    monete con almeno 10 trade (almeno ``monete_min``), almeno 100 trade."""
    if r.get("trade", 0) < 100 or not np.isfinite(r.get("t", np.nan)):
        return False
    if nome.startswith("R "):
        if r["lordo"] < 0.0025 or r["contro_caso"] < 0.0020:
            return False
    elif r["lordo"] < 0.0005 or not r.get("doppio", -1) > 0:
        return False
    if r["t"] < 3:
        return False
    if any(m <= 0 for n, m in r["per_semestre"].values() if n >= 20):
        return False
    monete = [m for n, m in r["per_moneta"].values() if n >= 10]
    return len(monete) >= monete_min and sum(1 for m in monete if m > 0) >= 0.7 * len(monete)
