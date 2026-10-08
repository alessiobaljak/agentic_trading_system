"""Fase 3: dove la variante NON funziona, sui soli dati di costruzione (solo lettura, non scrive il log).

  python fase3.py <ID>

Riesegue la variante sul periodo di costruzione e divide i trade per caratteristiche note AL
MOMENTO DEL SEGNALE (nessuna informazione dopo l'ingresso): terzili della volatilita' (ATR(14) in %
del close), terzili della forza del segnale quando la variante ne ha una, anno, giorno della
settimana, posizione rispetto alla media di 200 barre, direzione di BTC nella barra di segnale.
Per ogni gruppo: trade, R medio, R medio della (b) non si ricalcola (resta quella del log).
"""
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import comune  # noqa: E402
from varianti import VARIANTI, rendimenti  # noqa: E402


def forza(vid, s, i):
    """La grandezza del segnale alla barra i, se la variante ne ha una (None altrimenti)."""
    c = s.last
    if vid in ("SOLUSDT-014", "SOLUSDT-015"):
        per_ts = {x.ts: k for k, x in enumerate(c)}
        j = per_ts.get(c[i].ts - 23 * 3_600_000)
        return None if j is None else c[j].close / c[j].open - 1
    if i >= 1:
        return c[i].close / c[i - 1].close - 1
    return None


def gruppi(nome, valori, r):
    valori = np.asarray(valori, dtype=float)
    ok = ~np.isnan(valori)
    if ok.sum() < 6:
        return {}
    q1, q2 = np.nanpercentile(valori[ok], [100 / 3, 200 / 3])
    out = {}
    for etichetta, m in (("basso", valori <= q1), ("medio", (valori > q1) & (valori <= q2)), ("alto", valori > q2)):
        m = m & ok
        if m.sum():
            out[f"{nome}_{etichetta}"] = {"trade": int(m.sum()), "r_medio": round(float(np.mean(r[m])), 4),
                                          "soglie": [round(float(q1), 5), round(float(q2), 5)]}
    return out


def principale(vid):
    tf, costr = VARIANTI[vid][0], VARIANTI[vid][1]
    s = comune.carica(tf, "costruzione")
    ris = comune.motore.esegui(s.last, None, s.mark, s.funding, comune.fabbrica(s, costr)(), comune.PARAMETRI)
    tr = sorted(ris.trades, key=lambda t: t.ts_uscita)
    indice = {c.ts: k for k, c in enumerate(s.last)}
    passo = comune.ms_tf(tf)
    a = comune.atr(s.last, 14)
    close = comune.arr(s.last, "close")
    m200 = comune.sma(close, 200)
    r = np.array([t.r for t in tr])
    seg = [indice[t.ts_entrata] - 1 for t in tr]  # barra di segnale (ritardo 0)
    out = {"id": vid, "trade": len(tr), "r_medio": round(float(r.mean()), 4)}
    out.update(gruppi("volatilita", [a[i] / close[i] if i >= 0 else np.nan for i in seg], r))
    f = [forza(vid, s, i) for i in seg]
    out.update(gruppi("forza_abs", [abs(x) if x is not None else np.nan for x in f], r))
    sopra = np.array([close[i] > m200[i] if not math.isnan(m200[i]) else np.nan for i in seg], dtype=float)
    for nome, m in (("sopra_sma200", sopra == 1), ("sotto_sma200", sopra == 0)):
        if m.sum():
            out[nome] = {"trade": int(m.sum()), "r_medio": round(float(r[m].mean()), 4)}
    btc = []
    for i in seg:
        b, b0 = s.btc.get(s.last[i].ts), s.btc.get(s.last[i].ts - passo)
        btc.append(np.nan if b is None or b0 is None else float(np.sign(b.close - b0.close)))
    btc = np.array(btc)
    for nome, m in (("btc_su", btc == 1), ("btc_giu", btc == -1)):
        if m.sum():
            out[nome] = {"trade": int(m.sum()), "r_medio": round(float(r[m].mean()), 4)}
    if vid in ("SOLUSDT-014", "SOLUSDT-015"):
        # Gao et al. (2018): anche la penultima mezz'ora (qui la barra di segnale 23:00-23:30) e il resto del giorno
        c = s.last
        per_ts = {x.ts: k for k, x in enumerate(c)}
        penultima = np.array([c[i].close / c[i].open - 1 for i in seg])
        giorno = []
        for i in seg:
            j = per_ts.get(c[i].ts - 23 * 3_600_000)
            giorno.append(np.nan if j is None else c[i].close / c[j].open - 1)
        giorno = np.array(giorno)
        for nome, m in (("penultima_giu", penultima < 0), ("penultima_su", penultima >= 0),
                        ("giorno_giu", giorno < 0), ("giorno_su", giorno >= 0)):
            if m.sum():
                out[nome] = {"trade": int(m.sum()), "r_medio": round(float(r[m].mean()), 4)}
        dist = np.array([close[i] / m200[i] - 1 if not math.isnan(m200[i]) else np.nan for i in seg])
        out.update(gruppi("distanza_sma200", dist, r))
    gs = {}
    for t in tr:
        g = datetime.fromtimestamp(t.ts_entrata / 1000, tz=timezone.utc).weekday()
        gs.setdefault(g, []).append(t.r)
    out["giorno_ingresso"] = {str(g): {"trade": len(v), "r_medio": round(float(np.mean(v)), 4)} for g, v in sorted(gs.items())}
    es = {}
    for t in tr:
        es.setdefault(t.esito, []).append(t.r)
    out["per_esito"] = {e: {"trade": len(v), "r_medio": round(float(np.mean(v)), 4)} for e, v in es.items()}
    out["r_lordo_medio"] = round(float(np.mean([(t.pnl + t.commissioni + t.slippage_costo + t.funding_pagato) / t.rischio_iniziale for t in tr])), 4)
    return out


if __name__ == "__main__":
    for vid in sys.argv[1:]:
        print(json.dumps(principale(vid), ensure_ascii=False))
