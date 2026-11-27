"""Il simulatore a più titoli (un solo conto, più azioni), sulle barre al giorno.

Le regole sono quelle di `motore.py` (decisione alla chiusura, esecuzione nella barra dopo, limite
solo se il prezzo passa oltre, stop al tocco, dividendi e frazionamenti all'apertura del giorno di
stacco), più queste:

* Il calendario è l'unione dei giorni di tutti i titoli. Un ordine per un titolo che il giorno dopo
  non ha la barra (sospeso, tolto dal listino) **non si esegue** e viene contato in `senza_barra`.
* Nello stesso giorno: prima gli stop, poi le vendite, poi gli acquisti (le vendite liberano i
  contanti), poi i limiti.
* Il valore del conto usa per ogni titolo l'ultima chiusura nota. Un titolo che sparisce dal listino
  con azioni in mano resta valutato all'ultima chiusura finché non si vende: la strategia deve uscire
  (e se non c'è più la barra, non può: lo dice `bloccati`).
* La leva si controlla sul valore lordo di tutte le posizioni dopo l'esecuzione.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from stock.simulatore.costi import Costi
from stock.simulatore.motore import Ordine, _esecuzione

NY = "America/New_York"


@dataclass
class StatoConto:
    contanti: float
    azioni: dict[str, float] = field(default_factory=dict)
    ultimo_prezzo: dict[str, float] = field(default_factory=dict)

    def valore(self) -> float:
        return self.contanti + sum(q * self.ultimo_prezzo.get(s, 0.0) for s, q in self.azioni.items())

    def lordo(self) -> float:
        return sum(abs(q) * self.ultimo_prezzo.get(s, 0.0) for s, q in self.azioni.items())


@dataclass
class RisultatoConto:
    valore: pd.Series
    esecuzioni: pd.DataFrame
    rifiutati: int
    senza_barra: int
    commissioni: float
    costo_scarto: float
    dividendi: float
    bloccati: list = field(default_factory=list)
    liquidati: list = field(default_factory=list)      # titoli chiusi all'ultimo prezzo perché spariti dal listino
    uscite_rimandate: int = 0                           # uscite a mercato senza la barra del giorno, riprovate alla prima barra


class Storia:
    """Le barre di ogni titolo fino al giorno della decisione compreso, mai oltre."""

    def __init__(self, barre: dict[str, pd.DataFrame], giorni: list):
        self._barre = barre
        self._fine = {s: np.searchsorted(np.array(df.index.date if hasattr(df.index, "date") else df.index), giorni,
                                         side="right") for s, df in barre.items()}
        self.i = -1

    def __call__(self, simbolo: str) -> pd.DataFrame | None:
        df = self._barre.get(simbolo)
        if df is None:
            return None
        return df.iloc[: self._fine[simbolo][self.i]]

    def simboli(self) -> list[str]:
        return list(self._barre)


StrategiaConto = Callable[[object, Storia, StatoConto], list]


def _giorni(df: pd.DataFrame) -> np.ndarray:
    idx = df.index
    if isinstance(idx, pd.DatetimeIndex) and idx.tz is not None:
        return np.array(idx.tz_convert(NY).date)
    return np.array(pd.DatetimeIndex(idx).date)


def simula_conto(barre: dict[str, pd.DataFrame], strategia: StrategiaConto, costi: Costi | dict[str, Costi],
                 capitale: float = 100_000.0, leva_massima: float = 1.0, frazionarie: bool = False,
                 liquida_dopo: int | None = None) -> RisultatoConto:
    """`barre`: per ogni simbolo le barre al giorno (open, high, low, close; facoltative dividendo,
    frazionamento) con indice di tempo. `strategia(giorno, storia, stato)` restituisce una lista di
    coppie (simbolo, Ordine) per il giorno di borsa dopo. `liquida_dopo`: se un titolo in mano resta senza barra per quel numero
    di giorni di borsa di fila (uscito dal listino, comprato, simbolo cambiato), la posizione si chiude all'ultima chiusura, senza
    costi, e si conta in `liquidati`; senza, resta in mano all'ultimo prezzo (`bloccati`).

    Un'uscita a mercato (un ordine che riduce una posizione aperta) in un giorno senza la barra del titolo non si perde: si riprova
    alla prima barra, solo per ridurre, finché la strategia non manda un altro ordine per quel titolo (`uscite_rimandate`; audit del
    27 novembre 2026: le strategie a evento mandano l'uscita una volta sola, e la posizione restava aperta per sempre)."""
    giorni_per = {s: _giorni(df) for s, df in barre.items()}
    tutti = sorted(set().union(*[set(g) for g in giorni_per.values()]))
    riga = {s: {d: i for i, d in enumerate(g)} for s, g in giorni_per.items()}
    col = {s: {c: (df[c].to_numpy(float) if c in df else None) for c in
               ("open", "high", "low", "close", "dividendo", "frazionamento")} for s, df in barre.items()}
    # la storia si taglia per giorno di New York
    barre_ny = {s: df.set_axis(pd.Index(giorni_per[s])) for s, df in barre.items()}
    storia = Storia(barre_ny, tutti)
    c_di = (lambda s: costi[s]) if isinstance(costi, dict) else (lambda s: costi)
    tasso_debito = max(c.interesse_debito_annuo for c in costi.values()) if isinstance(costi, dict) else costi.interesse_debito_annuo

    stato = StatoConto(contanti=float(capitale))
    in_attesa: list[tuple[str, Ordine]] = []
    riportati: list[tuple[str, Ordine]] = []           # uscite rimaste senza barra, da riprovare
    uscite_rimandate = 0
    valori = np.empty(len(tutti))
    esecuzioni: list[dict] = []
    rifiutati = senza_barra = 0
    assenze: dict[str, int] = {}
    liquidati: list[str] = []
    tot_comm = tot_scarto = tot_div = 0.0

    for k, d in enumerate(tutti):
        oggi = {s: riga[s][d] for s in barre if d in riga[s]}
        if liquida_dopo is not None:
            for s in list(stato.azioni):
                if s in oggi:
                    assenze.pop(s, None)
                    continue
                assenze[s] = assenze.get(s, 0) + 1
                if assenze[s] >= liquida_dopo:
                    q = stato.azioni.pop(s)
                    prezzo = stato.ultimo_prezzo.get(s, 0.0)
                    stato.contanti += q * prezzo
                    liquidati.append(s)
                    in_attesa = [(x, o) for x, o in in_attesa if x != s]
                    riportati = [(x, o) for x, o in riportati if x != s]
                    esecuzioni.append({"giorno": d, "simbolo": s, "quantita": -q, "prezzo": prezzo, "tipo": "listino",
                                       "commissione": 0.0, "scarto": 0.0, "etichetta": "uscito dal listino"})
        # 1. dividendi e frazionamenti
        for s, i in oggi.items():
            q = stato.azioni.get(s, 0.0)
            div = col[s]["dividendo"]
            if div is not None and not np.isnan(div[i]) and div[i] and q:
                stato.contanti += q * div[i]
                tot_div += q * div[i]
            fr = col[s]["frazionamento"]
            if fr is not None and not np.isnan(fr[i]) and fr[i] not in (0.0, 1.0):
                if s in stato.ultimo_prezzo:
                    stato.ultimo_prezzo[s] /= fr[i]
                if q:
                    nuove = q * fr[i]
                    if not frazionarie:
                        # la frazione di azione si paga in contanti all'ultimo prezzo (come fa il broker)
                        intere = float(np.trunc(round(nuove, 9)))
                        stato.contanti += (nuove - intere) * stato.ultimo_prezzo.get(s, 0.0)
                        nuove = intere
                    stato.azioni[s] = nuove
                    if nuove == 0:
                        del stato.azioni[s]
                arrotonda = (lambda x: float(np.trunc(round(x, 9)))) if not frazionarie else (lambda x: x)

                def adatta(lista, s=s, f=fr[i], arrotonda=arrotonda):
                    nuovi = []
                    for x, o in lista:
                        if x != s:
                            nuovi.append((x, o))
                            continue
                        qq = arrotonda(o.quantita * f)
                        if qq:
                            nuovi.append((x, Ordine(qq, o.tipo, None if o.prezzo is None else o.prezzo / f, o.solo_riduce,
                                                    o.etichetta)))
                    return nuovi
                in_attesa, riportati = adatta(in_attesa), adatta(riportati)
        # 2. ordini: stop, vendite, acquisti, limiti
        ordine_tipo = {"stop": 0, "mercato": 1, "limite": 3}
        lavoro = [(s, o, False) for s, o in in_attesa] + [(s, o, True) for s, o in riportati]
        ordinati = sorted(lavoro, key=lambda so: ordine_tipo[so[1].tipo] + (0 if so[1].quantita < 0 or so[1].tipo != "mercato" else 1))
        da_riportare: list[tuple[str, Ordine]] = []
        for s, o, riportato in ordinati:
            if s not in oggi:
                if not riportato:
                    senza_barra += 1
                pos_ = stato.azioni.get(s, 0.0)
                if o.tipo == "mercato" and pos_ and np.sign(o.quantita) == -np.sign(pos_):
                    da_riportare.append((s, Ordine(o.quantita, o.tipo, o.prezzo, True, o.etichetta, o.dopo_ingresso)))
                    uscite_rimandate += 0 if riportato else 1
                continue
            i = oggi[s]
            cs = c_di(s)
            q = o.quantita
            pos = stato.azioni.get(s, 0.0)
            if o.solo_riduce:
                if pos == 0 or np.sign(q) == np.sign(pos):
                    continue
                q = np.sign(q) * min(abs(q), abs(pos))
            es = _esecuzione(o, col[s]["open"][i], col[s]["high"][i], col[s]["low"][i], cs)
            if es is None:
                continue
            prezzo, base = es
            comm = cs.commissione(q, prezzo)
            prima = dict(stato.ultimo_prezzo)
            stato.ultimo_prezzo[s] = prezzo
            dopo_azioni = pos + q
            dopo_contanti = stato.contanti - q * prezzo - comm
            lordo_dopo = stato.lordo() - abs(pos) * prezzo + abs(dopo_azioni) * prezzo
            valore_dopo = dopo_contanti + sum(x * stato.ultimo_prezzo.get(y, 0.0) for y, x in stato.azioni.items() if y != s) \
                + dopo_azioni * prezzo
            if lordo_dopo > leva_massima * valore_dopo + 1e-9 and abs(dopo_azioni) > abs(pos):
                rifiutati += 1
                stato.ultimo_prezzo = prima
                continue
            stato.azioni[s] = dopo_azioni
            if dopo_azioni == 0:
                del stato.azioni[s]
            stato.contanti = dopo_contanti
            scarto = abs(q) * abs(prezzo - base)
            tot_comm += comm
            tot_scarto += scarto
            esecuzioni.append({"giorno": d, "simbolo": s, "quantita": q, "prezzo": prezzo, "tipo": o.tipo,
                               "commissione": comm, "scarto": scarto, "etichetta": o.etichetta})
        # 3. valore alla chiusura, e l'interesse sui contanti presi a prestito (leva) per la notte
        for s, i in oggi.items():
            stato.ultimo_prezzo[s] = col[s]["close"][i]
        if stato.contanti < 0 and tasso_debito:
            stato.contanti -= -stato.contanti * tasso_debito / 252
        # il prestito dei titoli venduti allo scoperto, per ogni notte
        for s_, q_ in stato.azioni.items():
            if q_ < 0:
                tasso = c_di(s_).prestito_annuo
                if tasso:
                    stato.contanti -= -q_ * stato.ultimo_prezzo.get(s_, 0.0) * tasso / 252
        valori[k] = stato.valore()
        # 4. decisione per il giorno dopo
        storia.i = k
        vista = StatoConto(stato.contanti, dict(stato.azioni), dict(stato.ultimo_prezzo))
        decisi = strategia(d, storia, vista) or []
        for s, o in decisi:
            if not frazionarie and float(o.quantita) != int(o.quantita):
                raise ValueError(f"quantità frazionaria {o.quantita} per {s} con frazionarie=False")
        in_attesa = list(decisi)
        nuovi_titoli = {s for s, _ in decisi}
        riportati = [(s, o) for s, o in da_riportare if s not in nuovi_titoli]

    ultimo = tutti[-1] if tutti else None
    bloccati = [s for s, q in stato.azioni.items() if q and giorni_per[s][-1] != ultimo]
    es_df = pd.DataFrame(esecuzioni, columns=["giorno", "simbolo", "quantita", "prezzo", "tipo", "commissione", "scarto",
                                              "etichetta"])
    return RisultatoConto(valore=pd.Series(valori, index=pd.Index(tutti, name="giorno"), name="valore"),
                          esecuzioni=es_df, rifiutati=rifiutati, senza_barra=senza_barra, commissioni=tot_comm,
                          costo_scarto=tot_scarto, dividendi=tot_div, bloccati=bloccati, liquidati=liquidati,
                          uscite_rimandate=uscite_rimandate)


def verso_pesi(stato: StatoConto, pesi: dict[str, float], prezzi: dict[str, float], quota: float = 0.98,
               etichetta: str = "") -> list[tuple[str, Ordine]]:
    """Gli ordini a mercato che portano il conto ai `pesi` (frazione del valore, somma ≤ 1) con il
    `quota` del valore investito, ai `prezzi` della decisione; i titoli non nei pesi si vendono."""
    v = stato.valore() * quota
    out = []
    for s in sorted(set(stato.azioni) | set(pesi)):
        p = prezzi.get(s) or stato.ultimo_prezzo.get(s)
        voluto = int(v * pesi.get(s, 0.0) / p) if p else 0
        d = voluto - stato.azioni.get(s, 0.0)
        if d:
            out.append((s, Ordine(d, "mercato", etichetta=etichetta)))
    return out
