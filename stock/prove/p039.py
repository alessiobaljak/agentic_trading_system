"""Prova 39 — l'emissione netta di azioni nell'S&P 500: comprate le 50 aziende che hanno ridotto di più le azioni in un anno, vendute
allo scoperto le 50 che le hanno aumentate di più, ogni mese (idea I42; Pontiff e Woodgate 2008, Fama e French 2008).

    python -m stock.prove.p039            # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca)
    python -m stock.prove.p039 --finta    # prova del programma in locale, con il segnale mescolato a caso (non è il risultato)

Regole: `P039_emissione_netta.md` (scritte e committate prima del calcolo). Dati pubblici della SEC: `dati/P039_codici.csv.gz` e
`dati/P039_azioni.csv.gz` (`stock/dati/azioni_circolazione.py`); la composizione dell'indice: `dati/P028_membri.csv.gz`.
"""
from __future__ import annotations

import math
import sys
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd

from stock.dati import controlli
from stock.dati.azioni_circolazione import codice_al
from stock.prove.p001 import CAPITALE, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import prepara_titolo, rendimenti, scarti_misurati
from stock.prove.p011 import costi_per
from stock.prove.p027 import scarica
from stock.prove.p028 import decisioni as fine_mese
from stock.prove.p028 import ritorno
from stock.prove.p031 import LEVA_PER_IL_CAMBIO, LIQUIDA_DOPO, PRESTITO, scegli, strategia
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto

FINO = date(2024, 12, 31)
PRIMA_DECISIONE = date(2017, 1, 1)
DA, A = timedelta(days=273), timedelta(days=456)          # fra 9 e 15 mesi prima
DODICI = timedelta(days=365)
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}


def carica_dati() -> tuple[dict[str, list[tuple[date, int]]], dict[int, list[tuple[date, date, float]]]]:
    """Simbolo → [(giorno, codice)] in ordine; codice → [(deposito, data di riferimento, azioni)] in ordine di deposito."""
    c = pd.read_csv(QUI / "dati" / "P039_codici.csv.gz", dtype={"simbolo": str}, keep_default_na=False, parse_dates=["giorno"])
    codici = {s: sorted(zip(g["giorno"].dt.date, g["cik"].astype(int))) for s, g in c.groupby("simbolo")}
    a = pd.read_csv(QUI / "dati" / "P039_azioni.csv.gz", parse_dates=["fine", "deposito"])
    azioni = {int(k): sorted(zip(g["deposito"].dt.date, g["fine"].dt.date, g["azioni"].astype(float))) for k, g in a.groupby("cik")}
    return codici, azioni


def emissione(dichiarazioni: list[tuple[date, date, float]], giorno: date, frazionamenti: dict[date, float]) -> float | None:
    """log(azioni in d1 / (azioni in d0 × frazionamenti fra d0 e d1)): d1 la data di riferimento dell'ultimo deposito fatto prima di
    `giorno`; d0 quella più vicina a 12 mesi prima di d1, fra 9 e 15 mesi prima, fra i depositi fatti prima di `giorno`."""
    noti = [x for x in dichiarazioni if x[0] < giorno and x[2] > 0]
    if not noti:
        return None
    _, d1, s1 = max(noti, key=lambda x: (x[0], x[1]))
    candidati = [x for x in noti if DA <= d1 - x[1] <= A]
    if not candidati:
        return None
    _, d0, s0 = min(candidati, key=lambda x: (abs((d1 - x[1]) - DODICI), -x[0].toordinal()))
    f = math.prod(r for d, r in frazionamenti.items() if d0 < d <= d1)
    return math.log(s1 / (s0 * f))


