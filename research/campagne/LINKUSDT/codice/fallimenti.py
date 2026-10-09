"""Fase 3: studio dei fallimenti di una variante gia' testata (solo costruzione).

Riesegue la variante registrata e raggruppa gli R dei suoi trade per caratteristiche note alla barra
del segnale: rendimento della barra, volatilita' (ATR relativo), giorno della settimana, anno,
rendimento di BTCUSDT nella stessa barra.
Uso: python fallimenti.py V24
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune as C  # noqa: E402
import indicatori as I  # noqa: E402
import varianti as VV  # noqa: E402
from research.src import motore  # noqa: E402

vid = sys.argv[1]
spec = VV.VARIANTI[vid]
ctx = C.contesto(spec["tf"], "costruzione", VV.extra_per)
c = ctx.candele
prep = spec["prepara"](c, ctx.extra)
ris = motore.esegui(c, None, ctx.mark, ctx.funding, C.fabbrica(prep, c, ctx.liq, "variante")(), C.PARAMETRI)
idx = {x.ts: i for i, x in enumerate(c)}
close = I.arr(c, "close")
r1 = I.rendimenti(close, 1)
atrp = I.atr(c, 14) / close
btc = {x.ts: x.close / x.open - 1 for x in C.candele_last(spec["tf"], "BTCUSDT")}
righe = []
for t in ris.trades:
    i = idx[t.ts_entrata] - 1  # barra del segnale
    righe.append((t.r, r1[i], atrp[i], I.utc(c[i].ts).weekday(), I.utc(t.ts_uscita).year, btc.get(c[i].ts, np.nan),
                  btc.get(c[i + 1].ts, np.nan), t.esito))
R = np.array([x[0] for x in righe])
print(vid, "trade", len(R), "R medio", round(R.mean(), 4))


def gruppi(nome, chiave, tagli):
    v = np.array([chiave(x) for x in righe], dtype=float)
    q = np.nanquantile(v, tagli)
    lim = [-np.inf] + list(q) + [np.inf]
    print(nome)
    for a, b in zip(lim[:-1], lim[1:]):
        m = (v > a) & (v <= b)
        if m.sum():
            print(f"   ({a:+.4f}, {b:+.4f}]  n={m.sum():4d}  R medio {R[m].mean():+.3f}")


gruppi("rendimento della barra del segnale", lambda x: x[1], [0.25, 0.5, 0.75])
gruppi("ATR relativo alla barra del segnale", lambda x: x[2], [0.25, 0.5, 0.75])
gruppi("rendimento BTC nella barra del segnale", lambda x: x[5], [0.25, 0.5, 0.75])
gruppi("rendimento BTC nella barra del trade (contemporaneo, solo per 'e' solo il mercato')", lambda x: x[6], [0.25, 0.5, 0.75])
print("giorno della settimana del segnale")
for g in range(7):
    m = np.array([x[3] == g for x in righe])
    if m.sum():
        print(f"   {g} n={m.sum():3d} R medio {R[m].mean():+.3f}")
print("esiti", {e: int(sum(1 for x in righe if x[7] == e)) for e in ("stop", "segnale", "target", "fine_dati")})
print("stop: R medio", round(float(np.mean([x[0] for x in righe if x[7] == 'stop'] or [0])), 3))
