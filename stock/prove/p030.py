"""Prova 30 — le azioni dell'S&P 500 nella settimana in cui pubblicano i risultati, coperte con lo SPY (idea I32).

    python -m stock.prove.p030            # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca)
    python -m stock.prove.p030 --finta    # prova del programma in locale, con date dei comunicati inventate (non è il risultato)

Regole: `P030_premio_del_comunicato.md` (scritte e committate prima del calcolo). Le date dei comunicati (moduli 8-K, voce 2.02, della
SEC) sono in `dati/P030_comunicati.csv.gz`; la composizione dell'indice in `dati/P028_membri.csv.gz`; i prezzi con il simbolo di
allora, come la prova 28.
"""
from __future__ import annotations

import bisect
import math
import sys
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd

from stock.dati import controlli
from stock.prove.p001 import CAPITALE, IB_FISSO, MEZZO_SCARTO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import prepara_titolo, rendimenti, scarti_misurati
from stock.prove.p011 import costi_per
from stock.prove.p027 import scarica
from stock.prove.p028 import decisioni as fine_mese
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import tono

FINO = date(2024, 12, 31)
DAL = date(2016, 12, 1)            # la prima decisione è l'ultima settimana del 2016
ANTICIPO = timedelta(days=364)     # la data prevista: lo stesso giorno della settimana, 52 settimane dopo
MASSIMO, MINIMO = 50, 10
PRESTITO_SPY = 0.005
LIQUIDA_DOPO = 5
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}

sr = lambda x: annuo(asticella.sharpe(x))  # noqa: E731
tot = lambda x: (1 + x).prod() - 1  # noqa: E731
dd = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min()  # noqa: E731
t_di = lambda x: x.mean() / x.std(ddof=1) * math.sqrt(len(x)) if len(x) > 2 else float("nan")  # noqa: E731


def comunicati(finta: bool = False) -> dict[str, list[date]]:
    """Simbolo di allora -> date di deposito dei comunicati sui risultati. Con `finta`, date inventate (un comunicato ogni circa 91
    giorni da un giorno a caso): servono solo a provare il programma senza vedere il risultato vero."""
    c = pd.read_csv(QUI / "dati" / "P030_comunicati.csv.gz", parse_dates=["deposito"])
    out = {s: sorted(d.dt.date) for s, d in c.groupby("simbolo_allora")["deposito"]}
    if finta:
        rng = np.random.default_rng(30)
        out = {s: [date(2016, 1, 4) + timedelta(days=int(rng.integers(0, 91)) + 91 * k) for k in range(36)] for s in out}
        out = {s: [d for d in v if d.weekday() < 5] for s, v in out.items()}
    return out


def settimane(giorni_di_borsa: list[date]) -> list[tuple[date, date, date]]:
    """Per ogni settimana con una dopo: (giorno della decisione = ultimo giorno di borsa della settimana, primo giorno di borsa
    della settimana dopo = entrata, venerdì della settimana dopo)."""
    per = {}
    for g in giorni_di_borsa:
        per.setdefault(g.isocalendar()[:2], []).append(g)
    chiavi = sorted(per)
    out = []
    for a, b in zip(chiavi[:-1], chiavi[1:]):
        entrata = per[b][0]
        out.append((per[a][-1], entrata, entrata + timedelta(days=4 - entrata.weekday())))
    return out


def membri_al(giorno: date, fini: list[date], membri: dict[date, set[str]]) -> set[str]:
    k = bisect.bisect_right(fini, giorno) - 1
    return membri[fini[k]] if k >= 0 else set()


def previsti(date_c: dict[str, list[date]], entrata: date, venerdi: date) -> set[str]:
    """I simboli con una data prevista (deposito + 364 giorni) dopo l'entrata e fino al venerdì."""
    a, b = entrata - ANTICIPO, venerdi - ANTICIPO
    return {s for s, v in date_c.items() if bisect.bisect_right(v, b) > bisect.bisect_right(v, a)}


