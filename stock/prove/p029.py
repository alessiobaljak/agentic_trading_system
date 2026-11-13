"""Calcolo della prova 29 (`P029_notizie_cattive_piccole.md`): regole lì, scritte prima. Decide il periodo chiuso, una volta sola.

    python -m stock.prove.p029            # su GitHub (azioni-ricerca): scarica le notizie e i prezzi del periodo chiuso, calcola
    python -m stock.prove.p029 --finta    # prova del programma in locale: notizie inventate sul 2016-2024, niente file, niente rete

Notizie e prezzi restano nella memoria del lavoro; nel repository vanno solo i risultati.
"""
from __future__ import annotations

import math
import re
import sys
from dataclasses import replace
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli, notizie
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, annuo, carica_serie, salva_serie
from stock.prove.p003 import prepara_titolo, rendimenti
from stock.prove.p027 import DOLLARI_MINIMI, PREZZO_MINIMO, SEDUTE_DOLLARI, scarica
from stock.prove.p028 import ritorno
from stock.simulatore.costi import Costi
from stock.simulatore.portafoglio import simula_conto
from stock.strategie import tono

NY = ZoneInfo("America/New_York")
SIMBOLO = re.compile(r"[A-Z]{1,5}(\.[A-Z])?")
PRESTITO = 0.03
COSTI = Costi(mezzo_scarto=15 * PB, slittamento=5 * PB, prestito_annuo=PRESTITO, **IB_FISSO)
LIQUIDA_DOPO = 5
# Il simulatore esegue le vendite prima degli acquisti: nel cambio del mese le vendite allo scoperto nuove passerebbero prima delle
# ricoperture delle vecchie e, con il limite di leva 1, verrebbero rifiutate. Un conto con margine (Interactive Brokers, Alpaca)
# permette fino a 2 volte il valore; l'esposizione voluta resta 50% venduto + 50% comprato (`verso_pesi`).
LEVA_PER_IL_CAMBIO = 2.0
FONDO = "IWM"
PERIODI = {
    # il periodo chiuso: quello che decide
    "chiuso": dict(membri="P029_membri.csv.gz", primo_confine=datetime(2024, 11, 29, 16, tzinfo=NY),
                   notizie=notizie.mesi_fra((2024, 11), (2026, 8)), fino=date(2026, 9, 30),
                   tipi=("1Day_allora_chiuso", "azioni_allora_chiuso", "-"),
                   dal=datetime(2024, 10, 1, tzinfo=UTC), al=datetime(2026, 10, 1, 5, tzinfo=UTC)),
    # il 2016-2024, già visto: si stampa accanto e non conta
    "visto": dict(membri="P028_membri.csv.gz", primo_confine=datetime(2015, 12, 31, 16, tzinfo=NY),
                  notizie=notizie.mesi(2016, 2024), fino=date(2024, 12, 31),
                  tipi=("1Day_allora", "azioni_allora", "-"),
                  dal=datetime(2015, 11, 1, tzinfo=UTC), al=datetime(2025, 1, 1, 5, tzinfo=UTC)),
}

