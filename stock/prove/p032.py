"""Prova 32 — comprare le aziende piccole meno vendute allo scoperto (pochi giorni per ricomprare, FINRA), coperte con l'IWM (I34).

    python -m stock.prove.p032            # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca)
    python -m stock.prove.p032 --finta    # prova del programma in locale: titoli dell'archivio locale, giorni per ricomprare a caso

Regole: `P032_poco_vendute_piccole.md` (scritte e committate prima del calcolo, con l'aggiunta sui dati). FINRA si scarica dal lavoro
(pubblico, senza chiave) e non entra nel repository; il programma non legge date di FINRA dopo il 31 dicembre 2024.
"""
from __future__ import annotations

import math
import re
import sys
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli, finra
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import prepara_titolo, rendimenti
from stock.prove.p027 import DOLLARI_MINIMI, PREZZO_MINIMO, SEDUTE_DOLLARI, scarica
from stock.prove.p028 import decisioni as fine_mese
from stock.prove.p028 import ritorno
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import tono

FINO = date(2024, 12, 31)
PRIMA = date(2018, 1, 31)
ATTESA = timedelta(days=14)
QUOTA, MASSIMO, MINIMO = 0.2, 50, 25
COSTI = Costi(mezzo_scarto=15 * PB, slittamento=5 * PB, **IB_FISSO)
PRESTITO_IWM = 0.01
LIQUIDA_DOPO = 5
FONDO = "IWM"
ORDINARIE = re.compile(r"[A-Z]{1,4}(\.[AB])?")
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}
BLOCCO, RIPETIZIONI = 20, 2000

sr = lambda x: annuo(asticella.sharpe(x))  # noqa: E731
tot = lambda x: (1 + x).prod() - 1  # noqa: E731
dd = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min()  # noqa: E731
t_di = lambda x: float(np.mean(x) / np.std(x, ddof=1) * math.sqrt(len(x))) if len(x) > 2 else float("nan")  # noqa: E731


def vendite_scoperto(finta: bool = False) -> dict[date, dict[str, float]]:
    """Data di regolamento -> {simbolo: giorni per ricomprare} (vendute / volume medio, senza il pavimento a 1 del campo di FINRA),
    solo fino al 31 dicembre 2024 e per i simboli delle azioni ordinarie."""
    f = archivio.cartella_dati() / "finra" / "vendite_scoperto.csv.gz"
    if not f.exists():
        finra.scarica(date(2018, 1, 1), FINO)
    d = pd.read_csv(f, usecols=["settlementDate", "symbolCode", "currentShortPositionQuantity", "averageDailyVolumeQuantity"])
    d = d[(d["settlementDate"] <= FINO.isoformat()) & (d["averageDailyVolumeQuantity"] > 0)]
    d = d[d["symbolCode"].astype(str).str.fullmatch(ORDINARIE.pattern)]
    d["giorni"] = d["currentShortPositionQuantity"] / d["averageDailyVolumeQuantity"]
    if finta:
        d["giorni"] = np.random.default_rng(32).permutation(d["giorni"].to_numpy())
    return {date.fromisoformat(k): dict(zip(g["symbolCode"], g["giorni"])) for k, g in d.groupby("settlementDate")}


def data_valida(regolamenti: list[date], giorno: date) -> date | None:
    """L'ultima data di regolamento almeno 14 giorni prima della decisione (FINRA pubblica circa 7 giorni di borsa dopo)."""
    ok = [r for r in regolamenti if r <= giorno - ATTESA]
    return max(ok) if ok else None


def scegli(giorni: dict[str, float], ammessi: set[str]) -> list[str]:
    """Il 20% con meno giorni per ricomprare, al massimo 50, a pari valore in ordine alfabetico; meno di 25 ammessi: fuori."""
    a = sorted(s for s in ammessi if s in giorni)
    if len(a) < MINIMO:
        return []
    return sorted(sorted(a, key=lambda s: (giorni[s], s))[:min(int(QUOTA * len(a)), MASSIMO)])


