"""Prova 46 — le dimissioni del capo: venduto allo scoperto il titolo alla chiusura del giorno dopo l'annuncio, comprato lo stesso
valore di SPY, per 20 sedute (`P046_dimissioni_del_capo.md`, regole scritte prima; idea I54 del proprietario).

    python -m stock.prove.p046        # gira su GitHub (azioni-ricerca): notizie e prezzi di Alpaca nella memoria del lavoro

Le notizie non si stampano né si pubblicano (licenza): solo conteggi.
"""
from __future__ import annotations

import bisect
import math
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from stock.prove.p001 import CAPITALE, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import commissione, dd, sr, tot
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

NY = ZoneInfo("America/New_York")
DAL, ULTIMO, FINO = date(2016, 1, 4), date(2024, 11, 30), date(2024, 12, 31)
SEDUTE, QUOTA, MASSIMO, GIORNI_DOPPIONE, SIMBOLI_MASSIMI = 20, 0.10, 10, 60, 3
SLIT, PRESTITO = 2e-4, 0.03
TIPI = {"raw": "1Day_allora", "az": "azioni_allora", "asof": "-"}

CAPO = re.compile(r"\b(ceo|chief executive)\b", re.IGNORECASE)
USCITA = re.compile(r"\b(resign|resigns|resigned|resignation|steps down|step down|stepped down|stepping down|ousted|ousts|fired|"
                    r"terminated|departs|departure|departing|exits|exiting|leaves|leaving|to leave)\b", re.IGNORECASE)
ESCLUSI = re.compile(r"\b(retire|retires|retiring|retirement|former ceo|ex-ceo)\b", re.IGNORECASE)
SUBITO = re.compile(r"effective immediately", re.IGNORECASE)


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def parola(testo: str) -> str | None:
    """La parola d'uscita trovata se il testo parla dell'uscita di un capo (e non di un pensionamento o di un ex capo), altrimenti None."""
    if not CAPO.search(testo) or ESCLUSI.search(testo):
        return None
    m = USCITA.search(testo)
    return m.group(1).lower() if m else None


def giorno_annuncio(t: pd.Timestamp, calendario: list[date]) -> date | None:
    """Il giorno di borsa dell'annuncio: lo stesso giorno se esce prima delle 16:00 di New York in un giorno di borsa, altrimenti il primo
    giorno di borsa dopo."""
    ny = t.tz_convert(NY)
    g = ny.date()
    k = bisect.bisect_left(calendario, g)
    if k < len(calendario) and calendario[k] == g and ny.time() < time(16, 0):
        return g
    k = bisect.bisect_right(calendario, g)
    return calendario[k] if k < len(calendario) else None


def scegli_notizie(notizie: pd.DataFrame, membri_al, calendario: list[date]) -> tuple[pd.DataFrame, dict]:
    """Gli annunci: notizie scelte con le parole, al massimo 3 simboli ed esattamente un membro dell'S&P 500; la prima per azienda in
    60 giorni. Colonne: simbolo, creata, annuncio, parola, subito."""
    conta = {"notizie": len(notizie), "con le parole": 0, "più di 3 simboli": 0, "nessun membro": 0, "due o più membri": 0,
             "doppioni (60 giorni)": 0}
    righe, ultimo = [], {}
    for r in notizie.itertuples():
        w = parola(r.testo)
        if w is None:
            continue
        conta["con le parole"] += 1
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
        s = dentro[0]
        if s in ultimo and (g - ultimo[s]).days <= GIORNI_DOPPIONE:
            conta["doppioni (60 giorni)"] += 1
            continue
        ultimo[s] = g
        righe.append({"simbolo": s, "creata": r.creata, "annuncio": g, "parola": w, "subito": bool(SUBITO.search(r.testo))})
    return pd.DataFrame(righe, columns=["simbolo", "creata", "annuncio", "parola", "subito"]), conta


