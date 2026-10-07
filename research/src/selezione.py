"""Passo 1 del protocollo: la selezione delle monete di campagna.

SOLO PER IL COORDINAMENTO. Qui vivono le funzioni PURE della selezione (filtri,
ordinamento, fasce di slippage, conteggio della sopravvivenza) e le poche
funzioni di rete che il Passo 1 ammette come eccezione (sezione 4, regola 1):
la lista dei contratti con le date di listing e di delisting, e l'elenco dei
file mensili di un simbolo nell'archivio (solo NOMI di file, mai dati del
vault). Una sessione di campagna non deve importare questo modulo: rivela
quali contratti esistono oggi e quando sono morti.

La regola della selezione (sezione 3.3 e Passo 1 del protocollo), applicata
«come se fossimo al 31 dicembre 2023»:
  1. base: i contratti perpetui in USDT con dati nell'archivio mensile, compresi
     i delistati;
  2. storia minima: listing prima del 2022-01-01 (``storia_minima_anni`` = 2) E
     dati nell'archivio che cominciano prima del 2022-01-01: il protocollo
     chiede due anni di DATI, non solo di quotazione;
  3. dati fino alla fine dell'in-sample: l'ultimo file mensile e' almeno
     2023-12 e, quando le candele del 2023 sono state lette, l'ultimo giorno
     presente e' il 2023-12-31 (una moneta morta prima non ha ne' validazione
     intera ne' vault: il protocollo ammette i delistati DOPO il 2023);
  4. liquidita': volume medio giornaliero in USDT (quote volume) nel 2023 almeno
     ``liquidita_minima_usdt_giorno``;
  5. ordine per volume 2023 decrescente, le prime ``numero_monete_campagna``
     sono le monete di campagna; le altre sono le future monete di verifica.

Due cose NON sono filtri ma segnalazioni per lo STOP del Passo 1:
  * la copertura del 2023 (giorni di dati presenti): ne' il protocollo ne'
    parametri.yaml (congelato) fissano un minimo di giorni, quindi il codice
    non esclude nessuno per questo; le idonee sotto ``SOGLIA_COPERTURA_2023``
    giorni si elencano perche' l'utente le veda;
  * le sospette ridenominazioni: il protocollo chiede di ricucire i cambi di
    contratto e, nel dubbio, di chiedere all'utente. Qui non si cuce nulla da
    soli: si elencano i contratti spariti durante il 2022-2023 (meta' vecchia
    di un cambio di nome, oppure un delisting vero) e quelli nati nel 2022-2023
    (possibile meta' nuova), e il coordinamento li mostra allo STOP.
    ``serie_collegata`` resta uguale al simbolo finche' l'utente non decide.

Date di listing e di delisting, e da dove vengono, restano nel CSV del branch
di coordinamento: la scheda della moneta NON le riporta. La scheda dice solo il
primo mese di dati, che e' l'inizio dell'in-sample (sezione 3.1) ed e' uguale
per una moneta viva e per una delistata con gli stessi dati al 2023-12-31. (Fino
al 7 ott la scheda portava anche la data di listing: per una delistata coincideva
col primo mese di dati, per una viva quasi mai, e bastava confrontarle per
sapere se la moneta e' ancora negoziata.)
"""
from __future__ import annotations

import csv
import math
import re
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from research.src import dati

