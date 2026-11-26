"""Prova 53 — i giudizi degli analisti: dopo una promozione comprato il titolo e venduto lo SPY, dopo una bocciatura il contrario, alla
chiusura del giorno dopo l'annuncio, per 20 sedute (`P053_giudizi_degli_analisti.md`, regole scritte prima; la forma della prova 46).

    python -m stock.prove.p053        # gira su GitHub (azioni-ricerca): notizie e prezzi di Alpaca nella memoria del lavoro

Le notizie non si stampano né si pubblicano (licenza): solo conteggi.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.prove.p001 import CAPITALE, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import commissione, dd, sr, tot
from stock.prove.p046 import TIPI, giorno_annuncio, relativo
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

DAL, ULTIMO, FINO = date(2016, 1, 4), date(2024, 11, 30), date(2024, 12, 31)
SEDUTE, QUOTA, MASSIMO, SIMBOLI_MASSIMI = 20, 0.05, 20, 3
SLIT, PRESTITO = 2e-4, 0.005
SU = re.compile(r"\bupgrade(s|d)?\b", re.IGNORECASE)
GIU = re.compile(r"\bdowngrade(s|d)?\b", re.IGNORECASE)


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def lato(titolo: str) -> int:
    """+1 promozione, −1 bocciatura, 0 niente o tutte e due."""
    su, giu = bool(SU.search(titolo)), bool(GIU.search(titolo))
    return 0 if su == giu else (1 if su else -1)


def scegli_notizie(notizie: pd.DataFrame, membri_al, calendario: list[date]) -> tuple[pd.DataFrame, dict]:
    """Gli annunci: notizie con un lato, al massimo 3 simboli ed esattamente un membro dell'S&P 500 di allora. Colonne: simbolo,
    annuncio, lato."""
    conta = {"notizie": len(notizie), "con un lato": 0, "più di 3 simboli": 0, "nessun membro": 0, "due o più membri": 0}
    righe = []
    for r in notizie.itertuples():
        x = lato(r.titolo)
        if x == 0:
            continue
        conta["con un lato"] += 1
        if len(r.simboli) > SIMBOLI_MASSIMI:
            conta["più di 3 simboli"] += 1
            continue
        g = giorno_annuncio(r.creata, calendario)
        if g is None or not (DAL <= g <= ULTIMO):
            continue
        dentro = sorted(set(r.simboli) & membri_al(g))
        if not dentro:
            conta["nessun membro"] += 1
            continue
        if len(dentro) > 1:
            conta["due o più membri"] += 1
            continue
        righe.append({"simbolo": dentro[0], "annuncio": g, "lato": x})
    return pd.DataFrame(righe, columns=["simbolo", "annuncio", "lato"]), conta


@dataclass(frozen=True)
class Operazione:
    simbolo: str
    lato: int
    giorno_in: date
    p_in: float
    f_in: float
    giorno_out: date
    p_out: float
    f_out: float
    spy_in: float
    spy_f_in: float
    spy_out: float
    spy_f_out: float

    @property
    def titolo(self) -> float:
        return self.p_out * self.f_out / (self.p_in * self.f_in) - 1

    @property
    def spy(self) -> float:
        return self.spy_out * self.spy_f_out / (self.spy_in * self.spy_f_in) - 1


def scegli_ingressi(ops: list[Operazione], massimo: int = MASSIMO) -> list[Operazione]:
    """In ordine d'ingresso (a pari giorno alfabetico): al massimo `massimo` aperte; una posizione aperta sullo stesso titolo blocca."""
    aperte, out = [], []
    for op in sorted(ops, key=lambda o: (o.giorno_in, o.simbolo)):
        aperte = [a for a in aperte if a.giorno_out >= op.giorno_in]
        if len(aperte) >= massimo or any(a.simbolo == op.simbolo for a in aperte):
            continue
        aperte.append(op)
        out.append(op)
    return out


def conto(ops: list[Operazione], giorni: list[date], fattore: float = 1.0, costi: bool = True) -> pd.Series:
    """I rendimenti di ogni giorno: il 5% del conto nel titolo (comprato o venduto) e lo stesso valore di SPY dalla parte opposta, alla
    chiusura dell'ingresso; il guadagno contato il giorno dell'uscita (come la prova 46)."""
    per_in: dict[date, list[Operazione]] = {}
    for op in ops:
        per_in.setdefault(op.giorno_in, []).append(op)
    v, da_contare, out = CAPITALE, {}, {}
    for g in giorni:
        inizio = v
        for op in per_in.get(g, []):
            n = math.floor(QUOTA * inizio / op.p_in)
            m = math.floor(n * op.p_in / op.spy_in)
            if n <= 0 or m <= 0:
                continue
            nel_titolo, nello_spy = n * op.p_in, m * op.spy_in
            utile = op.lato * (nel_titolo * op.titolo - nello_spy * op.spy)
            if costi:
                c = SLIT * (nel_titolo * (2 + op.titolo) + nello_spy * (2 + op.spy))
                c += commissione(n, op.p_in) + commissione(n, op.p_in * (1 + op.titolo))
                c += commissione(m, op.spy_in) + commissione(m, op.spy_in * (1 + op.spy))
                venduto = nel_titolo if op.lato < 0 else nello_spy
                c += venduto * PRESTITO * (op.giorno_out - op.giorno_in).days / 365
                utile -= fattore * c
            da_contare[op.giorno_out] = da_contare.get(op.giorno_out, 0.0) + utile
        u = da_contare.pop(g, 0.0)
        out[g] = u / inizio
        v += u
    return pd.Series(out)


