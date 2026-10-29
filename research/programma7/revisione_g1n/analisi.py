"""Revisione di G1N (29 ottobre 2026): ricalcolo indipendente e controlli. Scrive `risultati.json` accanto a questo file.

Uso: python3 -m research.programma7.revisione_g1n.analisi
"""
from __future__ import annotations

import json
import os
import pickle
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as nu

QUI = Path(__file__).parent
CACHE = Path(os.environ.get("CACHE_G1N", "/tmp/cache_g1n"))
INIZIO, FINE = sc.giorno(2021, 1, 4), sc.giorno(2026, 10, 5)


def log(*a):
    print(*a, flush=True)


def candele_ore(simboli: list) -> dict:
    """{simbolo: {ora: (open, high, low, close)}} solo per le ore 00 e 01 UTC dei giorni della prova (cache su disco)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / "ore.pkl"
    ore = pickle.loads(f.read_bytes()) if f.exists() else {}
    mancano = [s for s in simboli if s not in ore]
    if mancano:
        from research.programma6 import esecuzione as es
        for n, s in enumerate(mancano):
            b = es.ore_di(s)
            if b.empty:
                ore[s] = {}
                continue
            b = b[(b.index >= INIZIO * 24) & (b.index < FINE * 24 + 48) & (b.index % 24 < 2)]
            ore[s] = {int(h): tuple(float(v) for v in r) for h, r in zip(b.index, b[["open", "high", "low", "close"]].to_numpy())}
            if n % 50 == 0:
                log(f"[ore] {n}/{len(mancano)}")
        f.write_bytes(pickle.dumps(ore))
    return ore


def conto(nome, Wx, R, F, costo, giorni, simboli, ore, oltre=0.0):
    lordo, sp_m, fund, D = nu.variazioni(Wx, R, F, costo)
    sp_l, n, n_lim = nu.spese_limite(D, giorni, simboli, costo, ore, oltre)
    d = pd.DataFrame({"lordo": lordo, "spese_mercato": sp_m, "spese": sp_l, "funding": fund}, index=giorni)
    d["netto"] = d["lordo"] - d["spese"] - d["funding"]
    d["netto_mercato"] = d["lordo"] - d["spese_mercato"] - d["funding"]
    d["netto_triplo"] = d["lordo"] - 3 * d["spese"] - d["funding"]
    d.attrs = {"variazioni": n, "a_limite": n_lim}
    return d


def settimane(d: pd.DataFrame) -> pd.DataFrame:
    lun = d.index.to_numpy() - ((d.index.to_numpy() + 3) % 7)
    return d.groupby(lun).sum()


def anno(giorni) -> np.ndarray:
    return pd.to_datetime(np.asarray(giorni) * 86400, unit="s").year.to_numpy()


def sintesi(d: pd.DataFrame, col="netto") -> dict:
    w = settimane(d)[col]
    out = nu.numeri(w.to_numpy())
    out["discesa_giornaliera"] = nu.numeri(d[col].to_numpy(), 365)["discesa"]
    a = anno(w.index)
    out["per_anno"] = {int(y): float(w[a == y].mean() * 52) for y in sorted(set(a))}
    out["sharpe_per_anno"] = {int(y): nu.numeri(w[a == y].to_numpy())["sharpe"] for y in sorted(set(a))}
    out["discesa_per_anno"] = {int(y): nu.numeri(w[a == y].to_numpy())["discesa"] for y in sorted(set(a))}
    return out


def discese(x: pd.Series, n=5) -> list:
    """Le n discese peggiori (settimanali), con inizio, fondo e recupero."""
    eq = (1 + x).cumprod()
    pic = eq.cummax()
    dd = eq / pic - 1
    out, usate = [], np.zeros(len(x), bool)
    for _ in range(n):
        v = dd.where(~usate)
        if v.isna().all() or v.min() >= 0:
            break
        fondo = v.idxmin()
        pos = x.index.get_loc(fondo)
        inizio = pos
        while inizio > 0 and dd.iloc[inizio - 1] < 0:
            inizio -= 1
        fine = pos
        while fine < len(x) - 1 and dd.iloc[fine + 1] < 0:
            fine += 1
        usate[inizio:fine + 1] = True
        out.append({"discesa": float(dd.loc[fondo]), "da": sc.data(int(x.index[max(0, inizio - 1)])), "fondo": sc.data(int(fondo)),
                    "recupero": sc.data(int(x.index[fine])) if fine < len(x) - 1 else "non ancora"})
    return out


def bootstrap_coppia(a: np.ndarray, b: np.ndarray, blocco=8, n=5000, seme=29):
    """Bootstrap a blocchi mobili sulle stesse settimane: differenza di Sharpe (b - a) e di discesa (b - a; positiva = b meglio)."""
    rng = np.random.default_rng(seme)
    T = len(a)
    nb = int(np.ceil(T / blocco))
    ds, dd = np.zeros(n), np.zeros(n)
    for z in range(n):
        st = rng.integers(0, T - blocco + 1, nb)
        ix = (st[:, None] + np.arange(blocco)[None, :]).ravel()[:T]
        xa, xb = a[ix], b[ix]
        na, nb_ = nu.numeri(xa), nu.numeri(xb)
        ds[z] = nb_["sharpe"] - na["sharpe"]
        dd[z] = nb_["discesa"] - na["discesa"]
    return {"sharpe_diff_media": float(ds.mean()), "sharpe_diff_5_95": [float(np.percentile(ds, 5)), float(np.percentile(ds, 95))],
            "p_sharpe_b_meglio": float((ds > 0).mean()),
            "discesa_diff_media": float(dd.mean()), "discesa_diff_5_95": [float(np.percentile(dd, 5)), float(np.percentile(dd, 95))],
            "p_discesa_b_meglio": float((dd > 0).mean())}


def main():
    t0 = time.time()
    pan = sc.pannello()
    simboli = pan["simboli"]
    giorni = np.arange(INIZIO, FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = np.array([nu.costo_di(s) for s in simboli])
    jt = simboli.index("TRXUSDT")
    jb = simboli.index("BTCUSDT")
    out = {}

    # ---- 1. pesi indipendenti e confronto con la ricerca ----
    U = nu.universo_giorni(pan, idx)
    W, WN, sc_ = nu.pesi(pan, idx, U)
    log(f"[pesi] fatti in {time.time() - t0:.0f}s")
    from research.programma6 import ottava as ot, sesta as se, terza as te, ventiquattresima as vq
    from research.programma7 import prima as pr, ventiquattresima as f5n
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    Wr = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    beta_r = f5n.beta_delle_monete(pan, Ud, idx)
    WNr, ar, br, blr, bsr = f5n.scala_neutra(Wr, beta_r)
    out["parita_con_la_ricerca"] = {
        "universo_giorni_diversi": int((U != Ud).any(axis=1).sum()),
        "pesi_G1_max_diff": float(np.abs(W - Wr).max()), "pesi_G1N_max_diff": float(np.abs(WN - WNr).max()),
        "a_max_diff": float(np.nanmax(np.abs(sc_["a"] - ar))),
    }
    log(out["parita_con_la_ricerca"])
    ore = candele_ore([simboli[j] for j in np.flatnonzero((np.abs(W) + np.abs(WN)).sum(axis=0) > 0)])
    log(f"[ore] pronte {time.time() - t0:.0f}s")

    conti = {}
    conti["G1"] = conto("G1", W, R, F, costo, giorni, simboli, ore)
    conti["G1N"] = conto("G1N", WN, R, F, costo, giorni, simboli, ore)
    WF = np.where(W > 0, W * 1.2, W * 0.8)
    conti["G1 120/80"] = conto("G1 120/80", WF, R, F, costo, giorni, simboli, ore)
    am, bm = float(np.nanmean(sc_["a"])), float(np.nanmean(sc_["b"]))
    WM = np.where(W > 0, W * am, W * bm)
    conti["G1 a,b medi fissi"] = conto("fissi", WM, R, F, costo, giorni, simboli, ore)
    out["scalatura"] = {"a_medio": am, "b_medio": bm, "a_min": float(np.nanmin(sc_["a"])), "a_max": float(np.nanmax(sc_["a"])),
                        "a_5_95": [float(np.nanpercentile(sc_["a"], 5)), float(np.nanpercentile(sc_["a"], 95))],
                        "beta_long_medio": float(np.nanmean(sc_["bl"])), "beta_short_medio": float(np.nanmean(sc_["bs"])),
                        "giorni_al_limite": int(((sc_["a"] <= 0.5) | (sc_["a"] >= 1.5)).sum()),
                        "giorni_bl_negativo": int((sc_["bl"] < 0).sum()), "giorni_bs_negativo": int((sc_["bs"] < 0).sum()),
                        "giorni_senza_scalatura": int(np.isnan(sc_["bl"]).sum())}
    # beta delle monete: quante con beta di ripiego (1) o negativo fra quelle tenute
    rc = nu.ritorni_chiusura(pan["close"])
    ripiego = neg = tenute = 0
    beta_prima, beta_dopo, lato_prima, lato_dopo = [], [], [], []
    for k in range(0, len(idx), 1):
        i = idx[k]
        tenute_k = np.flatnonzero(W[k] != 0)
        if not len(tenute_k):
            continue
        b = nu.beta90(rc, U[k], i)
        tenute += len(tenute_k)
        # ripiego: meno di 45 giorni comuni
        blocco = rc[i - 90:i]
        nn = np.isfinite(blocco[:, tenute_k]).sum(axis=0)
        ripiego += int((nn < 45).sum())
        neg += int((b[tenute_k] < 0).sum())
        if k % 7 == 0 and i + 90 <= rc.shape[0] and idx[k] + 90 <= idx[-1] + 1:
            b2 = nu.beta90(rc, U[k], i + 90)         # il beta dei 90 giorni DOPO (solo per misurare il rumore)
            ok = np.isfinite(b2[tenute_k])
            beta_prima += b[tenute_k][ok].tolist()
            beta_dopo += b2[tenute_k][ok].tolist()
            L, S_ = W[k] > 0, W[k] < 0
            lato_prima.append(float((W[k, L] * b[L]).sum() - (-W[k, S_] * b[S_]).sum()))
            lato_dopo.append(float((W[k, L] * b2[L]).sum() - (-W[k, S_] * b2[S_]).sum()))
    out["beta_monete"] = {"posizioni_giorno": tenute, "con_beta_di_ripiego_1": ripiego, "con_beta_negativo": neg,
                          "corr_beta_prima_dopo_moneta": float(np.corrcoef(beta_prima, beta_dopo)[0, 1]),
                          "corr_differenza_lati_prima_dopo": float(np.corrcoef(lato_prima, lato_dopo)[0, 1]),
                          "differenza_lati_prima_media": float(np.mean(lato_prima)), "differenza_lati_dopo_media": float(np.mean(lato_dopo))}
    log(out["beta_monete"])

    # ---- 2. i numeri ----
    out["sintesi"] = {n: sintesi(d) for n, d in conti.items()}
    for n, d in conti.items():
        out["sintesi"][n]["a_mercato"] = nu.numeri(settimane(d)["netto_mercato"].to_numpy())
        out["sintesi"][n]["costi_tripli"] = nu.numeri(settimane(d)["netto_triplo"].to_numpy())
        out["sintesi"][n]["spese_annue"] = float(d["spese"].mean() * 365)
        out["sintesi"][n]["funding_annuo_incassato"] = float(-d["funding"].mean() * 365)
        out["sintesi"][n]["ordini"] = d.attrs
    for n in ("G1", "G1N"):
        log(n, {k: out["sintesi"][n][k] for k in ("sharpe", "annuo", "vol", "discesa", "discesa_giornaliera")})
    # ordini limite piu' severi (il prezzo deve passare il livello dello 0,05% e dello 0,10%)
    for oltre in (0.0005, 0.001):
        for n, Wx in (("G1", W), ("G1N", WN)):
            d = conto(n, Wx, R, F, costo, giorni, simboli, ore, oltre)
            out["sintesi"][n][f"limite_oltre_{oltre}"] = nu.numeri(settimane(d)["netto"].to_numpy())
    wk = {n: settimane(d)["netto"] for n, d in conti.items()}
    out["discese_peggiori"] = {n: discese(wk[n]) for n in ("G1", "G1N")}
    out["bootstrap_G1N_meno_G1"] = bootstrap_coppia(wk["G1"].to_numpy(), wk["G1N"].to_numpy())
    out["bootstrap_fissi_meno_G1"] = bootstrap_coppia(wk["G1"].to_numpy(), wk["G1 a,b medi fissi"].to_numpy())
    out["bootstrap_G1N_meno_fissi"] = bootstrap_coppia(wk["G1 a,b medi fissi"].to_numpy(), wk["G1N"].to_numpy())
    peggiori = wk["G1"].nsmallest(15).index
    out["quindici_peggiori_di_G1"] = {n: float(wk[n].loc[peggiori].mean()) for n in wk}
    # code: la media delle 5% settimane peggiori di ciascuna
    out["cvar_5"] = {n: float(np.sort(wk[n].to_numpy())[:max(1, int(0.05 * len(wk[n])))].mean()) for n in wk}
    out["peggior_settimana"] = {n: float(wk[n].min()) for n in wk}
    out["peggior_giorno"] = {n: float(conti[n]["netto"].min()) for n in conti}

    # ---- 3. esposizione al mercato misurata dopo (beta realizzato) ----
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        mkt_d = np.nanmean(np.where(U, R, np.nan), axis=1)
    mk = pd.Series(mkt_d, index=giorni)
    mkw = settimane(pd.DataFrame({"m": mk}))["m"]
    btcw = settimane(pd.DataFrame({"m": pd.Series(R[:, jb], index=giorni)}))["m"]
    real = {}
    for n in ("G1", "G1N", "G1 a,b medi fissi"):
        y = wk[n].to_numpy()
        real[n] = {"beta_mercato_settimana": float(np.polyfit(mkw.to_numpy(), y, 1)[0]),
                   "beta_btc_settimana": float(np.polyfit(btcw.to_numpy(), y, 1)[0]),
                   "beta_mercato_giorno": float(np.polyfit(mkt_d, conti[n]["netto"].to_numpy(), 1)[0]),
                   "corr_mercato_settimana": float(np.corrcoef(mkw.to_numpy(), y)[0, 1])}
        up = mkw.to_numpy() > np.percentile(mkw.to_numpy(), 90)
        dn = mkw.to_numpy() < np.percentile(mkw.to_numpy(), 10)
        real[n]["media_nel_10pc_rally"] = float(y[up].mean())
        real[n]["media_nel_10pc_crolli"] = float(y[dn].mean())
    out["beta_realizzato"] = real
    log(real)

    # ---- 4. concentrazione: TRX e le monete che pesano ----
    lato_L = np.where(WN > 0, WN, 0).sum(axis=1)
    quota_trx = np.where(lato_L > 0, np.where(WN[:, jt] > 0, WN[:, jt], 0) / np.where(lato_L > 0, lato_L, 1), 0)
    mx = np.abs(WN).max(axis=1)
    contrib = (WN * R - WN * F).sum(axis=0)          # contributo lordo di funding, senza spese, somma dei giorni
    ordine = np.argsort(-contrib)
    tot = float(contrib.sum())
    out["concentrazione"] = {
        "TRX_quota_long_max": float(quota_trx.max()), "TRX_quota_long_media_quando_tenuta": float(quota_trx[quota_trx > 0].mean()),
        "TRX_giorni_tenuta": int((WN[:, jt] != 0).sum()), "TRX_giorni_sopra_20pc_del_long": int((quota_trx > 0.2).sum()),
        "TRX_giorni_sopra_30pc_del_long": int((quota_trx > 0.3).sum()),
        "peso_massimo_di_una_moneta_sul_capitale": float(mx.max()), "peso_massimo_mediano": float(np.median(mx)),
        "contributo_totale_somma_giorni": tot,
        "prime_10": [(simboli[j], float(contrib[j]), float(contrib[j] / tot)) for j in ordine[:10]],
        "ultime_5": [(simboli[j], float(contrib[j])) for j in ordine[-5:]],
        "TRX_contributo": float(contrib[jt]), "TRX_quota_contributo": float(contrib[jt] / tot),
    }
    # lato per lato
    for n, Wx in (("G1", W), ("G1N", WN)):
        L = np.where(Wx > 0, Wx, 0)
        S_ = np.where(Wx < 0, Wx, 0)
        out["sintesi"][n]["long_annuo_lordo_funding"] = float(((L * R).sum(1) - (L * F).sum(1)).mean() * 365)
        out["sintesi"][n]["short_annuo_lordo_funding"] = float(((S_ * R).sum(1) - (S_ * F).sum(1)).mean() * 365)
        out["sintesi"][n]["prezzo_annuo"] = float((Wx * R).sum(1).mean() * 365)
    log(out["concentrazione"]["prime_10"][:5])

    # ---- 5. varianti: senza TRX, con il tetto, ritardi del beta ----
    var = {}
    U_noT = nu.universo_giorni(pan, idx, escludi=(jt,))
    W2, WN2, _ = nu.pesi(pan, idx, U_noT)
    var["G1 senza TRX"] = sintesi(conto("", W2, R, F, costo, giorni, simboli, ore))
    var["G1N senza TRX"] = sintesi(conto("", WN2, R, F, costo, giorni, simboli, ore))
    for tetto in (0.10, 0.20):
        W3, WN3, _ = nu.pesi(pan, idx, U, tetto=tetto)
        var[f"G1 tetto {tetto:.0%}"] = sintesi(conto("", W3, R, F, costo, giorni, simboli, ore))
        var[f"G1N tetto {tetto:.0%}"] = sintesi(conto("", WN3, R, F, costo, giorni, simboli, ore))
    for rit in (1, 7):
        _, WN4, _ = nu.pesi(pan, idx, U, beta_ritardo=rit)
        var[f"G1N beta in ritardo di {rit} giorni"] = sintesi(conto("", WN4, R, F, costo, giorni, simboli, ore))
    # senza le 5 monete che contribuiscono di piu' (a posteriori, solo per misurare la dipendenza)
    top5 = tuple(int(j) for j in ordine[:5])
    U5 = nu.universo_giorni(pan, idx, escludi=top5)
    W5, WN5, _ = nu.pesi(pan, idx, U5)
    var["G1 senza le 5 monete migliori"] = sintesi(conto("", W5, R, F, costo, giorni, simboli, ore))
    var["G1N senza le 5 monete migliori"] = sintesi(conto("", WN5, R, F, costo, giorni, simboli, ore))
    var["_le_5"] = [simboli[j] for j in top5]
    out["varianti"] = var
    for n, v in var.items():
        if not n.startswith("_"):
            log(n, round(v["sharpe"], 3), round(v["annuo"], 3), round(v["discesa"], 3), {y: round(x, 3) for y, x in v["per_anno"].items()})

    # ---- 6. pochi giorni / poche settimane ----
    dip = {}
    for n in ("G1", "G1N"):
        x = conti[n]["netto"]
        w = wk[n]
        dip[n] = {}
        for k in (5, 10, 20):
            dip[n][f"senza i {k} giorni migliori"] = nu.numeri(settimane(pd.DataFrame({"netto": x.drop(x.nlargest(k).index)}))["netto"].to_numpy())
            dip[n][f"senza le {k} settimane migliori"] = nu.numeri(w.drop(w.nlargest(k).index).to_numpy())
        dip[n]["quota_dei_10_giorni_migliori_sul_totale"] = float(x.nlargest(10).sum() / x.sum())
    out["dipendenza"] = dip

    # ---- 7. liquidita' del lato short e capacita' ----
    V = pan["quote_volume"]
    liq = {}
    for n, Wx in (("G1N", WN),):
        rango_vol, vol_med, quote = [], [], []
        for k, i in enumerate(idx):
            u = np.flatnonzero(U[k])
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                med = np.nan_to_num(np.nanmedian(V[i - 30:i], axis=0))
            ordn = u[np.argsort(-med[u], kind="stable")]
            pos = {j: r + 1 for r, j in enumerate(ordn)}
            for j in np.flatnonzero(Wx[k] < 0):
                rango_vol.append(pos.get(j, 101))
                vol_med.append(med[j])
                quote.append((-Wx[k, j], med[j]))
        q = np.array(quote)
        liq["short_rango_volume_mediano"] = float(np.median(rango_vol))
        liq["short_quota_posizioni_fra_51_e_100"] = float(np.mean(np.array(rango_vol) > 50))
        liq["short_volume_giornaliero_mediano_usdt"] = float(np.median(vol_med))
        liq["short_volume_giornaliero_5pc_usdt"] = float(np.percentile(vol_med, 5))
        for cap in (1e4, 1e5, 1e6, 1e7):
            frac = q[:, 0] * cap / np.maximum(q[:, 1], 1)
            liq[f"capitale_{int(cap)}"] = {"posizione_su_volume_mediana": float(np.median(frac)), "massima": float(frac.max()),
                                          "quota_sopra_1pc_del_volume": float((frac > 0.01).mean())}
    out["liquidita"] = liq

    # ---- 8. monete tolte dal listino durante la tenuta, e il funding ----
    C = pan["close"]
    ultimo = np.array([np.flatnonzero(np.isfinite(C[:, j]))[-1] if np.isfinite(C[:, j]).any() else -1 for j in range(C.shape[1])])
    tolte = []
    for j in np.flatnonzero((np.abs(WN) > 0).any(axis=0)):
        if ultimo[j] < C.shape[0] - 3:
            giorni_dopo = np.flatnonzero((WN[:, j] != 0) & (idx >= ultimo[j] - 2))
            if len(giorni_dopo):
                tolte.append({"moneta": simboli[j], "ultima_candela": sc.data(int(ultimo[j] + pan["t0"])),
                              "peso_negli_ultimi_3_giorni": float(WN[giorni_dopo, j].mean()),
                              "esito_ultimi_giorni": float((WN[giorni_dopo, j] * R[giorni_dopo, j]).sum()),
                              "tenuta_dopo_ultima_candela_giorni": int(((WN[:, j] != 0) & (idx > ultimo[j])).sum())})
    out["tolte_dal_listino_tenute"] = tolte
    fd = conti["G1N"]["funding"]
    out["funding_G1N"] = {"incassato_annuo": float(-fd.mean() * 365), "peggior_giorno_pagato": float(fd.max()),
                          "giorni_in_cui_si_paga": float((fd > 0).mean()),
                          "short_peggior_giorno_moneta": None}
    # la perdita peggiore di una sola moneta short in un giorno (in frazione del capitale)
    perd = np.where(WN < 0, WN * R, 0)
    k, j = np.unravel_index(np.argmin(perd), perd.shape)
    out["funding_G1N"]["short_peggior_giorno_moneta"] = {"moneta": simboli[j], "giorno": sc.data(int(giorni[k])),
                                                          "perdita_sul_capitale": float(perd[k, j]), "rialzo": float(R[k, j])}
    perl = np.where(WN > 0, WN * R, 0)
    k, j = np.unravel_index(np.argmin(perl), perl.shape)
    out["funding_G1N"]["long_peggior_giorno_moneta"] = {"moneta": simboli[j], "giorno": sc.data(int(giorni[k])),
                                                         "perdita_sul_capitale": float(perl[k, j]), "ribasso": float(R[k, j])}

    # ---- 9. la banda che parte vuota (il bot G1N e' partito senza posizioni il 25-26 ottobre) ----
    rng = np.random.default_rng(3)
    partenze = sorted(rng.choice(np.arange(200, len(idx) - 60), 20, replace=False))
    conv = []
    for p0 in partenze:
        Wv, _, _ = nu.pesi(pan, idx[p0:p0 + 60], U[p0:p0 + 60])
        uguali = [(np.sign(Wv[t]) == np.sign(W[p0 + t])).all() for t in range(60)]
        diff = [float(np.abs(Wv[t] - W[p0 + t]).sum()) for t in range(60)]
        primo_uguale = next((t for t, x in enumerate(uguali) if x), None)
        conv.append({"partenza": sc.data(int(giorni[p0])), "giorno_in_cui_coincide": primo_uguale,
                     "diff_lorda_g0": diff[0], "diff_lorda_g7": diff[7], "diff_lorda_g30": diff[30]})
    out["banda_da_vuota"] = conv
    gc = [c["giorno_in_cui_coincide"] for c in conv if c["giorno_in_cui_coincide"] is not None]
    out["banda_da_vuota_sintesi"] = {"mediana_giorni": float(np.median(gc)) if gc else None, "massimo": max(gc) if gc else None,
                                    "mai_entro_60": sum(1 for c in conv if c["giorno_in_cui_coincide"] is None),
                                    "diff_lorda_media_g0": float(np.mean([c["diff_lorda_g0"] for c in conv])),
                                    "diff_lorda_media_g7": float(np.mean([c["diff_lorda_g7"] for c in conv])),
                                    "diff_lorda_media_g30": float(np.mean([c["diff_lorda_g30"] for c in conv]))}
    log(out["banda_da_vuota_sintesi"])

    (QUI / "risultati.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    log(f"FATTO in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
