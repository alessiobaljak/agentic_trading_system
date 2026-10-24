"""Il simulatore: una strategia sulle barre del passato, con i costi.

Le regole che tengono lontani i dati del futuro e le esecuzioni troppo comode:

* La strategia viene chiamata alla CHIUSURA di ogni barra con la storia fino a quella barra
  compresa, e restituisce gli ordini per la barra DOPO. Non vede mai la barra in cui si esegue.
* Gli ordini valgono una sola barra: se la strategia li vuole ancora, li rimanda (come annullare
  e rimettere un ordine a ogni barra).
* **A mercato**: eseguito all'apertura della barra dopo, più metà dello scarto e lo slittamento.
* **Limite**: eseguito solo se il prezzo PASSA OLTRE il livello (acquisto: minimo strettamente sotto
  il limite; vendita: massimo strettamente sopra). Toccarlo non basta (lezione delle crypto). Se
  l'apertura è già oltre il limite, si paga l'apertura più metà dello scarto, ma mai peggio del
  limite.
* **Stop**: scatta appena il prezzo tocca il livello; si paga il peggiore fra il livello e
  l'apertura (un'apertura oltre lo stop lo salta), più metà dello scarto e lo slittamento.
* Nella stessa barra gli stop si eseguono prima dei limiti: se in una barra si toccano sia lo stop
  sia l'obiettivo, si assume il caso peggiore.
* Dividendi e frazionamenti (colonne facoltative `dividendo`, `frazionamento` sul giorno di stacco)
  si applicano all'apertura di quel giorno, prima degli ordini: chi aveva le azioni alla chiusura di
  ieri incassa il dividendo (chi era allo scoperto lo paga), e le azioni si moltiplicano per il
  rapporto del frazionamento. I prezzi delle barre sono quelli scambiati davvero, non rettificati.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

from stock.simulatore.costi import Costi

NY = "America/New_York"
TIPI = ("mercato", "limite", "stop")


@dataclass(frozen=True)
class Ordine:
    quantita: float               # positiva compra, negativa vende
    tipo: str = "mercato"
    prezzo: float | None = None   # livello per limite e stop
    solo_riduce: bool = False     # non apre né gira la posizione: si taglia a quella che c'è
    etichetta: str = ""

    def __post_init__(self):
        if self.tipo not in TIPI:
            raise ValueError(f"tipo di ordine sconosciuto: {self.tipo}")
        if self.tipo != "mercato" and (self.prezzo is None or self.prezzo <= 0):
            raise ValueError(f"un ordine {self.tipo} vuole un prezzo positivo")
        if self.quantita == 0:
            raise ValueError("quantità zero")


@dataclass
class Stato:
    """Quello che la strategia sa del conto alla chiusura della barra."""
    contanti: float
    azioni: float = 0.0

    def valore(self, prezzo: float) -> float:
        return self.contanti + self.azioni * prezzo


@dataclass
class Risultato:
    valore: pd.Series                  # valore del conto alla chiusura di ogni barra
    esecuzioni: pd.DataFrame
    rifiutati: int
    commissioni: float
    costo_scarto: float                # scarto + slittamento pagati, in dollari
    prestito: float
    dividendi: float
    costi: Costi = field(repr=False, default=None)


Strategia = Callable[[pd.DataFrame, Stato], list]


def _esecuzione(o: Ordine, ap: float, alto: float, basso: float, c: Costi) -> tuple[float, float] | None:
    """Prezzo pagato e prezzo «senza costi» se l'ordine si esegue in questa barra, altrimenti None."""
    s = 1.0 if o.quantita > 0 else -1.0
    if o.tipo == "mercato":
        return ap * (1 + s * (c.mezzo_scarto + c.slittamento)), ap
    if o.tipo == "limite":
        if s > 0:
            if not basso < o.prezzo:
                return None
            if ap < o.prezzo:
                return min(ap * (1 + c.mezzo_scarto), o.prezzo), ap
            return o.prezzo, o.prezzo
        if not alto > o.prezzo:
            return None
        if ap > o.prezzo:
            return max(ap * (1 - c.mezzo_scarto), o.prezzo), ap
        return o.prezzo, o.prezzo
    # stop
    if s > 0:
        if not alto >= o.prezzo:
            return None
        base = max(ap, o.prezzo)
    else:
        if not basso <= o.prezzo:
            return None
        base = min(ap, o.prezzo)
    return base * (1 + s * (c.mezzo_scarto + c.slittamento)), base


