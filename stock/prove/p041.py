"""Prova 41 — «lazy prices» nell'S&P 500: comprate le 50 aziende il cui ultimo bilancio somiglia di più a quello dell'anno prima,
vendute allo scoperto le 50 che lo hanno cambiato di più, ogni mese (idea I40; Cohen, Malloy e Nguyen 2020).

    python -m stock.prove.p041            # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca)
    python -m stock.prove.p041 --finta    # prova del programma in locale, con il segnale mescolato a caso (non è il risultato)

Regole: `P041_lazy_prices.md` (scritte e committate prima del calcolo). Le somiglianze: `dati/P041_somiglianze.csv.gz`
(`stock/dati/testi_bilanci.py`); i codici SEC di allora: `dati/P039_codici.csv.gz`; la composizione dell'indice: `dati/P028_membri.csv.gz`.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd

from stock.dati.archivio import cartella_dati
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
QUATTRO_MESI = timedelta(days=122)
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}


def carica_somiglianze(finta: bool = False) -> dict[int, list[tuple[date, float]]]:
    """Codice SEC → [(deposito, somiglianza)] in ordine di deposito. Con `finta`, dai file per azienda già fatti in locale."""
    if finta:
        pezzi = [pd.read_csv(f) for f in (cartella_dati() / "sec" / "somiglianze").glob("*.csv")]
        s = pd.concat(pezzi)
    else:
        s = pd.read_csv(QUI / "dati" / "P041_somiglianze.csv.gz")
    s = s.dropna(subset=["somiglianza"])
    s["deposito"] = pd.to_datetime(s["deposito"]).dt.date
    return {int(k): sorted(zip(g["deposito"], g["somiglianza"].astype(float))) for k, g in s.groupby("cik")}


def segnale(bilanci: list[tuple[date, float]], giorno: date) -> float | None:
    """La somiglianza del bilancio più recente depositato prima del giorno e non più di 4 mesi prima."""
    noti = [(d, v) for d, v in bilanci if d < giorno and giorno - d <= QUATTRO_MESI]
    return max(noti)[1] if noti else None


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
    c = pd.read_csv(QUI / "dati" / "P039_codici.csv.gz", dtype={"simbolo": str}, keep_default_na=False, parse_dates=["giorno"])
    codici = {s: sorted(zip(g["giorno"].dt.date, g["cik"].astype(int))) for s, g in c.groupby("simbolo")}
    somi = carica_somiglianze(finta)
    rng = np.random.default_rng(41)
    elenchi, mesi, cambi, con_segnale, mediane = {}, [], [], [], []
    prima = (set(), set())
    fuori = {"senza prezzo": 0, "senza codice": 0, "senza bilancio recente": 0}
    for k in decisioni:
        g, g_dopo = fini[k], fini[k + 1]
        v = {}
        for s in sorted(membri[g]):
            if s not in rett or g not in rett[s].index:
                fuori["senza prezzo"] += 1
                continue
            cik = codice_al(codici.get(s, []), g)
            if cik is None:
                fuori["senza codice"] += 1
                continue
            x = segnale(somi.get(cik, []), g)
            if x is None:
                fuori["senza bilancio recente"] += 1
                continue
            v[s] = x
        con_segnale.append(len(v))
        if finta and v:
            chiavi = list(v)
            v = dict(zip(chiavi, rng.permutation(list(v.values()))))
        alti, bassi = scegli(v)                       # alti: la somiglianza più alta (comprati), bassi: la più bassa (venduti)
        elenchi[g] = (alti, bassi)
        if not alti:
            continue
        mediane.append((g.year, float(np.median([v[s] for s in alti])), float(np.median([v[s] for s in bassi])),
                        float(np.median(list(v.values())))))
        ra = [ritorno(rett[s], g, g_dopo) for s in alti]
        rb = [ritorno(rett[s], g, g_dopo) for s in bassi]
        mesi.append((g_dopo, float(np.mean(ra) - np.mean(rb))))
        if prima[0]:
            cambi.append((len(set(alti) - prima[0]) / len(alti), len(set(bassi) - prima[1]) / len(bassi)))
        prima = (set(alti), set(bassi))
    usati = set().union(*[set(a) | set(b) for a, b in elenchi.values()])
    b = {s: barre[s] for s in usati}
    base = costi_per(sorted(b), scarti_misurati(QUI.parent / "dati" / "ESITO_CONTROLLI_UNIVERSO.md"), 1)
    base = {s: replace(cc, prestito_annuo=PRESTITO) for s, cc in base.items()}
    varianti = (("costi", lambda x: x), ("costi doppi", lambda x: x.raddoppiati()), ("senza costi", lambda x: Costi()))
    out = {nome: simula_conto(b, strategia(elenchi), {s: f(base[s]) for s in b}, capitale=CAPITALE, liquida_dopo=LIQUIDA_DOPO,
                              leva_massima=LEVA_PER_IL_CAMBIO) for nome, f in varianti}
    primo = out["costi"].esecuzioni["giorno"].min()
    gg = {kk: rendimenti(vv.valore[vv.valore.index >= primo]) for kk, vv in out.items()}
    return dict(g=gg, out=out, mesi=mesi, cambi=cambi, con_segnale=con_segnale, mediane=mediane, fuori=fuori, senza=senza,
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
              f"ordini {len(r.esecuzioni)}, commissioni {r.commissioni:,.0f}; mesi {len(ls)}; con il segnale per mese "
              f"{c['con_segnale'][:3]}…{c['con_segnale'][-2:]}; fuori {c['fuori']}; senza prezzi {len(c['senza'])}")
        return
    spy = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P041_lazy_prices", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P041_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P041_miscela"]
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
    med = pd.DataFrame(c["mediane"], columns=["anno", "comprati", "venduti", "tutti"])
    per_anno = med.groupby("anno")["tutti"].median()
    prima20 = np.array([x for d, x in c["mesi"] if d.year < 2020])
    dopo20 = np.array([x for d, x in c["mesi"] if d.year >= 2020])
    testo = ["# Prova 41 — risultati", "",
             f"Calcolato da `python -m stock.prove.p041` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P041_lazy_prices.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Membri dell'indice nelle decisioni {c['simboli']}, senza prezzi {len(c['senza'])}; con il segnale per mese: mediana "
             f"{np.median(c['con_segnale']):.0f} (minimo {min(c['con_segnale'])}); fuori, sommati sui mesi: {c['fuori']}. Ordini "
             f"{len(r.esecuzioni)}, liquidati {len(r.liquidati)}; commissioni {r.commissioni:,.0f} dollari, scarto {r.costo_scarto:,.0f}.",
             f"* Somiglianza mediana: comprati {med['comprati'].mean():.4f}, venduti {med['venduti'].mean():.4f}; di tutti, per anno: "
             + " ".join(f"{y}: {x:.4f}" for y, x in per_anno.items()) + ".",
             f"* **Comprati meno venduti, il mese dopo, prima dei costi: {ls.mean():+.2%} al mese (t {t_di(ls):.2f})**, mesi positivi "
             f"{(ls > 0).mean():.0%}; prima del 2020 {prima20.mean():+.2%} (t {t_di(prima20):.2f}), dal 2020 {dopo20.mean():+.2%} (t "
             f"{t_di(dopo20):.2f}). Ogni mese cambia il {cambi[:, 0].mean():.0%} dei comprati e il {cambi[:, 1].mean():.0%} dei venduti.", "",
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
             "Nel conto: 2 prove (99)."]
    (QUI / "P041_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-20:]))


if __name__ == "__main__":
    main(finta="--finta" in sys.argv)
