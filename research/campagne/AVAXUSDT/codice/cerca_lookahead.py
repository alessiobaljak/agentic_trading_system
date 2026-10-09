"""Ricerca di un errore di lookahead in V-14 (Fase 4, test del ritardo), solo costruzione.

1. Ricalcolo indipendente del segnale: per ogni trade, z della barra di segnale dai CSV caricati,
   con una funzione scritta qui da capo (rendimento della barra / deviazione standard dei 180
   rendimenti precedenti), e controllo che la barra di segnale sia quella subito prima dell'ingresso.
2. Profilo nel tempo: rendimento medio del close-to-close di ciascuna delle 8 barre dopo la barra di
   segnale, sui segnali della variante (tutti, non solo quelli eseguiti) e su tutte le barre.
   Se l'effetto e' vero e breve, il grosso sta nelle prime barre e il ritardo lo perde.
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune  # noqa: E402
from varianti import VARIANTI  # noqa: E402

var = VARIANTI["V-14"]
ctx = comune.contesto("4h", "costruzione")
c = ctx.c
ris = comune.esegui(var, ctx)
errori = 0
for t in ris.trades:
    e = ctx.indice_ts[t.ts_entrata]
    s = e - 1
    if ctx.ts[e] - ctx.ts[s] != 4 * 3_600_000:
        print("barra di segnale non contigua all'ingresso", e)
    rets = [c[k] / c[k - 1] - 1 for k in range(s - 180, s)]
    z = (c[s] / c[s - 1] - 1) / np.std(rets)
    if not z > 2:
        errori += 1
        print("segnale non riprodotto", s, z)
    if abs(t.entrata - ctx.o[e] * (1 + comune.PARAMETRI.slippage_per_lato)) > 1e-9 * t.entrata:
        print("entrata diversa dall'apertura della barra dopo il segnale", e)
print("trade", len(ris.trades), "segnali non riprodotti", errori)

ind, risc = comune._indicatori(var, ctx)
segnali = [i for i in range(risc, ctx.n - 9) if ind["z"][i] > 2 and not ctx.illiquido[i]]
r = np.r_[np.nan, c[1:] / c[:-1] - 1]
print("segnali (tutti)", len(segnali))
for k in range(1, 9):
    dopo = np.array([r[i + k] for i in segnali])
    tutte = r[risc + k: ctx.n]
    print(f"barra +{k}: rendimento medio dopo il segnale {np.nanmean(dopo)*100:+.3f}%  "
          f"(mediana {np.nanmedian(dopo)*100:+.3f}%)  tutte le barre {np.nanmean(tutte)*100:+.3f}%")
