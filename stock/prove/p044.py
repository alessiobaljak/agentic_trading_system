"""Prova 44 — la volatilità rovesciata: VIXY comprato quando il VIX chiude sopra il VIX a tre mesi, venduto quando torna sotto
(idea I50; Johnson 2017).

    python -m stock.prove.p044        # gira su GitHub (azioni-ricerca): VIXY da Alpaca, VIX e VIX3M da CBOE (mai nel repository)

Regole: `P044_volatilita_rovesciata.md` (scritte e committate prima del calcolo).
"""
from __future__ import annotations

import io
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd
import requests

from stock.dati import archivio, controlli
from stock.prove.p001 import CAPITALE, IB_FISSO, PB, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p003 import rendimenti
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.costi import Costi
from stock.simulatore.finestre import finestre
from stock.simulatore.portafoglio import simula_conto, verso_pesi

DAL, FINO = date(2016, 1, 4), date(2024, 12, 31)
FONDO = "VIXY"
COSTI = Costi(mezzo_scarto=5 * PB, slittamento=1 * PB, **IB_FISSO)
CBOE = "https://cdn.cboe.com/api/global/us_indices/daily_prices/{nome}_History.csv"


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def segnale(vix: pd.Series, vix3m: pd.Series) -> pd.Series:
    """Giorno → True se la chiusura del VIX è maggiore o uguale a quella del VIX a tre mesi (solo i giorni con tutti e due)."""
    a, b = vix.align(vix3m, join="inner")
    return (a >= b).astype(bool)


def episodi(rovesciata: pd.Series, calendario: list[date]) -> list[tuple[date, date | None]]:
    """(giorno dell'acquisto, giorno della vendita): si compra all'apertura del giorno di borsa dopo la prima chiusura rovesciata, si
    vende all'apertura del giorno dopo la prima chiusura normale (None se si resta dentro fino alla fine)."""
    dopo = {g: calendario[k + 1] for k, g in enumerate(calendario[:-1])}
    out, dentro = [], None
    for g in calendario:
        if g not in rovesciata.index:
            continue
        r = bool(rovesciata.loc[g])
        if r and dentro is None and g in dopo:
            dentro = dopo[g]
        elif not r and dentro is not None and g in dopo:
            out.append((dentro, dopo[g]))
            dentro = None
    if dentro is not None:
        out.append((dentro, None))
    return out


def strategia(rovesciata: pd.Series):
    """Tutto in VIXY quando la chiusura è rovesciata, niente quando è normale; ordini solo quando lo stato cambia."""
    def decidi(giorno, storia, stato):
        if giorno not in rovesciata.index:
            return []
        dentro = stato.azioni.get(FONDO, 0) > 0
        voglio = bool(rovesciata.loc[giorno])
        if voglio == dentro:
            return []
        h = storia(FONDO)
        if h is None or h.empty:
            return []
        return verso_pesi(stato, {FONDO: 1.0} if voglio else {}, {FONDO: float(h["close"].iloc[-1])}, etichetta="vix")
    return decidi


# --- con la rete ------------------------------------------------------------------------------------------------------------------
def indice_cboe(nome: str) -> pd.Series:
    r = requests.get(CBOE.format(nome=nome), timeout=60)
    r.raise_for_status()
    d = pd.read_csv(io.StringIO(r.text))
    return pd.Series(d["CLOSE"].astype(float).to_numpy(), index=pd.Index(pd.to_datetime(d["DATE"], format="%m/%d/%Y").dt.date))


def main():
    from stock.prove.p003 import prepara_titolo
    from stock.prove.p027 import scarica
    scarica(["SPY", FONDO])
    spy = archivio.carica("SPY", "1Day_raw")
    cal = sorted(d for d in controlli.date_ny(spy.index) if date(2015, 12, 1) <= d <= FINO)
    df, _, _ = prepara_titolo(FONDO, FINO)
    rov = segnale(indice_cboe("VIX"), indice_cboe("VIX3M"))
    rov = rov[(rov.index >= date(2015, 12, 1)) & (rov.index <= FINO)]
    giorni = [g for g in cal if g >= DAL]
    ep = episodi(rov[rov.index >= max(g for g in cal if g < DAL)], [max(g for g in cal if g < DAL)] + giorni)
    varianti = (("costi", COSTI), ("costi doppi", COSTI.raddoppiati()), ("senza costi", Costi()))
    out = {nome: simula_conto({FONDO: df}, strategia(rov), c, capitale=CAPITALE) for nome, c in varianti}
    gg = {k: rendimenti(v.valore[v.valore.index >= DAL]) for k, v in out.items()}
    gc, r = gg["costi"], out["costi"]
    v = r.valore
    a, b = gc.index.min(), gc.index.max()
    prima = {g: v[v.index < g].iloc[-1] if len(v[v.index < g]) else CAPITALE for g, _ in ep}
    guadagni = [(e, x, float((v.loc[x] if x is not None else v.iloc[-1]) / prima[e] - 1)) for e, x in ep]
    guadagni_ord = sorted(guadagni, key=lambda t: t[2])
    giorni_dentro = int(rov[(rov.index >= a) & (rov.index <= b)].sum())
    spy_r = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P044_volatilita", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P044_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P044_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(gg["costi doppi"])
    da_sola = sr_c > sr(spy_r) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    sp = spy_r.reindex(gc.index).dropna()
    corr_spy = float(np.corrcoef(gc.loc[sp.index], sp)[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte = t_di(gc.to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(gg["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1
    senza_2020 = float((1 + gc[[x.year != 2020 for x in gc.index]]).prod() - 1)
    fmt = lambda t: f"{t[0]} → {t[1] or 'fine'} {t[2]:+.1%}"  # noqa: E731
    testo = ["# Prova 44 — risultati", "",
             f"Calcolato da `python -m stock.prove.p044` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P044_volatilita_rovesciata.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Chiusure rovesciate {giorni_dentro} su {len(gc)} giorni; episodi {len(ep)}; ordini {len(r.esecuzioni)}; commissioni "
             f"{r.commissioni:,.0f} dollari, scarto {r.costo_scarto:,.0f}. Segnale del 31 dicembre 2015: "
             f"{'rovesciata' if bool(rov.get(max(g for g in cal if g < DAL), False)) else 'normale'}.",
             f"* Episodi in guadagno {sum(x[2] > 0 for x in guadagni)} su {len(guadagni)}; i 5 migliori: "
             + "; ".join(fmt(t) for t in guadagni_ord[::-1][:5]) + "; i 5 peggiori: " + "; ".join(fmt(t) for t in guadagni_ord[:5]) + ".",
             f"* Senza il 2020: {senza_2020:+.1%}. Correlazione giornaliera con lo SPY {corr_spy:.2f}.", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(gg['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(gg['costi doppi']):+.1%} | {tot(spy_r):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(gg['senza costi']):.2f}) | {sr(spy_r):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy_r):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(gg['costi doppi'].reindex(comuni).dropna()):.2f}; **correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3)**; miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove."]
    (QUI / "P044_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
