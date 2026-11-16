"""Controllo dopo la prova 36: quanto costa davvero comprare fuori seduta (metodo in `P036b_costo_fuori_seduta.md`, scritto prima).

    python -m stock.prove.p036b           # servono le chiavi di Alpaca: gira su GitHub (azioni-ricerca)

**Non è una prova** (non entra nel conto): rifà le operazioni della prova 36 con gli stessi dati già scaricati, ne estrae un campione e
per ognuna guarda la quotazione al momento dell'ordine, dove sta l'apertura della barra rispetto alle quotazioni, e quanto hanno pagato
davvero le operazioni di mercato nel minuto dell'ingresso. Scrive `P036b_risultati.md`. Le quotazioni e le operazioni restano nella
memoria del lavoro, mai nel repository.
"""
from __future__ import annotations

import bisect
import math
import random
from datetime import UTC, date, datetime

import numpy as np
import pandas as pd

from stock.dati import alpaca
from stock.dati.scarto import quotazioni_valide
from stock.prove import p036
from stock.prove.p001 import QUI
from stock.prove.p027 import aspetta_fuori_dagli_ordini
from stock.prove.p032 import t_di
from stock.prove.p035 import commissione

NY = p036.NY
FUORI, DENTRO = 400, 200
SEME_FUORI, SEME_DENTRO = 3602, 3601
VALORE = 10_000.0
# la prova 36 (`P036_risultati.md`): mediana dello scarto misurato in punti base, in seduta e fuori seduta
MEDIANE_P036 = {"in seduta": 7.6e-4, "fuori seduta": 103.6e-4}
ORE = [((4, 0), (6, 59), "4:00-6:59"), ((7, 0), (9, 29), "7:00-9:29"), ((9, 30), (15, 59), "in seduta"),
       ((16, 0), (16, 59), "16:00-16:59"), ((17, 0), (17, 59), "17:00-17:59"), ((18, 0), (19, 59), "18:00-19:59")]


# --- le misure (senza rete) --------------------------------------------------------------------------------------------------------
def quotazione_prima(q: pd.DataFrame, t: pd.Timestamp) -> pd.Series | None:
    """L'ultima quotazione valida strettamente prima di `t`."""
    q = quotazioni_valide(q)
    q = q[q.index < t]
    return None if q.empty else q.iloc[-1]


def posizione(apertura: float, bid: float, ask: float) -> float:
    """(apertura − mezzo) / (vendita − mezzo): 1 al prezzo di chi vende, 0 al mezzo, −1 al prezzo di chi compra."""
    mezzo = (bid + ask) / 2
    return (apertura - mezzo) / (ask - mezzo) if ask > mezzo else float("nan")


def scarto_effettivo(scambi: pd.DataFrame, q: pd.DataFrame) -> float:
    """La mediana, sulle operazioni di mercato, della distanza dal prezzo di mezzo della quotazione valida in quel momento, divisa per il
    mezzo. NaN se non ci sono operazioni con una quotazione prima."""
    q = quotazioni_valide(q)
    if scambi.empty or q.empty:
        return float("nan")
    m = ((q["bid"] + q["ask"]) / 2).rename("mezzo").sort_index()
    s = scambi.sort_index()
    # le ore di Alpaca possono arrivare con precisioni diverse (microsecondi o nanosecondi): si portano alla stessa
    m.index = pd.DatetimeIndex(m.index).as_unit("ns").rename("t")
    s.index = pd.DatetimeIndex(s.index).as_unit("ns").rename("t")
    x = pd.merge_asof(s.reset_index(), m.reset_index(), on="t", direction="backward").dropna(subset=["mezzo"])
    if x.empty:
        return float("nan")
    return float(((x["prezzo"] - x["mezzo"]).abs() / x["mezzo"]).median())


def netto(lordo: float, costo: float, prezzo: float) -> float:
    """Il guadagno di un ingresso da 10'000 dollari dopo il costo dato, lo slittamento 2 + 2 punti base e le commissioni."""
    n = max(1, math.floor(VALORE / prezzo))
    comm = (commissione(n, prezzo) + commissione(n, prezzo * (1 + lordo))) / (n * prezzo)
    return lordo - costo - p036.SLIT_IN - p036.SLIT_OUT * (1 + lordo) - comm


