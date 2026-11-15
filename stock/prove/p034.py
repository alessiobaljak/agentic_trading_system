"""Prova 34 — la deriva dopo i risultati nelle aziende piccole: comprate le piccole con la reazione più alta nei giorni del comunicato,
un mese, coperte con l'IWM (idea I36).

    python -m stock.prove.p034            # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca)
    python -m stock.prove.p034 --finta    # prova del programma in locale: titoli dell'archivio locale, reazioni a caso

Regole: `P034_deriva_piccole.md` (scritte e committate prima del calcolo). I comunicati: `dati/P034_comunicati.csv.gz`
(`stock/dati/comunicati_piccole.py`, dati pubblici della SEC); la composizione dell'indice: `dati/P028_membri.csv.gz`.
"""
from __future__ import annotations

import bisect
import sys
from dataclasses import replace
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import prepara_titolo, rendimenti
from stock.prove.p027 import DOLLARI_MINIMI, PREZZO_MINIMO, SEDUTE_DOLLARI, scarica
from stock.prove.p028 import decisioni as fine_mese
from stock.prove.p028 import ritorno
from stock.prove.p032 import campionamento, t_di
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import tono

FINO = date(2024, 12, 31)
PRIMA = date(2016, 1, 29)
QUOTA, MASSIMO, MINIMO = 0.2, 50, 25
VUOTE = 6770
COSTI = Costi(mezzo_scarto=15 * PB, slittamento=5 * PB, **IB_FISSO)
PRESTITO_IWM = 0.01
LIQUIDA_DOPO = 5
FONDO = "IWM"
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}

sr = lambda x: annuo(asticella.sharpe(x))  # noqa: E731
tot = lambda x: (1 + x).prod() - 1  # noqa: E731
dd = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min()  # noqa: E731


def comunicati() -> pd.DataFrame:
    c = pd.read_csv(QUI / "dati" / "P034_comunicati.csv.gz", dtype={"simbolo": str}, keep_default_na=False)   # «NA» è un simbolo
    c["deposito"] = pd.to_datetime(c["deposito"]).dt.date
    c["sic"] = pd.to_numeric(c["sic"], errors="coerce")
    return c[c["deposito"] <= FINO]


def membri_al(giorno: date, fini: list[date], membri: dict[date, set[str]]) -> set[str]:
    k = bisect.bisect_right(fini, giorno) - 1
    return membri[fini[k]] if k >= 0 else set()


def intorno(calendario: list[date], d: date) -> tuple[date, date] | None:
    """Il giorno di borsa prima di d e quello dopo d."""
    k = bisect.bisect_left(calendario, d)
    j = bisect.bisect_right(calendario, d)
    if k == 0 or j >= len(calendario):
        return None
    return calendario[k - 1], calendario[j]


def del_mese(eventi: list[tuple[str, date, float]], dopo: date, fino: date) -> dict[str, float]:
    """Le reazioni dei comunicati con la finestra finita dopo `dopo` e fino a `fino`; un titolo con due comunicati conta con l'ultimo."""
    out = {}
    for s, fine, r in sorted(eventi, key=lambda x: x[1]):
        if dopo < fine <= fino:
            out[s] = r
    return out


def scegli(reazioni: dict[str, float]) -> list[str]:
    if len(reazioni) < MINIMO:
        return []
    n = min(int(QUOTA * len(reazioni)), MASSIMO)
    return sorted(sorted(reazioni, key=lambda s: (-reazioni[s], s))[:n])


