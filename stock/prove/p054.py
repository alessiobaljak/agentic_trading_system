"""Prova 54 — il ciclo della banca centrale: SPY al 98% del conto solo nelle settimane pari dopo ogni riunione programmata (settimane 0,
2, 4 e 6 contate dal comunicato, più il giorno prima), contanti al tasso dei buoni del Tesoro negli altri giorni
(`P054_ciclo_banca_centrale.md`, regole scritte prima; `METODO.md` sezione 4: due campioni e contanti al tasso DTB3).

    python -m stock.prove.p054        # in locale: SPY di Yahoo (dal 1993) e DTB3 di FRED, in memoria (mai nel repository)

Il periodo chiuso (2 gennaio 2025 → 30 settembre 2026) non si apre: i prezzi si scaricano fino al 31 dicembre 2024 e, a parte, dal 16
settembre 2026; di quel secondo pezzo si usano solo le date dei giorni di borsa (per contare i giorni dal comunicato del 16 settembre)
e la chiusura del 30 settembre come prezzo di partenza del primo giorno in avanti (il 1° ottobre).
"""
from __future__ import annotations

import io
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati.fomc import (
    COMUNICATI,
    COMUNICATI_1994_2015,
    COMUNICATI_AVANTI,
    COMUNICATI_CHIUSO,
)
from stock.prove.p001 import CAPITALE, QUI, carica_serie, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import commissione, dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

QUOTA, SLIT = 0.98, 2e-4
PARI = ((0, 3), (9, 13), (19, 23), (29, 33))         # settimane 0, 2, 4, 6 (settimana k = giorni da 5k−1 a 5k+3; il −1 a parte)
DISPARI = ((4, 8), (14, 18), (24, 28))              # settimane 1, 3, 5: solo da leggere
STUDIO = (date(1994, 1, 3), date(2015, 12, 31))     # il campione dello studio: si legge, non conferma
RICERCA = (date(2016, 1, 4), date(2024, 12, 31))    # il periodo di ricerca: decide
CHIUSO_DAL, CHIUSO_AL = date(2025, 1, 1), date(2026, 9, 30)
AVANTI_DAL = date(2026, 10, 1)
DTB3 = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DTB3"
SENZA_ANNUNCIO = date(2003, 9, 15)                  # la riunione senza comunicato del giorno prima di quella del 16 settembre 2003
AMBIGUITA = [
    "* **Le riunioni senza comunicato.** Fino al marzo 1999 la banca centrale non pubblicava un comunicato dopo le riunioni senza "
    "cambi (30 delle 48 riunioni del 1994-1999): il giorno 0 è comunque l'ultimo giorno della riunione programmata, come nello studio.",
    "* **Il 15 settembre 2003.** La pagina della Fed elenca una riunione il 15 e una il 16; il comunicato e i documenti per la decisione "
    "sono del 16: il 15 resta fuori (con il 15 dentro i giorni in mercato sono gli stessi, controllato sopra).",
    "* **Prima del 4 febbraio 1994** (il primo comunicato della storia) non c'è un «comunicato più recente»: quei giorni sono fuori, "
    "tranne il 3 febbraio (giorno −1). Nessuna riunione del 1993 aggiunta.",
    "* **I contanti.** Rende il tasso anche il 2% non investito nei giorni in mercato (`METODO.md`: «i contanti di una prova»). «Il "
    "valore del giorno prima» è l'ultimo DTB3 pubblicato con data prima del giorno di borsa; interesse semplice, DTB3/360 per ogni giorno "
    "di calendario dalla chiusura di borsa prima.",
    "* **Il 98%** si applica al rendimento di ogni giorno (0,98 × lo SPY), come le prove 49-52; si paga solo quando la quota passa da 0 "
    "a 98% o al contrario.",
    "* **Le settimane dispari** da leggere sono le settimane 1, 3 e 5 (d da 4 a 8, da 14 a 18, da 24 a 28, tolti i giorni −1); accanto, "
    "tutti i giorni fuori (anche d da 34 in su e i giorni senza ciclo).",
    "* **Nel conto 1 prova**, come scritto nelle regole: si salva solo `serie/P054_ciclo.csv`; la miscela nuova (3/4 e 1/4) si calcola "
    "in memoria e non entra nel conto (le prove 48-53 salvavano anche la miscela e contavano 2).",
    "* **Il 1994-2015 «con lo stesso esame»**: le stesse quattro condizioni con le stesse funzioni; lo Sharpe corretto con lo stesso "
    "conto delle serie (tutte del 2016-2024); i trimestri dalle finestre che avanzano dal 1994 (primo trimestre di prova il 1995). "
    "L'esame della miscela non si può fare (la miscela della prova 25 parte nel novembre 2016).",
    "* **L'inizio e la fine dei campioni**: il conto parte prima (dal 1993 e dal giugno 2015) e si taglia al primo giorno del campione, "
    "come la prova 52: il primo giorno la posizione è già quella della regola, senza il costo d'ingresso; l'ultimo giorno nessuna vendita "
    "forzata.",
    "* **I giorni in avanti** partono dal rendimento del 1° ottobre 2026 (dalla chiusura del 30 settembre), senza posizione e con il "
    "costo d'ingresso; d si conta dal comunicato del 16 settembre 2026 con le date dei giorni di borsa di Yahoo. Nessun rendimento del "
    "periodo chiuso è calcolato.",
    "* **Tenere lo SPY** è lo SPY rettificato di Yahoo sugli stessi giorni (come la prova 52).",
]


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def giorni_dal_comunicato(calendario: list[date], comunicati: list[date]) -> dict[date, int | None]:
    """d per ogni giorno di borsa: i giorni di borsa dal comunicato più recente (0 il giorno del comunicato); None prima del primo."""
    giorni = set(calendario)
    fuori = [c for c in comunicati if calendario[0] <= c <= calendario[-1] and c not in giorni]
    if fuori:
        raise ValueError(f"comunicati in giorni senza borsa: {fuori}")
    com, d, out = set(comunicati), None, {}
    for g in calendario:
        d = 0 if g in com else (None if d is None else d + 1)
        out[g] = d
    return out


