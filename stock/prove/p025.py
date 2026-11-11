"""Calcolo della prova 25 (`P025_miscela.md`): regole lì, scritte prima.

    python -m stock.prove.p025     # scrive stock/prove/P025_risultati.md
"""
from __future__ import annotations

import math
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.prove.p001 import QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

PARTI = ["P007_SPY", "P007_QQQ", "P015_SPY", "P015_QQQ", "P016_SPY", "P016_QQQ"]
# guadagno totale senza costi e con i costi, dai risultati committati delle prove 7, 15 e 16 (riga «Guadagno totale»)
GUADAGNI = {"P007_SPY": (0.182, 0.168), "P007_QQQ": (0.279, 0.261), "P015_SPY": (2.829, 2.363), "P015_QQQ": (3.798, 3.473),
            "P016_SPY": (1.541, 1.540), "P016_QQQ": (2.541, 2.539)}


def main():
    tutte = carica_serie()
    parti = pd.DataFrame({p: tutte[p] for p in PARTI}).dropna()
    m = parti.mean(axis=1)
    costo = []
    for p in PARTI:
        s = tutte[p]
        anni = len(s) / 252
        senza, con = GUADAGNI[p]
        costo.append((math.log(1 + senza) - math.log(1 + con)) / anni)
    m2 = m - np.mean(costo) / 252
    salva_serie("P025_miscela", m)
    tutte = carica_serie()
    a, b = m.index.min(), m.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    qqq = comprare_e_tenere("QQQ", a, b)
    meta = (0.5 * spy + 0.5 * qqq.reindex(spy.index)).dropna()
    sr, sr2 = annuo(asticella.sharpe(m)), annuo(asticella.sharpe(m2))
    sr_spy, sr_meta = annuo(asticella.sharpe(spy)), annuo(asticella.sharpe(meta))
    ast = asticella.sharpe_corretto(m, tutte)
    q = [float((1 + m[(m.index >= x) & (m.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(t > 0 for t in q) / len(q)
    passa = sr > max(sr_spy, sr_meta) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
    tot = lambda x: (1 + x).prod() - 1  # noqa: E731
    dd = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min()  # noqa: E731
    anni = (1 + m).groupby(pd.Index([d.year for d in m.index])).prod() - 1
    righe = ["# Prova 25 — risultati", "",
             f"Calcolato da `python -m stock.prove.p025` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di `P025_miscela.md` "
             f"(committate prima). Dal {a} al {b} ({len(m)} giorni). Nel conto dell'asticella: {len(tutte)} serie.", "",
             "| | Miscela | Tenere lo SPY | Metà SPY e metà QQQ |", "|---|---|---|---|",
             f"| Guadagno totale | {tot(m):+.1%} | {tot(spy):+.1%} | {tot(meta):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr:.2f}** | {sr_spy:.2f} | {sr_meta:.2f} |",
             f"| Perdita massima dal picco | {dd(m):.1%} | {dd(spy):.1%} | {dd(meta):.1%} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — | — |",
             f"| **3.** Sharpe con i costi doppi, stimato (> 0) | {sr2:.2f} | — | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(t > 0 for t in q)} su {len(q)} ({quota:.0%}) | — | — |",
             f"| Anno per anno (da leggere) | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — | — |",
             f"| **Esito** | **{'passa la ricerca' if passa else 'bocciata'}** | | |", "",
             "Da leggere, sullo stesso periodo: Sharpe di ciascuna parte "
             + ", ".join(f"{p} {annuo(asticella.sharpe(parti[p])):.2f}" for p in PARTI) + ".", "",
             "Correlazioni fra le parti:", "", "| | " + " | ".join(PARTI) + " |", "|---" * (len(PARTI) + 1) + "|"]
    c = parti.corr()
    for p in PARTI:
        righe.append(f"| {p} | " + " | ".join(f"{c.loc[p, x]:.2f}" for x in PARTI) + " |")
    (QUI / "P025_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
