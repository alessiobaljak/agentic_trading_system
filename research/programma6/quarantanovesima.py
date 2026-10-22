"""Programma 6, quarantanovesima prova (QUARANTANOVESIMA.md): X1 il momento delle 3 settimane e X2 la dimensione (le
piccole contro le grandi) fra le 100 monete, con la banda di F5; esame con lo Sharpe corretto rivisto (`asticella.py`).

Uso: python3 -m research.programma6.quarantanovesima
"""
from __future__ import annotations

import json
import math
import warnings
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
RIS = QUI / "risultati_quarantanovesima"


def momento(pan: dict, lun: np.ndarray) -> np.ndarray:
    C = pan["close"]
    out = np.full((len(lun), C.shape[1]), np.nan)
    for k, m in enumerate(lun):
        if m - 22 >= 0:
            with np.errstate(all="ignore"):
                out[k] = C[m - 1] / C[m - 22] - 1
    return out


def dimensione(pan: dict, lun: np.ndarray) -> np.ndarray:
    """Meno la mediana del volume dei 30 giorni prima: piu' alto = piu' piccola."""
    V = pan["quote_volume"]
    out = np.full((len(lun), V.shape[1]), np.nan)
    for k, m in enumerate(lun):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            out[k] = -np.nanmedian(V[max(0, m - 30): m], axis=0)
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    costo = sc.costi_moneta(ps["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    f5 = pd.read_csv(QUI / "risultati_ventiquattresima" / "settimane_F5.csv.gz", index_col=0)["netto"]
    RIS.mkdir(exist_ok=True)
    serie, esami = {}, {}
    for nome, segnale in (("X1", momento(pan, lun)), ("X2", dimensione(pan, lun))):
        ct = np.where(np.isfinite(sig), segnale, np.nan)
        df = te.conto(vq.pesi_banda(ct, ps["U"], sig), ps["R"], ps["F"], costo)
        df.index = ps["lunedi"]
        df.to_csv(RIS / f"settimane_{nome}.csv.gz")
        e = te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        comuni = df.index.intersection(f5.index)
        comuni = comuni[comuni >= se.INIZIO]
        e["correlazione_F5"] = float(np.corrcoef(df.loc[comuni, "netto"], f5.loc[comuni])[0, 1])
        serie[f"49 {nome}"] = df["netto"]
        esami[nome] = e
    prima = ast.conto_di_prima() + [e["intero"]["sharpe"] for e in esami.values()]
    rivisto = ast.corretto_rivisto(serie, {f"49 {n}": e["intero"] for n, e in esami.items()})
    for nome, e in esami.items():
        i = e["intero"]
        r = rivisto["candidate"][f"49 {nome}"]
        e["sharpe_corretto"] = r["corretto"]
        e["sharpe_corretto_prima"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], prima, 52)
        e["t"], e["gruppo"], e["gruppi"], e["prove_nel_conto"] = r["t"], r["gruppo"], rivisto["gruppi"], len(prima)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    righe = ["# Programma 6 — risultati della quarantanovesima prova (il momento e la dimensione fra monete)", "",
             "Regole in `QUARANTANOVESIMA.md` (scritte prima); prima prova con lo Sharpe corretto rivisto (`ASTICELLA.md`).", ""]
    for nome, e in esami.items():
        i = e["intero"]
        righe += [f"## {nome} ({'il momento delle 3 settimane' if nome == 'X1' else 'le piccole contro le grandi'})", "",
                  f"* Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, discesa "
                  f"{100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; correlazione con F5 {e['correlazione_F5']:.2f}.",
                  "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
                  f"* Sharpe corretto rivisto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi; prima {e['sharpe_corretto_prima']:.2f} "
                  f"con {e['prove_nel_conto']} prove); t dello Sharpe {e['t']:.2f}; gruppo: " + ", ".join(e["gruppo"]) + ".", "",
                  f"**Esito {nome}: {e['esito']}**", ""]
    testo = "\n".join(righe)
    (QUI / "RISULTATI_QUARANTANOVESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUARANTANOVESIMA FINITA", flush=True)
