"""Fase 3: studio dei fallimenti di una variante, solo sui dati di costruzione.

Raggruppa i trade per caratteristiche note all'ingresso e scrive la tabella in
data/insample/BTCUSDT/fallimenti_<ID>.json. Uso: python fallimenti.py V19
"""
import json
import sys
from datetime import datetime, timezone

import numpy as np

import quadro
import varianti
from comune import CARTELLA, SIMBOLO, motore, parametri

GIORNO = 86_400_000


def gruppi(trades, chiave, n=4):
    x = np.array([chiave(t) for t in trades], dtype=float)
    r = np.array([t.r for t in trades])
    q = np.quantile(x, np.linspace(0, 1, n + 1))
    out = []
    for k in range(n):
        sel = (x >= q[k]) & ((x <= q[k + 1]) if k == n - 1 else (x < q[k + 1]))
        out.append({"da": round(float(q[k]), 6), "a": round(float(q[k + 1]), 6), "trade": int(sel.sum()),
                    "r_medio": round(float(r[sel].mean()), 4) if sel.any() else None})
    return out


vid = sys.argv[1]
v = varianti.TUTTE[vid]()
candele, mark, funding = quadro.costruzione(v.tf)
ris = motore.esegui(candele, None, mark, funding, v.fabbrica(candele)(), parametri())
trades = ris.trades
idx = {c.ts: i for i, c in enumerate(candele)}
ms = quadro.MS[v.tf]


def barra_segnale(t):
    return idx[t.ts_entrata - ms] if (t.ts_entrata - ms) in idx else idx[t.ts_entrata] - 1


def r_prima_mezzora(t):
    g = (t.ts_entrata // GIORNO) * GIORNO
    if t.ts_entrata % GIORNO == 0:
        g -= GIORNO
    c = candele[idx[g]]
    return c.close / c.open - 1


def r_giornata(t):
    i = barra_segnale(t)
    g = (candele[i].ts // GIORNO) * GIORNO
    return candele[i].close / candele[idx[g]].open - 1


def vol_20(t):
    i = barra_segnale(t)
    c = np.array([x.close for x in candele[max(0, i - 48 * 20):i + 1]])
    return float(np.std(np.diff(np.log(c))))


def distanza_stop(t):
    return abs(t.entrata - t.stop) / t.entrata


out = {"trade": len(trades), "r_medio": float(np.mean([t.r for t in trades]))}
out["per_distanza_stop"] = gruppi(trades, distanza_stop)
out["per_volatilita_20_giorni"] = gruppi(trades, vol_20)
if vid in ("V18", "V19"):
    out["per_ampiezza_prima_mezzora"] = gruppi(trades, lambda t: abs(r_prima_mezzora(t)))
    out["per_rendimento_della_giornata"] = gruppi(trades, r_giornata)
out["per_giorno_settimana"] = {}
for t in trades:
    d = datetime.fromtimestamp(t.ts_entrata / 1000, tz=timezone.utc).weekday()
    out["per_giorno_settimana"].setdefault(d, []).append(t.r)
out["per_giorno_settimana"] = {k: [len(x), round(float(np.mean(x)), 4)] for k, x in sorted(out["per_giorno_settimana"].items())}
out["lordo_r_medio"] = round(float(np.mean([t.pnl_lordo / t.rischio_iniziale for t in trades])), 4)
out["costi_r_medi"] = round(float(np.mean([(t.commissioni + t.slippage_costo + t.funding_pagato) / t.rischio_iniziale for t in trades])), 4)
(CARTELLA.parents[1] / "data" / "insample" / SIMBOLO / f"fallimenti_{vid}.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out))
