"""Motore di backtest del protocollo di ricerca (sezione 7 di research/PROTOCOLLO.md).

E' un motore INDIPENDENTE dal bot: non importa nulla da bot/, backtesting/ o
scripts/. Usa solo la libreria standard. Tutte le funzioni sono pure: ricevono
dati e parametri, restituiscono risultati, non toccano file ne' stato globale.

Le scelte che il protocollo lascia aperte sono scritte qui, una per una, con il
perche'. Chi legge il codice deve poter ricostruire a mano ogni numero.

Convenzioni
-----------
* Timestamp in millisecondi. ``Candela.ts`` e' l'apertura, ``Candela.close_ts``
  la chiusura INCLUSA (stile Binance: ts + durata - 1).
* Tre serie di candele, allineate per ``ts``:
  - ``candele``: last price, su cui la strategia calcola i segnali e su cui si
    riempie il target (un take-profit limit si riempie sull'ultimo prezzo);
  - ``candele_stop``: la serie su cui scatta lo stop (quella che il bot
    confronta con lo stop, cioe' il suo ``workingType``);
  - ``candele_mark``: il mark price, su cui si valuta la liquidazione.
  Se ``candele_stop`` o ``candele_mark`` sono ``None`` si usa ``candele``.
* Solo barre chiuse: la strategia alla barra ``i`` riceve le barre ``0..i``
  (una ``StoriaChiusa``: si legge come ``candele[:i+1]`` ma non la copia);
  l'ingresso avviene all'apertura della barra ``i + 1 + ritardo_barre``.
* Il momento esatto in cui, dentro una barra, succedono le cose non si conosce:
  dove serve una scelta si prende quella PEGGIORE per il trade (stop prima del
  target, gap riempito all'apertura, funding ambiguo contato solo se costo).
  L'unica cosa che si sa per certo e' che l'APERTURA e' il primo prezzo della
  barra: se la barra apre gia' oltre la liquidazione, lo stop o il target,
  quell'uscita avviene all'apertura, prima di qualunque altro evento della
  barra, e la regola ``riempimento_intrabarra`` non si applica (non c'e'
  ambiguita' da risolvere). Ordine dei gap: liquidazione, poi stop, poi target
  (per una posizione ben formata non possono valere insieme).
* Tempi: un'uscita all'apertura (ingresso, "chiudi") ha ``ts`` = apertura
  della barra. Un'uscita avvenuta DENTRO la barra (stop, target, liquidazione)
  e "fine_dati" hanno ``ts_uscita`` = ``close_ts`` della barra: si sa solo che
  e' successa entro la chiusura. Cosi' un trade non risulta mai aperto e
  chiuso nello stesso istante e la curva del capitale non anticipa la perdita.
* Buchi nei dati: ``esegui`` accetta serie con barre mancanti (le serie reali
  ne hanno, vedi ``dati.py``), ma li CONTA (``n_buchi_dati``) e i settlement
  di funding caduti dentro un buco con posizione aperta si addebitano
  sull'ultimo mark disponibile (il close della barra prima del buco) e si
  contano a parte (``n_funding_in_buco``). Ts duplicati o non crescenti sono
  un errore nei dati: ValueError.

Dimensione, leva e liquidazione (scelte documentate)
----------------------------------------------------
* quantita' = capitale * rischio_per_trade / |apertura - stop|: il bot
  dimensiona l'ordine sul prezzo che vede (l'apertura della barra), PRIMA di
  conoscere il riempimento. Il rischio iniziale vero e' pero'
  ``quantita' * |entrata - stop|`` con ``entrata`` il riempimento peggiorato
  dallo slippage: e' un po' sopra capitale * rischio_per_trade, ed e' quello
  che divide il pnl per dare R. Cosi' la quantita' non dipende dai costi e la
  prova a costi doppi cambia solo i costi, non la dimensione.
* Se il notional (quantita' * entrata) supera capitale * leva_max, la quantita'
  si riduce al tetto: il trade e' RIDOTTO, contato e dichiarato, non scartato.
* Leva effettiva = min(leva_max, max(1, notional / capitale)). Il bot imposta la
  leva per ogni trade: una leva sotto 1 non esiste su Binance (il minimo e' 1x)
  e sopra ``leva_max`` il bot non va. Con questa scelta il prezzo di
  liquidazione e' quello di un conto che usa SOLO il margine necessario al
  trade (il resto del capitale non protegge la posizione): e' il caso prudente.
* Prezzo di liquidazione (margine di mantenimento ``mmr``):
  - isolated: long  liq = entrata * (1 - 1/leva + mmr)
              short liq = entrata * (1 + 1/leva - mmr)
    cioe' la liquidazione scatta quando la perdita sul mark price consuma
    margine (= notional/leva) meno margine di mantenimento (= mmr * notional).
  - cross: stessa formula ma con il capitale intero a fare da margine, cioe'
    leva_cross = notional / capitale (puo' essere sotto 1: la liquidazione e'
    allora lontanissima, per un long sotto zero = mai).
* La liquidazione si chiude al prezzo di liquidazione, con commissioni e
  slippage normali (approssimano la penale di liquidazione: scelta prudente).
  Se il mark APRE gia' oltre il prezzo di liquidazione, la chiusura e' comunque
  una liquidazione a quel prezzo: in isolated la perdita non puo' superare il
  margine della posizione (il conto non va mai sotto zero per un gap), e lo
  stop, che si riempirebbe all'apertura, non fa in tempo a scattare.
* Se nella stessa barra il mark tocca la liquidazione E la serie stop tocca lo
  stop (senza gap), vince lo stop se e' piu' vicino all'entrata della
  liquidazione (il prezzo deve passare prima da li'), altrimenti la liquidazione.
* Lo stop SCATTA sulla serie stop (per il protocollo il last price,
  ``serie_stop`` di parametri.yaml, cioe' ``candele_stop=None``; se si passasse il
  mark price, su cui nessuno scambia) ma si RIEMPIE sul last price: il prezzo di riferimento e' lo stop
  (o l'apertura del last, se la serie stop apre gia' oltre lo stop), ma mai
  fuori dall'intervallo low-high del last nella barra. Se il last non e' mai
  sceso fino allo stop di un long, il riempimento e' il minimo del last (il
  peggior prezzo eseguibile), non un prezzo che il mercato non ha fatto.

Costi
-----
* Commissione taker per lato sul notional del riempimento vero.
* Slippage per lato: entrata peggiorata, uscita peggiorata. ``slippage_costo``
  e' la differenza in valuta rispetto al prezzo di riferimento (apertura, stop,
  target, liquidazione, close).
* ``pnl_lordo`` = quantita' * (uscita di riferimento - entrata di riferimento),
  col segno della direzione; ``pnl`` = pnl_lordo - commissioni - slippage -
  funding. ``pnl_pct`` = pnl / capitale al momento dell'ingresso. Tutti i COSTI
  sono moltiplicati per ``moltiplicatore_costi``: commissioni, slippage e il
  funding solo quando e' un costo. Un incasso di funding non si moltiplica,
  altrimenti la prova a costi doppi migliorerebbe il risultato degli short in
  regime di funding positivo (il caso normale sul crypto).
* Funding: notional al settlement = quantita' * apertura della candela mark che
  contiene il settlement (il settlement cade di norma all'apertura della
  candela). Long paga tasso * notional se tasso > 0 e incassa se < 0; short il
  contrario. ``funding_pagato`` positivo = costo.
  Momenti ambigui (contati SOLO se costo): settlement nello stesso istante
  dell'ingresso (non si sa se la posizione era gia' aperta: su Binance la foto
  delle posizioni e' presa al settlement e un ordine mandato all'apertura
  arriva dopo), settlement nello stesso istante dell'uscita per "chiudi", e
  settlement nella stessa barra di un'uscita per stop/target/liquidazione.

Campagna di gruppo (campagne/GRUPPO/regole.md, sezione 13)
---------------------------------------------------------
* ``simula_baseline_casuale`` ha la chiave ``r_medio_per_seme`` (l'R medio di
  ogni seme, ``None`` per le simulazioni vuote) e, con
  ``rifiuta_poche_simulazioni=False``, non alza con meno di 2 simulazioni con
  trade: per le campagne singole non cambia nulla.
* ``simula_sfasamento_comune``: le strategie sfasate di una moneta (sezione 5,
  punto 5, e sezione 9, punti 3-4), con i trade in ``TradeSfasato``.
* ``metriche_di_gruppo``: le metriche dei trade sommati con le chiavi di
  ``statistica.criterio_vault`` (sezione 9, punto 2).
* ``somme_dei_trade`` e ``metriche_di_gruppo_da_somme``: le stesse quattro chiavi
  di ``criterio_vault`` dalle somme per moneta (numero dei trade, somma degli R,
  dei guadagni e delle perdite), per le sfasate del vault (sezione 9, punto 4).
* ``posizioni_aperte_insieme``: il massimo di posizioni aperte insieme, per
  direzione (sezione 8, punto 2).
"""

from __future__ import annotations

import math
from bisect import bisect_right
from collections.abc import Mapping as MappingABC
from collections.abc import Sequence as SequenceABC
from itertools import islice
import operator
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Callable, Dict, Iterable, List, Literal, Mapping, NamedTuple, Optional, Sequence, Tuple, Union

Direzione = Literal["long", "short"]
Esito = Literal["stop", "target", "segnale", "liquidazione", "fine_dati"]


# ---------------------------------------------------------------------------
# Dati
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Candela:
    """Una candela: ``ts`` apertura in ms, ``close_ts`` chiusura inclusa in ms."""

    ts: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_ts: int


@dataclass(frozen=True)
class Segnale:
    """Richiesta di ingresso della strategia: direzione, stop e target (opzionale)."""

    direzione: Direzione
    stop: float
    target: Optional[float] = None


@dataclass
class Posizione:
    """Posizione aperta. ``entrata`` e' il riempimento vero (con slippage)."""

    direzione: Direzione
    entrata: float
    stop: float
    target: Optional[float]
    quantita: float
    ts_entrata: int
    entrata_riferimento: float  # apertura della barra, prima dello slippage
    rischio_iniziale: float  # quantita * |entrata - stop|, in valuta
    leva_effettiva: float
    prezzo_liquidazione: float
    ridotto: bool
    violazione_liquidazione: bool
    funding_pagato: float = 0.0
    capitale_ingresso: float = 0.0  # capitale al momento dell'ingresso: base del pnl in percentuale


@dataclass
class Parametri:
    """Parametri del motore. I default sono D'ESEMPIO (usati dai test del Passo 0).

    I parametri di una campagna si prendono da ``config/parametri.yaml`` (rischio,
    leva, commissione, margine di mantenimento 0,025, ...) e dalla fascia di
    slippage di ``campagne/<SIMBOLO>/scheda_moneta.md`` (sezione 7).
    """

    commissione_per_lato: float = 0.0005
    slippage_per_lato: float = 0.0002
    rischio_per_trade: float = 0.01
    leva_max: float = 2.0
    modalita_margine: Literal["isolated", "cross"] = "isolated"
    tasso_margine_mantenimento: float = 0.01
    margine_minimo_da_liquidazione: float = 0.8
    capitale_iniziale: float = 1000.0
    riempimento_intrabarra: Literal["stop_prima", "target_prima"] = "stop_prima"
    moltiplicatore_costi: float = 1.0
    ritardo_barre: int = 0


