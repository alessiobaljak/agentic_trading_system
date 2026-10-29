"""Revisione di G1N (29 ottobre 2026): il controllo «inclinazione fissa» senza il senno di poi. Al posto di a e b del giorno (dal
beta dei 90 giorni) si usa la media di a dei giorni PRIMA (da 1 il primo giorno), b = 2 - a: un lato long un po' piu' pesante,
quasi costante, scelto solo con il passato. Se fa come G1N, la stima del beta di ogni giorno non aggiunge niente.

Uso: python3 -m research.programma7.revisione_g1n.inclinazione_causale
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import analisi as an
from research.programma7.revisione_g1n import nucleo as nu

QUI = Path(__file__).parent


def main():
    pan = sc.pannello()
    simboli = pan["simboli"]
    giorni = np.arange(an.INIZIO, an.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = np.array([nu.costo_di(s) for s in simboli])
    U = nu.universo_giorni(pan, idx)
    W, WN, scl = nu.pesi(pan, idx, U)
    a = scl["a"]
    a_prima = np.concatenate([[1.0], np.cumsum(a)[:-1] / np.arange(1, len(a))])
    WC = np.where(W > 0, W * a_prima[:, None], W * (2 - a_prima)[:, None])
    ore = an.candele_ore([simboli[j] for j in np.flatnonzero(np.abs(W).sum(axis=0) > 0)])
    out = {}
    conti = {n: an.conto(n, Wx, R, F, costo, giorni, simboli, ore) for n, Wx in (("G1", W), ("G1N", WN), ("inclinazione causale", WC))}
    for n, d in conti.items():
        out[n] = an.sintesi(d)
    wk = {n: an.settimane(d)["netto"] for n, d in conti.items()}
    out["bootstrap_G1N_meno_causale"] = an.bootstrap_coppia(wk["inclinazione causale"].to_numpy(), wk["G1N"].to_numpy())
    out["bootstrap_causale_meno_G1"] = an.bootstrap_coppia(wk["G1"].to_numpy(), wk["inclinazione causale"].to_numpy())
    peggiori = wk["G1"].nsmallest(15).index
    out["quindici_peggiori_di_G1"] = {n: float(wk[n].loc[peggiori].mean()) for n in wk}
    out["a_prima_fine"] = float(a_prima[-1])
    # dal 2025: il periodo piu' recente
    for n in wk:
        w = wk[n]
        out[n]["dal_2025"] = nu.numeri(w[w.index >= sc.giorno(2024, 12, 30)].to_numpy())
    print(json.dumps({n: {k: out[n][k] for k in ("sharpe", "annuo", "discesa", "per_anno", "dal_2025")} for n in conti}, indent=1))
    print(json.dumps({k: out[k] for k in ("bootstrap_G1N_meno_causale", "bootstrap_causale_meno_G1", "quindici_peggiori_di_G1")}, indent=1))
    (QUI / "inclinazione_causale.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
