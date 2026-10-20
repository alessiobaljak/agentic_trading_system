"""Programma 6, quattordicesima prova (QUATTORDICESIMA.md): un modello che impara ogni 4 settimane, solo dal passato, come
unire tutti gli ingredienti raccolti (28 indicatori di CTREND, rendimenti, volatilita', funding, acquisti a mercato,
volume, legame col Bitcoin, posizioni, e lo stato del mercato) per ordinare le monete della settimana dopo. M1: alberi
(HistGradientBoostingRegressor); M2: lineare (Ridge). Portafoglio come F3.

Uso: python3 -m research.programma6.quattordicesima
"""
from __future__ import annotations

import json
import math
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import undicesima as un
from research.programma6.motore import TAKER
from research.programma6.scarico_metrics import DATI as DATI_M

QUI = Path(__file__).parent
RIS = QUI / "risultati_quattordicesima"
INIZIO = sc.giorno(2022, 1, 3)
ANNI_PIENI = (2022, 2023, 2024, 2025)
OGNI, MAX_SETT, MIN_SETT = 4, 156, 52


# ---------------------------------------------------------------------------
# gli ingredienti
# ---------------------------------------------------------------------------

def _taker_ls(pan: dict) -> np.ndarray:
    T, S = pan["close"].shape
    out = np.full((T, S), np.nan)
    for j, s in enumerate(pan["simboli"]):
        f = DATI_M / f"{s}.pkl"
        if not f.exists():
            continue
        d = pd.read_pickle(f)
        d = d[(d.index >= pan["t0"]) & (d.index < pan["t0"] + T)]
        out[d.index.to_numpy() - pan["t0"], j] = d["sum_taker_long_short_vol_ratio"].to_numpy(float)
    return out


def ingredienti_giornalieri(pan: dict) -> dict:
    """Le serie giornaliere (giorni × monete) di ogni ingrediente, calcolate con i soli dati fino a quel giorno."""
    C = pd.DataFrame(pan["close"])
    H, L = pd.DataFrame(pan["high"]), pd.DataFrame(pan["low"])
    V = pd.DataFrame(pan["quote_volume"])
    B = pd.DataFrame(pan["taker_buy_quote_volume"])
    F = pd.DataFrame(pan["funding"])
    with np.errstate(all="ignore"):
        lc = np.log(C)
    lr = lc.diff()
    r = lambda df, k, mp=None: df.rolling(k, min_periods=mp or max(2, int(0.7 * k)))
    out = {}
    for k in (1, 7, 30, 90, 180):
        out[f"rend_{k}"] = lc - lc.shift(k)
    for k in (7, 30, 90):
        out[f"vol_{k}"] = r(lr, k).std()
    out["max_30"], out["min_30"], out["asim_30"] = r(lr, 30).max(), r(lr, 30).min(), r(lr, 30).skew()
    out["ampiezza_7"] = r((H - L) / C, 7).mean()
    for k in (1, 3, 7, 30):
        out[f"funding_{k}"] = F.rolling(k, min_periods=1).sum()
    for k in (1, 7, 30):
        with np.errstate(all="ignore"):
            out[f"acquisti_{k}"] = B.rolling(k, min_periods=1).sum() / V.rolling(k, min_periods=1).sum()
    with np.errstate(all="ignore"):
        out["volume_7_su_90"] = np.log(r(V, 7).mean() / r(V, 90).mean())
        out["grandezza"] = np.log(r(V, 30).median())
    ok = C.notna()
    out["eta"] = np.log1p(ok.cumsum().where(ok))
    jb = pan["simboli"].index("BTCUSDT")
    rb = lr[jb]
    cov = r(lr, 90).cov(rb)
    varb = r(rb, 90).var()
    beta = cov.div(varb, axis=0)
    out["beta_90"] = beta
    out["corr_90"] = r(lr, 90).corr(rb)
    with np.errstate(all="ignore"):
        out["vol_propria_90"] = np.sqrt((r(lr, 90).var() - beta.pow(2).mul(varb, axis=0)).clip(lower=0))
    pm = un.pannello_metrics(pan)
    oi = pd.DataFrame(pm["oi"])
    with np.errstate(all="ignore"):
        loi = np.log(oi)
        for k in (1, 7, 30):
            out[f"oi_{k}"] = loi - loi.shift(k)
        out["oi_sul_volume"] = loi - np.log(r(V, 30).mean())
        top = np.log(pd.DataFrame(pm["grandi"])).rolling(7, min_periods=5).mean()
        acc = np.log(pd.DataFrame(pm["tutti"])).rolling(7, min_periods=5).mean()
        out["ls_grandi_7"], out["ls_tutti_7"], out["ls_differenza_7"] = top, acc, top - acc
        out["acquisti_vendite_7"] = np.log(pd.DataFrame(_taker_ls(pan))).rolling(7, min_periods=5).mean()
    return {k: v.to_numpy(float) for k, v in out.items()}


