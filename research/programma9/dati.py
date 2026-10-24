"""Programma 9 (METODO.md): la tabella moneta-giorno con tutti gli ingredienti e i rendimenti dopo (meno la media dell'universo).

Scrive due file separati in research/data/p9: `esplorazione.pkl` (dal 2022-01-01 al 2023-12-24: i rendimenti a 7 giorni non
toccano il 2024) e `conferma.pkl` (dal 2024-01-01 al 2026-06-26). Il programma di esplorazione legge solo il primo.

Uso: python3 -m research.programma9.dati
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import terza as te
from research.programma6 import undicesima as un
from research.programma7 import prima as pr
from research.programma8 import prima as p8

DATI = Path(__file__).resolve().parents[2] / "research" / "data" / "p9"
DA, FINE_ESPLORAZIONE = sc.giorno(2022, 1, 1), sc.giorno(2023, 12, 24)
DA_CONFERMA, A = sc.giorno(2024, 1, 1), sc.giorno(2026, 6, 26)
ORIZZONTI = (1, 3, 7)


def _somma(x: np.ndarray, n: int) -> np.ndarray:
    """Somma degli ultimi n giorni (t compreso) lungo il tempo; NaN se mancano."""
    c = np.nancumsum(np.nan_to_num(x), axis=0)
    out = np.full(x.shape, np.nan)
    out[n:] = c[n:] - c[:-n]
    return out


def _rolling(x: np.ndarray, n: int, f) -> np.ndarray:
    return pd.DataFrame(x).rolling(n, min_periods=max(2, n * 2 // 3)).agg(f).to_numpy()


def costruisci(log=print) -> pd.DataFrame:
    pan = sc.pannello()
    t0, simboli = pan["t0"], pan["simboli"]
    T, S = pan["close"].shape
    C, O, H, L = pan["close"], pan["open"], pan["high"], pan["low"]
    V, TB, F = pan["quote_volume"], pan["taker_buy_quote_volume"], pan["funding"]
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        lr = np.log(C / np.roll(C, 1, axis=0))
        lr[0] = np.nan
        ing = {
            "r1": C / np.roll(C, 1, axis=0) - 1, "r3": C / np.roll(C, 3, axis=0) - 1,
            "r7": C / np.roll(C, 7, axis=0) - 1, "r30": C / np.roll(C, 30, axis=0) - 1,
            "max1d30": _rolling(np.expm1(lr), 30, "max"), "min1d30": _rolling(np.expm1(lr), 30, "min"),
            "vol30": _rolling(lr, 30, "std"),
            "dist_hi30": C / _rolling(H, 30, "max") - 1, "dist_lo30": C / _rolling(L, 30, "min") - 1,
            "volrel": V / _rolling(V, 30, "mean"),
            "taker1": TB / V, "taker7": _somma(TB, 7) / _somma(V, 7),
            "f1": F, "f7": _somma(F, 7), "fchg": F - _somma(F, 7) / 7,
            "ampiezza": H / L - 1,
        }
        vive = np.isfinite(C)
        primo = np.where(vive.any(axis=0), vive.argmax(axis=0), T)
        ing["eta"] = np.arange(T)[:, None] - primo[None, :]
        pm = un.pannello_metrics(pan)
        oi = pm["oi"]
        ing.update({"oi1": np.log(oi / np.roll(oi, 1, axis=0)), "oi7": np.log(oi / np.roll(oi, 7, axis=0)),
                    "oi30": np.log(oi / np.roll(oi, 30, axis=0)), "oi_su_volume": oi / _rolling(V, 7, "mean"),
                    "ls_grandi": np.log(pm["grandi"]), "ls_tutti": np.log(pm["tutti"]),
                    "ls_diff": np.log(pm["grandi"]) - np.log(pm["tutti"])})
        sp = p8.pannello_spot(pan)
        ing["quota_spot"] = _rolling(sp["quote_volume"], 7, "mean") / (_rolling(sp["quote_volume"], 7, "mean") + _rolling(V, 7, "mean"))
    jb = simboli.index("BTCUSDT")
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(DA, A + 1, dtype=np.int64)
    idx = giorni - t0
    U = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    fwd = {}
    for h in ORIZZONTI:
        with np.errstate(all="ignore"):
            r = np.roll(C, -h, axis=0) / C - 1
        r[-h:] = np.nan
        fwd[h] = r
    righe = []
    for k, (g, i) in enumerate(zip(giorni, idx)):
        js = np.flatnonzero(U[k] & np.isfinite(C[i]))
        if len(js) < 20:
            continue
        riga = {"giorno": np.full(len(js), g), "simbolo": np.array(simboli)[js]}
        for n, x in ing.items():
            riga[n] = x[i, js]
        riga["btc_r7"] = np.full(len(js), C[i, jb] / C[i - 7, jb] - 1)
        riga["btc_r30"] = np.full(len(js), C[i, jb] / C[i - 30, jb] - 1)
        riga["mercato_f7"] = np.full(len(js), np.nanmean(ing["f7"][i, js]))
        for h in ORIZZONTI:
            y = fwd[h][i, js]
            riga[f"y{h}"] = y - np.nanmean(y)
        righe.append(pd.DataFrame(riga))
    df = pd.concat(righe, ignore_index=True)
    df = df.replace([np.inf, -np.inf], np.nan)
    DATI.mkdir(parents=True, exist_ok=True)
    df[df["giorno"] <= FINE_ESPLORAZIONE].to_pickle(DATI / "esplorazione.pkl")
    df[df["giorno"] >= DA_CONFERMA].to_pickle(DATI / "conferma.pkl")
    log(f"[p9 dati] {len(df)} righe moneta-giorno, {df['simbolo'].nunique()} monete; esplorazione "
        f"{int((df['giorno'] <= FINE_ESPLORAZIONE).sum())}, conferma {int((df['giorno'] >= DA_CONFERMA).sum())}")
    return df


if __name__ == "__main__":
    costruisci()
