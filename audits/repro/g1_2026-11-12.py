"""Audit di G1 per il conto vero (12 nov 2026): ricalcolo di G1 (prova 57, con `nucleo`) e del conto A a 280 USDT (prova 148),
controlli dei dati, taglio, sensibilita', costi, leva e liquidazione, concentrazione, climi di mercato.

Non scrive fuori da `audits/` (le candele orarie in cache nella cartella data da CACHE_G1N, da mettere nello scratchpad).
Uso: CACHE_G1N=<cartella temporanea> PYTHONPATH=<radice> python3 audits/repro/g1_2026-11-12.py <parte>
parti: base | taglio | sensibilita | dati | rischio | misure
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
from research.programma7 import ottantaseiesima as o86
from research.programma7.revisione_g1n import analisi as an
from research.programma7.revisione_g1n import nucleo as nu

QUI = Path(__file__).parent
CACHE = Path(os.environ.get("CACHE_G1N", "/tmp/cache_g1n"))
ESITO = QUI / f"g1_2026-11-12_esito_{sys.argv[1] if len(sys.argv) > 1 else 'x'}.json"
INIZIO, FINE = an.INIZIO, an.FINE


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def salva(chiave, valore):
    d = json.loads(ESITO.read_text()) if ESITO.exists() else {}
    d[chiave] = valore
    ESITO.write_text(json.dumps(d, indent=1, ensure_ascii=False, default=float))


def basi():
    f = CACHE / "basi.pkl"
    if f.exists():
        return pickle.loads(f.read_bytes())
    pan = sc.pannello()
    simboli = pan["simboli"]
    giorni = np.arange(INIZIO, FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]
    F = np.nan_to_num(pan["funding"][idx])
    O = pan["open"][idx]
    costo = np.array([nu.costo_di(s) for s in simboli])
    U = nu.universo_giorni(pan, idx)
    W, _, _ = nu.pesi(pan, idx, U, fisso=(1.0, 1.0))
    usati = [simboli[j] for j in np.flatnonzero(np.abs(W).sum(axis=0) > 0)]
    ore = an.candele_ore(usati)
    b = dict(simboli=simboli, giorni=giorni, idx=idx, R=R, F=F, O=O, costo=costo, U=U, W=W, ore=ore, t0=pan["t0"])
    f.write_bytes(pickle.dumps(b))
    return b


def sint(d, col="netto"):
    s = an.sintesi(d, col)
    return {k: s[k] for k in ("sharpe", "annuo", "vol", "discesa", "discesa_giornaliera", "per_anno", "n")}


def conto_A(b, cap=280.0, Wx=None, oltre=0.0, minimi=True, chiusure=False):
    Wx = b["W"] if Wx is None else Wx
    vmin, passo, qmin = o86.carica_filtri(b["simboli"])
    X, D, st = o86.conto_vero(Wx, b["R"], b["O"], cap, vmin, passo, qmin, minimi, chiusure)
    sp, n, n_lim = nu.spese_limite(D, b["giorni"], b["simboli"], b["costo"], b["ore"], oltre)
    d = pd.DataFrame({"lordo": (X * b["R"]).sum(axis=1), "funding": (X * b["F"]).sum(axis=1), "spese": sp}, index=b["giorni"])
    # tutto a mercato sugli stessi ordini eseguiti
    d["spese_mercato"] = (np.abs(D) @ b["costo"])
    d["netto"] = d["lordo"] - d["spese"] - d["funding"]
    d["netto_mercato"] = d["lordo"] - d["spese_mercato"] - d["funding"]
    d.attrs = {"variazioni": n, "a_limite": n_lim, **st}
    return d, X, D


def parte_base():
    b = basi()
    out = {}
    d = an.conto("G1", b["W"], b["R"], b["F"], b["costo"], b["giorni"], b["simboli"], b["ore"])
    out["G1_nucleo"] = sint(d)
    out["G1_nucleo_mercato"] = sint(d, "netto_mercato")
    out["G1_variazioni"] = d.attrs
    out["G1_spese_annue"] = float(d["spese"].mean() * 365)
    out["G1_funding_incassato_annuo"] = float(-d["funding"].mean() * 365)
    dA, X, D = conto_A(b)
    out["A280"] = sint(dA)
    out["A280_mercato"] = sint(dA, "netto_mercato")
    out["A280_conteggi"] = {k: (int(v) if isinstance(v, (int, np.integer)) else v) for k, v in dA.attrs.items()}
    out["A280_spese_annue"] = float(dA["spese"].mean() * 365)
    out["A280_funding_incassato_annuo"] = float(-dA["funding"].mean() * 365)
    d0, _, _ = conto_A(b, minimi=False)
    out["G1_senza_minimi_capitale_fisso"] = sint(d0)
    # confronto con i giorni committati della prova 148
    g = pd.read_csv(o86.OUT / "giorni.csv.gz", index_col=0)
    out["confronto_giorni_148"] = {
        "A_diff_max": float((g["A, 280 USDT"] - dA["netto"]).abs().max()),
        "G1_diff_max": float((g["G1 senza minimi"] - d0["netto"]).abs().max()),
        "A_giorni_diversi_oltre_1e-6": int(((g["A, 280 USDT"] - dA["netto"]).abs() > 1e-6).sum())}
    pd.DataFrame({"G1": d["netto"], "A280": dA["netto"], "G1fisso": d0["netto"], "A280_lordo": dA["lordo"],
                  "A280_funding": dA["funding"], "A280_spese": dA["spese"]}).to_csv(CACHE / "giorni.csv")
    np.save(CACHE / "X_A280.npy", X)
    np.save(CACHE / "D_A280.npy", D)
    for k, v in out.items():
        log(k, json.dumps(v, default=float)[:300])
    salva("base", out)



# ---------------------------------------------------------------------------
# B. sguardo nel futuro: pannello tagliato (come parita_bot.tagliato, ma con nucleo e con l'universo rifatto)
# ---------------------------------------------------------------------------

def tagliato(pan, d):
    i = d - pan["t0"]
    p = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in pan.items()}
    for k in ("high", "low", "close", "quote_volume", "taker_buy_quote_volume"):
        p[k][i:] = np.nan
    p["open"][i + 1:] = np.nan
    p["funding"][i:] = 0.0
    return p


def parte_taglio():
    b = basi()
    pan = sc.pannello()
    rng = np.random.default_rng(1112)
    prove = sorted(set(rng.choice(np.arange(INIZIO + 200, FINE - 1), 5, replace=False).tolist()) | {FINE - 1, INIZIO + 400})
    out = []
    for d in prove:
        p = tagliato(pan, int(d))
        giorni = np.arange(INIZIO, d + 1, dtype=np.int64)
        idx = giorni - p["t0"]
        U = nu.universo_giorni(p, idx)
        W2, _, _ = nu.pesi(p, idx, U, fisso=(1.0, 1.0))
        k = int(d - INIZIO)
        r = {"giorno": sc.data(int(d)), "diff_max": float(np.abs(W2[k] - b["W"][k]).max()),
             "universo_uguale": bool((U[k] == b["U"][k]).all()), "monete": int((b["W"][k] != 0).sum())}
        log(r)
        out.append(r)
    salva("taglio", out)


# ---------------------------------------------------------------------------
# E. sensibilita' (G1 senza minimi, conto con limite) e C. ordine limite piu' severo
# ---------------------------------------------------------------------------

def _g1_con(b, pan, entra=0.20, resta=0.40, giorni_f=7, giorni_s=30, n_uni=100):
    vecchi = (nu.ENTRA, nu.RESTA, nu.N_UNI, nu.funding7, nu.sigma30)
    try:
        nu.ENTRA, nu.RESTA, nu.N_UNI = entra, resta, n_uni
        nu.funding7 = lambda F, i: np.round(F[i - giorni_f:i].sum(axis=0), 12)

        def s30(rc, i):
            f = rc[i - giorni_s:i]
            n = np.isfinite(f).sum(axis=0)
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                sd = np.nanstd(f, axis=0, ddof=1)
            return np.where((n >= round(20 * giorni_s / 30)) & (sd > 0), sd, np.nan)
        nu.sigma30 = s30
        U = b["U"] if n_uni == 100 else nu.universo_giorni(pan, b["idx"])
        W, _, _ = nu.pesi(pan, b["idx"], U, fisso=(1.0, 1.0))
    finally:
        nu.ENTRA, nu.RESTA, nu.N_UNI, nu.funding7, nu.sigma30 = vecchi
    usati = [b["simboli"][j] for j in np.flatnonzero(np.abs(W).sum(axis=0) > 0)]
    ore = an.candele_ore(usati) if any(s not in b["ore"] for s in usati) else b["ore"]
    d = an.conto("x", W, b["R"], b["F"], b["costo"], b["giorni"], b["simboli"], ore)
    return sint(d), W


def parte_sensibilita():
    b = basi()
    pan = sc.pannello()
    out = {}
    # ordine limite piu' severo: eseguito solo se il prezzo va oltre di `oltre`
    for oltre in (0.0002, 0.0005, 0.001, 0.002):
        d = an.conto("G1", b["W"], b["R"], b["F"], b["costo"], b["giorni"], b["simboli"], b["ore"], oltre)
        dA, _, _ = conto_A(b, oltre=oltre)
        out[f"oltre_{oltre}"] = {"G1": sint(d), "G1_quota_limite": d.attrs["a_limite"] / d.attrs["variazioni"],
                                 "A280": sint(dA), "A280_quota_limite": dA.attrs["a_limite"] / dA.attrs["variazioni"]}
        log("oltre", oltre, round(out[f"oltre_{oltre}"]["G1"]["sharpe"], 3), round(out[f"oltre_{oltre}"]["A280"]["sharpe"], 3))
    # tutto il limite pagato da taker (gli ordini GTC al mark che attraversano il libro)
    vmin, passo, qmin = o86.carica_filtri(b["simboli"])
    salva("sensibilita_limite", out)
    var = {"entra_0.16": dict(entra=0.16), "entra_0.18": dict(entra=0.18), "entra_0.22": dict(entra=0.22),
           "entra_0.24": dict(entra=0.24), "resta_0.32": dict(resta=0.32), "resta_0.36": dict(resta=0.36),
           "resta_0.44": dict(resta=0.44), "resta_0.48": dict(resta=0.48), "funding_6": dict(giorni_f=6),
           "funding_8": dict(giorni_f=8), "sigma_24": dict(giorni_s=24), "sigma_27": dict(giorni_s=27),
           "sigma_33": dict(giorni_s=33), "sigma_36": dict(giorni_s=36), "universo_80": dict(n_uni=80),
           "universo_90": dict(n_uni=90), "universo_110": dict(n_uni=110), "universo_120": dict(n_uni=120)}
    res = {}
    for nome, kw in var.items():
        s, W = _g1_con(b, pan, **kw)
        bb = dict(b, W=W)
        if any(sym not in b["ore"] for sym in [b["simboli"][j] for j in np.flatnonzero(np.abs(W).sum(axis=0) > 0)]):
            bb["ore"] = an.candele_ore([b["simboli"][j] for j in np.flatnonzero(np.abs(W).sum(axis=0) > 0)])
        dA, _, _ = conto_A(bb)
        res[nome] = {"G1": s, "A280": sint(dA)}
        log(nome, round(s["sharpe"], 3), round(res[nome]["A280"]["sharpe"], 3), {y: round(v, 3) for y, v in s["per_anno"].items()})
        salva("sensibilita_parametri", res)


if __name__ == "__main__":
    globals()["parte_" + sys.argv[1]]()