#: solo i perpetui in USDT: niente contratti trimestrali (``BTCUSDT_210326``),
#: niente USDC/USD1/BTC come valuta di quotazione
RE_PERPETUO_USDT = re.compile(r"^[A-Z0-9]+USDT$")
#: nome di un file mensile di candele: ``BTCUSDT-1d-2023-01.zip``
RE_FILE_MESE = re.compile(r"-(\d{4})-(\d{2})\.zip$")
#: le fasce di slippage per lato (parametri.yaml, ``slippage_per_lato``):
#: (volume medio giornaliero minimo in USDT, slippage per lato)
FASCE_SLIPPAGE: Tuple[Tuple[float, float], ...] = (
    (1_000_000_000, 0.0001),
    (200_000_000, 0.0002),
    (50_000_000, 0.0005),
    (20_000_000, 0.0010),
)
INIZIO_FINESTRA_VOLUME = date(2023, 1, 1)
FINE_FINESTRA_VOLUME = date(2023, 12, 31)
#: listing (e primo mese di dati) prima di questa data = almeno due anni di
#: storia prima del 2024
LIMITE_LISTING = date(2022, 1, 1)
LIQUIDITA_MINIMA = 20_000_000.0
NUMERO_MONETE_CAMPAGNA = 20
#: sotto questi giorni di dati nel 2023 la copertura si SEGNALA allo STOP, non
#: si esclude: il protocollo e parametri.yaml (congelato) non fissano un minimo
#: di giorni e il codice non puo' inventarne uno. 350 distingue qualche buco
#: breve (sospensioni) da mesi interi mancanti: e' una soglia di attenzione
SOGLIA_COPERTURA_2023 = 350
#: un contratto sparito o nato fra questa data e la fine del 2023 potrebbe
#: essere la meta' vecchia o nuova di un cambio di nome (es. «1000x», o un
#: simbolo nuovo dopo una migrazione): si segnala allo STOP, non si decide qui
INIZIO_PERIODO_SOSPETTO = date(2022, 1, 1)
#: la colonna del volume in valuta di quotazione nel CSV delle candele
COLONNA_QUOTE_VOLUME = 7
COLONNA_OPEN_TIME = 0

# --------------------------------------------------------------------------- #
# Motivi di esclusione. Ogni motivo e' un testo con un PREFISSO stabile, da     #
# cui si ricava un codice per i conteggi. Si conta per prefisso esatto, non per #
# parola contenuta: «data di listing sconosciuta» contiene «listing» ma non e'  #
# un listing tardivo, e nel bias di sopravvivenza i due casi sono diversi.      #
# --------------------------------------------------------------------------- #
MOTIVO_LISTING_SCONOSCIUTO = "data di listing sconosciuta"
MOTIVO_LISTING = "listing "                     # «listing 2022-03-01, non prima del 2022-01-01»
MOTIVO_PRIMO_MESE_SCONOSCIUTO = "primo mese nell'archivio sconosciuto"
MOTIVO_PRIMO_MESE = "dati nell'archivio che cominciano il "
MOTIVO_FINE_DATI_MESE = "dati che finiscono prima del 2023-12"
MOTIVO_FINE_DATI_GIORNO = "dati che finiscono il "   # «... il 2023-12-17 (prima del 2023-12-31)»
MOTIVO_ERRORE_SCARICO = "errore nello scarico del 2023: "   # lo scrive passo1, prima di ``valuta``
MOTIVO_NESSUN_VOLUME = "nessun volume nel 2023"
MOTIVO_VOLUME_NON_LEGGIBILE = "volume 2023 non leggibile"
MOTIVO_VOLUME_SOTTO = "volume medio 2023 "       # «volume medio 2023 5,000,000 USDT sotto 20,000,000»

#: (codice, prefisso). Nessun prefisso e' l'inizio di un altro con codice
#: diverso, quindi l'ordine non conta.
CODICI_MOTIVO: Tuple[Tuple[str, str], ...] = (
    ("listing_sconosciuto", MOTIVO_LISTING_SCONOSCIUTO),
    ("listing", MOTIVO_LISTING),
    ("primo_mese_sconosciuto", MOTIVO_PRIMO_MESE_SCONOSCIUTO),
    ("primo_mese", MOTIVO_PRIMO_MESE),
    ("fine_dati", MOTIVO_FINE_DATI_MESE),
    ("fine_dati_giorno", MOTIVO_FINE_DATI_GIORNO),
    ("errore_scarico", MOTIVO_ERRORE_SCARICO),
    ("nessun_volume", MOTIVO_NESSUN_VOLUME),
    ("volume_non_leggibile", MOTIVO_VOLUME_NON_LEGGIBILE),
    ("volume", MOTIVO_VOLUME_SOTTO),
)
CODICE_ALTRO = "altro"


