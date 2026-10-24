"""Calcolo della prova 2 (`P002_zona_di_rumore.md`): regole lì, scritte prima.

    python -m stock.prove.p002     # scrive stock/prove/P002_risultati.md
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np

from stock.dati import alpaca, archivio, controlli
from stock.prove.p001 import (CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, carica_serie, comprare_e_tenere,
                              rendimenti_giornalieri, salva_serie)
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.motore import simula
from stock.strategie import ultima_mezzora as um
from stock.strategie import zona_di_rumore as zr


def main():
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    finestre_prova = [f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))]
    ris = {}
    for s in ("SPY", "QQQ"):
        minuti = archivio.carica(s, "1Min_raw")
        seduta = um.solo_seduta(minuti, cal)
        problemi, _ = controlli.controlla_minuti(minuti, cal)
        esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
        seg = zr.prepara(seduta, cal, esclusi)
        costi = Costi(mezzo_scarto=MEZZO_SCARTO[s], slittamento=0.5 * PB, **IB_FISSO)
        out = {}
        for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
            r = simula(seduta, zr.strategia(seg), c, capitale=CAPITALE)
            out[nome] = {"r": r, "g": rendimenti_giornalieri(r.valore, CAPITALE)}
            print(s, nome, f"{r.valore.iloc[-1]:.0f}", flush=True)
        salva_serie(f"P002_{s}", out["costi"]["g"])
        giorni_validi = len({d for d, x in zip(seduta.index.tz_convert("America/New_York").date, seg["decisione"]) if x})
        ris[s] = {"out": out, "giorni_validi": giorni_validi}
    tutte = carica_serie()
    righe = ["# Prova 2 — risultati", "",
             f"Calcolato da `python -m stock.prove.p002` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             "`P002_zona_di_rumore.md` (committate prima). Nel conto dell'asticella: " + ", ".join(sorted(tutte)) + ".", "",
             "| | SPY | QQQ |", "|---|---|---|"]
    tab = {}
    for s in ("SPY", "QQQ"):
        o = ris[s]["out"]
        rc, gc = o["costi"]["r"], o["costi"]["g"]
        g0, g1 = gc.index.min(), gc.index.max()
        sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", g0, g1)))
        sr_suo = annuo(asticella.sharpe(comprare_e_tenere(s, g0, g1)))
        q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in finestre_prova]
        ast = asticella.sharpe_corretto(gc, tutte)
        e = rc.esecuzioni
        sr = annuo(asticella.sharpe(gc))
        sr2 = annuo(asticella.sharpe(o["costi doppi"]["g"]))
        quota_q = sum(x > 0 for x in q) / len(q)
        giorni_op = e[e.etichetta == "fine giornata"].shape[0]
        tab[s] = {
            "Giorni in cui la regola poteva operare": f"{ris[s]['giorni_validi']}",
            "Giorni con almeno un'operazione": f"{giorni_op}",
            "Ordini eseguiti (in media per giorno operato)": f"{len(e)} ({len(e) / max(giorni_op, 1):.1f})",
            "Ordini rifiutati": f"{rc.rifiutati}",
            "Guadagno totale, senza costi": f"{o['senza costi']['r'].valore.iloc[-1] / CAPITALE - 1:+.1%}",
            "Guadagno totale, con i costi": f"{rc.valore.iloc[-1] / CAPITALE - 1:+.1%}",
            "Guadagno totale, costi doppi": f"{o['costi doppi']['r'].valore.iloc[-1] / CAPITALE - 1:+.1%}",
            "Costi pagati (commissioni + scarto)": f"{rc.commissioni:,.0f} + {rc.costo_scarto:,.0f} dollari",
            "Sharpe annuo, senza costi": f"{annuo(asticella.sharpe(o['senza costi']['g'])):.2f}",
            "Sharpe annuo del comprare e tenere lo SPY / lo stesso titolo": f"{sr_spy:.2f} / {sr_suo:.2f}",
            "**1.** Sharpe annuo con i costi (deve battere tutti e due)": f"{sr:.2f}",
            "**2.** Sharpe corretto per i tentativi (soglia 0,95)": f"{ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']})",
            "t dello Sharpe (da leggere, contro 3)": f"{ast['t_sharpe']:.2f}",
            "**3.** Sharpe annuo, costi doppi (deve essere > 0)": f"{sr2:.2f}",
            "**4.** Trimestri in guadagno (almeno 60%)": f"{sum(x > 0 for x in q)} su {len(q)} ({quota_q:.0%})",
            "Perdita massima dal picco, con i costi": f"{((1 + gc).cumprod() / (1 + gc).cumprod().cummax() - 1).min():.1%}",
        }
        passa = sr > max(sr_spy, sr_suo) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota_q >= 0.6
        tab[s]["**Esito**"] = "**passa la ricerca**" if passa else "**bocciata**"
    for k in tab["SPY"]:
        righe.append(f"| {k} | {tab['SPY'][k]} | {tab['QQQ'][k]} |")
    (QUI / "P002_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
