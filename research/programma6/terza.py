"""Programma 6, terza prova (TERZA.md): CTREND, la tendenza fra monete da 28 indicatori tecnici (Fieberg, Liedtke,
Poddig, Walker e Zaremba, JFQA 2025), sulle candele giornaliere e il funding della seconda prova.

Convenzioni: la settimana ``w`` inizia il lunedi' (giorno ``m``); gli indicatori sono quelli della chiusura della
domenica ``m-1``; il rendimento della settimana e' il prodotto dei rendimenti giornalieri della seconda prova
(apertura → apertura dopo, o chiusura se la moneta viene tolta dal listino) dal lunedi' alla domenica.

Uso: python3 -m research.programma6.terza [C1 C2 C3]
"""
from __future__ import annotations

import json
import math
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

from research.programma6 import seconda as sc

QUI = Path(__file__).parent
RIS = QUI / "risultati_terza"
N_UNIVERSO, STORIA_MIN, MIN_MONETE, FINESTRA = 100, 200, 20, 52
PROVE_PROGRAMMA = 24
INIZIO_ESAME = sc.giorno(2022, 6, 6)
NOMI = (["rsi", "stochRSI", "stochK", "stochD", "cci"] + [f"sma_{n}d" for n in (3, 5, 10, 20, 50, 100, 200)]
        + ["macd", "macd_diff_signal"] + [f"volsma_{n}d" for n in (3, 5, 10, 20, 50, 100, 200)]
        + ["volmacd", "volmacd_diff_signal", "chaikin", "boll_low", "boll_mid", "boll_high", "boll_width"])


# ---------------------------------------------------------------------------
# gli indicatori (appendice A dell'articolo)
# ---------------------------------------------------------------------------

def ema(x: pd.Series, L: int) -> pd.Series:
    """EMA con alfa = 1/(1+L), come nell'appendice A.1."""
    return x.ewm(alpha=1.0 / (1 + L), adjust=False).mean()