def codice_motivo(motivo: str) -> str:
    """Il codice stabile di un motivo di esclusione (``CODICE_ALTRO`` se non e' uno dei nostri)."""
    for codice, prefisso in CODICI_MOTIVO:
        if motivo.startswith(prefisso):
            return codice
    return CODICE_ALTRO


def codici_motivi(motivi: Iterable[str]) -> Set[str]:
    return {codice_motivo(m) for m in motivi}


@dataclass
class Candidata:
    """Una moneta valutata dal Passo 1, con tutto cio' che serve a decidere."""
    simbolo: str
    negoziata_oggi: bool
    listing: Optional[date]           # onboardDate oggi, altrimenti primo mese dell'archivio
    #: "exchangeInfo" | "archivio" | "sconosciuta". Solo nel CSV del branch di
    #: coordinamento, MAI nella scheda: «archivio» vuol dire «assente da
    #: exchangeInfo oggi», cioe' delistata
    listing_da: str
    primo_mese: Optional[date]
    ultimo_mese: Optional[date]       # fine del mese dell'ultimo file; per i delistati e' il delisting
    volume_medio_2023: Optional[float] = None
    giorni_2023: int = 0
    #: l'ultimo giorno con una candela nel 2023: passo1 lo riempie insieme al
    #: volume; None finche' le candele non sono state lette
    ultimo_giorno_2023: Optional[date] = None
    #: la serie a cui il contratto si ricuce (Passo 1, punto 1): uguale al
    #: simbolo finche' l'utente non decide un collegamento allo STOP
    serie_collegata: str = ""
    motivi_esclusione: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.serie_collegata:
            self.serie_collegata = self.simbolo

    @property
    def delisting(self) -> Optional[date]:
        return None if self.negoziata_oggi else self.ultimo_mese

    @property
    def anni_storia(self) -> Optional[float]:
        if self.listing is None:
            return None
        return round((date(2024, 1, 1) - self.listing).days / 365.25, 2)

    @property
    def fascia_slippage(self) -> Optional[float]:
        return fascia_slippage(self.volume_medio_2023)


# --------------------------------------------------------------------------- #
# Funzioni pure                                                                #
# --------------------------------------------------------------------------- #
def fascia_slippage(volume_medio: Optional[float]) -> Optional[float]:
    """Lo slippage per lato della fascia di volume; None sotto la soglia minima o
    con un volume non leggibile (NaN, infinito)."""
    if volume_medio is None or not math.isfinite(volume_medio):
        return None
    for soglia, slippage in FASCE_SLIPPAGE:
        if volume_medio >= soglia:
            return slippage
    return None


def e_perpetuo_usdt(simbolo: str) -> bool:
    return bool(RE_PERPETUO_USDT.match(simbolo))


def mesi_dai_nomi(chiavi: Iterable[str]) -> List[Tuple[int, int]]:
    """(anno, mese) dei file mensili ``*.zip`` fra le chiavi, ordinati e senza doppioni
    (i ``.CHECKSUM`` e altro si ignorano)."""
    mesi = set()
    for chiave in chiavi:
        trovato = RE_FILE_MESE.search(chiave)
        if trovato:
            mesi.add((int(trovato.group(1)), int(trovato.group(2))))
    return sorted(mesi)


def fine_mese(anno: int, mese: int) -> date:
    if mese == 12:
        return date(anno, 12, 31)
    return date(anno, mese + 1, 1).fromordinal(date(anno, mese + 1, 1).toordinal() - 1)


def primo_e_ultimo_mese(chiavi: Iterable[str]) -> Tuple[Optional[date], Optional[date]]:
    """(primo giorno del primo mese, ultimo giorno dell'ultimo mese) dei file presenti."""
    mesi = mesi_dai_nomi(chiavi)
    if not mesi:
        return None, None
    (a0, m0), (a1, m1) = mesi[0], mesi[-1]
    return date(a0, m0, 1), fine_mese(a1, m1)


