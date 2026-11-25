"""Prova 51 — le acquisizioni pagate in contanti: comprata l'azienda comprata alla chiusura del giorno di borsa dopo l'annuncio, tenuta
fino all'ultimo giorno di borsa del titolo, 365 giorni o la fine del 2024 (`P051_arbitraggio_acquisizioni.md`, regole scritte prima).

    python -m stock.prove.p051        # gira su GitHub (azioni-ricerca): notizie e prezzi di Alpaca nella memoria del lavoro

Le notizie non si stampano né si pubblicano (licenza): solo conteggi.
"""
from __future__ import annotations

import bisect
import math
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

import numpy as np
import pandas as pd

from stock.prove.p001 import CAPITALE, QUI, carica_serie, comprare_e_tenere, salva_serie
from stock.prove.p032 import campionamento, t_di
from stock.prove.p035 import commissione, dd, sr, tot
from stock.prove.p046 import TIPI, giorno_annuncio
from stock.simulatore import asticella
from stock.simulatore.finestre import finestre

DAL, FINO = date(2016, 1, 4), date(2024, 12, 31)
QUOTA, MASSIMO, GIORNI_MASSIMI, SLIT = 0.05, 20, 365, 2e-4
PREZZO_MINIMO, DOLLARI_MINIMI, SCARTO_MASSIMO = 5.0, 2e6, 0.50

PREZZO = re.compile(r"\$\s?(\d{1,4}(?:,\d{3})*(?:\.\d+)?)\s*(?:per share|/share|a share)", re.IGNORECASE)
CONTANTI = re.compile(r"\bcash\b", re.IGNORECASE)
MISTO = re.compile(r"stock and cash|cash and stock|in stock|shares of|exchange ratio", re.IGNORECASE)
ACCORDO = re.compile(r"to acquire|to be acquired|agreement to acquire|definitive agreement|agrees to sell", re.IGNORECASE)
VOCE = re.compile(r"proposal|proposes|propose|offer to acquire|unsolicited|considering|explore|exploring|talks|report|reportedly|"
                  r"rumor|nonbinding|non-binding|bid for", re.IGNORECASE)


# --- senza rete -------------------------------------------------------------------------------------------------------------------
def leggi(titolo: str) -> float | None:
    """Il prezzo offerto in contanti per azione se il titolo della notizia è un accordo d'acquisto in contanti, altrimenti None."""
    if not CONTANTI.search(titolo) or MISTO.search(titolo) or not ACCORDO.search(titolo) or VOCE.search(titolo):
        return None
    m = PREZZO.search(titolo)
    return float(m.group(1).replace(",", "")) if m else None


def bersaglio(simboli: list[str], offerta: float, chiusure_prima: dict[str, float | None]) -> str | None:
    """L'azienda comprata: l'unico simbolo con la chiusura di prima sotto il prezzo offerto e il prezzo offerto fino al doppio."""
    buoni = [s for s in simboli if (c := chiusure_prima.get(s)) and c > 0 and c < offerta <= 2 * c]
    return buoni[0] if len(buoni) == 1 else None


def uscita(giorno_in: date, giorni_titolo: list[date], calendario: list[date]) -> tuple[date, str]:
    """(giorno, perché): l'ultimo giorno di borsa del titolo, 365 giorni dopo l'ingresso (il primo giorno di borsa del titolo da lì) o la
    fine del periodo, il primo dei tre."""
    limite = giorno_in + timedelta(days=GIORNI_MASSIMI)
    ultimo = max(giorni_titolo)
    if ultimo < FINO and ultimo <= limite and ultimo < calendario[-1]:
        return ultimo, "sparito"
    k = bisect.bisect_left(giorni_titolo, limite)
    if k < len(giorni_titolo) and giorni_titolo[k] <= FINO:
        return giorni_titolo[k], "365 giorni"
    return max(g for g in giorni_titolo if g <= FINO), "fine del periodo"


@dataclass(frozen=True)
class Affare:
    simbolo: str
    annuncio: date
    giorno_in: date
    giorno_out: date
    perche: str
    scarto: float


def scegli(affari: list[Affare], massimo: int = MASSIMO) -> list[Affare]:
    """In ordine d'ingresso (a pari giorno alfabetico), al massimo `massimo` affari aperti insieme (si libera il giorno dopo l'uscita)."""
    aperti, out = [], []
    for a in sorted(affari, key=lambda x: (x.giorno_in, x.simbolo)):
        aperti = [x for x in aperti if x.giorno_out >= a.giorno_in]
        if len(aperti) >= massimo:
            continue
        aperti.append(a)
        out.append(a)
    return out


