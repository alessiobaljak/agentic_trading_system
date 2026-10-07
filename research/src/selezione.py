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
  2. storia minima: listing prima del 2022-01-01 (``storia_minima_anni`` = 2);
  3. dati fino alla fine dell'in-sample: l'ultimo file mensile e' almeno
     2023-12 (una moneta morta prima non ha ne' validazione intera ne' vault);
  4. liquidita': volume medio giornaliero in USDT (quote volume) nel 2023 almeno
     ``liquidita_minima_usdt_giorno``;
  5. ordine per volume 2023 decrescente, le prime ``numero_monete_campagna``
     sono le monete di campagna; le altre sono le future monete di verifica.

Data di listing: ``onboardDate`` di exchangeInfo per i contratti di oggi; per i
delistati il primo mese nell'archivio (approssimazione dichiarata: l'archivio
mensile parte da gennaio 2020, quindi un contratto piu' vecchio compare come
2020-01). Data di delisting: l'ultimo mese nell'archivio, solo per i contratti
non piu' negoziati; resta sul branch di coordinamento.
"""
from __future__ import annotations

import csv
import re
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

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
#: listing prima di questa data = almeno due anni di storia prima del 2024
LIMITE_LISTING = date(2022, 1, 1)
LIQUIDITA_MINIMA = 20_000_000.0
NUMERO_MONETE_CAMPAGNA = 20
#: giorni del 2023 che servono per chiamare «intero» l'anno di volume: tollera
#: qualche buco di dati (sospensioni brevi), non mesi interi
GIORNI_MINIMI_2023 = 350
#: la colonna del volume in valuta di quotazione nel CSV delle candele
COLONNA_QUOTE_VOLUME = 7
COLONNA_OPEN_TIME = 0


@dataclass
class Candidata:
    """Una moneta valutata dal Passo 1, con tutto cio' che serve a decidere."""
    simbolo: str
    negoziata_oggi: bool
    listing: Optional[date]           # onboardDate oggi, altrimenti primo mese dell'archivio
    listing_da: str                   # "exchangeInfo" | "archivio" | "sconosciuta"
    primo_mese: Optional[date]
    ultimo_mese: Optional[date]       # fine del mese dell'ultimo file; per i delistati e' il delisting
    volume_medio_2023: Optional[float] = None
    giorni_2023: int = 0
    motivi_esclusione: List[str] = field(default_factory=list)

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
    """Lo slippage per lato della fascia di volume; None sotto la soglia minima."""
    if volume_medio is None:
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
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date()


def volume_quote_giornaliero(righe: Sequence[Sequence[str]]) -> List[Tuple[int, float]]:
    """(open_time ms, volume in valuta di quotazione) da righe CSV di candele
    giornaliere (``righe_csv_da_zip`` toglie gia' l'intestazione)."""
    out: List[Tuple[int, float]] = []
    for riga in righe:
        if len(riga) <= COLONNA_QUOTE_VOLUME:
            continue
        try:
            ts = dati.normalizza_ts(riga[COLONNA_OPEN_TIME])
            vol = float(riga[COLONNA_QUOTE_VOLUME])
        except (TypeError, ValueError):
            continue
        out.append((ts, vol))
    return out


def volume_medio_nella_finestra(
    giorni: Sequence[Tuple[int, float]],
    inizio: date = INIZIO_FINESTRA_VOLUME,
    fine: date = FINE_FINESTRA_VOLUME,
) -> Tuple[Optional[float], int]:
    """(media del volume giornaliero in USDT sui giorni presenti nella finestra, numero
    di giorni). Si divide per i giorni PRESENTI, non per 365: un buco di dati non
    abbassa la media; la copertura la dice il secondo valore."""
    da, a = dati.ms_da_data(inizio), dati.ms_da_data(fine) + dati.MS_GIORNO - 1
    visti: Dict[int, float] = {}
    for ts, vol in giorni:
        if da <= ts <= a:
            visti[ts] = vol            # un doppione sovrascrive, non raddoppia
    if not visti:
        return None, 0
    return sum(visti.values()) / len(visti), len(visti)


def valuta(candidata: Candidata) -> Candidata:
    """Applica i filtri 2-4 e scrive i motivi di esclusione (puro: ritorna la stessa
    istanza aggiornata)."""
    motivi: List[str] = []
    if candidata.listing is None:
        motivi.append("data di listing sconosciuta")
    elif candidata.listing >= LIMITE_LISTING:
        motivi.append(f"listing {candidata.listing.isoformat()} dopo il {LIMITE_LISTING.isoformat()}")
    if candidata.ultimo_mese is None or candidata.ultimo_mese < FINE_FINESTRA_VOLUME:
        motivi.append("dati che finiscono prima del 2023-12")
    if candidata.volume_medio_2023 is None:
        motivi.append("nessun volume nel 2023")
    else:
        if candidata.giorni_2023 < GIORNI_MINIMI_2023:
            motivi.append(f"solo {candidata.giorni_2023} giorni di dati nel 2023")
        if candidata.volume_medio_2023 < LIQUIDITA_MINIMA:
            motivi.append(f"volume medio 2023 {candidata.volume_medio_2023:,.0f} USDT sotto {LIQUIDITA_MINIMA:,.0f}")
    candidata.motivi_esclusione = motivi
    return candidata