def depositati(date_c: dict[str, list[date]], s: str, entrata: date, venerdi: date) -> bool:
    v = date_c.get(s, [])
    return bisect.bisect_right(v, venerdi) > bisect.bisect_left(v, entrata)


def scegli(candidati: set[str]) -> list[str]:
    return sorted(candidati)[:MASSIMO] if len(candidati) >= MINIMO else []


def calcola(finta: bool = False) -> dict:
    fini, membri = fine_mese()
    date_c = comunicati(finta)
    simboli = sorted(set().union(*[membri[g] for g in fini if g >= DAL - timedelta(days=40)]))
    if finta:
        TIPI.update(raw="1Day_raw", az="azioni", asof=None)
    else:
        scarica(["SPY"])                                                   # per il confronto con il tenere lo SPY
        scarica(simboli + ["SPY"], TIPI["raw"], TIPI["az"], TIPI["asof"])
    barre, rett, senza = {}, {}, []
    for s in simboli + ["SPY"]:
        try:
            barre[s], rett[s], _ = prepara_titolo(s, FINO, TIPI["raw"], TIPI["az"])
        except Exception as e:  # noqa: BLE001 — titolo senza prezzi: si conta
            senza.append(f"{s} ({type(e).__name__})")
    ha = {s: set(rett[s].index) for s in barre}
    calendario = sorted(g for g in rett["SPY"].index if DAL <= g <= FINO)
    sett = [x for x in settimane(calendario) if x[0] >= date(2016, 12, 26)]
    elenchi, tutti, conteggi = {}, {}, []
    for decisione, entrata, venerdi in sett:
        m = {s for s in membri_al(decisione, fini, membri) if s in ha and decisione in ha[s]}
        c = previsti(date_c, entrata, venerdi) & m
        tutti[decisione] = (entrata, sorted(c))
        elenchi[decisione] = scegli(c)
        conteggi.append(len(c))
    # aperture rettificate (dividendi e frazionamenti) per il rendimento dall'apertura all'apertura
    aperture = {}
    for s, df in barre.items():
        giorni = pd.Index(controlli.date_ny(df.index))
        aperture[s] = pd.Series(df["open"].to_numpy() * rett[s].reindex(giorni).to_numpy() / df["close"].to_numpy(), index=giorni)
    settimanale = []
    entrate = [tutti[d][0] for d, _, _ in sett]
    for k, (d, _, _) in enumerate(sett[:-1]):
        e0, e1 = entrate[k], entrate[k + 1]
        nomi = [s for s in tutti[d][1] if e0 in aperture[s].index and e1 in aperture[s].index]
        if nomi and e0 in aperture["SPY"].index and e1 in aperture["SPY"].index:
            r = np.mean([aperture[s][e1] / aperture[s][e0] - 1 for s in nomi])
            settimanale.append(r - (aperture["SPY"][e1] / aperture["SPY"][e0] - 1))
    scelte = [(s, tutti[d][0], v) for d, _, v in sett for s in elenchi[d]]
    veri = sum(depositati(date_c, s, e, v) for s, e, v in scelte) / max(len(scelte), 1)

    usati = set().union(*[set(v) for v in elenchi.values()]) | {"SPY"}
    b = {s: barre[s] for s in usati}
    base = costi_per([s for s in b if s != "SPY"], scarti_misurati(QUI.parent / "dati" / "ESITO_CONTROLLI_UNIVERSO.md"), 1)
    base["SPY"] = Costi(mezzo_scarto=MEZZO_SCARTO["SPY"], slittamento=0.5 * PB, prestito_annuo=PRESTITO_SPY, **IB_FISSO)
    varianti = (("costi", lambda c: c), ("costi doppi", lambda c: c.raddoppiati()), ("senza costi", lambda c: Costi()))
    out = {nome: simula_conto(b, tono.strategia(elenchi, "SPY"), {s: f(base[s]) for s in b}, capitale=CAPITALE,
                              liquida_dopo=LIQUIDA_DOPO) for nome, f in varianti}
    primo = out["costi"].esecuzioni["giorno"].min()
    g = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
    spy_r = rett["SPY"].pct_change().dropna()
    comuni = g["costi"].index.intersection(spy_r.index)
    x, y = spy_r.loc[comuni].to_numpy(), g["costi"].loc[comuni].to_numpy()
    beta = float(np.cov(x, y)[0, 1] / np.var(x, ddof=1))
    scelti = [len(v) for v in elenchi.values()]
    return dict(g=g, out=out, conteggi=conteggi, scelti=scelti, settimanale=np.array(settimanale), veri=veri, beta=beta,
                senza=senza, simboli=len(simboli), con_date=len(set(simboli) & set(date_c)))