@dataclass
class Trade:
    """Un trade chiuso. Prezzi di entrata e uscita sono i riempimenti veri."""

    direzione: Direzione
    ts_entrata: int
    ts_uscita: int
    entrata: float
    uscita: float
    stop: float
    target: Optional[float]
    quantita: float
    ridotto: bool
    violazione_liquidazione: bool
    esito: Esito
    pnl: float
    pnl_lordo: float
    commissioni: float
    slippage_costo: float
    funding_pagato: float
    rischio_iniziale: float
    r: float
    leva_effettiva: float
    prezzo_liquidazione: float
    pnl_pct: float = 0.0  # pnl netto / capitale al momento dell'ingresso (frazione)


@dataclass
class Risultato:
    """Esito di ``esegui``: trade chiusi, curva del capitale e contatori.

    I contatori distinguono i motivi per cui un segnale non e' diventato un
    trade: stop dalla parte sbagliata (``n_segnali_non_validi``), nessuna barra
    dopo il segnale (``n_segnali_senza_barra``), capitale esaurito
    (``n_segnali_capitale_esaurito``). ``n_buchi_dati`` e ``n_funding_in_buco``
    dichiarano le barre mancanti nella serie e i settlement caduti dentro un buco.
    """

    trades: List[Trade]
    curva_capitale: List[Tuple[int, float]]
    capitale_iniziale: float
    capitale_finale: float
    n_segnali_non_validi: int = 0
    n_segnali_senza_barra: int = 0  # segnali arrivati troppo vicino alla fine dei dati
    n_segnali_capitale_esaurito: int = 0  # segnali validi scartati perche' il capitale e' <= 0
    n_buchi_dati: int = 0  # coppie di barre consecutive non contigue nella serie
    n_funding_in_buco: int = 0  # settlement caduti in un buco e addebitati sull'ultimo mark

    def metriche(self) -> Dict[str, object]:
        return calcola_metriche(self)


Strategia = Callable[[Sequence[Candela], Optional[Posizione]], Union[Segnale, str, None]]


class StoriaChiusa(SequenceABC):
    """Le barre chiuse fino alla barra corrente, in sola lettura, SENZA copiarle.

    Fino al 7 ott 2026 ``esegui`` passava alla strategia ``candele[: i + 1]``,
    una copia della storia a ogni barra: il tempo cresceva col quadrato delle
    barre (a 1 ora, circa 26.000 barre in tre anni, piu' di un secondo per
    esecuzione), e le 200 simulazioni della baseline (b) diventavano ore. La
    vista si comporta come quella copia per tutte le letture: ``len``, indici
    interi (anche negativi; un indice non intero alza TypeError come una lista),
    fette (che restituiscono una lista), iterazione, ``in``, ``index``,
    ``count``. Non e' una lista: ``storia + altra_lista`` non funziona, e chi
    vuole una lista scrive ``list(storia)``.

    Niente futuro, neppure per sbaglio: ``esegui`` costruisce la vista sopra una
    lista che contiene SOLO le barre gia' chiuse (cresce di una barra alla
    volta), quindi anche l'attributo interno ``_base`` non arriva oltre la barra
    corrente. Un indice oltre alza IndexError.
    """

    __slots__ = ("_base", "_n")

    def __init__(self, base: Sequence[Candela], n: int) -> None:
        self._base = base
        self._n = n

    def __len__(self) -> int:
        return self._n

    def __getitem__(self, indice):
        if isinstance(indice, slice):
            inizio, fine, passo = indice.indices(self._n)
            if passo == 1:
                return list(self._base[inizio:fine]) if fine > inizio else []
            return [self._base[k] for k in range(inizio, fine, passo)]
        k = operator.index(indice)
        if k < 0:
            k += self._n
        if k < 0 or k >= self._n:
            raise IndexError("indice fuori dalla storia chiusa")
        return self._base[k]

    def __iter__(self):
        return islice(self._base, self._n)

    def __eq__(self, altra) -> bool:
        try:
            return len(altra) == self._n and all(a == b for a, b in zip(self, altra))
        except TypeError:
            return NotImplemented

    def __repr__(self) -> str:
        return f"StoriaChiusa({self._n} barre)"


# ---------------------------------------------------------------------------
# Pezzi puri: dimensione, liquidazione, costi
# ---------------------------------------------------------------------------


def prezzo_riempimento_entrata(prezzo: float, direzione: Direzione, parametri: Parametri) -> float:
    """Apertura peggiorata dallo slippage: long compra piu' caro, short vende piu' basso."""
    s = parametri.slippage_per_lato * parametri.moltiplicatore_costi
    return prezzo * (1 + s) if direzione == "long" else prezzo * (1 - s)


def prezzo_riempimento_uscita(prezzo: float, direzione: Direzione, parametri: Parametri) -> float:
    """Prezzo di uscita peggiorato dallo slippage: long vende piu' basso, short ricompra piu' caro."""
    s = parametri.slippage_per_lato * parametri.moltiplicatore_costi
    return prezzo * (1 - s) if direzione == "long" else prezzo * (1 + s)


def calcola_quantita(
    capitale: float, prezzo_riferimento: float, entrata: float, stop: float, parametri: Parametri
) -> Tuple[float, bool]:
    """Quantita' dal rischio per trade, ridotta al tetto di leva se serve.

    La dimensione si calcola sul prezzo di riferimento (l'apertura, quello che il
    bot vede quando manda l'ordine); il tetto di leva si verifica sul notional
    vero (quantita' * entrata riempita). Restituisce (quantita, ridotto).

    ValueError se lo stop coincide col prezzo di riferimento (distanza zero: la
    quantita' sarebbe infinita) o se l'entrata non e' positiva: la funzione e'
    pubblica e chi la usa da sola deve ricevere un errore parlante.
    """
    distanza = abs(prezzo_riferimento - stop)
    if distanza <= 0:
        raise ValueError(f"stop {stop} uguale al prezzo di riferimento {prezzo_riferimento}: distanza zero")
    if entrata <= 0:
        raise ValueError(f"prezzo di entrata non positivo: {entrata}")
    quantita = capitale * parametri.rischio_per_trade / distanza
    tetto = capitale * parametri.leva_max
    if quantita * entrata > tetto:
        return tetto / entrata, True
    return quantita, False


def leva_effettiva(notional: float, capitale: float, parametri: Parametri) -> float:
    """Leva che il bot imposterebbe per il trade: tra 1 e leva_max, secondo il notional."""
    if capitale <= 0:
        return parametri.leva_max
    return min(parametri.leva_max, max(1.0, notional / capitale))


def prezzo_liquidazione(entrata: float, direzione: Direzione, leva: float, parametri: Parametri) -> float:
    """Prezzo di liquidazione con la formula della docstring del modulo.

    Per un long il risultato e' azzerato se viene negativo (leva cross sotto 1):
    vuol dire che la liquidazione non puo' arrivare.
    """
    mmr = parametri.tasso_margine_mantenimento
    if direzione == "long":
        return max(0.0, entrata * (1 - 1 / leva + mmr))
    return entrata * (1 + 1 / leva - mmr)


def leva_per_liquidazione(notional: float, capitale: float, parametri: Parametri) -> float:
    """Leva da usare nel calcolo della liquidazione secondo la modalita' di margine.

    isolated: la leva effettiva del trade (margine = notional / leva).
    cross: tutto il capitale fa da margine, quindi leva_cross = notional / capitale.
    """
    if parametri.modalita_margine == "cross":
        return notional / capitale if capitale > 0 else parametri.leva_max
    if parametri.modalita_margine != "isolated":
        raise ValueError(f"modalita_margine sconosciuta: {parametri.modalita_margine!r}")
    return leva_effettiva(notional, capitale, parametri)


def violazione_margine(entrata: float, stop: float, liq: float, parametri: Parametri) -> bool:
    """True se lo stop e' piu' lontano di margine_minimo_da_liquidazione * distanza della liquidazione."""
    return abs(entrata - stop) > parametri.margine_minimo_da_liquidazione * abs(entrata - liq)


def segno(direzione: Direzione) -> int:
    return 1 if direzione == "long" else -1


def funding_di_un_settlement(direzione: Direzione, quantita: float, prezzo_mark: float, tasso: float, parametri: Parametri) -> float:
    """Funding (positivo = costo) di un settlement per una posizione aperta.

    Long paga tasso * notional se tasso > 0 (e incassa se < 0); short il contrario.
    ``moltiplicatore_costi`` si applica SOLO se e' un costo: un incasso resta
    uguale, cosi' la prova a costi doppi non puo' migliorare il risultato.
    """
    f = segno(direzione) * tasso * quantita * prezzo_mark
    return f * parametri.moltiplicatore_costi if f > 0 else f


# ---------------------------------------------------------------------------
# Allineamento serie e cucitura contratti
# ---------------------------------------------------------------------------


def allinea_serie(candele: Sequence[Candela], altra: Optional[Sequence[Candela]], nome: str) -> List[Candela]:
    """Riordina ``altra`` sui ts di ``candele``; ValueError se manca una barra.

    ``None`` vuol dire "usa le candele dei segnali". Un ts duplicato in ``altra``
    e' un errore nei dati (quale barra varrebbe?) e solleva ValueError.
    """
    if altra is None:
        return list(candele)
    per_ts: Dict[int, Candela] = {}
    for c in altra:
        if c.ts in per_ts:
            raise ValueError(f"serie {nome}: ts duplicato {c.ts}")
        per_ts[c.ts] = c
    allineata: List[Candela] = []
    for c in candele:
        if c.ts not in per_ts:
            raise ValueError(f"serie {nome}: manca la barra con ts={c.ts}")
        allineata.append(per_ts[c.ts])
    return allineata


def ricuci_serie(
    serie_prima: Sequence[Candela],
    serie_dopo: Sequence[Candela],
    fattore_prezzo: float,
    fattore_quantita: float,
) -> Tuple[List[Candela], int]:
    """Unisce due serie (cambio di contratto) in una sola e dichiara la cucitura.

    I prezzi della prima serie si moltiplicano per ``fattore_prezzo`` e i volumi
    per ``fattore_quantita`` cosi' da essere nelle unita' della seconda (es.
    contratto "1000SHIB" -> "SHIB": fattore_prezzo 1/1000, fattore_quantita 1000).
    Le barre della prima serie che si sovrappongono alla seconda si scartano.
    Restituisce (candele, ts_cucitura) dove ts_cucitura e' la prima barra della
    seconda serie. Un eventuale buco tra le due serie resta un buco: non si
    inventano barre.

    ValueError se la seconda serie e' vuota o se comincia prima (o insieme) della
    prima: vorrebbe dire scartare TUTTA la prima serie, quasi certamente perche'
    chi chiama le ha passate invertite.
    """
    if not serie_dopo:
        raise ValueError("serie_dopo e' vuota: niente da ricucire")
    ts_cucitura = serie_dopo[0].ts
    if serie_prima and ts_cucitura <= serie_prima[0].ts:
        raise ValueError(
            f"serie_dopo comincia a {ts_cucitura}, non dopo l'inizio di serie_prima ({serie_prima[0].ts}): serie invertite?"
        )
    riscalate = [
        Candela(
            ts=c.ts,
            open=c.open * fattore_prezzo,
            high=c.high * fattore_prezzo,
            low=c.low * fattore_prezzo,
            close=c.close * fattore_prezzo,
            volume=c.volume * fattore_quantita,
            close_ts=c.close_ts,
        )
        for c in serie_prima
        if c.ts < ts_cucitura
    ]
    return riscalate + list(serie_dopo), ts_cucitura