def campionamento(miscela: pd.Series, parte: pd.Series, seme: int = 32) -> float:
    """La quota di campionamenti a blocchi di 20 giorni (gli stessi giorni per le due serie) in cui la miscela nuova (3/4 miscela,
    1/4 parte) ha lo Sharpe più alto della miscela."""
    m, p = miscela.to_numpy(), parte.to_numpy()
    n = len(m)
    rng = np.random.default_rng(seme)
    vinte = 0
    for _ in range(RIPETIZIONI):
        inizi = rng.integers(0, n - BLOCCO + 1, size=math.ceil(n / BLOCCO))
        i = (inizi[:, None] + np.arange(BLOCCO)).ravel()[:n]
        a, b = m[i], 0.75 * m[i] + 0.25 * p[i]
        vinte += b.mean() / b.std(ddof=1) > a.mean() / a.std(ddof=1)
    return vinte / RIPETIZIONI


def calcola(finta: bool = False) -> dict:
    global FONDO
    if finta:
        FONDO = "QQQ"                  # in locale non c'è l'IWM: solo per provare il programma
    fini, membri = fine_mese()
    giorni = [g for g in fini if PRIMA <= g <= FINO]
    vs = vendite_scoperto(finta)
    regolamenti = sorted(vs)
    valida = {g: data_valida(regolamenti, g) for g in giorni}
    if finta:
        TIPI.update(raw="1Day_raw", az="azioni", asof=None)
        locali = {p.name for p in archivio.cartella_dati().iterdir() if p.is_dir()}
        membri = {g: set() for g in membri}
        candidati = sorted({s for g in giorni[:-1] for s in vs[valida[g]] if s in locali} - {FONDO, "SPY"})
        nomi = {}
    else:
        candidati = sorted({s for g in giorni[:-1] for s in vs[valida[g]] if s not in membri[g]} - {FONDO})
        print(f"candidati {len(candidati)}", flush=True)
        scarica(["SPY"])
        scarica(candidati + [FONDO], TIPI["raw"], TIPI["az"], TIPI["asof"])
        nomi = alpaca.nomi_dei_titoli()
    fondi = {s for s in candidati if tono.e_un_fondo(nomi.get(s, ""))}
    chiusure, dollari = {}, {}
    for s in candidati:
        df = archivio.carica(s, TIPI["raw"])
        if s in fondi or df is None or len(df) <= SEDUTE_DOLLARI:
            continue
        i = pd.Index(controlli.date_ny(df.index))
        chiusure[s] = pd.Series(df["close"].to_numpy(), index=i)
        dollari[s] = pd.Series((df["close"] * df["volume"]).to_numpy(), index=i)

    def comprabile(s: str, g: date) -> bool:
        c = chiusure.get(s)
        if c is None or g not in c.index or c.loc[g] < PREZZO_MINIMO:
            return False
        v = dollari[s].loc[:g].iloc[:-1].iloc[-SEDUTE_DOLLARI:]
        return len(v) == SEDUTE_DOLLARI and float(v.median()) >= DOLLARI_MINIMI
    ammessi = {g: {s for s in vs[valida[g]] if s not in membri[g] and comprabile(s, g)} for g in giorni[:-1]}
    barre, rett, rotti = {}, {}, []
    for s in sorted(set().union(*ammessi.values())) + [FONDO]:
        try:
            barre[s], rett[s], _ = prepara_titolo(s, FINO, TIPI["raw"], TIPI["az"])
        except Exception as e:  # noqa: BLE001 — titolo con i dati rotti: si conta e resta fuori
            rotti.append(f"{s} ({type(e).__name__})")
    ammessi = {g: {s for s in a if s in barre} for g, a in ammessi.items()}
    elenchi = {g: scegli(vs[valida[g]], ammessi[g]) for g in giorni[:-1]}
    elenchi[giorni[-1]] = []
    # i quinti, mese dopo, senza costi (da chiusura a chiusura)
    basso_alto, basso_fondo = [], []
    for k, g0 in enumerate(giorni[:-1]):
        g1 = giorni[k + 1]
        o = sorted((s for s in ammessi[g0] if g0 in rett[s].index), key=lambda s: (vs[valida[g0]][s], s))
        q = int(QUOTA * len(o))
        if q >= 5 and g0 in rett[FONDO].index:
            b = np.mean([ritorno(rett[s], g0, g1) for s in o[:q]])
            a = np.mean([ritorno(rett[s], g0, g1) for s in o[-q:]])
            basso_alto.append(b - a)
            basso_fondo.append(b - ritorno(rett[FONDO], g0, g1))
    usati = set().union(*[set(v) for v in elenchi.values()]) | {FONDO}
    bb = {s: barre[s] for s in usati}
    base = {s: COSTI for s in bb}
    base[FONDO] = replace(COSTI, prestito_annuo=PRESTITO_IWM)
    varianti = (("costi", lambda c: c), ("costi doppi", lambda c: c.raddoppiati()), ("senza costi", lambda c: Costi()))
    out = {nome: simula_conto(bb, tono.strategia(elenchi, FONDO), {s: f(base[s]) for s in bb}, capitale=CAPITALE,
                              liquida_dopo=LIQUIDA_DOPO) for nome, f in varianti}
    primo = out["costi"].esecuzioni["giorno"].min()
    g = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
    return dict(g=g, out=out, elenchi=elenchi, ammessi=ammessi, basso_alto=np.array(basso_alto), basso_fondo=np.array(basso_fondo),
                candidati=len(candidati), fondi=len(fondi), senza=len(candidati) - len(fondi) - len(chiusure), rotti=len(rotti))


