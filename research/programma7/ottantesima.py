"""Programma 7, ottantesima prova (OTTANTESIMA.md): G1S, G1 dentro ogni settore. Il rango del funding dei 7 giorni si calcola dentro il
settore della moneta (settori di CoinGecko); tutto il resto come G1. Si giudica sui rischi come la prova 124.

Uso: python3 -m research.programma7.ottantesima
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import annunci as an
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import cinquantaduesima as kp
from research.programma7 import prima as g1

QUI = Path(__file__).parent
RIS = QUI / "risultati_ottantesima"
DATI = QUI.parent / "data" / "coingecko_settori.json"
SETTORI = (("meme", "meme-token"), ("intelligenza artificiale", "artificial-intelligence"), ("giochi", "gaming"),
           ("finanza decentralizzata", "decentralized-finance-defi"), ("reti di secondo livello", "layer-2"),
           ("reti principali", "layer-1"), ("reti principali", "smart-contract-platform"))
MIN_SETTORE = 5


def categorie() -> dict:
    """{categoria: [sigle]} dalle monete di CoinGecko per categoria (fino a 1.000 per categoria), salvate in DATI."""
    if DATI.exists():
        return json.loads(DATI.read_text())
    out = {}
    for _, cat in SETTORI:
        sigle = []
        for p in range(1, 5):
            u = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category={cat}&order=market_cap_desc&per_page=250&page={p}"
            d = None
            for k in range(4):
                try:
                    with urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "ricerca/1.0"}), timeout=60) as r:
                        d = json.load(r)
                    break
                except Exception:  # noqa: BLE001
                    time.sleep(20 * (k + 1))
            time.sleep(4)
            if not d:
                break
            sigle += [(x.get("symbol") or "").upper() for x in d]
            if len(d) < 250:
                break
        out[cat] = sigle
    DATI.parent.mkdir(parents=True, exist_ok=True)
    DATI.write_text(json.dumps(out))
    return out


def settore_di(simboli: list) -> np.ndarray:
    cat = categorie()
    out = np.array(["altro"] * len(simboli), dtype=object)
    for j, s in enumerate(simboli):
        for nome, c in SETTORI:
            if any(an.perpetuo(x, [s]) == s for x in cat.get(c, [])):
                out[j] = nome
                break
    return out


def rango_nel_settore(ct: np.ndarray, U: np.ndarray, sett: np.ndarray) -> np.ndarray:
    out = np.full(ct.shape, np.nan)
    for k in range(ct.shape[0]):
        ok = U[k] & np.isfinite(ct[k])
        if not ok.any():
            continue
        s = sett.copy()
        nomi, conti = np.unique(s[ok], return_counts=True)
        for n, c in zip(nomi, conti):
            if c < MIN_SETTORE:
                s[s == n] = "altro"
        for n in np.unique(s[ok]):
            jj = np.flatnonzero(ok & (s == n))
            if len(jj) == 1:
                out[k, jj] = 0.5
            else:
                out[k, jj] = pd.Series(ct[k, jj]).rank(pct=True).to_numpy()
    return out


def esposizione_settori(W: np.ndarray, sett: np.ndarray) -> dict:
    nomi = sorted(set(sett))
    E = np.stack([W[:, sett == n].sum(axis=1) for n in nomi], axis=1)
    attivi = np.abs(W).sum(axis=1) > 0
    return {"piu_comprato_medio": float(E[attivi].max(axis=1).mean()), "piu_venduto_medio": float(E[attivi].min(axis=1).mean()),
            "per_settore_medio": {n: float(E[attivi, i].mean()) for i, n in enumerate(nomi)}}


def esegui(log=print) -> dict:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    S = list(pan["simboli"])
    sett = settore_di(S)
    giorni = np.arange(se.INIZIO, g1.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = g1.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    ct0 = np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan)
    conti_settori = {n: int(((sett == n) & Ud.any(axis=0)).sum()) for n in sorted(set(sett))}
    log(f"[ottantesima] monete dell'universo per settore: {conti_settori}")
    R = sc.rendimenti(pan)[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = sc.costi_moneta(pan["simboli"])
    btc = pd.Series(ps["R"][:, ps["simboli"].index("BTCUSDT")], index=ps["lunedi"])
    out, sett_df, Ws = {}, {}, {}
    RIS.mkdir(exist_ok=True)
    for nome, ct in (("G1", ct0), ("G1S", rango_nel_settore(ct0, Ud, sett))):
        W = vq.pesi_banda(ct, Ud, sig)
        lim, ordini = kp.conto(W, R, F, costo, giorni, pan["simboli"])
        s = g1.per_settimana(lim, giorni)
        s.to_csv(RIS / f"settimane_{nome}.csv.gz")
        e = te.esame(s, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        e["giorno_peggiore"] = float(lim["netto"].min())
        e["esposizione_settori"] = esposizione_settori(W, sett)
        out[nome], sett_df[nome], Ws[nome] = e, s, W
    a, b = out["G1"]["intero"], out["G1S"]["intero"]
    passa = bool(b["discesa_max"] > a["discesa_max"] and b["sharpe"] >= a["sharpe"] - 0.10)
    c = sett_df["G1"].index.intersection(sett_df["G1S"].index)
    corr = float(np.corrcoef(sett_df["G1"].loc[c, "netto"], sett_df["G1S"].loc[c, "netto"])[0, 1])
    (RIS / "esame.json").write_text(json.dumps({"settori": conti_settori, **out, "passa": passa, "correlazione": corr},
                                               ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    pc = lambda v: f"{100 * v:+.1f}%"  # noqa: E731
    righe = ["# Programma 7 — risultati dell'ottantesima prova (G1S: G1 dentro ogni settore)", "",
             "Regole in `OTTANTESIMA.md` (scritte prima). Dal 4 gennaio 2021 al 5 ottobre 2026, stesso codice e stessi dati per G1 e G1S.", "",
             "* Monete passate per l'universo, per settore: " + ", ".join(f"{k} {v}" for k, v in conti_settori.items()) + "."]
    for nome in ("G1", "G1S"):
        e = out[nome]
        i, x = e["intero"], e["esposizione_settori"]
        righe += [f"* **{nome}: Sharpe {i['sharpe']:.2f}**, {pc(i['annuo'])} l'anno, volatilità {100 * i['volatilita']:.1f}%, **discesa "
                  f"{100 * i['discesa_max']:.1f}%**, giorno peggiore {pc(e['giorno_peggiore'])}; spese {100 * e['spese_annue']:.1f}% l'anno; "
                  f"il settore più comprato pesa in media {pc(x['piu_comprato_medio'])}, il più venduto {pc(x['piu_venduto_medio'])}.",
                  "  * Per anno: " + ", ".join(f"{a_} {pc(v)}" for a_, v in e["per_anno"].items()) + ".",
                  "  * Peso medio per settore: " + ", ".join(f"{k} {pc(v)}" for k, v in x["per_settore_medio"].items()) + "."]
    righe += [f"* Correlazione fra G1 e G1S: {corr:.2f}.", "",
              f"**Esito: {'passa' if passa else 'no'}** (la regola: discesa più bassa di G1 e Sharpe non più di 0,10 sotto)."]
    testo = "\n".join(righe) + "\n"
    (QUI / "RISULTATI_OTTANTESIMA.md").write_text(testo, encoding="utf-8")
    log(testo)
    return out


if __name__ == "__main__":
    esegui(log=lambda x: print(x, flush=True))
    print("OTTANTESIMA FINITA", flush=True)
