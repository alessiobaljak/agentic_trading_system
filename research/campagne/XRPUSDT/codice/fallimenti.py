"""Fase 3: studio dei fallimenti di una variante, solo sui dati di costruzione.

Uso: python -m research.campagne.XRPUSDT.codice.fallimenti XRPUSDT-V21
Scrive in data/insample/XRPUSDT/fallimenti_<id>.txt: R per esito, per grandezza del segnale, per ora UTC,
per durata, per anno, e R dei trade in base al movimento delle barre prima.
"""
import sys
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

from research.src import dati, motore
from research.campagne.XRPUSDT.codice import quadro as q
from research.campagne.XRPUSDT.codice.varianti import VARIANTI

vid = sys.argv[1]
v = VARIANTI[vid]
s = q.serie(v.tf)
prep = q.Preparata(v, s)
ris = motore.esegui(s["candele"], None, s["mark"], s["funding"], prep.crea_candidato()(), q.parametri())
tr = ris.trades
ts = s["ts"]
righe = [f"{vid}: {len(tr)} trade, R medio {np.mean([t.r for t in tr]):.3f}"]


def gruppo(nome, chiave):
    g = defaultdict(list)
    for t in tr:
        g[chiave(t)].append(t.r)
    righe.append(f"-- per {nome}")
    for k in sorted(g):
        righe.append(f"   {k}: n={len(g[k])} R medio={np.mean(g[k]):.3f}")


gruppo("esito", lambda t: t.esito)
gruppo("ora UTC d'ingresso", lambda t: datetime.fromtimestamp(t.ts_entrata / 1000, tz=timezone.utc).hour // 4 * 4)
gruppo("anno-trimestre", lambda t: (lambda d: f"{d.year}-T{(d.month - 1) // 3 + 1}")(datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc)))
# grandezza del segnale: per le varianti del premio, il premio alla barra del segnale
mark = np.array([c.close for c in s["mark"]])
prem = s["close"] / mark - 1
r1 = np.full(len(ts), np.nan)
r1[1:] = s["close"][1:] / s["close"][:-1] - 1


def barra_segnale(t):
    return int(np.searchsorted(ts, t.ts_entrata)) - 1


gruppo("premio last/mark al segnale (decimi di punto %)", lambda t: round(prem[barra_segnale(t)] * 1000) / 10)
gruppo("rendimento della barra del segnale (punti %)", lambda t: int(np.floor(r1[barra_segnale(t)] * 100)))
# percorso medio in R dopo l'ingresso, barra per barra (chiusure), per vedere quando si guadagna
percorso = defaultdict(list)
for t in tr:
    j = int(np.searchsorted(ts, t.ts_entrata))
    rischio = abs(t.entrata - t.stop)
    for k in range(0, 8):
        if j + k < len(ts):
            percorso[k].append(motore.segno(t.direzione) * (s["close"][j + k] - t.entrata) / rischio)
righe.append("-- movimento medio in R alla chiusura delle barre dopo l'ingresso (senza stop)")
righe.append("   " + " ".join(f"b{k}={np.mean(x):.3f}" for k, x in sorted(percorso.items())))
testo = "\n".join(righe)
(dati.RADICE_DEFAULT / "data" / "insample" / "XRPUSDT" / f"fallimenti_{vid}.txt").write_text(testo + "\n")
print(testo)