def seleziona(candidate: Sequence[Candidata], n: int = NUMERO_MONETE_CAMPAGNA) -> Dict[str, object]:
    """La selezione finale: idonee ordinate per volume, le prime ``n`` di campagna,
    le altre idonee di verifica (la regola di verifica vera si applica al Passo 6),
    piu' i conteggi per il bias di sopravvivenza."""
    valutate = [valuta(c) for c in candidate]
    idonee = sorted((c for c in valutate if not c.motivi_esclusione),
                    key=lambda c: (-(c.volume_medio_2023 or 0.0), c.simbolo))
    campagna = idonee[:n]
    altre_idonee = idonee[n:]
    escluse = [c for c in valutate if c.motivi_esclusione]
    return {
        "campagna": campagna,
        "altre_idonee": altre_idonee,
        "escluse": escluse,
        "conteggi": {
            "candidate": len(valutate),
            "idonee": len(idonee),
            "campagna": len(campagna),
            "idonee_delistate_oggi": sum(1 for c in idonee if not c.negoziata_oggi),
            "campagna_delistate_oggi": sum(1 for c in campagna if not c.negoziata_oggi),
            "escluse_per_listing": sum(1 for c in escluse if any("listing" in m for m in c.motivi_esclusione)),
            "escluse_per_fine_dati": sum(1 for c in escluse if any("prima del 2023-12" in m for m in c.motivi_esclusione)),
            "escluse_per_volume": sum(1 for c in escluse if any("sotto" in m for m in c.motivi_esclusione)),
            "escluse_per_copertura": sum(1 for c in escluse if any("giorni di dati" in m for m in c.motivi_esclusione)),
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
    if troncata and prossimo is None and chiavi:
        prossimo = chiavi[-1]
    return chiavi, troncata, prossimo


def elenca_file_archivio(simbolo: str, intervallo: str = "1d", fetch: Optional[dati.Fetch] = None,
                         tipo: str = "klines") -> List[str]:
    """I NOMI dei file mensili di un simbolo nell'archivio (es. ``BTCUSDT-1d-2023-01.zip``),
    compresi quelli del periodo del vault. SOLO coordinamento: e' il modo di
    leggere listing e delisting di un contratto senza scaricare un solo prezzo."""
    scarica = fetch or dati.fetch_http
    prefisso = f"data/futures/um/monthly/{tipo}/{simbolo}/{intervallo}/"
    chiavi: List[str] = []
    marker: Optional[str] = None
    for _ in range(dati.MAX_PAGINE_INDICE):
        contenuto = scarica(url_indice_file(prefisso, marker))
        if contenuto is None:
            raise RuntimeError(f"indice dell'archivio non raggiungibile per {prefisso}")
        pagina, troncata, prossimo = _chiavi_della_pagina(contenuto)
        chiavi.extend(pagina)
        if not troncata or not prossimo or prossimo == marker:
            break
        marker = prossimo
    return [c.rsplit("/", 1)[-1] for c in chiavi]


# --------------------------------------------------------------------------- #
# Scrittura dei risultati                                                      #
# --------------------------------------------------------------------------- #
COLONNE_CSV = ("simbolo", "negoziata_oggi", "listing", "listing_da", "primo_mese_archivio",
               "ultimo_mese_archivio", "delisting", "anni_storia", "volume_medio_2023_usdt",
               "giorni_2023", "fascia_slippage", "motivi_esclusione")


def riga_csv(c: Candidata) -> Dict[str, object]:
    return {
        "simbolo": c.simbolo,
        "negoziata_oggi": "si" if c.negoziata_oggi else "no",
        "listing": c.listing.isoformat() if c.listing else "",
        "listing_da": c.listing_da,
        "primo_mese_archivio": c.primo_mese.isoformat() if c.primo_mese else "",
        "ultimo_mese_archivio": c.ultimo_mese.isoformat() if c.ultimo_mese else "",
        "delisting": c.delisting.isoformat() if c.delisting else "",
        "anni_storia": "" if c.anni_storia is None else c.anni_storia,
        "volume_medio_2023_usdt": "" if c.volume_medio_2023 is None else round(c.volume_medio_2023),
        "giorni_2023": c.giorni_2023,
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
    successivi): e' l'unica cosa che una sessione di campagna sa della moneta."""
    assert c.listing is not None and c.fascia_slippage is not None
    return (
        f"# {c.simbolo}\n\n"
        f"Scheda scritta dal coordinamento al Passo 1 del protocollo. Contiene solo cio' che era\n"
        f"vero al 31 dicembre 2023: una sessione di campagna non cerca altro sulla moneta.\n\n"
        f"| Campo | Valore |\n|---|---|\n"
        f"| Simbolo (Binance USDS-M, perpetuo in USDT) | `{c.simbolo}` |\n"
        f"| Data di listing dei futures | {c.listing.isoformat()} ({c.listing_da}) |\n"
        f"| Primo mese nell'archivio | {c.primo_mese.isoformat() if c.primo_mese else 'n.d.'} |\n"
        f"| Fascia di slippage per lato (volume medio 2023) | {c.fascia_slippage:.4%} |\n"
        f"| Fine dell'in-sample | 2023-12-31 |\n"
    )
