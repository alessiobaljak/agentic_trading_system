"""Prova 48 — la settimana della scadenza delle opzioni: SPY tenuto dalla chiusura dell'ultimo giorno di borsa prima del lunedì alla
chiusura del terzo venerdì (o dell'ultimo giorno di borsa prima), fuori nelle altre settimane (`P048_settimana_della_scadenza.md`).

    python -m stock.prove.p048        # in locale: chiusure dello SPY di Yahoo (mai nel repository)
"""
from __future__ import annotations

import bisect
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd

from stock.prove.p001 import CAPITALE, PB, QUI, carica_serie, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import commissione, dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

DAL, FINO = date(2016, 1, 4), date(2024, 12, 31)
QUOTA, SLIT = 0.98, 0.5 * PB


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def terzo_venerdi(anno: int, mese: int) -> date:
    d = date(anno, mese, 1)
    primo = d + timedelta(days=(4 - d.weekday()) % 7)
    return primo + timedelta(days=14)


def scadenze(calendario: list[date]) -> list[date]:
    """Il giorno della scadenza di ogni mese: il terzo venerdì, o l'ultimo giorno di borsa prima se quel venerdì la borsa è chiusa."""
    mesi = sorted({(g.year, g.month) for g in calendario})
    out = []
    for a, m in mesi:
        v = terzo_venerdi(a, m)
        k = bisect.bisect_right(calendario, v) - 1
        if k >= 0 and calendario[k].year == a and calendario[k].month == m:
            out.append(calendario[k])
    return out


def finestre_scadenza(calendario: list[date]) -> list[tuple[date, date]]:
    """(giorno dell'entrata alla chiusura, giorno della scadenza): l'entrata è l'ultimo giorno di borsa prima del lunedì della settimana."""
    out = []
    for s in scadenze(calendario):
        lunedi = s - timedelta(days=s.weekday())
        k = bisect.bisect_left(calendario, lunedi) - 1
        if k >= 0:
            out.append((calendario[k], s))
    return out


def conto(chiusure: pd.Series, finestre_s: list[tuple[date, date]], fattore: float = 1.0, costi: bool = True) -> pd.Series:
    """I rendimenti di ogni giorno: dentro (il 98% del conto) dal giorno dopo l'entrata fino alla scadenza compresa; slittamento e
    commissione all'entrata e all'uscita, alle aste di chiusura."""
    r = chiusure.pct_change()
    dentro, entrate, uscite = set(), set(), set()
    giorni = list(chiusure.index)
    pos = {g: i for i, g in enumerate(giorni)}
    for e, s in finestre_s:
        if e not in pos or s not in pos:
            continue
        entrate.add(e)
        uscite.add(s)
        dentro.update(giorni[pos[e] + 1: pos[s] + 1])
    v, out = CAPITALE, {}
    for g in giorni[1:]:
        x = QUOTA * float(r.loc[g]) if g in dentro else 0.0
        if costi and (g in entrate or g in uscite):
            n = int(QUOTA * v / float(chiusure.loc[g]))
            x -= fattore * (QUOTA * SLIT + commissione(n, float(chiusure.loc[g])) / v)
        out[g] = x
        v *= 1 + x
    return pd.Series(out)


def settimane(chiusure: pd.Series, scad: list[date]) -> dict[str, np.ndarray]:
    """I rendimenti settimanali (dall'ultima chiusura di una settimana all'ultima della dopo): settimane della scadenza, settimane dopo,
    altre."""
    idx = pd.Index(chiusure.index)
    chiave = [(g.isocalendar().year, g.isocalendar().week) for g in idx]
    ultima = pd.Series(chiusure.to_numpy(), index=pd.MultiIndex.from_tuples(chiave)).groupby(level=[0, 1]).last()
    giorni = pd.Series(list(idx), index=pd.MultiIndex.from_tuples(chiave)).groupby(level=[0, 1]).last()
    ret = ultima.pct_change().dropna()
    con_scad = {(s.isocalendar().year, s.isocalendar().week) for s in scad}
    chiavi = list(ret.index)
    tipo = {}
    for i, k in enumerate(chiavi):
        if k in con_scad:
            tipo[k] = "scadenza"
        elif i > 0 and chiavi[i - 1] in con_scad:
            tipo[k] = "dopo"
        else:
            tipo[k] = "altre"
    _ = giorni
    return {t: ret[[k for k in chiavi if tipo[k] == t]].to_numpy() for t in ("scadenza", "dopo", "altre")}


# --- con i prezzi ------------------------------------------------------------------------------------------------------------------
def main():
    from stock.dati import yahoo
    df = yahoo.prezzi("SPY", "2015-11-02", "2024-12-31")
    ch = pd.Series(df["rettificata"].to_numpy(float), index=pd.Index([x.date() for x in df.index]))
    ch = ch[ch.index <= FINO]
    cal = list(ch.index)
    fin = [(e, s) for e, s in finestre_scadenza(cal) if DAL <= s <= FINO and e >= cal[0]]
    serie = {"costi": conto(ch, fin), "costi doppi": conto(ch, fin, 2.0), "senza costi": conto(ch, fin, costi=False)}
    gg = {k: v[v.index >= DAL] for k, v in serie.items()}
    gc = gg["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = ch.pct_change().dropna()
    spy = spy[(spy.index >= a) & (spy.index <= b)]
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P048_scadenza", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P048_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P048_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(gg["costi doppi"])
    da_sola = sr_c > sr(spy) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = spy.reindex(comuni).dropna()
    t_parte = t_di(gc.to_numpy())
    t_senza = t_di(gc[[not (x.year == 2020 and x.month == 3) for x in gc.index]].to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(gg["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8 and t_senza >= 1.3
    sett = settimane(ch[(ch.index >= date(2015, 12, 24)) & (ch.index <= FINO)], [s for _, s in fin])
    prima = settimane(ch[(ch.index >= date(2015, 12, 24)) & (ch.index < date(2020, 1, 1))], [s for _, s in fin if s.year < 2020])
    dopo20 = settimane(ch[ch.index >= date(2019, 12, 24)], [s for _, s in fin if s.year >= 2020])
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1

    def riga(nome, x):
        return f"{nome} {x.mean():+.2%} (t {t_di(x):.2f}, {len(x)} settimane)" if len(x) else f"{nome}: nessuna"
    testo = ["# Prova 48 — risultati", "",
             f"Calcolato da `python -m stock.prove.p048` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P048_settimana_della_scadenza.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Settimane della scadenza {len(fin)}; giorni dentro {int(sum(1 for g in gc.index if gc.loc[g] != 0))} su {len(gc)}.",
             "* Lo SPY per settimana (da leggere): " + "; ".join(riga(n, sett[k]) for k, n in (("scadenza", "della scadenza"),
                                                                                              ("dopo", "la settimana dopo"),
                                                                                              ("altre", "le altre"))) + ".",
             "* Prima del 2020: " + "; ".join(riga(n, prima[k]) for k, n in (("scadenza", "della scadenza"), ("dopo", "dopo"),
                                                                            ("altre", "altre")))
             + ". Dal 2020: " + "; ".join(riga(n, dopo20[k]) for k, n in (("scadenza", "della scadenza"), ("dopo", "dopo"),
                                                                          ("altre", "altre"))) + ".", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(gg['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(gg['costi doppi']):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(gg['senza costi']):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(gg['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f}, senza marzo 2020 {t_senza:.2f} (soglia 1,3 "
             f"tutti e due)**; **miscela nuova più alta nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove."]
    (QUI / "P048_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
