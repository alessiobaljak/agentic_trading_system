"""Calcolo della prova 5 (`P005_tendenza.md`): regole lì, scritte prima.

    python -m stock.prove.p005     # scrive stock/prove/P005_risultati.md
"""
from __future__ import annotations

from datetime import UTC, date, datetime

from stock.dati import alpaca
from stock.prove.p001 import (CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, carica_serie, comprare_e_tenere,
                              salva_serie)
from stock.prove.p003 import prepara_titolo, rendimenti
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import tendenza


def main():
    esegui("5", "P005_tendenza.md", lambda s, cal, rett: tendenza.strategia(s, cal, rett),
           lambda rett, esecuzioni: rett.index[tendenza.SEDUTE])


def esegui(numero: str, regole: str, fabbrica, primo_giorno):
    """Una prova sull'indice con il simulatore a più titoli. `fabbrica(simbolo, calendario, rettificata)` dà la
    strategia; `primo_giorno(rettificata, esecuzioni)` il giorno da cui parte la serie."""
    cal = list(alpaca.calendario("2016-01-01", "2024-12-31").index)
    finestre_prova = [f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))]
    ris = {}
    for s in ("SPY", "QQQ"):
        df, rett, _ = prepara_titolo(s, date(2024, 12, 31))
        costi = Costi(mezzo_scarto=MEZZO_SCARTO[s], slittamento=0.5 * PB, **IB_FISSO)
        out = {}
        for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
            out[nome] = simula_conto({s: df}, fabbrica(s, cal, rett), c, capitale=CAPITALE)
            print(s, nome, f"{out[nome].valore.iloc[-1]:.0f}", flush=True)
        primo = primo_giorno(rett, out["costi"].esecuzioni)
        g = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
        salva_serie(f"P00{numero}_{s}", g["costi"])
        ris[s] = (out, g)
    tutte = carica_serie()
    righe = [f"# Prova {numero} — risultati", "",
             f"Calcolato da `python -m stock.prove.p00{numero}` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`{regole}` (committate prima). Nel conto dell'asticella: " + ", ".join(sorted(tutte)) + ".", "",
             "| | SPY | QQQ |", "|---|---|---|"]
    tab = {}
    for s in ("SPY", "QQQ"):
        out, g = ris[s]
        gc = g["costi"]
        sr_spy = annuo(asticella.sharpe(comprare_e_tenere("SPY", gc.index.min(), gc.index.max())))
        sr_suo = annuo(asticella.sharpe(comprare_e_tenere(s, gc.index.min(), gc.index.max())))
        sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(g["costi doppi"]))
        ast = asticella.sharpe_corretto(gc, tutte)
        q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in finestre_prova]
        quota = sum(x > 0 for x in q) / len(q)
        e = out["costi"].esecuzioni
        tot = lambda v: (1 + v).prod() - 1  # noqa: E731
        fuori = (e.quantita < 0).sum()
        tab[s] = {
            "Dal / al": f"{gc.index.min()} / {gc.index.max()}",
            "Ordini eseguiti (uscite dal mercato)": f"{len(e)} ({fuori})",
            "Guadagno totale senza costi / con i costi / costi doppi":
                f"{tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%}",
            "Guadagno del comprare e tenere lo stesso titolo": f"{tot(comprare_e_tenere(s, gc.index.min(), gc.index.max())):+.1%}",
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
    (QUI / f"P00{numero}_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
