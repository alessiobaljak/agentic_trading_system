"""Revisione di G1N (29 ottobre 2026): lo Sharpe corretto di G1N e di G1 con il mazzo delle prove di oggi (la funzione della
ricerca, `asticella.corretto_rivisto`, con le serie salvate dalle prove 57 e 88).

Uso: python3 -m research.programma7.revisione_g1n.corretto_oggi
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from research.programma6 import asticella as ast
from research.programma6 import sesta as se
from research.programma6 import terza as te

QUI = Path(__file__).parent
P7 = QUI.parent


def main():
    btc = pd.Series(dtype=float)
    cand = {}
    for nome, f in (("88 G1N", "risultati_ventiseiesima/settimane_G1N.csv.gz"), ("57 G1", "risultati_prima/settimane_G1.csv.gz")):
        d = pd.read_csv(P7 / f, index_col=0)
        e = te.esame(d, btc, inizio=se.INIZIO, anni_pieni=se.ANNI_PIENI)
        cand[nome] = e["intero"]
    nuove = ast.serie_nuove()          # tutte le serie a portafoglio dalla 49 in poi (G1 e G1N comprese)
    r = ast.corretto_rivisto(nuove, cand)
    out = {"serie_nuove": len(nuove), "gruppi": r["gruppi"], "deviazione": r["deviazione"],
           "candidate": {n: {k: (v if not isinstance(v, list) else len(v)) for k, v in x.items()} for n, x in r["candidate"].items()},
           "sharpe": {n: cand[n]["sharpe"] for n in cand}}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    (QUI / "corretto_oggi.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
