"""Fase 3: studio dei fallimenti di una variante, solo sui trade di costruzione salvati dal test.

Uso: python fallimenti.py <ID>
Stampa l'R medio per quintili della distanza dello stop, per ora d'ingresso (UTC), per anno, per
esito e per durata. Non rilancia il motore: legge data/insample/LTCUSDT/trade/<ID>.pkl.
"""
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import quadro  # noqa: E402


def gruppi(nome, chiavi, r):
    print(f"-- {nome}")
    for k in sorted(set(chiavi)):
        sel = [x for c, x in zip(chiavi, r) if c == k]
        print(f"   {k}: n={len(sel)} R medio={np.mean(sel):+.3f}")


if __name__ == "__main__":
    ident = sys.argv[1]
    with open(quadro.CARTELLA_DATI / "trade" / f"{ident}.pkl", "rb") as f:
        dati = pickle.load(f)
    tr = dati["trades"]
    r = np.array([t.r for t in tr])
    dist = np.array([abs(t.entrata - t.stop) / t.entrata for t in tr])
    costo = np.array([(t.commissioni + t.slippage_costo) / t.rischio_iniziale for t in tr])
    lordo = np.array([t.pnl_lordo / t.rischio_iniziale for t in tr])
    print(ident, "trade", len(tr), "R medio", round(r.mean(), 4), "R lordo medio", round(lordo.mean(), 4))
    q = np.quantile(dist, [0.2, 0.4, 0.6, 0.8])
    quint = [int(np.searchsorted(q, d)) for d in dist]
    print("soglie dei quintili di distanza dello stop:", np.round(q, 4))
    for k in range(5):
        sel = np.array([x == k for x in quint])
        print(f"   quintile {k}: n={sel.sum()} dist media={dist[sel].mean():.4f} R={r[sel].mean():+.3f} "
              f"lordo={lordo[sel].mean():+.3f} costo={costo[sel].mean():.3f}")
    ore = [datetime.fromtimestamp(t.ts_entrata / 1000, tz=timezone.utc).hour for t in tr]
    gruppi("ora d'ingresso", ore, r)
    gruppi("anno d'uscita", [datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year for t in tr], r)
    gruppi("esito", [t.esito for t in tr], r)
    durata = [int((t.ts_uscita - t.ts_entrata) // quadro.ms_barra(dati["tf"])) for t in tr]
    gruppi("durata in barre (a gruppi di 4)", [d // 4 * 4 for d in durata], r)
