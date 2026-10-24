"""Calcolo della prova 10 (`P010_dopo_i_bilanci.md`): regole lì, scritte prima.

    python -m stock.prove.p010     # scrive stock/prove/P010_risultati.md
"""
from __future__ import annotations

import math
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from stock.dati import alpaca, bilanci
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import RADICE, prepara_titolo, rendimenti, scarti_misurati
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import dopo_bilanci as db
from stock.strategie.rimbalzo import strategia_tenere_i_dieci
from stock.universo.costruisci import RINOMINATI


def main():
    universo = pd.read_csv(RADICE / "universo" / "dieci_di_allora.csv")
    originali = sorted(universo["simbolo"].unique())
    universo["simbolo"] = universo["simbolo"].replace(RINOMINATI)
    simboli = sorted(universo["simbolo"].unique())
    fino = date(2024, 12, 31)
    cal = list(alpaca.calendario("2016-01-01", "2024-12-31").index)
    ciks = bilanci.cik_dei_simboli(Path.home() / "stock_dati" / "sp500_attuale.csv", originali)
    comunicati = {}
    for s in originali:
        nome, giorni = bilanci.comunicati_del_simbolo(s, ciks[s])
        giorni = bilanci.un_evento_per_trimestre([d for d in giorni if date(2016, 1, 1) <= d <= date(2024, 11, 30)])
        comunicati[RINOMINATI.get(s, s)] = sorted(set(comunicati.get(RINOMINATI.get(s, s), [])) | set(giorni))
    barre, rett = {}, {}
    for s in simboli:
        barre[s], rett[s], _ = prepara_titolo(s, fino)
    _, spy, _ = prepara_titolo("SPY", fino)
    scarti = scarti_misurati(RADICE / "dati" / "ESITO_CONTROLLI_UNIVERSO.md")

    def costi_per(f):
        base = {s: Costi(mezzo_scarto=scarti[s] / 2, slittamento=0.5 * PB, **IB_FISSO) for s in simboli}
        return {s: Costi() for s in simboli} if f == 0 else base if f == 1 else {s: c.raddoppiati() for s, c in base.items()}

    out = {}
    for nome, f in (("costi", 1), ("costi doppi", 2), ("senza costi", 0)):
        out[nome] = simula_conto(barre, db.strategia(comunicati, universo, cal, rett, spy), costi_per(f), capitale=CAPITALE)
        print(nome, f"{out[nome].valore.iloc[-1]:.0f}", flush=True)
    dieci = simula_conto(barre, strategia_tenere_i_dieci(universo, cal), costi_per(1), capitale=CAPITALE)
    r = out["costi"]
    primo = r.esecuzioni["giorno"].min()
    taglia = lambda v: v[v.index >= primo]  # noqa: E731
    g = {k: rendimenti(taglia(v.valore)) for k, v in out.items()}
    gc = g["costi"]
    gd = rendimenti(taglia(dieci.valore))
    salva_serie("P010_bilanci", gc)
    tutte = carica_serie()
    # guadagno per evento rispetto allo SPY, dai prezzi eseguiti
    e = r.esecuzioni
    pe = []
    for s, x in e.groupby("simbolo"):
        ing, usc = x[x.etichetta == "ingresso"], x[x.etichetta == "uscita"]
        for (_, a), (_, b) in zip(ing.iterrows(), usc.iterrows()):
            pe.append(b["prezzo"] / a["prezzo"] - 1 - (spy[b["giorno"]] / spy[a["giorno"]] - 1))
    pe = np.array(pe)
    t_ev = pe.mean() / pe.std(ddof=1) * math.sqrt(len(pe))
    sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(g["costi doppi"]))
    sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", gc.index.min(), gc.index.max())))
    sr_dieci = annuo(asticella.sharpe(gd))
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1)
         for a, b in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1)))]
    quota = sum(x > 0 for x in q) / len(q)
    passa = sr > max(sr_spy, sr_dieci) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
    tot = lambda v: (1 + v).prod() - 1  # noqa: E731
    n_com = sum(len(v) for v in comunicati.values())
    righe = ["# Prova 10 — risultati", "",
             f"Calcolato da `python -m stock.prove.p010` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P010_dopo_i_bilanci.md` (committate prima). Dal {gc.index.min()} al {gc.index.max()}. Nel conto dell'asticella: "
             + ", ".join(sorted(tutte)) + ".", "",
             f"* Comunicati (8-K voce 2.02) delle aziende delle 10 di allora: {n_com}; ingressi eseguiti {(e.etichetta == 'ingresso').sum()}; "
             f"ordini senza barra {r.senza_barra}; rifiutati {r.rifiutati}; rimasti in mano: {r.bloccati or 'nessuno'}.",
             f"* Costi pagati: commissioni {r.commissioni:,.0f}, scarto e slittamento {r.costo_scarto:,.0f} dollari.", "",
             "| | Dopo i bilanci | Tenere le 10 | Tenere lo SPY |", "|---|---|---|---|",
             f"| Guadagno medio per evento, rispetto allo SPY, con i costi (t) | {pe.mean() * 100:+.2f}% ({t_ev:.2f}) su {len(pe)}; meglio dello SPY {np.mean(pe > 0):.0%} | — | — |",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%} | {tot(gd):+.1%} | — |",
             f"| Sharpe annuo senza costi | {annuo(asticella.sharpe(g['senza costi'])):.2f} | — | — |",
             f"| **1.** Sharpe annuo con i costi (deve battere le altre due colonne) | {sr:.2f} | {sr_dieci:.2f} | {sr_spy:.2f} |",
             f"| **2.** Sharpe corretto per i tentativi (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}) | — | — |",
             f"| t dello Sharpe (da leggere, contro 3) | {ast['t_sharpe']:.2f} | — | — |",
             f"| **3.** Sharpe annuo con i costi doppi (> 0) | {sr2:.2f} | — | — |",
             f"| **4.** Trimestri in guadagno (almeno 60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — | — |",
             f"| Perdita massima dal picco con i costi | {((1 + gc).cumprod() / (1 + gc).cumprod().cummax() - 1).min():.1%} | — | — |",
             f"| **Esito** | **{'passa la ricerca' if passa else 'bocciata'}** | | |"]
    (QUI / "P010_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
