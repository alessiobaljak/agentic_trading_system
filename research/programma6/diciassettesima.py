"""Programma 6, diciassettesima prova (DICIASSETTESIMA.md): sei modelli in gara. M4: a ogni riallenamento (ogni 4
settimane) si sceglie, con le 12 settimane piu' recenti tenute da parte, il modello che le ha previste meglio, e lo si
riallena su tutto il passato; M5: la media dei ranghi delle previsioni dei sei. Ingredienti, portafoglio ed esame di M1.

Uso: python3 -m research.programma6.diciassettesima
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import ottava as ot
from research.programma6 import quattordicesima as q
from research.programma6 import seconda as sc
from research.programma6 import terza as te

QUI = Path(__file__).parent
RIS = QUI / "risultati_diciassettesima"
MODELLI = ("alberi", "alberi_bassi", "foresta", "alberi_casuali", "lineare", "rete")
TENUTE = 12
N_MERCATO = 6


def crea(nome: str):
    from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
    from sklearn.linear_model import Ridge
    from sklearn.neural_network import MLPRegressor
    if nome == "alberi":
        return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=200,
                                             l2_regularization=1.0, random_state=2026)
    if nome == "alberi_bassi":
        return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=7, min_samples_leaf=400,
                                             l2_regularization=1.0, random_state=2026)
    if nome == "foresta":
        return RandomForestRegressor(n_estimators=200, max_depth=6, min_samples_leaf=200, max_features=0.3,
                                     n_jobs=-1, random_state=2026)
    if nome == "alberi_casuali":
        return ExtraTreesRegressor(n_estimators=200, max_depth=6, min_samples_leaf=200, max_features=0.3,
                                   n_jobs=-1, random_state=2026)
    if nome == "lineare":
        return Ridge(alpha=10.0)
    return MLPRegressor(hidden_layer_sizes=(32, 16), alpha=1e-3, early_stopping=True, max_iter=200, random_state=2026)


def preparatore(nome: str, Xa: np.ndarray):
    """La trasformazione degli ingredienti, stimata sul solo allenamento."""
    if nome in ("alberi", "alberi_bassi"):
        cols = np.isfinite(Xa).any(axis=0)
        return lambda Z: Z[:, cols]
    mu = np.nanmean(Xa[:, -N_MERCATO:], axis=0)
    sd = np.nanstd(Xa[:, -N_MERCATO:], axis=0)
    sd[~np.isfinite(sd) | (sd == 0)] = 1.0
    mu[~np.isfinite(mu)] = 0.0
    return lambda Z: np.nan_to_num(np.concatenate([Z[:, :-N_MERCATO], (Z[:, -N_MERCATO:] - mu) / sd], axis=1))


def allena(nome, Xa, Ya):
    prep = preparatore(nome, Xa)
    m = crea(nome)
    m.fit(prep(Xa), Ya)
    return m, prep


def ic_medio(m, prep, X, Y, U, settimane) -> float:
    v = []
    for u in settimane:
        idx = np.flatnonzero(U[u] & np.isfinite(Y[u]))
        if len(idx) < te.MIN_MONETE:
            continue
        p = m.predict(prep(X[u, idx]))
        v.append(pd.Series(p).corr(pd.Series(Y[u, idx]), method="spearman"))
    return float(np.nanmean(v)) if v else float("-inf")


def gara(X, Y, U, lunedi, log=print) -> tuple:
    W = X.shape[0]
    P4 = np.full(U.shape, np.nan)
    P5 = np.full(U.shape, np.nan)
    valide = [u for u in range(W) if (U[u] & np.isfinite(Y[u])).sum() >= te.MIN_MONETE]
    inizio = int(np.searchsorted(lunedi, q.INIZIO))
    scelte = {}
    for w0 in range(inizio, W, q.OGNI):
        allen = [u for u in valide if w0 - q.MAX_SETT <= u < w0]
        if len(allen) < q.MIN_SETT + TENUTE:
            continue
        fit_w, val_w = allen[:-TENUTE], allen[-TENUTE:]
        Xf, Yf = q._righe(X, Y, U, fit_w)
        punteggi = {}
        for nome in MODELLI:
            m, prep = allena(nome, Xf, Yf)
            punteggi[nome] = ic_medio(m, prep, X, Y, U, val_w)
        scelto = max(MODELLI, key=lambda n: (punteggi[n], -MODELLI.index(n)))
        scelte[sc.data(int(lunedi[w0]))] = {"scelto": scelto, "punteggi": {k: round(v, 4) for k, v in punteggi.items()}}
        Xa, Ya = q._righe(X, Y, U, allen)
        tutti = {nome: allena(nome, Xa, Ya) for nome in MODELLI}
        for w in range(w0, min(w0 + q.OGNI, W)):
            idx = np.flatnonzero(U[w])
            if len(idx) < te.MIN_MONETE:
                continue
            prev = {n: m.predict(prep(X[w, idx])) for n, (m, prep) in tutti.items()}
            P4[w, idx] = prev[scelto]
            ranghi = np.mean([pd.Series(v).rank(pct=True).to_numpy() for v in prev.values()], axis=0)
            P5[w, idx] = ranghi
        log(f"[diciassettesima] {sc.data(int(lunedi[w0]))}: scelto {scelto}")
    return P4, P5, scelte


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None)
    lun_idx = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun_idx)
    X, nomi, Y = q.tabella_settimanale(pan, ps, ps["U"])
    P4, P5, scelte = gara(X, Y, ps["U"], ps["lunedi"], log)
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    RIS.mkdir(exist_ok=True)
    (RIS / "scelte.json").write_text(json.dumps(scelte, ensure_ascii=False, indent=1), encoding="utf-8")
    m1 = pd.read_csv(QUI / "risultati_quattordicesima" / "settimane_M1.csv.gz", index_col=0)["netto"]
    f3 = pd.read_csv(QUI / "risultati_ottava" / "settimane_F3.csv.gz", index_col=0)["netto"]
    sr = q.tutte_le_prove()
    ee = json.loads((QUI / "risultati_quattordicesima" / "esame.json").read_text())
    sr += [ee["M1"]["intero"]["sharpe"], ee["M2"]["intero"]["sharpe"],
           json.loads((QUI / "risultati_quindicesima" / "esame.json").read_text())["intero"]["sharpe"],
           json.loads((QUI / "risultati_sedicesima" / "esame.json").read_text())["intero"]["sharpe"]]
    esami = {}
    for nome, P in (("M4", P4), ("M5", P5)):
        ct = np.where(np.isfinite(sig), P, np.nan)
        Wt = te.pesi_portafoglio(ct, ps["U"], np.nan_to_num(1.0 / sig), True)
        df = te.conto(Wt, ps["R"], ps["F"], sc.costi_moneta(ps["simboli"]))
        df.index = ps["lunedi"]
        df.to_csv(RIS / f"settimane_{nome}.csv.gz")
        e = te.esame(df, btc, inizio=q.INIZIO, anni_pieni=q.ANNI_PIENI)
        d = df[df.index >= q.INIZIO]
        for n, s in (("M1", m1), ("F3", f3)):
            c = d.index.intersection(s.index)
            e[f"correlazione_{n}"] = float(np.corrcoef(d.loc[c, "netto"], s.loc[c])[0, 1])
        esami[nome] = e
        sr.append(e["intero"]["sharpe"])
    conta = {}
    for v in scelte.values():
        conta[v["scelto"]] = conta.get(v["scelto"], 0) + 1
    for nome, e in esami.items():
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
    esami["scelte_quante_volte"] = conta
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della diciassettesima prova (sei modelli in gara)", "",
             "Regole in `DICIASSETTESIMA.md` (scritte prima). Le 100 monete più scambiate, dal 3 gennaio 2022.", "",
             "| Variante | Rendimento/anno | Sharpe | Intervallo (settimana) | Sharpe corretto | Anni positivi | Ultimo anno | "
             "Correlazione M1, F3 | Esito |", "|---|---|---|---|---|---|---|---|---|"]
    for nome in ("M4", "M5"):
        e = esami[nome]
        i = e["intero"]
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        righe.append(f"| {nome} | {100 * i['annuo']:+.1f}% | {i['sharpe']:.2f} | {100 * e['boot']['basso']:+.2f}%; "
                     f"{100 * e['boot']['alto']:+.2f}% | {e['sharpe_corretto']:.2f} | {anni}/{len(e['per_anno'])} | "
                     f"{100 * e['ultimo_anno']:+.1f}% | {e['correlazione_M1']:.2f}, {e['correlazione_F3']:.2f} | {e['esito']} |")
    for nome in ("M4", "M5"):
        righe.append(f"\n**{nome}, per anno**: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in esami[nome]["per_anno"].items()))
    righe.append("\n**Quante volte è stato scelto ogni modello (M4)**: " + ", ".join(f"{k} {v}" for k, v in sorted(conta.items(), key=lambda x: -x[1])))
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_DICIASSETTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("DICIASSETTESIMA FINITA", flush=True)
