"""Programma 8, prima prova (PRIMA.md): S1 e S2, il lato long di F5 comprato a pronti (a settimana e ogni giorno), con le
commissioni dello spot e senza funding; confronto con il paniere delle stesse monete e con il Bitcoin tenuto.

Uso: python3 -m research.programma8.prima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma5.strumenti import motore5 as m5
from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma6.motore import TAKER
from research.programma7 import prima as pr

QUI = Path(__file__).parent
RIS = QUI / "risultati_prima"
COMMISSIONE_SPOT = 0.0010


def pannello_spot(pan: dict) -> dict:
    """Giorni × monete: apertura, chiusura e volume in dollari della coppia contro USDT a pronti (NaN dove manca)."""
    T, S = pan["close"].shape
    O, C, V = (np.full((T, S), np.nan) for _ in range(3))
    for j, s in enumerate(pan["simboli"]):
        for f in sorted((sc.DATI / s / "spot").glob("*.zip")):
            if not f.with_suffix(".zip.ok").exists():
                continue
            df = m5._csv_da_zip(f, m5.KLINE)
            g = (m5._ms(df["open_time"]).to_numpy() // 86_400_000 - pan["t0"]).astype(np.int64)
            ok = (g >= 0) & (g < T)
            O[g[ok], j] = df["open"].to_numpy(float)[ok]
            C[g[ok], j] = df["close"].to_numpy(float)[ok]
            V[g[ok], j] = df["quote_volume"].to_numpy(float)[ok]
    return {"open": O, "close": C, "quote_volume": V}


def solo_long(W: np.ndarray) -> np.ndarray:
    return np.where(W > 0, W, 0.0)


def pesi_paniere(U: np.ndarray, sig: np.ndarray) -> np.ndarray:
    """Tutte le monete dell'universo con pesi 1/volatilita', il 100% del capitale (la stessa regola di S1 senza la scelta)."""
    W = np.zeros(U.shape)
    for k in range(U.shape[0]):
        idx = np.flatnonzero(U[k] & np.isfinite(sig[k]) & (sig[k] > 0))
        if len(idx) >= te.MIN_MONETE:
            inv = 1.0 / sig[k, idx]
            W[k, idx] = inv / inv.sum()
    return W


def differenza(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """La serie settimanale a − b, nella forma che `terza.esame` si aspetta."""
    c = a.index.intersection(b.index)
    d = pd.DataFrame({"netto": a.loc[c, "netto"] - b.loc[c, "netto"],
                      "netto_doppio": a.loc[c, "netto_doppio"] - b.loc[c, "netto_doppio"]}, index=c)
    for k in ("lordo", "spese", "funding", "giro", "long", "short"):
        d[k] = 0.0
    d["monete"] = 1
    return d


def esegui(log=print) -> dict:
    pan = sc.pannello()
    sp = pannello_spot(pan)
    log(f"[programma8] monete con lo spot: {int(np.isfinite(sp['close']).any(axis=0).sum())}")
    r_s = sc.rendimenti(sp)
    r_s[~np.isfinite(sp["open"])] = 0.0
    lr = np.log1p(np.clip(r_s, -0.999999, None))
    cum = np.vstack([np.zeros((1, lr.shape[1])), np.cumsum(lr, axis=0)])
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    costo = sc.costi_moneta(pan["simboli"]) - TAKER + COMMISSIONE_SPOT          # lo scarto della moneta, la commissione dello spot
    zero = np.zeros_like(ps["F"])
    # a settimana
    U = ps["U"] & np.isfinite(sp["open"][lun]) & (np.nan_to_num(sp["quote_volume"][lun - 1]) > 0)
    R = np.expm1(cum[lun + 7] - cum[lun])
    sig = ot.sigma_30(pan, lun)
    W = solo_long(vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, lun), np.nan), U, sig))
    s1 = te.conto(W, R, zero, costo)
    pan_w = te.conto(pesi_paniere(U, sig), R, zero, costo)
    s1.index = pan_w.index = ps["lunedi"]
    # ogni giorno
    giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"]) & np.isfinite(sp["open"][idx]) & \
        (np.nan_to_num(sp["quote_volume"][idx - 1]) > 0)
    sigd = ot.sigma_30(pan, idx)
    Wd = solo_long(vq.pesi_banda(np.where(np.isfinite(sigd), -se.funding_7(pan, idx), np.nan), Ud, sigd))
    s2 = pr.per_settimana(te.conto(Wd, r_s[idx], np.zeros_like(r_s[idx]), costo), giorni)
    RIS.mkdir(exist_ok=True)
    for n, d in (("S1", s1), ("S2", s2), ("paniere", pan_w)):
        d.to_csv(RIS / f"settimane_{n}.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    fine = lambda d: d[d.index < pr.FINE]  # noqa: E731
    out = {}
    for n, d in (("S1", s1), ("S2", s2), ("paniere", pan_w)):
        out[n] = te.esame(fine(d), btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    f5 = pd.read_csv(QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)
    f5l = f5.assign(netto=f5["long"], netto_doppio=f5["long"])
    out["F5 lato long nei future"] = te.esame(fine(f5l), btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    for n, d in (("S1 − paniere", differenza(fine(s1), fine(pan_w))), ("S2 − paniere", differenza(fine(s2), fine(pan_w)))):
        out[n] = te.esame(d, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    tenuto = btc[(btc.index >= se.INIZIO) & (btc.index < pr.FINE)]
    out["btc_tenuto"] = {"sharpe": float(tenuto.mean() / tenuto.std() * np.sqrt(52)), "annuo": float(tenuto.mean() * 52)}
    nuove = {**ast.serie_nuove(), "73 S1": s1["netto"], "73 S2": s2["netto"]}
    rivisto = ast.corretto_rivisto(nuove, {"73 S1": out["S1"]["intero"], "73 S2": out["S2"]["intero"]})
    for n in ("S1", "S2"):
        r = rivisto["candidate"][f"73 {n}"]
        out[n]["sharpe_corretto"], out[n]["t"] = r["corretto_con_aggiunta"], r["t"]
        out[n]["esito"] = te.esito(out[n], out[n]["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 8 — risultati della prima prova (il lato long di F5 a pronti: S1 a settimana, S2 ogni giorno)", "",
             "Regole in `PRIMA.md` (scritte prima). Dal 4 gennaio 2021.", "",
             "| | Sharpe | l'anno | volatilità | discesa | spese l'anno |", "|---|---|---|---|---|---|"]
    for n in ("S1", "S2", "paniere", "F5 lato long nei future"):
        i = out[n]["intero"]
        righe.append(f"| {n} | {i['sharpe']:.2f} | {100 * i['annuo']:+.1f}% | {100 * i['volatilita']:.1f}% | {100 * i['discesa_max']:.1f}% | "
                     f"{100 * out[n].get('spese_annue', 0):.1f}% |")
    b = out["btc_tenuto"]
    righe += [f"| Bitcoin tenuto | {b['sharpe']:.2f} | {100 * b['annuo']:+.1f}% | | | |", ""]
    for n in ("S1 − paniere", "S2 − paniere"):
        x = out[n]
        righe.append(f"* **{n}** (quanto aggiunge la scelta delle monete): {100 * x['intero']['annuo']:+.1f}% l'anno, intervallo della media "
                     f"settimanale {100 * x['boot']['basso']:+.3f}%; {100 * x['boot']['alto']:+.3f}% (p {x['boot']['p']:.4f}).")
    righe += [""] + [f"* {n} per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in out[n]["per_anno"].items()) for n in ("S1", "S2", "paniere")]
    righe += ["", f"**Esito**: S1 {out['S1']['esito']} (Sharpe corretto {out['S1']['sharpe_corretto']:.2f}); S2 {out['S2']['esito']} "
              f"(Sharpe corretto {out['S2']['sharpe_corretto']:.2f})."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_PRIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("PROGRAMMA 8 PRIMA FINITA", flush=True)