def vigilie(calendario: list[date], comunicati: list[date]) -> set[date]:
    """Il giorno di borsa prima di ogni comunicato (dentro il calendario)."""
    com = set(comunicati)
    return {calendario[k - 1] for k in range(1, len(calendario)) if calendario[k] in com}


def _dentro(d: int | None, intervalli) -> bool:
    return d is not None and any(a <= d <= b for a, b in intervalli)


def settimane_pari(calendario: list[date], comunicati: list[date]) -> pd.Series:
    """True nei giorni di borsa delle settimane pari: d da 0 a 3, da 9 a 13, da 19 a 23, da 29 a 33, più il giorno prima di ogni
    comunicato. Sono i giorni il cui rendimento (da chiusura a chiusura) si prende nello SPY."""
    d, v = giorni_dal_comunicato(calendario, comunicati), vigilie(calendario, comunicati)
    return pd.Series({g: g in v or _dentro(d[g], PARI) for g in calendario})


def settimane_dispari(calendario: list[date], comunicati: list[date]) -> pd.Series:
    """True nei giorni delle settimane 1, 3 e 5 (d da 4 a 8, da 14 a 18, da 24 a 28), tolti i giorni prima di un comunicato."""
    d, v = giorni_dal_comunicato(calendario, comunicati), vigilie(calendario, comunicati)
    return pd.Series({g: g not in v and _dentro(d[g], DISPARI) for g in calendario})


def quote(dentro: pd.Series) -> pd.Series:
    """La quota decisa alla chiusura di ogni giorno di borsa: 98% se il giorno di borsa dopo è nelle settimane pari, 0 altrimenti. Si
    compra alla chiusura del giorno prima del primo giorno della finestra, si vende alla chiusura dell'ultimo; due finestre attaccate
    sono una sola. L'ultimo giorno del calendario non ha quota (si tiene quello che c'è)."""
    g, x = list(dentro.index), dentro.to_numpy()
    return pd.Series({g[k]: QUOTA if bool(x[k + 1]) else 0.0 for k in range(len(g) - 1)})


def contanti(calendario: list[date], dtb3: pd.Series) -> pd.Series:
    """Il rendimento dei contanti per ogni giorno di borsa dopo il primo: il DTB3 del giorno prima (l'ultimo valore pubblicato con data
    prima del giorno, in punti percentuali) diviso 360, per i giorni di calendario dalla chiusura di borsa prima."""
    t = dtb3.dropna().sort_index()
    date_t = list(t.index)
    out, j = {}, 0
    for k in range(1, len(calendario)):
        g = calendario[k]
        while j < len(date_t) and date_t[j] < g:
            j += 1
        if j == 0:
            raise ValueError(f"nessun DTB3 prima del {g}")
        out[g] = float(t.iloc[j - 1]) / 100 / 360 * (g - calendario[k - 1]).days
    return pd.Series(out)


