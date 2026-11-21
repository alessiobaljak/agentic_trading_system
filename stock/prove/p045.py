"""Prova 45 — l'ultima mezz'ora segue la giornata solo nei giorni con la copertura delle opzioni sotto zero (SPY), uscita all'asta di
chiusura (idea I52; Baltussen, Da, Lammers e Martens 2021).

    python -m stock.prove.p045        # gira su GitHub (azioni-ricerca): calendario e prezzi di Alpaca, copertura da SqueezeMetrics

Regole: `P045_ultima_mezzora_gamma.md` (scritte e committate prima del calcolo). Il segnale è quello della prova 1
(`stock/strategie/ultima_mezzora.prepara`).
"""
from __future__ import annotations

import io
import math
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd
import requests

from stock.dati import alpaca, archivio, controlli
from stock.prove.p001 import CAPITALE, MEZZO_SCARTO, PB, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import commissione, dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre
from stock.strategie import ultima_mezzora as um

DAL, FINO = date(2016, 1, 4), date(2024, 12, 31)
QUOTA, SLIT = 0.98, 0.5 * PB
MEZZO = MEZZO_SCARTO["SPY"]
DIX = "https://squeezemetrics.com/monitor/static/DIX.csv"


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def copertura_del_giorno_prima(gex: pd.Series, giorni: list[date]) -> dict[date, float]:
    """Per ogni giorno di borsa, la copertura con la data del giorno di borsa prima (nessun valore se manca)."""
    out = {}
    for a, b in zip(giorni[:-1], giorni[1:]):
        if a in gex.index and np.isfinite(gex.loc[a]):
            out[b] = float(gex.loc[a])
    return out


def operazioni(seduta: pd.DataFrame, seg: dict, chiusure_ufficiali: dict[date, float]) -> dict[date, tuple[int, float, float, float]]:
    """Giorno → (direzione, prezzo del segnale, apertura della barra dopo, chiusura ufficiale), per i giorni con un segnale non nullo."""
    t = seduta.index.tz_convert("America/New_York")
    chiusure, aperture = seduta["close"].to_numpy(float), seduta["open"].to_numpy(float)
    out = {}
    for i in np.where(~np.isnan(seg["direzione"]))[0]:
        d = int(seg["direzione"][i])
        g = t[i].date()
        if d == 0 or i + 1 >= len(seduta) or t[i + 1].date() != g or g not in chiusure_ufficiali:
            continue
        out[g] = (d, float(chiusure[i]), float(aperture[i + 1]), float(chiusure_ufficiali[g]))
    return out


def conto(ops: dict[date, tuple[int, float, float, float]], giorni: list[date], fattore: float = 1.0,
          costi: bool = True) -> tuple[pd.Series, int]:
    """I rendimenti di ogni giorno: il 98% del conto al prezzo del segnale, azioni intere; ingresso con metà dello scarto e lo
    slittamento, uscita all'asta con il solo slittamento; commissioni. Il secondo valore: i giorni saltati perché servirebbe leva."""
    v, out, saltati = CAPITALE, {}, 0
    for g in giorni:
        x = ops.get(g)
        if x is None:
            out[g] = 0.0
            continue
        d, p_seg, p_in, p_out = x
        n = math.floor(QUOTA * v / p_seg)
        if n <= 0 or n * p_in > v:
            saltati += 1
            out[g] = 0.0
            continue
        if costi:
            ingresso = p_in * (1 + d * fattore * (MEZZO + SLIT))
            uscita = p_out * (1 - d * fattore * SLIT)
            spese = fattore * (commissione(n, p_in) + commissione(n, p_out))
        else:
            ingresso, uscita, spese = p_in, p_out, 0.0
        utile = d * n * (uscita - ingresso) - spese
        out[g] = utile / v
        v += utile
    return pd.Series(out), saltati


