"""Calcolo della prova 12 (`P012_bassa_volatilita.md`): regole lì, scritte prima. Stesso programma della prova 11, regola diversa.

    python -m stock.prove.p012     # scrive stock/prove/P012_risultati.md
"""
from __future__ import annotations

from datetime import UTC, date, datetime

from stock.dati import alpaca
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import RADICE, prepara_titolo, rendimenti, scarti_misurati
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import fattori
from stock.strategie.rimbalzo import strategia_tenere_l_indice
from stock.prove.p011 import carica_tutti, costi_per, membri_dell_indice

def main():
    membri, simboli = membri_dell_indice()
    fino = date(2024, 12, 31)
    cal = list(alpaca.calendario("2016-01-01", "2024-12-31").index)
    barre, rett, senza = carica_tutti(simboli, fino)
    scarti = scarti_misurati(RADICE / "dati" / "ESITO_CONTROLLI_UNIVERSO.md")
    out = {}
    for nome, f in (("costi", 1), ("costi doppi", 2), ("senza costi", 0)):
        out[nome] = simula_conto(barre, fattori.strategia_classifica(membri, cal, rett, fattori.volatilita, i_piu_bassi=True), costi_per(list(barre), scarti, f), capitale=CAPITALE)
        print(nome, f"{out[nome].valore.iloc[-1]:.0f}", flush=True)
    tutto = simula_conto(barre, strategia_tenere_l_indice(membri, cal), costi_per(list(barre), scarti, 1), capitale=CAPITALE)
    r = out["costi"]
    primo = r.esecuzioni["giorno"].min()
    taglia = lambda v: v[v.index >= primo]  # noqa: E731
    g = {k: rendimenti(taglia(v.valore)) for k, v in out.items()}
    gc, gt = g["costi"], rendimenti(taglia(tutto.valore))
    salva_serie("P012_bassa_volatilita", gc)
    tutte = carica_serie()
    sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(g["costi doppi"]))
    sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", gc.index.min(), gc.index.max())))
    sr_tutto = annuo(asticella.sharpe(gt))
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1)
         for a, b in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1)))]
    quota = sum(x > 0 for x in q) / len(q)
    passa = sr > max(sr_spy, sr_tutto) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
    tot = lambda v: (1 + v).prod() - 1  # noqa: E731
    e = r.esecuzioni
    righe = ["# Prova 12 — risultati", "",
             f"Calcolato da `python -m stock.prove.p012` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di `P012_bassa_volatilita.md` "
             f"(committate prima). Dal {gc.index.min()} al {gc.index.max()}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Titoli dell'indice nel periodo: {len(simboli)}; senza prezzi su Alpaca: {len(senza)} ({', '.join(senza) or 'nessuno'}).",
             f"* Ordini eseguiti {len(e)} su {e['simbolo'].nunique()} titoli diversi; senza barra {r.senza_barra}; rifiutati {r.rifiutati}; "
             f"rimasti in mano dopo l'uscita dal listino: {r.bloccati or 'nessuno'}.",
             f"* Costi pagati: commissioni {r.commissioni:,.0f}, scarto e slittamento {r.costo_scarto:,.0f} dollari.", "",
             "| | Le 50 meno nervose | Tenere tutto l'indice a pesi uguali | Tenere lo SPY |", "|---|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%} | {tot(gt):+.1%} | — |",
             f"| Sharpe annuo senza costi | {annuo(asticella.sharpe(g['senza costi'])):.2f} | — | — |",
             f"| **1.** Sharpe annuo con i costi (deve battere le altre due colonne) | {sr:.2f} | {sr_tutto:.2f} | {sr_spy:.2f} |",
             f"| **2.** Sharpe corretto per i tentativi (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}) | — | — |",
             f"| t dello Sharpe (da leggere, contro 3) | {ast['t_sharpe']:.2f} | — | — |",
             f"| **3.** Sharpe annuo con i costi doppi (> 0) | {sr2:.2f} | — | — |",
             f"| **4.** Trimestri in guadagno (almeno 60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — | — |",
             f"| Perdita massima dal picco con i costi | {((1 + gc).cumprod() / (1 + gc).cumprod().cummax() - 1).min():.1%} | "
             f"{((1 + gt).cumprod() / (1 + gt).cumprod().cummax() - 1).min():.1%} | — |",
             f"| **Esito** | **{'passa la ricerca' if passa else 'bocciata'}** | | |"]
    (QUI / "P012_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
