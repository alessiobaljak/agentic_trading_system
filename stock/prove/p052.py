"""Prova 52 — vendere la volatilità con la curva normale: SVXY al 98% del conto dalla chiusura di un giorno in cui il VIX del giorno di
borsa prima ha chiuso sotto il VIX a tre mesi, fuori altrimenti (`P052_vendere_volatilita.md`).

    python -m stock.prove.p052        # in locale: SVXY e SPY di Yahoo, VIX e VIX a tre mesi della CBOE (mai nel repository)
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.prove.p001 import CAPITALE, QUI, carica_serie, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import commissione, dd, sr, tot
from stock.prove.p044 import indice_cboe, segnale
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

DAL, FINO = date(2016, 1, 4), date(2024, 12, 31)
QUOTA, SLIT = 0.98, 2e-4
CAMBIO_FONDO = date(2018, 2, 27)


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def quote(normale: pd.Series, calendario: list[date]) -> pd.Series:
    """La quota tenuta dalla chiusura di ogni giorno di borsa: 98% se il giorno di borsa prima la curva era normale (VIX sotto il VIX a
    tre mesi), 0 altrimenti o se manca il dato di quel giorno."""
    q = {}
    for k in range(1, len(calendario)):
        ieri = calendario[k - 1]
        q[calendario[k]] = QUOTA if bool(normale.get(ieri, False)) else 0.0
    return pd.Series(q)


def conto(chiusure: pd.Series, quota: pd.Series, fattore: float = 1.0, costi: bool = True) -> pd.Series:
    """I rendimenti di ogni giorno: la quota decisa alla chiusura di ieri per il rendimento di oggi; a ogni cambio, slittamento e
    commissione sulla parte comprata o venduta, all'asta di chiusura."""
    r = chiusure.pct_change()
    giorni = list(chiusure.index)
    tenuta, v, out = 0.0, CAPITALE, {}
    for g in giorni[1:]:
        x = tenuta * float(r.loc[g])
        nuova = float(quota.get(g, 0.0))
        if costi and nuova != tenuta:
            delta = abs(nuova - tenuta)
            n = int(delta * v / float(chiusure.loc[g]))
            x -= fattore * (delta * SLIT + commissione(n, float(chiusure.loc[g])) / v)
        tenuta = nuova
        out[g] = x
        v *= 1 + x
    return pd.Series(out)


# --- con i prezzi ------------------------------------------------------------------------------------------------------------------
def main():
    from stock.dati import yahoo

    def chiusure(s):
        df = yahoo.prezzi(s, "2015-11-02", "2024-12-31", frazionamenti=True)     # SVXY ha un raggruppamento: si usa la rettificata
        c = pd.Series(df["rettificata"].to_numpy(float), index=pd.Index([x.date() for x in df.index]))
        return c[c.index <= FINO]
    sv, sp = chiusure("SVXY"), chiusure("SPY")
    cal = sorted(set(sv.index) & set(sp.index))
    sv, sp = sv.reindex(cal), sp.reindex(cal)
    normale = ~segnale(indice_cboe("VIX"), indice_cboe("VIX3M"))           # True: VIX sotto il VIX a tre mesi
    q = quote(normale, cal)
    serie = {"costi": conto(sv, q), "costi doppi": conto(sv, q, 2.0), "senza costi": conto(sv, q, costi=False)}
    gg = {k: v[v.index >= DAL] for k, v in serie.items()}
    gc = gg["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = sp.pct_change().dropna()
    spy = spy[(spy.index >= a) & (spy.index <= b)]
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P052_svxy", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P052_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P052_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    trim = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
            for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota_t = sum(x > 0 for x in trim) / len(trim)
    sr_c, sr_2 = sr(gc), sr(gg["costi doppi"])
    da_sola = sr_c > sr(spy) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota_t >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = spy.reindex(comuni).dropna()
    t_parte = t_di(gc.to_numpy())
    t_senza = t_di(gc[[not (x.year == 2020 and x.month == 3) for x in gc.index]].to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(gg["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8 and t_senza >= 1.3

    # da leggere
    sempre = sv.pct_change().reindex(gc.index)
    qp = q[(q.index >= DAL) & (q.index <= FINO)]
    dentro = float((qp > 0).mean())
    cambi = pd.Series([g.year for g, x, p in zip(qp.index, qp.to_numpy(), [0.0, *qp.to_numpy()[:-1]]) if x != p]).value_counts().sort_index()
    mesi = (1 + gc).groupby(pd.Index([(x.year, x.month) for x in gc.index])).prod() - 1
    feb18, mar20 = float(mesi.get((2018, 2), np.nan)), float(mesi.get((2020, 3), np.nan))
    prima, dopo = gc[gc.index < CAMBIO_FONDO], gc[gc.index >= CAMBIO_FONDO]
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1
    testo = ["# Prova 52 — risultati", "",
             f"Calcolato da `python -m stock.prove.p052` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P052_vendere_volatilita.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Giorni dentro {dentro:.0%}; cambi per anno: {', '.join(f'{y} {n}' for y, n in cambi.items())}.",
             f"* Il giorno peggiore {gc.min():+.1%} ({gc.idxmin()}); il mese peggiore {mesi.min():+.1%} ({mesi.idxmin()}); febbraio 2018 "
             f"{feb18:+.1%}; marzo 2020 {mar20:+.1%}.",
             f"* Prima del cambio del fondo (27 febbraio 2018): Sharpe {sr(prima):.2f}, {tot(prima):+.1%}; dopo: Sharpe {sr(dopo):.2f}, "
             f"{tot(dopo):+.1%}.",
             f"* SVXY tenuto sempre: Sharpe {sr(sempre.dropna()):.2f}, {tot(sempre.dropna()):+.1%}, perdita massima {dd(sempre.dropna()):.1%}.",
             "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(gg['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(gg['costi doppi']):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(gg['senza costi']):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in trim)} su {len(trim)} ({quota_t:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(gg['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f}, senza marzo 2020 {t_senza:.2f} (soglia 1,3 "
             f"tutti e due)**; **miscela nuova più alta nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove (120 e 121)."]
    (QUI / "P052_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
