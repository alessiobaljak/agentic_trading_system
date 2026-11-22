"""Prova 45b — l'esame «da crisi» della prova 45 sul periodo chiuso, dal 2 gennaio 2025 al 30 settembre 2026 (`P045b_esame_da_crisi.md`,
scritto prima). Si lancia UNA volta (decisione del proprietario del 22 novembre 2026: le idee si provano da sole).

    python -m stock.prove.p045b       # gira su GitHub (azioni-ricerca); i prezzi del periodo chiuso nei tipi d'archivio `*_chiuso`

Regola, dati e costi identici alla prova 45 (`p045.py`); cambiano solo le date.
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli
from stock.prove import p045
from stock.prove.p001 import QUI, salva_serie
from stock.prove.p002_chiuso import PRIMO, ULTIMO, scarica, tenere
from stock.prove.p032 import t_di
from stock.prove.p035 import dd, sr, tot
from stock.strategie import ultima_mezzora as um

MINIMO = 20


def mese_migliore_tolto(ops: dict) -> tuple[str, float, float]:
    """Il mese con la somma lorda più alta, la sua somma e la somma lorda degli altri mesi."""
    per_mese: dict[str, float] = {}
    for g, (d, _, p_in, p_out) in ops.items():
        k = f"{g.year}-{g.month:02d}"
        per_mese[k] = per_mese.get(k, 0.0) + d * (p_out / p_in - 1)
    if not per_mese:
        return "", 0.0, 0.0
    m = max(per_mese, key=per_mese.get)
    return m, per_mese[m], sum(v for k, v in per_mese.items() if k != m)


def esito(l_sotto: np.ndarray, l_sopra: np.ndarray, tot_c: float, tot_2: float, resto: float, corr_spy: float,
          sr_misto: float, sr_spy: float) -> tuple[str, list[bool]]:
    """Le quattro condizioni dell'esame da crisi; con meno di 20 operazioni «non si può dire»."""
    if len(l_sotto) < MINIMO:
        return "non si può dire (meno di 20 operazioni)", []
    c = [bool(l_sotto.mean() > 0 and l_sotto.mean() > (l_sopra.mean() if len(l_sopra) else 0.0)),
         bool(tot_c > 0 and tot_2 > 0), bool(resto > 0), bool(corr_spy < 0.3 and sr_misto > sr_spy)]
    return ("passa l'esame da crisi" if all(c) else "bocciata nel periodo chiuso"), c


