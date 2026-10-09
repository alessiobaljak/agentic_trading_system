"""Fase 3: studio dei fallimenti di una variante, solo sui dati di costruzione.

Uso: python -m research.campagne.GALAUSDT.codice.fallimenti <ID>
Scrive in research/data/insample/GALAUSDT/uscite/<ID>_fallimenti.json: R per esito, per anno, per
ora d'ingresso, per terzili delle caratteristiche della barra di segnale, durata.
"""

import json
import sys
from datetime import datetime, timezone

import numpy as np

from research.src import motore
from research.campagne.GALAUSDT.codice import comune
from research.campagne.GALAUSDT.codice.catalogo import crea_variante


def gruppi(chiavi, r):
    out = {}
    for k, x in zip(chiavi, r):
        out.setdefault(str(k), []).append(x)
    return {k: {"n": len(v), "r_medio": round(float(np.mean(v)), 3), "vinti": round(float(np.mean(np.array(v) > 0)), 2)}
            for k, v in sorted(out.items())}


def terzili(valori, r):
    v = np.array(valori, dtype=float)
    ok = ~np.isnan(v)
    if ok.sum() < 9:
        return {}
    q1, q2 = np.nanquantile(v, [1 / 3, 2 / 3])
    etich = np.where(v <= q1, "basso", np.where(v <= q2, "medio", "alto"))
    etich = np.where(ok, etich, "nan")
    return {"soglie": [round(float(q1), 5), round(float(q2), 5)], **gruppi(etich, r)}


def main(vid):
    var = crea_variante(vid)
    ctx = comune.contesto(var.tf, "costruzione")
    prm = comune.parametri()
    ris = motore.esegui(ctx.candele, None, ctx.candele_mark, ctx.funding,
                        comune.crea_fabbrica(var, ctx, "variante")(), prm)
    trades = ris.trades
    r = [t.r for t in trades]
    idx_ts = {c.ts: k for k, c in enumerate(ctx.candele)}
    df = ctx.df
    # barra di segnale = barra prima di quella d'ingresso
    seg = [idx_ts[t.ts_entrata] - 1 for t in trades]
    ret1 = (df["close"] / df["close"].shift(1) - 1).to_numpy()
    btc1 = (df["btc_close"] / df["btc_close"].shift(1) - 1).to_numpy()
    rng = ((df["high"] - df["low"]) / df["close"]).to_numpy()
    at = comune.atr(df, 24) / df["close"].to_numpy()
    vol = df["quote_volume"].to_numpy()
    volm = df["quote_volume"].shift(1).rolling(168, min_periods=24).mean().to_numpy()
    tend = (df["close"] / df["close"].shift(42) - 1).to_numpy()
    btc_tend = (df["btc_close"] / df["btc_close"].shift(42) - 1).to_numpy()
    out = {
        "trade": len(trades), "r_medio": float(np.mean(r)),
        "per_esito": gruppi([t.esito for t in trades], r),
        "per_anno": gruppi([datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).year for t in trades], r),
        "per_mese": gruppi([datetime.fromtimestamp(t.ts_uscita / 1000, tz=timezone.utc).strftime("%Y-%m") for t in trades], r),
        "per_ora_ingresso": gruppi([datetime.fromtimestamp(t.ts_entrata / 1000, tz=timezone.utc).hour for t in trades], r),
        "per_giorno_settimana": gruppi([datetime.fromtimestamp(t.ts_entrata / 1000, tz=timezone.utc).weekday() for t in trades], r),
        "terzili_rendimento_barra_segnale": terzili([ret1[k] for k in seg], r),
        "terzili_rendimento_btc_barra_segnale": terzili([btc1[k] for k in seg], r),
        "terzili_range_barra_segnale": terzili([rng[k] for k in seg], r),
        "terzili_atr_relativo": terzili([at[k] for k in seg], r),
        "terzili_volume_relativo": terzili([vol[k] / volm[k] if volm[k] > 0 else np.nan for k in seg], r),
        "terzili_tendenza_42_barre": terzili([tend[k] for k in seg], r),
        "terzili_tendenza_btc_42_barre": terzili([btc_tend[k] for k in seg], r),
        "r_migliori_5": sorted(r)[-5:], "r_peggiori_5": sorted(r)[:5],
    }
    comune.CARTELLA_DATI.joinpath("uscite").mkdir(parents=True, exist_ok=True)
    (comune.CARTELLA_DATI / "uscite" / f"{vid}_fallimenti.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, default=float)[:6000])


if __name__ == "__main__":
    main(sys.argv[1])
