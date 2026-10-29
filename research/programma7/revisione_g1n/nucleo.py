"""Revisione di G1N (29 ottobre 2026): G1 e G1N riscritte da zero dalle regole scritte (PRIMA.md, VENTISEIESIMA.md,
VENTIQUATTRESIMA.md), senza usare le funzioni della ricerca per i conti. Dalla ricerca si prende solo il caricamento dei dati
(`seconda.pannello`, `esecuzione.ore_di`).

Convenzioni (le stesse scritte in `seconda.py`): la riga ``i`` del pannello e' il giorno che apre alle 00:00 UTC; il peso
deciso alle 00:00 del giorno ``i`` si tiene dall'apertura di ``i`` all'apertura di ``i+1``; il funding della riga ``i`` e' quello
dei regolamenti pagati da chi tiene il giorno ``i`` (08:00 e 16:00 di ``i``, 00:00 di ``i+1``).
"""
from __future__ import annotations

import numpy as np
from scipy.stats import rankdata

STORIA, VOL_MIN, N_UNI, MIN_MONETE = 200, 2e6, 100, 20
ENTRA, RESTA = 0.20, 0.40
G_BETA, MIN_BETA = 90, 45
TAKER, MAKER = 0.0005, 0.0002


def costo_di(s: str) -> float:
    return TAKER + (0.0001 if s in ("BTCUSDT", "ETHUSDT", "SOLUSDT") else 0.0002)


def ritorni_chiusura(C: np.ndarray) -> np.ndarray:
    """r[t] = C[t]/C[t-1] - 1 (noto alla chiusura di t, cioe' alle 00:00 di t+1)."""
    with np.errstate(all="ignore"):
        r = C[1:] / C[:-1] - 1
    return np.vstack([np.full((1, C.shape[1]), np.nan), r])


def ritorni_tenuta(O: np.ndarray, C: np.ndarray) -> np.ndarray:
    """Apertura di t -> apertura di t+1 (chiusura di t se la candela dopo manca); 0 dove non c'e' prezzo."""
    dopo = np.vstack([O[1:], np.full((1, O.shape[1]), np.nan)])
    dopo = np.where(np.isfinite(dopo), dopo, C)
    with np.errstate(all="ignore"):
        r = dopo / O - 1
    return np.where(np.isfinite(r), r, 0.0)


def universo_lunedi(pan: dict, m: int, escludi=()) -> np.ndarray:
    """Le 100 del lunedi' (indice m): chiusura della domenica, 200 giorni di vita, mediana del volume dei 30 giorni prima
    >= 2 milioni, apertura del lunedi', volume della domenica > 0; ordinate per mediana."""
    C, O, V = pan["close"], pan["open"], pan["quote_volume"]
    ok = np.isfinite(C)
    primo = np.where(ok.any(axis=0), ok.argmax(axis=0), C.shape[0])
    with np.errstate(all="ignore"):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            med = np.nan_to_num(np.nanmedian(V[max(0, m - 30):m], axis=0), nan=0.0)
    amm = ok[m - 1] & (m - primo >= STORIA) & (med >= VOL_MIN) & np.isfinite(O[m]) & (np.nan_to_num(V[m - 1]) > 0)
    for j in escludi:
        amm[j] = False
    cand = np.flatnonzero(amm)
    scelte = cand[np.argsort(-med[cand], kind="stable")][:N_UNI]
    u = np.zeros(C.shape[1], bool)
    u[scelte] = True
    return u


def universo_giorni(pan: dict, idx: np.ndarray, escludi=()) -> np.ndarray:
    giorni = idx + pan["t0"]
    lun = giorni - ((giorni + 3) % 7) - pan["t0"]
    cache = {}
    out = np.zeros((len(idx), pan["close"].shape[1]), bool)
    for k, m in enumerate(lun):
        if m not in cache:
            cache[m] = universo_lunedi(pan, int(m), escludi)
        out[k] = cache[m]
    return out


def funding7(F: np.ndarray, i: int) -> np.ndarray:
    """Somma del funding dei 7 giorni di tenuta prima di i (fino al regolamento delle 00:00 di i), a 12 decimali."""
    return np.round(F[i - 7:i].sum(axis=0), 12)


