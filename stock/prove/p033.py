"""Prova 33 — il momento dei settori: comprati i 3 fondi di settore saliti di più in 12 mesi (meno l'ultimo), venduti i 3 saliti di
meno, ogni mese (idea I35).

    python -m stock.prove.p033

Regole: `P033_momento_dei_settori.md` (scritte e committate prima del calcolo). Prezzi di Yahoo (gratuiti, senza chiavi), scaricati
solo fino al 31 dicembre 2024 e tenuti fuori dal repository.
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import archivio, controlli, yahoo
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import rendimenti
from stock.prove.p031 import strategia
from stock.prove.p032 import campionamento, t_di
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto

SETTORI = ["XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY", "XLRE", "XLC"]
DAL, AL = "2014-11-01", "2024-12-31"
FINO = date(2024, 12, 31)
PRIMA = date(2015, 12, 1)
SEDUTE_ANNO, SEDUTE_MESE, QUANTI = 252, 21, 3
COSTI = Costi(mezzo_scarto=2.5 * PB, slittamento=1 * PB, prestito_annuo=0.005, **IB_FISSO)
LEVA_PER_IL_CAMBIO = 2.0

sr = lambda x: annuo(asticella.sharpe(x))  # noqa: E731
tot = lambda x: (1 + x).prod() - 1  # noqa: E731
dd = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min()  # noqa: E731


def carica() -> tuple[dict, dict]:
    cartella = archivio.cartella_dati() / "yahoo" / "p033"
    cartella.mkdir(parents=True, exist_ok=True)
    barre, rett = {}, {}
    for s in SETTORI:
        f = cartella / f"{s}.csv.gz"
        if f.exists():
            df = pd.read_csv(f, index_col=0)
            df.index = pd.to_datetime(df.index, utc=True).tz_convert("America/New_York")
        else:
            df = yahoo.prezzi(s, DAL, AL, frazionamenti=True)   # XLF, 19 set 2016: le quote di XLRE date ai detentori
            df.to_csv(f)
        df = df[pd.Index(df.index.date) <= FINO]
        barre[s] = df[["open", "high", "low", "close", "dividendo", "frazionamento"]]
        rett[s] = pd.Series(df["rettificata"].to_numpy(), index=pd.Index(df.index.date))
    return barre, rett


def segnale(r: pd.Series, giorno: date) -> float | None:
    """Il rendimento dalla chiusura di 252 sedute prima a quella di 21 sedute prima del giorno (12 mesi meno l'ultimo)."""
    if giorno not in r.index:
        return None
    k = r.index.get_loc(giorno)
    if k < SEDUTE_ANNO:
        return None
    return float(r.iloc[k - SEDUTE_MESE] / r.iloc[k - SEDUTE_ANNO] - 1)


def scegli(segnali: dict[str, float]) -> tuple[list[str], list[str]]:
    o = sorted(segnali, key=lambda s: (-segnali[s], s))
    if len(o) < 2 * QUANTI:
        return [], []
    return sorted(o[:QUANTI]), sorted(o[-QUANTI:])


def fine_dei_mesi(calendario: list[date]) -> list[date]:
    per = {}
    for g in calendario:
        per[(g.year, g.month)] = g
    return [per[k] for k in sorted(per)]


def main():
    spy = archivio.carica("SPY", "1Day_raw")
    cal = sorted(d for d in controlli.date_ny(spy.index) if d <= FINO)
    barre, rett = carica()
    giorni = [g for g in fine_dei_mesi(cal) if g >= PRIMA and g < date(2024, 12, 1)]
    elenchi, conti, ls = {}, {s: [0, 0] for s in SETTORI}, []
    for k, g in enumerate(giorni):
        seg = {s: v for s in SETTORI if (v := segnale(rett[s], g)) is not None}
        alti, bassi = scegli(seg)
        elenchi[g] = (alti, bassi)
        for s in alti:
            conti[s][0] += 1
        for s in bassi:
            conti[s][1] += 1
        g1 = giorni[k + 1] if k + 1 < len(giorni) else FINO
        if alti and all(g1 in rett[s].index for s in alti + bassi):
            ls.append(np.mean([rett[s][g1] / rett[s][g] - 1 for s in alti]) - np.mean([rett[s][g1] / rett[s][g] - 1 for s in bassi]))
    varianti = (("costi", COSTI), ("costi doppi", COSTI.raddoppiati()), ("senza costi", Costi()))
    out = {nome: simula_conto(barre, strategia(elenchi), c, capitale=CAPITALE, leva_massima=LEVA_PER_IL_CAMBIO) for nome, c in varianti}
    primo = out["costi"].esecuzioni["giorno"].min()
    g = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
    r = out["costi"]
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy_r = comprare_e_tenere("SPY", a, b)
    qq = (comprare_e_tenere("QQQ", a, b) - spy_r).dropna()
    corr_spy = float(np.corrcoef(*[x.loc[gc.index.intersection(spy_r.index)] for x in (spy_r, gc)])[0, 1])
    cq = gc.index.intersection(qq.index)
    corr_q = float(np.corrcoef(qq.loc[cq], gc.loc[cq])[0, 1])
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P033_momento_settori", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P033_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P033_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(g["costi doppi"])
    da_sola = sr_c > sr(spy_r) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte = t_di(gc.to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(g["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8
    anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
    ls = np.array(ls)
    testo = ["# Prova 33 — risultati", "",
             f"Calcolato da `python -m stock.prove.p033` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P033_momento_dei_settori.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* {len(giorni)} decisioni. Mesi comprato / venduto per settore: "
             + ", ".join(f"{s} {c[0]}/{c[1]}" for s, c in conti.items()) + ".",
             f"* Comprati meno venduti, mese dopo, senza costi: **{ls.mean():+.2%} al mese (t {t_di(ls):.2f})**, mediana "
             f"{np.median(ls):+.2%}, su {len(ls)} mesi. Correlazione con lo SPY {corr_spy:.2f}; **con QQQ meno SPY {corr_q:.2f}**.",
             f"* Ordini eseguiti {len(r.esecuzioni)}; senza barra {r.senza_barra}; rifiutati {r.rifiutati}. Costi pagati: commissioni "
             f"{r.commissioni:,.0f}, scarto e slittamento {r.costo_scarto:,.0f} dollari (il prestito è nel valore del conto).", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(g['costi doppi']):+.1%} | {tot(spy_r):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(g['senza costi']):.2f}) | {sr(spy_r):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy_r):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(g['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**; perdita massima {dd(nuova):.1%} contro {dd(miscela.loc[comuni]):.1%}. "
             f"**Esito: {'entra nella miscela (prima il revisore, poi il periodo chiuso e la misura in avanti)' if entra else 'non entra'}**",
             "", "Nel conto: 2 prove (83)."]
    (QUI / "P033_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-16:]))


if __name__ == "__main__":
    main()