@dataclass(frozen=True)
class Operazione:
    simbolo: str
    annuncio: date
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
    subito: bool = False

    @property
    def titolo(self) -> float:
        return self.p_out * self.f_out / (self.p_in * self.f_in) - 1

    @property
    def spy(self) -> float:
        return self.spy_out * self.spy_f_out / (self.spy_in * self.spy_f_in) - 1


def scegli_ingressi(ops: list[Operazione], massimo: int = MASSIMO) -> list[Operazione]:
    """In ordine d'ingresso (a pari giorno alfabetico): al massimo `massimo` posizioni aperte; una posizione aperta sullo stesso titolo
    blocca (le posizioni chiudono alla chiusura del giorno d'uscita, gli ingressi sono alla chiusura: si libera il giorno dopo)."""
    aperte, out = [], []
    for op in sorted(ops, key=lambda o: (o.giorno_in, o.simbolo)):
        aperte = [a for a in aperte if a.giorno_out >= op.giorno_in]          # ancora aperte il giorno dell'ingresso
        if len(aperte) >= massimo or any(a.simbolo == op.simbolo for a in aperte):
            continue
        aperte.append(op)
        out.append(op)
    return out


def conto(ops: list[Operazione], giorni: list[date], fattore: float = 1.0, costi: bool = True) -> pd.Series:
    """I rendimenti di ogni giorno: il 10% del conto venduto nel titolo e lo stesso valore comprato in SPY alla chiusura dell'ingresso;
    il guadagno contato il giorno dell'uscita. Slittamento su quattro ordini, commissioni, prestito del titolo."""
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
            venduto, comprato = n * op.p_in, m * op.spy_in
            utile = -venduto * op.titolo + comprato * op.spy
            if costi:
                c = SLIT * (venduto + venduto * (1 + op.titolo) + comprato + comprato * (1 + op.spy))
                c += commissione(n, op.p_in) + commissione(n, op.p_in * (1 + op.titolo))
                c += commissione(m, op.spy_in) + commissione(m, op.spy_in * (1 + op.spy))
                c += venduto * PRESTITO * (op.giorno_out - op.giorno_in).days / 365
                utile -= fattore * c
            da_contare[op.giorno_out] = da_contare.get(op.giorno_out, 0.0) + utile
        u = da_contare.pop(g, 0.0)
        out[g] = u / inizio
        v += u
    return pd.Series(out)


def relativo(d: dict, spy: dict, g0: date, g1: date) -> float | None:
    """Il titolo meno lo SPY dalla chiusura di g0 alla chiusura di g1 (con dividendi e frazionamenti)."""
    if g0 not in d or g1 not in d or g0 not in spy or g1 not in spy:
        return None
    return d[g1][1] * d[g1][2] / (d[g0][1] * d[g0][2]) - spy[g1][1] * spy[g1][2] / (spy[g0][1] * spy[g0][2])


