"""Programma 7, ottantaseiesima prova (prova 148 del registro): G1 con 250 euro (`OTTANTASEIESIMA.md`, regole scritte prima).

Il conto vero simulato a capitale fisso con i minimi di Binance di oggi (`risultati_ottantaseiesima/filtri_binance_2026-11-06.json`):
G1 senza minimi (il riferimento), A come il bot oggi, A2 con le chiusure «solo riduzione» permesse sotto il valore minimo, B con le 10
monete di peso piu' grande per lato (poi come A2). Basi, dati e spese della revisione di G1N (`revisione_g1n/nucleo.py`).

Uso: CACHE_G1N=<cartella per le candele orarie> python3 -m research.programma7.ottantaseiesima
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import analisi as an
from research.programma7.revisione_g1n import nucleo as nu

QUI = Path(__file__).parent
OUT = QUI / "risultati_ottantaseiesima"
FILTRI = OUT / "filtri_binance_2026-11-06.json"
INIZIO, FINE = an.INIZIO, an.FINE
CAPITALE = 280.0
K_LATO = 10
EPS = 1e-6


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def carica_filtri(simboli: list, quale: str = "vero"):
    """(valore minimo, passo, quantita' minima) per moneta; le monete che oggi non sono nel listino: 5 USDT, nessun passo."""
    f = json.loads(FILTRI.read_text(encoding="utf-8"))[quale]
    vmin = np.array([f[s]["valore_minimo"] if s in f else 5.0 for s in simboli])
    passo = np.array([f[s]["passo"] if s in f else 0.0 for s in simboli])
    qmin = np.array([f[s]["quantita_minima"] if s in f else 0.0 for s in simboli])
    return vmin, passo, qmin


def meno_monete(W: np.ndarray, k: int) -> np.ndarray:
    """B: per lato le k monete con il peso piu' grande, con i pesi riscalati al totale del lato."""
    out = np.zeros_like(W)
    for t in range(W.shape[0]):
        for segno in (1.0, -1.0):
            idx = np.flatnonzero(np.sign(W[t]) == segno)
            if not len(idx):
                continue
            tieni = idx[np.argsort(-np.abs(W[t, idx]), kind="stable")[:k]]
            out[t, tieni] = W[t, tieni] / np.abs(W[t, tieni]).sum() * np.abs(W[t, idx]).sum()
    return out


def conto_vero(W, R, O, capitale, vmin, passo, qmin, minimi=True, chiusure=False):
    """Il conto a capitale fisso. W: pesi voluti (frazione del capitale); R: rendimento da un'apertura all'altra; O: prezzi di apertura.
    Ritorna X (posizioni tenute nel giorno), D (ordini eseguiti), in frazione del capitale, e i conteggi."""
    T, S = W.shape
    P = np.zeros(S)
    X = np.zeros_like(W)
    D = np.zeros_like(W)
    voluti = saltati = polvere = 0
    vivo = np.isfinite(O) & (O > 0)
    for k in range(T):
        obi = W[k] * capitale
        delta = obi - P
        da_fare = np.abs(delta) > 1e-9
        if minimi:
            o = O[k]
            ok_p = np.isfinite(o) & (o > 0)
            o0 = np.where(ok_p, o, 0.0)
            sv = passo * o0                                       # valore di un passo di quantita'
            q = np.where(sv > 0, np.floor(np.abs(delta) / np.where(sv > 0, sv, 1.0) + EPS) * sv, np.abs(delta))
            # la chiusura e' sempre della posizione intera: sul conto vero la quantita' tenuta e' un multiplo del passo, qui il
            # valore puo' lasciare un resto sotto un passo dopo i giorni senza prezzo nei dati (correzione del 6 novembre, dopo il primo
            # calcolo: resti di meno di un centesimo che restavano aperti per anni)
            q = np.where((obi == 0) & (np.abs(delta) - q < sv + 1e-12), np.abs(delta), q)
            riduce = (obi == 0) | ((P != 0) & (np.sign(P) == np.sign(obi)) & (np.abs(obi) < np.abs(P)))
            ok = ok_p & (q > 1e-12) & (q >= qmin * o0 - 1e-12)
            ok &= (riduce | (q >= vmin - 1e-12)) if chiusure else (q >= vmin - 1e-12)
            d = np.where(ok & da_fare, np.sign(delta) * q, 0.0)
        else:
            d = np.where(da_fare, delta, 0.0)
        voluti += int(da_fare.sum())
        saltati += int((da_fare & (d == 0)).sum())
        P = P + d
        X[k] = P / capitale
        D[k] = d / capitale
        polvere += int(((obi == 0) & (np.abs(P) > 1e-9) & vivo[k]).sum())
        P = P * (1 + R[k])
    return X, D, {"ordini_voluti": voluti, "ordini_saltati": saltati, "posizioni_rimaste_giorno": polvere}


def netto_del_conto(X, D, R, F, costo, giorni, simboli, ore) -> pd.DataFrame:
    sp, n, n_lim = nu.spese_limite(D, giorni, simboli, costo, ore)
    d = pd.DataFrame({"lordo": (X * R).sum(axis=1), "funding": (X * F).sum(axis=1), "spese": sp}, index=giorni)
    d["netto"] = d["lordo"] - d["spese"] - d["funding"]
    d.attrs = {"variazioni": n, "a_limite": n_lim}
    return d


def esame(a: dict, rif: dict) -> dict:
    anni = {y: v for y, v in a["per_anno"].items()}
    return {"sharpe_rapporto": a["sharpe"] / rif["sharpe"], "sharpe_almeno_90pc": a["sharpe"] >= 0.9 * rif["sharpe"],
            "discesa_differenza_punti": (a["discesa"] - rif["discesa"]) * 100,
            "discesa_al_massimo_5_punti": a["discesa"] >= rif["discesa"] - 0.05,
            "ogni_anno_positivo": all(v > 0 for v in anni.values()),
            "passa": bool(a["sharpe"] >= 0.9 * rif["sharpe"] and a["discesa"] >= rif["discesa"] - 0.05
                          and all(v > 0 for v in anni.values()))}


def main():
    t0 = time.time()
    pan = sc.pannello()
    simboli = pan["simboli"]
    giorni = np.arange(INIZIO, FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]
    F = np.nan_to_num(pan["funding"][idx])
    O = pan["open"][idx]
    costo = np.array([nu.costo_di(s) for s in simboli])
    U = nu.universo_giorni(pan, idx)
    log("universo pronto")
    W, _, _ = nu.pesi(pan, idx, U, fisso=(1.0, 1.0))
    WB = meno_monete(W, K_LATO)
    log("pesi pronti", f"{time.time() - t0:.0f} s")
    usati = [simboli[j] for j in np.flatnonzero(np.abs(W).sum(axis=0) > 0)]
    ore = an.candele_ore(usati)
    log("candele orarie pronte", len(usati))
    vmin, passo, qmin = carica_filtri(simboli)

    out = {"capitale_usdt": CAPITALE, "giorni": [sc.data(int(giorni[0])), sc.data(int(giorni[-1]))], "conti": {}}
    # controllo del simulatore: G1 senza minimi contro nucleo.variazioni (capitale che si compone)
    d_nu = an.conto("G1", W, R, F, costo, giorni, simboli, ore)
    out["controllo_nucleo"] = an.sintesi(d_nu)

    def fai(nome, Wx, cap, minimi, chiusure):
        X, D, st = conto_vero(Wx, R, O, cap, vmin, passo, qmin, minimi, chiusure)
        d = netto_del_conto(X, D, R, F, costo, giorni, simboli, ore)
        s = an.sintesi(d)
        vivo = np.isfinite(O) & (O > 0)                         # le posizioni nei giorni senza prezzo non contano nelle misure
        lordo_voluto = np.abs(Wx).sum(axis=1)
        tenuto = (np.abs(X) * vivo).sum(axis=1)
        s.update(st)
        s["esposizione_tenuta_su_voluta"] = float(tenuto.sum() / lordo_voluto.sum())
        s["ordini_eseguiti_al_giorno"] = float((np.abs(D) > 1e-12).sum() / len(giorni))
        s["spese_annue"] = float(d["spese"].sum() / len(giorni) * 365)
        s["funding_annuo_pagato"] = float(d["funding"].sum() / len(giorni) * 365)
        s["monete_tenute_al_giorno"] = float(((np.abs(X) > 1e-12) & vivo).sum() / len(giorni))
        polv = (Wx == 0) & vivo & (np.abs(X) > 1e-12)
        s["valore_posizioni_rimaste_in_frazione_del_capitale"] = float((np.abs(X) * polv).sum(axis=1).mean())
        s["monete_volute_al_giorno"] = float((np.abs(Wx) > 1e-12).sum() / len(giorni))
        out["conti"][nome] = s
        log(nome, f"Sharpe {s['sharpe']:.2f}", f"annuo {s['annuo']:+.1%}", f"discesa {s['discesa']:.1%}",
            f"esposizione {s['esposizione_tenuta_su_voluta']:.0%}")
        return d

    rif = fai("G1 senza minimi", W, CAPITALE, False, False)
    serie = {"G1 senza minimi": rif["netto"]}
    for nome, Wx, cap, ch in (("A, 280 USDT", W, CAPITALE, False), ("A2, 280 USDT", W, CAPITALE, True),
                              ("B, 280 USDT", WB, CAPITALE, True),
                              ("A, 200 USDT", W, 200.0, False),   # per capire, aggiunto dopo il primo calcolo: il conto dopo una discesa
                              ("A, 1.000 USDT", W, 1000.0, False), ("A2, 1.000 USDT", W, 1000.0, True),
                              ("A, 5.000 USDT", W, 5000.0, False), ("A2, 5.000 USDT", W, 5000.0, True)):
        d = fai(nome, Wx, cap, True, ch)
        serie[nome] = d["netto"]
        out["conti"][nome]["oscillazione_differenza_giornaliera"] = float((d["netto"] - rif["netto"]).std(ddof=1))
        out["conti"][nome]["correlazione_settimanale_con_G1"] = float(
            an.settimane(pd.DataFrame({"a": d["netto"], "b": rif["netto"]})).corr().iloc[0, 1])
    # per capire (aggiunto dopo il primo calcolo, non decide niente): quanto il risultato di A cambia con il capitale
    out["capitali_per_capire"] = {}
    for cap in (150, 200, 225, 250, 280, 300, 350, 400, 500, 700, 1000, 2000):
        X, D, _ = conto_vero(W, R, O, float(cap), vmin, passo, qmin, True, False)
        d = netto_del_conto(X, D, R, F, costo, giorni, simboli, ore)
        s = an.sintesi(d)
        out["capitali_per_capire"][str(cap)] = {"sharpe": s["sharpe"], "annuo": s["annuo"], "discesa": s["discesa"],
                                                "oscillazione_differenza_giornaliera": float((d["netto"] - rif["netto"]).std(ddof=1)),
                                                "anni_negativi": [y for y, v in s["per_anno"].items() if v <= 0]}
        log("capitale", cap, f"Sharpe {s['sharpe']:.2f}", f"annuo {s['annuo']:+.1%}", f"discesa {s['discesa']:.1%}")
    rs = out["conti"]["G1 senza minimi"]
    out["esame"] = {n: esame(out["conti"][n], rs) for n in ("A, 280 USDT", "A2, 280 USDT", "B, 280 USDT")}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "risultati.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(serie).to_csv(OUT / "giorni.csv.gz", float_format="%.8f")
    log("fatto", f"{time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