def conto(chiusure: pd.Series, quota: pd.Series, cassa: pd.Series, fattore: float = 1.0, costi: bool = True) -> pd.Series:
    """I rendimenti di ogni giorno di borsa: la quota decisa alla chiusura di ieri per il rendimento di oggi, il resto dei contanti al
    rendimento di `cassa`; a ogni cambio, slittamento (2 punti base) e commissione di Interactive Brokers sulla parte comprata o
    venduta, all'asta di chiusura. Un cambio alla chiusura del primo giorno si paga sul rendimento del secondo."""
    r = chiusure.pct_change()
    giorni = list(chiusure.index)
    tenuta, v, out, da_pagare = 0.0, CAPITALE, {}, 0.0
    for k, g in enumerate(giorni):
        x = 0.0 if k == 0 else tenuta * float(r.loc[g]) + (1 - tenuta) * float(cassa.get(g, 0.0)) - da_pagare
        da_pagare = 0.0
        nuova = float(quota.get(g, tenuta))
        if costi and nuova != tenuta:
            delta = abs(nuova - tenuta)
            n = int(delta * v / float(chiusure.loc[g]))
            c = fattore * (delta * SLIT + commissione(n, float(chiusure.loc[g])) / v)
            if k == 0:
                da_pagare = c
            else:
                x -= c
        tenuta = nuova
        if k > 0:
            out[g] = x
            v *= 1 + x
    return pd.Series(out)


def trimestri(g: pd.Series, dal: date, al: date) -> list[float]:
    """Il guadagno di ogni trimestre di prova delle finestre che avanzano (12 mesi di scelta, 3 di prova), come le prove prima."""
    return [float((1 + g[(g.index >= x) & (g.index < y)]).prod() - 1)
            for x, y in (f["prova"] for f in finestre(dal, al, chiuso_dal=al)) if x >= g.index.min()]


# --- con la rete -------------------------------------------------------------------------------------------------------------------
def spy(dal: str, al: str) -> pd.Series:
    from stock.dati import yahoo
    df = yahoo.prezzi("SPY", dal, al)
    return pd.Series(df["rettificata"].to_numpy(float), index=pd.Index([x.date() for x in df.index])).sort_index()


def dtb3() -> pd.Series:
    import requests
    r = requests.get(DTB3, timeout=60)
    r.raise_for_status()
    d = pd.read_csv(io.StringIO(r.text))
    d.columns = ["giorno", "tasso"]
    return pd.Series(pd.to_numeric(d["tasso"], errors="coerce").to_numpy(),
                     index=pd.Index(pd.to_datetime(d["giorno"]).dt.date)).dropna()


def calcola_campione(ch: pd.Series, tassi: pd.Series, com: list[date], dal: date, al: date) -> dict:
    """Il conto di un campione: prezzi e date dal riscaldamento (prima di `dal`) ad `al`; le serie tagliate da `dal`."""
    ch = ch[ch.index <= al]
    cal = list(ch.index)
    pari = settimane_pari(cal, com)
    q = quote(pari)
    cassa, zero = contanti(cal, tassi), pd.Series(0.0, index=cal[1:])
    s = {"costi": conto(ch, q, cassa), "costi doppi": conto(ch, q, cassa, 2.0), "senza costi": conto(ch, q, cassa, costi=False),
         "contanti a zero": conto(ch, q, zero)}
    s = {k: x[x.index >= dal] for k, x in s.items()}
    giorni = list(s["costi"].index)
    spy_r = ch.pct_change().reindex(giorni)
    dispari = settimane_dispari(cal, com).reindex(giorni)
    pari_g = pari.reindex(giorni)
    senza_ciclo = pd.Series({g: d is None for g, d in giorni_dal_comunicato(cal, com).items()}).reindex(giorni)
    return {"serie": s, "spy": spy_r, "pari": pari_g, "dispari": dispari, "senza_ciclo": senza_ciclo,
            "cassa": cassa.reindex(giorni), "uguale_2003": bool((settimane_pari(cal, sorted(com + [SENZA_ANNUNCIO])) == pari).all())
            if dal <= SENZA_ANNUNCIO <= al else None}


