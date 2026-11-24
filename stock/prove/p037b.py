"""Prova 37b — l'esame «da crisi» della prova 37 (anticipare il ribilanciamento dei fondi 60/40) sul periodo chiuso, dal 2 gennaio 2025
al 30 settembre 2026, con la regola, i dati e i costi della prova 37 (`P037b_esame_da_crisi.md`).

    python -m stock.prove.p037b       # in locale: prezzi di Yahoo (mai nel repository)
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.prove import p037 as b
from stock.prove.p001 import QUI
from stock.prove.p035 import dd, sr, tot

DAL_DATI, DAL, FINO = "2024-10-01", date(2025, 1, 2), date(2026, 9, 30)


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def mese_della_crisi(spy: pd.Series) -> tuple[int, int]:
    """Il mese di calendario con la deviazione standard dei rendimenti giornalieri dello SPY più alta."""
    k = spy.groupby(pd.Index([d.year * 100 + d.month for d in spy.index])).std(ddof=1).idxmax()
    return int(k) // 100, int(k) % 100


def nel_mese(x: pd.Series, mese: tuple[int, int]) -> pd.Series:
    return x[[(d.year, d.month) == mese for d in x.index]]


def esame(gc: pd.Series, doppi: pd.Series, spy: pd.Series) -> dict:
    """Le tre condizioni dell'esame da crisi (P037b_esame_da_crisi.md)."""
    mese = mese_della_crisi(spy)
    crisi = float((1 + nel_mese(gc, mese)).prod() - 1)
    comuni = gc.index.intersection(spy.index)
    corr = float(np.corrcoef(gc.loc[comuni], spy.loc[comuni])[0, 1])
    insieme = 0.75 * spy.loc[comuni] + 0.25 * gc.loc[comuni]
    c1 = crisi > 0
    c2 = tot(gc) > 0 and tot(doppi) > 0
    c3 = corr < 0.3 and sr(insieme) > sr(spy.loc[comuni])
    return {"mese": mese, "crisi": crisi, "corr": corr, "sr_insieme": sr(insieme), "sr_spy": sr(spy.loc[comuni]),
            "c1": c1, "c2": c2, "c3": c3, "passa": c1 and c2 and c3}


# --- con i prezzi ------------------------------------------------------------------------------------------------------------------
def carica(simbolo: str) -> pd.DataFrame:
    from stock.dati import yahoo
    df = yahoo.prezzi(simbolo, DAL_DATI, FINO.isoformat())
    df = df[df.index.date <= FINO]
    return pd.DataFrame({"rett": df["rettificata"].to_numpy(), "close": df["close"].to_numpy()}, index=pd.Index(df.index.date))


def main():
    d = {s: carica(s) for s in ("SPY", "IEF", "TLT")}
    giorni = sorted(set(d["SPY"].index) & set(d["IEF"].index) & set(d["TLT"].index))
    r = {s: d[s]["rett"].reindex(giorni).pct_change().fillna(0.0) for s in d}
    p = {s: d[s]["close"].reindex(giorni) for s in d}
    pesi = {}
    for obbl in ("IEF", "TLT"):
        fa = b.segnale_fascia(r["SPY"], r[obbl])
        ca = b.segnale_calendario(r["SPY"], r[obbl])
        pf, pc = b.posizioni(fa, ca, finisce_a_fine_mese=True)          # i dati finiscono il 30 settembre 2026, fine mese
        pesi[obbl] = (pf + pc) / 2
    tieni = [g for g in giorni if DAL <= g <= FINO]

    def serie(peso, obbl="IEF", **k):
        return b.conto(peso, r["SPY"], r[obbl], p["SPY"], p[obbl], obbl=obbl, **k).loc[tieni]
    gc = serie(pesi["IEF"])
    g = {"costi doppi": serie(pesi["IEF"], fattore=2.0), "senza costi": serie(pesi["IEF"], costi=False),
         "un giorno di ritardo": serie(pesi["IEF"], ritardo=1), "con TLT": serie(pesi["TLT"], "TLT")}
    spy = r["SPY"].loc[tieni]
    e = esame(gc, g["costi doppi"], spy)
    mesi = sorted({(x.year, x.month) for x in gc.index})
    tab = [f"| {a}-{m:02d} | {float((1 + nel_mese(gc, (a, m))).prod() - 1):+.2%} | {float((1 + nel_mese(spy, (a, m))).prod() - 1):+.2%} | "
           f"{float(nel_mese(spy, (a, m)).std(ddof=1)):.2%} |" for a, m in mesi]
    log = np.log1p(gc)
    quota_10 = float(log.sort_values(ascending=False).iloc[:10].sum() / log.sum()) if log.sum() > 0 else float("nan")
    lettura = [f"| {k} | {sr(v):.2f} | {tot(v):+.1%} | {dd(v):.1%} |" for k, v in g.items()]
    si = lambda x: "sì" if x else "no"
    testo = ["# Prova 37b — risultati (esame da crisi sul periodo chiuso)", "",
             f"Calcolato da `python -m stock.prove.p037b` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P037b_esame_da_crisi.md` (committate prima). Dal {gc.index.min()} al {gc.index.max()}, {len(gc)} giorni; prezzi di Yahoo.",
             "",
             f"**Il mese della crisi** (deviazione standard dello SPY più alta): **{e['mese'][0]}-{e['mese'][1]:02d}**, SPY "
             f"{float((1 + nel_mese(spy, e['mese'])).prod() - 1):+.2%} nel mese.", "",
             "| Condizione | Valore | Passa |", "|---|---|---|",
             f"| **1.** Paga nella crisi (rendimento con i costi nel mese della crisi > 0) | {e['crisi']:+.2%} | {si(e['c1'])} |",
             f"| **2.** Paga più di quanto costa (periodo in guadagno con i costi e con i costi doppi) | {tot(gc):+.2%} / "
             f"{tot(g['costi doppi']):+.2%} | {si(e['c2'])} |",
             f"| **3.** Serve accanto allo SPY (correlazione < 0,3; 3/4 SPY + 1/4 parte con Sharpe più alto) | correlazione "
             f"{e['corr']:+.2f}; Sharpe {e['sr_insieme']:.2f} contro {e['sr_spy']:.2f} | {si(e['c3'])} |",
             f"| **Esito** | | **{'passa: la proposta va al proprietario' if e['passa'] else 'non passa: la prova 37 è bocciata definitivamente'}** |",
             "", f"Con i costi: Sharpe {sr(gc):.2f}, perdita massima {dd(gc):.1%}; lo SPY: Sharpe {sr(spy):.2f}, {tot(spy):+.1%}. Dai 10 giorni "
             f"migliori viene il {quota_10:.0%} del guadagno (in logaritmi).", "",
             "**Mese per mese (da leggere):**", "", "| Mese | La regola, con i costi | Lo SPY | Deviazione standard giornaliera dello SPY |",
             "|---|---|---|---|", *tab, "",
             "**Da leggere accanto (non cambiano l'esito):**", "", "| Versione | Sharpe | Guadagno totale | Perdita massima |", "|---|---|---|---|",
             *lettura, "", "Nel conto: 1 prova (115). Il periodo chiuso della famiglia «ribilanciamento» è usato."]
    (QUI / "P037b_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:14]))


if __name__ == "__main__":
    main()
