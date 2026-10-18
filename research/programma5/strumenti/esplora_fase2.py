"""Programma 5, fase 2: l'esplorazione a ore su un periodo e un elenco di monete qualunque (REGOLE.md, 6bis e 7).

Raccoglie in un solo programma le famiglie di E-001 (scosse, rotture, funding, rapporti long/short, acquisti aggressivi,
volume, calma, calendario, tendenza, interesse aperto), di E-004 (premio sullo spot, liquidazioni) e di E-003 (scosse
proprie coperte con BTC, classifiche, paniere contro BTC), con le stesse definizioni. Una cella e' un insieme di trade
con il loro lordo (funding compreso, senza commissioni e scarto) e il lordo meno la media della stessa moneta e dello
stesso mese (il caso).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma5.strumenti.esplorazione import riassumi, t_giorni
from research.programma5.strumenti.ore import barre

BTC = "BTCUSDT"
HH = (1, 4, 12, 24, 72, 168)
H5 = (1, 4, 12, 24, 72)


def avanti(b: pd.DataFrame, h: int) -> np.ndarray:
    o, c, f = (b[k].to_numpy(float) for k in ("open", "close", "funding_cum"))
    n = len(c)
    out = np.full(n, np.nan)
    if h < n:
        out[: n - h] = (c[h:] / o[1: n - h + 1] - 1 - (f[h - 1: n - 1] - f[: n - h]))
    return out


def sfoltisci(cond: np.ndarray, pausa: int) -> np.ndarray:
    scelti, ultimo = [], -10 ** 12
    for t in np.flatnonzero(cond):
        if t - ultimo >= pausa:
            scelti.append(t)
            ultimo = t
    return np.asarray(scelti, dtype=np.int64)


def pct(x: pd.Series, finestra: int = 720, minimo: int = 500) -> np.ndarray:
    return x.rolling(finestra, min_periods=minimo).rank(pct=True).to_numpy()


def pannello(monete, periodo: str):
    grezze = {s: barre(s, periodo) for s in monete}
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
        b["premio"] = m5.premio(s, periodo).reindex(ore)
        P[s] = b
    btc = P[BTC]
    for s in monete:
        if s == BTC:
            continue
        b, rb = P[s], btc["r1"]
        m = dict(window=720, min_periods=500)
        cov = (b["r1"] * rb).rolling(**m).mean() - b["r1"].rolling(**m).mean() * rb.rolling(**m).mean()
        b["beta"] = cov / rb.rolling(**m).var(ddof=0)
        b["sigma_e"] = (b["r1"] - b["beta"].shift(1) * rb).rolling(**m).std()
    A = {h: {s: avanti(P[s], h) for s in monete} for h in HH}
    return ore, P, A


# ---------------------------------------------------------------------------
# famiglie per moneta: (nome, famiglia, h, pausa, condizione, direzione, valore o None)
# ---------------------------------------------------------------------------

def celle_moneta(s: str, b: pd.DataFrame, btc: pd.DataFrame, A: dict):
    ora = b.index.to_numpy()
    mezzanotte = ((ora + 1) % 24) == 0
    uno = np.ones(len(b))
    r1 = b["r1"].to_numpy()
    c = b["close"].to_numpy()
    # F1 scossa
    for w in (1, 4, 24):
        z = b[f"z{w}"].to_numpy()
        for k in (3, 4, 5):
            for h in H5:
                yield f"F1 w{w} k{k} su h{h}", "F1", h, max(w, h), z >= k, uno, None
                yield f"F1 w{w} k{k} giu h{h}", "F1", h, max(w, h), z <= -k, -uno, None
    # G1 scossa propria coperta con BTC
    if s != BTC:
        for w in (1, 4, 24):
            ew = (b["lc"] - b["lc"].shift(w)) - b["beta"].shift(w) * (btc["lc"] - btc["lc"].shift(w))
            ze = (ew / (b["sigma_e"].shift(w) * np.sqrt(w))).to_numpy()
            bt = b["beta"].shift(w).to_numpy()
            for h in H5:
                cop = A[h][s] - bt * A[h][BTC]
                for k in (2, 3, 4):
                    yield f"G1 w{w} k{k} su h{h}", "G1", h, max(w, h), ze >= k, uno, cop
                    yield f"G1 w{w} k{k} giu h{h}", "G1", h, max(w, h), ze <= -k, -uno, cop
    # F5 rottura
    for N in (5, 20, 60):
        mx = b["high"].rolling(N * 24, min_periods=N * 24 - 12).max().shift(1).to_numpy()
        mn = b["low"].rolling(N * 24, min_periods=N * 24 - 12).min().shift(1).to_numpy()
        for h in (24, 72, 168):
            yield f"F5 N{N} su h{h}", "F5", h, h, c > mx, uno, None
            yield f"F5 N{N} giu h{h}", "F5", h, h, c < mn, -uno, None
    # F6 funding al regolamento
    reg = b["regolamento"].eq(True).to_numpy()
    sett = b["funding_8h"].where(b["regolamento"].eq(True)).dropna()
    pf = pd.Series(np.nan, index=b.index)
    pf.loc[sett.index] = sett.rolling(270, min_periods=90).rank(pct=True).to_numpy()
    pf = pf.to_numpy()
    for h in (24, 72, 168):
        yield f"F6 alto h{h}", "F6", h, h, reg & (pf >= 0.9), uno, None
        yield f"F6 basso h{h}", "F6", h, h, reg & (pf <= 0.1), -uno, None
    # F7 rapporti long/short a mezzanotte
    for col in ("ls_tutti", "ls_grandi_pos", "ls_grandi_conti"):
        giorni = b[col].where(mezzanotte).dropna()
        px = pd.Series(np.nan, index=b.index)
        px.loc[giorni.index] = giorni.rolling(31, min_periods=20).rank(pct=True).to_numpy()
        px = px.to_numpy()
        for h in (24, 72):
            yield f"F7 {col} alto h{h}", "F7", h, h, mezzanotte & (px >= 0.9), uno, None
            yield f"F7 {col} basso h{h}", "F7", h, h, mezzanotte & (px <= 0.1), -uno, None
    # F8 acquisti aggressivi
    for w in (1, 4, 24):
        q = b["buy"].rolling(w).sum() / b["volume"].rolling(w).sum()
        pq = pct(q)
        for h in (1, 4, 24):
            yield f"F8 w{w} alta h{h}", "F8", h, max(w, h), pq >= 0.95, uno, None
            yield f"F8 w{w} bassa h{h}", "F8", h, max(w, h), pq <= 0.05, -uno, None
    # F9 volume
    vr = (b["volume"] / b["volume"].rolling(720, min_periods=500).median().shift(1)).to_numpy()
    for k in (5, 10):
        for h in (1, 4, 24):
            yield f"F9 k{k} su h{h}", "F9", h, h, (vr >= k) & (r1 > 0), uno, None
            yield f"F9 k{k} giu h{h}", "F9", h, h, (vr >= k) & (r1 < 0), -uno, None
    # F10 calma poi rottura
    mx24, mn24 = b["high"].rolling(24).max(), b["low"].rolling(24).min()
    amp = (mx24 - mn24) / b["close"]
    calma = (amp / amp.rolling(720, min_periods=500).median()).shift(1).to_numpy() < 0.5
    for h in (4, 24, 72):
        yield f"F10 su h{h}", "F10", h, h, calma & (c > mx24.shift(1).to_numpy()), uno, None
        yield f"F10 giu h{h}", "F10", h, h, calma & (c < mn24.shift(1).to_numpy()), -uno, None
    # F11 calendario
    for X in range(24):
        yield f"F11 ora {X:02d}", "F11", 1, 1, (ora % 24) == ((X - 1) % 24), uno, None
    giorno = pd.to_datetime((ora + 1) * 3600, unit="s").dayofweek.to_numpy()
    for g, nome in enumerate(("lun", "mar", "mer", "gio", "ven", "sab", "dom")):
        yield f"F11 {nome}", "F11", 24, 24, mezzanotte & (giorno == g), uno, None
    # F12 tendenza
    for N in (3, 7, 30):
        r = (b["lc"] - b["lc"].shift(24 * N)).to_numpy()
        for h in (24, 168):
            yield f"F12 N{N} su h{h}", "F12", h, h, mezzanotte & (r > 0), uno, None
            yield f"F12 N{N} giu h{h}", "F12", h, h, mezzanotte & (r < 0), -uno, None
    # F13 prezzo e interesse aperto
    loi = np.log(b["oi"].where(b["oi"] > 0))
    z24 = b["z24"].to_numpy()
    doi24 = (loi - loi.shift(24)).to_numpy()
    for lp, cp, d in (("su", z24 >= 1, uno), ("giu", z24 <= -1, -uno)):
        for lo, co in (("oi su", doi24 > 0), ("oi giu", doi24 < 0)):
            for h in (24, 72):
                yield f"F13 prezzo {lp} {lo} h{h}", "F13", h, h, mezzanotte & cp & co, d, None
    # P1-P3 premio
    pr = b["premio"]
    ppr = pct(pr)
    for q in (0.05, 0.01):
        for h in (1, 4, 24, 72):
            yield f"P1 q{int(q * 100)} alto h{h}", "P1", h, h, ppr >= 1 - q, uno, None
            yield f"P1 q{int(q * 100)} basso h{h}", "P1", h, h, ppr <= q, -uno, None
    for w in (1, 4):
        pd_ = pct(pr - pr.shift(w))
        for h in (1, 4, 24):
            yield f"P2 w{w} sale h{h}", "P2", h, max(w, h), pd_ >= 0.95, uno, None
            yield f"P2 w{w} scende h{h}", "P2", h, max(w, h), pd_ <= 0.05, -uno, None
    for w in (1, 4):
        z = b[f"z{w}"].to_numpy()
        for h in (4, 12, 24):
            yield f"P3 w{w} giu sconto h{h}", "P3", h, max(w, h), (z <= -3) & (ppr <= 0.10), -uno, None
            yield f"P3 w{w} giu senza sconto h{h}", "P3", h, max(w, h), (z <= -3) & (ppr > 0.10), -uno, None
            yield f"P3 w{w} su premio h{h}", "P3", h, max(w, h), (z >= 3) & (ppr >= 0.90), uno, None
            yield f"P3 w{w} su senza premio h{h}", "P3", h, max(w, h), (z >= 3) & (ppr < 0.90), uno, None
    # L0-L2 liquidazioni e posizioni nuove
    poi = pct(loi - loi.shift(1))
    z1 = b["z1"].to_numpy()
    for h in (4, 12, 24):
        yield f"L0 giu h{h}", "L0", h, h, z1 <= -2, -uno, None
        yield f"L0 su h{h}", "L0", h, h, z1 >= 2, uno, None
        yield f"L1 giu h{h}", "L1", h, h, (poi <= 0.02) & (z1 <= -2), -uno, None
        yield f"L1 su h{h}", "L1", h, h, (poi <= 0.02) & (z1 >= 2), uno, None
        yield f"L2 giu h{h}", "L2", h, h, (poi >= 0.98) & (z1 <= -2), -uno, None
        yield f"L2 su h{h}", "L2", h, h, (poi >= 0.98) & (z1 >= 2), uno, None


# ---------------------------------------------------------------------------
# famiglie di portafoglio (G2-G6), come E-003
# ---------------------------------------------------------------------------

def decisioni(ore: np.ndarray, nel: np.ndarray, h: int) -> np.ndarray:
    fine = ore + 1
    if h <= 24:
        ok = (fine % h) == 0
    else:
        giorno0 = (fine[nel][0] // 24) if nel.any() else 0
        ok = ((fine % 24) == 0) & (((fine // 24 - giorno0) % (h // 24)) == 0)
    return np.flatnonzero(ok & nel)


def classifica(ore, punteggio: dict, A_h: dict, dec: np.ndarray, minimo: int = 12, quanti: int = 5):
    monete = list(punteggio)
    S = np.vstack([punteggio[s] for s in monete])
    R = np.vstack([A_h[s] for s in monete])
    righe, contributi = [], []
    for t in dec:
        p, r = S[:, t], R[:, t]
        ok = np.isfinite(p) & np.isfinite(r)
        if ok.sum() < minimo:
            continue
        idx = np.flatnonzero(ok)
        ordine = idx[np.argsort(p[idx], kind="stable")]
        basse, alte = ordine[:quanti], ordine[-quanti:]
        v = (r[alte].mean() - r[basse].mean()) / 2
        media = r[idx].mean()
        righe.append(("PORTAFOGLIO", int(ore[t] * 60), v, v))
        contributi += [(monete[i], r[i] - media) for i in alte] + [(monete[i], -(r[i] - media)) for i in basse]
    return pd.DataFrame(righe, columns=["s", "minuto", "v", "x"]), contributi


def portafogli(ore, P, A, monete):
    nel = P[BTC]["periodo"].to_numpy()
    btc = P[BTC]
    altre = [s for s in monete if s != BTC]
    for w in (1, 4, 24, 72, 168):
        grezzo = {s: (P[s]["lc"] - P[s]["lc"].shift(w)).to_numpy() for s in monete}
        residuo = {s: ((P[s]["lc"] - P[s]["lc"].shift(w)) - P[s]["beta"].shift(w) *
                       (btc["lc"] - btc["lc"].shift(w))).to_numpy() for s in altre}
        for h in (1, 4, 24, 72, 168):
            dec = decisioni(ore, nel, h)
            yield (f"G2 rendimento w{w} h{h}", "G2") + classifica(ore, grezzo, A[h], dec)
            yield (f"G2 residuo w{w} h{h}", "G2") + classifica(ore, residuo, {s: A[h][s] for s in altre}, dec)
    for h in (24, 72, 168):
        f8 = {s: P[s]["funding_8h"].to_numpy(float) for s in monete}
        yield (f"G3 funding h{h}", "G3") + classifica(ore, f8, A[h], decisioni(ore, nel, h))
    for w in (24, 72):
        doi = {}
        for s in monete:
            lo = np.log(P[s]["oi"].where(P[s]["oi"] > 0))
            doi[s] = (lo - lo.shift(w)).to_numpy()
        for h in (24, 72):
            yield (f"G4 oi w{w} h{h}", "G4") + classifica(ore, doi, A[h], decisioni(ore, nel, h))
    vol = {}
    for s in monete:
        v24 = P[s]["volume"].rolling(24).sum()
        vol[s] = (v24 / v24.rolling(720, min_periods=500).median().shift(24)).to_numpy()
    for h in (24, 72):
        yield (f"G5 volume h{h}", "G5") + classifica(ore, vol, A[h], decisioni(ore, nel, h))
    # G6 paniere contro BTC
    r1 = pd.DataFrame({s: P[s]["r1"] for s in altre})
    sig = (r1.mean(axis=1) - btc["r1"]).rolling(720, min_periods=500).std()
    lc = pd.DataFrame({s: P[s]["lc"] for s in altre})
    for w in (4, 24, 72):
        sw = (lc - lc.shift(w)).mean(axis=1) - (btc["lc"] - btc["lc"].shift(w))
        z = (sw / (sig.shift(w) * np.sqrt(w))).to_numpy()
        for h in (4, 24, 72):
            with np.errstate(all="ignore"):
                paniere = np.nanmean(np.vstack([A[h][s] for s in altre]), axis=0)
            v_lungo = (paniere - A[h][BTC]) / 2
            ok = nel & np.isfinite(v_lungo)
            for k in (2, 3):
                for lato, cond, d in (("su", z >= k, 1), ("giu", z <= -k, -1)):
                    ev = sfoltisci(cond & ok, max(w, h))
                    righe = pd.DataFrame({"s": "PANIERE", "minuto": ore[ev] * 60, "v": d * v_lungo[ev],
                                          "x": d * v_lungo[ev]})
                    yield f"G6 w{w} k{k} {lato} h{h}", "G6", righe, None


# ---------------------------------------------------------------------------

def semestri(minuti: np.ndarray) -> np.ndarray:
    t = pd.to_datetime(minuti * 60, unit="s")
    return (t.year.astype(str) + np.where(t.month <= 6, "-1", "-2")).to_numpy()


def riassumi_fase2(righe: pd.DataFrame, contributi=None) -> dict:
    r = riassumi(righe)
    if not r["trade"]:
        return r
    sem = semestri(righe["minuto"].to_numpy(np.int64))
    v = righe["v"].to_numpy(float)
    r["per_semestre"] = {x: [int((sem == x).sum()), float(v[sem == x].mean())] for x in sorted(set(sem))}
    if contributi is not None:
        c = pd.DataFrame(contributi, columns=["s", "v"])
        r["per_moneta"] = {m: [int(len(g)), float(g["v"].mean())] for m, g in c.groupby("s")}
    return r


def promossa(fam: str, r: dict, lordo_min: float = 0.003, caso_min: float = 0.0025, monete_min: int = 10) -> bool:
    if r.get("trade", 0) < 100 or not np.isfinite(r.get("t", np.nan)):
        return False
    segno = np.sign(r["lordo"])
    if fam == "G1":
        lordo_min, caso_min = 0.005, 0.004
    if segno * r["lordo"] < lordo_min or segno * r["contro_caso"] < caso_min:
        return False
    if segno * r["t"] < (3.5 if fam == "G6" else 3.0):
        return False
    if any(segno * m <= 0 for n, m in r["per_semestre"].values() if n >= 20):
        return False
    if fam == "G6":
        return True
    monete = [m for n, m in r["per_moneta"].values() if n >= 10]
    giuste = sum(1 for m in monete if segno * m > 0)
    return len(monete) >= monete_min and giuste >= 0.7 * len(monete)


#: i fenomeni gia' provati su R sulle 12 monete della fase 1 (REGOLE.md, 7): il rimbalzo dopo i crolli, preso «contro»
PARENTI_R = ("F1 w4 k5 giu", "F1 w4 k4 giu", "F1 w24 k3 giu", "F9", "P3 w4 giu sconto", "P3 w1 giu sconto", "P1 q1 basso")


def parente_r(nome: str, r: dict) -> bool:
    return r.get("lordo", 0) < 0 and any(nome.startswith(p) for p in PARENTI_R) and (" giu" in nome or "basso" in nome)


def esplora(monete, periodo: str, log=print) -> dict:
    ore, P, A = pannello(monete, periodo)
    btc = P[BTC]
    raccolte: dict = {}
    for s in monete:
        b = P[s]
        nel = b["periodo"].to_numpy(bool)
        mese = pd.to_datetime(b.index.to_numpy() * 3600, unit="s").to_period("M").astype(str).to_numpy()
        basi: dict = {}
        conta = 0
        for nome, fam, h, pausa, cond, d, valore in celle_moneta(s, b, btc, A):
            a = A[h][s] if valore is None else valore
            if valore is not None or h not in basi:
                ok = nel & np.isfinite(a)
                base = pd.Series(mese).map(pd.Series(a[ok]).groupby(mese[ok]).mean()).to_numpy(float)
                if valore is None:
                    basi[h] = base
            else:
                base = basi[h]
            ev = sfoltisci(np.asarray(cond, bool) & nel & np.isfinite(a), pausa)
            raccolte.setdefault(nome, [fam, [], None])[1].append(pd.DataFrame(
                {"s": s, "minuto": b.index.to_numpy()[ev] * 60, "v": d[ev] * a[ev], "x": d[ev] * (a[ev] - base[ev])}))
            conta += len(ev)
        log(f"[fase 2 {periodo}] {s}: {conta} eventi")
    for nome, fam, righe, contributi in portafogli(ore, P, A, monete):
        raccolte[nome] = [fam, [righe], contributi]
    risultati = {}
    for nome, (fam, parti, contributi) in raccolte.items():
        parti = [p for p in parti if len(p)]
        righe = pd.concat(parti, ignore_index=True) if parti else pd.DataFrame(columns=["s", "minuto", "v", "x"])
        r = riassumi_fase2(righe, contributi)
        r["famiglia"] = fam
        r["promossa"] = bool(r["trade"]) and fam != "L0" and promossa(fam, r)
        r["parente_R"] = parente_r(nome, r)
        risultati[nome] = r
    return risultati
