"""Prova 31 — la redditività lorda nell'S&P 500: comprati i più redditizi, venduti allo scoperto i meno, un anno (idea I33).

    python -m stock.prove.p031            # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca)
    python -m stock.prove.p031 --finta    # prova del programma in locale, con la redditività mescolata a caso (non è il risultato)

Regole: `P031_redditivita_lorda.md` (scritte e committate prima del calcolo). I conti: `dati/P031_redditivita.csv.gz`
(`stock/dati/conti.py`); i codici SEC: `stock/universo/codici_sec.csv`; la composizione dell'indice: `dati/P028_membri.csv.gz`.
"""
from __future__ import annotations

import math
import sys
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd

from stock.dati import controlli
from stock.prove.p001 import CAPITALE, IB_FISSO, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import prepara_titolo, rendimenti, scarti_misurati
from stock.prove.p011 import costi_per
from stock.prove.p027 import scarica
from stock.prove.p028 import decisioni as fine_mese
from stock.prove.p028 import ritorno
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import Storia, StatoConto, simula_conto, verso_pesi

FINO = date(2024, 12, 31)
RITARDO = timedelta(days=120)
QUOTA, MASSIMO, MINIMO = 0.2, 50, 100
PRESTITO = 0.005
LIQUIDA_DOPO = 5
LEVA_PER_IL_CAMBIO = 2.0
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}

sr = lambda x: annuo(asticella.sharpe(x))  # noqa: E731
tot = lambda x: (1 + x).prod() - 1  # noqa: E731
dd = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min()  # noqa: E731
t_di = lambda x: x.mean() / x.std(ddof=1) * math.sqrt(len(x)) if len(x) > 2 else float("nan")  # noqa: E731


def conti(finta: bool = False) -> tuple[dict[str, int], dict[int, list[tuple[date, float]]], dict[int, int | None]]:
    """Simbolo di allora -> codice SEC; codice -> [(fine dell'esercizio, redditività)] in ordine; codice -> SIC. Con `finta`, la
    redditività è mescolata a caso fra le aziende (solo per provare il programma)."""
    c = pd.read_csv(QUI.parent / "universo" / "codici_sec.csv")
    codice = dict(zip(c["simbolo"], c["cik"].astype(int)))
    tutte = pd.read_csv(QUI / "dati" / "P031_redditivita.csv.gz", parse_dates=["fine"])
    sic = {int(k): (int(v) if v == v else None) for k, v in tutte.drop_duplicates("cik")[["cik", "sic"]].itertuples(index=False)}
    r = tutte.dropna(subset=["redditivita"]).copy()
    if finta:
        r["redditivita"] = np.random.default_rng(31).permutation(r["redditivita"].to_numpy())
    r = r.sort_values(["cik", "fine"])
    red = {int(k): list(zip(g["fine"].dt.date, g["redditivita"])) for k, g in r.groupby("cik")}
    return codice, red, sic


def finanziaria(sic: int | None) -> bool:
    return sic is not None and 6000 <= sic <= 6999


def redditivita_al(esercizi: list[tuple[date, float]], giorno: date) -> float | None:
    """La redditività dell'esercizio più recente chiuso almeno 120 giorni prima del giorno."""
    ok = [v for fine, v in esercizi if fine <= giorno - RITARDO]
    return ok[-1] if ok else None


def scegli(valori: dict[str, float]) -> tuple[list[str], list[str]]:
    """Il 20% più alto e il 20% più basso, al massimo 50 ciascuno; a pari valore in ordine alfabetico; meno di 100: fuori."""
    if len(valori) < MINIMO:
        return [], []
    n = min(int(QUOTA * len(valori)), MASSIMO)
    alti = sorted(valori, key=lambda s: (-valori[s], s))[:n]
    bassi = sorted(valori, key=lambda s: (valori[s], s))[:n]
    return sorted(alti), sorted(bassi)


def strategia(elenchi: dict[date, tuple[list[str], list[str]]]):
    """Metà del conto nei comprati, metà venduta allo scoperto nei venduti, a pesi uguali; elenchi vuoti: tutto chiuso."""
    def decidi(giorno: date, storia: Storia, stato: StatoConto) -> list:
        scelta = elenchi.get(giorno)
        if scelta is None:
            return []
        alti, bassi = scelta
        pesi = {s: 0.5 / len(alti) for s in alti} if alti else {}
        pesi.update({s: -0.5 / len(bassi) for s in bassi} if bassi else {})
        prezzi = {}
        for s in set(pesi) | set(stato.azioni):
            h = storia(s)
            if h is not None and not h.empty:
                prezzi[s] = float(h["close"].iloc[-1])
        return verso_pesi(stato, pesi, prezzi, etichetta="anno")
    return decidi