def data_da_ms(ms: int) -> date:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date()


def volume_quote_giornaliero(righe: Sequence[Sequence[str]]) -> List[Tuple[int, float]]:
    """(open_time ms, volume in valuta di quotazione) da righe CSV di candele
    giornaliere (``righe_csv_da_zip`` toglie gia' l'intestazione). Una riga
    corrotta si scarta da sola, il resto del file resta."""
    out: List[Tuple[int, float]] = []
    for riga in righe:
        if len(riga) <= COLONNA_QUOTE_VOLUME:
            continue
        try:
            ts = dati.normalizza_ts(riga[COLONNA_OPEN_TIME])
            vol = float(riga[COLONNA_QUOTE_VOLUME])
        except (TypeError, ValueError, OverflowError):
            # OverflowError: ``int(float("inf"))`` in normalizza_ts. Senza
            # catturarlo saltava l'intero file del mese, non la sola riga
            continue
        # ``float("nan")``, ``float("inf")`` e i negativi NON sollevano: una media
        # con un NaN e' NaN (e ``nan < soglia`` e' falso: la moneta passerebbe il
        # filtro), un infinito mette la moneta prima di BTC, un negativo abbassa
        # la media di tutto l'anno. Una riga cosi' e' corrotta: via
        if not math.isfinite(vol) or vol < 0:
            continue
        out.append((ts, vol))
    return out


