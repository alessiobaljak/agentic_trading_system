"""Calcolo della prova 9 (`P009_giorni_speciali.md`): il 2016-2024 solo da leggere, l'esito sul periodo chiuso.

    python -m stock.prove.p009     # scrive stock/prove/P009_risultati.md
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np

from stock.dati import alpaca, archivio
from stock.dati.fomc import COMUNICATI, COMUNICATI_CHIUSO
from stock.dati.integrazioni import azioni_complete
from stock.prove.p001 import (CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, comprare_e_tenere,
                              rendimenti_giornalieri, salva_serie)
from stock.prove.p002_chiuso import PRIMO, TRIMESTRI, ULTIMO, tenere
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.motore import simula
from stock.strategie import calendario as calen
from stock.strategie import notte
from stock.strategie import ultima_mezzora as um


def calcola(seduta, seg, s):
    costi = Costi(mezzo_scarto=MEZZO_SCARTO[s], slittamento=0.5 * PB, **IB_FISSO)
    out = {}
    for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
        r = simula(seduta, calen.strategia_dentro(seg), c, capitale=CAPITALE)
        out[nome] = (r, rendimenti_giornalieri(r.valore, CAPITALE))
    return out


def main():
    righe = ["# Prova 9 — risultati", "",
             f"Calcolato da `python -m stock.prove.p009` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             "`P009_giorni_speciali.md` (committate prima). **L'esito lo decide solo il periodo chiuso**; il 2016-2024 è da leggere.", ""]
    # 1. il 2016-2024, solo da leggere
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    righe += ["## Il 2016-2024 (solo da leggere)", "", "| | SPY | QQQ |", "|---|---|---|"]
    tab = {}
    for s in ("SPY", "QQQ"):
        seduta = notte.con_dividendi(um.solo_seduta(archivio.carica(s, "1Min_raw"), cal), azioni_complete(s, archivio.carica(s, "azioni")))
        seg = calen.prepara_giorni_speciali(seduta, cal, COMUNICATI)
        out = calcola(seduta, seg, s)
        g = out["costi"][1]
        salva_serie(f"P009_{s}", g)
        tab[s] = [f"{np.mean(seg['dentro']):.0%}", f"{annuo(asticella.sharpe(out['senza costi'][1])):.2f}", f"{annuo(asticella.sharpe(g)):.2f}",
                  f"{annuo(asticella.sharpe(comprare_e_tenere('SPY', g.index.min(), g.index.max()))):.2f} / "
                  f"{annuo(asticella.sharpe(comprare_e_tenere(s, g.index.min(), g.index.max()))):.2f}",
                  f"{out['costi'][0].valore.iloc[-1] / CAPITALE - 1:+.1%}"]
    for k, nome in enumerate(["Parte del tempo investita (barre)", "Sharpe annuo senza costi", "Sharpe annuo con i costi",
                              "Sharpe del tenere lo SPY / lo stesso titolo", "Guadagno totale con i costi"]):
        righe.append(f"| {nome} | {tab['SPY'][k]} | {tab['QQQ'][k]} |")
    # 2. il periodo chiuso: l'esame
    cal_c = alpaca.calendario("2024-11-01", "2026-09-30")
    righe += ["", "## Il periodo chiuso (2 gennaio 2025 → 30 settembre 2026): l'esame", "", "| | SPY | QQQ |", "|---|---|---|"]
    tab = {}
    for s in ("SPY", "QQQ"):
        seduta = notte.con_dividendi(um.solo_seduta(archivio.carica(s, "1Min_raw_chiuso"), cal_c),
                                     azioni_complete(s, archivio.carica(s, "azioni_chiuso")))
        seg = calen.prepara_giorni_speciali(seduta, cal_c, COMUNICATI_CHIUSO)
        seg["dentro"] &= np.array(seduta.index.tz_convert("America/New_York").date) >= PRIMO
        out = calcola(seduta, seg, s)
        g = {k: v[1][(v[1].index >= PRIMO) & (v[1].index <= ULTIMO)] for k, v in out.items()}
        gc = g["costi"]
        salva_serie(f"P009_{s}_chiuso", gc)
        sr, sr2 = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(g["costi doppi"]))
        sr_spy, sr_suo = annuo(asticella.sharpe(tenere("SPY"))), annuo(asticella.sharpe(tenere(s)))
        q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in TRIMESTRI]
        c1, c2, c3 = sr > max(sr_spy, sr_suo), sr2 > 0, sum(x > 0 for x in q) >= 4
        tot = lambda v: (1 + v).prod() - 1  # noqa: E731
        tab[s] = [f"{tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%}",
                  f"{annuo(asticella.sharpe(g['senza costi'])):.2f}", f"{sr_spy:.2f} / {sr_suo:.2f}",
                  f"{sr:.2f} → {'sì' if c1 else 'no'}", f"{sr2:.2f} → {'sì' if c2 else 'no'}",
                  f"{sum(x > 0 for x in q)} su 7 ({', '.join(f'{x:+.1%}' for x in q)}) → {'sì' if c3 else 'no'}",
                  f"**{'passa il periodo chiuso' if c1 and c2 and c3 else 'bocciata'}**"]
    for k, nome in enumerate(["Guadagno totale senza costi / con i costi / costi doppi", "Sharpe annuo senza costi",
                              "Sharpe del tenere lo SPY / lo stesso titolo", "**1.** Sharpe annuo con i costi (deve battere tutti e due)",
                              "**2.** Sharpe annuo con i costi doppi (> 0)", "**3.** Trimestri in guadagno (almeno 4 su 7)", "**Esito**"]):
        righe.append(f"| {nome} | {tab['SPY'][k]} | {tab['QQQ'][k]} |")
    (QUI / "P009_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
