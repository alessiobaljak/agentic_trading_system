"""Controllo dopo la revisione della prova 37: la miscela del demo con le chiusure ufficiali di SPY e QQQ (`P025c_chiusure_ufficiali.md`).

    python -m stock.prove.p025c           # prezzi di Yahoo (senza chiavi), tenuti fuori dal repository; scrive P025c_risultati.md

**Non è una prova**: rifà le prove 15 e 16 con gli stessi programmi, cambiando solo apertura, massimo, minimo e chiusura di SPY e QQQ
(Yahoo al posto di Alpaca, sugli stessi giorni dell'archivio, mai dopo il 31 dicembre 2024), e ricalcola la miscela della prova 25. Le
serie e i risultati committati delle prove 15, 16 e 25 non si toccano.
"""
from __future__ import annotations

import tempfile
from datetime import UTC, date, datetime
from pathlib import Path

import numpy as np
import pandas as pd

from stock.dati import alpaca, archivio, controlli, yahoo
from stock.prove import p005
from stock.prove.p001 import QUI, annuo, carica_serie
from stock.simulatore import asticella

FINO = date(2024, 12, 31)
FONDI = ("SPY", "QQQ")
COLONNE = ["open", "high", "low", "close"]


def barre_ufficiali(simbolo: str, alpaca_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Le barre dell'archivio con apertura, massimo, minimo e chiusura di Yahoo sugli stessi giorni (fino al 31 dicembre 2024); e il
    conto dei giorni in cui le due fonti differiscono."""
    cartella = archivio.cartella_dati() / "yahoo" / "p025c"
    cartella.mkdir(parents=True, exist_ok=True)
    f = cartella / f"{simbolo}.csv.gz"
    if f.exists():
        y = pd.read_csv(f, index_col=0)
        y.index = pd.to_datetime(y.index, utc=True).tz_convert("America/New_York")
    else:
        y = yahoo.prezzi(simbolo, "2015-12-01", FINO.isoformat())
        y.to_csv(f)
    y = y[[d <= FINO for d in y.index.date]]
    y.index = pd.Index(y.index.date)
    g = pd.Index(controlli.date_ny(alpaca_raw.index))
    tieni = [d <= FINO for d in g]
    a = alpaca_raw[tieni].copy()
    g = g[tieni]
    mancano = [d for d in g if d not in y.index]
    if mancano:
        raise SystemExit(f"{simbolo}: {len(mancano)} giorni dell'archivio mancano in Yahoo (primo {mancano[0]})")
    conto = {}
    for c in ("open", "close"):
        diff = (a[c].to_numpy() / y.loc[list(g), c].to_numpy() - 1) * 1e4
        conto[c] = (int((np.abs(diff) > 5).sum()), len(diff), float(np.abs(diff).max()))
    for c in COLONNE:
        a[c] = y.loc[list(g), c].to_numpy()
    return a, conto


def main():
    originale = archivio.carica
    ufficiali, conti = {}, {}
    for s in FONDI:
        ufficiali[s], conti[s] = barre_ufficiali(s, originale(s, "1Day_raw"))

    def carica(simbolo: str, tipo: str):
        if simbolo in ufficiali and tipo == "1Day_raw":
            return ufficiali[simbolo].copy()
        return originale(simbolo, tipo)
    archivio.carica = carica
    giorni_spy = sorted(set(controlli.date_ny(ufficiali["SPY"].index)))
    alpaca.calendario = lambda inizio, fine: pd.DataFrame(  # noqa: E731 — senza chiavi: i giorni dell'archivio di SPY
        index=pd.Index([d for d in giorni_spy if str(inizio)[:10] <= d.isoformat() <= str(fine)[:10]], name="data"))
    nuove: dict[str, pd.Series] = {}
    p005.salva_serie = lambda nome, s: nuove.__setitem__(nome, s)
    p005.QUI = Path(tempfile.mkdtemp())                       # i risultati di p005 non sovrascrivono quelli committati

    from stock.prove.p011 import carica_tutti, membri_dell_indice
    from stock.strategie import ampiezza as amp
    from stock.strategie.tendenza import strategia_calma
    p005.esegui("15", "P015_calma_e_agitazione.md", lambda s, cal, rett: strategia_calma(s, cal, rett),
                lambda rett, esecuzioni: esecuzioni["giorno"].min(), leva_massima=1.5, interesse=0.06)
    membri, simboli = membri_dell_indice()
    _, rett, _ = carica_tutti(simboli, FINO)
    cal = list(alpaca.calendario("2016-01-01", "2024-12-31").index)
    serie = amp.serie_ampiezza(rett, membri, cal)
    p005.esegui("16", "P016_ampiezza.md", lambda s, c, r: amp.strategia(s, c, serie), lambda r, esecuzioni: esecuzioni["giorno"].min())

    vecchie = carica_serie()
    parti_v = ["P007_SPY", "P007_QQQ", "P015_SPY", "P015_QQQ", "P016_SPY", "P016_QQQ"]
    parti_n = {p: (nuove[p] if p in nuove else vecchie[p]) for p in parti_v}
    m_v = vecchie["P025_miscela"]
    m_n = pd.DataFrame(parti_n).dropna().mean(axis=1)
    a, b = m_n.index.min(), m_n.index.max()
    from stock.prove.p001 import comprare_e_tenere
    spy, qqq = comprare_e_tenere("SPY", a, b), comprare_e_tenere("QQQ", a, b)       # con le chiusure ufficiali (archivio cambiato)
    meta = (0.5 * spy + 0.5 * qqq.reindex(spy.index)).dropna()
    archivio.carica = originale
    spy_v = comprare_e_tenere("SPY", a, b)
    sr = lambda x: annuo(asticella.sharpe(x))  # noqa: E731
    tot = lambda x: (1 + x).prod() - 1  # noqa: E731
    dd = lambda x: ((1 + x).cumprod() / (1 + x).cumprod().cummax() - 1).min()  # noqa: E731
    resta = sr(m_n) > sr(spy) and sr(m_n) > sr(meta)
    righe_parti = [f"| {p} | {sr(vecchie[p].loc[a:b]):.2f} | {sr(parti_n[p].loc[a:b]):.2f} | {tot(vecchie[p].loc[a:b]):+.1%} | "
                   f"{tot(parti_n[p].loc[a:b]):+.1%} |" for p in parti_v]
    testo = ["# Controllo dopo la revisione della prova 37 — la miscela del demo con le chiusure ufficiali", "",
             f"Calcolato da `python -m stock.prove.p025c` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con il metodo di "
             "`P025c_chiusure_ufficiali.md` (scritto prima). **Non è una prova**: stesse regole delle prove 15, 16 e 25, cambiano solo "
             f"apertura, massimo, minimo e chiusura di SPY e QQQ (Yahoo al posto di Alpaca). Dal {a} al {b}.", "",
             "**Le due fonti** (giorni oltre 5 punti base di differenza / giorni / differenza massima in punti base): " +
             "; ".join(f"{s} apertura {conti[s]['open'][0]}/{conti[s]['open'][1]} ({conti[s]['open'][2]:.0f}), chiusura "
                       f"{conti[s]['close'][0]}/{conti[s]['close'][1]} ({conti[s]['close'][2]:.0f})" for s in FONDI) + ".", "",
             "| Parte | Sharpe prima (Alpaca) | Sharpe con le chiusure ufficiali | Guadagno prima | Guadagno con le chiusure ufficiali |",
             "|---|---|---|---|---|", *righe_parti, "",
             "| | Miscela prima | Miscela con le chiusure ufficiali | Tenere lo SPY (ufficiali) | Metà SPY e metà QQQ (ufficiali) |",
             "|---|---|---|---|---|",
             f"| Sharpe con i costi | {sr(m_v.loc[a:b]):.2f} | **{sr(m_n):.2f}** | {sr(spy):.2f} (Alpaca {sr(spy_v):.2f}) | {sr(meta):.2f} |",
             f"| Guadagno totale | {tot(m_v.loc[a:b]):+.1%} | {tot(m_n):+.1%} | {tot(spy):+.1%} | {tot(meta):+.1%} |",
             f"| Perdita massima | {dd(m_v.loc[a:b]):.1%} | {dd(m_n):.1%} | {dd(spy):.1%} | {dd(meta):.1%} |",
             f"| Correlazione giornaliera fra prima e ora | {float(np.corrcoef(m_v.reindex(m_n.index).fillna(0), m_n)[0, 1]):.4f} | | | |",
             "",
             f"**Esito (regola scritta prima):** {'la miscela resta sopra il tenere lo SPY e metà SPY metà QQQ: resta sul demo come è' if resta else 'la miscela scende sotto: va detto subito al proprietario'}."]
    (QUI / "P025c_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
