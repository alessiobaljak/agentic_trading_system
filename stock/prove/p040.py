"""Prova 40 — i giorni con molti dividendi pagati: tenere lo SPY solo quando il pagamento del giorno e di quello prima è sopra la mediana
dei 252 giorni prima (idea I46; Hartzmark e Solomon, «Predictable Price Pressure»).

    python -m stock.prove.p040            # servono le chiavi di Alpaca (date di pagamento): gira su GitHub (azioni-ricerca)
    python -m stock.prove.p040 --finta    # prova del programma in locale, con date di pagamento inventate (non è il risultato)

Regole: `P040_dividendi_pagati.md` (scritte e committate prima del calcolo). Azioni in circolazione e codici SEC di allora:
`dati/P039_azioni.csv.gz`, `dati/P039_codici.csv.gz`; composizione dell'indice: `dati/P028_membri.csv.gz`.
"""
from __future__ import annotations

import bisect
import math
import sys
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.dati.azioni_circolazione import codice_al
from stock.prove.p001 import CAPITALE, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p028 import decisioni as fine_mese
from stock.prove.p032 import campionamento, t_di
from stock.prove.p034 import membri_al
from stock.prove.p035 import dd, sr, tot
from stock.prove.p039 import carica_dati
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

DAL, FINO = date(2017, 1, 3), date(2024, 12, 31)
FINESTRA = 252
MEZZO, SLITTAMENTO = 0.185e-4, 0.5e-4
IB_PER_AZIONE, IB_MINIMO, IB_MASSIMO = 0.005, 1.0, 0.01
TIPO_AZ = "azioni_allora"


def cartella():
    p = archivio.cartella_dati() / "p040"
    p.mkdir(parents=True, exist_ok=True)
    return p


# --- le parti senza rete -----------------------------------------------------------------------------------------------------------
def giorno_di_borsa(d: date, calendario: list[date]) -> date | None:
    """Il giorno stesso se è di borsa, altrimenti il giorno di borsa dopo."""
    k = bisect.bisect_left(calendario, d)
    return calendario[k] if k < len(calendario) else None


def azioni_allo_stacco(dichiarazioni: list[tuple[date, date, float]], stacco: date, frazionamenti: dict[date, float]) -> float | None:
    """L'ultimo numero di copertina depositato prima della data di stacco, moltiplicato per i frazionamenti fra la sua data e lo stacco."""
    noti = [x for x in dichiarazioni if x[0] < stacco and x[2] > 0]
    if not noti:
        return None
    _, fine, n = max(noti, key=lambda x: (x[0], x[1]))
    return n * math.prod(r for d, r in frazionamenti.items() if fine < d <= stacco)


def pagamenti(div: pd.DataFrame, calendario: list[date]) -> pd.Series:
    """`div`: colonne pagamento, dollari. Il totale per giorno di borsa (un pagamento in un giorno senza borsa va al giorno dopo)."""
    div = div[div["pagamento"] >= calendario[0]]                  # prima del calendario non si sa dove cadrebbero
    g = [giorno_di_borsa(d, calendario) for d in div["pagamento"]]
    s = pd.Series(div["dollari"].to_numpy(), index=g, dtype=float).groupby(level=0).sum()
    return s.reindex(calendario, fill_value=0.0)


def misura(p: pd.Series) -> pd.Series:
    """D(t) = pagamento di t + pagamento del giorno di borsa prima."""
    return p + p.shift(1).fillna(0.0)


def soglie(d: pd.Series, quota: float = 0.5, finestra: int = FINESTRA) -> pd.Series:
    """Per ogni giorno, il quantile `quota` dei D dei `finestra` giorni di borsa prima (NaN se non ce ne sono abbastanza)."""
    return d.shift(1).rolling(finestra, min_periods=finestra).quantile(quota)


def dentro(d: pd.Series, quota: float = 0.5) -> pd.Series:
    """1 nei giorni con D sopra la soglia dell'anno prima, 0 negli altri (e prima che la soglia esista)."""
    s = soglie(d, quota)
    return ((d > s) & s.notna()).astype(float)