def simula(barre: pd.DataFrame, strategia: Strategia, costi: Costi, capitale: float = 100_000.0,
           leva_massima: float = 1.0, frazionarie: bool = False) -> Risultato:
    """Fa girare `strategia` su `barre` (indice di tempo; colonne open, high, low, close e, se ci
    sono, dividendo e frazionamento). `leva_massima`: valore lordo delle posizioni / valore del
    conto oltre il quale un ordine viene rifiutato (1 = niente prestito)."""
    if not barre.index.is_monotonic_increasing or barre.index.has_duplicates:
        raise ValueError("le barre devono essere in ordine di tempo e senza doppioni")
    ap_ = barre["open"].to_numpy(float)
    al_ = barre["high"].to_numpy(float)
    ba_ = barre["low"].to_numpy(float)
    ch_ = barre["close"].to_numpy(float)
    div_ = barre["dividendo"].fillna(0).to_numpy(float) if "dividendo" in barre else np.zeros(len(barre))
    fr_ = barre["frazionamento"].fillna(1).to_numpy(float) if "frazionamento" in barre else np.ones(len(barre))
    fr_[fr_ == 0] = 1.0
    giorni = barre.index.tz_convert(NY).date if isinstance(barre.index, pd.DatetimeIndex) and barre.index.tz is not None \
        else pd.Index(barre.index).map(lambda t: pd.Timestamp(t).date())
    ultima_del_giorno = np.r_[np.array(giorni[1:]) != np.array(giorni[:-1]), True]

    stato = Stato(contanti=float(capitale))
    in_attesa: list[Ordine] = []
    valori = np.empty(len(barre))
    esecuzioni: list[dict] = []
    rifiutati = 0
    tot_comm = tot_scarto = tot_prestito = tot_div = 0.0

    for i in range(len(barre)):
        ap, alto, basso, chiu = ap_[i], al_[i], ba_[i], ch_[i]
        # 1. eventi del giorno di stacco, prima di qualunque ordine
        if div_[i] and stato.azioni:
            incasso = stato.azioni * div_[i]
            stato.contanti += incasso
            tot_div += incasso
        if fr_[i] != 1.0:
            stato.azioni *= fr_[i]
            in_attesa = [Ordine(o.quantita * fr_[i], o.tipo, None if o.prezzo is None else o.prezzo / fr_[i],
                                o.solo_riduce, o.etichetta) for o in in_attesa]
        # 2. ordini decisi alla chiusura della barra prima: stop, poi a mercato, poi limiti
        ordinati = sorted(in_attesa, key=lambda o: {"stop": 0, "mercato": 1, "limite": 2}[o.tipo])
        for o in ordinati:
            q = o.quantita
            if o.solo_riduce:
                if stato.azioni == 0 or np.sign(q) == np.sign(stato.azioni):
                    continue
                q = np.sign(q) * min(abs(q), abs(stato.azioni))
            es = _esecuzione(o, ap, alto, basso, costi)
            if es is None:
                continue
            prezzo, base = es
            comm = costi.commissione(q, prezzo)
            dopo_azioni = stato.azioni + q
            dopo_contanti = stato.contanti - q * prezzo - comm
            valore_dopo = dopo_contanti + dopo_azioni * prezzo
            if abs(dopo_azioni) * prezzo > leva_massima * valore_dopo + 1e-9 and abs(dopo_azioni) > abs(stato.azioni):
                rifiutati += 1
                continue
            stato.azioni, stato.contanti = dopo_azioni, dopo_contanti
            scarto = abs(q) * abs(prezzo - base)
            tot_comm += comm
            tot_scarto += scarto
            esecuzioni.append({"t": barre.index[i], "quantita": q, "prezzo": prezzo, "tipo": o.tipo,
                               "commissione": comm, "scarto": scarto, "etichetta": o.etichetta})
        # 3. il prestito delle azioni allo scoperto si paga per ogni notte
        if stato.azioni < 0 and ultima_del_giorno[i] and costi.prestito_annuo:
            p = -stato.azioni * chiu * costi.prestito_annuo / 252
            stato.contanti -= p
            tot_prestito += p
        valori[i] = stato.valore(chiu)
        # 4. la strategia decide alla chiusura, per la barra dopo
        decisi = strategia(barre.iloc[: i + 1], Stato(stato.contanti, stato.azioni)) or []
        for o in decisi:
            if not frazionarie and float(o.quantita) != int(o.quantita):
                raise ValueError(f"quantità frazionaria {o.quantita} con frazionarie=False")
        in_attesa = list(decisi)

    es_df = pd.DataFrame(esecuzioni, columns=["t", "quantita", "prezzo", "tipo", "commissione", "scarto", "etichetta"])
    return Risultato(valore=pd.Series(valori, index=barre.index, name="valore"), esecuzioni=es_df,
                     rifiutati=rifiutati, commissioni=tot_comm, costo_scarto=tot_scarto, prestito=tot_prestito,
                     dividendi=tot_div, costi=costi)


def simula_anche_doppi(barre: pd.DataFrame, strategia: Strategia, costi: Costi, **kw) -> tuple[Risultato, Risultato]:
    """Lo stesso calcolo con i costi veri e con i costi raddoppiati (`METODO.md`, sezione 5)."""
    return simula(barre, strategia, costi, **kw), simula(barre, strategia, costi.raddoppiati(), **kw)


def verso(stato: Stato, azioni_volute: float, etichetta: str = "") -> list[Ordine]:
    """L'ordine a mercato che porta la posizione a `azioni_volute` (nessuno se ci è già)."""
    d = azioni_volute - stato.azioni
    return [Ordine(d, "mercato", etichetta=etichetta)] if d else []


def statistiche(valore: pd.Series) -> dict:
    """Rendimento totale, rendimento annuo, Sharpe annuo sui rendimenti giornalieri (252 giorni,
    senza tasso privo di rischio) e massima perdita dal picco. I giorni sono quelli di New York."""
    if valore.empty:
        return {}
    idx = valore.index.tz_convert(NY) if getattr(valore.index, "tz", None) is not None else valore.index
    per_giorno = pd.Series(valore.to_numpy(), index=pd.Index(pd.DatetimeIndex(idx).date)).groupby(level=0).last()
    r = per_giorno.pct_change().dropna()
    anni = max(len(per_giorno) / 252, 1e-9)
    totale = per_giorno.iloc[-1] / per_giorno.iloc[0] - 1
    sharpe = float(r.mean() / r.std() * np.sqrt(252)) if len(r) > 1 and r.std() > 0 else float("nan")
    picco = per_giorno.cummax()
    return {"rendimento_totale": float(totale), "rendimento_annuo": float((1 + totale) ** (1 / anni) - 1),
            "sharpe": sharpe, "perdita_massima": float((per_giorno / picco - 1).min()), "giorni": int(len(per_giorno))}
