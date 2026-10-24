"""Calcolo della prova 8 (`P008_usciti_dall_indice.md`): regole lì, scritte prima.

    python -m stock.prove.p008     # scrive stock/prove/P008_risultati.md
"""
from __future__ import annotations

import math
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np

from stock.dati import alpaca, archivio
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import prepara_titolo, rendimenti
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import usciti
from stock.universo.costruisci import carica_composizione

INIZIO, FINE = datetime(2016, 1, 1, 5, tzinfo=UTC), datetime(2025, 1, 1, 5, tzinfo=UTC)


def main():
    comp = carica_composizione(Path.home() / "stock_dati" / "sp500_storico.csv")
    eventi = usciti.eventi_di_uscita(comp, date(2016, 5, 1), date(2024, 11, 30))
    cal = list(alpaca.calendario("2016-01-01", "2024-12-31").index)
    barre, senza_dati = {}, []
    for d, t in eventi:
        if t in barre or t in senza_dati:
            continue
        raw = archivio.carica(t, "1Day_raw")
        if raw is None or raw.empty:
            senza_dati.append(t)
            continue
        if archivio.carica(t, "azioni") is None:
            archivio.salva(alpaca.azioni_societarie(t, INIZIO, FINE), t, "azioni")
        barre[t], _, _ = prepara_titolo(t, date(2024, 12, 31))
    eventi_validi = [(d, t) for d, t in eventi if t in barre]
    base = Costi(mezzo_scarto=10 * PB, slittamento=5 * PB, **IB_FISSO)
    out = {}
    for nome, c in (("costi", base), ("costi doppi", base.raddoppiati()), ("senza costi", Costi())):
        out[nome] = simula_conto(barre, usciti.strategia(eventi_validi, cal), c, capitale=CAPITALE)
        print(nome, f"{out[nome].valore.iloc[-1]:.0f}", flush=True)
    r = out["costi"]
    primo = r.esecuzioni["giorno"].min()
    g = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
    gc = g["costi"]
    salva_serie("P008_usciti", gc)
    tutte = carica_serie()
    e = r.esecuzioni
    per_evento = []
    for t, x in e.groupby("simbolo"):
        ing = x[x.etichetta == "ingresso"]["prezzo"].to_numpy()
        usc = x[x.etichetta == "uscita"]["prezzo"].to_numpy()
        per_evento += list(usc[: len(ing)] / ing[: len(usc)] - 1)
    pe = np.array(per_evento)
    t_ev = pe.mean() / pe.std(ddof=1) * math.sqrt(len(pe))
    sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(g["costi doppi"]))
    sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", gc.index.min(), gc.index.max())))
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1)
         for a, b in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1)))]
    quota = sum(x > 0 for x in q) / len(q)
    passa = sr > sr_spy and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
    tot = lambda v: (1 + v).prod() - 1  # noqa: E731
    righe = ["# Prova 8 — risultati", "",
             f"Calcolato da `python -m stock.prove.p008` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P008_usciti_dall_indice.md` (committate prima). Dal {gc.index.min()} al {gc.index.max()}. Nel conto dell'asticella: "
             + ", ".join(sorted(tutte)) + ".", "",
             f"* Uscite dall'indice nel periodo: {len(eventi)}; titoli senza prezzi su Alpaca: {len(senza_dati)}; ingressi eseguiti "
             f"{(e.etichetta == 'ingresso').sum()}; uscite eseguite {(e.etichetta == 'uscita').sum()}; ordini senza barra "
             f"{r.senza_barra} (titoli spariti dal listino o senza scambi quel giorno); rimasti in mano: {r.bloccati or 'nessuno'}.",
             f"* Costi pagati: commissioni {r.commissioni:,.0f}, scarto e slittamento {r.costo_scarto:,.0f} dollari.", "",
             "| | Usciti dall'indice |", "|---|---|",
             f"| Guadagno medio per evento con i costi (t) | {pe.mean() * 100:+.2f}% ({t_ev:.2f}) su {len(pe)}; in guadagno {np.mean(pe > 0):.0%} |",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%} |",
             f"| Sharpe annuo senza costi | {annuo(asticella.sharpe(g['senza costi'])):.2f} |",
             f"| **1.** Sharpe annuo con i costi (contro {sr_spy:.2f} del tenere lo SPY) | {sr:.2f} |",
             f"| **2.** Sharpe corretto per i tentativi (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}) |",
             f"| t dello Sharpe (da leggere, contro 3) | {ast['t_sharpe']:.2f} |",
             f"| **3.** Sharpe annuo con i costi doppi (> 0) | {sr2:.2f} |",
             f"| **4.** Trimestri in guadagno (almeno 60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) |",
             f"| Perdita massima dal picco con i costi | {((1 + gc).cumprod() / (1 + gc).cumprod().cummax() - 1).min():.1%} |",
             f"| **Esito** | **{'passa la ricerca' if passa else 'bocciata'}** |"]
    (QUI / "P008_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
