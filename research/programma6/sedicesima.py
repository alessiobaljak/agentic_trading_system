"""Programma 6, sedicesima prova (SEDICESIMA.md): M3, il modello ad alberi di M1 che decide ogni giorno (obiettivo: il
rango del rendimento del giorno dopo), riallenato ogni 28 giorni sugli ultimi 730; portafoglio con entrata al 20% e uscita
al 40%, pesi secondo la volatilita'.

Uso: python3 -m research.programma6.sedicesima
"""
from __future__ import annotations

import json
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_sedicesima"
OGNI, MAX_G, MIN_G = 28, 730, 365
ENTRA, RESTA = 0.20, 0.40


def universo_giornaliero(pan: dict, ps: dict) -> np.ndarray:
    """Ud[t]: l'universo della settimana che contiene il giorno di tenuta t+1."""
    T, S = pan["close"].shape
    Ud = np.zeros((T, S), bool)
    lun = ps["lunedi"] - pan["t0"]
    for k, m in enumerate(lun):
        a, b = max(0, m - 1), min(T, m + 6)          # decisioni dalla domenica prima al sabato
        Ud[a:b] = ps["U"][k]
    return Ud


def indicatori_giornalieri(pan: dict, colonne: np.ndarray) -> np.ndarray:
    C, O, H, L, V = (pan[k] for k in ("close", "open", "high", "low", "quote_volume"))
    T = C.shape[0]
    Z = np.full((T, len(colonne), len(te.NOMI)), np.nan, np.float32)
    for c, j in enumerate(colonne):
        ok = np.flatnonzero(np.isfinite(C[:, j]))
        if len(ok) < te.STORIA_MIN:
            continue
        Z[ok, c] = te.indicatori(O[ok, j], H[ok, j], L[ok, j], C[ok, j], V[ok, j])
    return Z


def tabella(pan: dict, Ud: np.ndarray, colonne: np.ndarray) -> tuple:
    """(X: giorni × monete scelte × ingredienti, nomi, Y: rango del rendimento del giorno dopo)."""
    U = Ud[:, colonne]
    Z = indicatori_giornalieri(pan, colonne)
    g = q.ingredienti_giornalieri(pan)
    nomi, strati = [], []
    for k in range(Z.shape[2]):
        nomi.append(te.NOMI[k])
        strati.append(q.rango_nan(Z[:, :, k].astype(float), U).astype(np.float32))
    for n, a in g.items():
        nomi.append(n)
        strati.append(q.rango_nan(a[:, colonne], U).astype(np.float32))
    jb = pan["simboli"].index("BTCUSDT")
    S = len(colonne)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        r7 = np.where(U, g["rend_7"][:, colonne], np.nan)
        mercato = {"btc_rend_7": g["rend_7"][:, jb], "btc_rend_30": g["rend_30"][:, jb], "btc_vol_30": g["vol_30"][:, jb],
                   "funding_mercato_7": np.nanmean(np.where(U, g["funding_7"][:, colonne], np.nan), axis=1),
                   "rend_mercato_7": np.nanmean(r7, axis=1), "dispersione_7": np.nanstd(r7, axis=1)}
    for n, v in mercato.items():
        nomi.append(n)
        strati.append(np.repeat(np.asarray(v, np.float32)[:, None], S, axis=1))
    X = np.stack(strati, axis=2)
    r = sc.rendimenti(pan)[:, colonne]
    domani = np.vstack([r[1:], np.full((1, S), np.nan)])
    ok_domani = np.vstack([np.isfinite(pan["open"][1:, colonne]), np.zeros((1, S), bool)])
    Y = q.rango_nan(np.where(ok_domani, domani, np.nan), U & ok_domani).astype(np.float32)
    return X, nomi, Y, U


def previsioni(X, Y, U, giorni, log=print) -> np.ndarray:
    T = X.shape[0]
    P = np.full(U.shape, np.nan, np.float32)
    inizio = int(np.searchsorted(giorni, q.INIZIO))
    valide = np.array([(U[u] & np.isfinite(Y[u])).sum() >= te.MIN_MONETE for u in range(T)])
    for t0 in range(inizio, T, OGNI):
        # si allena sui giorni il cui obiettivo (il giorno dopo) e' gia' concluso alla decisione di t0
        allen = [u for u in range(max(0, t0 - MAX_G), t0 - 1) if valide[u]]
        if len(allen) < MIN_G:
            continue
        xs, ys = [], []
        for u in allen:
            idx = np.flatnonzero(U[u] & np.isfinite(Y[u]))
            xs.append(X[u, idx])
            ys.append(Y[u, idx])
        Xa, Ya = np.vstack(xs), np.concatenate(ys)
        cols = np.isfinite(Xa).any(axis=0)
        m = q._modello("M1")
        m.fit(Xa[:, cols], Ya)
        for t in range(t0, min(t0 + OGNI, T)):
            idx = np.flatnonzero(U[t])
            if len(idx) >= te.MIN_MONETE:
                P[t, idx] = m.predict(X[t, idx][:, cols])
        log(f"[sedicesima] allenato al {sc.data(int(giorni[t0]))} su {len(Ya)} righe")
    return P


