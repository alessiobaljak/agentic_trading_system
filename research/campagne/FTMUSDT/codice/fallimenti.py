"""Fase 3: studia i trade di una variante GIA' testata, solo sui dati di costruzione. Uso: python fallimenti.py ID
Stampa i trade raggruppati per esito, per anno, per semestre e per rendimento di BTC nello stesso intervallo."""
import sys
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

from comune import PARAMETRI, motore
import quadro
from registro import VARIANTI

id_ = sys.argv[1]
var = VARIANTI[id_][1]()
s = quadro.carica(var.tf, "costruzione")
ctx, crea, _, _, _ = quadro._fabbriche(var, s)
ris = motore.esegui(s.candele, None, s.mark, s.funding, crea(), PARAMETRI)
tr = ris.trades
r = np.array([t.r for t in tr])
print(id_, var.tf, var.direzione, "trade", len(tr), "R medio", round(r.mean(), 3))
per = defaultdict(list)
for t in tr:
    per["esito " + t.esito].append(t.r)
    d = datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc)
    per[f"semestre {d.year}-{1 if d.month <= 6 else 2}"].append(t.r)
btc = quadro.mercato_btc(tr, var.tf)
print("btc", btc)
for k in sorted(per):
    v = per[k]
    print(f"  {k}: n={len(v)} R medio={np.mean(v):.3f} quota vincenti={np.mean(np.array(v) > 0):.2f}")
# R lordo (senza costi) per vedere quanto pesano i costi
lordo = np.array([t.pnl_lordo / t.rischio_iniziale for t in tr])
print("R lordo medio", round(lordo.mean(), 3), "costi medi in R", round((lordo - r).mean(), 3),
      "funding medio in R", round(np.mean([t.funding_pagato / t.rischio_iniziale for t in tr]), 4))
if len(sys.argv) > 2 and sys.argv[2] == "regime":
    # regime alla barra di segnale: close sopra o sotto la media di 50 barre
    m50 = __import__("indicatori").media_mobile(s.c, 50)
    pos_ts = {int(t): k for k, t in enumerate(s.ts)}
    gruppi = defaultdict(list)
    for t in tr:
        k = pos_ts[t.ts_entrata] - 1
        gruppi["sopra media 50" if s.c[k] > m50[k] else "sotto media 50"].append(t.r)
    for g, v in sorted(gruppi.items()):
        print(f"  {g}: n={len(v)} R medio={np.mean(v):.3f}")
dist = np.array([abs(t.entrata - t.stop) / t.entrata for t in tr])
print("distanza dello stop: mediana", round(float(np.median(dist)), 4), "quota oltre 6%", round(float(np.mean(dist > 0.06)), 2))