# ---------------------------------------------------------------------------
# Uscite dentro la barra
# ---------------------------------------------------------------------------


def prezzo_riempimento_stop(stop: float, lato: int, stop_gap: bool, barra_last: Candela) -> float:
    """Prezzo di riferimento a cui si riempie uno stop scattato sulla serie stop.

    Lo stop e' un ordine a mercato che parte quando la serie stop tocca ``stop``
    e si esegue sul last. Il riferimento e' lo stop stesso (o l'apertura del
    last, se non migliore dello stop, quando la serie stop apre gia' oltre lo
    stop: il gap e' PEGGIORE per il trade), ma sempre dentro l'intervallo
    low-high del last nella barra: un prezzo che il last non ha mai fatto non
    e' eseguibile. Esempio: long con stop 95, last con open 100 e low 99.5,
    serie stop che apre a 90: lo stop scatta, il riempimento e' 99.5 (il
    peggior prezzo del last), non 90.
    """
    if lato == 1:
        candidato = min(barra_last.open, stop) if stop_gap else stop
        return min(max(candidato, barra_last.low), barra_last.high)
    candidato = max(barra_last.open, stop) if stop_gap else stop
    return max(min(candidato, barra_last.high), barra_last.low)


def valuta_uscita_in_barra(
    pos: Posizione,
    barra_segnali: Candela,
    barra_stop: Candela,
    barra_mark: Candela,
    parametri: Parametri,
) -> Optional[Tuple[Esito, float]]:
    """Dice se e come la posizione si chiude dentro la barra: (esito, prezzo di riferimento).

    Regole, nell'ordine in cui si applicano:
    * stop SCATTA sulla serie stop ma si RIEMPIE sul last (serie dei segnali),
      target sulla serie dei segnali, liquidazione sul mark;
    * gap in apertura: l'apertura e' il primo prezzo della barra, quindi
      l'ordine e' noto e ``riempimento_intrabarra`` NON si applica. Se il mark
      apre gia' oltre la liquidazione -> liquidazione al prezzo di liquidazione
      (in isolated la perdita non supera il margine); altrimenti se la serie
      stop apre gia' oltre lo stop -> stop all'apertura; altrimenti se il last
      apre gia' oltre il target -> target all'apertura;
    * liquidazione e stop toccati dentro la barra: vince chi e' piu' vicino
      all'entrata (il prezzo deve passare prima da li');
    * stop e target toccati dentro la barra: decide ``riempimento_intrabarra``.

    Esempi a mano (long entrato a 100, stop 95, target 110, liquidazione 51):
    * barra open 90 / high 112: stop a 90 anche con "target_prima" (a 90 la
      posizione e' gia' chiusa quando il prezzo arriva a 110);
    * barra open 115 / low 94: target a 115 anche con "stop_prima";
    * mark open 30: liquidazione a 51, perdita 49 per unita' e non 70.
    """
    lato = segno(pos.direzione)

    # Stop: per un long scatta se il low della serie stop scende a stop; per uno short se l'high sale a stop.
    stop_toccato = (barra_stop.low <= pos.stop) if lato == 1 else (barra_stop.high >= pos.stop)
    stop_gap = (barra_stop.open <= pos.stop) if lato == 1 else (barra_stop.open >= pos.stop)
    prezzo_stop = prezzo_riempimento_stop(pos.stop, lato, stop_gap, barra_segnali)

    target_toccato = False
    target_gap = False
    prezzo_target = 0.0
    if pos.target is not None:
        target_toccato = (barra_segnali.high >= pos.target) if lato == 1 else (barra_segnali.low <= pos.target)
        target_gap = (barra_segnali.open >= pos.target) if lato == 1 else (barra_segnali.open <= pos.target)
        prezzo_target = barra_segnali.open if target_gap else pos.target

    liq = pos.prezzo_liquidazione
    liq_toccata = (liq > 0 and barra_mark.low <= liq) if lato == 1 else (barra_mark.high >= liq)
    liq_gap = (liq > 0 and barra_mark.open <= liq) if lato == 1 else (barra_mark.open >= liq)

    # Eventi gia' veri all'apertura: ordine noto, niente ambiguita' da risolvere.
    if liq_gap:
        return "liquidazione", liq
    if stop_gap:
        return "stop", prezzo_stop
    if target_gap:
        return "target", prezzo_target

    if liq_toccata:
        stop_piu_vicino = abs(pos.entrata - pos.stop) <= abs(pos.entrata - liq)
        if not (stop_toccato and stop_piu_vicino):
            return "liquidazione", liq

    if stop_toccato and target_toccato:
        if parametri.riempimento_intrabarra == "stop_prima":
            return "stop", prezzo_stop
        if parametri.riempimento_intrabarra == "target_prima":
            return "target", prezzo_target
        raise ValueError(f"riempimento_intrabarra sconosciuto: {parametri.riempimento_intrabarra!r}")
    if stop_toccato:
        return "stop", prezzo_stop
    if target_toccato:
        return "target", prezzo_target
    return None


# ---------------------------------------------------------------------------
# Motore
# ---------------------------------------------------------------------------


def _apri_posizione(
    segnale: Segnale, barra: Candela, capitale: float, parametri: Parametri
) -> Optional[Posizione]:
    """Apre la posizione all'apertura della barra; None se il segnale non e' valido.

    Non valido: stop dalla parte sbagliata rispetto all'entrata vera (o uguale),
    target dalla parte sbagliata, prezzi non positivi. Il capitale esaurito
    NON e' un segnale non valido: lo decide il chiamante, con il suo contatore.
    """
    if segnale.stop <= 0 or barra.open <= 0:
        return None
    lato = segno(segnale.direzione)
    entrata = prezzo_riempimento_entrata(barra.open, segnale.direzione, parametri)
    if lato * (entrata - segnale.stop) <= 0 or lato * (barra.open - segnale.stop) <= 0:
        return None
    if segnale.target is not None and lato * (segnale.target - entrata) <= 0:
        return None

    quantita, ridotto = calcola_quantita(capitale, barra.open, entrata, segnale.stop, parametri)
    notional = quantita * entrata
    leva = leva_effettiva(notional, capitale, parametri)
    leva_liq = leva_per_liquidazione(notional, capitale, parametri)
    liq = prezzo_liquidazione(entrata, segnale.direzione, leva_liq, parametri)
    return Posizione(
        direzione=segnale.direzione,
        entrata=entrata,
        stop=segnale.stop,
        target=segnale.target,
        quantita=quantita,
        ts_entrata=barra.ts,
        entrata_riferimento=barra.open,
        rischio_iniziale=quantita * abs(entrata - segnale.stop),
        leva_effettiva=leva,
        prezzo_liquidazione=liq,
        ridotto=ridotto,
        violazione_liquidazione=violazione_margine(entrata, segnale.stop, liq, parametri),
        capitale_ingresso=capitale,
    )


def _chiudi_posizione(pos: Posizione, prezzo_riferimento: float, ts_uscita: int, esito: Esito, parametri: Parametri) -> Trade:
    """Chiude la posizione al prezzo di riferimento (peggiorato dallo slippage) e fa i conti."""
    lato = segno(pos.direzione)
    uscita = prezzo_riempimento_uscita(prezzo_riferimento, pos.direzione, parametri)
    pnl_lordo = lato * pos.quantita * (prezzo_riferimento - pos.entrata_riferimento)
    commissioni = parametri.commissione_per_lato * parametri.moltiplicatore_costi * pos.quantita * (pos.entrata + uscita)
    slippage_costo = pos.quantita * (abs(pos.entrata - pos.entrata_riferimento) + abs(uscita - prezzo_riferimento))
    pnl = pnl_lordo - commissioni - slippage_costo - pos.funding_pagato
    return Trade(
        direzione=pos.direzione,
        ts_entrata=pos.ts_entrata,
        ts_uscita=ts_uscita,
        entrata=pos.entrata,
        uscita=uscita,
        stop=pos.stop,
        target=pos.target,
        quantita=pos.quantita,
        ridotto=pos.ridotto,
        violazione_liquidazione=pos.violazione_liquidazione,
        esito=esito,
        pnl=pnl,
        pnl_lordo=pnl_lordo,
        commissioni=commissioni,
        slippage_costo=slippage_costo,
        funding_pagato=pos.funding_pagato,
        rischio_iniziale=pos.rischio_iniziale,
        r=pnl / pos.rischio_iniziale if pos.rischio_iniziale > 0 else 0.0,
        leva_effettiva=pos.leva_effettiva,
        prezzo_liquidazione=pos.prezzo_liquidazione,
        pnl_pct=pnl / pos.capitale_ingresso if pos.capitale_ingresso > 0 else 0.0,
    )


def _settlement_fino_alla_barra(
    funding: Sequence[Tuple[int, float]], da_ts_escluso: int, barra: Candela
) -> List[Tuple[int, float]]:
    """Settlement con da_ts_escluso < ts <= barra.close_ts (``funding`` ordinato per ts).

    ``da_ts_escluso`` e' il close_ts della barra precedente (o barra.ts - 1 per
    la prima barra): cosi' un settlement caduto in un buco tra due barre viene
    attribuito alla prima barra dopo il buco invece di sparire.
    """
    inizio = bisect_right(funding, (da_ts_escluso, math.inf))
    fine = bisect_right(funding, (barra.close_ts, math.inf))
    return list(funding[inizio:fine])


def _verifica_serie(candele: Sequence[Candela]) -> int:
    """ValueError se i ts non sono strettamente crescenti; restituisce il numero di buchi.

    Un buco e' una coppia di barre consecutive con ``ts`` della seconda oltre
    ``close_ts + 1`` della prima (chiusura inclusa, stile Binance).
    """
    buchi = 0
    for prima, dopo in zip(candele, candele[1:]):
        if dopo.ts <= prima.ts:
            raise ValueError(f"serie dei segnali: ts non crescente o duplicato a {dopo.ts}")
        if dopo.ts > prima.close_ts + 1:
            buchi += 1
    return buchi