def commissione(azioni: float, prezzo: float) -> float:
    if azioni <= 0:
        return 0.0
    return min(max(IB_MINIMO, IB_PER_AZIONE * azioni), IB_MASSIMO * azioni * prezzo)


def conto(w: pd.Series, r: pd.Series, prezzo: pd.Series, fattore: float = 1.0, costi: bool = True) -> pd.Series:
    """Rendimento di ogni giorno: w(t)·r(t), meno i costi di ogni entrata e uscita alla chiusura del giorno prima."""
    v, prima, out = CAPITALE, 0.0, {}
    for g in r.index:
        h = float(w.loc[g])
        x = h * float(r.loc[g])
        if costi and h != prima:
            p = float(prezzo.loc[g])
            x -= fattore * (MEZZO + SLITTAMENTO + commissione(v / p, p) / v)
        out[g] = x
        v *= 1 + x
        prima = h
    return pd.Series(out)


def cambio_del_mese(calendario: list[date]) -> set[date]:
    """L'ultimo giorno di borsa di ogni mese e i primi tre del mese dopo."""
    out = set()
    for k, g in enumerate(calendario):
        if k + 1 < len(calendario) and calendario[k + 1].month != g.month:
            out.update(calendario[k:k + 4])
    return out


# --- il calcolo --------------------------------------------------------------------------------------------------------------------
def dividendi(simboli: list[str], finta: bool) -> pd.DataFrame:
    f = cartella() / ("finti.csv.gz" if finta else "dividendi.csv.gz")
    if f.exists():
        return pd.read_csv(f, dtype={"simbolo": str}, keep_default_na=False, parse_dates=["stacco", "pagamento"]).assign(
            stacco=lambda x: x["stacco"].dt.date, pagamento=lambda x: x["pagamento"].dt.date)
    if finta:
        righe = []
        for s in simboli:
            az = archivio.carica(s, "azioni")
            if az is None:
                continue
            for d, imp in zip(az.loc[az["tipo"] == "dividendo", "data"], az.loc[az["tipo"] == "dividendo", "importo"]):
                d = pd.Timestamp(d).date()
                righe.append({"simbolo": s, "stacco": d, "pagamento": d + timedelta(days=int(7 + (hash(s) % 21))), "importo": imp})
        df = pd.DataFrame(righe)
    else:
        df = alpaca.dividendi_pagati(simboli, date(2015, 6, 1), FINO)
    df.to_csv(f, index=False)
    return df


def calcola(finta: bool = False) -> dict:
    fini, membri = fine_mese()
    simboli = sorted(set().union(*membri.values()))
    spy_raw = archivio.carica("SPY", "1Day_raw")
    calendario = sorted(g for g in controlli.date_ny(spy_raw.index) if g <= FINO)
    prezzo = pd.Series(spy_raw["close"].to_numpy(), index=pd.Index(controlli.date_ny(spy_raw.index)))
    div = dividendi(simboli, finta)
    div = div[(div["pagamento"] <= FINO) & (div["importo"] > 0)].copy()
    codici, azioni = carica_dati()
    tipo = "azioni" if finta else TIPO_AZ
    fraz = {}
    for s in sorted(set(div["simbolo"])):
        az = archivio.carica(s, tipo)
        if az is not None and len(az):
            x = az[az["tipo"] == "frazionamento"]
            fraz[s] = {pd.Timestamp(d).date(): float(r) for d, r in zip(x["data"], x["rapporto"])}
    dollari, fuori = [], {"non membro": 0, "senza codice": 0, "senza azioni": 0}
    for s, st, pg, imp in zip(div["simbolo"], div["stacco"], div["pagamento"], div["importo"]):
        if s not in membri_al(pg, fini, membri) and pg >= fini[0]:
            fuori["non membro"] += 1
            dollari.append(np.nan)
            continue
        cik = codice_al(codici.get(s, []), st)
        if cik is None:
            fuori["senza codice"] += 1
            dollari.append(np.nan)
            continue
        n = azioni_allo_stacco(azioni.get(cik, []), st, fraz.get(s, {}))
        if n is None:
            fuori["senza azioni"] += 1
            dollari.append(np.nan)
            continue
        dollari.append(imp * n)
    div["dollari"] = dollari
    usati = div.dropna(subset=["dollari"])
    p = pagamenti(usati, calendario)
    d = misura(p)
    w = dentro(d, 0.5)
    r = comprare_e_tenere("SPY", calendario[calendario.index(DAL) - 1], FINO)
    r = r[(r.index >= DAL) & (r.index <= FINO)]
    w = w.reindex(r.index).fillna(0.0)
    return dict(d=d, w=w, r=r, prezzo=prezzo, calendario=calendario, fuori=fuori, totale=len(div), usati=len(usati),
                quarto=dentro(d, 0.75).reindex(r.index).fillna(0.0),
                dieci=dentro(d, 1 - 10 / FINESTRA).reindex(r.index).fillna(0.0))


