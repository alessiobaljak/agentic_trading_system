"""Calcolo della prova 18 (`P018_acquisti_dirigenti.md`): regole lì, scritte prima.

    python -m stock.prove.p018     # scrive stock/prove/P018_risultati.md
"""
from __future__ import annotations

import math
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca, controlli
from stock.dati.dirigenti import acquisti
from stock.prove.p001 import CAPITALE, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import RADICE, rendimenti, scarti_misurati
from stock.prove.p011 import carica_tutti, costi_per, membri_dell_indice
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import dirigenti
from stock.strategie.rimbalzo import strategia_tenere_l_indice
from stock.universo.costruisci import cambi_di_nome


def main():
    membri, simboli = membri_dell_indice()
    fino = date(2024, 12, 31)
    cal = list(alpaca.calendario("2016-01-01", "2024-12-31").index)
    barre, rett, senza = carica_tutti(simboli, fino)
    cambi = cambi_di_nome()
    chiusure = {s: pd.Series(df["close"].to_numpy(), index=pd.Index(controlli.date_ny(df.index))) for s, df in barre.items()}
    a = acquisti("2016-01-01", "2024-11-30", chiusure=lambda s: chiusure.get(cambi.get(s, s)))
    a["simbolo"] = a["simbolo"].map(lambda s: cambi.get(s, s))
    nell_indice = a[[s in set(membri(d)) and s in barre for d, s in zip(a["deposito"], a["simbolo"])]]
    eventi = list(zip(nell_indice["deposito"], nell_indice["simbolo"], nell_indice["valore"]))
    print(f"acquisti puliti sopra 100'000: {len(a)}; nell'S&P 500: {len(eventi)}", flush=True)
    scarti = scarti_misurati(RADICE / "dati" / "ESITO_CONTROLLI_UNIVERSO.md")
    out = {}
    for nome, f in (("costi", 1), ("costi doppi", 2), ("senza costi", 0)):
        out[nome] = simula_conto(barre, dirigenti.strategia(eventi, cal), costi_per(list(barre), scarti, f), capitale=CAPITALE)
        print(nome, f"{out[nome].valore.iloc[-1]:.0f}", flush=True)
    tutto = simula_conto(barre, strategia_tenere_l_indice(membri, cal), costi_per(list(barre), scarti, 1), capitale=CAPITALE)
    r = out["costi"]
    primo = r.esecuzioni["giorno"].min()
    taglia = lambda v: v[v.index >= primo]  # noqa: E731
    g = {k: rendimenti(taglia(v.valore)) for k, v in out.items()}
    gc, gt = g["costi"], rendimenti(taglia(tutto.valore))
    salva_serie("P018_dirigenti", gc)
    tutte = carica_serie()
    _, spy, _ = __import__("stock.prove.p003", fromlist=["prepara_titolo"]).prepara_titolo("SPY", fino)
    e = r.esecuzioni
    pe = []
    for s, x in e.groupby("simbolo"):
        ing, usc = x[x.etichetta == "ingresso"], x[x.etichetta == "uscita"]
        for (_, i), (_, u) in zip(ing.iterrows(), usc.iterrows()):
            pe.append(u["prezzo"] / i["prezzo"] - 1 - (spy[u["giorno"]] / spy[i["giorno"]] - 1))
    pe = np.array(pe)
    t_ev = pe.mean() / pe.std(ddof=1) * math.sqrt(len(pe))
    sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(g["costi doppi"]))
    sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", gc.index.min(), gc.index.max())))
    sr_tutto = annuo(asticella.sharpe(gt))
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= a_) & (gc.index < b_)]).prod() - 1)
         for a_, b_ in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1)))]
    quota = sum(x > 0 for x in q) / len(q)
    anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
    passa = sr > max(sr_spy, sr_tutto) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
    tot = lambda v: (1 + v).prod() - 1  # noqa: E731
    righe = ["# Prova 18 — risultati", "",
             f"Calcolato da `python -m stock.prove.p018` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P018_acquisti_dirigenti.md` (committate prima). Dal {gc.index.min()} al {gc.index.max()}. Nel conto: {len(tutte)} serie.", "",
             f"* Acquisti di dirigenti e consiglieri sopra 100'000 dollari, dopo la pulizia: {len(a)} (tutte le aziende americane); "
             f"di aziende dell'S&P 500 quel giorno: {len(eventi)}.",
             f"* Ingressi eseguiti {(e.etichetta == 'ingresso').sum()}; senza barra {r.senza_barra}; rifiutati {r.rifiutati}; "
             f"rimasti in mano dopo l'uscita dal listino: {r.bloccati or 'nessuno'}.", "",
             "| | Acquisti dei dirigenti | Tenere l'indice a pesi uguali | Tenere lo SPY |", "|---|---|---|---|",
             f"| Guadagno medio per evento rispetto allo SPY, con i costi (t) | {pe.mean() * 100:+.2f}% ({t_ev:.2f}) su {len(pe)}; meglio dello SPY {np.mean(pe > 0):.0%} | — | — |",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%} | {tot(gt):+.1%} | — |",
             f"| **1.** Sharpe annuo con i costi (deve battere le altre due colonne) | {sr:.2f} | {sr_tutto:.2f} | {sr_spy:.2f} |",
             f"| **2.** Sharpe corretto per i tentativi (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}) | — | — |",
             f"| t dello Sharpe (da leggere, contro 3) | {ast['t_sharpe']:.2f} | — | — |",
             f"| **3.** Sharpe annuo con i costi doppi (> 0) | {sr2:.2f} | — | — |",
             f"| **4.** Trimestri in guadagno (almeno 60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — | — |",
             f"| Anni in guadagno (da leggere) | {(anni > 0).sum()} su {len(anni)} | — | — |",
             f"| Perdita massima dal picco con i costi | {((1 + gc).cumprod() / (1 + gc).cumprod().cummax() - 1).min():.1%} | — | — |",
             f"| **Esito** | **{'passa la ricerca' if passa else 'bocciata'}** | | |"]
    (QUI / "P018_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
