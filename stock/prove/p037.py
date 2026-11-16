"""Prova 37 — anticipare il ribilanciamento dei fondi 60/40: SPY contro IEF (idea I39; Harvey, Mazzoleni, Melone, NBER w33554).

    python -m stock.prove.p037            # prezzi di Yahoo (senza chiavi), tenuti fuori dal repository; scrive P037_risultati.md

Regole: `P037_ribilanciamento.md` (scritte e committate prima del calcolo).
"""
from __future__ import annotations

from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import archivio, yahoo
from stock.prove.p001 import CAPITALE, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

DAL_DATI, DAL, FINO = "2014-01-02", date(2016, 1, 4), date(2024, 12, 31)
FINE_ARTICOLO = date(2023, 3, 17)
QUOTA_AZIONI = 0.60
FASCE = [round(0.001 * k, 4) for k in range(26)]          # da 0% a 2,5% a passi di 0,1%
SCALA = 0.015
ULTIMI, INDIETRO = 5, 4
LIMITE = 1.0
MEZZO = {"SPY": 0.185e-4, "IEF": 1e-4, "TLT": 1e-4}
SLITTAMENTO, PRESTITO = 1e-4, 0.005
IB_PER_AZIONE, IB_MINIMO, IB_MASSIMO = 0.005, 1.0, 0.01


# --- i segnali ---------------------------------------------------------------------------------------------------------------------
def alla_deriva(w: float, rs: float, rb: float) -> float:
    """Il peso delle azioni dopo un giorno, senza scambi."""
    a, b = w * (1 + rs), (1 - w) * (1 + rb)
    return a / (a + b)


def segnale_fascia(rs: pd.Series, rb: pd.Series, fasce=FASCE) -> pd.Series:
    """La media, sulle fasce, di (peso delle azioni alla chiusura − 60%); un portafoglio torna al 60% quando |peso − 60%| ≥ fascia."""
    w = {d: QUOTA_AZIONI for d in fasce}
    out = []
    for a, b in zip(rs.to_numpy(), rb.to_numpy()):
        somma = 0.0
        for d in fasce:
            x = alla_deriva(w[d], a, b)
            somma += x - QUOTA_AZIONI
            w[d] = QUOTA_AZIONI if abs(x - QUOTA_AZIONI) >= d else x
        out.append(somma / len(fasce))
    return pd.Series(out, index=rs.index)


def ultimo_del_mese(giorni: list[date]) -> list[bool]:
    return [k == len(giorni) - 1 or giorni[k + 1].month != g.month for k, g in enumerate(giorni)]


def segnale_calendario(rs: pd.Series, rb: pd.Series) -> pd.Series:
    """(Peso delle azioni alla chiusura − 60%) di un portafoglio che torna al 60% alla chiusura dell'ultimo giorno di borsa del mese."""
    fine = ultimo_del_mese(list(rs.index))
    w, out = QUOTA_AZIONI, []
    for a, b, f in zip(rs.to_numpy(), rb.to_numpy(), fine):
        x = alla_deriva(w, a, b)
        out.append(x - QUOTA_AZIONI)
        w = QUOTA_AZIONI if f else x
    return pd.Series(out, index=rs.index)


def posizioni(fascia: pd.Series, calendario: pd.Series, finisce_a_fine_mese: bool = False) -> tuple[pd.Series, pd.Series]:
    """Le due posizioni decise alla chiusura di ogni giorno: −fascia/1,5%; il segno di −calendario negli ultimi 5 giorni di borsa del
    mese, il segno del calendario di 4 giorni di borsa prima nel primo giorno del mese, zero negli altri."""
    giorni = list(calendario.index)
    pf = -fascia / SCALA
    c = calendario.to_numpy()
    pc = np.zeros(len(giorni))
    mese = [(g.year, g.month) for g in giorni]
    for k in range(len(giorni)):
        restano = sum(1 for j in range(k, min(k + ULTIMI + 1, len(giorni))) if mese[j] == mese[k])   # compreso oggi
        # il mese finisce dentro i dati se dopo c'è un giorno del mese dopo, o se i dati finiscono a fine mese (31 dicembre 2024)
        finisce = any(mese[j] != mese[k] for j in range(k + 1, len(giorni))) or finisce_a_fine_mese
        if restano <= ULTIMI and finisce:
            pc[k] = np.sign(-c[k])
        if k >= 1 and mese[k - 1] != mese[k]:
            pc[k] = np.sign(c[k - INDIETRO]) if k >= INDIETRO else 0.0
    return pf, pd.Series(pc, index=calendario.index)


def commissione(azioni: float, prezzo: float) -> float:
    if azioni <= 0:
        return 0.0
    return min(max(IB_MINIMO, IB_PER_AZIONE * azioni), IB_MASSIMO * azioni * prezzo)


def conto(w: pd.Series, rs: pd.Series, rb: pd.Series, ps: pd.Series, pb: pd.Series, obbl: str = "IEF", fattore: float = 1.0,
          costi: bool = True, limite: float | None = LIMITE, ritardo: int = 0) -> pd.Series:
    """I rendimenti di ogni giorno: il peso deciso alla chiusura del giorno prima (o `ritardo` giorni prima) per (r_SPY − r_obbl), meno
    gli scambi della differenza di peso su tutte e due le parti, le commissioni e il prestito della parte corta. `ps`, `pb`: le chiusure
    come scambiate (per le azioni intere delle commissioni)."""
    x = w.clip(-limite, limite) if limite is not None else w
    tenuto = x.shift(1 + ritardo).fillna(0.0)
    v, out = CAPITALE, {}
    prima = 0.0
    for g in w.index:
        h = float(tenuto.loc[g])
        r = h * (rs.loc[g] - rb.loc[g])
        if costi:
            d = abs(h - prima)
            c = d * (MEZZO["SPY"] + SLITTAMENTO) + d * (MEZZO[obbl] + SLITTAMENTO)
            c += (commissione(d * v / ps.loc[g], ps.loc[g]) + commissione(d * v / pb.loc[g], pb.loc[g])) / v
            c += abs(h) * PRESTITO / 252
            r -= fattore * c
        out[g] = r
        v *= 1 + r
        prima = h
    return pd.Series(out)