# --- con i prezzi ------------------------------------------------------------------------------------------------------------------
def main():
    from stock.dati import archivio, controlli, notizie
    from stock.prove.p027 import scarica
    from stock.prove.p028 import decisioni
    from stock.prove.p034 import membri_al
    from stock.prove.p042 import giorni_e_dollari
    from stock.prove.p051 import titoli_delle_notizie
    if notizie.mancanti(2016, 2024):
        raise SystemExit(f"mancano {len(notizie.mancanti(2016, 2024))} mesi di notizie: prima `python -m stock.prove.p028b`")
    scarica(["SPY"])
    cal = sorted(d for d in controlli.date_ny(archivio.carica("SPY", "1Day_raw").index) if d <= FINO)
    fini, membri = decisioni()
    ann, conta = scegli_notizie(titoli_delle_notizie(), lambda g: membri_al(g, fini, membri), cal)
    simboli = sorted(set(ann["simbolo"]))
    scarica(simboli, TIPI["raw"], TIPI["az"], TIPI["asof"])
    prezzi = {s: x[0] for s in simboli if (x := giorni_e_dollari(s, TIPI["raw"], TIPI["az"])) is not None}
    spy = giorni_e_dollari("SPY", "1Day_raw", "azioni")[0]
    pos = {g: i for i, g in enumerate(cal)}
    tutte, fuori = [], {"senza prezzi": 0, "uscita oltre il 2024": 0}
    lettura = {(x, h): [] for x in (1, -1) for h in ("prima", 1, 5, 20)}
    for r in ann.itertuples():
        d, k = prezzi.get(r.simbolo), pos.get(r.annuncio)
        if d is None or k is None or k < 1 or k + 1 >= len(cal):
            fuori["senza prezzi"] += 1
            continue
        gi = cal[k + 1]
        if gi not in d or gi not in spy:
            fuori["senza prezzi"] += 1
            continue
        if k + 1 + SEDUTE >= len(cal) or cal[k + 1 + SEDUTE] > FINO:
            fuori["uscita oltre il 2024"] += 1
            continue
        gu = cal[k + 1 + SEDUTE]
        if gu not in d:
            dopo = [x for x in d if gi < x <= gu]
            if not dopo:
                fuori["senza prezzi"] += 1
                continue
            gu = max(dopo)
        if gu not in spy:
            fuori["senza prezzi"] += 1
            continue
        x = relativo(d, spy, cal[k - 1], gi)
        if x is not None:
            lettura[(r.lato, "prima")].append(x)
        for h in (1, 5, 20):
            y = relativo(d, spy, gi, cal[k + 1 + h]) if k + 1 + h < len(cal) else None
            if y is not None:
                lettura[(r.lato, h)].append(y)
        tutte.append(Operazione(r.simbolo, int(r.lato), gi, d[gi][1], d[gi][2], gu, d[gu][1], d[gu][2],
                                spy[gi][1], spy[gi][2], spy[gu][1], spy[gu][2]))
    ops = scegli_ingressi(tutte)
    giorni = [g for g in cal if DAL <= g <= FINO]
    serie = {"costi": conto(ops, giorni), "costi doppi": conto(ops, giorni, 2.0), "senza costi": conto(ops, giorni, costi=False)}
    gc = serie["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy_r = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P053_analisti", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P053_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte_s = carica_serie()
    nuova = tutte_s["P053_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte_s)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(serie["costi doppi"])
    da_sola = sr_c > sr(spy_r) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte = t_di(gc.to_numpy())
    t_senza = t_di(gc[[not (x.year == 2020 and x.month == 3) for x in gc.index]].to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(serie["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8 and t_senza >= 1.3
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1
    per_anno = ann["annuncio"].map(lambda g: g.year).value_counts().sort_index()

    def riga(x, h):
        v = np.array(lettura[(x, h)])
        return f"{v.mean():+.2%} (t {t_di(v):.2f})" if len(v) > 2 else "—"
    testo = ["# Prova 53 — risultati", "",
             f"Calcolato da `python -m stock.prove.p053` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P053_giudizi_degli_analisti.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte_s)} serie.", "",
             f"* La scelta delle notizie: {conta}. Annunci {len(ann)} (promozioni {int((ann['lato'] > 0).sum())}, bocciature "
             f"{int((ann['lato'] < 0).sum())}); per anno: " + ", ".join(f"{y} {n}" for y, n in per_anno.items())
             + f". Fuori: {fuori}. Operazioni possibili {len(tutte)}, prese {len(ops)}.",
             "* Il titolo meno lo SPY (da leggere) | dalla chiusura prima dell'annuncio all'ingresso | 1 seduta dopo | 5 | 20:",
             f"  promozioni {riga(1, 'prima')} | {riga(1, 1)} | {riga(1, 5)} | {riga(1, 20)}; bocciature {riga(-1, 'prima')} | "
             f"{riga(-1, 1)} | {riga(-1, 5)} | {riga(-1, 20)}.", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(serie['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(serie['costi doppi']):+.1%} | {tot(spy_r):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(serie['senza costi']):.2f}) | {sr(spy_r):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy_r):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(serie['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f}, senza marzo 2020 {t_senza:.2f} (soglia 1,3 "
             f"tutti e due)**; **miscela nuova più alta nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove (122 e 123)."]
    (QUI / "P053_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