def rango_nan(x: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Rango fra le monete dell'universo, fra −0,5 e +0,5; mancante dove manca il dato o la moneta non e' nell'universo."""
    out = np.full(x.shape, np.nan)
    for w in range(x.shape[0]):
        idx = np.flatnonzero(U[w] & np.isfinite(x[w]))
        if len(idx) < 2:
            continue
        rk = pd.Series(x[w, idx]).rank(method="average").to_numpy()
        out[w, idx] = (rk - 1) / (len(idx) - 1) - 0.5
    return out


def tabella_settimanale(pan: dict, ps: dict, U: np.ndarray) -> tuple:
    """(X: settimane × monete × ingredienti, nomi, obiettivo: settimane × monete)."""
    lun = ps["lunedi"] - pan["t0"]
    g = ingredienti_giornalieri(pan)
    nomi, strati = [], []
    for k in range(ps["Z"].shape[2]):
        nomi.append(te.NOMI[k])
        strati.append(rango_nan(np.where(np.isfinite(ps["Z"][:, :, k]), ps["Z"][:, :, k], np.nan), U))
    for n, a in g.items():
        nomi.append(n)
        strati.append(rango_nan(a[lun - 1], U))
    # lo stato del mercato, uguale per tutte le monete
    jb = pan["simboli"].index("BTCUSDT")
    W, S = U.shape
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        r7 = np.where(U, g["rend_7"][lun - 1], np.nan)
        mercato = {"btc_rend_7": g["rend_7"][lun - 1, jb], "btc_rend_30": g["rend_30"][lun - 1, jb],
                   "btc_vol_30": g["vol_30"][lun - 1, jb],
                   "funding_mercato_7": np.nanmean(np.where(U, g["funding_7"][lun - 1], np.nan), axis=1),
                   "rend_mercato_7": np.nanmean(r7, axis=1), "dispersione_7": np.nanstd(r7, axis=1)}
    for n, v in mercato.items():
        nomi.append(n)
        strati.append(np.repeat(np.asarray(v, float)[:, None], S, axis=1))
    X = np.stack(strati, axis=2)
    Y = rango_nan(ps["R"], U & np.isfinite(ps["R"]))
    return X, nomi, Y


# ---------------------------------------------------------------------------
# allenamento a finestre che avanzano
# ---------------------------------------------------------------------------

def _modello(tipo: str):
    if tipo == "M1":
        from sklearn.ensemble import HistGradientBoostingRegressor
        return HistGradientBoostingRegressor(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=200,
                                             l2_regularization=1.0, random_state=2026)
    from sklearn.linear_model import Ridge
    return Ridge(alpha=10.0)


def _righe(X, Y, U, settimane):
    xs, ys = [], []
    for u in settimane:
        idx = np.flatnonzero(U[u] & np.isfinite(Y[u]))
        xs.append(X[u, idx])
        ys.append(Y[u, idx])
    return (np.vstack(xs), np.concatenate(ys)) if xs else (np.empty((0, X.shape[2])), np.empty(0))


def previsioni(tipo: str, X, Y, U, lunedi, n_mercato: int, log=print) -> tuple:
    W = X.shape[0]
    P = np.full(U.shape, np.nan)
    valide = [u for u in range(W) if (U[u] & np.isfinite(Y[u])).sum() >= te.MIN_MONETE]
    inizio = int(np.searchsorted(lunedi, INIZIO))
    ultimo = None
    for w0 in range(inizio, W, OGNI):
        allen = [u for u in valide if w0 - MAX_SETT <= u < w0]
        if len(allen) < MIN_SETT:
            continue
        Xa, Ya = _righe(X, Y, U, allen)
        # le colonne tutte mancanti nell'allenamento (le posizioni prima del dicembre 2021) si tolgono: il modello ad
        # alberi di scikit-learn 1.9 si ferma su una colonna vuota, e da una colonna vuota non si impara niente
        cols = np.isfinite(Xa).any(axis=0) if tipo == "M1" else np.ones(Xa.shape[1], bool)
        Xa = Xa[:, cols]
        m = _modello(tipo)
        if tipo == "M2":
            mu = np.nanmean(Xa[:, -n_mercato:], axis=0)
            sd = np.nanstd(Xa[:, -n_mercato:], axis=0)
            sd[sd == 0] = 1.0
            prep = lambda Z, mu=mu, sd=sd: np.nan_to_num(np.concatenate([Z[:, :-n_mercato], (Z[:, -n_mercato:] - mu) / sd], axis=1))
        else:
            prep = lambda Z: Z
        m.fit(prep(Xa), Ya)
        for w in range(w0, min(w0 + OGNI, W)):
            idx = np.flatnonzero(U[w])
            if len(idx) >= te.MIN_MONETE:
                P[w, idx] = m.predict(prep(X[w, idx][:, cols]))
        ultimo = (m, prep, Xa, Ya, cols)
    log(f"[quattordicesima] {tipo} allenato")
    return P, ultimo


def importanza(tipo: str, ultimo, nomi) -> dict:
    m, prep, Xa, Ya, cols = ultimo
    nomi = [n for n, c in zip(nomi, cols) if c]
    if tipo == "M2":
        return dict(sorted(((n, float(abs(c))) for n, c in zip(nomi, m.coef_)), key=lambda x: -x[1])[:15])
    from sklearn.inspection import permutation_importance
    rng = np.random.default_rng(2026)
    sel = rng.choice(len(Ya), min(8000, len(Ya)), replace=False)
    pi = permutation_importance(m, prep(Xa[sel]), Ya[sel], n_repeats=3, random_state=2026)
    return dict(sorted(((n, float(v)) for n, v in zip(nomi, pi.importances_mean)), key=lambda x: -x[1])[:15])


def tutte_le_prove() -> list:
    """Gli Sharpe annui di tutte le prove del programma 6 fino alla tredicesima (34)."""
    sr = sc.sharpe_prove()
    sr += [json.loads((te.RIS / f"{v}.json").read_text())["intero"]["sharpe"] for v in ("C1", "C2", "C3")]
    sr += [json.loads((se.RIS / f"{v}.json").read_text())["intero"]["sharpe"] for v in ("F1", "F2")]
    sr.append(json.loads((QUI / "risultati_ottava" / "esame.json").read_text())["cento"]["intero"]["sharpe"])
    nn = json.loads((QUI / "risultati_nona" / "esame.json").read_text())
    sr += [nn["G1"]["cento"]["intero"]["sharpe"], nn["G2"]["cento"]["intero"]["sharpe"]]
    sr.append(json.loads((QUI / "risultati_decima" / "esame.json").read_text())["cento"]["intero"]["sharpe"])
    uu = json.loads((QUI / "risultati_undicesima" / "esame.json").read_text())
    sr += [uu["P1"]["intero"]["sharpe"], uu["P2"]["intero"]["sharpe"]]
    sr.append(json.loads((QUI / "risultati_dodicesima" / "esame.json").read_text())["intero"]["sharpe"])
    sr.append(json.loads((QUI / "risultati_tredicesima" / "esame.json").read_text())["intero"]["sharpe"])
    return sr


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None)
    lun_idx = ps["lunedi"] - pan["t0"]
    sig = ot.sigma_30(pan, lun_idx)
    X, nomi, Y = tabella_settimanale(pan, ps, ps["U"])
    n_mercato = 6
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    RIS.mkdir(exist_ok=True)
    f3 = pd.read_csv(QUI / "risultati_ottava" / "settimane_F3.csv.gz", index_col=0)["netto"]
    k1 = pd.read_csv(QUI / "risultati_dodicesima" / "settimane_K1.csv.gz", index_col=0)["netto"]
    sr = tutte_le_prove()
    esami = {}
    for tipo in ("M1", "M2"):
        P, ultimo = previsioni(tipo, X, Y, ps["U"], ps["lunedi"], n_mercato, log)
        ct = np.where(np.isfinite(sig), P, np.nan)
        Wt = te.pesi_portafoglio(ct, ps["U"], np.nan_to_num(1.0 / sig), True)
        df = te.conto(Wt, ps["R"], ps["F"], sc.costi_moneta(ps["simboli"]))
        df.index = ps["lunedi"]
        df.to_csv(RIS / f"settimane_{tipo}.csv.gz")
        e = te.esame(df, btc, inizio=INIZIO, anni_pieni=ANNI_PIENI)
        d = df[df.index >= INIZIO]
        e["dal_funding_annuo"] = float(-d["funding"].mean() * 52)
        e["dal_prezzo_annuo"] = float(d["lordo"].mean() * 52)
        e["importanza"] = importanza(tipo, ultimo, nomi) if ultimo else {}
        for n, s in (("F3", f3), ("K1", k1)):
            c = d.index.intersection(s.index)
            e[f"correlazione_{n}"] = float(np.corrcoef(d.loc[c, "netto"], s.loc[c])[0, 1])
        # informazione: la stessa procedura sulle monete 101-200, scarto 0,10%
        ps2 = te.pannello_settimane(pan, log=lambda x: None, da=100, a=200, indicatori_si=False)
        X2, _, Y2 = tabella_settimanale(pan, {**ps, "U": ps2["U"]}, ps2["U"])
        P2, _ = previsioni(tipo, X2, Y2, ps2["U"], ps["lunedi"], n_mercato, lambda x: None)
        ct2 = np.where(np.isfinite(sig), P2, np.nan)
        W2 = te.pesi_portafoglio(ct2, ps2["U"], np.nan_to_num(1.0 / sig), True)
        df2 = te.conto(W2, ps["R"], ps["F"], np.full(len(ps["simboli"]), TAKER + 0.001))
        df2.index = ps["lunedi"]
        d2 = df2[(df2.index >= INIZIO) & (df2["monete"] > 0)]["netto"]
        e["monete_101_200"] = {"settimane": int(len(d2)), "annuo": float(d2.mean() * 52) if len(d2) else float("nan"),
                               "sharpe": float(d2.mean() / d2.std(ddof=1) * math.sqrt(52)) if len(d2) > 1 else float("nan")}
        esami[tipo] = e
        sr.append(e["intero"]["sharpe"])
    for tipo, e in esami.items():
        i = e["intero"]
        e["sharpe_corretto"] = te.sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        e["prove_nel_conto"] = len(sr)
        e["esito"] = te.esito(e, e["sharpe_corretto"])
    (RIS / "esame.json").write_text(json.dumps(esami, ensure_ascii=False, indent=1), encoding="utf-8")
    righe = ["# Programma 6 — risultati della quattordicesima prova (il modello che unisce gli indicatori)", "",
             "Regole in `QUATTORDICESIMA.md` (scritte prima). Le 100 monete più scambiate, dal 3 gennaio 2022; il modello si "
             "allena ogni 4 settimane solo sul passato.", "",
             "| Modello | Rendimento/anno | Sharpe | Intervallo (settimana) | Sharpe corretto | Anni positivi | Ultimo anno | "
             "Dal prezzo | Dal funding | Correlazione F3, K1 | 101-200 (informazione) | Esito |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for tipo, e in esami.items():
        i = e["intero"]
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        m2 = e["monete_101_200"]
        righe.append(f"| {tipo} | {100 * i['annuo']:+.1f}% | {i['sharpe']:.2f} | {100 * e['boot']['basso']:+.2f}%; "
                     f"{100 * e['boot']['alto']:+.2f}% | {e['sharpe_corretto']:.2f} | {anni}/{len(e['per_anno'])} | "
                     f"{100 * e['ultimo_anno']:+.1f}% | {100 * e['dal_prezzo_annuo']:+.1f}% | {100 * e['dal_funding_annuo']:+.1f}% | "
                     f"{e['correlazione_F3']:.2f}, {e['correlazione_K1']:.2f} | {100 * m2['annuo']:+.1f}%, Sharpe {m2['sharpe']:.2f} | "
                     f"{e['esito']} |")
    for tipo, e in esami.items():
        righe += ["", f"**{tipo}, per anno**: " + ", ".join(f"{a} {100 * v:+.1f}%" for a, v in e["per_anno"].items()),
                  f"**{tipo}, gli ingredienti che contano di più nell'ultimo modello**: "
                  + ", ".join(f"{n} ({v:.4f})" for n, v in list(e["importanza"].items())[:10])]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_QUATTORDICESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return esami


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("QUATTORDICESIMA FINITA", flush=True)