def conto(affari: list[Affare], prezzi: dict, giorni: list[date], fattore: float = 1.0, costi: bool = True) -> pd.Series:
    """I rendimenti di ogni giorno, con il valore di mercato di ogni giorno (le chiusure come scambiate per il fattore dei dividendi e
    dei frazionamenti). `prezzi[s]`: giorno → (apertura, chiusura, fattore). Ingresso e uscita all'asta di chiusura."""
    per_in: dict[date, list[Affare]] = {}
    for a in affari:
        per_in.setdefault(a.giorno_in, []).append(a)
    contanti, aperti, ieri, out = CAPITALE, [], CAPITALE, {}
    for g in giorni:
        valore_prima = contanti + sum(_valore(p, prezzi, g, ultimo=True) for p in aperti)
        for a in per_in.get(g, []):
            c, f = prezzi[a.simbolo][g][1], prezzi[a.simbolo][g][2]
            n = math.floor(QUOTA * valore_prima / c)
            if n <= 0:
                continue
            contanti -= n * c
            if costi:
                contanti -= fattore * (SLIT * n * c + commissione(n, c))
            aperti.append({"a": a, "n": n, "f_in": f, "ultimo": c * f / f})
        restano = []
        for p in aperti:
            if p["a"].giorno_out == g:
                c, f = prezzi[p["a"].simbolo][g][1], prezzi[p["a"].simbolo][g][2]
                incasso = p["n"] * c * f / p["f_in"]
                contanti += incasso
                if costi:
                    contanti -= fattore * (SLIT * incasso + commissione(p["n"], c))
            else:
                restano.append(p)
        aperti = restano
        v = contanti + sum(_valore(p, prezzi, g) for p in aperti)
        out[g] = v / ieri - 1
        ieri = v
    return pd.Series(out)


def _valore(p: dict, prezzi: dict, g: date, ultimo: bool = False) -> float:
    """Il valore di mercato di una posizione (con dividendi e frazionamenti); un giorno senza barra tiene l'ultimo valore."""
    d = prezzi[p["a"].simbolo].get(g)
    if d is not None and not ultimo:
        p["ultimo"] = d[1] * d[2] / p["f_in"]
    return p["n"] * p["ultimo"]


# --- con i prezzi ------------------------------------------------------------------------------------------------------------------
def titoli_delle_notizie() -> pd.DataFrame:
    """Solo il titolo delle notizie (non il riassunto), dall'archivio mensile: creata (UTC), simboli, titolo."""
    from stock.dati import notizie
    pezzi = []
    for a, m in notizie.mesi(2016, 2024):
        df = pd.read_csv(notizie._file(a, m), dtype=str, keep_default_na=False)
        pezzi.append(pd.DataFrame({"creata": pd.to_datetime(df["creata"], utc=True, format="ISO8601"),
                                   "simboli": df["simboli"].str.split(), "titolo": df["titolo"]}))
    return pd.concat(pezzi, ignore_index=True).sort_values("creata", kind="stable").reset_index(drop=True)