def lettura_giorni(c: dict) -> list[str]:
    """Lo SPY nei giorni delle settimane pari, delle dispari, di tutti i giorni fuori (da leggere)."""
    sp = c["spy"]
    righe = []
    for nome, m in (("settimane pari (in mercato)", c["pari"]), ("settimane dispari 1, 3, 5", c["dispari"]),
                    ("tutti i giorni fuori", ~c["pari"].astype(bool))):
        x = sp[m.astype(bool)]
        righe.append(f"| {nome} | {len(x)} | {x.mean() * 1e4:+.2f} (t {t_di(x.to_numpy()):.2f}) | {x.std(ddof=1) * np.sqrt(252):.1%} | "
                     f"{sr(x):.2f} |")
    return righe


def esame_da_sola(c: dict, tutte: dict, dal: date, al_escluso: date) -> dict:
    gc, g2 = c["serie"]["costi"], c["serie"]["costi doppi"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = trimestri(gc, dal, al_escluso)
    quota = sum(x > 0 for x in q) / len(q)
    passa = sr(gc) > sr(c["spy"]) and ast["sharpe_corretto"] >= asticella.SOGLIA and sr(g2) > 0 and quota >= 0.6
    return {"ast": ast, "q": q, "quota": quota, "passa": passa}


def tabella(c: dict, e: dict, titolo: str) -> tuple[list[str], pd.Series, pd.Series]:
    """Le righe della tabella dell'esame da sola, e l'anno per anno della strategia e dello SPY."""
    s, sp, ast = c["serie"], c["spy"], e["ast"]
    gc = s["costi"]
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1
    anni_spy = (1 + sp).groupby(pd.Index([x.year for x in sp.index])).prod() - 1
    pos = sum(x > 0 for x in anni)
    return [f"| {titolo} | La strategia | Tenere lo SPY |", "|---|---|---|",
            f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(s['senza costi']):+.1%} / {tot(gc):+.1%} / "
            f"{tot(s['costi doppi']):+.1%} | {tot(sp):+.1%} |",
            f"| **1.** Sharpe annuo con i costi | **{sr(gc):.2f}** (senza costi {sr(s['senza costi']):.2f}) | {sr(sp):.2f} |",
            f"| **2.** Sharpe corretto (soglia {asticella.SOGLIA:.2f}) | {ast['sharpe_corretto']:.2f} (lo Sharpe annuo del migliore fra "
            f"prove senza vantaggio {ast['soglia_giornaliera'] * np.sqrt(252):.2f}; gruppi {ast['gruppi']}, di cui "
            f"{ast['gruppi_perdenti']} perdenti fuori dalla varianza; con tutti i gruppi nella varianza {ast['sharpe_corretto_tutti']:.2f}; "
            f"t dello Sharpe {ast['t_sharpe']:.2f}) | — |",
            f"| **3.** Sharpe con i costi doppi (> 0) | {sr(s['costi doppi']):.2f} | — |",
            f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in e['q'])} su {len(e['q'])} ({e['quota']:.0%}) | — |",
            f"| Sharpe con i contanti a zero (come le prove prima della 54) | {sr(s['contanti a zero']):.2f} "
            f"({tot(s['contanti a zero']):+.1%}) | — |",
            f"| Volatilità annua | {gc.std(ddof=1) * np.sqrt(252):.1%} | {sp.std(ddof=1) * np.sqrt(252):.1%} |",
            f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(sp):.1%} |",
            f"| Giorni in mercato | {c['pari'].mean():.1%} ({int(c['pari'].sum())} su {len(c['pari'])}) | 100% |",
            f"| Anni in guadagno | {pos} su {len(anni)} | {sum(x > 0 for x in anni_spy)} su {len(anni_spy)} |",
            f"| **Esito da sola** | **{'passa' if e['passa'] else 'non passa'}** | |"], anni, anni_spy