def sigma30(rc: np.ndarray, i: int) -> np.ndarray:
    f = rc[i - 30:i]
    n = np.isfinite(f).sum(axis=0)
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sd = np.nanstd(f, axis=0, ddof=1)
    return np.where((n >= 20) & (sd > 0), sd, np.nan)


def beta90(rc: np.ndarray, u: np.ndarray, i: int) -> np.ndarray:
    """Pendenza dei rendimenti (chiusura su chiusura, giorni i-90..i-1) sulla media dell'universo u; 1 con meno di 45 giorni."""
    blocco = rc[i - G_BETA:i]
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mkt = np.nanmean(np.where(u[None, :], blocco, np.nan), axis=1)
    out = np.ones(rc.shape[1])
    msk = np.isfinite(mkt)[:, None] & np.isfinite(blocco)
    n = msk.sum(axis=0)
    x = np.where(msk, mkt[:, None], 0.0)
    y = np.where(msk, blocco, 0.0)
    with np.errstate(all="ignore"):
        mx, my = x.sum(0) / n, y.sum(0) / n
        vx = (x * x).sum(0) / n - mx * mx
        cv = (x * y).sum(0) / n - mx * my
        b = cv / vx
    buono = u & (n >= MIN_BETA) & (vx > 1e-18) & np.isfinite(b)
    out[buono] = b[buono]
    return out


def passo_banda(ct, u, sig, lunghi, corti):
    idx = np.flatnonzero(u & np.isfinite(ct) & np.isfinite(sig) & (sig > 0))
    w = np.zeros(len(u))
    if len(idx) < MIN_MONETE:
        return w, set(), set()
    p = rankdata(ct[idx], method="average") / len(idx)
    rango = dict(zip(idx.tolist(), p))
    lunghi = {j for j in lunghi if rango.get(j, 0.0) >= 1 - RESTA} | {j for j, q in rango.items() if q > 1 - ENTRA}
    corti = {j for j in corti if rango.get(j, 1.0) <= RESTA} | {j for j, q in rango.items() if q <= ENTRA}
    for lato, segno in ((sorted(lunghi), 1.0), (sorted(corti), -1.0)):
        if lato:
            inv = 1.0 / sig[lato]
            w[lato] = segno * inv / inv.sum()
    return w, lunghi, corti


def scala(w: np.ndarray, beta: np.ndarray, limiti=(0.5, 1.5)):
    L, S = w > 0, w < 0
    if not L.any() or not S.any():
        return w.copy(), 1.0, 1.0, np.nan, np.nan
    bl = float((w[L] * beta[L]).sum() / w[L].sum())
    bs = float((-w[S] * beta[S]).sum() / (-w[S]).sum())
    if bl + bs <= 0:
        return w.copy(), 1.0, 1.0, bl, bs
    a = float(np.clip(2 * bs / (bl + bs), *limiti))
    b = float(np.clip(2 * bl / (bl + bs), *limiti))
    out = w.copy()
    out[L] *= a
    out[S] *= b
    return out, a, b, bl, bs


def tetto_lato(w: np.ndarray, tetto: float) -> np.ndarray:
    """Ogni lato con un tetto per moneta (frazione del lato): l'eccesso va alle altre in proporzione (riempimento ad acqua)."""
    out = w.copy()
    for segno in (1.0, -1.0):
        lato = np.flatnonzero(np.sign(w) == segno)
        if not len(lato):
            continue
        v = np.abs(w[lato])
        tot = v.sum()
        v = v / tot
        if len(lato) * tetto < 1:
            v = np.full(len(lato), tetto)
        else:
            fissi = np.zeros(len(lato), bool)
            for _ in range(len(lato)):
                sopra = (v > tetto + 1e-15) & ~fissi
                if not sopra.any():
                    break
                fissi |= sopra
                v[fissi] = tetto
                resto = 1 - tetto * fissi.sum()
                liberi = ~fissi
                v[liberi] = v[liberi] / v[liberi].sum() * resto
        out[lato] = segno * v * tot
    return out