def esegui(
    candele: List[Candela],
    candele_stop: Optional[List[Candela]],
    candele_mark: Optional[List[Candela]],
    funding: List[Tuple[int, float]],
    strategia: Strategia,
    parametri: Parametri,
) -> Risultato:
    """Esegue la strategia barra per barra e restituisce i trade e la curva del capitale.

    Ordine dentro ogni barra ``i``:
    1. all'apertura: chiusura per "chiudi" pendente (con il funding dei
       settlement caduti nel buco prima della barra, e di quello esattamente
       all'apertura solo se costo), poi ingresso pendente;
    2. durante la barra: stop / target / liquidazione sulle rispettive serie;
    3. funding dei settlement con posizione aperta: quelli nel buco prima della
       barra per intero (la posizione era certamente aperta); quello nello
       stesso istante dell'ingresso solo se costo; quelli dentro la barra per
       intero se la posizione resta aperta, solo se costo se si e' chiusa in
       questa barra per stop/target/liquidazione;
    4. alla chiusura: la strategia vede ``candele[:i+1]`` e decide;
    5. all'ultima barra: la posizione ancora aperta si chiude al close ("fine_dati").

    ValueError se i ts non sono strettamente crescenti o se una serie stop/mark
    non e' allineata; i buchi si accettano e si contano.
    """
    if not candele:
        return Risultato([], [], parametri.capitale_iniziale, parametri.capitale_iniziale)
    if parametri.ritardo_barre < 0:
        raise ValueError("ritardo_barre deve essere >= 0")

    n_buchi = _verifica_serie(candele)
    serie_stop = allinea_serie(candele, candele_stop, "stop")
    serie_mark = allinea_serie(candele, candele_mark, "mark")
    funding_ordinato = sorted(funding)

    capitale = parametri.capitale_iniziale
    trades: List[Trade] = []
    curva: List[Tuple[int, float]] = [(candele[0].ts, capitale)]
    pos: Optional[Posizione] = None
    ingresso_pendente: Optional[Tuple[Segnale, int]] = None  # (segnale, indice barra di ingresso)
    chiusura_pendente = False
    n_non_validi = 0
    n_senza_barra = 0
    n_capitale_esaurito = 0
    n_funding_in_buco = 0
    n = len(candele)
    visibili: List[Candela] = []  # le barre chiuse fin qui: la sola cosa che la strategia puo' raggiungere

    def registra(trade: Trade) -> None:
        nonlocal capitale
        capitale += trade.pnl
        trades.append(trade)
        curva.append((trade.ts_uscita, capitale))

    def applica_funding(posizione: Posizione, i: int, settlement: Sequence[Tuple[int, float]], chiusa_in_barra: bool) -> None:
        """Addebita alla posizione i settlement secondo le regole del passo 3."""
        nonlocal n_funding_in_buco
        barra = candele[i]
        for t, tasso in settlement:
            if t < posizione.ts_entrata:
                continue  # la posizione non esisteva ancora (settlement nel buco prima dell'ingresso)
            in_buco = t < barra.ts
            # Nel buco l'ultimo mark disponibile e' il close della barra precedente.
            mark = serie_mark[i - 1].close if in_buco else serie_mark[i].open
            f = funding_di_un_settlement(posizione.direzione, posizione.quantita, mark, tasso, parametri)
            ambiguo = (t == posizione.ts_entrata) or (chiusa_in_barra and not in_buco)
            if ambiguo and f <= 0:
                continue
            if in_buco:
                n_funding_in_buco += 1
            posizione.funding_pagato += f

    for i in range(n):
        barra = candele[i]
        da_ts_escluso = candele[i - 1].close_ts if i > 0 else barra.ts - 1
        settlement = _settlement_fino_alla_barra(funding_ordinato, da_ts_escluso, barra)

        # 1. apertura della barra: prima le chiusure da segnale, poi gli ingressi
        if pos is not None and chiusura_pendente:
            # Settlement nel buco prima della barra: posizione certamente aperta, si contano.
            # Settlement esattamente all'apertura: momento ambiguo, si conta solo se costo.
            applica_funding(pos, i, [(t, r) for t, r in settlement if t <= barra.ts], chiusa_in_barra=True)
            registra(_chiudi_posizione(pos, barra.open, barra.ts, "segnale", parametri))
            pos = None
        chiusura_pendente = False

        if pos is None and ingresso_pendente is not None and ingresso_pendente[1] == i:
            segnale, _ = ingresso_pendente
            ingresso_pendente = None
            if capitale <= 0:
                n_capitale_esaurito += 1
            else:
                pos = _apri_posizione(segnale, barra, capitale, parametri)
                if pos is None:
                    n_non_validi += 1

        # 2. durante la barra: stop, target, liquidazione
        if pos is not None:
            esito_prezzo = valuta_uscita_in_barra(pos, barra, serie_stop[i], serie_mark[i], parametri)
            # 3. funding dei settlement caduti nel buco prima della barra o nella barra
            applica_funding(pos, i, settlement, chiusa_in_barra=esito_prezzo is not None)
            if esito_prezzo is not None:
                esito, prezzo = esito_prezzo
                # Si sa solo che e' successo entro la chiusura della barra: ts_uscita = close_ts.
                registra(_chiudi_posizione(pos, prezzo, barra.close_ts, esito, parametri))
                pos = None

        # 5. fine dei dati: chiusura forzata all'ultimo close
        if i == n - 1 and pos is not None:
            registra(_chiudi_posizione(pos, barra.close, barra.close_ts, "fine_dati", parametri))
            pos = None
            break

        # 4. chiusura della barra: la strategia vede solo barre chiuse
        visibili.append(barra)
        decisione = strategia(StoriaChiusa(visibili, i + 1), pos)
        if isinstance(decisione, Segnale):
            if pos is None and ingresso_pendente is None:
                indice = i + 1 + parametri.ritardo_barre
                if indice < n:
                    ingresso_pendente = (decisione, indice)
                else:
                    n_senza_barra += 1
        elif decisione == "chiudi":
            if pos is not None:
                chiusura_pendente = True
        elif decisione is not None:
            raise ValueError(f"la strategia ha restituito un valore sconosciuto: {decisione!r}")

    if curva[-1][0] != candele[-1].close_ts:
        curva.append((candele[-1].close_ts, capitale))
    return Risultato(
        trades=trades,
        curva_capitale=curva,
        capitale_iniziale=parametri.capitale_iniziale,
        capitale_finale=capitale,
        n_segnali_non_validi=n_non_validi,
        n_segnali_senza_barra=n_senza_barra,
        n_segnali_capitale_esaurito=n_capitale_esaurito,
        n_buchi_dati=n_buchi,
        n_funding_in_buco=n_funding_in_buco,
    )


# ---------------------------------------------------------------------------
# Stima dei trade (sezione 8, dalla versione 4.4)
# ---------------------------------------------------------------------------


def _strategia_nuova(crea_strategia: Callable[..., Strategia], chi: str, attesa: str, *argomenti) -> Strategia:
    """Chiama la fabbrica (con ``argomenti``) e controlla che restituisca una strategia."""
    try:
        strategia = crea_strategia(*argomenti)
    except TypeError as e:
        raise TypeError(
            f"{chi} vuole {attesa}: ogni esecuzione del motore usa un'istanza nuova "
            f"della strategia (sezione 7). Errore: {e}"
        ) from e
    if not callable(strategia):
        raise TypeError(f"{chi}: la fabbrica deve restituire una strategia (una funzione di storia e posizione)")
    return strategia


def conta_trade(
    candele: List[Candela],
    crea_strategia: Callable[[], Strategia],
    fine_costruzione_ts: int,
    parametri: Parametri,
    candele_stop: Optional[List[Candela]] = None,
    candele_mark: Optional[List[Candela]] = None,
    funding: Sequence[Tuple[int, float]] = (),
) -> Dict[str, int]:
    """La stima dei trade del protocollo, uguale per tutte le campagne (sezione 8).

    Fino alla 4.3 ogni campagna stimava a modo suo (occupazione dichiarata,
    distanza fra segnali, durata misurata con entrate casuali) e la stessa idea
    poteva passare o no il minimo secondo la regola scelta. Dalla 4.4 la stima
    E' il numero di trade del test: questo motore, con le regole complete della
    variante, gli stessi ``parametri`` (costi), lo stesso funding e le stesse
    serie del test, sui soli dati di costruzione. Non serve indovinare quanto
    dura una posizione: la decide l'uscita della variante, barra per barra.

    Restituisce SOLO conteggi, mai risultati: niente R, pnl, profit factor ne'
    esiti delle uscite (quanti stop e quanti target direbbero gia' come va la
    variante). Si chiama una volta sola per variante, sulle regole esatte che si
    registrano, e il numero va nel log (sezione 8): contare regole che non si
    registrano e' vietato, perche' con un'uscita solo a stop il numero di trade
    dice gia' se dopo gli ingressi il prezzo va a favore.

    ``crea_strategia`` e' la FUNZIONE che crea la strategia (senza argomenti):
    ogni esecuzione del motore usa un'istanza nuova, cosi' lo stato interno di
    una strategia (indicatori aggiornati barra per barra, contatori) non passa
    dal conteggio al test vero. Passare la strategia gia' creata alza TypeError.

    ``fine_costruzione_ts`` (ms) e' obbligatorio: la fine del periodo di
    costruzione scritta nel log in Fase 0. Una candela che chiude dopo alza
    ValueError, cosi' la stima non tocca mai il periodo di validazione.

    Ritorna: ``trade`` (totale), ``long``, ``short``, ``segnali_non_validi``
    (stop o target dalla parte sbagliata), ``segnali_senza_barra`` (segnali
    troppo vicini alla fine dei dati) e ``barre`` (candele usate).
    """
    strategia = _strategia_nuova(crea_strategia, "conta_trade",
                                 "crea() SENZA argomenti, la funzione che crea la strategia della variante")
    if not candele:
        return {"trade": 0, "long": 0, "short": 0, "segnali_non_validi": 0, "segnali_senza_barra": 0, "barre": 0}
    for nome, serie in (("candele", candele), ("candele_stop", candele_stop), ("candele_mark", candele_mark)):
        oltre = [c for c in (serie or []) if c.close_ts > int(fine_costruzione_ts)]
        if oltre:
            raise ValueError(
                f"conta_trade: {len(oltre)} {nome} chiudono dopo la fine della costruzione "
                f"({fine_costruzione_ts}); la stima si fa solo sui dati di costruzione"
            )
    funding_costruzione = [(t, r) for t, r in funding if t <= int(fine_costruzione_ts)]
    risultato = esegui(candele, candele_stop, candele_mark, funding_costruzione, strategia, parametri)
    return {
        "trade": len(risultato.trades),
        "long": sum(1 for t in risultato.trades if t.direzione == "long"),
        "short": sum(1 for t in risultato.trades if t.direzione == "short"),
        "segnali_non_validi": risultato.n_segnali_non_validi,
        "segnali_senza_barra": risultato.n_segnali_senza_barra,
        "barre": len(candele),
    }


def durata_media_barre(trades: Sequence[Trade], ms_per_barra: int) -> int:
    """Durata media dei trade in barre, arrotondata all'intero piu' vicino (almeno 1).

    E' la distanza minima fra gli ingressi casuali della baseline (b) (sezione 8).
    La durata di un trade e' (ts_uscita - ts_entrata) / ms_per_barra: un'uscita
    dentro una barra ha ts_uscita alla chiusura della barra (sezione 7, «Tempi»).
    """
    if not trades:
        raise ValueError("servono trade per calcolare la durata media")
    if ms_per_barra <= 0:
        raise ValueError("ms_per_barra deve essere positivo")
    media = sum((t.ts_uscita - t.ts_entrata) / ms_per_barra for t in trades) / len(trades)
    return max(1, int(math.floor(media + 0.5)))