def _cci(h, l, c) -> np.ndarray:
    X = (np.asarray(h) + np.asarray(l) + np.asarray(c)) / 3
    out = np.full(len(X), np.nan)
    if len(X) >= 20:
        w = sliding_window_view(X, 20)
        m = w.mean(axis=1)
        dev = np.abs(w - m[:, None]).mean(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            out[19:] = (X[19:] - m) / (0.015 * dev)
    return out


def indicatori(o, h, l, c, v) -> np.ndarray:
    """I 28 indicatori (colonne in ``NOMI``) per ogni giorno di una serie senza buchi."""
    c, h, l, v = (pd.Series(np.asarray(x, float)) for x in (c, h, l, v))
    d = c.diff()
    g, p = d.clip(lower=0).rolling(14).mean(), (-d.clip(upper=0)).rolling(14).mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        rsi = 100 - 100 / (1 + g / p)
    rsi = rsi.where(p > 0, 100.0).where(g.notna())
    lo_r, hi_r = rsi.rolling(14).min(), rsi.rolling(14).max()
    stoch_rsi = (rsi - lo_r) / (hi_r - lo_r)
    ll, hh = l.rolling(14).min(), h.rolling(14).max()
    stoch_k = (c - ll) / (hh - ll)
    stoch_d = stoch_k.rolling(3).mean()
    cols = [rsi, stoch_rsi, stoch_k, stoch_d, pd.Series(_cci(h, l, c))]
    cols += [c.rolling(n).mean() / c for n in (3, 5, 10, 20, 50, 100, 200)]
    e12, e26 = ema(c, 12), ema(c, 26)
    macd = (e12 - e26) / e12
    cols += [macd, macd - ema(macd, 9)]
    vv = v.where(v > 0)
    cols += [v.rolling(n).mean() / vv for n in (3, 5, 10, 20, 50, 100, 200)]
    v12, v26 = ema(v, 12), ema(v, 26)
    vmacd = (v12 - v26) / v12.where(v12 > 0)
    cols += [vmacd, vmacd - ema(vmacd, 9)]
    rng = (h - l)
    ad = (((c - l) - (h - c)) / rng.where(rng > 0)).fillna(0.0) * v
    cols += [ad.rolling(21).sum() / v.rolling(21).sum().where(lambda x: x > 0)]
    mid, sd = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
    cols += [(mid - 2 * sd) / c, mid / c, (mid + 2 * sd) / c, (4 * sd) / mid]
    out = np.column_stack([x.to_numpy(float) for x in cols])
    out[~np.isfinite(out)] = np.nan
    return out


# ---------------------------------------------------------------------------
# il pannello settimanale
# ---------------------------------------------------------------------------

def settimane(pan: dict) -> np.ndarray:
    """Gli indici (nel pannello) dei lunedi' con una settimana completa e la domenica prima."""
    giorni = np.arange(pan["close"].shape[0]) + pan["t0"]
    lun = np.flatnonzero((giorni + 3) % 7 == 0)
    return lun[(lun >= 1) & (lun + 7 <= len(giorni))]


def pannello_settimane(pan: dict, log=print) -> dict:
    """Per ogni settimana: universo, pesi (mediana del volume), indicatori della domenica, rendimento e funding."""
    C, O, H, L, V = (pan[k] for k in ("close", "open", "high", "low", "quote_volume"))
    T, S = C.shape
    lun = settimane(pan)
    W = len(lun)
    Z = np.full((W, S, len(NOMI)), np.nan)
    for j in range(S):
        ok = np.flatnonzero(np.isfinite(C[:, j]))
        if len(ok) < STORIA_MIN:
            continue
        ind = np.full((T, len(NOMI)), np.nan)
        ind[ok] = indicatori(O[ok, j], H[ok, j], L[ok, j], C[ok, j], V[ok, j])
        Z[:, j] = ind[lun - 1]
    r = sc.rendimenti(pan)
    lr = np.log1p(np.clip(r, -0.999999, None))
    cum = np.vstack([np.zeros((1, S)), np.cumsum(lr, axis=0)])
    R = np.expm1(cum[lun + 7] - cum[lun])
    Fc = np.vstack([np.zeros((1, S)), np.cumsum(pan["funding"], axis=0)])
    F = Fc[lun + 7] - Fc[lun]
    ok = np.isfinite(C)
    primo = np.where(ok.any(axis=0), ok.argmax(axis=0), T)
    U = np.zeros((W, S), bool)
    peso = np.zeros((W, S))
    for k, m in enumerate(lun):
        fin = V[max(0, m - 30): m]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            med = np.nan_to_num(np.nanmedian(fin, axis=0), nan=0.0)
        amm = ok[m - 1] & (m - primo >= STORIA_MIN) & (med >= sc.VOLUME_MIN) & np.isfinite(O[m])
        cand = np.flatnonzero(amm)
        scelte = cand[np.argsort(-med[cand], kind="stable")][:N_UNIVERSO]
        U[k, scelte] = True
        peso[k] = med
    log(f"[terza] settimane {W}, monete {S}")
    return {"lunedi": lun + pan["t0"], "U": U, "peso": peso, "Z": Z, "R": R, "F": F, "simboli": pan["simboli"]}


def ranghi(Z: np.ndarray, U: np.ndarray) -> np.ndarray:
    """Il rango fra le monete dell'universo, fra −0,5 e +0,5; il valore mancante vale 0 (TERZA.md, sezione 3)."""
    W, S, J = Z.shape
    out = np.zeros((W, S, J))
    for k in range(W):
        idx = np.flatnonzero(U[k])
        if len(idx) < 2:
            continue
        for j in range(J):
            x = Z[k, idx, j]
            f = np.isfinite(x)
            if f.sum() < 2:
                continue
            rk = pd.Series(x[f]).rank(method="average").to_numpy()
            out[k, idx[f], j] = (rk - 1) / (f.sum() - 1) - 0.5
    return out


# ---------------------------------------------------------------------------
# le regressioni e il segnale (sezione 3 di TERZA.md)
# ---------------------------------------------------------------------------

def coefficienti(Zr: np.ndarray, R: np.ndarray, U: np.ndarray, peso: np.ndarray, pesato: bool) -> np.ndarray:
    """(alfa, beta) delle regressioni univariate di ogni settimana u: rendimento di u sul rango della settimana prima
    (calcolato alla domenica prima di u, cioe' ``Zr[u]``). NaN dove le monete sono meno di 20."""
    W, S, J = Zr.shape
    out = np.full((W, J, 2), np.nan)
    for u in range(W):
        idx = np.flatnonzero(U[u] & np.isfinite(R[u]))
        if len(idx) < MIN_MONETE:
            continue
        w = peso[u, idx] if pesato else np.ones(len(idx))
        w = w / w.sum()
        y = R[u, idx]
        x = Zr[u, idx]                                   # (n, J)
        xm = w @ x
        ym = w @ y
        dx = x - xm
        var = w @ (dx * dx)
        cov = w @ (dx * (y - ym)[:, None])
        with np.errstate(divide="ignore", invalid="ignore"):
            b = np.where(var > 0, cov / var, 0.0)
        out[u, :, 0] = ym - b * xm
        out[u, :, 1] = b
    return out


def previsioni(Zr: np.ndarray, coef: np.ndarray) -> np.ndarray:
    """Per ogni settimana w la previsione di ogni indicatore con la media dei coefficienti delle 52 settimane prima
    (NaN se le settimane valide sono meno di 52)."""
    W, S, J = Zr.shape
    out = np.full((W, S, J), np.nan)
    for w in range(FINESTRA, W):
        c = coef[w - FINESTRA: w]
        if np.isnan(c[:, 0, 0]).any():
            continue
        a, b = c[:, :, 0].mean(axis=0), c[:, :, 1].mean(axis=0)
        out[w] = a[None, :] + b[None, :] * Zr[w]
    return out


def _aicc(n: int, rss: float, k: int) -> float:
    if n - k - 1 <= 0 or rss <= 0:
        return float("inf")
    return n * math.log(rss / n) + 2 * k + 2 * k * (k + 1) / (n - k - 1)


def selezione(X: np.ndarray, y: np.ndarray, w: np.ndarray) -> np.ndarray:
    """La rete elastica (meta' L1, meta' L2) con la forza scelta dal criterio di Akaike corretto, ai minimi quadrati
    pesati; ritorna i coefficienti (le previsioni da tenere sono quelle positive)."""
    from sklearn.linear_model import enet_path
    w = w * len(w) / w.sum()
    xm, ym = (w @ X) / len(w), (w @ y) / len(w)
    sq = np.sqrt(w)
    Xs = (X - xm) * sq[:, None]
    ys = (y - ym) * sq
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        _, coefs, _ = enet_path(Xs, ys, l1_ratio=0.5, n_alphas=100)
    n = len(y)
    migliore, scelta = float("inf"), np.zeros(X.shape[1])
    for k in range(coefs.shape[1]):
        th = coefs[:, k]
        rss = float(np.sum((ys - Xs @ th) ** 2))
        a = _aicc(n, rss, int(np.count_nonzero(th)) + 1)
        if a < migliore:
            migliore, scelta = a, th
    return scelta


def segnale(variante: str, Zr, R, U, peso) -> tuple:
    """(CTREND per settimana e moneta, previsioni scelte per settimana)."""
    pesato = variante != "C3"
    coef = coefficienti(Zr, R, U, peso, pesato)
    P = previsioni(Zr, coef)
    W, S, J = P.shape
    ct = np.full((W, S), np.nan)
    tenute = {}
    for w in range(W):
        if np.isnan(P[w]).all():
            continue
        if variante == "C2":
            ct[w] = P[w].mean(axis=1)
            continue
        # la rete elastica sulle 52 settimane prima, con le previsioni fatte allora
        righe = []
        for u in range(w - FINESTRA, w):
            if u < 0 or np.isnan(P[u]).all():
                righe = None
                break
            idx = np.flatnonzero(U[u] & np.isfinite(R[u]))
            righe.append((P[u, idx], R[u, idx], peso[u, idx] if pesato else np.ones(len(idx))))
        if not righe:
            continue
        X = np.vstack([r[0] for r in righe])
        y = np.concatenate([r[1] for r in righe])
        pw = np.concatenate([r[2] for r in righe])
        th = selezione(X, y, pw)
        sel = np.flatnonzero(th > 0)
        tenute[w] = sel.tolist()
        if len(sel):
            ct[w] = P[w][:, sel].mean(axis=1)
    return ct, tenute


# ---------------------------------------------------------------------------
# il portafoglio e il conto
# ---------------------------------------------------------------------------

def pesi_portafoglio(ct: np.ndarray, U: np.ndarray, peso: np.ndarray, pesato: bool) -> np.ndarray:
    W, S = ct.shape
    out = np.zeros((W, S))
    for w in range(W):
        idx = np.flatnonzero(U[w] & np.isfinite(ct[w]))
        if len(idx) < MIN_MONETE:
            continue
        k = len(idx) // 5
        ordine = idx[np.argsort(ct[w, idx], kind="stable")]
        basso, alto = ordine[:k], ordine[-k:]
        for lato, segno in ((alto, 1.0), (basso, -1.0)):
            p = peso[w, lato] if pesato else np.ones(len(lato))
            out[w, lato] = segno * p / p.sum()
    return out


def conto(Wt: np.ndarray, R: np.ndarray, F: np.ndarray, costo: np.ndarray) -> pd.DataFrame:
    """Il conto settimanale: lordo, spese sul giro (con i pesi che derivano col prezzo), funding, netto; e i due lati."""
    Wn, S = Wt.shape
    R0 = np.nan_to_num(R)
    righe = []
    deriva = np.zeros(S)
    for w in range(Wn):
        x = Wt[w]
        d = np.abs(x - deriva)
        lordo_i = x * R0[w]
        fund_i = x * F[w]
        spesa_i = d * costo
        lordo, spese, fund = lordo_i.sum(), spesa_i.sum(), fund_i.sum()
        netto = lordo - spese - fund
        L, Sh = x > 0, x < 0
        righe.append({"lordo": lordo, "spese": spese, "funding": fund, "netto": netto,
                      "netto_doppio": lordo - 2 * spese - fund, "giro": d.sum(),
                      "long": lordo_i[L].sum() - spesa_i[L].sum() - fund_i[L].sum(),
                      "short": lordo_i[Sh].sum() - spesa_i[Sh].sum() - fund_i[Sh].sum(),
                      "monete": int((x != 0).sum())})
        deriva = x * (1 + R0[w]) / (1 + netto) if 1 + netto > 0 else np.zeros(S)
    return pd.DataFrame(righe)


# ---------------------------------------------------------------------------
# esame (sezione 4 di TERZA.md)
# ---------------------------------------------------------------------------

def sharpe_corretto(sr_annuo: float, n: int, asim: float, curt: float, sr_prove: list, periodi: int) -> float:
    """Deflated Sharpe Ratio (Bailey e Lopez de Prado 2014) con ``periodi`` osservazioni l'anno."""
    from scipy import stats
    sr = sr_annuo / math.sqrt(periodi)
    N = max(2, len(sr_prove))
    var = float(np.var([x / math.sqrt(periodi) for x in sr_prove], ddof=1))
    g = 0.5772156649
    sr0 = math.sqrt(var) * ((1 - g) * stats.norm.ppf(1 - 1 / N) + g * stats.norm.ppf(1 - 1 / (N * math.e)))
    den = math.sqrt(max(1e-12, 1 - asim * sr + (curt - 1) / 4 * sr * sr))
    return float(stats.norm.cdf((sr - sr0) * math.sqrt(n - 1) / den))


def numeri_settimana(x: pd.Series) -> dict:
    v = x.to_numpy(float)
    sd = v.std(ddof=1)
    eq = np.cumprod(1 + v)
    return {"settimane": int(len(v)), "annuo": float(v.mean() * 52), "volatilita": float(sd * math.sqrt(52)),
            "sharpe": float(v.mean() / sd * math.sqrt(52)) if sd > 0 else 0.0,
            "discesa_max": float((eq / np.maximum.accumulate(eq) - 1).min()), "asimmetria": float(pd.Series(v).skew()),
            "curtosi": float(pd.Series(v).kurt() + 3)}


def esame(df: pd.DataFrame, btc: pd.Series, inizio: int = INIZIO_ESAME, anni_pieni=(2023, 2024, 2025)) -> dict:
    d = df[df.index >= inizio]
    date = pd.to_datetime(d.index.to_numpy() * 86400, unit="s")
    e = {"intero": numeri_settimana(d["netto"]),
         "boot": sc.bootstrap_blocchi(d["netto"].to_numpy(), blocco=4),
         "costi_doppi": float(d["netto_doppio"].mean()), "giro_medio": float(d["giro"].mean()),
         "spese_annue": float(d["spese"].mean() * 52), "funding_annuo": float(d["funding"].mean() * 52),
         "long_annuo": float(d["long"].mean() * 52), "short_annuo": float(d["short"].mean() * 52),
         "settimane_ferme": int((d["monete"] == 0).sum())}
    e["per_anno"] = {int(a): float(d["netto"][date.year == a].mean() * 52) for a in sorted(set(date.year))}
    e["ultimo_anno"] = float(d["netto"][d.index >= sc.ULTIMO_ANNO].mean() * 52)
    e["per_trimestre"] = {f"{a}T{q}": float(d["netto"][(date.year == a) & (date.quarter == q)].mean() * 52)
                          for a in anni_pieni for q in (1, 2, 3, 4)}
    e["dopo_aprile_2025"] = numeri_settimana(d["netto"][d.index >= sc.PUBBLICAZIONE])
    tutto = df[df["monete"] > 0]
    e["dal_primo_segnale"] = {"da": sc.data(int(tutto.index.min())) if len(tutto) else "",
                              **(numeri_settimana(df.loc[tutto.index.min():, "netto"]) if len(tutto) else {})}
    b = btc.reindex(d.index).fillna(0.0).to_numpy()
    X = np.vstack([np.ones(len(b)), b]).T
    coef, *_ = np.linalg.lstsq(X, d["netto"].to_numpy(), rcond=None)
    e["extra_btc_annuo"], e["beta_btc"] = float(coef[0] * 52), float(coef[1])
    return e


def esito(e: dict, dsr: float) -> str:
    if not e["boot"]["basso"] > 0:
        return "netto con l'intervallo non sopra zero"
    if not dsr >= 0.95:
        return f"Sharpe corretto {dsr:.2f} sotto 0,95"
    if sum(1 for v in e["per_anno"].values() if v > 0) < 4:
        return f"positiva in meno di 4 anni su {len(e['per_anno'])}"
    if not e["ultimo_anno"] > 0:
        return "non positiva nell'ultimo anno"
    if not e["costi_doppi"] > 0:
        return "non positiva a costi doppi"
    for a in sorted({k[:4] for k in e["per_trimestre"]}):
        if sum(1 for q in range(1, 5) if e["per_trimestre"][f"{a}T{q}"] > 0) < 2:
            return f"positiva in meno di 2 trimestri nel {a}"
    if not e["extra_btc_annuo"] > 0:
        return "niente in più del Bitcoin"
    return "VALIDA"


def esegui(varianti=("C1", "C2", "C3"), log=print) -> dict:
    pan = sc.pannello()
    ps = pannello_settimane(pan, log=log)
    Zr = ranghi(ps["Z"], ps["U"])
    costo = sc.costi_moneta(ps["simboli"])
    jb = ps["simboli"].index("BTCUSDT")
    btc = pd.Series(ps["R"][:, jb], index=ps["lunedi"])
    RIS.mkdir(exist_ok=True)
    out = {}
    for v in varianti:
        ct, tenute = segnale(v, Zr, ps["R"], ps["U"], ps["peso"])
        Wt = pesi_portafoglio(ct, ps["U"], ps["peso"], v != "C3")
        df = conto(Wt, ps["R"], ps["F"], costo)
        df.index = ps["lunedi"]
        df.to_csv(RIS / f"settimane_{v}.csv.gz")
        e = esame(df, btc)
        e["indicatori_tenuti"] = {sc.data(int(ps["lunedi"][w])): [NOMI[j] for j in s] for w, s in tenute.items()}
        out[v] = e
        (RIS / f"{v}.json").write_text(json.dumps(e, ensure_ascii=False, indent=1), encoding="utf-8")
        log(f"[terza] {v} fatto")
    out["btc"] = numeri_settimana(btc[btc.index >= INIZIO_ESAME])
    (RIS / "btc.json").write_text(json.dumps(out["btc"], indent=1), encoding="utf-8")
    return out


def rapporto() -> str:
    sr = sc.sharpe_prove()
    for v in ("C1", "C2", "C3"):
        f = RIS / f"{v}.json"
        if f.exists():
            sr.append(json.loads(f.read_text())["intero"]["sharpe"])
    while len(sr) < PROVE_PROGRAMMA:
        sr.append(0.0)
    btc = json.loads((RIS / "btc.json").read_text())
    righe = ["# Programma 6 — risultati della terza prova (CTREND)", "",
             "Regole in `TERZA.md` (scritte prima). Settimane dal 6 giugno 2022 (fuori dal campione dell'articolo) all'ultima "
             "completa; le 100 monete più scambiate di ogni settimana, fra tutte quelle dell'archivio; long il quinto più "
             "forte, short il quinto più debole, leva lorda 2.", "",
             "| Variante | Rendimento/anno | Intervallo (settimana) | Volatilità | Sharpe | Sharpe corretto | Discesa massima | "
             "Anni positivi | Ultimo anno | Costi doppi (settimana) | Lato long/anno | Lato short/anno | Giro a settimana | "
             "In più del BTC/anno | Esito |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for v in ("C1", "C2", "C3"):
        f = RIS / f"{v}.json"
        if not f.exists():
            continue
        e = json.loads(f.read_text())
        i = e["intero"]
        dsr = sharpe_corretto(i["sharpe"], i["settimane"], i["asimmetria"], i["curtosi"], sr, 52)
        anni = sum(1 for x in e["per_anno"].values() if x > 0)
        righe.append(f"| {v} | {100 * i['annuo']:+.1f}% | {100 * e['boot']['basso']:+.2f}%; {100 * e['boot']['alto']:+.2f}% | "
                     f"{100 * i['volatilita']:.1f}% | {i['sharpe']:.2f} | {dsr:.2f} | {100 * i['discesa_max']:.1f}% | "
                     f"{anni}/{len(e['per_anno'])} | {100 * e['ultimo_anno']:+.1f}% | {100 * e['costi_doppi']:+.2f}% | "
                     f"{100 * e['long_annuo']:+.1f}% | {100 * e['short_annuo']:+.1f}% | {100 * e['giro_medio']:.0f}% | "
                     f"{100 * e['extra_btc_annuo']:+.1f}% | {esito(e, dsr)} |")
    righe += ["", f"Bitcoin sempre comprato nelle stesse settimane: {100 * btc['annuo']:+.1f}% l'anno, Sharpe {btc['sharpe']:.2f}.",
              "", "### Per anno e dopo l'aprile 2025 (rendimento netto annualizzato; Sharpe)", "",
              "| Variante | 2022 | 2023 | 2024 | 2025 | 2026 | Dopo aprile 2025 | Dal primo segnale |", "|---|---|---|---|---|---|---|---|"]
    for v in ("C1", "C2", "C3"):
        f = RIS / f"{v}.json"
        if not f.exists():
            continue
        e = json.loads(f.read_text())
        pa = e["per_anno"]
        d = e["dopo_aprile_2025"]
        p = e["dal_primo_segnale"]
        righe.append(f"| {v} | " + " | ".join(f"{100 * pa.get(str(a), pa.get(a, float('nan'))):+.1f}%" for a in range(2022, 2027))
                     + f" | {100 * d['annuo']:+.1f}%; {d['sharpe']:.2f} | dal {p.get('da')}: {100 * p.get('annuo', float('nan')):+.1f}%; "
                       f"{p.get('sharpe', float('nan')):.2f} |")
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_TERZA.md").write_text(testo, encoding="utf-8")
    return testo


if __name__ == "__main__":
    esegui(tuple(sys.argv[1:]) or ("C1", "C2", "C3"), log=lambda x: print(x, flush=True))
    print(rapporto())
    print("TERZA FINITA", flush=True)