# --- i dati ------------------------------------------------------------------------------------------------------------------------
def carica(simbolo: str) -> pd.DataFrame:
    cartella = archivio.cartella_dati() / "yahoo" / "p037"
    cartella.mkdir(parents=True, exist_ok=True)
    f = cartella / f"{simbolo}.csv.gz"
    if f.exists():
        df = pd.read_csv(f, index_col=0)
        df.index = pd.to_datetime(df.index, utc=True).tz_convert("America/New_York")
    else:
        df = yahoo.prezzi(simbolo, DAL_DATI, FINO.isoformat())
        df.to_csv(f)
    df = df[df.index.date <= FINO]
    return pd.DataFrame({"rett": df["rettificata"].to_numpy(), "close": df["close"].to_numpy()}, index=pd.Index(df.index.date))


def main():
    d = {s: carica(s) for s in ("SPY", "IEF", "TLT")}
    giorni = sorted(set(d["SPY"].index) & set(d["IEF"].index) & set(d["TLT"].index))
    r = {s: d[s]["rett"].reindex(giorni).pct_change().fillna(0.0) for s in d}
    p = {s: d[s]["close"].reindex(giorni) for s in d}
    risultati = {}
    for obbl in ("IEF", "TLT"):
        fa = segnale_fascia(r["SPY"], r[obbl])
        ca = segnale_calendario(r["SPY"], r[obbl])
        pf, pc = posizioni(fa, ca, finisce_a_fine_mese=True)       # i dati finiscono il 31 dicembre 2024
        risultati[obbl] = (fa, ca, pf, pc, (pf + pc) / 2)
    fa, ca, pf, pc, w = risultati["IEF"]
    tieni = [g for g in giorni if DAL <= g <= FINO]

    def serie(peso, obbl="IEF", **k):
        return conto(peso, r["SPY"], r[obbl], p["SPY"], p[obbl], obbl=obbl, **k).loc[tieni]
    gc = serie(w)
    g = {"costi doppi": serie(w, fattore=2.0), "senza costi": serie(w, costi=False), "articolo, senza limite": serie(w, limite=None),
         "solo fascia": serie(pf), "solo calendario": serie(pc), "un giorno di ritardo": serie(w, ritardo=1),
         "con TLT": serie(risultati["TLT"][4], "TLT")}
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    ys = r["SPY"].loc[tieni].iloc[1:]
    comune = spy.index.intersection(ys.index)
    corr_fonti = float(np.corrcoef(spy.loc[comune], ys.loc[comune])[0, 1])
    diff_fonti = float((spy.loc[comune] - ys.loc[comune]).abs().median() * 1e4)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P037_ribilanciamento", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P037_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P037_miscela"]
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
    prima, dopo = gc[gc.index <= FINE_ARTICOLO], gc[gc.index > FINE_ARTICOLO]
    senza_marzo = gc[~((gc.index >= date(2020, 3, 1)) & (gc.index <= date(2020, 3, 31)))]
    migliori = gc.sort_values(ascending=False).iloc[:10]
    quota_10 = float(np.log1p(migliori).sum() / np.log1p(gc).sum()) if np.log1p(gc).sum() > 0 else float("nan")
    wt = w.loc[tieni]
    righe_lettura = [f"| {k} | {sr(v):.2f} | {tot(v):+.1%} | {dd(v):.1%} |" for k, v in g.items()]
    testo = ["# Prova 37 — risultati", "",
             f"Calcolato da `python -m stock.prove.p037` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P037_ribilanciamento.md` (committate prima). Dal {a} al {b}, {len(gc)} giorni; prezzi di Yahoo (seconda fonte: rendimenti "
             f"di SPY contro Alpaca, correlazione {corr_fonti:.4f}, differenza mediana {diff_fonti:.2f} punti base). Nel conto "
             f"dell'asticella: {len(tutte)} serie.", "",
             f"* Peso medio |w| {wt.abs().mean():.2f}, massimo {wt.abs().max():.2f} (limitato a 1 nell'esame: giorni oltre il limite "
             f"{int((wt.abs() > LIMITE).sum())}); giorni con la parte di calendario accesa {int((pc.loc[tieni] != 0).sum())}; "
             f"correlazione fra le due parti {float(np.corrcoef(pf.loc[tieni], pc.loc[tieni])[0, 1]):.2f}.",
             f"* Asimmetria dei rendimenti {gc.skew():.2f}; dai 10 giorni migliori viene il {quota_10:.0%} del guadagno (in logaritmi).", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(g['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(g['costi doppi']):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(g['senza costi']):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Fino al 17 marzo 2023 (dentro il campione dell'articolo) / dopo | Sharpe {sr(prima):.2f} / {sr(dopo):.2f} "
             f"({tot(prima):+.1%} / {tot(dopo):+.1%}) | — |",
             f"| Senza marzo 2020 | Sharpe {sr(senza_marzo):.2f} | — |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(g['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "**Da leggere accanto (non cambiano l'esito):**", "", "| Versione | Sharpe | Guadagno totale | Perdita massima |",
             "|---|---|---|---|", *righe_lettura, "", "Nel conto: 2 prove (91)."]
    (QUI / "P037_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-28:]))


if __name__ == "__main__":
    main()