def calcola(finta: bool = False) -> dict:
    global FONDO
    fini, membri = fine_mese()
    giorni = [g for g in fini if PRIMA <= g <= FINO]
    ev = comunicati()
    ev = ev[ev["sic"] != VUOTE]
    if finta:
        FONDO = "QQQ"                  # in locale non c'è l'IWM: solo per provare il programma
        TIPI.update(raw="1Day_raw", az="azioni", asof=None)
        locali = {p.name for p in archivio.cartella_dati().iterdir() if p.is_dir()}
        membri = {g: set() for g in membri}
        ev = ev[ev["simbolo"].isin(locali - {FONDO, "SPY"})]
        nomi = {}
    else:
        scarica(["SPY"])
        scarica(sorted(set(ev["simbolo"])) + [FONDO], TIPI["raw"], TIPI["az"], TIPI["asof"])
        nomi = alpaca.nomi_dei_titoli()
    candidati = sorted(set(ev["simbolo"]) - {FONDO})
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
    barre, rett = {}, {}
    barre[FONDO], rett[FONDO], _ = prepara_titolo(FONDO, FINO, TIPI["raw"], TIPI["az"])
    calendario = sorted(rett[FONDO].index)
    ammessi = []
    for s, d in zip(ev["simbolo"], ev["deposito"]):
        x = intorno(calendario, d)
        if x and s in chiusure and s not in membri_al(x[0], fini, membri) and comprabile(s, x[0]):
            ammessi.append((s, x[0], x[1]))
    rotti = []
    for s in sorted({s for s, _, _ in ammessi}):
        try:
            barre[s], rett[s], _ = prepara_titolo(s, FINO, TIPI["raw"], TIPI["az"])
        except Exception as e:  # noqa: BLE001 — titolo con i dati rotti: si conta e resta fuori
            rotti.append(f"{s} ({type(e).__name__})")
    f = rett[FONDO]
    eventi = [(s, n, float(rett[s][n] / rett[s][p] - f[n] / f[p])) for s, p, n in ammessi
              if s in rett and p in rett[s].index and n in rett[s].index]
    if finta:
        rng = np.random.default_rng(34)
        eventi = [(s, n, float(r)) for (s, n, _), r in zip(eventi, rng.permutation([r for _, _, r in eventi]))]
    reazioni, elenchi = {}, {}
    for k, g in enumerate(giorni[:-1]):
        prima = giorni[k - 1] if k else date(2015, 12, 31)
        reazioni[g] = del_mese(eventi, prima, g)
        elenchi[g] = scegli(reazioni[g])
    elenchi[giorni[-1]] = []
    alto_basso, alto_fondo = [], []
    for k, g0 in enumerate(giorni[:-1]):
        g1 = giorni[k + 1]
        o = sorted((s for s in reazioni[g0] if g0 in rett[s].index), key=lambda s: (-reazioni[g0][s], s))
        q = int(QUOTA * len(o))
        if q >= 5 and g0 in f.index:
            a = np.mean([ritorno(rett[s], g0, g1) for s in o[:q]])
            b = np.mean([ritorno(rett[s], g0, g1) for s in o[-q:]])
            alto_basso.append(a - b)
            alto_fondo.append(a - ritorno(f, g0, g1))
    usati = set().union(*[set(v) for v in elenchi.values()]) | {FONDO}
    bb = {s: barre[s] for s in usati}
    base = {s: COSTI for s in bb}
    base[FONDO] = replace(COSTI, prestito_annuo=PRESTITO_IWM)
    varianti = (("costi", lambda c: c), ("costi doppi", lambda c: c.raddoppiati()), ("senza costi", lambda c: Costi()))
    out = {nome: simula_conto(bb, tono.strategia(elenchi, FONDO), {s: fz(base[s]) for s in bb}, capitale=CAPITALE,
                              liquida_dopo=LIQUIDA_DOPO) for nome, fz in varianti}
    primo = out["costi"].esecuzioni["giorno"].min()
    g = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
    return dict(g=g, out=out, elenchi=elenchi, reazioni=reazioni, alto_basso=np.array(alto_basso), alto_fondo=np.array(alto_fondo),
                comunicati=len(ev), ammessi=len(eventi), fondi=len(fondi), rotti=len(rotti))


def main(finta: bool = False):
    c = calcola(finta)
    g, r = c["g"], c["out"]["costi"]
    gc = g["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    cs = gc.index.intersection(spy.index)
    corr_spy = float(np.corrcoef(spy.loc[cs], gc.loc[cs])[0, 1])
    per_mese = [len(v) for v in c["reazioni"].values()]
    scelti = [len(c["elenchi"][k]) for k in c["reazioni"]]
    if finta:
        print(f"PROVA LOCALE con reazioni a caso (non è il risultato): Sharpe {sr(gc):.2f}, senza costi {sr(g['senza costi']):.2f}, "
              f"ordini {len(r.esecuzioni)}, rifiutati {r.rifiutati}, senza barra {r.senza_barra}, liquidati {len(r.liquidati)}; "
              f"comunicati {c['comunicati']}, ammessi {c['ammessi']}, per mese mediana {np.median(per_mese):.0f}, scelti mediana "
              f"{np.median(scelti):.0f}, mesi fuori {sum(1 for x in scelti if x == 0)} su {len(scelti)}; quinti "
              f"{c['alto_basso'].mean():+.2%} (t {t_di(c['alto_basso']):.2f}); corr SPY {corr_spy:.2f}")
        return
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P034_deriva_piccole", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P034_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P034_miscela"]
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
    ab, af = c["alto_basso"], c["alto_fondo"]
    testo = ["# Prova 34 — risultati", "",
             f"Calcolato da `python -m stock.prove.p034` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P034_deriva_piccole.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Comunicati (senza le società vuote) {c['comunicati']}, ammessi con i filtri e i prezzi {c['ammessi']}; fondi esclusi "
             f"{c['fondi']}, titoli con i dati rotti {c['rotti']}. Comunicati per mese: mediana {np.median(per_mese):.0f}, minimo "
             f"{min(per_mese)}; scelti: mediana {np.median(scelti):.0f}; mesi fuori {sum(1 for x in scelti if x == 0)} su {len(scelti)}.",
             f"* Mese dopo, senza costi, da chiusura a chiusura: il quinto con la reazione più alta meno il quinto più basso "
             f"**{ab.mean():+.2%} al mese (t {t_di(ab):.2f})**, mediana {np.median(ab):+.2%}; il quinto alto meno l'IWM "
             f"**{af.mean():+.2%} al mese (t {t_di(af):.2f})**; su {len(ab)} mesi. Correlazione con lo SPY {corr_spy:.2f}.",
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
             "", "Nel conto: 2 prove (85)."]
    (QUI / "P034_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-16:]))


if __name__ == "__main__":
    main("--finta" in sys.argv)
