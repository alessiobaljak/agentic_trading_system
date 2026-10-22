"""Programma 6, cinquantaduesima prova (CINQUANTADUESIMA.md): B1, scommettere contro il beta fra le 100 monete, con la
banda di F5 e i lati scalati per essere neutri al Bitcoin (al massimo 2 volte).

Uso: python3 -m research.programma6.cinquantaduesima
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq

QUI = Path(__file__).parent
RIS = QUI / "risultati_cinquantaduesima"
GIORNI_BETA, MINIMO, TETTO = 90, 60, 2.0


def beta(pan: dict, lun: np.ndarray) -> np.ndarray:
    C = pan["close"]
    with np.errstate(all="ignore"):
        r = np.vstack([np.full((1, C.shape[1]), np.nan), C[1:] / C[:-1] - 1])
    jb = pan["simboli"].index("BTCUSDT")
    out = np.full((len(lun), C.shape[1]), np.nan)
    for k, m in enumerate(lun):
        f = r[max(0, m - GIORNI_BETA): m]
        b = f[:, jb]
        ok = np.isfinite(f) & np.isfinite(b)[:, None]
        n = ok.sum(axis=0)
        x = np.where(ok, b[:, None], np.nan)
        y = np.where(ok, f, np.nan)
        mx, my = np.nanmean(x, axis=0), np.nanmean(y, axis=0)
        cov = np.nansum((x - mx) * (y - my), axis=0)
        var = np.nansum((x - mx) ** 2, axis=0)
        out[k] = np.where((n >= MINIMO) & (var > 0), cov / np.where(var > 0, var, 1), np.nan)
    return out


def neutro(W: np.ndarray, B: np.ndarray) -> tuple:
    """I lati scalati per 1/beta medio pesato (al massimo 2 volte); e le leve usate."""
    out = W.copy()
    leve = []
    for k in range(W.shape[0]):
        lati = []
        for segno in (1, -1):
            idx = np.flatnonzero(np.sign(W[k]) == segno)
            if not len(idx):
                lati.append(np.nan)
                continue
            bm = float(np.nansum(np.abs(W[k, idx]) * B[k, idx]))
            leva = min(TETTO, 1.0 / bm) if bm > 0 else TETTO
            out[k, idx] *= leva
            lati.append(leva)
        leve.append(lati)
    return out, np.array(leve)


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    B = beta(pan, lun)
    ct = np.where(np.isfinite(sig) & np.isfinite(B), -B, np.nan)
    W, leve = neutro(vq.pesi_banda(ct, ps["U"], sig), B)
    df = te.conto(W, ps["R"], ps["F"], sc.costi_moneta(ps["simboli"]))
    df.index = ps["lunedi"]
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_B1.csv.gz")
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
    f5 = pd.read_csv(QUI / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0)["netto"]
    comuni = df.index[(df.index >= se.INIZIO)].intersection(f5.index)
    e["correlazione_F5"] = float(np.corrcoef(df.loc[comuni, "netto"], f5.loc[comuni])[0, 1])
    dentro = ps["lunedi"] >= se.INIZIO
    e["leva_media"] = {"long": float(np.nanmean(leve[dentro, 0])), "short": float(np.nanmean(leve[dentro, 1]))}
    x49 = {f"49 {k}": pd.read_csv(QUI / "risultati_quarantanovesima" / f"settimane_{k}.csv.gz", index_col=0)["netto"] for k in ("X1", "X2")}
    f7 = pd.read_csv(QUI / "risultati_cinquantunesima" / "settimane_F7.csv.gz", index_col=0)["netto"]
    rivisto = ast.corretto_rivisto({**x49, "51 F7": f7, "52 B1": df["netto"]}, {"52 B1": e["intero"]})
    r = rivisto["candidate"]["52 B1"]
    e["sharpe_corretto"], e["t"], e["gruppo"], e["gruppi"] = r["corretto"], r["t"], r["gruppo"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i = e["intero"]
    testo = "\n".join([
        "# Programma 6 — risultati della cinquantaduesima prova (B1: scommettere contro il beta)", "",
        "Regole in `CINQUANTADUESIMA.md` (scritte prima).", "",
        f"* Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
        f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; beta verso il Bitcoin {e['beta_btc']:.2f}; "
        f"leva media long {e['leva_media']['long']:.2f}, short {e['leva_media']['short']:.2f}; correlazione con F5 {e['correlazione_F5']:.2f}.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto rivisto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t dello Sharpe {e['t']:.2f}; gruppo: "
        + ", ".join(e["gruppo"]) + ".", "", f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_CINQUANTADUESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("CINQUANTADUESIMA FINITA", flush=True)
