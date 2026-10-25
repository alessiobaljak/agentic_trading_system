"""Calcolo della prova 17 (`P017_prima_candela.md`): regole lì, scritte prima.

    python -m stock.prove.p017     # scrive stock/prove/P017_risultati.md
"""
from __future__ import annotations

from datetime import UTC, date, datetime

from stock.dati import alpaca, archivio, controlli
from stock.prove.p001 import (CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, carica_serie, comprare_e_tenere,
                              rendimenti_giornalieri, salva_serie)
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.motore import simula
from stock.strategie import prima_candela as pc
from stock.strategie import ultima_mezzora as um

VARIANTI = (5.0, 20.0, None)


def main():
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    finestre_prova = [f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))]
    ris = {}
    for s in ("SPY", "QQQ"):
        minuti = archivio.carica(s, "1Min_raw")
        seduta = um.solo_seduta(minuti, cal)
        problemi, _ = controlli.controlla_minuti(minuti, cal)
        esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
        costi = Costi(mezzo_scarto=MEZZO_SCARTO[s], slittamento=0.5 * PB, **IB_FISSO)
        for n in (5, 15):
            seg = pc.prepara(seduta, cal, esclusi, n)
            out = {}
            for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
                r = simula(seduta, pc.strategia(seg), c, capitale=CAPITALE)
                out[nome] = (r, rendimenti_giornalieri(r.valore, CAPITALE))
            var = {}
            for m in VARIANTI:
                r = simula(seduta, pc.strategia(seg, multiplo=m), costi, capitale=CAPITALE)
                var[m] = annuo(asticella.sharpe(rendimenti_giornalieri(r.valore, CAPITALE)))
            salva_serie(f"P017_{s}_{n}m", out["costi"][1])
            ris[(s, n)] = (out, var)
            print(s, n, f"{out['costi'][0].valore.iloc[-1]:.0f}", flush=True)
    tutte = carica_serie()
    righe = ["# Prova 17 — risultati", "",
             f"Calcolato da `python -m stock.prove.p017` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P017_prima_candela.md` (committate prima). Nel conto dell'asticella: {len(tutte)} serie.", "",
             "| | SPY 5 min | QQQ 5 min | SPY 15 min | QQQ 15 min |", "|---|---|---|---|---|"]
    chiavi = [("SPY", 5), ("QQQ", 5), ("SPY", 15), ("QQQ", 15)]
    tab = {}
    for k in chiavi:
        s = k[0]
        out, var = ris[k]
        rc, gc = out["costi"]
        g0, g1 = gc.index.min(), gc.index.max()
        sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", g0, g1)))
        sr_suo = annuo(asticella.sharpe(comprare_e_tenere(s, g0, g1)))
        sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(out["costi doppi"][1]))
        ast = asticella.sharpe_corretto(gc, tutte)
        q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in finestre_prova]
        quota = sum(x > 0 for x in q) / len(q)
        e = rc.esecuzioni
        anni = (1 + gc).groupby(pd_anno(gc.index)).prod() - 1
        passa = sr > max(sr_spy, sr_suo) and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
        tab[k] = [f"{(e.etichetta == 'ingresso').sum()}",
                  f"{(e.etichetta == 'stop').sum()} / {(e.etichetta == 'obiettivo').sum()} / {(e.etichetta == 'chiusura').sum()}",
                  f"{out['senza costi'][0].valore.iloc[-1] / CAPITALE - 1:+.1%} / {rc.valore.iloc[-1] / CAPITALE - 1:+.1%} / "
                  f"{out['costi doppi'][0].valore.iloc[-1] / CAPITALE - 1:+.1%}",
                  f"{annuo(asticella.sharpe(out['senza costi'][1])):.2f}", f"{sr_spy:.2f} / {sr_suo:.2f}", f"{sr:.2f}",
                  f"{ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']})", f"{sr2:.2f}", f"{sum(x > 0 for x in q)} su 32 ({quota:.0%})",
                  f"{(anni > 0).sum()} su {len(anni)}",
                  " / ".join(f"{var[m]:.2f}" for m in VARIANTI),
                  f"**{'passa la ricerca' if passa else 'bocciata'}**"]
    nomi = ["Giorni con un ingresso", "Uscite: stop / obiettivo / chiusura", "Guadagno senza costi / con i costi / costi doppi",
            "Sharpe annuo senza costi", "Sharpe del tenere lo SPY / lo stesso titolo", "**1.** Sharpe annuo con i costi",
            "**2.** Sharpe corretto (soglia 0,95)", "**3.** Sharpe con i costi doppi (> 0)", "**4.** Trimestri in guadagno (60%)",
            "Anni in guadagno (da leggere)", "Robustezza, Sharpe con i costi: obiettivo 5R / 20R / nessuno (da leggere)", "**Esito**"]
    for j, nome in enumerate(nomi):
        righe.append(f"| {nome} | " + " | ".join(tab[k][j] for k in chiavi) + " |")
    (QUI / "P017_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


def pd_anno(indice):
    import pandas as pd
    return pd.Index([d.year for d in indice])


if __name__ == "__main__":
    main()