def main(finta: bool = False):
    c = calcola(finta)
    w, r, prezzo = c["w"], c["r"], c["prezzo"]
    gc = conto(w, r, prezzo)
    g = {"costi doppi": conto(w, r, prezzo, 2.0), "senza costi": conto(w, r, prezzo, costi=False)}
    a, b = gc.index.min(), gc.index.max()
    spy = r
    sopra, sotto = r[w == 1], r[w == 0]
    diff = sopra.mean() - sotto.mean()
    t_diff = diff / math.sqrt(sopra.var(ddof=1) / len(sopra) + sotto.var(ddof=1) / len(sotto))
    if finta:
        print(f"PROVA LOCALE con date di pagamento inventate (non è il risultato): Sharpe {sr(gc):.2f}, SPY {sr(spy):.2f}, giorni dentro "
              f"{w.mean():.0%}, sopra {sopra.mean() * 1e4:.1f} contro sotto {sotto.mean() * 1e4:.1f} punti base; dividendi "
              f"{c['totale']}, usati {c['usati']}, fuori {c['fuori']}")
        return
    righe_quote = []
    for nome, x in (("sopra la mediana (la regola)", w), ("nel quarto più alto", c["quarto"]), ("fra i 10 più alti", c["dieci"])):
        s1, s0 = r[x == 1], r[x == 0]
        dx = s1.mean() - s0.mean()
        tx = dx / math.sqrt(s1.var(ddof=1) / len(s1) + s0.var(ddof=1) / len(s0)) if len(s1) > 2 else float("nan")
        righe_quote.append(f"| {nome} | {len(s1)} ({len(s1) / len(r):.0%}) | {s1.mean() * 1e4:+.1f} | {s0.mean() * 1e4:+.1f} | "
                           f"{dx * 1e4:+.1f} (t {tx:.2f}) |")
    cm = cambio_del_mese(c["calendario"])
    quota_cm = float(np.mean([x in cm for x in w.index[w == 1]]))
    quota_cm_tutti = float(np.mean([x in cm for x in w.index]))
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P040_dividendi", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P040_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P040_miscela"]
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
    testo = ["# Prova 40 — risultati", "",
             f"Calcolato da `python -m stock.prove.p040` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P040_dividendi_pagati.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Dividendi in contanti dei membri {c['totale']}, usati {c['usati']} ({c['usati'] / max(c['totale'], 1):.0%}); fuori: "
             f"{c['fuori']}. Dentro lo SPY il {w.mean():.0%} dei giorni; cambi di posizione {int((w.diff().abs() > 0).sum())}.",
             f"* Giorni scelti nel cambio del mese (ultimo giorno e primi tre): {quota_cm:.0%}, contro il {quota_cm_tutti:.0%} di tutti i giorni.",
             "", "| Giorni | Quanti | SPY nel giorno, punti base | Negli altri giorni | Differenza |", "|---|---|---|---|---|",
             *righe_quote, "",
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
             f"Differenza fra i giorni sopra e sotto la mediana: {diff * 1e4:+.1f} punti base (t {t_diff:.2f}). Nel conto: 2 prove (97)."]
    (QUI / "P040_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-24:]))


if __name__ == "__main__":
    main(finta="--finta" in sys.argv)
