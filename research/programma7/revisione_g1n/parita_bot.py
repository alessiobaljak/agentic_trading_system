"""Revisione di G1N (29 ottobre 2026): due controlli meccanici.

1. **Sguardo nel futuro.** I pesi di G1N del giorno d calcolati dalla ricerca (`ventiseiesima`) sul pannello vero e sul pannello
   tagliato alle 00:00 del giorno d (prezzi dopo l'apertura di d cancellati, funding dei giorni di tenuta da d in poi a zero):
   se coincidono, i pesi non usano niente del giorno d o dopo.
2. **Bot contro ricerca sui dati veri.** Le funzioni pure del bot (`bot/portafoglio/f5.py`: universo, sigma_30, funding_7,
   pesi_banda, beta_delle_monete, scala_neutra) con gli stessi dati della ricerca per una serie di giorni; la banda del giorno
   prima e' quella della ricerca. La chiusura del giorno d (la candela in corso alle 00:05) e' messa a un valore falso: se il bot
   la usasse, i numeri cambierebbero.

Uso: python3 -m research.programma7.revisione_g1n.parita_bot
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from bot.portafoglio import f5 as bot
from research.programma6 import ottava as ot
from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma6 import ventiquattresima as vq
from research.programma7 import prima as pr
from research.programma7 import ventiquattresima as f5n

QUI = Path(__file__).parent
INIZIO, FINE = sc.giorno(2021, 1, 4), sc.giorno(2026, 10, 5)


def ricerca(pan: dict, fine: int):
    """I pesi di G1 e G1N della ricerca dal 4 gennaio 2021 al giorno ``fine`` compreso (come `ventiseiesima.esegui`)."""
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(INIZIO, fine + 1, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    sig = ot.sigma_30(pan, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
    beta = f5n.beta_delle_monete(pan, Ud, idx)
    WN, a, b, bl, bs = f5n.scala_neutra(W, beta)
    return giorni, Ud, sig, W, beta, WN


def tagliato(pan: dict, d: int) -> dict:
    i = d - pan["t0"]
    p = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in pan.items()}
    for k in ("high", "low", "close", "quote_volume", "taker_buy_quote_volume"):
        p[k][i:] = np.nan
    p["open"][i + 1:] = np.nan               # l'apertura delle 00:00 del giorno d e' nota
    p["funding"][i:] = 0.0                   # i regolamenti dalle 08:00 di d in poi
    return p


def main():
    pan = sc.pannello()
    out = {}
    giorni, Ud, sig, W, beta, WN = ricerca(pan, FINE - 1)
    rng = np.random.default_rng(11)
    # --- 1. pannello tagliato ---
    prove = sorted(set(rng.choice(np.arange(INIZIO + 120, FINE - 1), 5, replace=False).tolist()) | {FINE - 1})
    fut = []
    for d in prove:
        g2, _, _, W2, _, WN2 = ricerca(tagliato(pan, int(d)), int(d))
        k = int(d - INIZIO)
        fut.append({"giorno": sc.data(int(d)), "diff_max_G1N": float(np.abs(WN2[k] - WN[k]).max()),
                    "diff_max_G1": float(np.abs(W2[k] - W[k]).max()), "monete": int((WN[k] != 0).sum())})
        print(fut[-1], flush=True)
    out["pannello_tagliato"] = fut

    # --- 2. bot contro ricerca ---
    simboli = pan["simboli"]
    C, O, V, F = pan["close"], pan["open"], pan["quote_volume"], pan["funding"]
    ok = np.isfinite(C)
    primo_i = np.where(ok.any(axis=0), ok.argmax(axis=0), C.shape[0])
    primo = {s: int(primo_i[j] + pan["t0"]) for j, s in enumerate(simboli)}
    giorni_prova = sorted(rng.choice(np.arange(INIZIO + 1, FINE), 60, replace=False).tolist())
    righe = []
    for d in giorni_prova:
        k = int(d - INIZIO)
        i = int(d - pan["t0"])
        attivi = [j for j in range(len(simboli)) if np.isfinite(C[i - 99:i + 1, j]).any()]
        giornaliere = {}
        for j in attivi:
            s = simboli[j]
            g = {}
            for t in range(i - 99, i + 1):
                if np.isfinite(O[t, j]) or np.isfinite(C[t, j]):
                    chiusura = C[t, j] if t < i else C[t, j] * 7.0      # la candela in corso: valore falso
                    vol = V[t, j] if t < i else V[t, j] * 7.0
                    g[t + pan["t0"]] = (float(O[t, j]), float(chiusura), float(vol))
            giornaliere[s] = g
        lun = bot.lunedi_di(int(d))
        uni = bot.universo(giornaliere, {s: primo[s] for s in giornaliere}, lun)
        uni_r = sorted(simboli[j] for j in np.flatnonzero(Ud[k]))
        sigma = {s: bot.sigma_30({t: v[1] for t, v in giornaliere[s].items()}, int(d)) for s in uni}
        funding = {s: {t + pan["t0"]: float(F[t, simboli.index(s)]) for t in range(i - 8, i)} for s in uni}
        segnale = {s: (-bot.funding_7(funding[s], int(d)) if np.isfinite(sigma[s]) else float("nan")) for s in uni}
        prev = W[k - 1] if k > 0 else np.zeros(len(simboli))
        lunghi = {simboli[j] for j in np.flatnonzero(prev > 0)}
        corti = {simboli[j] for j in np.flatnonzero(prev < 0)}
        pesi, _, _ = bot.pesi_banda(segnale, sigma, lunghi, corti)
        chiusure = {s: {t: v[1] for t, v in giornaliere[s].items()} for s in uni}
        b = bot.beta_delle_monete(chiusure, uni, int(d))
        pesi_n, a, bb, bl, bs = bot.scala_neutra(pesi, b)
        vett = np.zeros(len(simboli))
        for s, w in pesi_n.items():
            vett[simboli.index(s)] = w
        vett_g1 = np.zeros(len(simboli))
        for s, w in pesi.items():
            vett_g1[simboli.index(s)] = w
        jb = [simboli.index(s) for s in uni]
        righe.append({"giorno": sc.data(int(d)), "universo_uguale": sorted(uni) == uni_r,
                      "diff_universo": len(set(uni) ^ set(uni_r)),
                      "diff_max_G1": float(np.abs(vett_g1 - W[k]).max()), "diff_max_G1N": float(np.abs(vett - WN[k]).max()),
                      "diff_max_beta": float(np.max(np.abs(np.array([b[s] for s in uni]) - beta[k, jb]))) if uni else None,
                      "lati_cambiati": int((np.sign(vett) != np.sign(WN[k])).sum())})
    out["bot_contro_ricerca"] = righe
    out["bot_contro_ricerca_sintesi"] = {
        "giorni": len(righe), "universo_uguale": sum(r["universo_uguale"] for r in righe),
        "diff_max_G1": max(r["diff_max_G1"] for r in righe), "diff_max_G1N": max(r["diff_max_G1N"] for r in righe),
        "diff_max_beta": max(r["diff_max_beta"] for r in righe if r["diff_max_beta"] is not None),
        "giorni_con_lati_cambiati": sum(1 for r in righe if r["lati_cambiati"] > 0)}
    print(out["bot_contro_ricerca_sintesi"], flush=True)
    (QUI / "parita_bot.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
