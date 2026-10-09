"""Fase 3: studio dei fallimenti, solo sui dati di costruzione. Stampa tabelle, non decide nulla.

Uso: python fase3.py <analisi>
  orario     -> V-11/V-12: R lordo e netto, distanza dello stop e costo in R all'ora 23:30 contro
                le altre mezz'ore (ingressi a ogni mezz'ora con la stessa uscita); R per quartile
                del rendimento del giorno.
  quartili K -> per la variante K: R medio per quartile di alcune caratteristiche dell'ingresso.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from varianti import VARIANTI  # noqa: E402


def r_lordo(t):
    return t.pnl_lordo / t.rischio_iniziale


def tabella(nome, gruppi):
    print(nome)
    for etichetta, trades in gruppi:
        if not trades:
            continue
        r = np.array([t.r for t in trades])
        rl = np.array([r_lordo(t) for t in trades])
        dist = np.array([abs(t.entrata - t.stop) / t.entrata * 100 for t in trades])
        print(f"   {etichetta:28s} n {len(trades):5d}  R {r.mean():+.4f}  R lordo {rl.mean():+.4f}  "
              f"costo R {(rl - r).mean():.4f}  stop % {np.median(dist):.2f}")


def orario():
    ctx = comune.contesto("30m", "costruzione")
    for chiave in ("V-11", "V-12"):
        var = VARIANTI[chiave]
        ris = comune.esegui(var, ctx)
        trades = ris.trades
        ind, _ = comune._indicatori(var, ctx)
        rg = np.array([abs(ind["ret_giorno"][ctx.indice_ts[t.ts_entrata] - 1]) for t in trades])
        q = np.quantile(rg, [0.25, 0.5, 0.75])
        gruppi = [(f"|giorno| q{k+1}", [t for t, x in zip(trades, rg) if (k == 0 or x > q[k-1]) and (k == 3 or x <= q[k])])
                  for k in range(4)]
        tabella(f"{chiave}: per quartile di |rendimento del giorno| (soglie {np.round(q*100, 2)}%)", gruppi)
        anni = {}
        for t in trades:
            anni.setdefault(comune._anno(t.ts_uscita), []).append(t)
        tabella(f"{chiave}: per anno", [(str(k), v) for k, v in sorted(anni.items())])
        # la baseline (a) della stessa variante: ingressi a ogni barra libera, per ora d'ingresso
        ris_a = comune.esegui(var, ctx, quale="a")
        per_ora = {}
        for t in ris_a.trades:
            minuto = (t.ts_entrata % 86_400_000) // 60_000
            per_ora.setdefault(minuto, []).append(t)
        tabella(f"{chiave}: baseline (a) per mezz'ora d'ingresso (minuti dalla mezzanotte UTC)",
                [(str(m), per_ora[m]) for m in sorted(per_ora)])


def quartili(chiave):
    var = VARIANTI[chiave]
    ctx = comune.contesto(var.tf, "costruzione")
    ris = comune.esegui(var, ctx)
    trades = ris.trades
    a = comune.atr(ctx, 14) / ctx.c
    ret1 = np.r_[np.nan, ctx.c[1:] / ctx.c[:-1] - 1]
    vol_rel = ctx.v / comune.sma(ctx.v, 30)
    caratteristiche = {"ATR/prezzo": a, "rendimento barra di segnale": ret1, "volume relativo (30 barre)": vol_rel}
    for nome, arr in caratteristiche.items():
        x = np.array([arr[ctx.indice_ts[t.ts_entrata] - 1] for t in trades])
        ok = np.isfinite(x)
        q = np.quantile(x[ok], [0.25, 0.5, 0.75])
        gruppi = []
        for k in range(4):
            sel = [t for t, v in zip(trades, x) if np.isfinite(v) and (k == 0 or v > q[k-1]) and (k == 3 or v <= q[k])]
            gruppi.append((f"q{k+1}", sel))
        tabella(f"{chiave}: per quartile di {nome} (soglie {np.round(q, 4)})", gruppi)
    tabella(f"{chiave}: per esito", [(e, [t for t in trades if t.esito == e]) for e in ("stop", "segnale", "target", "fine_dati")])


if __name__ == "__main__":
    if sys.argv[1] == "orario":
        orario()
    else:
        quartili(sys.argv[2])