def pesi(pan: dict, idx: np.ndarray, U: np.ndarray, beta_ritardo: int = 0, tetto=None, fisso=None, limiti=(0.5, 1.5)):
    """I pesi di G1 (W) e di G1N (WN) giorno per giorno, piu' a, b, beta dei lati e i beta delle monete."""
    rc = ritorni_chiusura(pan["close"])
    F = pan["funding"]
    S = rc.shape[1]
    W = np.zeros((len(idx), S))
    WN = np.zeros((len(idx), S))
    A, B, BL, BS = (np.full(len(idx), np.nan) for _ in range(4))
    lunghi, corti = set(), set()
    for k, i in enumerate(idx):
        sig = sigma30(rc, i)
        ct = np.where(np.isfinite(sig), -funding7(F, i), np.nan)
        w, lunghi, corti = passo_banda(ct, U[k], sig, lunghi, corti)
        if tetto is not None:
            w = tetto_lato(w, tetto)
        W[k] = w
        if fisso is not None:
            WN[k] = np.where(w > 0, w * fisso[0], w * fisso[1])
            continue
        beta = beta90(rc, U[k], i - beta_ritardo)
        WN[k], A[k], B[k], BL[k], BS[k] = scala(w, beta, limiti)
    return W, WN, {"a": A, "b": B, "bl": BL, "bs": BS}


def variazioni(W: np.ndarray, R: np.ndarray, F: np.ndarray, costo: np.ndarray):
    """Conto giornaliero a mercato e variazioni di peso (con i pesi che derivano col prezzo)."""
    T, S = W.shape
    deriva = np.zeros(S)
    D = np.zeros_like(W)
    lordo, spese, fund = np.zeros(T), np.zeros(T), np.zeros(T)
    for k in range(T):
        x = W[k]
        D[k] = x - deriva
        lordo[k] = float(x @ R[k])
        fund[k] = float(x @ F[k])
        spese[k] = float(np.abs(D[k]) @ costo)
        netto = lordo[k] - spese[k] - fund[k]
        deriva = x * (1 + R[k]) / (1 + netto) if 1 + netto > 0 else np.zeros(S)
    return lordo, spese, fund, D


def spese_limite(D: np.ndarray, giorni: np.ndarray, simboli: list, costo: np.ndarray, ore: dict, oltre: float = 0.0):
    """Le spese con le variazioni a ordine limite all'apertura delle 00:00 per un'ora: eseguito se il minimo (chi compra) o il
    massimo (chi vende) passano l'apertura di almeno ``oltre``; altrimenti a mercato alle 01:00 con il movimento contro."""
    sp = np.zeros(D.shape[0])
    n = n_lim = 0
    for j in np.flatnonzero(np.abs(D).sum(axis=0) > 0):
        b = ore.get(simboli[j])
        for k in np.flatnonzero(np.abs(D[:, j]) > 1e-9):
            dw = D[k, j]
            h = int(giorni[k]) * 24
            n += 1
            if b is None or h not in b or h + 1 not in b:
                sp[k] += abs(dw) * costo[j]
                continue
            o, hi, lo, _ = b[h]
            p1 = b[h + 1][0]
            if not all(np.isfinite([o, hi, lo, p1])):
                sp[k] += abs(dw) * costo[j]
                continue
            compra = dw > 0
            preso = (lo < o * (1 - oltre)) if compra else (hi > o * (1 + oltre))
            if preso:
                sp[k] += abs(dw) * MAKER
                n_lim += 1
            else:
                contro = (p1 / o - 1) if compra else (1 - p1 / o)
                sp[k] += abs(dw) * (costo[j] + contro)
    return sp, n, n_lim


def numeri(x: np.ndarray, per_anno: int = 52) -> dict:
    x = np.asarray(x, float)
    sd = x.std(ddof=1)
    eq = np.cumprod(1 + x)
    return {"n": int(len(x)), "annuo": float(x.mean() * per_anno), "vol": float(sd * np.sqrt(per_anno)),
            "sharpe": float(x.mean() / sd * np.sqrt(per_anno)) if sd > 0 else 0.0,
            "discesa": float((eq / np.maximum.accumulate(eq) - 1).min())}
