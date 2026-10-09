"""Fase 3: studio dei fallimenti di una variante sui dati di costruzione.

Uso: python fallimenti.py NOME
Unisce i trade del test (esiti/<NOME>_test.json) con alcune caratteristiche della barra del
segnale e stampa l'R medio per gruppi (terzili). Solo costruzione.
"""
from __future__ import annotations

import json
import sys

import numpy as np

import comune
import quadro as q
import varianti


def caratteristiche(nome, s):
    _, ap, esc = varianti._giorno_apertura_escursione(s)
    a14 = q.atr(s, 14)
    return {
        "rend_giorno": s.c / ap - 1,
        "rend_giorno_in_atr": (s.c - ap) / a14,
        "atr_pct": a14 / s.c,
        "rend_btc_giorno": (s.btc_c / np.roll(s.btc_c, 5) - 1) if s.tf == "4h" else None,
        "rend_btc_4barre": q.rendimento(s.btc_c, 4),
        "rend_24h": q.rendimento(s.c, 6 if s.tf == "4h" else 24),
        "rend_7g": q.rendimento(s.c, 42 if s.tf == "4h" else 168),
        "vol_rel": s.v_usdt / q.sma(np.nan_to_num(s.v_usdt), 42 if s.tf == "4h" else 168),
    }


if __name__ == "__main__":
    nome = sys.argv[1]
    v = varianti.TUTTE[nome]()
    s = q.carica(v.tf, "costruzione")
    e = json.loads((comune.CARTELLA_DATI / "esiti" / f"{nome}_test.json").read_text())
    passo = q.MS[v.tf]
    righe = []
    for ts_in, ts_out, r, esito in e["trade_dettaglio"]:
        i_segnale = s.indice_ts.get(ts_in - passo)
        if i_segnale is None:
            continue
        righe.append((i_segnale, r))
    car = caratteristiche(nome, s)
    r = np.array([x[1] for x in righe])
    idx = np.array([x[0] for x in righe])
    print(nome, "trade", len(r), "R medio", round(r.mean(), 4))
    for k, arr in car.items():
        if arr is None:
            continue
        x = arr[idx]
        ok = np.isfinite(x)
        if ok.sum() < 9:
            continue
        t1, t2 = np.nanpercentile(x[ok], [33.3, 66.7])
        gruppi = [(x <= t1) & ok, (x > t1) & (x <= t2) & ok, (x > t2) & ok]
        testo = "  ".join(f"[{'basso' if j == 0 else 'medio' if j == 1 else 'alto'} n={g.sum()} R={r[g].mean():+.3f}]"
                          for j, g in enumerate(gruppi))
        print(f" {k:22s} soglie {t1:.4g} {t2:.4g}  {testo}")
    anni = {}
    for (i, rr) in righe:
        anni.setdefault(int(s.ts[i] // (365.25 * 86_400_000)) + 1970, []).append(rr)
    print(" per anno", {a: (len(x), round(float(np.mean(x)), 3)) for a, x in sorted(anni.items())})
