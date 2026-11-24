"""Prova 49 — le vendite allo scoperto fuori borsa (il DIX di SqueezeMetrics): lo SPY al 98% del conto quando la media del DIX della
settimana è sopra quella delle 52 settimane prima, al 49% altrimenti; decisione eseguita alla chiusura del primo giorno di borsa della
settimana dopo (`P049_vendite_fuori_borsa.md`).

    python -m stock.prove.p049        # in locale: chiusure dello SPY di Yahoo e DIX di SqueezeMetrics (mai nel repository)
"""
from __future__ import annotations

import bisect
import csv
import io
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.prove.p001 import CAPITALE, PB, QUI, carica_serie, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import commissione, dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

DAL, FINO = date(2016, 1, 4), date(2024, 12, 31)
ALTA, BASSA, SLIT = 0.98, 0.49, 0.5 * PB
SETTIMANE = 52
DIX_URL = "https://squeezemetrics.com/monitor/static/DIX.csv"


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def leggi_dix(testo: str) -> pd.Series:
    righe = [(date.fromisoformat(r["date"]), float(r["dix"])) for r in csv.DictReader(io.StringIO(testo)) if r.get("dix", "").strip()]
    return pd.Series([v for _, v in righe], index=[d for d, _ in righe]).sort_index()


def decisioni(dix: pd.Series, calendario: list[date], alta: float = ALTA, bassa: float = BASSA) -> dict[date, float]:
    """{giorno di esecuzione: quota}. Per ogni settimana (ISO) con almeno 52 settimane prima nel file: la media del DIX della settimana
    contro la media dei giorni delle 52 settimane prima; eseguita alla chiusura del primo giorno di borsa dopo l'ultimo giorno della
    settimana."""
    chiave = [d.isocalendar()[:2] for d in dix.index]
    gruppi = pd.Series(dix.to_numpy(), index=pd.MultiIndex.from_tuples(chiave))
    settimane = list(dict.fromkeys(chiave))
    ultimo = {k: max(d for d, c in zip(dix.index, chiave) if c == k) for k in settimane}
    out = {}
    for i in range(SETTIMANE, len(settimane)):
        k = settimane[i]
        prima = np.concatenate([np.atleast_1d(gruppi.loc[[settimane[j]]].to_numpy()) for j in range(i - SETTIMANE, i)])
        media = float(np.mean(np.atleast_1d(gruppi.loc[[k]].to_numpy())))
        j = bisect.bisect_right(calendario, ultimo[k])
        if j < len(calendario):
            out[calendario[j]] = alta if media > float(np.mean(prima)) else bassa
    return out


def conto(chiusure: pd.Series, esecuzioni: dict[date, float], fattore: float = 1.0, costi: bool = True) -> pd.Series:
    """I rendimenti di ogni giorno: la quota decisa vale dalla chiusura del giorno di esecuzione; a ogni cambio, slittamento e
    commissione sulla parte comprata o venduta (all'asta di chiusura). Prima della prima esecuzione: fuori."""
    r = chiusure.pct_change()
    giorni = list(chiusure.index)
    quota, v, out = 0.0, CAPITALE, {}
    for g in giorni[1:]:
        x = quota * float(r.loc[g])
        if g in esecuzioni:
            nuova = esecuzioni[g]
            if costi and nuova != quota:
                delta = abs(nuova - quota)
                n = int(delta * v / float(chiusure.loc[g]))
                x -= fattore * (delta * SLIT + commissione(n, float(chiusure.loc[g])) / v)
            quota = nuova
        out[g] = x
        v *= 1 + x
    return pd.Series(out)


