"""Calcolo della prova 21 (`P021_notizie_ordini_limite.md`): regole lì, scritte prima.

    python -m stock.prove.p021     # scrive stock/prove/P021_risultati.md
"""
from __future__ import annotations

import math
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca
from stock.dati.archivio import cartella_dati
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import RADICE, rendimenti, scarti_misurati
from stock.prove.p011 import carica_tutti, costi_per, membri_dell_indice
from stock.prove.p020 import MASSIMO, QUOTA, operazioni
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.motore import simula
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import prima_candela as pc
from stock.strategie.rimbalzo import strategia_tenere_l_indice

COSTI = Costi(mezzo_scarto=23 / 2 * PB, slittamento=2 * PB, **IB_FISSO)


def gira(cal, cal_df, per_giorno, costi, fabbrica):
    valore = CAPITALE
    giornalieri, per_op, eseguiti, non_eseguiti = {}, [], 0, []
    for g in cal:
        lista = sorted(per_giorno.get(g, []), key=lambda x: -abs(x[1]))[:MASSIMO]
        if not lista:
            giornalieri[g] = 0.0
            continue
        m = pd.read_csv(cartella_dati() / "eventi" / "minuti" / f"{g}.csv.gz", index_col="t", parse_dates=["t"])
        guadagno = 0.0
        for s, _ in lista:
            b = m[m["simbolo"] == s][["open", "high", "low", "close", "volume", "vwap"]].sort_index()
            seg = pc.prepara(b, cal_df, set(), 5)
            if not (seg["direzione"] != 0).any():
                continue
            capitale = QUOTA * valore
            r = simula(b, fabbrica(seg), costi, capitale=capitale)
            if r.esecuzioni.empty:
                non_eseguiti.append((g, s))
                continue
            eseguiti += 1
            guadagno += r.valore.iloc[-1] - capitale
            per_op.append(r.valore.iloc[-1] / capitale - 1)
        giornalieri[g] = guadagno / valore
        valore += guadagno
    return pd.Series(giornalieri), np.array(per_op), eseguiti, non_eseguiti


def main():
    membri, simboli = membri_dell_indice()
    cal_df = alpaca.calendario("2016-01-01", "2024-12-31")
    cal = sorted(cal_df.index)
    ops = operazioni(cal, membri)
    per_giorno: dict[date, list] = {}
    for g, s, x in ops:
        per_giorno.setdefault(g, []).append((s, x))
    g, pe, n_es, fuori = gira(cal, cal_df, per_giorno, COSTI, lambda seg: pc.strategia_limite(seg))
    g2, _, _, _ = gira(cal, cal_df, per_giorno, COSTI.raddoppiati(), lambda seg: pc.strategia_limite(seg))
    g0, pe0, _, _ = gira(cal, cal_df, per_giorno, Costi(), lambda seg: pc.strategia_limite(seg))
    # i giorni in cui il limite non si è eseguito: cosa avrebbe dato l'ingresso a mercato (stessi costi)
    solo_fuori: dict[date, list] = {}
    for gg, s in fuori:
        solo_fuori.setdefault(gg, []).append((s, 1.0))
    _, pe_fuori, _, _ = gira(cal, cal_df, solo_fuori, COSTI, lambda seg: pc.strategia(seg))
    inizio = min(per_giorno)
    g, g2, g0 = g[g.index >= inizio], g2[g2.index >= inizio], g0[g0.index >= inizio]
    salva_serie("P021_notizie_limite", g)
    tutte = carica_serie()
    sr, sr2 = annuo(asticella.sharpe(g)), annuo(asticella.sharpe(g2))
    sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", g.index.min(), g.index.max())))
    barre_g, _, _ = carica_tutti(simboli, date(2024, 12, 31))
    scarti = scarti_misurati(RADICE / "dati" / "ESITO_CONTROLLI_UNIVERSO.md")
    tutto = simula_conto(barre_g, strategia_tenere_l_indice(membri, cal), costi_per(list(barre_g), scarti, 1), capitale=CAPITALE)
    sr_tutto = annuo(asticella.sharpe(rendimenti(tutto.valore[tutto.valore.index >= g.index.min()])))
    ast = asticella.sharpe_corretto(g, tutte)
    q = [float((1 + g[(g.index >= a) & (g.index < b)]).prod() - 1)
         for a, b in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1)))]
    quota = sum(x > 0 for x in q) / len(q)
    tot = lambda v: (1 + v).prod() - 1  # noqa: E731
    t_op = pe.mean() / pe.std(ddof=1) * math.sqrt(len(pe))
    anni = (1 + g).groupby(pd.Index([d.year for d in g.index])).prod() - 1
    passa = sr > max(sr_spy, sr_tutto) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
    righe = ["# Prova 21 — risultati", "",
             f"Calcolato da `python -m stock.prove.p021` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P021_notizie_ordini_limite.md` (committate prima). Dal {g.index.min()} al {g.index.max()}. Nel conto: {len(tutte)} serie.", "",
             f"* Giorni in gioco: {len(ops)}; ordini limite eseguiti {n_es}; non eseguiti {len(fuori)}.",
             f"* Nei giorni non eseguiti, l'ingresso a mercato (stessi costi) avrebbe dato {pe_fuori.mean() * 100:+.3f}% a operazione "
             f"(su {len(pe_fuori)}): {'restano fuori i casi migliori' if len(pe_fuori) and pe_fuori.mean() > pe.mean() else 'non restano fuori i casi migliori'}.", "",
             "| | Notizie, ingresso a limite | Tenere lo SPY |", "|---|---|---|",
             f"| Per operazione con i costi (t) | {pe.mean() * 100:+.3f}% ({t_op:.2f}); in guadagno {np.mean(pe > 0):.0%}; senza costi {pe0.mean() * 100:+.3f}% | — |",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g0):+.1%} / {tot(g):+.1%} / {tot(g2):+.1%} | — |",
             f"| Sharpe annuo senza costi | {annuo(asticella.sharpe(g0)):.2f} | — |",
             f"| **1.** Sharpe annuo con i costi | {sr:.2f} | {sr_spy:.2f} (indice a pesi uguali: {sr_tutto:.2f}) |",
             f"| **2.** Sharpe corretto per i tentativi (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}) | — |",
             f"| t dello Sharpe (da leggere, contro 3) | {ast['t_sharpe']:.2f} | — |",
             f"| **3.** Sharpe annuo con i costi doppi (> 0) | {sr2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (almeno 60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Anni in guadagno (da leggere) | {(anni > 0).sum()} su {len(anni)} | — |",
             f"| Perdita massima dal picco con i costi | {((1 + g).cumprod() / (1 + g).cumprod().cummax() - 1).min():.1%} | — |",
             f"| **Esito** | **{'passa la ricerca' if passa else 'bocciata'}** | |"]
    (QUI / "P021_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
