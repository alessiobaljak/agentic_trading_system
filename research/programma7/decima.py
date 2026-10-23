"""Programma 7, decima prova (DECIMA.md): MAX, long le monete con il giorno migliore dei 30 giorni piu' alto, short le piu' basse,
con la banda di F5.

Uso: python3 -m research.programma7.decima
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
RIS = QUI / "risultati_decima"


def massimo_30(r: np.ndarray, lun_idx: np.ndarray, minimo: int = 20) -> np.ndarray:
    """(settimane × monete) il rendimento giornaliero piu' alto dei 30 giorni prima del lunedi' (NaN con meno di ``minimo``)."""
    out = np.full((len(lun_idx), r.shape[1]), np.nan)
    for k, m in enumerate(lun_idx):
        f = r[max(0, m - 30): m]
        n = np.isfinite(f).sum(axis=0)
        with np.errstate(all="ignore"):
            mx = np.nanmax(np.where(np.isfinite(f), f, -np.inf), axis=0)
        out[k] = np.where(n >= minimo, mx, np.nan)
    return out


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun)
    r = sc.rendimenti(pan).astype(float)
    r[~np.isfinite(pan["close"])] = np.nan
    mx = massimo_30(r, lun)
    costo = sc.costi_moneta(ps["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out = {}
    for nome, segno in (("MAX", 1.0), ("MAX al contrario (per capire)", -1.0)):
        W = vq.pesi_banda(np.where(np.isfinite(sig), segno * mx, np.nan), ps["U"], sig)
        df = te.conto(W, ps["R"], ps["F"], costo)
        df.index = ps["lunedi"]
        out[nome] = (df, te.esame(df, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI))
    df, e = out["MAX"]
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_MAX.csv.gz")
    f5 = pd.read_csv(QUI.parent / "programma6" / "risultati_controllo_parita" / "settimane_F5.csv.gz", index_col=0)["netto"]
    c = df.index[df.index >= se.INIZIO].intersection(f5.index)
    e["correlazione_F5"] = float(np.corrcoef(df.loc[c, "netto"], f5.loc[c])[0, 1])
    rivisto = ast.corretto_rivisto({**ast.serie_nuove(), "66 MAX": df["netto"]}, {"66 MAX": e["intero"]})
    rr = rivisto["candidate"]["66 MAX"]
    e["sharpe_corretto"], e["t"], e["gruppi"] = rr["corretto_con_aggiunta"], rr["t"], rivisto["gruppi"]
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    contrario = out["MAX al contrario (per capire)"][1]["intero"]
    e["al_contrario"] = {k: contrario[k] for k in ("sharpe", "annuo", "discesa_max")}
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    i, x = e["intero"], e["al_contrario"]
    testo = "\n".join([
        "# Programma 7 — risultati della decima prova (MAX: il giorno migliore del mese)", "",
        "Regole in `DECIMA.md` (scritte prima).", "",
        f"* MAX (verso pubblicato): Sharpe {i['sharpe']:.2f}, {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, "
        f"discesa {100 * i['discesa_max']:.1f}%; spese {100 * e['spese_annue']:.1f}% l'anno; correlazione con F5 {e['correlazione_F5']:.2f}.",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()) + ".",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} ({e['gruppi']} gruppi); t {e['t']:.2f}.",
        f"* Il verso opposto, solo per capire: Sharpe {x['sharpe']:.2f}, {100 * x['annuo']:+.1f}% l'anno, discesa {100 * x['discesa_max']:.1f}%.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_DECIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("DECIMA FINITA", flush=True)
