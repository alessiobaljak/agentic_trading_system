"""Prova 50 — l'incertezza sulla politica economica (Baker, Bloom e Davis): lo SPY al 98% del conto quando la media dell'indice
giornaliero del mese è sopra quella dei 12 mesi prima, al 49% altrimenti; decisione eseguita alla chiusura del primo giorno di borsa
del mese dopo (`P050_incertezza_politica.md`). Il conto e i costi sono quelli della prova 49.

    python -m stock.prove.p050        # in locale: chiusure dello SPY di Yahoo e indice di policyuncertainty.com (mai nel repository)
"""
from __future__ import annotations

import bisect
import csv
import io
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.prove.p001 import QUI, carica_serie, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import dd, sr, tot
from stock.prove.p049 import ALTA, BASSA, conto
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

DAL, FINO = date(2016, 1, 4), date(2024, 12, 31)
MESI = 12
EPU_URL = "https://www.policyuncertainty.com/media/All_Daily_Policy_Data.csv"


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def leggi_indice(testo: str) -> pd.Series:
    righe = [(date(int(r["year"]), int(r["month"]), int(r["day"])), float(r["daily_policy_index"]))
             for r in csv.DictReader(io.StringIO(testo)) if (r.get("daily_policy_index") or "").strip()]
    return pd.Series([v for _, v in righe], index=[d for d, _ in righe]).sort_index()


def decisioni(indice: pd.Series, calendario: list[date]) -> dict[date, float]:
    """{giorno di esecuzione: quota}. Per ogni mese con 12 mesi prima nel file: la media dell'indice del mese contro la media di tutti i
    giorni dei 12 mesi prima; eseguita alla chiusura del primo giorno di borsa dopo l'ultimo giorno del mese."""
    chiave = np.array([d.year * 12 + d.month - 1 for d in indice.index])
    valori = indice.to_numpy()
    mesi = sorted(set(chiave.tolist()))
    out = {}
    for i in range(MESI, len(mesi)):
        m = mesi[i]
        if mesi[i - MESI] != m - MESI:                       # mesi mancanti nel file: si salta
            continue
        media = float(valori[chiave == m].mean())
        prima = float(valori[(chiave >= m - MESI) & (chiave < m)].mean())
        ultimo = max(d for d, k in zip(indice.index, chiave) if k == m)
        j = bisect.bisect_right(calendario, ultimo)
        if j < len(calendario):
            out[calendario[j]] = ALTA if media > prima else BASSA
    return out


# --- con i prezzi ------------------------------------------------------------------------------------------------------------------
def main():
    import requests

    from stock.dati import yahoo
    indice = leggi_indice(requests.get(EPU_URL, headers={"User-Agent": "Mozilla/5.0 (ricerca)"}, timeout=60).text)
    df = yahoo.prezzi("SPY", "2015-11-02", "2024-12-31")
    ch = pd.Series(df["rettificata"].to_numpy(float), index=pd.Index([x.date() for x in df.index]))
    ch = ch[ch.index <= FINO]
    cal = list(ch.index)
    indice = indice[indice.index <= FINO]
    es = {g: q for g, q in decisioni(indice, cal).items() if g >= cal[0]}
    serie = {"costi": conto(ch, es), "costi doppi": conto(ch, es, 2.0), "senza costi": conto(ch, es, costi=False)}
    gg = {k: v[v.index >= DAL] for k, v in serie.items()}
    gc = gg["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = ch.pct_change().dropna()
    spy = spy[(spy.index >= a) & (spy.index <= b)]
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P050_incertezza", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P050_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P050_miscela"]
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
    dopo = {(k, n): [] for k in ("alta", "bassa") for n in (21, 63)}
    dietro = []
    for g, v in nel_periodo.items():
        i, k = pos[g], ("alta" if v == ALTA else "bassa")
        for n in (21, 63):
            if i + n < len(cal):
                dopo[(k, n)].append(float(ch.iloc[i + n] / ch.iloc[i] - 1))
        if i - 22 >= 0:
            dietro.append((1.0 if v == ALTA else 0.0, float(ch.iloc[i - 1] / ch.iloc[i - 22] - 1)))
    corr_dietro = float(np.corrcoef([x for x, _ in dietro], [y for _, y in dietro])[0, 1])
    vals = list(nel_periodo.values())
    cambi = pd.Series([g.year for g, v, p in zip(list(nel_periodo), vals, [None, *vals[:-1]]) if v != p]).value_counts().sort_index()
    alte = sum(1 for v in vals if v == ALTA)
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1

    def riga(nome, x):
        x = np.asarray(x)
        return f"{nome} {x.mean():+.2%} (t {t_di(x):.2f}, {len(x)} mesi)" if len(x) > 2 else f"{nome}: troppo pochi"
    testo = ["# Prova 50 — risultati", "",
             f"Calcolato da `python -m stock.prove.p050` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P050_incertezza_politica.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Decisioni nel periodo {len(nel_periodo)}, con l'incertezza sopra la media di un anno {alte} ({alte / len(nel_periodo):.0%}); "
             f"quota media {q_media:.1%}; cambi di quota per anno: {', '.join(f'{y} {n}' for y, n in cambi.items())}.",
             "* Lo SPY dopo la decisione (da leggere; la misura dello studio): nel mese " + riga("con l'incertezza alta", dopo[("alta", 21)])
             + "; " + riga("bassa", dopo[("bassa", 21)]) + ". Nei 3 mesi " + riga("alta", dopo[("alta", 63)]) + "; "
             + riga("bassa", dopo[("bassa", 63)]) + " (i 3 mesi si sovrappongono: il t è troppo alto).",
             f"* La decisione e lo SPY del mese prima (da leggere): correlazione {corr_dietro:+.2f} (negativa = l'incertezza alta viene dopo "
             "le cadute).",
             f"* Lo SPY sempre alla quota media ({q_media:.1%}): Sharpe {sr(fissa.dropna()):.2f}, totale {tot(fissa.dropna()):+.1%}. La regola "
             f"al contrario (98% con l'incertezza bassa): Sharpe {sr(contrario):.2f}, totale {tot(contrario):+.1%}.", "",
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
             "Nel conto: 2 prove (116 e 117)."]
    (QUI / "P050_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
