"""Calcolo della prova 24 (`P024_vendite_allo_scoperto.md`): regole lì, scritte prima.

    python -m stock.prove.p024     # scrive stock/prove/P024_risultati.md
"""
from __future__ import annotations

from dataclasses import replace
from datetime import UTC, date, datetime

import pandas as pd

from stock.dati import controlli, finra
from stock.prove.p001 import CAPITALE, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import RADICE, prepara_titolo, rendimenti, scarti_misurati
from stock.prove.p011 import carica_tutti, costi_per, membri_dell_indice
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie.affollate import giorni_per_ricomprare, strategia_affollate
from stock.universo.costruisci import cambi_di_nome

PRESTITO = 0.005
INTERESSE = 0.05
LEVA = {"A": 1.0, "B": 1.35}


def costi_con_prestito(simboli, scarti, f):
    base = costi_per(simboli, scarti, f)
    if f == 0:
        return base
    return {s: replace(c, prestito_annuo=PRESTITO * f, interesse_debito_annuo=INTERESSE * f) for s, c in base.items()}


def main():
    membri, simboli = membri_dell_indice()
    fino = date(2024, 12, 31)
    barre, rett, senza = carica_tutti(simboli, fino)
    barre["SPY"], rett["SPY"], _ = prepara_titolo("SPY", fino)
    # il calendario dai giorni con la barra dello SPY (le chiavi di Alpaca non sono più nell'ambiente delle sessioni dall'11 nov 2026)
    cal = sorted(controlli.date_ny(barre["SPY"].index))
    scarti = scarti_misurati(RADICE / "dati" / "ESITO_CONTROLLI_UNIVERSO.md")
    dati = finra.carica()
    dati = dati[dati["settlementDate"] <= fino]
    gpr = giorni_per_ricomprare(dati, cambi_di_nome())
    finestre_prova = [f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))]
    ris = {}
    for v in ("A", "B"):
        out, diario = {}, []
        for nome, f in (("costi", 1), ("costi doppi", 2), ("senza costi", 0)):
            out[nome] = simula_conto(barre, strategia_affollate(membri, cal, rett, gpr, v, diario if f == 1 else None),
                                     costi_con_prestito(list(barre), scarti, f), capitale=CAPITALE, leva_massima=LEVA[v])
            print(v, nome, f"{out[nome].valore.iloc[-1]:.0f}", flush=True)
        primo = out["costi"].esecuzioni["giorno"].min()
        g = {k: rendimenti(r.valore[r.valore.index >= primo]) for k, r in out.items()}
        salva_serie(f"P024_{v}", g["costi"])
        ris[v] = (out, g, diario)
    tutte = carica_serie()
    righe = ["# Prova 24 — risultati", "",
             f"Calcolato da `python -m stock.prove.p024` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P024_vendite_allo_scoperto.md` (committate prima). Nel conto dell'asticella: {len(tutte)} serie. Titoli senza prezzi: "
             f"{len(senza)}. Date di FINRA: {len(gpr)} (dal {min(gpr)} al {max(gpr)}).", "",
             "| | A: lungo e corto | B: SPY meno gli affollati |", "|---|---|---|"]
    celle = {}
    for v in ("A", "B"):
        out, g, diario = ris[v]
        gc = g["costi"]
        a, b = gc.index.min(), gc.index.max()
        spy = comprare_e_tenere("SPY", a, b)
        sr, sr2, sr0 = (annuo(asticella.sharpe(g[k])) for k in ("costi", "costi doppi", "senza costi"))
        sr_spy = annuo(asticella.sharpe(spy))
        ast = asticella.sharpe_corretto(gc, tutte)
        q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1) for x, y in finestre_prova if x >= a]
        quota = sum(t > 0 for t in q) / len(q) if q else 0.0
        passa = sr > sr_spy and ast["sharpe_corretto"] >= 0.95 and sr2 > 0 and quota >= 0.6
        tot = lambda x: (1 + x).prod() - 1  # noqa: E731
        anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
        r = out["costi"]
        d = pd.DataFrame(diario)
        perdita = ((1 + gc).cumprod() / (1 + gc).cumprod().cummax() - 1).min()
        celle[v] = [
            f"{a} → {b} ({len(gc)} giorni, {len(d)} decisioni)",
            f"{d['corti'].mean():.0f} corti, {d['lunghi'].mean():.0f} lunghi in media" if len(d) else "—",
            f"{len(r.esecuzioni)}",
            f"{tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / {tot(g['costi doppi']):+.1%} (SPY {tot(spy):+.1%})",
            f"{r.commissioni:,.0f} + {r.costo_scarto:,.0f}",
            f"{sr0:.2f}", f"**{sr:.2f}** (SPY {sr_spy:.2f})", f"{ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f})",
            f"{sr2:.2f}", f"{sum(t > 0 for t in q)} su {len(q)} ({quota:.0%})", f"{perdita:.1%}",
            " ".join(f"{y}: {x:+.1%}" for y, x in anni.items()),
            f"**{'passa la ricerca' if passa else 'bocciata'}**"]
    nomi = ["Periodo", "Titoli per lato", "Ordini eseguiti", "Guadagno senza costi / con i costi / costi doppi",
            "Costi pagati (commissioni + scarto e slittamento, dollari)", "Sharpe annuo senza costi", "**1.** Sharpe annuo con i costi",
            "**2.** Sharpe corretto (soglia 0,95)", "**3.** Sharpe con i costi doppi (> 0)", "**4.** Trimestri in guadagno (60%)",
            "Perdita massima dal picco (da leggere)", "Anno per anno (da leggere)", "**Esito**"]
    for j, n in enumerate(nomi):
        righe.append(f"| {n} | {celle['A'][j]} | {celle['B'][j]} |")
    # il cuore dell'idea, da leggere: B meno SPY sugli stessi giorni (cioè il 30% venduto allo scoperto, con i costi)
    gb = ris["B"][1]["costi"]
    diff = gb - comprare_e_tenere("SPY", gb.index.min(), gb.index.max()).reindex(gb.index).fillna(0)
    righe += ["", f"Da leggere: B meno SPY, giorno per giorno, media annua {diff.mean() * 252:+.2%} (t "
              f"{diff.mean() / diff.std(ddof=1) * len(diff) ** 0.5:.2f}): è il guadagno (o la perdita) del lato venduto allo scoperto."]
    (QUI / "P024_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main()