def ora_di(t: pd.Timestamp) -> str:
    x = t.tz_convert(NY)
    m = x.hour * 60 + x.minute
    for (h0, m0), (h1, m1), nome in ORE:
        if h0 * 60 + m0 <= m <= h1 * 60 + m1:
            return nome
    return "altro"


# --- le operazioni della prova 36 (stessi dati, stesse regole) ----------------------------------------------------------------------
def operazioni_p036() -> list[p036.Operazione]:
    from stock.prove.p027 import scarica
    ev = pd.read_csv(QUI / "dati" / "P036_depositi.csv.gz", dtype={"simbolo": str}, keep_default_na=False, na_values=[""])
    ev["accettato"] = pd.to_datetime(ev["accettato"], utc=True)
    ev["giorno_op"] = pd.to_datetime(ev["giorno_op"], errors="coerce").dt.date
    g_ny = ev["accettato"].dt.tz_convert(NY).dt.date
    ev = ev[(g_ny >= p036.DAL) & (g_ny <= p036.FINO)].reset_index(drop=True)
    simboli = sorted(set(ev["simbolo"]))
    scarica(simboli + ["SPY"], p036.TIPI["raw"], p036.TIPI["az"], p036.TIPI["asof"])
    prezzi = {s: x for s in simboli if (x := p036.giorni_del_titolo(s)) is not None}
    spy = p036.giorni_del_titolo("SPY")
    calendario = sorted(g for g in spy if g >= date(2015, 12, 1))

    def pulito(s: str, g, p: float) -> bool:
        d = prezzi.get(s)
        if d is None or pd.isna(g) or not p > 0:
            return False
        k = bisect.bisect_right(calendario, g) - 1
        while k >= 0 and calendario[k] not in d:
            k -= 1
        return k >= 0 and abs(p / d[calendario[k]][1] - 1) <= p036.SCARTO_PREZZO
    ev = ev[[pulito(s, g, p) for s, g, p in zip(ev["simbolo"], ev["giorno_op"], ev["prezzo_op"])]].reset_index(drop=True)
    sg = p036.segnali(ev, calendario)
    tutte, _ = p036.operazioni(sg, p036.RITARDO, calendario, prezzi, spy)
    return p036.scegli_ingressi(tutte)


def misura(op: p036.Operazione) -> dict | None:
    t = op.ora_ingresso
    aspetta_fuori_dagli_ordini()
    try:
        q = alpaca.quotazioni(op.simbolo, (t - pd.Timedelta(seconds=30)).to_pydatetime(), (t + pd.Timedelta(seconds=60)).to_pydatetime())
        prima = quotazione_prima(q, t)
        if prima is None:
            q0 = alpaca.quotazioni(op.simbolo, (t - pd.Timedelta(minutes=5)).to_pydatetime(), (t - pd.Timedelta(seconds=30)).to_pydatetime())
            prima = quotazione_prima(q0, t)
            q = pd.concat([q0, q]).sort_index()
        if prima is None:
            return None
        s = alpaca.scambi(op.simbolo, t.to_pydatetime(), (t + pd.Timedelta(seconds=60)).to_pydatetime())
    except alpaca.ErroreAlpaca:
        return None
    bid, ask = float(prima["bid"]), float(prima["ask"])
    mezzo = (bid + ask) / 2
    lordo_mezzo = (1 + op.lordo) * op.prezzo_in / mezzo - 1
    eff = scarto_effettivo(s, q)
    chiave = "in seduta" if p036.fascia(t) == "in seduta" else "fuori seduta"
    return {"fascia": p036.fascia(t), "ora": ora_di(t), "quotato": (ask - mezzo) / mezzo, "effettivo": eff,
            "posizione": posizione(op.prezzo_in, bid, ask), "scambi": len(s),
            "A": netto(lordo_mezzo, (ask - mezzo) / mezzo, mezzo),
            "B": netto(lordo_mezzo, eff, mezzo) if np.isfinite(eff) else float("nan"),
            "C": netto(op.lordo, MEDIANE_P036[chiave] / 2, op.prezzo_in),
            "lordo_mezzo": lordo_mezzo, "lordo_apertura": op.lordo}


