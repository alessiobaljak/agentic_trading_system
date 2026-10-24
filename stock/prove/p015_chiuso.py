"""La prova 15 nel periodo chiuso (`P015_calma_e_agitazione.md`, ultima sezione; eccezione decisa dal proprietario il 24
ottobre 2026). Si lancia UNA volta, dopo il revisore.

    python -m stock.prove.p015_chiuso     # scrive stock/prove/P015_chiuso.md
"""
from __future__ import annotations

from datetime import UTC, datetime

from stock.dati import alpaca
from stock.prove.p001 import CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, salva_serie
from stock.prove.p002_chiuso import PRIMO, TRIMESTRI, ULTIMO, tenere
from stock.prove.p003 import prepara_titolo, rendimenti
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.portafoglio import simula_conto
from stock.strategie.tendenza import strategia_calma


def main():
    cal = list(alpaca.calendario("2024-11-01", "2026-09-30").index)
    righe = ["# Prova 15 — il periodo chiuso", "",
             f"Calcolato UNA volta da `python -m stock.prove.p015_chiuso` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC, dopo il sì del "
             "proprietario del 24 ottobre 2026 (eccezione: la prova non aveva passato l'asticella corretta per i tentativi). Regole ed "
             "esame scritti prima (`P015_calma_e_agitazione.md`).", "", "| | SPY | QQQ |", "|---|---|---|"]
    tab = {}
    for s in ("SPY", "QQQ"):
        df, rett, _ = prepara_titolo(s, ULTIMO, tipo_raw="1Day_raw_chiuso", tipo_az="azioni_chiuso")
        costi = Costi(mezzo_scarto=MEZZO_SCARTO[s], slittamento=0.5 * PB, interesse_debito_annuo=0.06, **IB_FISSO)

        def fabbrica():
            dentro = strategia_calma(s, cal, rett)
            return lambda giorno, storia, stato: dentro(giorno, storia, stato) if giorno >= PRIMO else []
        out = {}
        for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
            out[nome] = simula_conto({s: df}, fabbrica(), c, capitale=CAPITALE, leva_massima=1.5)
        g = {k: rendimenti(v.valore[(v.valore.index >= PRIMO) & (v.valore.index <= ULTIMO)]) for k, v in out.items()}
        gc = g["costi"]
        salva_serie(f"P015_{s}_chiuso", gc)
        bh_spy, bh_suo = tenere("SPY"), tenere(s)
        bh_spy, bh_suo = bh_spy[bh_spy.index >= PRIMO], bh_suo[bh_suo.index >= PRIMO]
        sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(g["costi doppi"]))
        sr_spy, sr_suo = annuo(asticella.sharpe(bh_spy)), annuo(asticella.sharpe(bh_suo))
        q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in TRIMESTRI]
        c1, c2, c3 = sr > max(sr_spy, sr_suo), sr2 > 0, sum(x > 0 for x in q) >= 4
        tot = lambda v: (1 + v).prod() - 1  # noqa: E731
        dd = lambda v: ((1 + v).cumprod() / (1 + v).cumprod().cummax() - 1).min()  # noqa: E731
        e = out["costi"].esecuzioni
        tab[s] = [f"{gc.index.min()} / {gc.index.max()} ({len(gc)} giorni; prima esecuzione {e['giorno'].min()})",
                  f"{len(e)} / {out['costi'].rifiutati}",
                  f"{tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%}", f"{tot(bh_suo):+.1%}",
                  f"{sr_spy:.2f} / {sr_suo:.2f}", f"{sr:.2f} → {'sì' if c1 else 'no'}", f"{sr2:.2f} → {'sì' if c2 else 'no'}",
                  f"{sum(x > 0 for x in q)} su 7 ({', '.join(f'{x:+.1%}' for x in q)}) → {'sì' if c3 else 'no'}",
                  f"{dd(gc):.1%} / {dd(bh_suo):.1%}",
                  f"**{'passa il periodo chiuso' if c1 and c2 and c3 else 'bocciata nel periodo chiuso'}**"]
    for k, nome in enumerate(["Giorni", "Ordini eseguiti / rifiutati", "Guadagno totale senza costi / con i costi / costi doppi",
                              "Guadagno del tenere lo stesso titolo", "Sharpe del tenere lo SPY / lo stesso titolo",
                              "**1.** Sharpe annuo con i costi (deve battere tutti e due)", "**2.** Sharpe con i costi doppi (> 0)",
                              "**3.** Trimestri in guadagno (almeno 4 su 7)", "Perdita massima dal picco: regola / tenere", "**Esito**"]):
        righe.append(f"| {nome} | {tab['SPY'][k]} | {tab['QQQ'][k]} |")
    (QUI / "P015_chiuso.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
