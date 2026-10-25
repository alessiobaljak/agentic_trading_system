"""Calcolo della prova 19 (`P019_contro_i_dirigenti.md`): il 2016-2024 solo da leggere, l'esito sul periodo chiuso.

    python -m stock.prove.p019     # scrive stock/prove/P019_risultati.md
"""
from __future__ import annotations

import math
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca, controlli
from stock.dati.dirigenti import acquisti
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, comprare_e_tenere, salva_serie
from stock.prove.p002_chiuso import PRIMO, TRIMESTRI, ULTIMO, tenere
from stock.prove.p003 import RADICE, prepara_titolo, rendimenti, scarti_misurati
from stock.prove.p011 import membri_dell_indice
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import dirigenti
from stock.universo.costruisci import cambi_di_nome


def carica(simboli, fino, tipo_raw, tipo_az):
    barre, rett = {}, {}
    for s in simboli:
        try:
            barre[s], rett[s], _ = prepara_titolo(s, fino, tipo_raw=tipo_raw, tipo_az=tipo_az)
        except Exception:
            pass
    return barre, rett


def costi_per(simboli, scarti, f):
    base = {}
    for s in simboli:
        c = (Costi(mezzo_scarto=scarti[s] / 2, slittamento=0.5 * PB, **IB_FISSO) if s in scarti
             else Costi(mezzo_scarto=5 * PB, slittamento=2 * PB, **IB_FISSO))
        base[s] = Costi(**{**c.__dict__, "prestito_annuo": 0.01, "interesse_debito_annuo": 0.06})
    if f == 0:
        return {s: Costi() for s in simboli}
    return base if f == 1 else {s: c.raddoppiati() for s, c in base.items()}


def calcola(dal, al, fino, tipo_raw, tipo_az, cal, primo=None):
    membri, _ = membri_dell_indice()
    cambi = cambi_di_nome()
    a0 = acquisti(dal, al)
    candidati = sorted({cambi.get(s, s) for s in a0["simbolo"]} | {"SPY"})
    barre, rett = carica(candidati, fino, tipo_raw, tipo_az)
    chiusure = {s: pd.Series(df["close"].to_numpy(), index=pd.Index(controlli.date_ny(df.index))) for s, df in barre.items()}
    a = acquisti(dal, al, chiusure=lambda s: chiusure.get(cambi.get(s, s)))
    a["simbolo"] = a["simbolo"].map(lambda s: cambi.get(s, s))
    a = a[[s in set(membri(d)) and s in barre for d, s in zip(a["deposito"], a["simbolo"])]]
    eventi = list(zip(a["deposito"], a["simbolo"], a["valore"]))
    scarti = scarti_misurati(RADICE / "dati" / "ESITO_CONTROLLI_UNIVERSO.md")
    out = {}
    for nome, f in (("costi", 1), ("costi doppi", 2), ("senza costi", 0)):
        out[nome] = simula_conto(barre, dirigenti.strategia_contro(eventi, cal, primo=primo), costi_per(list(barre), scarti, f),
                                 capitale=CAPITALE, leva_massima=2)
    e = out["costi"].esecuzioni
    spy = rett["SPY"]
    pe = []
    for s, x in e[e.simbolo != "SPY"].groupby("simbolo"):
        ing, usc = x[x.etichetta == "scoperto"], x[x.etichetta == "ricopertura"]
        for (_, i), (_, u) in zip(ing.iterrows(), usc.iterrows()):
            pe.append(u["prezzo"] / i["prezzo"] - 1 - (spy[u["giorno"]] / spy[i["giorno"]] - 1))
    return out, np.array(pe), len(eventi)


