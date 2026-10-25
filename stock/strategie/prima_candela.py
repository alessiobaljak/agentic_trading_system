"""La direzione della prima candela dopo l'apertura (`stock/prove/P017_prima_candela.md`)."""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from stock.simulatore.motore import Ordine, Stato

NY = "America/New_York"
QUOTA = 0.98
MINUTI_SEDUTA = 390


def prepara(barre: pd.DataFrame, cal: pd.DataFrame, giorni_esclusi: set, minuti: int) -> dict:
    """Per ogni barra di decisione (l'ultima della candela): direzione e stop; la barra dell'ingresso; la decisione d'uscita."""
    t = barre.index.tz_convert(NY)
    giorni = np.array(t.date)
    n = len(barre)
    ap, al, ba, ch = (barre[c].to_numpy(float) for c in ("open", "high", "low", "close"))
    direzione = np.zeros(n)
    stop = np.full(n, np.nan)
    giorno_di = np.full(n, -1)
    uscita = np.zeros(n, dtype=bool)
    tagli = np.r_[0, np.where(giorni[1:] != giorni[:-1])[0] + 1, n]
    for j, (a, b) in enumerate(zip(tagli[:-1], tagli[1:])):
        d = giorni[a]
        apertura, chiusura = cal.loc[d, "apertura"], cal.loc[d, "chiusura"]
        if d in giorni_esclusi or (chiusura - apertura) != pd.Timedelta(minutes=MINUTI_SEDUTA):
            continue
        k = ((t[a:b] - apertura).total_seconds() // 60).astype(int).to_numpy()
        pos = dict(zip(k, range(a, b)))
        if not all(x in pos for x in range(minuti + 1)) or (MINUTI_SEDUTA - 2) not in pos or (MINUTI_SEDUTA - 1) not in pos:
            continue
        idx = [pos[x] for x in range(minuti)]
        o, c = ap[idx[0]], ch[idx[-1]]
        alto, basso = al[idx].max(), ba[idx].min()
        segno = float(np.sign(c - o))
        if segno == 0:
            continue
        i = idx[-1]
        direzione[i] = segno
        stop[i] = basso if segno > 0 else alto
        giorno_di[a:b] = j
        uscita[pos[MINUTI_SEDUTA - 2]] = True
    return {"direzione": direzione, "stop": stop, "giorno": giorno_di, "uscita": uscita}


def strategia(seg: dict, multiplo: float | None = 10.0):
    """`multiplo`: l'obiettivo in volte il rischio (None = nessun obiettivo, solo stop o chiusura)."""
    direzione, stop, giorno_di, uscita = seg["direzione"], seg["stop"], seg["giorno"], seg["uscita"]
    aperta = {}                                   # giorno -> (segno, stop, prezzo d'ingresso di riferimento)

    def livelli(segno, liv_stop, riferimento, q):
        ordini = [Ordine(-segno * q, "stop", liv_stop, solo_riduce=True, etichetta="stop", dopo_ingresso=True)]
        if multiplo is not None:
            r = abs(riferimento - liv_stop)
            if r > 0:
                ordini.append(Ordine(-segno * q, "limite", riferimento + segno * multiplo * r, solo_riduce=True,
                                     etichetta="obiettivo", dopo_ingresso=True))
        return ordini

    def decidi(storia: pd.DataFrame, stato: Stato) -> list:
        i = len(storia) - 1
        g = giorno_di[i]
        if uscita[i]:
            aperta.pop(g, None)
            return [Ordine(-stato.azioni, "mercato", etichetta="chiusura")] if stato.azioni else []
        if direzione[i] != 0 and stato.azioni == 0:
            c = float(storia["close"].iat[-1])
            q = math.floor(QUOTA * stato.valore(c) / c)
            if q <= 0:
                return []
            segno = direzione[i]
            aperta[g] = [segno, stop[i], None]
            # nella barra dell'ingresso il rischio si misura dalla chiusura della candela; dalla barra dopo, dal prezzo d'ingresso
            return [Ordine(segno * q, "mercato", etichetta="ingresso")] + livelli(segno, stop[i], c, q)
        if stato.azioni and g in aperta:
            segno, liv_stop, rif = aperta[g]
            if rif is None:
                rif = aperta[g][2] = float(storia["open"].iat[-1])    # l'apertura della barra dell'ingresso
            return livelli(segno, liv_stop, rif, abs(stato.azioni))
        return []
    return decidi
