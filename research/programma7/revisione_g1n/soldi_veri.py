"""Revisione di G1N (29 ottobre 2026): cose che con i soldi veri contano e che il paper non vede.

* la dimensione degli ordini di ogni giorno (Binance non accetta ordini sotto un valore minimo, di solito 5 USDT; il passo di
  quantita' arrotonda il resto): quanti ordini di G1N sarebbero sotto 5 USDT con 1.000, 5.000, 10.000, 100.000 USDT;
* quanto del giro di ogni giorno viene solo dalla scalatura (a e b che cambiano) e quanto dalla banda;
* i rialzi dentro la giornata delle monete vendute (il massimo del giorno sopra l'apertura) e la perdita peggiore possibile del
  conto dentro un giorno (tutti i massimi per gli short e tutti i minimi per i long nello stesso momento: un limite alto).

Uso: python3 -m research.programma7.revisione_g1n.soldi_veri
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as nu

QUI = Path(__file__).parent
INIZIO, FINE = sc.giorno(2021, 1, 4), sc.giorno(2026, 10, 5)


def main():
    pan = sc.pannello()
    simboli = pan["simboli"]
    giorni = np.arange(INIZIO, FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]
    F = np.nan_to_num(pan["funding"][idx])
    costo = np.array([nu.costo_di(s) for s in simboli])
    U = nu.universo_giorni(pan, idx)
    W, WN, scl = nu.pesi(pan, idx, U)
    out = {}
    _, _, _, D = nu.variazioni(WN, R, F, costo)
    _, _, _, D1 = nu.variazioni(W, R, F, costo)
    v = np.abs(D[np.abs(D) > 1e-9])
    out["ordini"] = {"variazioni_totali": int(len(v)), "al_giorno": float(len(v) / len(giorni)),
                     "mediana_in_frazione_del_capitale": float(np.median(v)), "quantile_25": float(np.percentile(v, 25))}
    for cap in (1e3, 5e3, 1e4, 1e5):
        sotto = v * cap < 5.0
        out["ordini"][f"capitale_{int(cap)}"] = {"quota_ordini_sotto_5_usdt": float(sotto.mean()),
                                                  "quota_del_giro_sotto_5_usdt": float(v[sotto].sum() / v.sum())}
    # giro di G1N contro G1: quanto in piu' fa la scalatura giornaliera
    out["giro_annuo"] = {"G1": float(np.abs(D1).sum() / len(giorni) * 365), "G1N": float(np.abs(D).sum() / len(giorni) * 365)}
    # rialzi dentro il giorno delle monete vendute
    H, L, O = pan["high"][idx], pan["low"][idx], pan["open"][idx]
    with np.errstate(all="ignore"):
        su = H / O - 1
        giu = L / O - 1
    corti = WN < 0
    s = su[corti]
    s = s[np.isfinite(s)]
    out["short_rialzo_nel_giorno"] = {"posizioni_giorno": int(len(s)), "sopra_20pc": int((s > 0.2).sum()),
                                      "sopra_30pc": int((s > 0.3).sum()), "sopra_50pc": int((s > 0.5).sum()),
                                      "massimo": float(s.max())}
    peggio = (np.where(corti, WN * np.nan_to_num(su), 0) + np.where(WN > 0, WN * np.nan_to_num(giu), 0)).sum(axis=1)
    k = int(np.argmin(peggio))
    out["perdita_peggiore_possibile_nel_giorno"] = {"valore": float(peggio[k]), "giorno": sc.data(int(giorni[k])),
                                                   "quantile_1pc": float(np.percentile(peggio, 1))}
    # due casi di mercato intero, piu' realistici: tutte le monete al minimo insieme (crollo) o al massimo insieme (rialzo)
    crollo = (WN * np.nan_to_num(giu)).sum(axis=1)
    rialzo = (WN * np.nan_to_num(su)).sum(axis=1)
    caso = np.minimum(crollo, rialzo)
    k = int(np.argmin(caso))
    out["mercato_intero_al_minimo_o_al_massimo"] = {"peggiore": float(caso[k]), "giorno": sc.data(int(giorni[k])),
                                                   "quantile_1pc": float(np.percentile(caso, 1)),
                                                   "peggiore_crollo": float(crollo.min()), "peggiore_rialzo": float(rialzo.min())}
    # quanto pesa la moneta short piu' grande
    out["short_peso_massimo"] = float((-WN).max())
    print(json.dumps(out, indent=1, ensure_ascii=False))
    (QUI / "soldi_veri.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
