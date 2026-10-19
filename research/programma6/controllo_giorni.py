"""Programma 6, seconda prova: il controllo dei dati giornalieri prima dei calcoli (SECONDA.md, sezione 3).

1. Le candele giornaliere dell'archivio contro quelle fatte dalle ore della prima prova (a loro volta dai minuti
   verificati del programma 5; le 100 monete della prima prova; solo i giorni con tutte le 24 ore): differenza relativa di apertura, massimo, minimo, chiusura e volume.
2. I buchi: giorni senza candela fra la prima e l'ultima di ogni moneta.
3. Il funding: giorni con la candela e senza il dato (riempiti con la media dei 90 giorni prima).

Scrive ``risultati_seconda/controllo_dati.json``. Uso: python3 -m research.programma6.controllo_giorni
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from research.programma6 import dati
from research.programma6 import seconda as sc


def confronto(simbolo: str) -> dict:
    g = sc.candele(simbolo)
    m = dati.barre(simbolo, "1h")          # le ore fatte dai minuti verificati (almeno l'80% dei minuti)
    if g.empty or m.empty:
        return {}
    m = m.dropna(subset=["close"]).assign(giorno=m["minuto"] // 1440)
    d = m.groupby("giorno").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                                close=("close", "last"), quote_volume=("quote_volume", "sum"), n=("close", "size"))
    d = d[d["n"] == 24]
    comuni = g.index.intersection(d.index)
    out = {"giorni": int(len(comuni))}
    for k in ("open", "high", "low", "close", "quote_volume"):
        rel = (g.loc[comuni, k] / d.loc[comuni, k] - 1).abs()
        out[k] = {"max": float(rel.max()), "oltre_0,1%": int((rel > 0.001).sum())}
    return out


def main() -> int:
    pan = sc.pannello()
    C = pan["close"]
    ok = np.isfinite(C)
    buchi = {}
    for j, s in enumerate(pan["simboli"]):
        idx = np.flatnonzero(ok[:, j])
        if len(idx):
            n = int((idx[-1] - idx[0] + 1) - len(idx))
            if n:
                buchi[s] = n
    conf = {}
    for s in dati.CENTO:
        if s in pan["simboli"]:
            conf[s] = confronto(s)
    peggiori = sorted(((v["close"]["max"], s) for s, v in conf.items() if v), reverse=True)[:10]
    rep = {"simboli": len(pan["simboli"]), "giorni": int(C.shape[0]), "primo": sc.data(pan["t0"]),
           "ultimo": sc.data(pan["t0"] + C.shape[0] - 1), "buchi": buchi,
           "confronto_con_1_minuto": conf, "peggiori_chiusure": peggiori}
    sc.RIS.mkdir(exist_ok=True)
    (sc.RIS / "controllo_dati.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    print("simboli", rep["simboli"], "giorni", rep["giorni"], rep["primo"], "→", rep["ultimo"])
    print("monete con buchi:", len(buchi), "giorni mancanti in tutto:", sum(buchi.values()))
    tot = {k: sum(v[k]["oltre_0,1%"] for v in conf.values() if v) for k in ("open", "high", "low", "close", "quote_volume")}
    print("confronto con 1 minuto su", len(conf), "monete,", sum(v.get("giorni", 0) for v in conf.values()),
          "giorni; giorni oltre lo 0,1%:", tot)
    print("chiusure peggiori:", peggiori[:5])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