def calcola(finta: bool = False) -> dict:
    fini, membri = fine_mese()
    giugni = [g for g in fini if g.month == 6 and 2016 <= g.year <= 2024]
    codice, red, sic = conti(finta)
    simboli = sorted(set().union(*[membri[g] for g in giugni]))
    if finta:
        TIPI.update(raw="1Day_raw", az="azioni", asof=None)
    else:
        scarica(["SPY", "QQQ"])
        scarica(simboli + ["SPY"], TIPI["raw"], TIPI["az"], TIPI["asof"])
    barre, rett, senza = {}, {}, []
    for s in simboli:
        try:
            barre[s], rett[s], _ = prepara_titolo(s, FINO, TIPI["raw"], TIPI["az"])
        except Exception as e:  # noqa: BLE001 — titolo senza prezzi: si conta
            senza.append(f"{s} ({type(e).__name__})")
    elenchi, conteggi, anni_ls = {}, [], []
    for k, g in enumerate(giugni):
        valori, fuori = {}, {"senza codice": 0, "finanziarie": 0, "senza conti": 0, "senza barra": 0}
        for s in sorted(membri[g]):
            if s not in rett or g not in rett[s].index:
                fuori["senza barra"] += 1
                continue
            c = codice.get(s)
            if c is None:
                fuori["senza codice"] += 1
            elif finanziaria(sic.get(c)):
                fuori["finanziarie"] += 1
            elif (v := redditivita_al(red.get(c, []), g)) is None:
                fuori["senza conti"] += 1
            else:
                valori[s] = v
        elenchi[g] = scegli(valori)
        conteggi.append((g.year, len(valori), fuori))
        fine = giugni[k + 1] if k + 1 < len(giugni) else FINO
        alti, bassi = elenchi[g]
        if alti:
            la = np.mean([ritorno(rett[s], g, fine) for s in alti])
            lb = np.mean([ritorno(rett[s], g, fine) for s in bassi])
            anni_ls.append((g.year, la - lb))
    usati = set().union(*[set(a) | set(b) for a, b in elenchi.values()])
    b = {s: barre[s] for s in usati}
    base = costi_per(sorted(b), scarti_misurati(QUI.parent / "dati" / "ESITO_CONTROLLI_UNIVERSO.md"), 1)
    base = {s: replace(c, prestito_annuo=PRESTITO) for s, c in base.items()}
    varianti = (("costi", lambda c: c), ("costi doppi", lambda c: c.raddoppiati()), ("senza costi", lambda c: Costi()))
    out = {nome: simula_conto(b, strategia(elenchi), {s: f(base[s]) for s in b}, capitale=CAPITALE, liquida_dopo=LIQUIDA_DOPO,
                              leva_massima=LEVA_PER_IL_CAMBIO) for nome, f in varianti}
    primo = out["costi"].esecuzioni["giorno"].min()
    g = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
    return dict(g=g, out=out, conteggi=conteggi, anni_ls=anni_ls, senza=senza, simboli=len(simboli))


def main(finta: bool = False):
    c = calcola(finta)
    g, r = c["g"], c["out"]["costi"]
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    comuni_spy = gc.index.intersection(spy.index)
    beta = float(np.cov(spy.loc[comuni_spy], gc.loc[comuni_spy])[0, 1] / np.var(spy.loc[comuni_spy], ddof=1))
    qmeno = (comprare_e_tenere("QQQ", a, b) - spy).dropna()
    cq = gc.index.intersection(qmeno.index)
    corr_q = float(np.corrcoef(qmeno.loc[cq], gc.loc[cq])[0, 1])
    if finta:
        print(f"PROVA LOCALE con la redditività mescolata (non è il risultato): Sharpe {sr(gc):.2f}, senza costi "
              f"{sr(g['senza costi']):.2f}, ordini {len(r.esecuzioni)}, rifiutati {r.rifiutati}, senza barra {r.senza_barra}, "
              f"liquidati {len(r.liquidati)}, commissioni {r.commissioni:,.0f}, scarto {r.costo_scarto:,.0f}; aziende per anno "
              f"{[n for _, n, _ in c['conteggi']]}; fuori {c['conteggi'][0][2]}; beta {beta:.2f}; corr QQQ-SPY {corr_q:.2f}; "
              f"senza prezzi {len(c['senza'])}")
        return
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P031_redditivita", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P031_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P031_miscela"]
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
    ls = np.array([x for _, x in c["anni_ls"]])
    testo = ["# Prova 31 — risultati", "",
             f"Calcolato da `python -m stock.prove.p031` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P031_redditivita_lorda.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Membri dell'indice nelle decisioni {c['simboli']}, senza prezzi {len(c['senza'])}. Aziende con la redditività, per "
             f"anno: " + ", ".join(f"{y} {n}" for y, n, _ in c["conteggi"]) + f". Fuori nell'ultimo anno: {c['conteggi'][-1][2]}.",
             f"* Comprati meno venduti, da giugno a giugno, senza costi: " + ", ".join(f"{y} {x:+.1%}" for y, x in c["anni_ls"])
             + f"; media {ls.mean():+.1%} l'anno (t {t_di(ls):.2f}). Beta rispetto allo SPY {beta:.2f}; **correlazione con QQQ meno "
             f"SPY {corr_q:.2f}**.",
             f"* Ordini eseguiti {len(r.esecuzioni)}; senza barra {r.senza_barra}; rifiutati {r.rifiutati}; chiusi all'ultimo prezzo "
             f"perché spariti dal listino {len(r.liquidati)}. Costi pagati: commissioni {r.commissioni:,.0f}, scarto e slittamento "
             f"{r.costo_scarto:,.0f} dollari (il prestito è nel valore del conto).", "",
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
             "Nel conto: 2 prove (79)."]
    (QUI / "P031_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-16:]))


if __name__ == "__main__":
    main("--finta" in sys.argv)