def pesi_isteresi(P: np.ndarray, U: np.ndarray, sig: np.ndarray) -> np.ndarray:
    T, S = P.shape
    W = np.zeros((T, S))
    lunghi, corti = set(), set()
    for t in range(T):
        idx = np.flatnonzero(U[t] & np.isfinite(P[t]) & np.isfinite(sig[t]) & (sig[t] > 0))
        if len(idx) < te.MIN_MONETE:
            lunghi, corti = set(), set()
            continue
        pr = pd.Series(P[t, idx]).rank(pct=True).to_numpy()
        rango = dict(zip(idx.tolist(), pr))
        lunghi = {j for j in lunghi if rango.get(j, 0) >= 1 - RESTA} | {j for j, p in rango.items() if p >= 1 - ENTRA}
        corti = {j for j in corti if rango.get(j, 1) <= RESTA} | {j for j, p in rango.items() if p <= ENTRA}
        for lato, segno in ((sorted(lunghi), 1.0), (sorted(corti), -1.0)):
            if lato:
                inv = 1.0 / sig[t, lato]
                W[t, lato] = segno * inv / inv.sum()
    return W


def sigma_giornaliera(pan: dict, colonne: np.ndarray) -> np.ndarray:
    C = pd.DataFrame(pan["close"][:, colonne])
    with np.errstate(all="ignore"):
        lr = np.log(C).diff()
    return lr.rolling(30, min_periods=20).std().to_numpy()


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    Ud = universo_giornaliero(pan, ps)
    colonne = np.flatnonzero(Ud.any(axis=0))
    log(f"[sedicesima] {len(colonne)} monete passate dall'universo")
    X, nomi, Y, U = tabella(pan, Ud, colonne)
    giorni = np.arange(X.shape[0]) + pan["t0"]
    P = previsioni(X, Y, U, giorni, log)
    sig = sigma_giornaliera(pan, colonne)
    Wc = pesi_isteresi(P, U, sig)
    W = np.zeros(pan["close"].shape)
    W[:, colonne] = Wc
    # nessuna posizione dove manca la candela di domani (moneta tolta dal listino)
    domani = np.vstack([np.isfinite(pan["open"][1:]), np.zeros((1, W.shape[1]), bool)])
    W = np.where(domani, W, 0.0)
    df = sc.portafoglio(pan, W)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "giorni_M3.csv.gz")
    r = sc.rendimenti(pan)
    jb = pan["simboli"].index("BTCUSDT")
    btc = pd.Series(r[:, jb], index=giorni)
    d = df[df.index >= q.INIZIO]
    e = sc.esame_a(d, btc)
    sr = q.tutte_le_prove()
    ee = json.loads((QUI / "risultati_quattordicesima" / "esame.json").read_text())
    sr += [ee["M1"]["intero"]["sharpe"], ee["M2"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_quindicesima" / "esame.json").read_text())["intero"]["sharpe"], e["intero"]["sharpe"]]
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["giorni"], i["asimmetria"], i["curtosi"], sr, 365)
    e["prove_nel_conto"] = len(sr)
    es = "VALIDA"
    if not e["boot"]["basso"] > 0:
        es = "netto con l'intervallo non sopra zero"
    elif not e["sharpe_corretto"] >= 0.95:
        es = f"Sharpe corretto {e['sharpe_corretto']:.2f} sotto 0,95"
    elif sum(1 for v in e["per_anno"].values() if v > 0) < 4:
        es = "positiva in meno di 4 anni"
    elif not e["ultimo_anno"] > 0:
        es = "non positiva nell'ultimo anno"
    elif not e["costi_doppi"] > 0:
        es = "non positiva a costi doppi"
    elif not e["extra_btc_annuo"] > 0:
        es = "niente in più del Bitcoin"
    e["esito"] = es
    # correlazione settimanale con F3 e M1
    sett = d["netto"].groupby(((d.index.to_numpy() + 3) // 7) * 7 - 3).sum()
    for n, f in (("F3", QUI / "risultati_ottava" / "settimane_F3.csv.gz"), ("M1", QUI / "risultati_quattordicesima" / "settimane_M1.csv.gz")):
        s = pd.read_csv(f, index_col=0)["netto"]
        c = sett.index.intersection(s.index)
        e[f"correlazione_{n}"] = float(np.corrcoef(sett.loc[c], s.loc[c])[0, 1]) if len(c) > 10 else float("nan")
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    pa = e["per_anno"]
    testo = "\n".join([
        "# Programma 6 — risultati della sedicesima prova (M3: il modello ogni giorno)", "",
        "Regole in `SEDICESIMA.md` (scritte prima). Dal 3 gennaio 2022; riallenato ogni 28 giorni solo sul passato.", "",
        f"* {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, **Sharpe {i['sharpe']:.2f}**, discesa massima "
        f"{100 * i['discesa_max']:.1f}%; media giornaliera {100 * e['boot']['media']:+.4f}% (intervallo "
        f"{100 * e['boot']['basso']:+.4f}; {100 * e['boot']['alto']:+.4f}).",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in pa.items()) + f"; ultimo anno {100 * e['ultimo_anno']:+.1f}%.",
        f"* Giro {e['giro_annuo']:.0f} volte il capitale l'anno; spese {100 * e['spese_annue']:.1f}% l'anno; funding "
        f"{100 * e['funding_annuo']:+.1f}% (pagato); a costi doppi {100 * e['costi_doppi']:+.4f}% al giorno.",
        f"* Correlazione settimanale con F3 {e['correlazione_F3']:.2f}, con M1 {e['correlazione_M1']:.2f}.",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} con {e['prove_nel_conto']} prove.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_SEDICESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("SEDICESIMA FINITA", flush=True)