def main():
    cal = alpaca.calendario("2024-11-01", "2026-09-30")
    scarica("SPY")
    minuti = archivio.carica("SPY", "1Min_raw_chiuso")
    seduta = um.solo_seduta(minuti, cal)
    problemi, _ = controlli.controlla_minuti(minuti, cal)
    esclusi = {date.fromisoformat(p["quando"]) for p in problemi if p["controllo"] == "minuti mancanti"}
    seg = um.prepara(seduta, cal, esclusi)
    giorno = archivio.carica("SPY", "1Day_raw_chiuso")
    ufficiali = dict(zip(controlli.date_ny(giorno.index), giorno["close"].astype(float)))
    giorni = [g for g in sorted(cal.index) if PRIMO <= g <= ULTIMO]
    gex = p045.copertura_del_giorno_prima(p045.copertura(), sorted(cal.index))
    tutte_ops = {g: x for g, x in p045.operazioni(seduta, seg, ufficiali).items() if PRIMO <= g <= ULTIMO}
    sotto = {g for g in giorni if gex.get(g, np.nan) < 0}
    sopra = {g for g in giorni if gex.get(g, np.nan) >= 0}
    ops = {g: x for g, x in tutte_ops.items() if g in sotto}
    gc, saltati = p045.conto(ops, giorni)
    g2, _ = p045.conto(ops, giorni, 2.0)
    g0, _ = p045.conto(ops, giorni, costi=False)
    l_sotto, l_sopra = p045.lordo(ops, sotto), p045.lordo(tutte_ops, sopra)
    mese, somma_mese, resto = mese_migliore_tolto(ops)
    spy = tenere("SPY")
    comuni = spy.index.intersection(gc.index)
    corr_spy = float(np.corrcoef(gc.loc[comuni], spy.loc[comuni])[0, 1]) if len(comuni) > 2 else float("nan")
    misto = 0.75 * spy.loc[comuni] + 0.25 * gc.loc[comuni]
    verdetto, cond = esito(l_sotto, l_sopra, tot(gc), tot(g2), resto, corr_spy, sr(misto), sr(spy.loc[comuni]))
    salva_serie("P045_chiuso", gc)
    # da leggere: la chiusura ufficiale di Yahoo al posto di quella di Alpaca
    try:
        from stock.dati import yahoo
        y = yahoo.prezzi("SPY", "2024-12-01", "2026-09-30")
        uff_y = dict(zip([x.date() for x in y.index], y["close"].astype(float)))
        ops_y = {g: x for g, x in p045.operazioni(seduta, seg, uff_y).items() if g in sotto and PRIMO <= g <= ULTIMO}
        l_y = p045.lordo(ops_y, sotto)
        yahoo_txt = f"{len(l_y)} operazioni, {l_y.mean() * 1e4:+.2f} punti base (t {t_di(l_y):.2f})" if len(l_y) else "nessuna"
    except Exception as e:  # noqa: BLE001 — solo una lettura accanto
        yahoo_txt = f"non calcolata ({type(e).__name__})"
    per_mese = pd.Series([f"{g.year}-{g.month:02d}" for g in ops]).value_counts().sort_index()
    aprile = p045.lordo({g: x for g, x in ops.items() if g.year == 2025 and g.month == 4}, sotto)

    def riga(nome, x):
        return (f"{nome}: {len(x)} operazioni, **{x.mean() * 1e4:+.2f} punti base** a operazione (t {t_di(x):.2f}), in guadagno "
                f"{(x > 0).mean():.0%}") if len(x) else f"{nome}: nessuna operazione"
    nomi = ["1. il segnale c'è ancora", "2. il guadagno c'è, anche con i costi doppi", "3. non un solo mese",
            "4. serve accanto a chi tiene lo SPY"]
    testo = ["# Prova 45b — l'esame da crisi sul periodo chiuso", "",
             f"Calcolato UNA volta da `python -m stock.prove.p045b` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P045b_esame_da_crisi.md` (committate prima). Dal {PRIMO} al {ULTIMO}.", "",
             f"* Giorni con la copertura del giorno prima sotto zero {len(sotto)}, sopra o uguale {len(sopra)}; esclusi dal controllo "
             f"dei minuti {len(esclusi)}; operazioni {len(ops)}, saltate per la leva {saltati}; per mese: "
             + (", ".join(f"{m} {n}" for m, n in per_mese.items()) or "nessuna") + ".",
             f"* {riga('Nei giorni sotto zero (la regola)', l_sotto)}; {riga('nei giorni sopra o uguale a zero', l_sopra)}.",
             f"* Il mese migliore {mese or '—'} vale {somma_mese * 1e4:+.1f} punti base lordi; gli altri insieme {resto * 1e4:+.1f}. "
             f"Aprile 2025 da solo: {riga('', aprile).lstrip(': ')}.",
             f"* Guadagno senza costi / con i costi / costi doppi: {tot(g0):+.2%} / {tot(gc):+.2%} / {tot(g2):+.2%}; Sharpe con i "
             f"costi {sr(gc):.2f}; perdita massima {dd(gc):.1%}. Correlazione giornaliera con lo SPY {corr_spy:.2f}; tre quarti SPY e "
             f"un quarto la parte: Sharpe {sr(misto):.2f} contro {sr(spy.loc[comuni]):.2f} del solo SPY.",
             f"* Da leggere: con la chiusura ufficiale di Yahoo nei giorni sotto zero {yahoo_txt}.", "",
             "| Condizione | Esito |", "|---|---|", *[f"| {n} | {'sì' if c else 'no'} |" for n, c in zip(nomi, cond)], "",
             f"**Esito: {verdetto}.** Conta 1 prova nel registro (un'apertura del periodo chiuso)."]
    (QUI / "P045b_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
