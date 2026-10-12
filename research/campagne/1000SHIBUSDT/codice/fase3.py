"""Fase 3: studio dei fallimenti di una variante sui dati di costruzione.

Uso: python fase3.py <nome> <indicatore> [quantili]
Raggruppa i trade del test (risultati/<nome>_trade.json) per il valore dell'indicatore
della variante alla barra di segnale (la barra prima dell'ingresso) e stampa per gruppo:
numero di trade, R medio, quota di vincenti. Solo costruzione.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402
import varianti  # noqa: E402

nome, chiave = sys.argv[1], sys.argv[2]
nq = int(sys.argv[3]) if len(sys.argv) > 3 else 3
v = varianti.VARIANTI[nome]
serie = q.carica(v.tf, con_btc=v.con_btc)
n = q.candele_costruzione(serie)
candele = serie.candele[:n]
ind = v.prepara(candele, serie)
indice = {c.ts: k for k, c in enumerate(candele)}
trades = json.loads((q.CARTELLA_DATI / "risultati" / f"{nome}_trade.json").read_text())
valori, r = [], []
for ts_e, ts_u, rr, esito in trades:
    k = indice[ts_e] - 1  # barra di segnale
    valori.append(ind[chiave][k])
    r.append(rr)
valori, r = np.array(valori), np.array(r)
confini = np.quantile(valori, np.linspace(0, 1, nq + 1))
for j in range(nq):
    sel = (valori >= confini[j]) & (valori <= confini[j + 1]) if j == nq - 1 else (valori >= confini[j]) & (valori < confini[j + 1])
    print(json.dumps({"gruppo": j + 1, "da": round(float(confini[j]), 6), "a": round(float(confini[j + 1]), 6),
                      "trade": int(sel.sum()), "r_medio": round(float(r[sel].mean()), 4),
                      "vincenti": round(float((r[sel] > 0).mean()), 3)}))
