"""Prova 47 — la prima candela da 15 minuti sullo SPY (regola della prova 17) solo nei giorni con la copertura delle opzioni del giorno
prima sotto zero (`P047_prima_candela_gamma.md`, regole scritte prima; idea I55).

    python -m stock.prove.p047        # gira su GitHub (azioni-ricerca): calendario e prezzi di Alpaca, copertura da SqueezeMetrics
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.prove import p045
from stock.prove.p001 import CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, carica_serie, comprare_e_tenere, rendimenti_giornalieri, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.motore import simula
from stock.strategie import prima_candela as pc
from stock.strategie import ultima_mezzora as um

DAL, FINO, N = date(2016, 1, 4), date(2024, 12, 31), 15


def esclusi_per_copertura(giorni: list[date], gex: dict[date, float], sotto: bool) -> set[date]:
    """I giorni da escludere: con `sotto`, quelli senza la copertura del giorno prima sotto zero; altrimenti quelli sotto zero o senza
    il dato (per la lettura accanto)."""
    if sotto:
        return {g for g in giorni if not gex.get(g, np.nan) < 0}
    return {g for g in giorni if not gex.get(g, np.nan) >= 0}


def giorni_d_ingresso(e: pd.DataFrame) -> list[date]:
    """I giorni (di New York) con un ingresso, dalle esecuzioni del simulatore al minuto (colonna `t`)."""
    if e.empty:
        return []
    t = pd.to_datetime(e.loc[e.etichetta == "ingresso", "t"], utc=True).dt.tz_convert("America/New_York")
    return sorted(set(t.dt.date))


def senza_marzo_2020(g: pd.Series) -> pd.Series:
    return g[[not (x.year == 2020 and x.month == 3) for x in g.index]]


def main():
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    minuti = archivio.carica("SPY", "1Min_raw")
    if minuti is None or minuti.empty:
        from stock.dati.scarica import scarica_titolo
        scarica_titolo("SPY", "2016-01-01", "2024-12-31", minuti=True)
        minuti = archivio.carica("SPY", "1Min_raw")
    seduta = um.solo_seduta(minuti, cal)
    problemi, _ = controlli.controlla_minuti(minuti, cal)
    esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
    giorni = [g for g in sorted(cal.index) if DAL <= g <= FINO]
    gex = p045.copertura_del_giorno_prima(p045.copertura(), sorted(cal.index))
    costi = Costi(mezzo_scarto=MEZZO_SCARTO["SPY"], slittamento=0.5 * PB, **IB_FISSO)
    out = {}
    for quali, sotto in (("sotto", True), ("sopra", False)):
        seg = pc.prepara(seduta, cal, esclusi | esclusi_per_copertura(giorni, gex, sotto), N)
        for nome, c in (("costi", costi), ("costi doppi", costi.raddoppiati()), ("senza costi", Costi())):
            if quali == "sopra" and nome != "senza costi":
                continue
            r = simula(seduta, pc.strategia(seg), c, capitale=CAPITALE)
            out[(quali, nome)] = (r, rendimenti_giornalieri(r.valore, CAPITALE))
    rc, gc = out[("sotto", "costi")]
    g2, g0 = out[("sotto", "costi doppi")][1], out[("sotto", "senza costi")][1]
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P047_prima_candela_gamma", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P047_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P047_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(g2)
    da_sola = sr_c > sr(spy) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte, t_senza = t_di(gc.to_numpy()), t_di(senza_marzo_2020(gc).to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(g2.reindex(comuni).dropna()) > 0 and corr < 0.3 and sr(nuova) > sr(miscela.loc[comuni]) \
        and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8 and t_senza >= 1.3
    e = rc.esecuzioni
    giorni_op = giorni_d_ingresso(e)
    lordo = g0.reindex(giorni_op).dropna().to_numpy()
    g_sopra = out[("sopra", "senza costi")]
    e_s = g_sopra[0].esecuzioni
    giorni_s = giorni_d_ingresso(e_s)
    lordo_s = g_sopra[1].reindex(giorni_s).dropna().to_numpy()
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1

    def riga(nome, x):
        return (f"{nome}: {len(x)} giorni, **{x.mean() * 1e4:+.2f} punti base** al giorno sul conto (t {t_di(x):.2f}), in guadagno "
                f"{(x > 0).mean():.0%}") if len(x) else f"{nome}: nessun giorno"
    testo = ["# Prova 47 — risultati", "",
             f"Calcolato da `python -m stock.prove.p047` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P047_prima_candela_gamma.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Giorni con la copertura del giorno prima sotto zero {len(giorni) - len(esclusi_per_copertura(giorni, gex, True))}; "
             f"ingressi {(e.etichetta == 'ingresso').sum()}; uscite: stop {(e.etichetta == 'stop').sum()}, obiettivo "
             f"{(e.etichetta == 'obiettivo').sum()}, chiusura {(e.etichetta == 'chiusura').sum()}; ordini rifiutati {rc.rifiutati}.",
             f"* Prima dei costi: {riga('nei giorni sotto zero (la regola)', lordo)}; da leggere, "
             f"{riga('nei giorni sopra o uguale a zero', lordo_s)}.", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g0):+.1%} / {tot(gc):+.1%} / {tot(g2):+.1%} | "
             f"{tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(g0):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(g2.reindex(comuni).dropna()):.2f}; correlazione con la miscela {corr:.2f} "
             f"(soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e {sr(spy_c):.2f} del "
             f"tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f}, senza marzo 2020 {t_senza:.2f} (soglia 1,3 tutti e due)**; "
             f"**miscela nuova più alta nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove."]
    (QUI / "P047_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