def main():
    from stock.dati import archivio, controlli, notizie
    from stock.prove.p027 import scarica
    from stock.prove.p042 import giorni_e_dollari
    if notizie.mancanti(2016, 2024):
        raise SystemExit(f"mancano {len(notizie.mancanti(2016, 2024))} mesi di notizie: prima `python -m stock.prove.p028b`")
    scarica(["SPY"])
    cal = sorted(d for d in controlli.date_ny(archivio.carica("SPY", "1Day_raw").index) if d <= FINO)
    nt = titoli_delle_notizie()
    conta = {"notizie": len(nt), "accordi in contanti letti": 0, "fuori periodo": 0, "senza bersaglio unico": 0, "doppioni": 0,
             "senza prezzi": 0, "filtri (5 dollari, 2 milioni)": 0, "scarto ≤ 0": 0, "scarto > 50%": 0}
    lette = []
    for r in nt.itertuples():
        x = leggi(r.titolo)
        if x is None:
            continue
        conta["accordi in contanti letti"] += 1
        g = giorno_annuncio(r.creata, cal)
        if g is None or not (DAL <= g <= FINO):
            conta["fuori periodo"] += 1
            continue
        lette.append((g, list(r.simboli), x))
    simboli = sorted({s for _, ss, _ in lette for s in ss})
    scarica(simboli, TIPI["raw"], TIPI["az"], TIPI["asof"])
    dati = {s: x for s in simboli if (x := giorni_e_dollari(s, TIPI["raw"], TIPI["az"])) is not None}
    prezzi = {s: x[0] for s, x in dati.items()}
    pos = {g: i for i, g in enumerate(cal)}
    visti, affari, scarti = set(), [], []
    for g, ss, offerta in lette:
        k = pos[g]
        if k < 1 or k + 1 >= len(cal):
            conta["fuori periodo"] += 1
            continue
        prima, gi = cal[k - 1], cal[k + 1]
        chiusure = {s: (prezzi[s][prima][1] if s in prezzi and prima in prezzi[s] else None) for s in ss}
        s = bersaglio(ss, offerta, chiusure)
        if s is None:
            conta["senza bersaglio unico"] += 1
            continue
        if s in visti:
            conta["doppioni"] += 1
            continue
        visti.add(s)
        if gi not in prezzi[s]:
            conta["senza prezzi"] += 1
            continue
        c_in = prezzi[s][gi][1]
        dollari_s = dati[s][2]
        mediana = float(dollari_s[dollari_s.index < gi].iloc[-20:].median()) if (dollari_s.index < gi).sum() >= 20 else 0.0
        if c_in < PREZZO_MINIMO or mediana < DOLLARI_MINIMI:
            conta["filtri (5 dollari, 2 milioni)"] += 1
            continue
        sc = offerta / c_in - 1
        if sc <= 0:
            conta["scarto ≤ 0"] += 1
            continue
        if sc > SCARTO_MASSIMO:
            conta["scarto > 50%"] += 1
            continue
        giorni_titolo = sorted(x for x in prezzi[s] if x >= gi)
        go, perche = uscita(gi, giorni_titolo, cal)
        if go <= gi:
            conta["senza prezzi"] += 1
            continue
        affari.append(Affare(s, g, gi, go, perche, sc))
        scarti.append(sc)
    scelti = scegli(affari)
    giorni = [g for g in cal if DAL <= g <= FINO]
    serie = {"costi": conto(scelti, prezzi, giorni), "costi doppi": conto(scelti, prezzi, giorni, 2.0),
             "senza costi": conto(scelti, prezzi, giorni, costi=False)}
    gc = serie["costi"]
    a, b = gc.index.min(), gc.index.max()
    spy = comprare_e_tenere("SPY", a, b)
    miscela = carica_serie()["P025_miscela"]
    salva_serie("P051_acquisizioni", gc)
    comuni = miscela.index.intersection(gc.index)
    salva_serie("P051_miscela", 0.75 * miscela.loc[comuni] + 0.25 * gc.loc[comuni])
    tutte = carica_serie()
    nuova = tutte["P051_miscela"]
    ast = asticella.sharpe_corretto(gc, tutte)
    q = [float((1 + gc[(gc.index >= x) & (gc.index < y)]).prod() - 1)
         for x, y in (f["prova"] for f in finestre(date(2016, 1, 1), date(2025, 1, 1), chiuso_dal=date(2025, 1, 1))) if x >= a]
    quota_t = sum(x > 0 for x in q) / len(q)
    sr_c, sr_2 = sr(gc), sr(serie["costi doppi"])
    da_sola = sr_c > sr(spy) and ast["sharpe_corretto"] >= 0.95 and sr_2 > 0 and quota_t >= 0.6
    corr = float(np.corrcoef(miscela.loc[comuni], gc.loc[comuni])[0, 1])
    spy_c = comprare_e_tenere("SPY", comuni.min(), comuni.max())
    t_parte = t_di(gc.to_numpy())
    t_senza = t_di(gc[[not (x.year == 2020 and x.month == 3) for x in gc.index]].to_numpy())
    vinte = campionamento(miscela.loc[comuni], gc.loc[comuni])
    entra = sr(gc.loc[comuni]) > 0 and sr(serie["costi doppi"].reindex(comuni).dropna()) > 0 and corr < 0.3 \
        and sr(nuova) > sr(miscela.loc[comuni]) and sr(nuova) > sr(spy_c) and t_parte >= 1.3 and vinte >= 0.8 and t_senza >= 1.3

    # da leggere
    def resa(x: Affare) -> float:
        p = prezzi[x.simbolo]
        return p[x.giorno_out][1] * p[x.giorno_out][2] / (p[x.giorno_in][1] * p[x.giorno_in][2]) - 1
    chiusi = [resa(x) for x in scelti if x.perche == "sparito"]
    altri = [resa(x) for x in scelti if x.perche != "sparito"]
    tenuta = [(x.giorno_out - x.giorno_in).days for x in scelti]
    per_anno = pd.Series([x.giorno_in.year for x in scelti]).value_counts().sort_index()
    mesi_g = (1 + gc).groupby(pd.Index([(x.year, x.month) for x in gc.index])).prod() - 1
    mesi_s = (1 + spy).groupby(pd.Index([(x.year, x.month) for x in spy.index])).prod() - 1
    giu = [m for m in mesi_s.index if mesi_s[m] < 0 and m in mesi_g.index]
    corr_giu = float(np.corrcoef([mesi_g[m] for m in giu], [mesi_s[m] for m in giu])[0, 1]) if len(giu) > 2 else float("nan")
    marzo = float(mesi_g.get((2020, 3), float("nan")))
    anni = (1 + gc).groupby(pd.Index([x.year for x in gc.index])).prod() - 1

    def riga(nome, x):
        x = np.asarray(x)
        return f"{nome}: {len(x)}, media {x.mean():+.2%} (t {t_di(x):.2f})" if len(x) > 2 else f"{nome}: {len(x)}"
    testo = ["# Prova 51 — risultati", "",
             f"Calcolato da `python -m stock.prove.p051` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con le regole di "
             f"`P051_arbitraggio_acquisizioni.md` (committate prima). Dal {a} al {b}. Nel conto dell'asticella: {len(tutte)} serie.", "",
             f"* La scelta: {conta}. Affari possibili {len(affari)}, presi {len(scelti)} (fuori per i posti {len(affari) - len(scelti)}); "
             f"per anno: {', '.join(f'{y} {n}' for y, n in per_anno.items())}.",
             f"* Scarto medio all'ingresso {np.mean(scarti):.2%} (mediana {np.median(scarti):.2%}); giorni medi di tenuta "
             f"{np.mean(tenuta):.0f}. " + riga("Affari chiusi (titolo sparito entro 365 giorni)", chiusi) + "; "
             + riga("gli altri", altri) + ".",
             f"* Nei mesi con lo SPY in perdita ({len(giu)}): correlazione mensile con lo SPY {corr_giu:+.2f}. Marzo 2020 da solo: "
             f"{marzo:+.2%}.", "",
             "| | La strategia | Tenere lo SPY |", "|---|---|---|",
             f"| Guadagno totale senza costi / con i costi / costi doppi | {tot(serie['senza costi']):+.1%} / {tot(gc):+.1%} / "
             f"{tot(serie['costi doppi']):+.1%} | {tot(spy):+.1%} |",
             f"| **1.** Sharpe annuo con i costi | **{sr_c:.2f}** (senza costi {sr(serie['senza costi']):.2f}) | {sr(spy):.2f} |",
             f"| **2.** Sharpe corretto (soglia 0,95) | {ast['sharpe_corretto']:.2f} (gruppi {ast['gruppi']}, t {ast['t_sharpe']:.2f}) | — |",
             f"| **3.** Sharpe con i costi doppi (> 0) | {sr_2:.2f} | — |",
             f"| **4.** Trimestri in guadagno (60%) | {sum(x > 0 for x in q)} su {len(q)} ({quota_t:.0%}) | — |",
             f"| Perdita massima dal picco | {dd(gc):.1%} | {dd(spy):.1%} |",
             f"| Anno per anno | {' '.join(f'{y}: {x:+.1%}' for y, x in anni.items())} | — |",
             f"| **Esito da sola** | **{'passa la ricerca' if da_sola else 'bocciata'}** | |", "",
             f"**Per entrare nella miscela** (giorni in comune dal {comuni.min()} al {comuni.max()}): Sharpe della parte "
             f"{sr(gc.loc[comuni]):.2f}, con i costi doppi {sr(serie['costi doppi'].reindex(comuni).dropna()):.2f}; correlazione con la "
             f"miscela {corr:.2f} (soglia 0,3); miscela nuova {sr(nuova):.2f} contro {sr(miscela.loc[comuni]):.2f} della miscela e "
             f"{sr(spy_c):.2f} del tenere lo SPY; **t dello Sharpe della parte {t_parte:.2f}, senza marzo 2020 {t_senza:.2f} (soglia 1,3 "
             f"tutti e due)**; **miscela nuova più alta nel {vinte:.0%} dei campionamenti (soglia 80%)**. **Esito: "
             f"{'entra nella miscela (prima il revisore)' if entra else 'non entra'}**", "",
             "Nel conto: 2 prove (118 e 119)."]
    (QUI / "P051_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[4:]))


if __name__ == "__main__":
    main()