def simula_baseline_casuale(
    candele: List[Candela],
    crea_strategia_casuale: Callable[[frozenset], Strategia],
    n_trade: int,
    durata_media: int,
    parametri: Parametri,
    candele_stop: Optional[List[Candela]] = None,
    candele_mark: Optional[List[Candela]] = None,
    funding: Sequence[Tuple[int, float]] = (),
    barre_vietate: Sequence[Tuple[int, int]] = (),
    n_simulazioni: int = 200,
    primo_seme: int = 0,
    rifiuta_poche_simulazioni: bool = True,
) -> Dict[str, object]:
    """La baseline (b) della sezione 8, eseguita sempre allo stesso modo.

    Per ogni seme da ``primo_seme`` a ``primo_seme + n_simulazioni - 1`` (di regola
    0..199, ``parametri.yaml``):
    1. ``statistica.entrate_casuali`` sceglie ``n_trade`` barre (il numero di trade
       del candidato nel periodo), distanti almeno ``durata_media`` barre
       (``durata_media_barre`` dei trade del candidato), fuori dalle
       ``barre_vietate`` (riscaldamento degli indicatori della variante, periodi
       esclusi in Fase 0; in validazione anche tutte le barre di costruzione) e
       dall'ultima barra, che si esclude da sola (un segnale li' non entra piu');
    2. ``crea_strategia_casuale(ingressi)`` crea la strategia casuale: alla
       CHIUSURA di ogni barra il cui indice e' in ``ingressi``, se non ha una
       posizione, emette il Segnale della variante (stessa direzione, stesso
       modo di calcolare stop e target), e poi esce con l'uscita della variante;
    3. il motore la esegue una posizione alla volta, con gli stessi ``parametri``,
       funding e serie del candidato.

    Siccome le durate variano, una simulazione puo' avere qualche trade in meno di
    ``n_trade`` (un ingresso che cade mentre la posizione e' aperta si salta): e'
    voluto e si riporta (``trade_per_simulazione``). Le simulazioni senza alcun
    trade non entrano nella media e si contano (``simulazioni_vuote``); se ne
    restano meno di 2, ValueError. Se ``entrate_casuali`` non trova ``n_trade``
    ingressi, alza ValueError: la variante e' non valutabile contro la (b).

    Gli ingressi casuali si estraggono solo fra le barre in cui il segnale
    della variante e' valido: le altre vanno in ``barre_vietate``
    (``barre_vietate_segnale_non_valido``). I segnali scartati comunque dal
    motore si contano per simulazione e si riportano.

    Ritorna il dizionario di ``statistica.baseline_casuale`` sugli R medi (tipo
    "b", media, errore_standard, errore_minimo_candidato, n_simulazioni,
    percentile_90, valori) piu' ``trade_per_simulazione``, ``simulazioni_vuote``,
    ``segnali_non_validi_per_simulazione`` e ``segnali_senza_barra_per_simulazione``.
    Si passa cosi' com'e' a ``statistica.contro_baseline``.

    Campagna di gruppo (``campagne/GRUPPO/regole.md``, sezione 5, punto 4, e
    sezione 13). Il dizionario ha in piu' la chiave ``r_medio_per_seme``: una
    lista lunga ``n_simulazioni``, nell'ordine dei semi (posizione s = seme
    ``primo_seme + s``), con l'R medio di ogni simulazione e ``None`` per quelle
    senza trade. E' la m_j(s) della sezione 5, punto 4: il gruppo combina le
    simulazioni con lo STESSO s su monete diverse, quindi gli serve sapere quale
    seme ha dato quale R medio, anche quando qualche simulazione e' vuota (le
    chiavi ``valori`` e ``trade_per_simulazione`` saltano le vuote e perdono la
    posizione). Per le campagne singole non cambia nient'altro.

    ``rifiuta_poche_simulazioni`` (predefinito True, il comportamento di sempre):
    con meno di 2 simulazioni con trade alza ValueError. Con False (uso di
    gruppo) non alza: restituisce comunque ``r_medio_per_seme`` e i conteggi
    (``trade_per_simulazione``, ``simulazioni_vuote``,
    ``segnali_non_validi_per_simulazione``, ``segnali_senza_barra_per_simulazione``),
    SENZA le chiavi di ``statistica.baseline_casuale`` (niente ``tipo``: il
    dizionario non si puo' passare a ``contro_baseline`` per sbaglio). Decidere
    se la variante e' non valutabile («una moneta con n_j > 0 ha meno di 2
    simulazioni con trade») spetta a ``statistica.baseline_casuale_di_gruppo``.
    Con 2 simulazioni con trade o piu' il risultato e' identico a quello del
    predefinito. Gli ingressi che non entrano (``entrate_casuali``) alzano
    ValueError anche con False.
    """
    from research.src import statistica  # import qui: statistica non dipende dal motore

    if n_trade < 1:
        raise ValueError("n_trade deve essere almeno 1")
    # un segnale alla chiusura dell'ultima barra non ha una barra in cui entrare
    vietate = list(barre_vietate) + [(len(candele) - 1, len(candele))]
    r_medi: List[float] = []
    r_medio_per_seme: List[Optional[float]] = []
    trade_per_sim: List[int] = []
    non_validi: List[int] = []
    senza_barra: List[int] = []
    vuote = 0
    semi = list(range(primo_seme, primo_seme + n_simulazioni))
    tutti_gli_ingressi = statistica.entrate_casuali_per_semi(len(candele), n_trade, durata_media, semi, vietate)
    for ingressi_lista in tutti_gli_ingressi:
        ingressi = frozenset(ingressi_lista)
        strategia = _strategia_nuova(
            crea_strategia_casuale, "simula_baseline_casuale",
            "crea_casuale(ingressi): una funzione con UN argomento (l'insieme degli indici delle barre di "
            "segnale) che restituisce la strategia CASUALE: alla chiusura di quelle barre il segnale della "
            "variante, poi la sua uscita", ingressi)
        ris = esegui(candele, candele_stop, candele_mark, list(funding), strategia, parametri)
        non_validi.append(ris.n_segnali_non_validi)
        senza_barra.append(ris.n_segnali_senza_barra)
        if not ris.trades:
            vuote += 1
            r_medio_per_seme.append(None)
            continue
        r_medio = sum(t.r for t in ris.trades) / len(ris.trades)
        r_medi.append(r_medio)
        r_medio_per_seme.append(r_medio)
        trade_per_sim.append(len(ris.trades))
    if len(r_medi) < 2:
        if rifiuta_poche_simulazioni:
            raise ValueError(f"simula_baseline_casuale: solo {len(r_medi)} simulazioni con trade su {n_simulazioni}")
        return {
            "r_medio_per_seme": r_medio_per_seme,
            "trade_per_simulazione": trade_per_sim,
            "simulazioni_vuote": vuote,
            "segnali_non_validi_per_simulazione": non_validi,
            "segnali_senza_barra_per_simulazione": senza_barra,
        }
    base = statistica.baseline_casuale(r_medi)
    base["trade_per_simulazione"] = trade_per_sim
    base["simulazioni_vuote"] = vuote
    base["segnali_non_validi_per_simulazione"] = non_validi
    base["segnali_senza_barra_per_simulazione"] = senza_barra
    base["r_medio_per_seme"] = r_medio_per_seme
    return base


def barre_vietate_segnale_non_valido(
    candele: List[Candela],
    crea_segnale: Callable[[], Callable[[Sequence[Candela]], Optional[Segnale]]],
    parametri: Parametri,
) -> List[Tuple[int, int]]:
    """Le barre in cui il segnale della variante NON sarebbe valido, da vietare alla (b).

    ``crea_segnale()`` restituisce la funzione che, date le barre chiuse fino a
    una barra, calcola il Segnale che la variante emetterebbe li' (direzione,
    stop, target) SENZA la condizione d'ingresso, oppure None se non si puo'
    calcolare (per esempio durante il riscaldamento degli indicatori). E' lo
    stesso calcolo che la strategia casuale usa agli ingressi.

    Una barra i e' vietata se il segnale e' None, se e' l'ultima barra, o se il
    motore lo scarterebbe entrando all'apertura della barra i + 1 (stop o target
    dalla parte sbagliata dell'entrata con lo slippage). Senza questo, gli
    ingressi casuali della (b) cadrebbero anche dove il segnale non e' valido, il
    motore li scarterebbe in silenzio e la (b) terrebbe solo le barre in cui
    stop e target sono validi: meta' della condizione d'ingresso dentro la
    baseline (revisione del 7 ott 2026). Le barre vietate si passano a
    ``simula_baseline_casuale`` in ``barre_vietate`` (insieme al resto), e la
    loro quota si riporta. Ritorna intervalli (inizio incluso, fine esclusa).
    """
    segnale_alla_barra = crea_segnale()
    if not callable(segnale_alla_barra):
        raise TypeError("crea_segnale() deve restituire una funzione delle barre chiuse")
    vietate: List[Tuple[int, int]] = []
    visibili: List[Candela] = []
    n = len(candele)
    for i, barra in enumerate(candele):
        visibili.append(barra)
        valida = False
        if i < n - 1:
            segnale = segnale_alla_barra(StoriaChiusa(visibili, i + 1))
            if isinstance(segnale, Segnale):
                valida = _apri_posizione(segnale, candele[i + 1], parametri.capitale_iniziale, parametri) is not None
        if not valida:
            if vietate and vietate[-1][1] == i:
                vietate[-1] = (vietate[-1][0], i + 1)
            else:
                vietate.append((i, i + 1))
    return vietate


# ---------------------------------------------------------------------------
# Campagna di gruppo: le strategie sfasate (campagne/GRUPPO/regole.md, sezioni 5, 9, 13)
# ---------------------------------------------------------------------------


class TradeSfasato(NamedTuple):
    """Un trade di una strategia sfasata, con solo quello che serve al gruppo.

    ``campagne/GRUPPO/regole.md``, sezione 5, punto 5 (pavimento delle sfasate:
    l'R di ogni trade) e sezione 9, punti 3-4 (sfasate del vault: profit factor e
    risultato totale in USDT, R medio, anno d'uscita). ``r`` e' l'R del trade,
    ``pnl`` il risultato netto in USDT sul capitale della moneta, ``ts_entrata``
    e ``ts_uscita`` in ms come in ``Trade``. E' una tupla: occupa poco quando le
    sfasate sono 200 (o 1.000 nel vault) per 80 monete, si passa fra processi
    con pickle, e ``metriche_di_gruppo`` la legge come un ``Trade``.
    """

    ts_entrata: int
    ts_uscita: int
    r: float
    pnl: float