sr = lambda x: annuo(float(x.mean() / x.std(ddof=1))) if len(x) > 2 and x.std(ddof=1) > 0 else float("nan")  # noqa: E731
tot = lambda x: float((1 + x).prod() - 1)  # noqa: E731
dd = lambda x: float(((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min())  # noqa: E731
t_di = lambda x: float(x.mean() / x.std(ddof=1) * math.sqrt(len(x))) if len(x) > 2 else float("nan")  # noqa: E731


def decisioni(nome_file: str) -> tuple[list[date], dict[date, set[str]]]:
    m = pd.read_csv(QUI / "dati" / nome_file, parse_dates=["giorno"])
    giorni = [d.date() for d in m["giorno"]]
    return giorni, {g: set(s.split()) for g, s in zip(giorni, m["simboli"])}


def calcola(periodo: str, finta: bool = False) -> dict:
    p = PERIODI[periodo]
    fondo = "QQQ" if finta else FONDO              # nella prova locale l'IWM non c'è in archivio
    raw_t, az_t, asof = p["tipi"]
    if finta:
        p = dict(PERIODI["visto"])
        raw_t, az_t, asof = "1Day_raw", "azioni", None
    giorni, membri = decisioni(p["membri"])
    if finta:
        from stock.prove.p028 import notizie_finte
        n = notizie_finte(membri)
        membri = {g: set() for g in membri}       # nella prova locale i titoli dell'indice fanno da «aziende piccole»
    else:
        restano = notizie.scarica(0, 0, minuti=200, elenco=p["notizie"])
        if restano:
            raise SystemExit(f"{periodo}: mancano {len(restano)} mesi di notizie (minuti degli ordini o tempo finito): rilanciare")
        n = notizie.carica(0, 0, elenco=p["notizie"])
    confini = [p["primo_confine"]] + [datetime(g.year, g.month, g.day, 16, tzinfo=NY) for g in giorni[:-1]]
    toni = tono.toni(n, confini)
    del n
    candidati = sorted({s for k, g in enumerate(giorni[:-1]) for s in toni[k] if s not in membri[g] and SIMBOLO.fullmatch(s)})
    print(f"{periodo}: candidati {len(candidati)}", flush=True)
    if not finta:
        scarica(candidati + [fondo, "SPY"], raw_t, az_t, asof, p["dal"], p["al"])
        nomi = alpaca.nomi_dei_titoli()
    else:
        nomi = {}
    fondi = {s for s in candidati if tono.e_un_fondo(nomi.get(s, ""))}
    chiusure, dollari = {}, {}
    for s in candidati:
        df = archivio.carica(s, raw_t)
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
    ammessi = {g: {s for s in toni[k] if s not in membri[g] and comprabile(s, g)} for k, g in enumerate(giorni[:-1])}
    barre, rett, rotti = {}, {}, []
    for s in sorted(set().union(*ammessi.values())) + [fondo, "SPY"]:
        try:
            barre[s], rett[s], _ = prepara_titolo(s, p["fino"], raw_t, az_t)
        except Exception as e:  # noqa: BLE001 — titolo con i dati rotti: si conta e resta fuori
            rotti.append(f"{s} ({type(e).__name__})")
    ammessi = {g: {s for s in a if s in barre} for g, a in ammessi.items()}
    elenchi = {g: tono.scegli(toni[k], ammessi[g], piu_bassi=True) for k, g in enumerate(giorni[:-1])}
    spy_b = barre.pop("SPY")
    usati = set().union(*[set(v) for v in elenchi.values()]) | {fondo}
    b = {s: barre[s] for s in usati}
    base = {s: COSTI for s in b}
    base[fondo] = replace(COSTI, prestito_annuo=0.0)              # l'IWM si compra: nessun prestito
    varianti = (("costi", lambda c: c), ("costi doppi", lambda c: c.raddoppiati()), ("senza costi", lambda c: Costi()),
                ("senza prestito", lambda c: replace(c, prestito_annuo=0.0)))
    out = {nome: simula_conto(b, tono.strategia(elenchi, fondo, lato=-1), {s: f(c) for s, c in base.items()}, capitale=CAPITALE,
                              liquida_dopo=LIQUIDA_DOPO, leva_massima=LEVA_PER_IL_CAMBIO) for nome, f in varianti}
    primo = out["costi"].esecuzioni["giorno"].min()
    g = {k: rendimenti(v.valore[v.valore.index >= primo]) for k, v in out.items()}
    spy_r = pd.Series(spy_b["close"].to_numpy(), index=pd.Index(controlli.date_ny(spy_b.index)))
    spy = rett["SPY"].pct_change().dropna()
    spy = spy[(spy.index >= g["costi"].index.min()) & (spy.index <= g["costi"].index.max())]
    # il quinto più basso meno l'IWM, mese per mese, senza costi
    quinti = []
    for k in range(len(giorni) - 1):
        g0, g1 = giorni[k], giorni[k + 1]
        ordine = [s for s in tono.classifica(toni[k], ammessi[g0], piu_bassi=True) if s in rett and g0 in rett[s].index]
        q = int(tono.QUINTO * len(ordine))
        if q >= 5 and g0 in rett[fondo].index:
            quinti.append(np.mean([ritorno(rett[s], g0, g1) for s in ordine[:q]]) - ritorno(rett[fondo], g0, g1))
    scelti = [len(v) for v in elenchi.values()]
    return dict(g=g, out=out, spy=spy, quinti=np.array(quinti), scelti=scelti, candidati=len(candidati), fondi=len(fondi),
                senza=len(candidati) - len(fondi) - len(chiusure), rotti=len(rotti), spy_controllo=len(spy_r))


def main(finta: bool = False):
    if finta:
        r = calcola("visto", finta=True)
        gc = r["g"]["costi"]
        print(f"PROVA LOCALE con notizie inventate (non è il risultato): Sharpe {sr(gc):.2f}, senza costi {sr(r['g']['senza costi']):.2f}, "
              f"senza prestito {sr(r['g']['senza prestito']):.2f}, quinti {r['quinti'].mean():+.2%} (t {t_di(r['quinti']):.2f}), scelti "
              f"mediana {np.median(r['scelti'])}, chiusi dal listino {len(r['out']['costi'].liquidati)}")
        return
    visto = calcola("visto")
    chiuso = calcola("chiuso")
    gc = chiuso["g"]["costi"]
    g2 = chiuso["g"]["costi doppi"]
    spy = chiuso["spy"]
    q = pd.Series(gc).groupby(pd.Index([(d.year, (d.month - 1) // 3) for d in gc.index])).apply(lambda x: (1 + x).prod() - 1)
    trimestri = int((q > 0).sum())
    corr_spy = float(np.corrcoef(gc.loc[gc.index.intersection(spy.index)], spy.loc[gc.index.intersection(spy.index)])[0, 1])
    miscela = carica_serie()["P025_miscela"]
    gv = visto["g"]["costi"]
    comuni = miscela.index.intersection(gv.index)
    corr_misc = float(np.corrcoef(miscela.loc[comuni], gv.loc[comuni])[0, 1])
    da_sola = sr(gc) > sr(spy) and sr(g2) > 0 and trimestri >= 4
    entra = sr(gc) > 0 and sr(g2) > 0 and corr_spy < 0.3 and corr_misc < 0.3
    # il prestito che azzera il guadagno (approssimato: il prestito si paga sul 50% del conto venduto allo scoperto)
    g0 = chiuso["g"]["senza prestito"]
    pareggio = float(g0.mean() * 252 / 0.5)
    salva_serie("P029_notizie_cattive_chiuso", gc)
    salva_serie("P029_notizie_cattive_visto", gv)
    o = chiuso["out"]["costi"]
    anni = (1 + gc).groupby(pd.Index([d.year for d in gc.index])).prod() - 1
    righe = ["# Prova 29 — risultati (periodo chiuso, aperto una volta)", "",
             f"Calcolato da `python -m stock.prove.p029` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P029_notizie_cattive_piccole.md` (committate prima). Periodo chiuso dal {gc.index.min()} al {gc.index.max()}.", "",
             f"* Candidati fuori dall'indice con il tono {chiuso['candidati']}, fondi esclusi {chiuso['fondi']}, senza prezzi "
             f"{chiuso['senza']}, con i dati rotti {chiuso['rotti']}; titoli scelti per mese: mediana {int(np.median(chiuso['scelti']))}, "
             f"mesi fuori {sum(1 for x in chiuso['scelti'] if x == 0)} su {len(chiuso['scelti'])}.",
             f"* Ordini eseguiti {len(o.esecuzioni)}; senza barra {o.senza_barra}; rifiutati {o.rifiutati}; **chiusi all'ultimo prezzo "
             f"perché spariti dal listino: {len(o.liquidati)}**. Costi pagati: commissioni {o.commissioni:,.0f}, scarto e slittamento "
             f"{o.costo_scarto:,.0f} dollari (il prestito è nel valore del conto).",
             f"* Il quinto con le notizie peggiori meno l'IWM, mese dopo, senza costi: **{chiuso['quinti'].mean():+.2%} al mese (t "
             f"{t_di(chiuso['quinti']):.2f})**, mediana {np.median(chiuso['quinti']):+.2%}, su {len(chiuso['quinti'])} mesi (negativo = "
             f"le notizie cattive scendono, è quello che la vendita allo scoperto guadagna).", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(chiuso['g']['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(g2):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi (più alto dello SPY) | **{sr(gc):.2f}** (senza costi {sr(chiuso['g']['senza costi']):.2f}) | "
             f"{sr(spy):.2f} |",
             f"| **2.** Sharpe con i costi doppi (> 0) | {sr(g2):.2f} | — |",
             f"| **3.** Trimestri in guadagno (almeno 4 su 7) | {trimestri} su {len(q)} | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| Prestito annuo che azzera il guadagno (approssimato) | {pareggio:.1%} (usato: {PRESTITO:.0%}) | — |",
             f"| **Esito da sola** | **{'passa' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela:** Sharpe con i costi {sr(gc):.2f} e con i costi doppi {sr(g2):.2f} (sopra zero); correlazione "
             f"con lo SPY sul periodo chiuso {corr_spy:.2f} e con la miscela sul 2016-2024 {corr_misc:.2f} (soglia 0,3). **Esito: "
             f"{'entra (prima il revisore, poi la proposta del demo)' if entra else 'non entra'}**", "",
             f"**Già visto, non conta** (2016-2024, gli stessi dati da cui è nata l'idea): Sharpe con i costi {sr(gv):.2f}, senza costi "
             f"{sr(visto['g']['senza costi']):.2f}, senza prestito {sr(visto['g']['senza prestito']):.2f}; quinto basso meno IWM "
             f"{visto['quinti'].mean():+.2%} al mese (t {t_di(visto['quinti']):.2f}); perdita massima {dd(gv):.1%}.", "",
             "Nel conto: 1 prova più 1 apertura del periodo chiuso = 2. Il periodo chiuso ora è usato per la famiglia «notizie»."]
    (QUI / "P029_risultati.md").write_text("\n".join(righe) + "\n")
    print("\n".join(righe))


if __name__ == "__main__":
    main("--finta" in sys.argv)
