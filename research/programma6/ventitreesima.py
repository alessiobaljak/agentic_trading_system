"""Programma 6, ventitreesima prova (VENTITREESIMA.md): M6, il modello ad alberi di M1 con la media dei ranghi delle
previsioni di cinque semi (1-5), sui dati corretti del 20 ottobre. Portafoglio ed esame come M1.

Uso: python3 -m research.programma6.ventitreesima
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import diciottesima as di
from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_ventitreesima"
SEMI = (1, 2, 3, 4, 5)


def previsioni_seme(seme: int, X, Y, U, lunedi) -> np.ndarray:
    from sklearn.ensemble import HistGradientBoostingRegressor
    originale = q._modello
    q._modello = lambda tipo: HistGradientBoostingRegressor(
        max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=200, l2_regularization=1.0, random_state=seme)
    try:
        P, _ = q.previsioni("M1", X, Y, U, lunedi, 6, lambda x: None)
    finally:
        q._modello = originale
    return P


def media_ranghi(Ps: list, U: np.ndarray) -> np.ndarray:
    R = [q.rango_nan(P, U & np.isfinite(P)) for P in Ps]
    with np.errstate(all="ignore"):
        return np.nanmean(np.stack(R), axis=0) if len(R) > 1 else R[0]


def portafoglio(P: np.ndarray, ps: dict, sig: np.ndarray) -> pd.DataFrame:
    ct = np.where(np.isfinite(sig), P, np.nan)
    Wt = te.pesi_portafoglio(ct, ps["U"], np.nan_to_num(1.0 / sig), True)
    df = te.conto(Wt, ps["R"], ps["F"], sc.costi_moneta(ps["simboli"]))
    df.index = ps["lunedi"]
    return df


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None)
    sig = ot.sigma_30(pan, ps["lunedi"] - pan["t0"])
    X, _, Y = q.tabella_settimanale(pan, ps, ps["U"])
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    Ps, per_seme = [], {}
    for s in SEMI:
        P = previsioni_seme(s, X, Y, ps["U"], ps["lunedi"])
        Ps.append(P)
        d = portafoglio(P, ps, sig)
        d = d[d.index >= q.INIZIO]["netto"]
        per_seme[str(s)] = float(d.mean() / d.std(ddof=1) * math.sqrt(52))
        log(f"[ventitreesima] seme {s}: Sharpe {per_seme[str(s)]:.2f}")
    with np.errstate(all="ignore"):
        Pm = np.where(ps["U"], media_ranghi(Ps, ps["U"]), np.nan)
    df = portafoglio(Pm, ps, sig)
    RIS.mkdir(exist_ok=True)
    df.to_csv(RIS / "settimane_M6.csv.gz")
    e = te.esame(df, btc, inizio=q.INIZIO, anni_pieni=q.ANNI_PIENI)
    d = df[df.index >= q.INIZIO]
    e["dal_funding_annuo"] = float(-d["funding"].mean() * 52)
    e["dal_prezzo_annuo"] = float(d["lordo"].mean() * 52)
    e["per_seme"] = per_seme
    for n, f in (("F3", QUI / "risultati_ottava" / "settimane_F3.csv.gz"), ("K1", QUI / "risultati_dodicesima" / "settimane_K1.csv.gz"),
                 ("M1", QUI / "risultati_quattordicesima" / "settimane_M1.csv.gz")):
        s = pd.read_csv(f, index_col=0)["netto"]
        c = d.index.intersection(s.index)
        e[f"correlazione_{n}"] = float(np.corrcoef(d.loc[c, "netto"], s.loc[c])[0, 1])
    sr = di.prove_fino_alla_diciassettesima()
    for n, f in (("N1", "risultati_diciottesima"), ("N2", "risultati_diciottesima"), ("P1", "risultati_diciannovesima"),
                 ("P2", "risultati_diciannovesima"), ("S1", "risultati_ventesima"), ("S2", "risultati_ventesima")):
        sr.append(json.loads((QUI / f / "esame.json").read_text())[n]["intero"]["sharpe"])
    sr.append(e["intero"]["sharpe"])
    i = e["intero"]
    e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
    e["prove_nel_conto"] = len(sr)
    e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
    pa = e["per_anno"]
    testo = "\n".join([
        "# Programma 6 — risultati della ventitreesima prova (M6: il modello ad alberi con la media di cinque semi)", "",
        "Regole in `VENTITREESIMA.md` (scritte prima). Le 100 monete più scambiate, dal 3 gennaio 2022, dati corretti del 20 "
        "ottobre; semi 1-5, media dei ranghi delle previsioni.", "",
        f"* {100 * i['annuo']:+.1f}% l'anno, volatilità {100 * i['volatilita']:.1f}%, **Sharpe {i['sharpe']:.2f}**, discesa massima "
        f"{100 * i['discesa_max']:.1f}%; media settimanale {100 * e['boot']['media']:+.3f}% (intervallo "
        f"{100 * e['boot']['basso']:+.3f}; {100 * e['boot']['alto']:+.3f}).",
        "* Per anno: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in pa.items()) + f"; ultimo anno {100 * e['ultimo_anno']:+.1f}%.",
        f"* Dal prezzo {100 * e['dal_prezzo_annuo']:+.1f}% l'anno, dal funding {100 * e['dal_funding_annuo']:+.1f}%; a costi doppi "
        f"{100 * e['costi_doppi']:+.3f}% a settimana.",
        "* Ogni seme da solo (descrittivo): " + ", ".join(f"{k} {v:.2f}" for k, v in per_seme.items()) + ".",
        f"* Correlazione con F3 {e['correlazione_F3']:.2f}, K1 {e['correlazione_K1']:.2f}, M1 (dati di prima) {e['correlazione_M1']:.2f}.",
        f"* Sharpe corretto {e['sharpe_corretto']:.2f} con {e['prove_nel_conto']} prove.", "",
        f"**Esito: {e['esito']}**"]) + "\n"
    (QUI / "RISULTATI_VENTITREESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return e


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("VENTITREESIMA FINITA", flush=True)
