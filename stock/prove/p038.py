"""Prova 38 — la stagionalità dello stesso mese nell'S&P 500: comprate le 50 salite di più nello stesso mese dell'anno prima, vendute
allo scoperto le 50 scese di più, ogni mese (idea I45; Heston e Sadka 2008).

    python -m stock.prove.p038            # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca)
    python -m stock.prove.p038 --finta    # prova del programma in locale, con il segnale mescolato a caso (non è il risultato)

Regole: `P038_stagionalita.md` (scritte e committate prima del calcolo). La composizione dell'indice: `dati/P028_membri.csv.gz`; i
comunicati sui risultati (solo da leggere): `dati/P030_comunicati.csv.gz`.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

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
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}


def segnali(fini: list[date], k: int, membri: set[str], rett: dict[str, pd.Series]) -> dict[str, float]:
    """Alla decisione fini[k] (fine del mese m−1): il rendimento di ogni membro nel mese m dell'anno prima, cioè da fini[k−12] (fine del
    mese m−1 dell'anno prima) a fini[k−11] (fine del mese m dell'anno prima). Fuori chi non ha il prezzo in uno dei due giorni."""
    g0, g1 = fini[k - 12], fini[k - 11]
    out = {}
    for s in sorted(membri):
        r = rett.get(s)
        if r is None or g0 not in r.index or g1 not in r.index:
            continue
        out[s] = ritorno(r, g0, g1)
    return out


def mese_con_comunicato(comunicati: dict[str, set[tuple[int, int]]], s: str, anno: int, mese: int) -> bool:
    return (anno, mese) in comunicati.get(s, set())


def calcola(finta: bool = False) -> dict:
    fini, membri = fine_mese()
    decisioni = [k for k, g in enumerate(fini) if PRIMA_DECISIONE <= g and k + 1 < len(fini) and k >= 12]
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
    com = pd.read_csv(QUI / "dati" / "P030_comunicati.csv.gz", dtype={"simbolo_allora": str}, keep_default_na=False,
                      parse_dates=["deposito"])
    comunicati: dict[str, set[tuple[int, int]]] = {}
    for s, d in zip(com["simbolo_allora"], com["deposito"]):
        comunicati.setdefault(s, set()).add((d.year, d.month))
    rng = np.random.default_rng(38)
    elenchi, mesi, cambi, quote = {}, [], [], []
    prima = (set(), set())
    for k in decisioni:
        g, g_dopo = fini[k], fini[k + 1]
        v = segnali(fini, k, membri[g], rett)
        if finta and v:
            chiavi = list(v)
            v = dict(zip(chiavi, rng.permutation(list(v.values()))))
        alti, bassi = scegli(v)
        elenchi[g] = (alti, bassi)
        if not alti:
            continue
        anno_prima, mese = g_dopo.year - 1, g_dopo.month
        ra = {s: ritorno(rett[s], g, g_dopo) for s in alti if g in rett[s].index}
        rb = {s: ritorno(rett[s], g, g_dopo) for s in bassi if g in rett[s].index}
        ca = {s for s in alti if mese_con_comunicato(comunicati, s, anno_prima, mese)}
        cb = {s for s in bassi if mese_con_comunicato(comunicati, s, anno_prima, mese)}
        senza_c = (np.mean([x for s, x in ra.items() if s not in ca]) if len(ra) > len(ca) else np.nan) - \
                  (np.mean([x for s, x in rb.items() if s not in cb]) if len(rb) > len(cb) else np.nan)
        mesi.append((g_dopo, float(np.mean(list(ra.values())) - np.mean(list(rb.values()))), float(senza_c), len(v)))
        quote.append((len(ca) / len(alti), len(cb) / len(bassi)))
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
    gg = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
    return dict(g=gg, out=out, mesi=mesi, cambi=cambi, quote=quote, senza=senza, simboli=len(simboli))


def main(finta: bool = False):
    c = calcola(finta)
    g, r = c["g"], c["out"]["costi"]
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    ls = np.array([x for _, x, _, _ in c["mesi"]])
    if finta:
        print(f"PROVA LOCALE con il segnale mescolato (non è il risultato): Sharpe {sr(gc):.2f}, senza costi {sr(g['senza costi']):.2f}, "
              f"ordini {len(r.esecuzioni)}, rifiutati {r.rifiutati}, senza barra {r.senza_barra}, liquidati {len(r.liquidati)}, "
              f"commissioni {r.commissioni:,.0f}, scarto {r.costo_scarto:,.0f}; mesi {len(ls)}, candidati per mese "
              f"{[n for *_, n in c['mesi']][:6]}; cambio medio {np.mean(c['cambi'], axis=0) if c['cambi'] else '—'}; "
              f"senza prezzi {len(c['senza'])}")
        return
    spy = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P038_stagionalita", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P038_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P038_miscela"]
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
    senza_c = np.array([x for _, _, x, _ in c["mesi"] if np.isfinite(x)])
    cambi = np.array(c["cambi"]) if c["cambi"] else np.zeros((1, 2))
    quote = np.array(c["quote"])
    no2020 = gc[[x.year != 2020 for x in gc.index]]
    testo = ["# Prova 38 — risultati", "",
             f"Calcolato da `python -m stock.prove.p038` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P038_stagionalita.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Membri dell'indice nelle decisioni {c['simboli']}, senza prezzi {len(c['senza'])}; mesi {len(ls)}, candidati per mese "
             f"mediana {np.median([n for *_, n in c['mesi']]):.0f}. Ordini {len(r.esecuzioni)}, rifiutati {r.rifiutati}, liquidati "
             f"{len(r.liquidati)}; commissioni {r.commissioni:,.0f} dollari, scarto {r.costo_scarto:,.0f}.",
             f"* **Comprati meno venduti, il mese dopo, prima dei costi: {ls.mean():+.2%} al mese (t {t_di(ls):.2f})**, mesi positivi "
             f"{(ls > 0).mean():.0%}. Ogni mese cambia il {cambi[:, 0].mean():.0%} dei comprati e il {cambi[:, 1].mean():.0%} dei venduti.",
             f"* Con un comunicato sui risultati nello stesso mese dell'anno prima: {quote[:, 0].mean():.0%} dei comprati, "
             f"{quote[:, 1].mean():.0%} dei venduti; togliendoli, comprati meno venduti {senza_c.mean():+.2%} al mese (t "
             f"{t_di(senza_c):.2f}).", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(g['costi doppi']):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(g['senza costi']):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Senza il 2020 (da leggere) | Sharpe {sr(no2020):.2f} | — |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(g['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Limite noto: i comunicati vengono dal file della prova 30 (solo S&P 500, dal 2016). Nel conto: 2 prove (93)."]
    (QUI / "P038_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-20:]))


if __name__ == "__main__":
    main(finta="--finta" in sys.argv)