def main():
    righe = ["# Prova 19 — risultati", "",
             f"Calcolato da `python -m stock.prove.p019` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             "`P019_contro_i_dirigenti.md` (committate prima). **L'esito lo decide solo il periodo chiuso**; il 2016-2024 è da leggere.", ""]
    tot = lambda v: (1 + v).prod() - 1  # noqa: E731
    t_di = lambda p: p.mean() / p.std(ddof=1) * math.sqrt(len(p)) if len(p) > 1 else float("nan")  # noqa: E731
    # 1. il 2016-2024, da leggere
    cal = list(alpaca.calendario("2016-01-01", "2024-12-31").index)
    out, pe, n = calcola("2016-01-01", "2024-11-30", date(2024, 12, 31), "1Day_raw", "azioni", cal)
    gc = rendimenti(out["costi"].valore[out["costi"].valore.index >= out["costi"].esecuzioni["giorno"].min()])
    salva_serie("P019_contro_dirigenti", gc)
    bh = comprare_e_tenere("SPY", gc.index.min(), gc.index.max())
    righe += ["## Il 2016-2024 (solo da leggere)", "",
              f"* Eventi nell'S&P 500: {n}; scoperti eseguiti {(out['costi'].esecuzioni.etichetta == 'scoperto').sum()}; per evento il titolo "
              f"rispetto allo SPY {pe.mean() * 100:+.2f}% (t {t_di(pe):.2f}).",
              f"* Sharpe con i costi {annuo(asticella.sharpe(gc)):.2f} contro {annuo(asticella.sharpe(bh)):.2f} del tenere lo SPY; "
              f"guadagno {tot(gc):+.1%} contro {tot(bh):+.1%}.", ""]
    # 2. il periodo chiuso: l'esame
    cal_c = list(alpaca.calendario("2024-11-01", "2026-09-30").index)
    out, pe, n = calcola("2025-01-01", "2026-03-31", ULTIMO, "1Day_raw_chiuso", "azioni_chiuso", cal_c, primo=PRIMO)
    g = {k: rendimenti(v.valore[(v.valore.index >= PRIMO) & (v.valore.index <= ULTIMO)]) for k, v in out.items()}
    gc = g["costi"]
    salva_serie("P019_contro_dirigenti_chiuso", gc)
    bh = tenere("SPY")
    bh = bh[bh.index >= PRIMO]
    sr, sr_bh = annuo(asticella.sharpe(gc)), annuo(asticella.sharpe(bh))
    q = [float((1 + gc[(gc.index >= a) & (gc.index < b)]).prod() - 1) for a, b in TRIMESTRI]
    c1, c2, c3 = sr > sr_bh, tot(g["costi doppi"]) > tot(bh), sum(x > 0 for x in q) >= 4
    e = out["costi"].esecuzioni
    righe += ["## Il periodo chiuso (2 gennaio 2025 → 30 settembre 2026): l'esame", "",
              f"* Eventi nell'S&P 500 (depositi dal 2 gennaio 2025 al 31 marzo 2026): {n}; scoperti eseguiti {(e.etichetta == 'scoperto').sum()}; "
              f"rifiutati {out['costi'].rifiutati}; senza barra {out['costi'].senza_barra}.", "",
              "| | |", "|---|---|",
              f"| Per evento, il titolo rispetto allo SPY (deve essere negativo; t) | {pe.mean() * 100:+.2f}% ({t_di(pe):.2f}) su {len(pe)}; peggio dello SPY {np.mean(pe < 0):.0%} |",
              f"| Guadagno senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%} |",
              f"| Guadagno del tenere lo SPY | {tot(bh):+.1%} |",
              f"| **1.** Sharpe annuo con i costi (contro {sr_bh:.2f} del tenere lo SPY) | {sr:.2f} → {'sì' if c1 else 'no'} |",
              f"| **2.** Con i costi doppi guadagna più del tenere lo SPY | {tot(g['costi doppi']):+.2%} contro {tot(bh):+.2%} → {'sì' if c2 else 'no'} |",
              f"| **3.** Trimestri in guadagno (almeno 4 su 7) | {sum(x > 0 for x in q)} su 7 → {'sì' if c3 else 'no'} |",
              f"| **Esito** | **{'passa il periodo chiuso' if c1 and c2 and c3 else 'bocciata'}** |"]
    (QUI / "P019_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