def _riga(nome: str, d: pd.DataFrame) -> str:
    if d.empty:
        return f"| {nome} | 0 | — | — | — | — | — | — | — |"
    pb = lambda x: f"{np.nanmedian(x) * 1e4:.1f}"  # noqa: E731
    def media(c):
        x = d[c].dropna().to_numpy()
        return f"{x.mean():+.3%} (t {t_di(x):.2f}, n {len(x)})" if len(x) > 2 else "—"
    return (f"| {nome} | {len(d)} | {pb(d['quotato'])} | {pb(d['effettivo'])} | {np.nanmedian(d['posizione']):+.2f} "
            f"({(d['posizione'] >= 0.8).mean():.0%}) | {d['lordo_mezzo'].mean():+.3%} | {media('A')} | {media('B')} | {media('C')} |")


def main():
    ops = operazioni_p036()
    fuori = [o for o in ops if p036.fascia(o.ora_ingresso) != "in seduta"]
    dentro = [o for o in ops if p036.fascia(o.ora_ingresso) == "in seduta"]
    campione = random.Random(SEME_FUORI).sample(fuori, min(FUORI, len(fuori))) + \
        random.Random(SEME_DENTRO).sample(dentro, min(DENTRO, len(dentro)))
    print(f"operazioni della prova 36 {len(ops)} (fuori seduta {len(fuori)}, in seduta {len(dentro)}); campione {len(campione)}", flush=True)
    righe, mancano = [], 0
    for k, op in enumerate(campione):
        r = misura(op)
        if r is None:
            mancano += 1
        else:
            righe.append(r)
        if k % 100 == 99:
            print(f"misurati {k + 1}", flush=True)
    d = pd.DataFrame(righe)
    fu = d[d["fascia"] != "in seduta"]
    tab = ["| Gruppo | Ingressi | Metà dello scarto quotato, mediana (punti base) | Scarto effettivo, mediana (punti base) | "
           "Dove apre la barra, mediana (quota al prezzo di chi vende) | Guadagno dal mezzo prima dei costi | Netto A (quotato) | "
           "Netto B (effettivo) | Netto C (come la prova 36) |", "|---|---|---|---|---|---|---|---|---|",
           _riga("fuori seduta, tutti", fu), *(_riga(k, d[d["fascia"] == k]) for k in ("dopo la chiusura", "prima dell'apertura", "in seduta")),
           *(_riga(f"ora {nome}", d[d["ora"] == nome]) for _, _, nome in ORE if nome != "in seduta")]
    testo = ["# Controllo dopo la prova 36 — il costo vero degli acquisti fuori seduta", "",
             f"Calcolato da `python -m stock.prove.p036b` il {datetime.now(UTC):%Y-%m-%d %H:%M} UTC con il metodo di "
             "`P036b_costo_fuori_seduta.md` (scritto prima). **Non è una prova**: la prova 36 resta bocciata. Campione: "
             f"{min(FUORI, len(fuori))} ingressi fuori seduta e {min(DENTRO, len(dentro))} in seduta delle {len(ops)} operazioni della "
             f"prova 36; senza quotazione prima dell'ingresso (o rifiutati da Alpaca) {mancano}; senza operazioni di mercato nel minuto "
             f"dell'ingresso {int(d['effettivo'].isna().sum())}.", "",
             "La «metà dello scarto quotato» è il costo di chi compra subito al prezzo di chi vende; lo «scarto effettivo» è quanto hanno "
             "pagato davvero, rispetto al mezzo, le operazioni di mercato di quel minuto. «Dove apre la barra»: 1 al prezzo di chi vende, 0 "
             "al mezzo, −1 al prezzo di chi compra; fra parentesi la quota di barre che aprono da 0,8 in su. I netti tolgono anche lo "
             "slittamento 2 + 2 punti base e le commissioni su 10'000 dollari.", "", *tab]
    (QUI / "P036b_risultati.md").write_text("\n".join(testo) + "\n")
    print("\n".join(testo[-len(tab):]))


if __name__ == "__main__":
    main()