def main():
    oggi = datetime.now(UTC).date()
    prezzi = spy("1993-01-01", "2024-12-31")
    prezzi = prezzi[prezzi.index <= RICERCA[1]]
    tassi = dtb3()
    tassi_prima = tassi[tassi.index < CHIUSO_DAL]
    com = sorted(COMUNICATI_1994_2015 + COMUNICATI)

    studio = calcola_campione(prezzi[prezzi.index >= date(1993, 1, 1)], tassi_prima, com, *STUDIO)
    ricerca = calcola_campione(prezzi[prezzi.index >= date(2015, 6, 1)], tassi_prima, com, *RICERCA)
    gc = ricerca["serie"]["costi"]
    a, b = gc.index.min(), gc.index.max()

    # la serie nel conto: una prova (la miscela nuova si calcola in memoria e non entra nel conto)
    salva_serie("P054_ciclo", gc)
    tutte = carica_serie()
    e_ric = esame_da_sola(ricerca, tutte, date(2016, 1, 1), date(2025, 1, 1))
    e_stu = esame_da_sola(studio, tutte, date(1994, 1, 1), date(2016, 1, 1))

    miscela = tutte["P025_miscela"]
    comuni = miscela.index.intersection(gc.index)
    nuova = 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni]
    g2c = ricerca["serie"]["costi doppi"].reindex(comuni).dropna()
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = ricerca["spy"].reindex(comuni).dropna()
    t_parte = t_di(gc.to_numpy())
    t_senza = t_di(gc[[not (x.year == 2020 and x.month == 3) for x in gc.index]].to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(g2c) > 0 and corr < 0.3 and sr(nuova) > sr(miscela.loc[comuni]) \
        and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and t_senza >= 1.3 and vinte >= 0.8

    # i giorni in avanti dal 1° ottobre 2026: date dal 16 settembre (per contare d), prezzi dal 30 settembre
    avanti_txt = []
    try:
        pa = spy("2026-09-16", oggi.isoformat())
    except Exception as x:        # noqa: BLE001
        pa, avanti_txt = None, [f"* I giorni in avanti: Yahoo non ha risposto ({type(x).__name__}); non calcolati."]
    if pa is not None and len(pa[pa.index >= AVANTI_DAL]):
        cal_a = list(pa.index)
        com_a = [COMUNICATI_CHIUSO[-1]] + COMUNICATI_AVANTI
        pari_a = settimane_pari(cal_a, com_a)
        partenza = max(g for g in cal_a if g < AVANTI_DAL)
        ch_a = pa[pa.index >= partenza]                                    # nessun rendimento prima del 1° ottobre
        cal_c = list(ch_a.index)
        q_a = quote(pari_a.reindex(cal_c))
        ta = tassi[tassi.index >= date(2026, 9, 16)]
        cassa_a = contanti(cal_c, ta)
        ga = conto(ch_a, q_a, cassa_a)
        ga2 = conto(ch_a, q_a, cassa_a, 2.0)
        spy_a = ch_a.pct_change().dropna()
        dentro_a = pari_a.reindex(ga.index)
        sp_dentro, sp_fuori = spy_a[dentro_a.to_numpy()], spy_a[~dentro_a.to_numpy()]
        avanti_txt = [
            f"* **I giorni in avanti** (da leggere; il periodo chiuso non si apre: di settembre 2026 solo le date dal 16 e la chiusura del "
            f"{partenza}): dal {ga.index.min()} al {ga.index.max()}, {len(ga)} giorni di borsa, in mercato {int(dentro_a.sum())}. La "
            f"strategia con i costi **{tot(ga):+.2%}** (costi doppi {tot(ga2):+.2%}), tenere lo SPY **{tot(spy_a):+.2%}**. Lo SPY nei "
            f"giorni delle settimane pari {sp_dentro.mean() * 1e4:+.1f} punti base al giorno ({len(sp_dentro)} giorni), negli altri "
            f"{sp_fuori.mean() * 1e4:+.1f} ({len(sp_fuori)} giorni). Comunicati usati: {COMUNICATI_CHIUSO[-1]} e {COMUNICATI_AVANTI[0]}."]

    tab_r, anni_r, anni_spy_r = tabella(ricerca, e_ric, "2016-2024 (decide)")
    tab_s, anni_s, anni_spy_s = tabella(studio, e_stu, "1994-2015 (campione dello studio: si legge)")
    dentro_r, dentro_s = ricerca["pari"], studio["pari"]
    finestre_r = int((dentro_r.astype(int).diff() == 1).sum() + int(dentro_r.iloc[0]))
    testo = ["# Prova 54 — risultati", "",
             f"Calcolato da `python -m stock.prove.p054` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P054_ciclo_banca_centrale.md` (committate prima). SPY rettificato di Yahoo, DTB3 di FRED (il valore del giorno prima, /360 "
             f"per giorno di calendario). Periodo di ricerca dal {a} al {b}; campione dello studio dal {studio['serie']['costi'].index.min()} "
             f"al {studio['serie']['costi'].index.max()}. Comunicati: {len(COMUNICATI_1994_2015)} riunioni programmate 1994-2015 "
             f"(`stock/dati/fomc.py`, `COMUNICATI_1994_2015`) e {len(COMUNICATI)} del 2016-2024. Nel conto dell'asticella: {len(tutte)} "
             f"serie.", "",
             f"* In mercato nel 2016-2024 il {dentro_r.mean():.1%} dei giorni ({finestre_r} finestre), nel 1994-2015 il {dentro_s.mean():.1%} "
             f"(prima del primo comunicato, 4 febbraio 1994, nessun ciclo: {int(studio['senza_ciclo'].sum())} giorni fuori). Contanti: "
             f"circa {ricerca['cassa'].mean() * 252:.2%} l'anno nel 2016-2024, {studio['cassa'].mean() * 252:.2%} nel "
             f"1994-2015.",
             f"* Con la riunione senza comunicato del 15 settembre 2003 i giorni in mercato sarebbero "
             f"{'gli stessi' if studio['uguale_2003'] else 'DIVERSI'}.", "",
             "## L'esame da sola", "", *tab_r, "", *tab_s, "",
             "## Per entrare nella miscela (2016-2024)", "",
             f"Giorni in comune con la miscela della prova 25 dal {comuni.min()} al {comuni.max()} ({len(comuni)}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(g2c):.2f}; correlazione con la miscela **{corr:.2f}** (soglia 0,3); miscela "
             f"nuova (3/4 miscela, 1/4 la parte, in memoria: non entra nel conto) **{sr(nuova):.2f}** contro {sr(miscela.loc[comuni]):.2f} "
             f"della miscela e {sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f}, senza marzo 2020 "
             f"{t_senza:.2f}** (soglia 1,3 tutti e due); **miscela nuova più alta nel {vinte:.0%} dei campionamenti** (2000 a blocchi di 20 "
             f"giorni, soglia 80%). **Esito: {'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel 1994-2015 l'esame della miscela non si può fare: la miscela della prova 25 esiste solo dal novembre 2016.", "",
             "## Da leggere accanto (non cambiano l'esito)", "",
             "Lo SPY (da chiusura a chiusura, senza costi) nei giorni del ciclo: giorni, rendimento medio in punti base al giorno (t), "
             "volatilità annua, Sharpe annuo.", "",
             "| 2016-2024 | Giorni | Media (t) | Volatilità | Sharpe |", "|---|---|---|---|---|", *lettura_giorni(ricerca), "",
             "| 1994-2015 | Giorni | Media (t) | Volatilità | Sharpe |", "|---|---|---|---|---|", *lettura_giorni(studio), "",
             "Anno per anno, la strategia con i costi (lo SPY fra parentesi):", "",
             "* 2016-2024: " + ", ".join(f"{y} {x:+.1%} ({anni_spy_r[y]:+.1%})" for y, x in anni_r.items()) + ".",
             "* 1994-2015: " + ", ".join(f"{y} {x:+.1%} ({anni_spy_s[y]:+.1%})" for y, x in anni_s.items()) + ".", "",
             *avanti_txt, "",
             "## Ambiguità chiuse così (la lettura più letterale delle regole; scelte nel programma prima della prima esecuzione)", "",
             *AMBIGUITA, "",
             "Nel conto: 1 prova (SPY, una variante)."]
    (QUI / "P054_risultati.md").write_text("\n".join(testo) + "\n")
    corto = [f"2016-2024: Sharpe {sr(gc):.2f} contro {sr(ricerca['spy']):.2f}; corretto {e_ric['ast']['sharpe_corretto']:.2f}; costi doppi "
             f"{sr(ricerca['serie']['costi doppi']):.2f}; trimestri {e_ric['quota']:.0%} → {'passa' if e_ric['passa'] else 'non passa'}",
             f"1994-2015: Sharpe {sr(studio['serie']['costi']):.2f} contro {sr(studio['spy']):.2f}; corretto "
             f"{e_stu['ast']['sharpe_corretto']:.2f}; trimestri {e_stu['quota']:.0%} → {'passa' if e_stu['passa'] else 'non passa'}",
             f"miscela: corr {corr:.2f}, nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f}, t {t_parte:.2f}/{t_senza:.2f}, "
             f"campionamenti {vinte:.0%} → {'entra' if entra else 'non entra'}", *avanti_txt]
    print("\n".join(corto))


if __name__ == "__main__":
    main()
