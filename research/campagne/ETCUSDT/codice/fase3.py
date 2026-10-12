"""Fase 3: studio dei fallimenti di una variante testata, solo sui dati di costruzione.

Uso: python fase3.py <NOME>. Scrive in uscite/ultima.txt l'R dei trade per gruppi: anno, uscita,
e per quantili delle grandezze note alla barra del segnale (indicatori della variante e rendimento
della barra). Nessuna nuova variante nasce qui: un filtro che ne esce e' un ritocco (regola 6).
"""
import sys
from datetime import datetime, timezone

import numpy as np

import comune as C
import varianti as V

nome = sys.argv[1]
var, meta = V.CATALOGO[nome]() if nome in V.CATALOGO else V.RITOCCHI[nome]()[:2]
serie, ind, ris = C.trade_di(var)
idx = {c.ts: i for i, c in enumerate(serie.candele)}
trades = [t for t in ris.trades]
C.stampa("== Fase 3", nome, "trade", len(trades), "R medio", round(float(np.mean([t.r for t in trades])), 4))


def gruppi(etichetta, chiave):
    g = {}
    for t in trades:
        k = chiave(t)
        if k is None:
            continue
        g.setdefault(k, []).append(t.r)
    for k in sorted(g):
        v = g[k]
        C.stampa(f"  {etichetta} {k}: n={len(v)} R medio={np.mean(v):.4f} R mediano={np.median(v):.4f} vinti={np.mean([x > 0 for x in v]):.2f}")


gruppi("anno", lambda t: datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year)
gruppi("esito", lambda t: t.esito)
gruppi("costi in R (commissioni+slippage)", lambda t: round((t.commissioni + t.slippage_costo) / t.rischio_iniziale, 2))
gruppi("R lordo>0", lambda t: t.pnl_lordo > 0)


def per_quantili(nome_grandezza, valori_per_trade, q=4):
    v = np.array([x for x in valori_per_trade if x is not None])
    if len(v) < q:
        return
    soglie = np.quantile(v, np.linspace(0, 1, q + 1)[1:-1])
    gruppi(f"{nome_grandezza} quartile", lambda t: None if val[id(t)] is None else int(np.searchsorted(soglie, val[id(t)])))
    C.stampa(f"  soglie dei quartili di {nome_grandezza}: {[round(float(s), 5) for s in soglie]}")


for chiave in [k for k in ind if isinstance(ind[k], list) and k not in ("c",) and len(ind[k]) == serie.n]:
    val = {}
    for t in trades:
        i = idx[t.ts_entrata] - 1  # barra del segnale
        x = ind[chiave][i]
        val[id(t)] = float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else None
    if all(v is None for v in val.values()):
        continue
    per_quantili(chiave, list(val.values()))

# rendimento della barra del segnale e distanza dello stop in percentuale
val = {}
for t in trades:
    i = idx[t.ts_entrata] - 1
    val[id(t)] = serie.candele[i].close / serie.candele[i].open - 1
per_quantili("rendimento barra segnale", list(val.values()))
val = {id(t): abs(t.entrata - t.stop) / t.entrata for t in trades}
per_quantili("distanza stop %", list(val.values()))