def calcola(finta: bool = False) -> dict:
    fini, membri = fine_mese()
    decisioni = [k for k, g in enumerate(fini) if PRIMA_DECISIONE <= g and k + 1 < len(fini)]
    simboli = sorted(set().union(*[membri[fini[k]] for k in decisioni]))
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
    fraz = {s: {d: float(r) for d, r in zip(controlli.date_ny(df.index), df["frazionamento"]) if r != 1.0} for s, df in barre.items()}
    codici, azioni = carica_dati()
    rng = np.random.default_rng(39)
    elenchi, mesi, cambi, con_segnale, mediane = {}, [], [], [], []
    prima = (set(), set())
    fuori_tot = {"senza codice": 0, "senza due dichiarazioni": 0, "senza prezzo": 0}
    for k in decisioni:
        g, g_dopo = fini[k], fini[k + 1]
        v = {}
        for s in sorted(membri[g]):
            if s not in rett or g not in rett[s].index:
                fuori_tot["senza prezzo"] += 1
                continue
            cik = codice_al(codici.get(s, []), g)
            if cik is None:
                fuori_tot["senza codice"] += 1
                continue
            e = emissione(azioni.get(cik, []), g, fraz.get(s, {}))
            if e is None:
                fuori_tot["senza due dichiarazioni"] += 1
                continue
            v[s] = e
        con_segnale.append(len(v))
        if finta and v:
            chiavi = list(v)
            v = dict(zip(chiavi, rng.permutation(list(v.values()))))
        alti, bassi = scegli({s: -x for s, x in v.items()})        # alti: l'emissione più bassa (comprati)
        elenchi[g] = (alti, bassi)
        if not alti:
            continue
        mediane.append((float(np.median([v[s] for s in alti])), float(np.median([v[s] for s in bassi]))))
        ra = [ritorno(rett[s], g, g_dopo) for s in alti]
        rb = [ritorno(rett[s], g, g_dopo) for s in bassi]
        mesi.append((g_dopo, float(np.mean(ra) - np.mean(rb))))
        if prima[0]:
            cambi.append((len(set(alti) - prima[0]) / len(alti), len(set(bassi) - prima[1]) / len(bassi)))
        prima = (set(alti), set(bassi))
    usati = set().union(*[set(a) | set(b) for a, b in elenchi.values()])
    b = {s: barre[s] for s in usati}
    base = costi_per(sorted(b), scarti_misurati(QUI.parent / "dati" / "ESITO_CONTROLLI_UNIVERSO.md"), 1)
    base = {s: replace(c, prestito_annuo=PRESTITO) for s, c in base.items()}
    varianti = (("costi", lambda c: c), ("costi doppi", lambda c: c.raddoppiati()), ("senza costi", lambda c: Costi()))
    out = {nome: simula_conto(b, strategia(elenchi), {s: f(base[s]) for s in b}, capitale=CAPITALE, liquida_dopo=LIQUIDA_DOPO,
                              leva_massima=LEVA_PER_IL_CAMBIO) for nome, f in varianti}
    primo = out["costi"].esecuzioni["giorno"].min()
    gg = {kk: rendimenti(vv.valore[vv.valore.index >= primo]) for kk, vv in out.items()}
    return dict(g=gg, out=out, mesi=mesi, cambi=cambi, con_segnale=con_segnale, mediane=mediane, fuori=fuori_tot, senza=senza,
                simboli=len(simboli))


def main(finta: bool = False):
    c = calcola(finta)
    g, r = c["g"], c["out"]["costi"]
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    ls = np.array([x for _, x in c["mesi"]])
    cambi = np.array(c["cambi"]) if c["cambi"] else np.zeros((1, 2))
    if finta:
        print(f"PROVA LOCALE con il segnale mescolato (non è il risultato): Sharpe {sr(gc):.2f}, senza costi {sr(g['senza costi']):.2f}, "
              f"ordini {len(r.esecuzioni)}, rifiutati {r.rifiutati}, liquidati {len(r.liquidati)}, commissioni {r.commissioni:,.0f}; "
              f"mesi {len(ls)}; con il segnale per mese {c['con_segnale'][:4]}…{c['con_segnale'][-2:]}; fuori {c['fuori']}; "
              f"senza prezzi {len(c['senza'])}")
        return
    spy = comprare_e_tenere("SPY", a, b)
    qmeno = (comprare_e_tenere("QQQ", a, b) - spy).dropna()
    cq = gc.index.intersection(qmeno.index)
    corr_q = float(np.corrcoef(qmeno.loc[cq], gc.loc[cq])[0, 1])
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P039_emissione", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P039_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P039_miscela"]
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
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1
    med = np.array(c["mediane"])
    testo = ["# Prova 39 — risultati", "",
             f"Calcolato da `python -m stock.prove.p039` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P039_emissione_netta.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Membri dell'indice nelle decisioni {c['simboli']}, senza prezzi {len(c['senza'])}; con il segnale per mese: mediana "
             f"{np.median(c['con_segnale']):.0f} (minimo {min(c['con_segnale'])}); fuori, sommati sui mesi: {c['fuori']}. Ordini "
             f"{len(r.esecuzioni)}, liquidati {len(r.liquidati)}; commissioni {r.commissioni:,.0f} dollari, scarto {r.costo_scarto:,.0f}.",
             f"* Emissione mediana in un anno: comprati {np.mean(med[:, 0]):+.1%}, venduti {np.mean(med[:, 1]):+.1%} (in logaritmi).",
             f"* **Comprati meno venduti, il mese dopo, prima dei costi: {ls.mean():+.2%} al mese (t {t_di(ls):.2f})**, mesi positivi "
             f"{(ls > 0).mean():.0%}. Ogni mese cambia il {cambi[:, 0].mean():.0%} dei comprati e il {cambi[:, 1].mean():.0%} dei venduti. "
             f"Correlazione con QQQ meno SPY: {corr_q:.2f}.", "",
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
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove (95)."]
    (QUI / "P039_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-20:]))


if __name__ == "__main__":
    main(finta="--finta" in sys.argv)