def simula_sfasamento_comune(
    candele: List[Candela],
    crea_strategia_casuale: Callable[[frozenset], Strategia],
    ts_segnali: Sequence[int],
    finestra_unione: Tuple[int, int],
    finestra_moneta: Tuple[int, int],
    ms_per_barra: int,
    sfasamenti: Sequence[int],
    parametri: Parametri,
    candele_stop: Optional[List[Candela]] = None,
    candele_mark: Optional[List[Candela]] = None,
    funding: Sequence[Tuple[int, float]] = (),
    barre_vietate: Sequence[Tuple[int, int]] = (),
) -> Dict[str, object]:
    """Le strategie sfasate di UNA moneta (``campagne/GRUPPO/regole.md``, sezione 5, punto 5, e sezione 9, punti 3-4).

    La strategia sfasata s prende gli ingressi del candidato (le barre di
    segnale) su tutte le monete e li sposta tutti dello stesso intervallo d_s,
    in cerchio sulla finestra del periodo; emette il segnale della variante ed
    esce con la sua uscita: e' la strategia casuale della (b) con gli ingressi
    spostati. Questa funzione fa il lavoro di una moneta, cosi' il gruppo lo
    distribuisce una moneta per processo (sezione 13): lo spostamento e' lo
    stesso su tutte le monete perche' dipende solo dall'istante, dalla finestra
    unione e da d_s, mai dalla moneta.

    Argomenti:

    * ``candele``, ``candele_stop``, ``candele_mark``, ``funding``,
      ``parametri``: la serie della moneta e i suoi parametri, gli stessi del
      test e della (b) (in validazione la serie dall'inizio della costruzione,
      sezione 1, punto 5). ``candele`` e' il last gia' allineato al mark
      (``dati.carica_serie_allineate``).
    * ``crea_strategia_casuale``: la funzione della moneta che, dato l'insieme
      degli indici delle barre di segnale, crea la strategia casuale (la stessa
      della (b), ``simula_baseline_casuale``). Si chiama con un'istanza NUOVA per
      ogni s (sezione 7 del protocollo).
    * ``ts_segnali``: gli istanti (``ts``, cioe' l'apertura) delle barre di
      SEGNALE dei trade del candidato su questa moneta nel periodo (la barra
      alla cui chiusura la variante ha emesso il segnale, non quella
      d'ingresso). Ognuno deve essere una barra della serie e cadere sulla
      griglia del calendario della finestra unione; ValueError se no o se due
      coincidono. Un istante prima o dopo la finestra unione (per esempio la
      barra di segnale del 2023-01-16 di un trade entrato il 2023-01-17, primo
      giorno di validazione, o del 2023-01-14 se il 15 e il 16 mancano nella
      serie) si sposta con la stessa aritmetica del cerchio e si conta in
      ``segnali_fuori_dalla_finestra_unione``. Due istanti con lo stesso resto
      modulo L (distanti un multiplo di L barre: succede solo con un segnale fuori
      dalla finestra unione, per esempio con un buco o con il ritardo subito prima
      dell'inizio della validazione) cadono nella stessa barra per ogni d_s: il
      motore ci apre una posizione sola, e l'altro ingresso si salta e si conta in
      ``posizione_aperta`` (cade mentre la posizione del primo e' aperta), con il
      numero a parte in ``segnali_coincidenti`` (regole.md, sezione 2, punto 9: i
      buchi non rendono mai non valutabile una variante).
    * ``finestra_unione``: (inizio, fine) in ms della finestra del periodo,
      l'unione delle finestre delle monete con trade del candidato (sezione 5,
      punto 5; nel vault, il vault: sezione 9, punto 3). ``fine`` e' l'ultimo
      millisecondo INCLUSO, come ``close_ts`` e ``fine_costruzione_ts`` (per il
      2023-01-16: 23:59:59.999). L = (fine + 1 - inizio) / ``ms_per_barra``,
      contato sul calendario, buchi compresi; se la divisione non e' esatta
      ValueError (di solito vuol dire una fine passata esclusa).
    * ``finestra_moneta``: (inizio, fine incluso) in ms della finestra della
      moneta: in costruzione dal suo primo giorno di dati al 2023-01-16, in
      validazione dal 2023-01-17 al 2023-12-31, nel vault fino al suo ultimo
      giorno con candele (sezione 10, punto 1.2).
    * ``ms_per_barra``: la durata della barra del timeframe della variante.
    * ``sfasamenti``: i d_s in barre, nell'ordine di s (``statistica.griglia_sfasamenti``).
    * ``barre_vietate``: intervalli di indici (inizio incluso, fine esclusa)
      vietati agli ingressi, gli stessi della (b) della moneta (riscaldamento,
      mesi sotto la liquidita', segnale non valido, in validazione le barre
      prima del 2023-01-17: sezione 2, punto 7, e sezione 5, punto 4). Come
      nella (b) e' vietata anche l'ultima barra della serie (un segnale li' non
      ha una barra in cui entrare).

    Per ogni s, per ogni istante di segnale: posizione p = (istante - inizio
    della finestra unione) / ``ms_per_barra``; nuova posizione (p + d_s) modulo
    L; nuovo istante = inizio + nuova posizione x ``ms_per_barra``. L'ingresso
    spostato si salta, e si conta, nell'ordine (sezione 5, punto 5):

    * ``fuori_finestra``: la barra spostata non sta tutta nella finestra della moneta;
    * ``buco``: nessuna barra della serie della moneta ha quel ``ts``;
    * ``vietata``: la barra e' in ``barre_vietate`` (o e' l'ultima);
    * ``posizione_aperta``: il motore non lo trasforma in un trade perche'
      cade mentre la posizione e' aperta (o mentre un ingresso e' gia' in
      attesa, con ``ritardo_barre`` > 0, o nella stessa barra di un altro
      ingresso coincidente). Si conta per differenza: ingressi spostati arrivati
      fin qui - trade - segnali non validi - segnali senza barra - segnali con
      capitale esaurito (questi tre si riportano a parte). Se la differenza viene
      negativa la strategia casuale ha emesso segnali fuori dagli ingressi:
      ValueError.

    Nessun numero casuale: stessi argomenti, stesso risultato.

    Ritorna un dizionario con ``L``, ``n_segnali``,
    ``segnali_fuori_dalla_finestra_unione``, ``segnali_coincidenti`` (quanti
    istanti hanno lo stesso resto modulo L di un istante prima di loro),
    ``sfasamenti`` (i d_s usati, come interi), ``saltati_totali`` (i quattro
    conteggi sommati su tutti gli s) e ``per_sfasamento``: una lista nell'ordine
    di ``sfasamenti``, con per ogni s un dizionario ``d`` (d_s), ``trade`` (lista
    di ``TradeSfasato`` nell'ordine del motore, cioe' d'uscita), ``ingressi``
    (quanti ingressi spostati hanno passato i primi tre controlli: ``ingressi`` +
    ``fuori_finestra`` + ``buco`` + ``vietata`` = ``n_segnali``), ``coincidenti``
    (quanti di questi cadono nella barra di un altro), ``saltati`` ({motivo:
    numero}, i quattro motivi sopra), ``segnali_non_validi``,
    ``segnali_senza_barra`` e ``capitale_esaurito``. M'(s) e n'(s) del gruppo si
    ottengono dai ``trade`` dello stesso s su tutte le monete con
    ``statistica.riassunto_sfasate`` (per moneta) e ``statistica.medie_sfasate``
    (fra le monete), e vanno a ``statistica.pavimento_sfasamento``.
    """
    ms = operator.index(ms_per_barra)
    if ms <= 0:
        raise ValueError("ms_per_barra deve essere positivo")
    inizio_u, fine_u = (operator.index(x) for x in finestra_unione)
    durata = fine_u + 1 - inizio_u
    if durata <= 0 or durata % ms != 0:
        raise ValueError(
            f"finestra unione ({inizio_u}, {fine_u}): la durata (fine inclusa) di {durata} ms non e' un multiplo "
            f"positivo della barra ({ms} ms); la fine va passata INCLUSA (es. 23:59:59.999)"
        )
    L = durata // ms
    inizio_m, fine_m = (operator.index(x) for x in finestra_moneta)
    if fine_m < inizio_m:
        raise ValueError(f"finestra della moneta vuota: ({inizio_m}, {fine_m})")

    _verifica_serie(candele)  # ts crescenti, prima di costruire l'indice per ts
    indice_per_ts = {c.ts: i for i, c in enumerate(candele)}
    n = len(candele)

    posizioni: List[int] = []
    fuori_unione = 0
    for valore in ts_segnali:
        ts = operator.index(valore)
        if ts not in indice_per_ts:
            raise ValueError(f"l'istante di segnale {ts} non e' una barra della serie della moneta")
        scarto = ts - inizio_u
        if scarto % ms != 0:
            raise ValueError(f"l'istante di segnale {ts} non cade sulla griglia del calendario della finestra unione")
        p = scarto // ms
        if not 0 <= p < L:
            fuori_unione += 1
        posizioni.append(p)
    if len(set(posizioni)) != len(posizioni):
        raise ValueError("due istanti di segnale coincidono")
    # lo spostamento e' una rotazione sui resti modulo L: due istanti con lo stesso resto cadono insieme
    coincidenti = len(posizioni) - len({p % L for p in posizioni})

    vietata = bytearray(n)
    # come nella (b): un segnale alla chiusura dell'ultima barra non ha una barra in cui entrare
    for inizio, fine in list(barre_vietate) + [(n - 1, n)]:
        lo, hi = max(0, int(inizio)), min(n, int(fine))
        if hi > lo:
            vietata[lo:hi] = b"\x01" * (hi - lo)

    funding_lista = list(funding)
    sfas = [operator.index(d) for d in sfasamenti]
    per_sfasamento: List[Dict[str, object]] = []
    totali = {"fuori_finestra": 0, "buco": 0, "vietata": 0, "posizione_aperta": 0}
    for d in sfas:
        saltati = {"fuori_finestra": 0, "buco": 0, "vietata": 0, "posizione_aperta": 0}
        arrivati = 0  # ingressi spostati che passano i primi tre controlli, coincidenti compresi
        ingressi = set()
        for p in posizioni:
            ts = inizio_u + ((p + d) % L) * ms
            if ts < inizio_m or ts + ms - 1 > fine_m:
                saltati["fuori_finestra"] += 1
                continue
            i = indice_per_ts.get(ts)
            if i is None:
                saltati["buco"] += 1
                continue
            if vietata[i]:
                saltati["vietata"] += 1
                continue
            arrivati += 1
            ingressi.add(i)
        strategia = _strategia_nuova(
            crea_strategia_casuale, "simula_sfasamento_comune",
            "crea_casuale(ingressi): una funzione con UN argomento (l'insieme degli indici delle barre di "
            "segnale) che restituisce la strategia CASUALE della (b): alla chiusura di quelle barre il segnale "
            "della variante, poi la sua uscita", frozenset(ingressi))
        ris = esegui(candele, candele_stop, candele_mark, funding_lista, strategia, parametri)
        saltati["posizione_aperta"] = (arrivati - len(ris.trades) - ris.n_segnali_non_validi
                                       - ris.n_segnali_senza_barra - ris.n_segnali_capitale_esaurito)
        if len(ingressi) - len(ris.trades) - ris.n_segnali_non_validi - ris.n_segnali_senza_barra \
                - ris.n_segnali_capitale_esaurito < 0:
            raise ValueError(
                f"sfasamento {d}: {len(ris.trades)} trade e {ris.n_segnali_non_validi} segnali non validi da "
                f"{len(ingressi)} ingressi: la strategia casuale emette segnali fuori dagli ingressi"
            )
        for motivo, quanti in saltati.items():
            totali[motivo] += quanti
        per_sfasamento.append({
            "d": d,
            "trade": [TradeSfasato(t.ts_entrata, t.ts_uscita, t.r, t.pnl) for t in ris.trades],
            "ingressi": arrivati,
            "coincidenti": arrivati - len(ingressi),
            "saltati": saltati,
            "segnali_non_validi": ris.n_segnali_non_validi,
            "segnali_senza_barra": ris.n_segnali_senza_barra,
            "capitale_esaurito": ris.n_segnali_capitale_esaurito,
        })
    return {
        "L": L,
        "n_segnali": len(posizioni),
        "segnali_fuori_dalla_finestra_unione": fuori_unione,
        "segnali_coincidenti": coincidenti,
        "sfasamenti": sfas,
        "saltati_totali": totali,
        "per_sfasamento": per_sfasamento,
    }