# --- con i prezzi ------------------------------------------------------------------------------------------------------------------
def main():
    import requests

    from stock.dati import yahoo
    testo = requests.get(DIX_URL, headers={"User-Agent": "Mozilla/5.0 (ricerca)"}, timeout=60).text
    dix = leggi_dix(testo)
    df = yahoo.prezzi("SPY", "2015-11-02", "2024-12-31")
    ch = pd.Series(df["rettificata"].to_numpy(float), index=pd.Index([x.date() for x in df.index]))
    ch = ch[ch.index <= FINO]
    cal = list(ch.index)
    dix = dix[dix.index <= FINO]
    es = {g: q for g, q in decisioni(dix, cal).items() if g >= cal[0]}
    serie = {"costi": conto(ch, es), "costi doppi": conto(ch, es, 2.0), "senza costi": conto(ch, es, costi=False)}
    gg = {k: v[v.index >= DAL] for k, v in serie.items()}
    gc = gg["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = ch.pct_change().dropna()
    spy = spy[(spy.index >= a) & (spy.index <= b)]
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P049_dix", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P049_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P049_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota_t = sum(x > 0 for x in q) / len(q)
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
    nel_periodo = {g: v for g, v in es.items() if DAL <= g <= FINO}
    quota_giorno = pd.Series(np.nan, index=ch.index)
    for g, v in es.items():
        quota_giorno.loc[g] = v
    quota_giorno = quota_giorno.ffill().fillna(0.0)
    q_media = float(quota_giorno[(quota_giorno.index >= DAL)].mean())
    fissa = (q_media * ch.pct_change()).reindex(gc.index)
    contrario = conto(ch, {g: (BASSA if v == ALTA else ALTA) for g, v in es.items()})
    contrario = contrario[contrario.index >= DAL]
    pos = {g: i for i, g in enumerate(cal)}
    avanti, dietro = {"alta": [], "bassa": []}, []
    for g, v in nel_periodo.items():
        i = pos[g]
        if i + 20 < len(cal):
            avanti["alta" if v == ALTA else "bassa"].append(float(ch.iloc[i + 20] / ch.iloc[i] - 1))
        if i - 21 >= 0:
            dietro.append((1.0 if v == ALTA else 0.0, float(ch.iloc[i - 1] / ch.iloc[i - 21] - 1)))
    corr_dietro = float(np.corrcoef([x for x, _ in dietro], [y for _, y in dietro])[0, 1])
    cambi = pd.Series([g.year for g, v, p in zip(list(nel_periodo), list(nel_periodo.values()),
                                                  [None, *list(nel_periodo.values())[:-1]]) if v != p]).value_counts().sort_index()
    alte = sum(1 for v in nel_periodo.values() if v == ALTA)
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1

    def riga(nome, x):
        x = np.asarray(x)
        return f"{nome} {x.mean():+.2%} (t {t_di(x):.2f}, {len(x)} settimane)" if len(x) > 2 else f"{nome}: troppo poche"
    testo = ["# Prova 49 — risultati", "",
             f"Calcolato da `python -m stock.prove.p049` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P049_vendite_fuori_borsa.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Decisioni nel periodo {len(nel_periodo)}, con il DIX sopra la media di un anno {alte} ({alte / len(nel_periodo):.0%}); "
             f"quota media {q_media:.1%}; cambi di quota per anno: {', '.join(f'{y} {n}' for y, n in cambi.items())}.",
             "* Lo SPY nelle 4 settimane dopo la decisione (da leggere): " + riga("dopo il DIX alto", avanti["alta"]) + "; "
             + riga("dopo il DIX basso", avanti["bassa"]) + ".",
             f"* La decisione e lo SPY delle 4 settimane prima (da leggere): correlazione {corr_dietro:+.2f} (negativa = il DIX alto viene "
             "dopo le cadute).",
             f"* Lo SPY sempre alla quota media ({q_media:.1%}): Sharpe {sr(fissa.dropna()):.2f}, totale {tot(fissa.dropna()):+.1%}. La regola "
             f"al contrario (98% con il DIX basso): Sharpe {sr(contrario):.2f}, totale {tot(contrario):+.1%}.", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(gg['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(gg['costi doppi']):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(gg['senza costi']):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota_t:.0%}) | — |",
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
    (QUI / "P049_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