# --- con i prezzi ------------------------------------------------------------------------------------------------------------------
def main():
    from stock.dati import archivio, controlli, notizie
    from stock.prove.p027 import scarica
    from stock.prove.p028 import decisioni
    from stock.prove.p034 import membri_al
    from stock.prove.p042 import giorni_e_dollari
    if notizie.mancanti(2016, 2024):
        raise SystemExit(f"mancano {len(notizie.mancanti(2016, 2024))} mesi di notizie: prima `python -m stock.prove.p028b`")
    scarica(["SPY"])
    spy_b = archivio.carica("SPY", "1Day_raw")
    cal = sorted(d for d in controlli.date_ny(spy_b.index) if d <= FINO)
    fini, membri = decisioni()
    ann, conta = scegli_notizie(notizie.carica(2016, 2024), lambda g: membri_al(g, fini, membri), cal)
    simboli = sorted(set(ann["simbolo"]))
    scarica(simboli, TIPI["raw"], TIPI["az"], TIPI["asof"])
    prezzi = {s: x[0] for s in simboli if (x := giorni_e_dollari(s, TIPI["raw"], TIPI["az"])) is not None}
    spy = giorni_e_dollari("SPY", "1Day_raw", "azioni")[0]
    pos = {g: i for i, g in enumerate(cal)}
    tutte, fuori, orizzonti, prima = [], {"senza prezzi": 0, "uscita oltre il 2024": 0}, {1: [], 5: [], 10: [], 20: []}, []
    for r in ann.itertuples():
        d = prezzi.get(r.simbolo)
        k = pos.get(r.annuncio)
        if d is None or k is None or k + 1 >= len(cal):
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
        for h in orizzonti:
            x = relativo(d, spy, gi, cal[k + 1 + h]) if k + 1 + h < len(cal) else None
            if x is not None:
                orizzonti[h].append(x)
        g_prima = cal[k - 1] if k >= 1 else None        # l'ultima chiusura prima della notizia è sempre quella prima del giorno d'annuncio
        x = relativo(d, spy, g_prima, gi) if g_prima else None
        if x is not None:
            prima.append(x)
        tutte.append(Operazione(r.simbolo, r.annuncio, gi, d[gi][1], d[gi][2], gu, d[gu][1], d[gu][2],
                                spy[gi][1], spy[gi][2], spy[gu][1], spy[gu][2], bool(r.subito)))
    ops = scegli_ingressi(tutte)
    giorni = [g for g in cal if DAL <= g <= FINO]
    serie = {"costi": conto(ops, giorni), "costi doppi": conto(ops, giorni, 2.0), "senza costi": conto(ops, giorni, costi=False)}
    gc = serie["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy_r = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P046_dimissioni", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P046_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte_s = carica_serie()
    nuova = tutte_s["P046_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte_s)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(serie["costi doppi"])
    da_sola = sr_c > sr(spy_r) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte = t_di(gc.to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(serie["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1
    venduto = np.array([-(o.titolo - o.spy) for o in tutte])               # guadagno della vendita allo scoperto coperta, prima dei costi
    senza_max = np.delete(venduto, np.argmax(venduto)) if len(venduto) else venduto
    subito = np.array([-(o.titolo - o.spy) for o in tutte if o.subito])

    def riga(nome, x):
        x = np.array(x)
        return (f"{nome}: {len(x)} casi, media **{x.mean():+.2%}**, mediana {np.median(x):+.2%}, t {t_di(x):.2f}, in calo rispetto allo "
                f"SPY {(x < 0).mean():.0%}") if len(x) else f"{nome}: nessun caso"
    per_anno = ann["annuncio"].map(lambda g: g.year).value_counts().sort_index()
    per_parola = ann["parola"].value_counts()
    testo = ["# Prova 46 — risultati", "",
             f"Calcolato da `python -m stock.prove.p046` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P046_dimissioni_del_capo.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte_s)} serie.", "",
             f"* La scelta delle notizie: {conta}. Annunci {len(ann)}; per anno: " + ", ".join(f"{y} {n}" for y, n in per_anno.items())
             + "; per parola: " + ", ".join(f"{w} {n}" for w, n in per_parola.items()) + f". Fuori: {fuori}. Operazioni possibili "
             f"{len(tutte)}, fatte {len(ops)} (le altre saltate per i 10 posti o per una posizione aperta sullo stesso titolo).",
             "* **La risposta alla domanda** (titolo meno SPY, prima dei costi, dalla chiusura del giorno dopo l'annuncio):",
             *[f"  * {riga(f'a {h} sedute', x)}" for h, x in orizzonti.items()],
             f"  * {riga('già successo, dalla chiusura prima dell annuncio all ingresso', prima)}",
             f"* La vendita allo scoperto coperta, prima dei costi, su tutti i casi: media {venduto.mean():+.2%} (t {t_di(venduto):.2f}); "
             f"senza il caso migliore {senza_max.mean():+.2%}; con «effective immediately» ({len(subito)} casi) "
             f"{subito.mean() if len(subito) else float('nan'):+.2%}.", "",
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
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f} (soglia 1,3)**; **miscela nuova più alta "
             f"nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove."]
    (QUI / "P046_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