# ---------------------------------------------------------------------------
# Metriche e riferimenti
# ---------------------------------------------------------------------------


def drawdown_massimo(curva: Sequence[Tuple[int, float]]) -> float:
    """Massima caduta dal picco sulla curva del capitale, come frazione del picco."""
    picco = -math.inf
    peggiore = 0.0
    for _, capitale in curva:
        picco = max(picco, capitale)
        if picco > 0:
            peggiore = max(peggiore, (picco - capitale) / picco)
    return peggiore


def _anno(ts_ms: int) -> int:
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).year


def rendimento_per_anno(trades: Sequence[Trade], capitale_iniziale: float) -> Dict[int, float]:
    """Rendimento di ogni anno = pnl dei trade chiusi nell'anno / capitale a inizio anno."""
    capitale = capitale_iniziale
    inizio: Dict[int, float] = {}
    fine: Dict[int, float] = {}
    for t in sorted(trades, key=lambda t: t.ts_uscita):
        anno = _anno(t.ts_uscita)
        if anno not in inizio:
            inizio[anno] = capitale
        capitale += t.pnl
        fine[anno] = capitale
    return {a: (fine[a] - inizio[a]) / inizio[a] if inizio[a] > 0 else 0.0 for a in inizio}


def _stat_gruppo(trades: Sequence[Trade]) -> Dict[str, float]:
    n = len(trades)
    return {
        "n": n,
        "r_medio": sum(t.r for t in trades) / n if n else 0.0,
        "pnl": sum(t.pnl for t in trades),
    }


def calcola_metriche(risultato: Risultato) -> Dict[str, object]:
    """Riassunto del risultato. profit_factor e' inf se non ci sono perdite."""
    trades = risultato.trades
    n = len(trades)
    vinti = [t for t in trades if t.pnl > 0]
    persi = [t for t in trades if t.pnl < 0]
    somma_vinti = sum(t.pnl for t in vinti)
    somma_persi = -sum(t.pnl for t in persi)
    if somma_persi > 0:
        profit_factor = somma_vinti / somma_persi
    else:
        profit_factor = math.inf if somma_vinti > 0 else 0.0
    pnl_totale = sum(t.pnl for t in trades)
    cap0 = risultato.capitale_iniziale
    return {
        "n_trade": n,
        "vinti": len(vinti),
        "profit_factor": profit_factor,
        "win_rate": len(vinti) / n if n else 0.0,
        "r_medio": sum(t.r for t in trades) / n if n else 0.0,
        "pnl_totale": pnl_totale,
        "rendimento_totale": pnl_totale / cap0 if cap0 > 0 else 0.0,
        "drawdown_max": drawdown_massimo(risultato.curva_capitale),
        "rendimento_per_anno": rendimento_per_anno(trades, cap0),
        "n_ridotti": sum(1 for t in trades if t.ridotto),
        "n_violazioni_liquidazione": sum(1 for t in trades if t.violazione_liquidazione),
        "n_segnali_non_validi": risultato.n_segnali_non_validi,
        "n_segnali_senza_barra": risultato.n_segnali_senza_barra,
        "n_segnali_capitale_esaurito": risultato.n_segnali_capitale_esaurito,
        "n_buchi_dati": risultato.n_buchi_dati,
        "n_funding_in_buco": risultato.n_funding_in_buco,
        "costi_totali": sum(t.commissioni + t.slippage_costo + t.funding_pagato for t in trades),
        "funding_totale": sum(t.funding_pagato for t in trades),
        "per_direzione": {
            "long": _stat_gruppo([t for t in trades if t.direzione == "long"]),
            "short": _stat_gruppo([t for t in trades if t.direzione == "short"]),
        },
        "esiti": {e: sum(1 for t in trades if t.esito == e) for e in ("stop", "target", "segnale", "liquidazione", "fine_dati")},
    }


def buy_and_hold(candele: Sequence[Candela], parametri: Parametri, direzione: Direzione = "long") -> float:
    """Rendimento (frazione) del comprare al primo open e vendere all'ultimo close.

    Una unita' di contratto, leva 1: rendimento = pnl / prezzo di entrata vero,
    con commissioni sui due lati e slippage sui due lati. "short" e' l'opposto.
    """
    if not candele:
        return 0.0
    entrata = prezzo_riempimento_entrata(candele[0].open, direzione, parametri)
    uscita = prezzo_riempimento_uscita(candele[-1].close, direzione, parametri)
    commissioni = parametri.commissione_per_lato * parametri.moltiplicatore_costi * (entrata + uscita)
    pnl = segno(direzione) * (uscita - entrata) - commissioni
    return pnl / entrata


# ---------------------------------------------------------------------------
# Campagna di gruppo: metriche dei trade sommati (campagne/GRUPPO/regole.md, sezioni 8, 9, 13)
# ---------------------------------------------------------------------------


def _campo(trade: object, nome: str):
    """Il campo ``nome`` di un trade: attributo (``Trade``, ``TradeSfasato``) o chiave (dizionario da JSON).

    Serve a ``metriche_di_gruppo`` e ``posizioni_aperte_insieme`` (``campagne/GRUPPO/regole.md``,
    sezione 13), che ricevono i trade del candidato, delle sfasate o riletti dai file di ``trade/``.
    """
    if isinstance(trade, MappingABC):
        return trade[nome]
    return getattr(trade, nome)


def metriche_di_gruppo(
    trade_per_moneta: Mapping[str, Sequence[object]],
    n_monete_nel_periodo: int,
    capitale_per_moneta: float,
    trade_migliori_tolti: int = 30,
) -> Dict[str, object]:
    """Le metriche dei trade sommati di tutte le monete (``campagne/GRUPPO/regole.md``, sezione 9, punto 2, e sezione 8, punto 1).

    ``trade_per_moneta`` e' {simbolo: trade della moneta}, ogni moneta con il suo
    capitale iniziale ``capitale_per_moneta`` (1.000 USDT, ``parametri.yaml``,
    sezione 2, punto 8). I trade possono essere ``Trade`` del motore,
    ``TradeSfasato`` delle sfasate o dizionari letti dal JSON: servono ``r``,
    ``pnl``, ``ts_entrata`` e ``ts_uscita``. Le chiavi di ``criterio_vault``
    (``profit_factor``, ``n_trade``, ``rendimento_totale``, ``r_medio``) ci
    sono tutte: giudicano il candidato (sezione 9, punto 2). Le sfasate del vault
    hanno le stesse quattro chiavi, con le stesse regole, da
    ``metriche_di_gruppo_da_somme`` (sezione 9, punto 4).

    Ordine fisso dei trade sommati (sezione 5, punto 1): per istante d'uscita,
    poi per simbolo, poi per istante d'entrata; tutte le somme si fanno in
    quell'ordine, quindi l'esito non cambia con l'ordine delle monete in
    ``trade_per_moneta``. Con una moneta sola i numeri sono quelli di
    ``calcola_metriche`` (stesso ordine, stesse somme).

    * ``profit_factor``: somma dei pnl positivi / somma dei valori assoluti dei
      pnl negativi, su tutti i trade di tutte le monete (sezione 9, punto 2.1);
      senza perdite inf se c'e' un guadagno, 0 senza guadagni (come ``calcola_metriche``);
    * ``n_trade``: i trade sommati (punto 2.2);
    * ``pnl_totale``: la somma dei pnl in USDT (il «risultato totale» del punto 2.3);
    * ``rendimento_totale`` = ``pnl_totale`` / ``capitale_totale``, con
      ``capitale_totale`` = ``capitale_per_moneta`` x ``n_monete_nel_periodo``.
      DICHIARATO: ``n_monete_nel_periodo`` e' il numero delle monete con almeno
      una barra nel periodo giudicato, con o senza trade (lo sa chi chiama: i
      trade non lo dicono). Il punto 2.3 guarda solo il segno, che non dipende
      dal denominatore; il numero serve solo a riportarlo. ValueError se e'
      minore delle monete con trade;
    * ``r_medio``: la media semplice degli R di tutti i trade (0 senza trade,
      come ``calcola_metriche``);
    * ``r_medio_per_anno``: {anno d'uscita UTC: R medio dei trade usciti nell'anno};
    * ``r_medio_senza_<k>_migliori`` (k = ``trade_migliori_tolti``, 30 per il
      gruppo: ``parametri.yaml``, ``gruppo.fase4.trade_migliori_tolti``; sezione
      6, punto 2.5): l'R medio senza i k trade con l'R piu' alto; None se non
      resta nessun trade;
    * ``drawdown_max``: la caduta massima dal picco, come frazione del picco,
      sulla curva del capitale del gruppo = ``capitale_totale`` + pnl sommati in
      ordine d'uscita (``drawdown_massimo``, positiva come in
      ``calcola_metriche``). I trade che escono nello stesso istante, su monete
      diverse, entrano nella curva insieme, in un punto solo: in quell'istante
      non c'e' un prima e un dopo. ``drawdown_max_usdt`` e' la stessa caduta in USDT;
    * ``monete_con_trade``, ``monete_nel_periodo``, ``capitale_totale``;
    * ``per_moneta``: {simbolo: {``n_trade``, ``r_medio``}} per le monete con trade.
    """
    k = operator.index(trade_migliori_tolti)
    if k < 0:
        raise ValueError("trade_migliori_tolti non puo' essere negativo")
    righe: List[Tuple[int, str, int, float, float]] = []  # (ts_uscita, simbolo, ts_entrata, r, pnl)
    for simbolo in sorted(trade_per_moneta):
        for t in trade_per_moneta[simbolo]:
            righe.append((int(_campo(t, "ts_uscita")), str(simbolo), int(_campo(t, "ts_entrata")),
                          float(_campo(t, "r")), float(_campo(t, "pnl"))))
    righe.sort(key=lambda riga: riga[:3])
    monete_con_trade = sorted({riga[1] for riga in righe})
    n_monete = operator.index(n_monete_nel_periodo)
    if n_monete < len(monete_con_trade):
        raise ValueError(f"n_monete_nel_periodo = {n_monete}, ma le monete con trade sono {len(monete_con_trade)}")
    capitale_totale = float(capitale_per_moneta) * n_monete

    n = len(righe)
    r_valori = [riga[3] for riga in righe]
    pnl_valori = [riga[4] for riga in righe]
    somma_vinti = sum(p for p in pnl_valori if p > 0)
    somma_persi = -sum(p for p in pnl_valori if p < 0)
    if somma_persi > 0:
        profit_factor = somma_vinti / somma_persi
    else:
        profit_factor = math.inf if somma_vinti > 0 else 0.0
    pnl_totale = sum(pnl_valori)

    per_anno: Dict[int, List[float]] = {}
    for riga in righe:
        per_anno.setdefault(_anno(riga[0]), []).append(riga[3])
    restanti = sorted(r_valori, reverse=True)[k:]

    # curva del capitale del gruppo: un punto per istante d'uscita
    curva: List[Tuple[int, float]] = [(righe[0][0] if righe else 0, capitale_totale)]
    capitale = capitale_totale
    j = 0
    while j < n:
        istante = righe[j][0]
        somma_istante = 0.0
        while j < n and righe[j][0] == istante:
            somma_istante += righe[j][4]
            j += 1
        capitale += somma_istante
        curva.append((istante, capitale))
    picco = -math.inf
    caduta_usdt = 0.0
    for _, valore in curva:
        picco = max(picco, valore)
        caduta_usdt = max(caduta_usdt, picco - valore)

    per_moneta: Dict[str, Dict[str, object]] = {}
    for simbolo in monete_con_trade:
        r_moneta = [riga[3] for riga in righe if riga[1] == simbolo]
        per_moneta[simbolo] = {"n_trade": len(r_moneta), "r_medio": sum(r_moneta) / len(r_moneta)}

    return {
        "profit_factor": profit_factor,
        "n_trade": n,
        "pnl_totale": pnl_totale,
        "rendimento_totale": pnl_totale / capitale_totale if capitale_totale > 0 else 0.0,
        "r_medio": sum(r_valori) / n if n else 0.0,
        "r_medio_per_anno": {anno: sum(valori) / len(valori) for anno, valori in sorted(per_anno.items())},
        f"r_medio_senza_{k}_migliori": sum(restanti) / len(restanti) if restanti else None,
        "drawdown_max": drawdown_massimo(curva),
        "drawdown_max_usdt": caduta_usdt,
        "monete_con_trade": len(monete_con_trade),
        "monete_nel_periodo": n_monete,
        "capitale_totale": capitale_totale,
        "per_moneta": per_moneta,
    }


