"""Calcolo della prova 14 (`P014_leva_banca_centrale.md`): il 2016-2024 solo da leggere, l'esito sul periodo chiuso.

    python -m stock.prove.p014     # scrive stock/prove/P014_risultati.md
"""
from __future__ import annotations

from datetime import UTC, datetime

import numpy as np

from stock.dati import alpaca, archivio
from stock.dati.fomc import COMUNICATI, COMUNICATI_CHIUSO
from stock.dati.integrazioni import azioni_complete
from stock.prove.p001 import CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, comprare_e_tenere, rendimenti_giornalieri, salva_serie
from stock.prove.p002_chiuso import PRIMO, TRIMESTRI, ULTIMO, tenere
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.motore import simula
from stock.strategie import calendario as calen
from stock.strategie import notte
from stock.strategie import ultima_mezzora as um


def calcola(seduta, seg, s, inizio=0):
    costi = Costi(mezzo_scarto=MEZZO_SCARTO[s], slittamento=0.5 * PB, interesse_debito_annuo=0.06, **IB_FISSO)
    out = {}
    for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
        r = simula(seduta, calen.strategia_leva_finestre(seg, inizio=inizio), c, capitale=CAPITALE, leva_massima=1.5)
        out[nome] = (r, rendimenti_giornalieri(r.valore, CAPITALE))
    return out


def main():
    righe = ["# Prova 14 — risultati", "",
             f"Calcolato da `python -m stock.prove.p014` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             "`P014_leva_banca_centrale.md` (committate prima). **L'esito lo decide solo il periodo chiuso**; il 2016-2024 è da leggere.", "",
             "## Il 2016-2024 (solo da leggere)", "", "| | SPY | QQQ |", "|---|---|---|"]
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    tab = {}
    for s in ("SPY", "QQQ"):
        seduta = notte.con_dividendi(um.solo_seduta(archivio.carica(s, "1Min_raw"), cal), azioni_complete(s, archivio.carica(s, "azioni")))
        seg = calen.prepara_prima_della_fed(seduta, cal, COMUNICATI, set())
        out = calcola(seduta, seg, s)
        g = out["costi"][1]
        salva_serie(f"P014_{s}", g)
        g0, g1 = g.index.min(), g.index.max()
        bh = comprare_e_tenere(s, g0, g1)
        tot = lambda v: (1 + v).prod() - 1  # noqa: E731
        tab[s] = [f"{annuo(asticella.sharpe(g)):.2f}", f"{annuo(asticella.sharpe(comprare_e_tenere('SPY', g0, g1))):.2f} / {annuo(asticella.sharpe(bh)):.2f}",
                  f"{tot(g):+.1%} / {tot(bh):+.1%}", f"{out['costi'][0].prestito:,.0f} dollari"]
    for k, nome in enumerate(["Sharpe annuo con i costi", "Sharpe del tenere lo SPY / lo stesso titolo",
                              "Guadagno totale con i costi / del tenere lo stesso titolo", "Interessi pagati sul prestito"]):
        righe.append(f"| {nome} | {tab['SPY'][k]} | {tab['QQQ'][k]} |")
    cal_c = alpaca.calendario("2024-11-01", "2026-09-30")
    righe += ["", "## Il periodo chiuso (2 gennaio 2025 → 30 settembre 2026): l'esame", "", "| | SPY | QQQ |", "|---|---|---|"]
    tab = {}
    for s in ("SPY", "QQQ"):
        seduta = notte.con_dividendi(um.solo_seduta(archivio.carica(s, "1Min_raw_chiuso"), cal_c),
                                     azioni_complete(s, archivio.carica(s, "azioni_chiuso")))
        seg = calen.prepara_prima_della_fed(seduta, cal_c, COMUNICATI_CHIUSO, set())
        giorni = np.array(seduta.index.tz_convert("America/New_York").date)
        inizio = int(np.argmax(giorni >= PRIMO))
        out = calcola(seduta, seg, s, inizio=inizio)
        g = {k: v[1][(v[1].index >= PRIMO) & (v[1].index <= ULTIMO)] for k, v in out.items()}
        gc = g["costi"]
        salva_serie(f"P014_{s}_chiuso", gc)
        bh_suo, bh_spy = tenere(s), tenere("SPY")
        bh_suo, bh_spy = bh_suo[bh_suo.index >= PRIMO], bh_spy[bh_spy.index >= PRIMO]
        tot = lambda v: (1 + v).prod() - 1  # noqa: E731
        sr = annuo(asticella.sharpe(gc))
        sr_spy, sr_suo = annuo(asticella.sharpe(bh_spy)), annuo(asticella.sharpe(bh_suo))
        q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in TRIMESTRI]
        c1 = sr > max(sr_spy, sr_suo)
        c2 = tot(g["costi doppi"]) > tot(bh_suo)
        c3 = sum(x > 0 for x in q) >= 4
        e = out["costi"][0].esecuzioni
        e = e[e["t"].dt.tz_convert("America/New_York").dt.date >= PRIMO]
        tab[s] = [f"{tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%}", f"{tot(bh_suo):+.1%}",
                  f"{sr_spy:.2f} / {sr_suo:.2f}", f"{sr:.2f} → {'sì' if c1 else 'no'}",
                  f"{tot(g['costi doppi']):+.2%} contro {tot(bh_suo):+.2%} → {'sì' if c2 else 'no'}",
                  f"{sum(x > 0 for x in q)} su 7 → {'sì' if c3 else 'no'}", f"{(e.etichetta == 'leva').sum()}",
                  f"**{'passa il periodo chiuso' if c1 and c2 and c3 else 'bocciata'}**"]
    for k, nome in enumerate(["Guadagno totale senza costi / con i costi / costi doppi", "Guadagno del tenere lo stesso titolo",
                              "Sharpe del tenere lo SPY / lo stesso titolo", "**1.** Sharpe annuo con i costi (deve battere tutti e due)",
                              "**2.** Con i costi doppi guadagna più del tenere", "**3.** Trimestri in guadagno (almeno 4 su 7)",
                              "Finestre con la leva eseguite", "**Esito**"]):
        righe.append(f"| {nome} | {tab['SPY'][k]} | {tab['QQQ'][k]} |")
    (QUI / "P014_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
