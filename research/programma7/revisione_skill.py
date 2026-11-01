"""Revisione di G1 con le skill (1° novembre 2026, richiesta del proprietario): costruisce la serie giornaliera di G1 e le serie di
confronto per la skill `residual-edge-analyzer`, scelte e scritte qui prima di guardare il risultato:
* mercato: il Bitcoin (apertura → apertura);
* pesi_uguali: la media delle monete dell'universo di G1 del giorno;
* momento: long il quinto con il rendimento dei 28 giorni prima più alto, short il più basso, pesi uguali, fra le monete dell'universo;
* settori: reti principali meno (meme + finanza decentralizzata), pesi uguali, fra le monete dell'universo (settori di CoinGecko di oggi,
  prova 142).
G1 si misura prima delle spese di scambio (lordo meno funding), come le serie di confronto che non hanno costi.
Il regime: il Bitcoin sopra o sotto il prezzo di 30 giorni prima (deciso solo con i prezzi già noti).

Uso: python3 -m research.programma7.revisione_skill
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.programma6 import seconda as sc
from research.programma6 import sesta as se
from research.programma6 import terza as te
from research.programma7 import ottantesima as gs
from research.programma7 import prima as g1

QUI = Path(__file__).parent
OUT = QUI / "revisione_skill"


def esegui() -> None:
    pan = sc.pannello()
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    giorni = np.arange(se.INIZIO, g1.FINE, dtype=np.int64)
    idx = giorni - pan["t0"]
    Ud = g1.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
    S = list(pan["simboli"])
    R = sc.rendimenti(pan)[idx]
    c = pan["close"]
    with np.errstate(all="ignore"):
        m28 = c[idx - 1] / c[idx - 29] - 1
    sett = gs.settore_di(S)
    jb = S.index("BTCUSDT")
    righe = []
    d = pd.read_csv(QUI / "risultati_prima" / "giorni_G1.csv.gz").set_index("giorno")
    for k, g in enumerate(giorni):
        u = Ud[k] & np.isfinite(R[k])
        r = R[k]
        ew = float(r[u].mean())
        ok = u & np.isfinite(m28[k])
        q = pd.Series(m28[k, ok]).rank(pct=True).to_numpy()
        jj = np.flatnonzero(ok)
        mom = float(r[jj[q > 0.8]].mean() - r[jj[q <= 0.2]].mean()) if len(jj) >= 20 else 0.0
        l1 = u & (sett == "reti principali")
        md = u & np.isin(sett, ["meme", "finanza decentralizzata"])
        sec = float(r[l1].mean() - r[md].mean()) if l1.sum() >= 3 and md.sum() >= 3 else 0.0
        btc_trend = "sopra" if c[idx[k] - 1, jb] >= c[idx[k] - 31, jb] else "sotto"
        x = d.loc[int(g)]
        righe.append({"date": sc.data(int(g)), "g1_lordo": float(x["lordo"] - x["funding"]), "g1_netto": float(x["netto"]),
                      "mercato": float(r[jb]), "pesi_uguali": ew, "momento": mom, "settori": sec, "bitcoin_30_giorni": btc_trend})
    OUT.mkdir(exist_ok=True)
    pd.DataFrame(righe).to_csv(OUT / "serie.csv", index=False)
    base = {"schema_version": "1.0", "date_column": "date", "return_unit": "decimal", "frequency": "daily", "annualization_factor": 365,
            "primary_model": {"name": "mercato_e_altcoin", "baseline_columns": ["mercato", "pesi_uguali"]},
            "sensitivity_models": [{"name": "mercato", "baseline_columns": ["mercato"]},
                                   {"name": "piu_momento", "baseline_columns": ["mercato", "pesi_uguali", "momento"]},
                                   {"name": "piu_settori", "baseline_columns": ["mercato", "pesi_uguali", "settori"]},
                                   {"name": "tutti", "baseline_columns": ["mercato", "pesi_uguali", "momento", "settori"]}],
            "regime_columns": ["bitcoin_30_giorni"], "rolling_window": 182, "minimum_observations": 60, "minimum_regime_observations": 20,
            "minimum_rolling_windows": 12, "hac_lags": "auto", "include_series": False}
    for nome, col, basis in (("lordo", "g1_lordo", "gross"), ("netto", "g1_netto", "net")):
        cfg = {**base, "strategy_column": col,
               "data_declarations": {"baseline_selection": "predeclared", "strategy_return_basis": basis, "baseline_return_basis": "gross",
                                     "analysis_scope": "in_sample", "universe_data": "point_in_time"}}
        (OUT / f"config_{nome}.json").write_text(json.dumps(cfg, indent=1))
    print("serie", len(righe))


if __name__ == "__main__":
    esegui()


def rapporto_rischio(periodi: int = 365) -> dict:
    """La skill `risk-report` sui rendimenti giornalieri netti di G1 (serie.csv)."""
    d = pd.read_csv(OUT / "serie.csv", parse_dates=["date"]).set_index("date")
    r, b = d["g1_netto"], d["mercato"]
    cum = (1 + r).cumprod()
    dd = cum / cum.cummax() - 1
    giu = r[r < 0]
    var95, var99 = np.percentile(r, 5), np.percentile(r, 1)
    durate = (dd < 0).astype(int).groupby(dd.eq(0).cumsum()).sum()
    # discese: profondità di ogni tratto sotto il massimo
    tratti = dd.groupby(dd.eq(0).cumsum()).min()
    mesi = (1 + r).resample("ME").prod() - 1
    cagr = cum.iloc[-1] ** (periodi / len(r)) - 1
    out = {"rendimento_totale": cum.iloc[-1] - 1, "rendimento_annuo_composto": cagr,
           "mese_medio": mesi.mean(), "mese_mediano": mesi.median(), "mese_deviazione": mesi.std(),
           "volatilita_annua": r.std() * np.sqrt(periodi), "discesa_massima": dd.min(), "discesa_piu_lunga_giorni": int(durate.max()),
           "indice_ulcer": float(np.sqrt((dd ** 2).mean())), "deviazione_al_ribasso_annua": giu.std() * np.sqrt(periodi),
           "sharpe": r.mean() / r.std() * np.sqrt(periodi), "sortino": r.mean() / giu.std() * np.sqrt(periodi),
           "calmar": cagr / abs(dd.min()), "omega": r[r > 0].sum() / abs(r[r < 0].sum()),
           "var_95": var95, "var_99": var99, "cvar_95": r[r <= var95].mean(), "cvar_99": r[r <= var99].mean(),
           "rapporto_code": abs(np.percentile(r, 95)) / abs(var95), "asimmetria": r.skew(), "curtosi": r.kurtosis(),
           "beta_bitcoin": float(np.cov(r, b)[0, 1] / np.var(b, ddof=1)),
           "correlazione_bitcoin_30_giorni": {"mediana": float(r.rolling(30).corr(b).median()), "minima": float(r.rolling(30).corr(b).min()),
                                              "massima": float(r.rolling(30).corr(b).max())},
           "mesi_positivi": float((mesi > 0).mean()),
           "tre_mesi_peggiori": {k.strftime("%Y-%m"): float(v) for k, v in mesi.nsmallest(3).items()},
           "tre_mesi_migliori": {k.strftime("%Y-%m"): float(v) for k, v in mesi.nlargest(3).items()},
           "discese_oltre": {"5%": int((tratti < -0.05).sum()), "10%": int((tratti < -0.10).sum()), "20%": int((tratti < -0.20).sum())}}
    (OUT / "rischio.json").write_text(json.dumps(out, indent=1, default=float))
    return out
