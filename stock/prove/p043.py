"""Prova 43 — il carry delle valute: ogni fine mese comprate le 2 valute (fondi CurrencyShares) con il tasso a tre mesi più alto,
vendute allo scoperto le 2 con il più basso, metà e metà (idea I47; Lustig, Roussanov e Verdelhan 2011; Koijen e altri 2018).

    python -m stock.prove.p043        # in locale: prezzi di Yahoo (tenuti fuori dal repository), tassi in dati/P043_tassi.csv

Regole: `P043_carry_valute.md` (scritte e committate prima del calcolo).
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import archivio, controlli, yahoo
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import rendimenti
from stock.prove.p031 import LEVA_PER_IL_CAMBIO, LIQUIDA_DOPO, PRESTITO, strategia
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto

FONDI = ["FXA", "FXB", "FXC", "FXE", "FXF", "FXY"]
PRIMA, ULTIMA, FINO = date(2015, 12, 1), date(2024, 11, 30), date(2024, 12, 31)
COSTI = Costi(mezzo_scarto=5 * PB, slittamento=1 * PB, prestito_annuo=PRESTITO, **IB_FISSO)
QUANTI = 2


def carica_fondi(dal: str = "2015-11-02", al: str = "2024-12-31"):
    cartella = archivio.cartella_dati() / "yahoo" / "p043"
    cartella.mkdir(parents=True, exist_ok=True)
    barre, rett = {}, {}
    for s in FONDI:
        f = cartella / f"{s}.csv.gz"
        if f.exists():
            df = pd.read_csv(f, index_col=0)
            df.index = pd.to_datetime(df.index, utc=True).tz_convert("America/New_York")
        else:
            df = yahoo.prezzi(s, dal, al)
            df.to_csv(f)
        barre[s] = df[["open", "high", "low", "close", "dividendo", "frazionamento"]]
        rett[s] = pd.Series(df["rettificata"].to_numpy(), index=pd.Index(df.index.date))
    return barre, rett


def tassi() -> dict[str, dict[str, float]]:
    t = pd.read_csv(QUI / "dati" / "P043_tassi.csv")
    return {m: dict(zip(g["fondo"], g["tasso"].astype(float))) for m, g in t.groupby("mese")}


def fine_dei_mesi(calendario: list[date]) -> list[date]:
    """L'ultimo giorno di borsa di ogni mese del calendario."""
    s = pd.Series(calendario, index=[(d.year, d.month) for d in calendario])
    return [g.iloc[-1] for _, g in s.groupby(level=0)]


def mese_del_tasso(giorno: date) -> str:
    """Il tasso noto alla decisione di fine mese m: quello del mese m − 2."""
    p = pd.Period(giorno, "M") - 2
    return f"{p.year:04d}-{p.month:02d}"


def scegli(t: dict[str, float]) -> tuple[list[str], list[str]]:
    """Le 2 con il tasso più alto (comprate) e le 2 con il più basso (vendute); a pari tasso in ordine alfabetico; meno di 6: niente."""
    if len(t) < len(FONDI):
        return [], []
    alti = sorted(t, key=lambda s: (-t[s], s))[:QUANTI]
    bassi = sorted(t, key=lambda s: (t[s], s))[:QUANTI]
    return sorted(alti), sorted(bassi)


def calcola() -> dict:
    spy = archivio.carica("SPY", "1Day_raw")
    cal = sorted(d for d in controlli.date_ny(spy.index) if date(2015, 11, 2) <= d <= FINO)
    barre, rett = carica_fondi()
    mancanti = {s: len(set(cal) - set(rett[s].index)) for s in FONDI}
    tt = tassi()
    fini = [g for g in fine_dei_mesi(cal) if PRIMA <= g <= ULTIMA]
    elenchi, mesi, diff, volte = {}, [], [], {s: [0, 0] for s in FONDI}
    for k, g in enumerate(fini):
        t = tt.get(mese_del_tasso(g), {})
        alti, bassi = scegli(t)
        elenchi[g] = (alti, bassi)
        if not alti:
            continue
        for s in alti:
            volte[s][0] += 1
        for s in bassi:
            volte[s][1] += 1
        diff.append(np.mean([t[s] for s in alti]) - np.mean([t[s] for s in bassi]))
        dopo = fini[k + 1] if k + 1 < len(fini) else max(d for d in cal if d <= FINO)
        r = {s: float(rett[s].loc[dopo] / rett[s].loc[g] - 1) for s in alti + bassi}
        mesi.append((dopo, float(np.mean([r[s] for s in alti]) - np.mean([r[s] for s in bassi]))))
    varianti = (("costi", COSTI), ("costi doppi", COSTI.raddoppiati()), ("senza costi", Costi()))
    out = {nome: simula_conto(barre, strategia(elenchi), c, capitale=CAPITALE, liquida_dopo=LIQUIDA_DOPO,
                              leva_massima=LEVA_PER_IL_CAMBIO) for nome, c in varianti}
    primo = out["costi"].esecuzioni["giorno"].min()
    gg = {kk: rendimenti(vv.valore[vv.valore.index >= primo]) for kk, vv in out.items()}
    return dict(g=gg, out=out, mesi=mesi, diff=diff, volte=volte, mancanti=mancanti, decisioni=len(fini))


def main():
    c = calcola()
    g, r = c["g"], c["out"]["costi"]
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    ls = np.array([x for _, x in c["mesi"]])
    per_mese = {f"{d.year}-{d.month:02d}": x for d, x in c["mesi"]}
    spy = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P043_carry", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P043_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P043_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(g["costi doppi"])
    da_sola = sr_c > sr(spy) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    sp = spy.reindex(gc.index).dropna()
    corr_spy = float(np.corrcoef(gc.loc[sp.index], sp)[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte = t_di(gc.to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(g["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1
    volte = ", ".join(f"{s} {v[0]}/{v[1]}" for s, v in c["volte"].items())
    testo = ["# Prova 43 — risultati", "",
             f"Calcolato da `python -m stock.prove.p043` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P043_carry_valute.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Decisioni {c['decisioni']}; giorni senza prezzo per fondo {c['mancanti']}. Ordini {len(r.esecuzioni)}, liquidati "
             f"{len(r.liquidati)}; commissioni {r.commissioni:,.0f} dollari, scarto {r.costo_scarto:,.0f}.",
             f"* Mesi comprati / venduti per fondo: {volte}. Differenza media dei tassi fra comprati e venduti "
             f"{np.mean(c['diff']):.2f} punti percentuali l'anno.",
             f"* **Comprati meno venduti, il mese dopo, prima dei costi: {ls.mean():+.2%} al mese (t {t_di(ls):.2f})**, mesi positivi "
             f"{(ls > 0).mean():.0%}; marzo 2020 {per_mese.get('2020-03', float('nan')):+.2%}, agosto 2024 "
             f"{per_mese.get('2024-08', float('nan')):+.2%}. Correlazione giornaliera con lo SPY {corr_spy:.2f}.", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(g['costi doppi']):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(g['senza costi']):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(g['costi doppi'].reindex(comuni).dropna()):.2f}; **correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3)**; miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove."]
    (QUI / "P043_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
