"""Migliorare G1, voce 7, seconda parte: perché nel 2026 il lato venduto di G1 fa meglio della media dell'universo (cioè perde per G1).
Solo una misura (`MIGLIORARE_G1.md`): mese per mese, le monete che pesano di più, e il funding che il lato venduto incassa.

Uso: python3 -m research.programma7.g1_venduto_2026
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as nu

QUI = Path(__file__).parent


def main():
    pan = sc.pannello()
    simboli = pan["simboli"]
    giorni = np.arange(sc.giorno(2026, 1, 1), sc.giorno(2026, 10, 5), dtype=np.int64)
    idx = giorni - pan["t0"]
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]
    F = np.nan_to_num(pan["funding"][idx])
    U = nu.universo_giorni(pan, idx)
    W, _, _ = nu.pesi(pan, idx, U, fisso=(1.0, 1.0))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        media = np.nan_to_num(np.nanmean(np.where(U, R, np.nan), axis=1))
    S = np.where(W < 0, W, 0.0)
    L = np.where(W > 0, W, 0.0)
    rel_s = S * (R - media[:, None])          # positivo = guadagno per G1 (la venduta fa peggio della media)
    rel_l = L * (R - media[:, None])
    mesi = pd.to_datetime(giorni * 86400, unit="s").strftime("%Y-%m")
    d = pd.DataFrame({"venduto_sotto_la_media": rel_s.sum(1), "comprato_sopra_la_media": rel_l.sum(1),
                      "funding_incassato_dal_venduto": -(S * F).sum(1), "funding_incassato_dal_comprato": -(L * F).sum(1),
                      "mercato": media}, index=mesi)
    per_mese = d.groupby(level=0).sum()
    contrib = pd.Series(rel_s.sum(0), index=simboli)
    peggiori = contrib.nsmallest(12)
    giorni_peggiori = pd.Series(rel_s.sum(1), index=[sc.data(int(g)) for g in giorni]).nsmallest(8)
    out = {"periodo": [sc.data(int(giorni[0])), sc.data(int(giorni[-1]))],
           "totale": {k: float(v) for k, v in d.sum().items()},
           "per_mese": {m: {k: round(float(v), 4) for k, v in r.items()} for m, r in per_mese.iterrows()},
           "vendute_che_costano_di_piu": {s: round(float(v), 4) for s, v in peggiori.items()},
           "giorni_peggiori_del_venduto": {g: round(float(v), 4) for g, v in giorni_peggiori.items()},
           "quota_delle_12_peggiori": float(peggiori.sum() / rel_s.sum()) if rel_s.sum() else None}
    (QUI / "risultati_g1_venduto_2026.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