def volume_medio_nella_finestra(
    giorni: Sequence[Tuple[int, float]],
    inizio: date = INIZIO_FINESTRA_VOLUME,
    fine: date = FINE_FINESTRA_VOLUME,
) -> Tuple[Optional[float], int, Optional[int]]:
    """(media del volume giornaliero in USDT sui giorni presenti nella finestra, numero
    di giorni, open_time in ms della mezzanotte UTC dell'ULTIMO giorno presente).

    Si divide per i giorni PRESENTI, non per 365: un buco di dati non abbassa la
    media; la copertura la dice il secondo valore. Il giorno si riconosce per
    giorno UTC (``ts // MS_GIORNO``), non per timestamp identico: due righe
    dello stesso giorno con millisecondi diversi sono un doppione, non due
    giorni, quindi il numero di giorni non supera mai i giorni della finestra.
    Senza giorni nella finestra: ``(None, 0, None)``."""
    da, a = dati.ms_da_data(inizio), dati.ms_da_data(fine) + dati.MS_GIORNO - 1
    visti: Dict[int, float] = {}
    for ts, vol in giorni:
        if da <= ts <= a:
            visti[ts // dati.MS_GIORNO] = vol      # un doppione sovrascrive, non raddoppia
    if not visti:
        return None, 0, None
    return sum(visti.values()) / len(visti), len(visti), max(visti) * dati.MS_GIORNO


def motivi_prima_del_volume(c: Candidata) -> List[str]:
    """I motivi di esclusione che si conoscono SENZA leggere le candele (storia
    minima su listing e primo mese, fine dei dati al mese): passo1 scarica il
    volume solo per chi non ne ha."""
    motivi: List[str] = []
    if c.listing is None:
        motivi.append(MOTIVO_LISTING_SCONOSCIUTO)
    elif c.listing >= LIMITE_LISTING:
        motivi.append(f"{MOTIVO_LISTING}{c.listing.isoformat()}, non prima del {LIMITE_LISTING.isoformat()}")
    # la storia minima e' sui DATI, non solo sulla quotazione: un contratto quotato
    # nel 2021 ma con il primo file nel 2022 ha meno di due anni di candele
    if c.primo_mese is None:
        motivi.append(MOTIVO_PRIMO_MESE_SCONOSCIUTO)
    elif c.primo_mese >= LIMITE_LISTING:
        motivi.append(f"{MOTIVO_PRIMO_MESE}{c.primo_mese.isoformat()}, non prima del {LIMITE_LISTING.isoformat()}")
    if c.ultimo_mese is None or c.ultimo_mese < FINE_FINESTRA_VOLUME:
        motivi.append(MOTIVO_FINE_DATI_MESE)
    return motivi


def valuta(candidata: Candidata) -> Candidata:
    """Applica i filtri 2-4 e AGGIUNGE i motivi di esclusione a quelli gia' presenti
    (es. «errore nello scarico del 2023: ...» scritto da passo1), senza doppioni:
    chiamarla due volte non cambia nulla. Ritorna la stessa istanza aggiornata.

    La copertura del 2023 (``giorni_2023``) NON e' un motivo: non c'e' nel
    protocollo ne' in parametri.yaml; la segnala ``seleziona``."""
    motivi = list(candidata.motivi_esclusione)

    def aggiungi(m: str) -> None:
        if m not in motivi:
            motivi.append(m)

    for m in motivi_prima_del_volume(candidata):
        aggiungi(m)
    # fine dei dati al GIORNO: l'ultimo giorno presente nel 2023 si conosce solo
    # dopo aver letto le candele (passo1 lo riempie insieme al volume); finche'
    # manca resta il controllo sul mese qui sopra. Una moneta con il file 2023-12
    # ma morta il 17 dicembre non ha un giorno di vault: il protocollo ammette i
    # delistati DOPO il 2023, non durante
    if candidata.ultimo_giorno_2023 is not None and candidata.ultimo_giorno_2023 < FINE_FINESTRA_VOLUME:
        aggiungi(f"{MOTIVO_FINE_DATI_GIORNO}{candidata.ultimo_giorno_2023.isoformat()} "
                 f"(prima del {FINE_FINESTRA_VOLUME.isoformat()})")
    errore_scarico = any(m.startswith(MOTIVO_ERRORE_SCARICO) for m in motivi)
    volume = candidata.volume_medio_2023
    if volume is None:
        # con un errore di scarico «nessun volume» sarebbe falso: il volume non
        # si e' potuto leggere, e il motivo vero c'e' gia'
        if not errore_scarico:
            aggiungi(MOTIVO_NESSUN_VOLUME)
    elif not math.isfinite(volume):
        # non dovrebbe arrivare qui (volume_quote_giornaliero scarta le righe
        # corrotte), ma un NaN passerebbe il confronto con la soglia in silenzio
        aggiungi(MOTIVO_VOLUME_NON_LEGGIBILE)
    elif volume < LIQUIDITA_MINIMA:
        aggiungi(f"{MOTIVO_VOLUME_SOTTO}{volume:,.0f} USDT sotto {LIQUIDITA_MINIMA:,.0f}")
    candidata.motivi_esclusione = motivi
    return candidata


def _inizio_serie(c: Candidata) -> Optional[date]:
    """Quando il contratto e' nato, per quel che se ne sa: il listing, altrimenti il primo mese."""
    return c.listing if c.listing is not None else c.primo_mese


def seleziona(candidate: Sequence[Candidata], n: int = NUMERO_MONETE_CAMPAGNA) -> Dict[str, object]:
    """La selezione finale: idonee ordinate per volume, le prime ``n`` di campagna,
    le altre idonee di verifica (la regola di verifica vera si applica al Passo 6),
    piu' i conteggi per il bias di sopravvivenza e le segnalazioni per lo STOP.

    Un simbolo che compare due volte (per esempio da due liste non fuse) conta
    una volta sola: resta la prima occorrenza.

    Ritorna:
      * ``campagna``, ``altre_idonee``, ``escluse``: liste di ``Candidata``;
      * ``copertura_incompleta``: i simboli idonei con meno di
        ``SOGLIA_COPERTURA_2023`` giorni di dati nel 2023 (segnalazione, non
        esclusione);
      * ``sospette_ridenominazioni``: ``sparite_2022_2023`` (non negoziate oggi
        con l'ultimo mese nel 2022-2023: ridenominazione o delisting durante
        l'in-sample) e ``listate_2022_2023`` (nate nel 2022-2023: possibile
        nuovo nome). Nessuna cucitura si applica qui: il coordinamento le
        elenca allo STOP e chiede;
      * ``conteggi``: ``candidate`` (dopo i doppioni), ``doppioni_scartati``,
        ``idonee``, ``campagna``, ``escluse``, ``idonee_delistate_oggi``,
        ``campagna_delistate_oggi``, ``idonee_con_copertura_incompleta``, le
        sospette, e un ``escluse_per_<codice>`` per ogni motivo. I conteggi per
        motivo SI SOVRAPPONGONO: una moneta esclusa per due motivi conta in
        entrambi, quindi la loro somma puo' superare ``escluse``.
        ``escluse_per_fine_dati`` comprende anche la fine al giorno, che ha
        pure il suo conteggio a parte."""
    uniche: List[Candidata] = []
    visti: Set[str] = set()
    for c in candidate:
        if c.simbolo in visti:
            continue
        visti.add(c.simbolo)
        uniche.append(c)
    valutate = [valuta(c) for c in uniche]
    idonee = sorted((c for c in valutate if not c.motivi_esclusione),
                    key=lambda c: (-(c.volume_medio_2023 or 0.0), c.simbolo))
    campagna = idonee[:n]
    altre_idonee = idonee[n:]
    escluse = [c for c in valutate if c.motivi_esclusione]
    codici = {c.simbolo: codici_motivi(c.motivi_esclusione) for c in escluse}

    def escluse_con(*cercati: str) -> int:
        return sum(1 for c in escluse if codici[c.simbolo] & set(cercati))

    copertura_incompleta = [c.simbolo for c in idonee if c.giorni_2023 < SOGLIA_COPERTURA_2023]
    sparite = sorted(c.simbolo for c in valutate
                     if not c.negoziata_oggi and c.ultimo_mese is not None
                     and INIZIO_PERIODO_SOSPETTO <= c.ultimo_mese <= FINE_FINESTRA_VOLUME)
    listate = sorted(c.simbolo for c in valutate
                     if _inizio_serie(c) is not None
                     and INIZIO_PERIODO_SOSPETTO <= _inizio_serie(c) <= FINE_FINESTRA_VOLUME)
    return {
        "campagna": campagna,
        "altre_idonee": altre_idonee,
        "escluse": escluse,
        "copertura_incompleta": copertura_incompleta,
        "sospette_ridenominazioni": {"sparite_2022_2023": sparite, "listate_2022_2023": listate},
        "conteggi": {
            "candidate": len(valutate),
            "doppioni_scartati": len(candidate) - len(valutate),
            "idonee": len(idonee),
            "campagna": len(campagna),
            "escluse": len(escluse),
            "idonee_delistate_oggi": sum(1 for c in idonee if not c.negoziata_oggi),
            "campagna_delistate_oggi": sum(1 for c in campagna if not c.negoziata_oggi),
            "idonee_con_copertura_incompleta": len(copertura_incompleta),
            "sospette_sparite_2022_2023": len(sparite),
            "sospette_listate_2022_2023": len(listate),
            "escluse_per_listing": escluse_con("listing"),
            "escluse_per_listing_sconosciuto": escluse_con("listing_sconosciuto"),
            "escluse_per_primo_mese": escluse_con("primo_mese"),
            "escluse_per_primo_mese_sconosciuto": escluse_con("primo_mese_sconosciuto"),
            "escluse_per_fine_dati": escluse_con("fine_dati", "fine_dati_giorno"),
            "escluse_per_fine_dati_giorno": escluse_con("fine_dati_giorno"),
            "escluse_per_volume": escluse_con("volume"),
            "escluse_per_volume_non_leggibile": escluse_con("volume_non_leggibile"),
            "escluse_per_errore_scarico": escluse_con("errore_scarico"),
        },
    }


# --------------------------------------------------------------------------- #
# Rete (eccezione del Passo 1, solo coordinamento)                             #
# --------------------------------------------------------------------------- #
def url_indice_file(prefisso: str, marker: Optional[str] = None) -> str:
    """Una pagina dell'indice S3 al livello dei FILE (senza ``delimiter``): elenca
    le chiavi sotto ``prefisso``, 1000 per pagina."""
    parametri = {"prefix": prefisso}
    if marker:
        parametri["marker"] = marker
    return dati.URL_INDICE_ARCHIVIO + "?" + urllib.parse.urlencode(parametri, safe="/")


def prefisso_archivio(simbolo: str, intervallo: Optional[str], tipo: str = "klines") -> str:
    """La cartella dei file mensili di un simbolo nell'archivio. Per ``fundingRate``
    non esiste il livello dell'intervallo (come in ``dati.url_mese``)."""
    if tipo not in dati.TIPI:
        raise ValueError(f"tipo di dato sconosciuto: {tipo!r} (ammessi: {dati.TIPI})")
    if tipo == "fundingRate":
        return f"data/futures/um/monthly/fundingRate/{simbolo}/"
    if not intervallo:
        raise ValueError(f"per il tipo {tipo!r} serve l'intervallo (es. '1d')")
    return f"data/futures/um/monthly/{tipo}/{simbolo}/{intervallo}/"


def _chiavi_della_pagina(contenuto: bytes) -> Tuple[List[str], bool, Optional[str]]:
    radice = ET.fromstring(contenuto)
    chiavi: List[str] = []
    troncata = False
    prossimo: Optional[str] = None
    for elemento in radice:
        nome = elemento.tag.split("}")[-1]
        if nome == "Contents":
            for figlio in elemento:
                if figlio.tag.split("}")[-1] == "Key" and figlio.text and figlio.text.strip():
                    chiavi.append(figlio.text.strip())
        elif nome == "IsTruncated":
            troncata = (elemento.text or "").strip().lower() == "true"
        elif nome == "NextMarker" and elemento.text and elemento.text.strip():
            prossimo = elemento.text.strip()
    # senza ``delimiter`` S3 non manda NextMarker: si riparte dall'ultima chiave
    if troncata and prossimo is None and chiavi:
        prossimo = chiavi[-1]
    return chiavi, troncata, prossimo


def elenca_file_archivio(simbolo: str, intervallo: Optional[str] = "1d", fetch: Optional[dati.Fetch] = None,
                         tipo: str = "klines") -> List[str]:
    """I NOMI dei file mensili di un simbolo nell'archivio (es. ``BTCUSDT-1d-2023-01.zip``),
    compresi quelli del periodo del vault. SOLO coordinamento: e' il modo di
    leggere listing e delisting di un contratto senza scaricare un solo prezzo.

    Mai una lista parziale in silenzio: un elenco a meta' sposterebbe
    ``ultimo_mese`` (filtro «fine dati») o ``primo_mese`` (listing dei
    delistati) senza che nessuno lo sappia. Quindi una pagina troncata senza un
    marker che avanza, o ancora troncata dopo ``MAX_PAGINE_INDICE`` pagine,
    solleva ``RuntimeError``; e si tengono solo le chiavi sotto il prefisso,
    perche' una chiave di un'altra cartella diventerebbe un mese di questo
    simbolo."""
    scarica = fetch or dati.fetch_http
    prefisso = prefisso_archivio(simbolo, intervallo, tipo)
    chiavi: List[str] = []
    marker: Optional[str] = None
    url = url_indice_file(prefisso)
    for _ in range(dati.MAX_PAGINE_INDICE):
        url = url_indice_file(prefisso, marker)
        contenuto = scarica(url)
        if contenuto is None:
            raise RuntimeError(f"indice dell'archivio non raggiungibile per {prefisso}")
        pagina, troncata, prossimo = _chiavi_della_pagina(contenuto)
        chiavi.extend(k for k in pagina if k.startswith(prefisso))
        if not troncata:
            return [c.rsplit("/", 1)[-1] for c in chiavi]
        if not prossimo:
            raise RuntimeError(f"{url}: pagina troncata senza chiavi ne' NextMarker")
        if marker is not None and prossimo <= marker:
            raise RuntimeError(f"{url}: pagina troncata con un marker che non avanza "
                               f"({prossimo!r} dopo {marker!r})")
        marker = prossimo
    raise RuntimeError(f"indice dell'archivio ancora troncato dopo {dati.MAX_PAGINE_INDICE} pagine: {url}")


# --------------------------------------------------------------------------- #
# Scrittura dei risultati                                                      #
# --------------------------------------------------------------------------- #
COLONNE_CSV = ("simbolo", "serie_collegata", "negoziata_oggi", "listing", "listing_da",
               "primo_mese_archivio", "ultimo_mese_archivio", "delisting", "anni_storia",
               "volume_medio_2023_usdt", "giorni_2023", "ultimo_giorno_2023", "fascia_slippage",
               "motivi_esclusione")


def riga_csv(c: Candidata) -> Dict[str, object]:
    volume = c.volume_medio_2023
    return {
        "simbolo": c.simbolo,
        "serie_collegata": c.serie_collegata,
        "negoziata_oggi": "si" if c.negoziata_oggi else "no",
        "listing": c.listing.isoformat() if c.listing else "",
        "listing_da": c.listing_da,
        "primo_mese_archivio": c.primo_mese.isoformat() if c.primo_mese else "",
        "ultimo_mese_archivio": c.ultimo_mese.isoformat() if c.ultimo_mese else "",
        "delisting": c.delisting.isoformat() if c.delisting else "",
        "anni_storia": "" if c.anni_storia is None else c.anni_storia,
        # ``round(nan)`` e ``round(inf)`` sollevano: un volume non leggibile resta vuoto
        "volume_medio_2023_usdt": "" if volume is None or not math.isfinite(volume) else round(volume),
        "giorni_2023": c.giorni_2023,
        "ultimo_giorno_2023": c.ultimo_giorno_2023.isoformat() if c.ultimo_giorno_2023 else "",
        "fascia_slippage": "" if c.fascia_slippage is None else c.fascia_slippage,
        "motivi_esclusione": "; ".join(c.motivi_esclusione),
    }


def scrivi_csv(percorso: Path, candidate: Sequence[Candidata]) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    with open(percorso, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLONNE_CSV)
        w.writeheader()
        for c in candidate:
            w.writerow(riga_csv(c))


def scheda_moneta(c: Candidata) -> str:
    """Il testo di ``campagne/<SIMBOLO>/scheda_moneta.md`` per il branch principale:
    SOLO informazioni valide al 2023-12-31 (niente delisting, niente simboli
    successivi): e' l'unica cosa che una sessione di campagna sa della moneta.

    Due monete con gli stessi dati al 2023-12-31 hanno la stessa scheda, viva o
    delistata che sia. Percio' la scheda NON porta la data di listing: per una
    delistata la data viene dal primo mese dell'archivio e coincide col primo
    mese di dati, per una viva viene da exchangeInfo e quasi mai coincide, e il
    confronto direbbe se la moneta e' ancora negoziata. Non compaiono neppure
    ``negoziata_oggi``, ``listing_da`` ne' ``serie_collegata``. Il primo mese di
    dati e' l'inizio dell'in-sample (sezione 3.1, Fase 0)."""
    assert c.fascia_slippage is not None
    return (
        f"# {c.simbolo}\n\n"
        "Scheda scritta dal coordinamento al Passo 1 del protocollo. Contiene solo cio' che era\n"
        "vero al 31 dicembre 2023: una sessione di campagna non cerca altro sulla moneta.\n\n"
        "| Campo | Valore |\n|---|---|\n"
        f"| Simbolo (Binance USDS-M, perpetuo in USDT) | `{c.simbolo}` |\n"
        f"| Primo mese di dati (inizio dell'in-sample) | {c.primo_mese.isoformat() if c.primo_mese else 'n.d.'} |\n"
        f"| Fascia di slippage per lato (volume medio 2023) | {c.fascia_slippage:.4%} |\n"
        "| Fine dell'in-sample | 2023-12-31 |\n"
    )
