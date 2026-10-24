"""Calcolo della prova 4 (`P004_notte.md`): regole lì, scritte prima.

    python -m stock.prove.p004     # scrive stock/prove/P004_risultati.md
"""
from __future__ import annotations

from datetime import UTC, date, datetime

from stock.dati import alpaca, archivio, controlli
from stock.dati.integrazioni import azioni_complete
from stock.prove.p001 import (CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, carica_serie, comprare_e_tenere,
                              rendimenti_giornalieri, salva_serie)
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.motore import simula
from stock.strategie import notte
from stock.strategie import ultima_mezzora as um


def main():
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    finestre_prova = [f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))]
    ris = {}
    for s in ("SPY", "QQQ"):
        minuti = archivio.carica(s, "1Min_raw")
        seduta = notte.con_dividendi(um.solo_seduta(minuti, cal), azioni_complete(s, archivio.carica(s, "azioni")))
        problemi, _ = controlli.controlla_minuti(minuti, cal)
        esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
        seg = notte.prepara(seduta, cal, esclusi)
        costi = Costi(mezzo_scarto=MEZZO_SCARTO[s], slittamento=0.5 * PB, **IB_FISSO)
        out = {}
        for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
            r = simula(seduta, notte.strategia(seg), c, capitale=CAPITALE)
            out[nome] = {"r": r, "g": rendimenti_giornalieri(r.valore, CAPITALE)}
            print(s, nome, f"{r.valore.iloc[-1]:.0f}", flush=True)
        salva_serie(f"P004_{s}", out["costi"]["g"])
        ris[s] = out
    tutte = carica_serie()
    righe = ["# Prova 4 — risultati", "",
             f"Calcolato da `python -m stock.prove.p004` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             "`P004_notte.md` (committate prima). Nel conto dell'asticella: " + ", ".join(sorted(tutte)) + ".", "",
             "| | SPY | QQQ |", "|---|---|---|"]
    tab = {}
    for s in ("SPY", "QQQ"):
        o = ris[s]
        rc, gc = o["costi"]["r"], o["costi"]["g"]
        g0, g1 = gc.index.min(), gc.index.max()
        sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", g0, g1)))
        sr_suo = annuo(asticella.sharpe(comprare_e_tenere(s, g0, g1)))
        q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in finestre_prova]
        ast = asticella.sharpe_corretto(gc, tutte)
        sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(o["costi doppi"]["g"]))
        quota = sum(x > 0 for x in q) / len(q)
        e = rc.esecuzioni
        tab[s] = {
            "Notti tenute": f"{(e.etichetta == 'sera').sum()}",
            "Uscite in ritardo (barra mancante)": f"{(e.etichetta == 'mattina, in ritardo').sum()}",
            "Ordini rifiutati": f"{rc.rifiutati}",
            "Dividendi incassati": f"{rc.dividendi:,.0f} dollari",
            "Guadagno totale senza costi / con i costi / costi doppi":
                f"{o['senza costi']['r'].valore.iloc[-1] / CAPITALE - 1:+.1%} / {rc.valore.iloc[-1] / CAPITALE - 1:+.1%} / "
                f"{o['costi doppi']['r'].valore.iloc[-1] / CAPITALE - 1:+.1%}",
            "Costi pagati (commissioni + scarto)": f"{rc.commissioni:,.0f} + {rc.costo_scarto:,.0f} dollari",
            "Sharpe annuo senza costi": f"{annuo(asticella.sharpe(o['senza costi']['g'])):.2f}",
            "Sharpe annuo del comprare e tenere lo SPY / lo stesso titolo": f"{sr_spy:.2f} / {sr_suo:.2f}",
            "**1.** Sharpe annuo con i costi (deve battere tutti e due)": f"{sr:.2f}",
            "**2.** Sharpe corretto per i tentativi (soglia 0,95)": f"{ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']})",
            "t dello Sharpe (da leggere, contro 3)": f"{ast['t_sharpe']:.2f}",
            "**3.** Sharpe annuo, costi doppi (deve essere > 0)": f"{sr2:.2f}",
            "**4.** Trimestri in guadagno (almeno 60%)": f"{sum(x > 0 for x in q)} su {len(q)} ({quota:.0%})",
            "Perdita massima dal picco, con i costi": f"{((1 + gc).cumprod() / (1 + gc).cumprod().cummax() - 1).min():.1%}",
        }
        passa = sr > max(sr_spy, sr_suo) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
        tab[s]["**Esito**"] = "**passa la ricerca**" if passa else "**bocciata**"
    for k in tab["SPY"]:
        righe.append(f"| {k} | {tab['SPY'][k]} | {tab['QQQ'][k]} |")
    (QUI / "P004_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