def main(finta: bool = False):
    c = calcola(finta)
    g, r = c["g"], c["out"]["costi"]
    gc = g["costi"]
    if finta:
        print(f"PROVA LOCALE con date inventate (non è il risultato): Sharpe {sr(gc):.2f}, senza costi {sr(g['senza costi']):.2f}, "
              f"ordini {len(r.esecuzioni)}, rifiutati {r.rifiutati}, senza barra {r.senza_barra}, liquidati {len(r.liquidati)}, "
              f"commissioni {r.commissioni:,.0f}, scarto {r.costo_scarto:,.0f}; previsti per settimana mediana "
              f"{np.median(c['conteggi']):.0f}, scelti mediana {np.median(c['scelti']):.0f}, settimane fuori "
              f"{sum(1 for x in c['scelti'] if x == 0)} su {len(c['scelti'])}; depositati davvero {c['veri']:.0%}; beta {c['beta']:.2f}; "
              f"settimanale {c['settimanale'].mean():+.3%} (t {t_di(c['settimanale']):.2f}); senza prezzi {len(c['senza'])}")
        return
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P030_premio_comunicato", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P030_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P030_miscela"]
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(g["costi doppi"])
    da_sola = sr_c > sr(spy) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    entra = sr(gc.loc[comuni]) > 0 and sr(g["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c)
    anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
    s = c["settimanale"]
    testo = ["# Prova 30 — risultati", "",
             f"Calcolato da `python -m stock.prove.p030` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P030_premio_del_comunicato.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Membri dell'indice nel periodo {c['simboli']}, con le date dei comunicati {c['con_date']}, senza prezzi {len(c['senza'])}. "
             f"Titoli con la data prevista per settimana: mediana {np.median(c['conteggi']):.0f}, massimo {max(c['conteggi'])}; scelti: "
             f"mediana {np.median(c['scelti']):.0f}; settimane fuori (meno di {MINIMO}) {sum(1 for x in c['scelti'] if x == 0)} su "
             f"{len(c['scelti'])}. **Scelte che hanno depositato davvero un comunicato nella settimana: {c['veri']:.0%}.**",
             f"* Tutti i titoli con la data prevista meno lo SPY, dall'apertura all'apertura, senza costi: **{s.mean():+.3%} a settimana "
             f"(t {t_di(s):.2f})**, mediana {np.median(s):+.3%}, su {len(s)} settimane. Beta della strategia rispetto allo SPY "
             f"{c['beta']:.2f}.",
             f"* Ordini eseguiti {len(r.esecuzioni)}; senza barra {r.senza_barra}; rifiutati {r.rifiutati}; chiusi all'ultimo prezzo "
             f"perché spariti dal listino {len(r.liquidati)}. Costi pagati: commissioni {r.commissioni:,.0f}, scarto e slittamento "
             f"{r.costo_scarto:,.0f} dollari.", "",
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
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(g['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; perdita massima {dd(nuova):.1%} contro {dd(miscela.loc[comuni]):.1%}. **Esito: "
             f"{'entra nella miscela (prima il revisore, poi il periodo chiuso e la misura in avanti)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove (77)."]
    (QUI / "P030_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-16:]))


if __name__ == "__main__":
    main("--finta" in sys.argv)