def main(finta: bool = False):
    c = calcola(finta)
    g, r = c["g"], c["out"]["costi"]
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    cs = gc.index.intersection(spy.index)
    corr_spy = float(np.corrcoef(spy.loc[cs], gc.loc[cs])[0, 1])
    n_amm = [len(v) for k, v in c["ammessi"].items()]
    scelti = [len(v) for k, v in c["elenchi"].items() if k in c["ammessi"]]
    if finta:
        print(f"PROVA LOCALE con giorni per ricomprare a caso (non è il risultato): Sharpe {sr(gc):.2f}, senza costi "
              f"{sr(g['senza costi']):.2f}, ordini {len(r.esecuzioni)}, rifiutati {r.rifiutati}, senza barra {r.senza_barra}, "
              f"liquidati {len(r.liquidati)}, commissioni {r.commissioni:,.0f}, scarto {r.costo_scarto:,.0f}; ammessi mediana "
              f"{np.median(n_amm):.0f}, scelti mediana {np.median(scelti):.0f}, mesi fuori {sum(1 for x in scelti if x == 0)} su "
              f"{len(scelti)}; quinti {c['basso_alto'].mean():+.2%} (t {t_di(c['basso_alto']):.2f}); corr SPY {corr_spy:.2f}; "
              f"campionamento di prova {campionamento(gc.iloc[:400], gc.iloc[400:800].set_axis(gc.index[:400])):.0%}")
        return
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P032_poco_vendute", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P032_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P032_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(g["costi doppi"])
    da_sola = sr_c > sr(spy) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte = t_di(gc.to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(g["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8
    anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
    ba, bf = c["basso_alto"], c["basso_fondo"]
    testo = ["# Prova 32 — risultati", "",
             f"Calcolato da `python -m stock.prove.p032` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P032_poco_vendute_piccole.md` (committate prima, con l'aggiunta sui dati). Dal {a} al {b}. Nel conto dell'asticella: "
             f"{len(tutte)} serie.", "",
             f"* Candidati (simboli di FINRA fuori dall'indice) {c['candidati']}, fondi esclusi {c['fondi']}, senza prezzi {c['senza']}, "
             f"con i dati rotti {c['rotti']}. Titoli ammessi per mese: mediana {np.median(n_amm):.0f}, minimo {min(n_amm)}; scelti: "
             f"mediana {np.median(scelti):.0f}; mesi fuori {sum(1 for x in scelti if x == 0)} su {len(scelti)}.",
             f"* Mese dopo, senza costi, da chiusura a chiusura: il quinto con meno giorni per ricomprare meno il quinto con più giorni "
             f"**{ba.mean():+.2%} al mese (t {t_di(ba):.2f})**, mediana {np.median(ba):+.2%}; il quinto basso meno l'IWM "
             f"**{bf.mean():+.2%} al mese (t {t_di(bf):.2f})**; su {len(ba)} mesi. Correlazione con lo SPY {corr_spy:.2f}.",
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
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**; perdita massima {dd(nuova):.1%} contro {dd(miscela.loc[comuni]):.1%}. "
             f"**Esito: {'entra nella miscela (prima il revisore, poi il periodo chiuso e la misura in avanti)' if entra else 'non entra'}**",
             "", "Nel conto: 2 prove (81)."]
    (QUI / "P032_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-16:]))


if __name__ == "__main__":
    main("--finta" in sys.argv)