def somme_dei_trade(trade: Iterable[object]) -> List[object]:
    """Le quattro somme dei trade di UNA moneta per ``metriche_di_gruppo_da_somme`` (``campagne/GRUPPO/regole.md``, sezione 9, punto 4).

    ``trade``: ``Trade``, ``TradeSfasato`` o dizionari letti dal JSON (servono
    ``r`` e ``pnl``). Ritorna ``[n, somma degli R, somma dei pnl positivi, somma
    dei valori assoluti dei pnl negativi]``, le tre somme con ``math.fsum``
    (esatte e indipendenti dall'ordine dei trade; la somma degli R e' la stessa
    di ``statistica.riassunto_sfasate``). Un pnl nullo non e' ne' un guadagno ne'
    una perdita, come in ``metriche_di_gruppo``. ValueError per un R o un pnl non
    finito.
    """
    r_valori: List[float] = []
    guadagni: List[float] = []
    perdite: List[float] = []
    for t in trade:
        r, pnl = float(_campo(t, "r")), float(_campo(t, "pnl"))
        if not (math.isfinite(r) and math.isfinite(pnl)):
            raise ValueError(f"somme_dei_trade: R ({r!r}) o pnl ({pnl!r}) non finiti")
        r_valori.append(r)
        if pnl > 0:
            guadagni.append(pnl)
        elif pnl < 0:
            perdite.append(-pnl)
    return [len(r_valori), math.fsum(r_valori), math.fsum(guadagni), math.fsum(perdite)]


def metriche_di_gruppo_da_somme(
    somme_per_moneta: Mapping[str, Sequence[object]],
    n_monete_nel_periodo: int,
    capitale_per_moneta: float,
) -> Dict[str, object]:
    """Le quattro chiavi di ``statistica.criterio_vault`` dalle somme per moneta, con le regole di ``metriche_di_gruppo`` (``campagne/GRUPPO/regole.md``, sezione 9, punto 4).

    Serve alle sfasate del vault: per ogni s bastano, per ogni moneta, i quattro
    numeri di ``somme_dei_trade`` (numero dei trade, somma degli R, somma dei
    guadagni e somma delle perdite in USDT) invece dei trade, cosi' il pezzo di
    una moneta sta nel file di avanzamento (circa 1.000 x 4 numeri). ``somme_per_moneta``
    e' {simbolo: [n, somma_r, somma_guadagni, somma_perdite]}; una moneta con n = 0
    non conta fra le monete con trade.

    * ``n_trade``: la somma degli n;
    * ``profit_factor``: somma dei guadagni / somma delle perdite; senza perdite
      inf se c'e' un guadagno, 0 senza guadagni (come ``metriche_di_gruppo``);
    * ``pnl_totale`` = guadagni - perdite, e ``rendimento_totale`` = ``pnl_totale`` /
      (``capitale_per_moneta`` x ``n_monete_nel_periodo``), 0 con capitale 0;
      ValueError se ``n_monete_nel_periodo`` e' minore delle monete con trade;
    * ``r_medio``: somma degli R / ``n_trade``, 0 senza trade.

    Le somme fra monete sono ``math.fsum``, in ordine dei caratteri dei simboli:
    l'esito non dipende dall'ordine delle monete. Sugli stessi trade
    ``metriche_di_gruppo`` somma in ordine d'uscita con ``sum``: ``n_trade`` e'
    identico, profit factor, rendimento e R medio differiscono solo per gli
    arrotondamenti (test: entro 1e-12 relativo). Ritorna anche ``somma_r``,
    ``somma_guadagni``, ``somma_perdite``, ``monete_con_trade``,
    ``monete_nel_periodo`` e ``capitale_totale``. ValueError per una voce che non
    ha quattro numeri, un n negativo o non intero, una somma non finita, guadagni
    o perdite negativi, o somme diverse da 0 con n = 0.
    """
    quanti: List[int] = []
    somme_r: List[float] = []
    somme_vinti: List[float] = []
    somme_persi: List[float] = []
    monete_con_trade = 0
    for simbolo in sorted(somme_per_moneta):
        voce = list(somme_per_moneta[simbolo])
        if len(voce) != 4:
            raise ValueError(f"{simbolo}: servono [n, somma_r, somma_guadagni, somma_perdite], non {voce!r}")
        n_s, somma_r, vinti, persi = voce
        try:
            intero = None if isinstance(n_s, bool) else operator.index(n_s)
        except TypeError:
            intero = None
        if intero is None or intero < 0:
            raise ValueError(f"{simbolo}: numero di trade non valido ({n_s!r})")
        n_s = intero
        somma_r, vinti, persi = float(somma_r), float(vinti), float(persi)
        if not all(math.isfinite(x) for x in (somma_r, vinti, persi)) or vinti < 0 or persi < 0:
            raise ValueError(f"{simbolo}: somme non valide ({voce!r})")
        if n_s == 0 and (somma_r != 0.0 or vinti != 0.0 or persi != 0.0):
            raise ValueError(f"{simbolo}: somme diverse da 0 senza trade ({voce!r})")
        if n_s:
            monete_con_trade += 1
        quanti.append(n_s)
        somme_r.append(somma_r)
        somme_vinti.append(vinti)
        somme_persi.append(persi)
    n_monete = operator.index(n_monete_nel_periodo)
    if n_monete < monete_con_trade:
        raise ValueError(f"n_monete_nel_periodo = {n_monete}, ma le monete con trade sono {monete_con_trade}")
    capitale_totale = float(capitale_per_moneta) * n_monete
    n = sum(quanti)
    somma_r = math.fsum(somme_r)
    somma_vinti = math.fsum(somme_vinti)
    somma_persi = math.fsum(somme_persi)
    if somma_persi > 0:
        profit_factor = somma_vinti / somma_persi
    else:
        profit_factor = math.inf if somma_vinti > 0 else 0.0
    pnl_totale = somma_vinti - somma_persi
    return {
        "profit_factor": profit_factor,
        "n_trade": n,
        "pnl_totale": pnl_totale,
        "rendimento_totale": pnl_totale / capitale_totale if capitale_totale > 0 else 0.0,
        "r_medio": somma_r / n if n else 0.0,
        "somma_r": somma_r,
        "somma_guadagni": somma_vinti,
        "somma_perdite": somma_persi,
        "monete_con_trade": monete_con_trade,
        "monete_nel_periodo": n_monete,
        "capitale_totale": capitale_totale,
    }


def posizioni_aperte_insieme(trade: Iterable[object]) -> Dict[str, int]:
    """Il massimo di posizioni aperte nello stesso istante, per direzione (``campagne/GRUPPO/regole.md``, sezione 8, punto 2, e sezione 10, punto 3).

    ``trade`` sono i trade sommati di tutte le monete, in una lista sola
    (``Trade`` o dizionari con ``direzione``, ``ts_entrata``, ``ts_uscita``).
    Una posizione e' aperta da ``ts_entrata`` compreso a ``ts_uscita`` escluso:
    nello stesso istante le uscite vengono prima degli ingressi, come nel
    motore («all'apertura: prima le chiusure da segnale, poi gli ingressi»).
    Cosi' una posizione chiusa all'apertura di una barra e una aperta alla
    stessa apertura non contano come aperte insieme. Serve alla consegna e al
    paper: il bot tiene poche posizioni insieme (``config/regole_dimensione.md``).

    Ritorna {``long``: massimo dei long, ``short``: massimo degli short,
    ``totale``: massimo delle due direzioni insieme}. ValueError se un trade
    esce prima di entrare o ha una direzione sconosciuta.
    """
    eventi: List[Tuple[int, int, str]] = []  # (istante, 0 = uscita / 1 = ingresso, direzione)
    for t in trade:
        direzione = _campo(t, "direzione")
        if direzione not in ("long", "short"):
            raise ValueError(f"direzione sconosciuta: {direzione!r}")
        entrata, uscita = int(_campo(t, "ts_entrata")), int(_campo(t, "ts_uscita"))
        if uscita < entrata:
            raise ValueError(f"un trade esce ({uscita}) prima di entrare ({entrata})")
        eventi.append((entrata, 1, direzione))
        eventi.append((uscita, 0, direzione))
    eventi.sort()
    aperte = {"long": 0, "short": 0}
    massimo = {"long": 0, "short": 0, "totale": 0}
    for _, tipo, direzione in eventi:
        aperte[direzione] += 1 if tipo == 1 else -1
        massimo[direzione] = max(massimo[direzione], aperte[direzione])
        massimo["totale"] = max(massimo["totale"], aperte["long"] + aperte["short"])
    return massimo