def lordo(ops: dict, giorni: set) -> np.ndarray:
    """Il guadagno lordo per operazione (direzione × uscita / ingresso − 1) nei giorni dati."""
    return np.array([d * (p_out / p_in - 1) for g, (d, _, p_in, p_out) in ops.items() if g in giorni])


# --- con la rete ------------------------------------------------------------------------------------------------------------------
def copertura() -> pd.Series:
    r = requests.get(DIX, headers={"User-Agent": "Mozilla/5.0 (ricerca)"}, timeout=60)
    r.raise_for_status()
    d = pd.read_csv(io.StringIO(r.text))
    return pd.Series(d["gex"].astype(float).to_numpy(), index=pd.Index(pd.to_datetime(d["date"]).dt.date))


def main():
    cal = alpaca.calendario("2016-01-01", "2024-12-31")
    minuti = archivio.carica("SPY", "1Min_raw")
    if minuti is None or minuti.empty:
        from stock.dati.scarica import scarica_titolo
        scarica_titolo("SPY", "2016-01-01", "2024-12-31", minuti=True)
        minuti = archivio.carica("SPY", "1Min_raw")
    seduta = um.solo_seduta(minuti, cal)
    problemi, _ = controlli.controlla_minuti(minuti, cal)
    esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
    seg = um.prepara(seduta, cal, esclusi)
    giorno = archivio.carica("SPY", "1Day_raw")
    ufficiali = dict(zip(controlli.date_ny(giorno.index), giorno["close"].astype(float)))
    giorni = [g for g in sorted(cal.index) if DAL <= g <= FINO]
    gex = copertura_del_giorno_prima(copertura(), sorted(cal.index))
    tutte_ops = operazioni(seduta, seg, ufficiali)
    sotto = {g for g in giorni if gex.get(g, np.nan) < 0}
    sopra = {g for g in giorni if gex.get(g, np.nan) >= 0}
    ops = {g: x for g, x in tutte_ops.items() if g in sotto}
    serie = {}
    for nome, f, c in (("costi", 1.0, True), ("costi doppi", 2.0, True), ("senza costi", 1.0, False)):
        serie[nome] = conto(ops, giorni, f, c)
    gc, saltati = serie["costi"]
    gg = {k: v[0] for k, v in serie.items()}
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P045_ultima_mezzora_gamma", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P045_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P045_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(gg["costi doppi"])
    da_sola = sr_c > sr(spy) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte = t_di(gc.to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(gg["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8
    l_sotto, l_sopra, l_tutti = lordo(ops, sotto), lordo(tutte_ops, sopra), lordo(tutte_ops, set(giorni))
    netti = np.array([x for g, x in gc.items() if g in ops])
    per_anno = pd.Series([g.year for g in ops]).value_counts().sort_index()
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1

    def riga(nome, x):
        return (f"{nome}: {len(x)} operazioni, **{x.mean() * 1e4:+.2f} punti base** a operazione (t {t_di(x):.2f}), in guadagno "
                f"{(x > 0).mean():.0%}") if len(x) else f"{nome}: nessuna operazione"
    testo = ["# Prova 45 — risultati", "",
             f"Calcolato da `python -m stock.prove.p045` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P045_ultima_mezzora_gamma.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* Giorni con la copertura del giorno prima sotto zero {len(sotto)}, sopra o uguale {len(sopra)}; giorni esclusi dal "
             f"controllo dei minuti {len(esclusi)}; operazioni {len(ops)}, saltate per la leva {saltati}; per anno: "
             + ", ".join(f"{y} {n}" for y, n in per_anno.items()) + ".",
             f"* {riga('Prima dei costi, nei giorni sotto zero (la regola)', l_sotto)}; dopo i costi "
             f"{netti.mean() * 1e4 if len(netti) else float('nan'):+.2f} punti base sul conto.",
             f"* Da leggere: {riga('nei giorni sopra o uguale a zero', l_sopra)}; {riga('in tutti i giorni', l_tutti)}.", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(gg['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(gg['costi doppi']):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(gg['senza costi']):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(gg['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove."]
    (QUI / "P045_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
