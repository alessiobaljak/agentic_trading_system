"""Caricatore dei dati di mercato del protocollo di ricerca (sezioni 4 e 5 di
research/PROTOCOLLO.md), con il BLOCCO DEL VAULT e il controllo delle impronte.

Fonte: i file mensili pubblici di Binance USDS-M futures su data.binance.vision.
E' un modulo INDIPENDENTE dal bot: non importa nulla da bot/, backtesting/ o
scripts/. L'unica dipendenza interna e' ``Candela`` di ``research.src.motore``,
cosi' le candele caricate entrano nel motore senza conversioni.

Il blocco del vault
-------------------
Il vault e' il periodo dal 2024-01-01 al 2026-09-30. Finche' non esiste il file
``<radice>/vault/APERTURA.md`` (creato solo dopo che l'utente ha scritto in chat
"APRI IL VAULT"), qualunque richiesta di dati con una data oltre il 2023-12-31
viene rifiutata con ``VaultChiuso`` PRIMA di qualunque accesso alla rete o al
disco. Anche un solo giorno oltre il limite basta a far scattare il rifiuto:
il controllo si fa sull'intero periodo richiesto, non mese per mese, cosi' un
periodo a cavallo del limite non scarica nemmeno la parte lecita (chi lo
chiede ha sbagliato qualcosa e deve accorgersene). Il file deve avere un
contenuto (data, ora, candidati congelati): un ``APERTURA.md`` vuoto, nato da
un ``touch`` o da un editor, NON apre il vault.

Il confine vale anche verso l'alto: oltre il 2026-09-30 comincia il periodo
del paper trading, che per il protocollo non alimenta mai la ricerca. Una
richiesta oltre ``FINE_VAULT`` e' rifiutata con ``OltreIlVault`` anche a vault
aperto, sempre prima di toccare rete o disco.

Il filtro per date delle candele guarda sia l'apertura sia la chiusura: una
candela che apre entro ``fine`` ma chiude dopo (succede con intervalli come
'3d', il cui confine non coincide col 2023-12-31) porterebbe dentro prezzi
del vault, quindi si scarta.

Le eccezioni, previste dalla sezione 4 del protocollo e riservate alla sessione
di coordinamento al Passo 1, sono due: ``lista_contratti`` (la lista dei
contratti con date di listing e delisting, letta da due URL in ordine perche'
l'host delle API risponde 451 da alcune reti) ed ``elenca_simboli_archivio``
(i simboli che hanno dati nell'archivio, delistati compresi). Una sessione di
campagna non deve chiamarle, e con il marcatore di campagna le due funzioni la
rifiutano (vedi «In una sessione di campagna» qui sotto).

Niente elenchi di directory remote (con una sola eccezione)
-----------------------------------------------------------
Gli URL si costruiscono direttamente, un file per mese. Non si interroga mai
l'indice del bucket: elencare i file disponibili rivelerebbe fino a quando
esistono dati (cioe' informazione del vault). Un 404 per un mese vuol dire
"mese non disponibile" e si segna come assente, non e' un errore.

L'eccezione e' ``elenca_simboli_archivio``, che legge l'indice del bucket al
solo livello delle cartelle dei simboli (non dei file, quindi non delle date):
e' l'elenco dei contratti che hanno dati, compresi quelli delistati, e serve
SOLO alla sessione di coordinamento al Passo 1, perche' rivela quali contratti
esistono oggi.

Integrita' dei file scaricati: il CHECKSUM remoto
-------------------------------------------------
Accanto a ogni zip Binance pubblica ``<stesso URL>.CHECKSUM``, un file di
testo con ``<sha256 esadecimale>  <nome del file>``. Con lo scarico di rete
(``fetch`` non passato) ``scarica_mese`` lo legge sempre e confronta lo sha256
del contenuto PRIMA di scrivere su disco: se non combaciano solleva
``IntegritaFallita`` e il file non viene scritto; se il CHECKSUM manca (404) il
file si accetta ma il suo URL finisce in ``CHECKSUM_MANCANTI``, cosi' la
campagna puo' dichiararlo. Con un fetch iniettato il controllo e' spento salvo
``verifica_checksum=True``: chi inietta un fetch (un test, un mirror locale)
decide lui se serve anche i file ``.CHECKSUM``. Un file gia' su disco non si
riscarica e non si ricontrolla: per quello ci sono le impronte.

Dove finiscono i file
---------------------
``<radice>/data/insample/<SIMBOLO>/<tipo>/<INTERVALLO>/<nome>.zip`` per i mesi
fino al 2023-12, ``<radice>/data/vault/<SIMBOLO>/...`` per i mesi successivi
(solo a vault aperto). ``fundingRate`` non ha l'intervallo nel percorso. Un
file gia' presente su disco non si riscarica: il controllo dell'impronta
(``verifica_impronte``) dice se e' ancora quello della campagna.

Formato dei CSV di Binance
--------------------------
* klines e markPriceKlines: open_time, open, high, low, close, volume,
  close_time, quote_volume, count, taker_buy_volume, taker_buy_quote_volume,
  ignore. La riga di intestazione c'e' nei file nuovi e manca in quelli
  vecchi: si riconosce dal NOME del primo campo (``open_time`` o
  ``calc_time``). Un primo campo che non e' ne' un numero ne' un nome noto
  e' un file corrotto e solleva: nessuna riga si scarta in silenzio. Un
  eventuale BOM UTF-8 in testa viene tolto prima (``utf-8-sig``).
* I timestamp sono in millisecondi, ma dal 2025 alcuni file li hanno in
  microsecondi: un valore sopra 10**14 (cioe' oltre l'anno 5138 se letto in
  ms) e' in microsecondi e si divide per 1000.
* fundingRate: calc_time, funding_interval_hours, last_funding_rate. Nei file
  vecchi la colonna funding_interval_hours manca: allora vale 8 (l'intervallo
  storico di Binance).

Last e mark: un caricatore solo
-------------------------------
Il motore vuole last e mark allineati barra per barra, ma il mark ha buchi che
il last non ha (e viceversa), in giorni diversi da moneta a moneta. Nella prova
di processo tre campagne hanno scritto tre codici diversi per allinearli:
``carica_serie_allineate`` e' la regola unica (intersezione delle barre, barre
tolte elencate e contate, volume in USDT dalla colonna ``quote_volume``).

In una sessione di campagna: cosa il caricatore rifiuta
------------------------------------------------------
(``campagne/GRUPPO/regole.md``, sezione 2, punto 4, sezione 12, punto 4, e
sezione 13.) Il caricatore legge il marcatore della sessione come lo legge il
guardiano, con le sue funzioni (``guardiano.marcatore_presente`` e
``guardiano.leggi_marcatore``) e nello stesso percorso:
``<RADICE_PROGETTO>/research/.sessione``. ``RADICE_PROGETTO`` e' la cartella che
contiene ``research/``, calcolata da QUESTO file; non e' mai l'argomento
``radice`` delle funzioni, che dice solo dove stanno i dati (nei test e' una
cartella temporanea, e uno script potrebbe sceglierne un'altra): il controllo
non deve dipendere da dove si scrivono i dati. Un test che vuole simulare un
marcatore cambia la costante (``monkeypatch.setattr(dati, "RADICE_PROGETTO", ...)``).

* nessun marcatore, un marcatore vuoto o ``{"tipo": "coordinamento"}``: tutto
  come prima, nessun controllo;
* ``{"tipo": "campagna", ...}`` (qualunque simbolo): ``lista_contratti`` ed
  ``elenca_simboli_archivio`` alzano ``VietatoInCampagna`` prima di toccare la
  rete. Direbbero quali monete sono ancora negoziate oggi;
* ``{"tipo": "campagna", "simbolo": "GRUPPO"}``: le funzioni che scaricano o
  caricano i dati di un simbolo (``scarica_mese``, ``scarica_periodo``,
  ``carica_candele``, ``carica_funding``, ``carica_funding_dettaglio``,
  ``carica_serie_allineate``, ``calcola_impronte`` e le funzioni che le usano,
  ``liquidita_mensile`` e ``mesi_sotto_liquidita``) rifiutano i simboli fuori
  dall'elenco ``research/campagne/GRUPPO/monete.csv`` e da BTCUSDT. L'elenco si
  legge con ``guardiano.leggi_monete_gruppo``, cioe' solo se ha l'impronta
  approvata: se non ce l'ha ogni simbolo e' rifiutato, BTCUSDT compreso, come
  nel guardiano. L'insieme ammesso e' ``guardiano.monete_dati_ammesse``: una
  sola fonte per il guardiano e per il caricatore;
* ``{"tipo": "campagna", "simbolo": S}`` con una moneta sola: le stesse
  funzioni rifiutano i simboli diversi da S e da BTCUSDT (Passo 3 del
  protocollo, percorsi ammessi);
* un marcatore che c'e' ma e' rotto: ogni funzione controllata alza
  ``VietatoInCampagna`` (come il guardiano, che allora blocca tutto).

Le funzioni che leggono un percorso (``candele_da_zip``, ``volume_usdt_da_zip``,
``funding_da_zip``) e quelle che costruiscono nomi e URL senza toccare rete o
disco non controllano nulla. Come il guardiano, e' una barriera contro la
distrazione, non contro uno script scritto per aggirarla.

Campagna di gruppo (``campagne/GRUPPO/regole.md``, sezione 13)
--------------------------------------------------------------
* ``periodi_gruppo``: il taglio comune fra costruzione e validazione e le date
  di ogni moneta (sezione 1, punto 3), con numeri interi;
* ``leggi_scheda_gruppo``: primo mese di dati e fascia di slippage dalla scheda
  della moneta (sezione 1, punto 2, e sezione 2, punto 8);
* ``liquidita_mensile``, ``mesi_sotto_liquidita``, ``barra_vietata_liquidita`` e
  ``barre_vietate_liquidita``: il filtro di liquidita' (sezione 2, punto 7), con la
  soglia ``liquidita_minima_usdt_giorno`` di ``parametri.yaml``;
* ``VietatoInCampagna`` e i controlli descritti sopra (sezione 2, punto 4, e
  sezione 12, punto 4).
"""

from __future__ import annotations

import bisect
import csv
import hashlib
import io
import json
import math
import operator
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Callable, Collection, Dict, FrozenSet, Iterator, List, Mapping, Optional, Sequence, Tuple, Union

from research.src import guardiano
from research.src.motore import Candela

# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------

#: Ultimo giorno dei dati utilizzabili a vault chiuso (sezione 3.1 del protocollo).
FINE_IN_SAMPLE = date(2023, 12, 31)
#: Periodo del vault (sezione 3.1): uguale per tutte le monete.
INIZIO_VAULT = date(2024, 1, 1)
FINE_VAULT = date(2026, 9, 30)

#: La cartella research/ del repo, calcolata da questo file (research/src/dati.py).
RADICE_DEFAULT = Path(__file__).resolve().parent.parent
#: La radice del progetto: la cartella che contiene research/, calcolata da questo file.
#: Qui, e solo qui, si cerca il marcatore della sessione (``<RADICE_PROGETTO>/research/.sessione``,
#: lo stesso percorso del guardiano): mai sotto l'argomento ``radice`` delle funzioni.
#: I test che simulano un marcatore la cambiano con monkeypatch (si legge a ogni chiamata).
RADICE_PROGETTO = RADICE_DEFAULT.parent
#: I parametri congelati del progetto (sezione 3 del protocollo; sezione 0, punto 5, delle
#: regole del gruppo). Le soglie si leggono sempre da qui, mai da sotto ``radice``: ``radice``
#: dice dove stanno i dati, i numeri dell'esame sono quelli del progetto.
PERCORSO_PARAMETRI = RADICE_DEFAULT / "config" / "parametri.yaml"
#: Dove stanno le schede delle monete del gruppo, relativo a ``radice`` (regole.md, sezione 1, punto 2).
CARTELLA_SCHEDE_GRUPPO = Path("campagne") / "GRUPPO" / "schede"

BASE_URL = "https://data.binance.vision/data/futures/um/monthly"
URL_EXCHANGE_INFO = "https://fapi.binance.com/fapi/v1/exchangeInfo"
#: Stesso JSON sullo stesso percorso, ma servito dal sito: l'host delle API risponde
#: 451 ("non disponibile da questa regione") da alcune reti, tra cui quella delle
#: sessioni di lavoro (verificato il 6 ott 2026: 924 simboli da entrambi gli URL).
URL_EXCHANGE_INFO_ALTERNATIVO = "https://www.binance.com/fapi/v1/exchangeInfo"
#: Gli URL della lista dei contratti, nell'ordine in cui si provano.
URL_EXCHANGE_INFO_TUTTI = (URL_EXCHANGE_INFO, URL_EXCHANGE_INFO_ALTERNATIVO)
#: Campi di exchangeInfo riportati solo se la fonte li manda, col valore grezzo.
CAMPI_CONTRATTO_FACOLTATIVI = ("maintMarginPercent", "liquidationFee")

#: L'indice vero del bucket di data.binance.vision: la pagina sul sito e' HTML, il
#: bucket S3 risponde in XML con la paginazione classica (1000 voci per pagina).
URL_INDICE_ARCHIVIO = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
#: Il prefisso delle cartelle dei simboli delle candele mensili USDS-M.
PREFISSO_KLINES_ARCHIVIO = "data/futures/um/monthly/klines/"
#: Tetto alle pagine dell'indice: 100 pagine sono 100.000 simboli, oggi sono ~900.
#: Serve solo a non girare per sempre dietro a un server che manda marker sempre nuovi.
MAX_PAGINE_INDICE = 100

#: Suffisso del file col CHECKSUM che Binance pubblica accanto a ogni zip.
SUFFISSO_CHECKSUM = ".CHECKSUM"
#: URL degli zip scaricati e accettati SENZA CHECKSUM remoto (404), in ordine di scarico
#: e senza doppioni. Lo riempie ``scarica_mese`` quando il controllo e' acceso; la
#: campagna lo legge a fine Fase 0 per dichiarare quali file non hanno avuto la
#: verifica. ``azzera_checksum_mancanti`` lo svuota.
CHECKSUM_MANCANTI: List[str] = []

USER_AGENT = "research-dati/1.0 (caricatore del protocollo di ricerca)"
TIMEOUT_SECONDI = 60

#: Tipi di dato mensili che si sanno scaricare.
TIPI = ("klines", "markPriceKlines", "fundingRate")

#: Sopra questa soglia un timestamp e' in microsecondi (in ms sarebbe oltre l'anno 5138).
SOGLIA_MICROSECONDI = 10**14

#: Intervallo di funding usato quando il file non ha la colonna (file vecchi).
ORE_FUNDING_DEFAULT = 8

#: Nomi con cui Binance apre la riga di intestazione dei CSV (klines/markPriceKlines
#: e fundingRate). Solo questi fanno saltare la prima riga: tutto il resto solleva.
NOMI_INTESTAZIONE = ("open_time", "calc_time")

#: Indice della colonna ``quote_volume`` (volume in valuta di quotazione, cioe' USDT)
#: nei CSV klines di Binance: la stessa costante di ``selezione.COLONNA_QUOTE_VOLUME``.
COLONNA_QUOTE_VOLUME = 7

MS_ORA = 3_600_000
MS_GIORNO = 24 * MS_ORA

Fetch = Callable[[str], Optional[bytes]]


class VaultChiuso(Exception):
    """Richiesta di dati oltre il 2023-12-31 senza il file vault/APERTURA.md."""


class OltreIlVault(ValueError):
    """Richiesta di dati oltre il 2026-09-30: e' il periodo del paper, mai dato di ricerca."""


class VietatoInCampagna(Exception):
    """Richiesta che una sessione di campagna non puo' fare (``campagne/GRUPPO/regole.md``, sezione 2, punto 4, e sezione 12, punto 4).

    La lista dei contratti di oggi o l'indice dell'archivio con il marcatore di
    campagna; i dati di un simbolo fuori dall'insieme ammesso della campagna
    (per GRUPPO le monete di ``monete.csv`` e BTCUSDT, per una moneta sola la
    moneta e BTCUSDT); qualunque richiesta controllata con un marcatore rotto o,
    per GRUPPO, con un elenco che non ha l'impronta approvata.

    Non e' un ``OSError`` ne' un ``ValueError`` di proposito: chi prende gli errori
    di rete (``_scarica_exchange_info`` passa all'URL successivo su ``OSError``)
    o i dati malformati non deve inghiottire un rifiuto e riprovare.
    """


class IntegritaFallita(ValueError):
    """Lo sha256 del file scaricato non combacia col CHECKSUM remoto (o il CHECKSUM e' illeggibile).

    Il file NON e' stato scritto su disco. ``url`` e' quello dello zip,
    ``attesa`` l'impronta letta dal CHECKSUM (``None`` se illeggibile),
    ``trovata`` quella calcolata sul contenuto scaricato.
    """

    def __init__(self, messaggio: str, url: str, attesa: Optional[str], trovata: Optional[str]) -> None:
        super().__init__(messaggio)
        self.url = url
        self.attesa = attesa
        self.trovata = trovata


# ---------------------------------------------------------------------------
# Blocco del vault
# ---------------------------------------------------------------------------


def vault_aperto(radice: Path = RADICE_DEFAULT) -> bool:
    """True se ``<radice>/vault/APERTURA.md`` esiste ed ha un contenuto: il vault e' aperto.

    Il Passo 5 del protocollo crea il file con data, ora ed elenco dei
    candidati congelati: un file da 0 byte (o di soli spazi) e' un incidente,
    non un'apertura, e viene trattato come assente. Una cartella con quel
    nome non conta.
    """
    percorso = Path(radice) / "vault" / "APERTURA.md"
    if not percorso.is_file():
        return False
    try:
        return bool(percorso.read_text(encoding="utf-8", errors="replace").strip())
    except OSError:
        return False


def controlla_vault(fine: date, radice: Path = RADICE_DEFAULT) -> None:
    """Rifiuta le date fuori dal perimetro della ricerca, PRIMA di ogni accesso a rete o disco.

    ``fine`` e' l'ultima data del periodo richiesto: basta che quella sia
    oltre il limite. Due controlli, nell'ordine:

    * oltre ``FINE_VAULT`` (2026-09-30) si solleva ``OltreIlVault`` SEMPRE,
      anche a vault aperto: da li' in poi e' il periodo del paper trading,
      che il protocollo vieta di usare come dato di ricerca;
    * oltre ``FINE_IN_SAMPLE`` (2023-12-31) si solleva ``VaultChiuso`` finche'
      non esiste (con un contenuto) ``vault/APERTURA.md``.
    """
    if fine > FINE_VAULT:
        raise OltreIlVault(
            f"richiesti dati fino al {fine.isoformat()}, oltre la fine del vault "
            f"({FINE_VAULT.isoformat()}): e' il periodo del paper e non si usa per la ricerca"
        )
    if fine > FINE_IN_SAMPLE and not vault_aperto(radice):
        raise VaultChiuso(
            f"richiesti dati fino al {fine.isoformat()}, oltre il {FINE_IN_SAMPLE.isoformat()}: "
            f"il vault e' chiuso (manca {Path(radice) / 'vault' / 'APERTURA.md'})"
        )


# ---------------------------------------------------------------------------
# Sessione di campagna: cosa il caricatore rifiuta (regole.md del gruppo, 2.4 e 12.4)
# ---------------------------------------------------------------------------


def marcatore_di_campagna() -> Optional[Dict[str, str]]:
    """Il marcatore della sessione se dice ``campagna``, altrimenti ``None`` (``campagne/GRUPPO/regole.md``, sezione 12, punti 2 e 4).

    Lo legge il guardiano, con le sue funzioni e nel suo percorso:
    ``guardiano.marcatore_presente`` e ``guardiano.leggi_marcatore`` su
    ``RADICE_PROGETTO`` (la cartella che contiene ``research/``, calcolata da
    questo file e letta a ogni chiamata), mai sull'argomento ``radice`` delle
    funzioni del modulo:

    * nessun marcatore, o un marcatore vuoto (solo spazi): ``None``, come per il
      guardiano, che allora non fa nulla;
    * ``{"tipo": "coordinamento"}``: ``None``, il caricatore lavora come prima;
    * ``{"tipo": "campagna", "simbolo": S}``: ``{"tipo": "campagna", "simbolo": S}``;
    * un marcatore che c'e' ma e' rotto (JSON illeggibile, tipo sconosciuto,
      simbolo che non e' ``[A-Z0-9_]+``): ``VietatoInCampagna``. Il guardiano in
      quel caso blocca ogni azione: il caricatore fa lo stesso, perche' un
      marcatore rotto si sistema, non si ignora.
    """
    radice = str(RADICE_PROGETTO)
    if not guardiano.marcatore_presente(radice):
        return None
    try:
        marcatore = guardiano.leggi_marcatore(radice)
    except (ValueError, OSError) as errore:
        raise VietatoInCampagna(
            f"il marcatore {guardiano.percorso_marcatore(radice)} e' rotto ({errore}): il caricatore rifiuta "
            "ogni richiesta controllata finche' non e' sistemato (come il guardiano)"
        ) from errore
    if marcatore.get("tipo") != "campagna":
        return None
    return {"tipo": "campagna", "simbolo": str(marcatore["simbolo"])}


def simboli_ammessi_in_campagna() -> Optional[FrozenSet[str]]:
    """I simboli di cui la sessione di campagna puo' scaricare e caricare i dati; ``None`` fuori campagna (``campagne/GRUPPO/regole.md``, sezione 12, punto 4).

    E' ``guardiano.monete_dati_ammesse``, la stessa fonte del guardiano: per
    ``GRUPPO`` le monete di ``research/campagne/GRUPPO/monete.csv`` lette con
    ``guardiano.leggi_monete_gruppo`` (solo con l'impronta approvata) piu'
    BTCUSDT; per una moneta sola la moneta e BTCUSDT. Un elenco del gruppo che
    non ha l'impronta approvata (o non si legge) alza ``VietatoInCampagna``:
    come nel guardiano, finche' l'elenco non torna quello approvato nessun
    simbolo passa, BTCUSDT compreso.
    """
    marcatore = marcatore_di_campagna()
    if marcatore is None:
        return None
    simbolo = marcatore["simbolo"]
    monete_gruppo: FrozenSet[str] = frozenset()
    if simbolo == guardiano.SIMBOLO_GRUPPO:
        try:
            monete_gruppo = frozenset(guardiano.leggi_monete_gruppo(str(RADICE_PROGETTO)))
        except (ValueError, OSError) as errore:
            raise VietatoInCampagna(
                f"sessione di campagna GRUPPO con un elenco delle monete che non e' quello approvato ({errore}): "
                "il caricatore rifiuta ogni simbolo (campagne/GRUPPO/regole.md, sezione 12, punto 4)"
            ) from errore
    return frozenset(guardiano.monete_dati_ammesse(simbolo, monete_gruppo))


def controlla_simbolo_in_campagna(simbolo: str, chi: str = "dati") -> None:
    """Alza ``VietatoInCampagna`` se una sessione di campagna chiede i dati di un simbolo fuori dal suo insieme (``campagne/GRUPPO/regole.md``, sezione 2, punto 4, e sezione 12, punto 4).

    Fuori campagna (nessun marcatore, marcatore vuoto, coordinamento) non fa
    nulla. ``chi`` e' il nome della funzione che chiede, per il messaggio. Lo
    chiamano, prima di toccare rete o file di dati, ``scarica_mese``,
    ``scarica_periodo``, ``carica_serie_allineate``, ``calcola_impronte`` e
    ``_percorsi_presenti`` (cioe' ``carica_candele``, ``carica_funding``,
    ``carica_funding_dettaglio`` e il filtro di liquidita').
    """
    ammessi = simboli_ammessi_in_campagna()
    if ammessi is None or simbolo in ammessi:
        return
    marcatore = marcatore_di_campagna() or {}
    proprio = marcatore.get("simbolo", "?")
    if proprio == guardiano.SIMBOLO_GRUPPO:
        motivo = (f"{simbolo!r} non e' fra le monete di {guardiano.MONETE_GRUPPO} ne' "
                  f"{guardiano.MONETA_RIFERIMENTO} (campagne/GRUPPO/regole.md, sezione 12, punto 4)")
    else:
        motivo = (f"{simbolo!r} non e' {proprio} ne' {guardiano.MONETA_RIFERIMENTO} "
                  "(PROTOCOLLO.md, Passo 3, percorsi ammessi)")
    raise VietatoInCampagna(f"{chi}: in una sessione di campagna {proprio} il caricatore rifiuta i dati di {motivo}")


def controlla_fuori_campagna(chi: str, perche: str) -> None:
    """Alza ``VietatoInCampagna`` se il marcatore dice ``campagna``, con qualunque simbolo (``campagne/GRUPPO/regole.md``, sezione 2, punto 4, e sezione 12, punto 4).

    Serve alle due eccezioni del Passo 1 riservate al coordinamento,
    ``lista_contratti`` ed ``elenca_simboli_archivio``: in campagna direbbero
    quali monete sono ancora negoziate oggi (sezione 4, regola 1, del
    protocollo). ``perche'`` completa il messaggio.
    """
    marcatore = marcatore_di_campagna()
    if marcatore is not None:
        raise VietatoInCampagna(
            f"{chi}: vietata in una sessione di campagna ({marcatore['simbolo']}): {perche} "
            "(PROTOCOLLO.md, sezione 4, regola 1; campagne/GRUPPO/regole.md, sezione 2, punto 4)"
        )


# ---------------------------------------------------------------------------
# Nomi, URL e percorsi
# ---------------------------------------------------------------------------


def _controlla_tipo(tipo: str) -> None:
    if tipo not in TIPI:
        raise ValueError(f"tipo di dato sconosciuto: {tipo!r} (ammessi: {TIPI})")


def nome_file_mese(simbolo: str, tipo: str, intervallo: Optional[str], anno: int, mese: int) -> str:
    """Nome del file mensile di Binance, es. ``BTCUSDT-1h-2023-01.zip``.

    Per ``fundingRate`` il nome e' ``BTCUSDT-fundingRate-2023-01.zip`` e
    l'intervallo non conta.
    """
    _controlla_tipo(tipo)
    if tipo == "fundingRate":
        return f"{simbolo}-fundingRate-{anno:04d}-{mese:02d}.zip"
    if not intervallo:
        raise ValueError(f"per il tipo {tipo!r} serve l'intervallo (es. '1h')")
    return f"{simbolo}-{intervallo}-{anno:04d}-{mese:02d}.zip"


def url_mese(simbolo: str, tipo: str, intervallo: Optional[str], anno: int, mese: int) -> str:
    """URL diretto del file mensile: nessun elenco remoto, si costruisce e basta."""
    nome = nome_file_mese(simbolo, tipo, intervallo, anno, mese)
    if tipo == "fundingRate":
        return f"{BASE_URL}/fundingRate/{simbolo}/{nome}"
    return f"{BASE_URL}/{tipo}/{simbolo}/{intervallo}/{nome}"


def _ultimo_giorno_del_mese(anno: int, mese: int) -> date:
    primo_del_successivo = date(anno + (mese == 12), (mese % 12) + 1, 1)
    return primo_del_successivo - timedelta(days=1)


def percorso_mese(
    simbolo: str, tipo: str, intervallo: Optional[str], anno: int, mese: int, radice: Path = RADICE_DEFAULT
) -> Path:
    """Dove sta (o stara') il file del mese su disco.

    I mesi che finiscono entro il 2023-12-31 vanno in ``data/insample``, gli
    altri in ``data/vault``: cosi' i dati del vault non si mescolano mai a
    quelli in-sample, nemmeno per sbaglio.
    """
    nome = nome_file_mese(simbolo, tipo, intervallo, anno, mese)
    area = "insample" if _ultimo_giorno_del_mese(anno, mese) <= FINE_IN_SAMPLE else "vault"
    base = Path(radice) / "data" / area / simbolo / tipo
    if tipo != "fundingRate":
        base = base / str(intervallo)
    return base / nome


def mesi_del_periodo(inizio: date, fine: date) -> Iterator[Tuple[int, int]]:
    """Genera (anno, mese) per ogni mese toccato dal periodo [inizio, fine]."""
    if inizio > fine:
        raise ValueError(f"periodo vuoto: inizio {inizio} dopo fine {fine}")
    anno, mese = inizio.year, inizio.month
    while (anno, mese) <= (fine.year, fine.month):
        yield anno, mese
        anno, mese = anno + (mese == 12), (mese % 12) + 1


# ---------------------------------------------------------------------------
# Scarico
# ---------------------------------------------------------------------------


def fetch_http(url: str) -> Optional[bytes]:
    """Scarico di default: urllib con timeout 60 s e User-Agent semplice.

    urllib rispetta da solo ``HTTPS_PROXY`` dall'ambiente. Un 404 ritorna
    ``None`` (mese non disponibile); ogni altro errore HTTP o di rete solleva.
    """
    richiesta = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(richiesta, timeout=TIMEOUT_SECONDI) as risposta:
            return risposta.read()
    except urllib.error.HTTPError as errore:
        if errore.code == 404:
            return None
        raise


def _scrivi_atomico(percorso: Path, contenuto: bytes) -> None:
    """Scrive su un file temporaneo e poi rinomina: mai uno zip a meta' su disco."""
    percorso.parent.mkdir(parents=True, exist_ok=True)
    temporaneo = percorso.with_name(percorso.name + ".parziale")
    temporaneo.write_bytes(contenuto)
    os.replace(temporaneo, percorso)


def url_checksum(url: str) -> str:
    """URL del CHECKSUM pubblicato accanto a uno zip: lo stesso URL con ``.CHECKSUM`` in coda."""
    return url + SUFFISSO_CHECKSUM


def impronta_bytes(contenuto: bytes) -> str:
    """SHA-256 esadecimale di un contenuto in memoria (lo zip appena scaricato, prima di scriverlo)."""
    return hashlib.sha256(contenuto).hexdigest()


def leggi_checksum(contenuto: bytes, url: str = "") -> str:
    """L'impronta sha256 (64 esadecimali, minuscoli) dentro un file CHECKSUM di Binance.

    Il formato e' quello di ``sha256sum``: ``<sha256>  <nome del file>`` con
    due spazi e un newline finale; qui si tollerano spazi in piu', CRLF,
    righe vuote in testa e maiuscole. Si legge solo il primo campo della
    prima riga non vuota: il nome del file non si confronta, perche'
    un'impronta giusta con un nome sbagliato non capita e un'impronta
    sbagliata la prende il confronto. Un file senza un'impronta leggibile
    solleva ``IntegritaFallita``: il server dice di avere il CHECKSUM, quindi
    non si puo' far finta che manchi e accettare lo zip.
    """
    testo = contenuto.decode("utf-8", errors="replace")
    for riga in testo.splitlines():
        campi = riga.split()
        if not campi:
            continue
        candidato = campi[0].lower()
        if len(candidato) == 64 and all(c in "0123456789abcdef" for c in candidato):
            return candidato
        break
    raise IntegritaFallita(
        f"{url_checksum(url) if url else 'CHECKSUM'}: nessuna impronta sha256 leggibile in {contenuto[:80]!r}",
        url=url,
        attesa=None,
        trovata=None,
    )


def azzera_checksum_mancanti() -> None:
    """Svuota ``CHECKSUM_MANCANTI`` (es. all'inizio di una Fase 0, per contare solo i suoi scarichi)."""
    CHECKSUM_MANCANTI.clear()


def _controlla_integrita(url: str, contenuto: bytes, scarica: Fetch) -> None:
    """Confronta lo sha256 del contenuto col CHECKSUM remoto; solleva se non combaciano.

    Un CHECKSUM assente (404) non blocca: il file si accetta e l'URL si segna
    in ``CHECKSUM_MANCANTI`` (una volta sola), perche' per i file vecchi
    Binance potrebbe non pubblicarlo e la campagna deve poterlo dichiarare
    invece di fermarsi.
    """
    testo = scarica(url_checksum(url))
    if testo is None:
        if url not in CHECKSUM_MANCANTI:
            CHECKSUM_MANCANTI.append(url)
        return
    attesa = leggi_checksum(testo, url)
    trovata = impronta_bytes(contenuto)
    if attesa != trovata:
        raise IntegritaFallita(
            f"{url}: lo sha256 del file scaricato non combacia col CHECKSUM remoto "
            f"({url_checksum(url)}): attesa {attesa}, trovata {trovata}; file non scritto",
            url=url,
            attesa=attesa,
            trovata=trovata,
        )


def scarica_mese(
    simbolo: str,
    tipo: str,
    intervallo: Optional[str],
    anno: int,
    mese: int,
    radice: Path = RADICE_DEFAULT,
    fetch: Optional[Fetch] = None,
    verifica_checksum: Optional[bool] = None,
) -> Optional[Path]:
    """Scarica (se manca su disco) il file di un mese, ne controlla l'integrita' e ritorna il percorso.

    Ritorna ``None`` se la fonte risponde 404 (mese non disponibile). Solleva
    ``VaultChiuso`` se il mese e' oltre il 2023-12 e il vault e' chiuso, prima
    di toccare rete o disco.

    ``verifica_checksum`` governa il confronto col CHECKSUM remoto (vedi la
    docstring del modulo): ``None`` (default) vuol dire acceso con lo scarico
    di rete (``fetch`` non passato) e spento con un fetch iniettato, perche'
    chi inietta un fetch decide lui se serve anche i file ``.CHECKSUM``;
    ``True`` e ``False`` forzano. Col controllo acceso lo stesso fetch riceve
    anche l'URL del CHECKSUM, subito dopo quello dello zip: un'impronta
    diversa solleva ``IntegritaFallita`` e il file NON si scrive; un CHECKSUM
    assente (404) si accetta e si segna in ``CHECKSUM_MANCANTI``. Un file
    gia' su disco non si riscarica e non si ricontrolla.

    In una sessione di campagna un simbolo fuori dall'insieme ammesso alza
    ``VietatoInCampagna`` subito dopo il controllo del vault, prima di toccare
    rete o disco (``controlla_simbolo_in_campagna``; regole del gruppo,
    sezione 12, punto 4).
    """
    _controlla_tipo(tipo)
    controlla_vault(date(anno, mese, 1), radice)
    controlla_simbolo_in_campagna(simbolo, "scarica_mese")
    percorso = percorso_mese(simbolo, tipo, intervallo, anno, mese, radice)
    if percorso.is_file():
        return percorso
    scarica = fetch or fetch_http
    url = url_mese(simbolo, tipo, intervallo, anno, mese)
    contenuto = scarica(url)
    if contenuto is None:
        return None
    if verifica_checksum is None:
        verifica_checksum = fetch is None
    if verifica_checksum:
        _controlla_integrita(url, contenuto, scarica)
    _scrivi_atomico(percorso, contenuto)
    return percorso


def scarica_periodo(
    simbolo: str,
    tipo: str,
    intervallo: Optional[str],
    inizio: date,
    fine: date,
    radice: Path = RADICE_DEFAULT,
    fetch: Optional[Fetch] = None,
    verifica_checksum: Optional[bool] = None,
) -> List[Path]:
    """Scarica mese per mese i file del periodo [inizio, fine] e ritorna i percorsi.

    Il blocco del vault si applica all'INTERO periodo prima del primo scarico:
    se ``fine`` e' oltre il 2023-12-31 a vault chiuso, non parte nemmeno una
    richiesta. I mesi assenti (404) non compaiono nella lista.

    ``verifica_checksum`` passa tale e quale a ``scarica_mese``: col controllo
    acceso il primo mese con un'impronta diversa dal CHECKSUM remoto ferma
    tutto con ``IntegritaFallita`` (i mesi gia' scritti restano, sono buoni),
    e a fine scarico ``CHECKSUM_MANCANTI`` dice quali URL non avevano il
    CHECKSUM.

    In una sessione di campagna un simbolo fuori dall'insieme ammesso alza
    ``VietatoInCampagna`` prima del primo mese (``controlla_simbolo_in_campagna``).
    """
    _controlla_tipo(tipo)
    mesi = list(mesi_del_periodo(inizio, fine))  # valida anche inizio <= fine
    controlla_vault(fine, radice)
    controlla_simbolo_in_campagna(simbolo, "scarica_periodo")
    percorsi: List[Path] = []
    for anno, mese in mesi:
        percorso = scarica_mese(simbolo, tipo, intervallo, anno, mese, radice, fetch, verifica_checksum)
        if percorso is not None:
            percorsi.append(percorso)
    return percorsi


# ---------------------------------------------------------------------------
# Lettura dei CSV dentro gli zip
# ---------------------------------------------------------------------------


def _e_numero(testo: str) -> bool:
    try:
        float(testo)
        return True
    except ValueError:
        return False


def righe_csv_da_zip(percorso: Path) -> List[List[str]]:
    """Legge l'unico CSV dentro lo zip e ritorna le righe di dati (senza intestazione).

    L'intestazione c'e' nei file nuovi e manca in quelli vecchi: si riconosce
    dal nome del primo campo (``open_time`` o ``calc_time``), non dal fatto
    che "non e' un numero". Cosi' una prima riga che non e' ne' un numero ne'
    un'intestazione nota (file corrotto) solleva invece di sparire in
    silenzio: un caricatore che poi registra impronte non puo' perdere dati
    senza dirlo. Un eventuale BOM UTF-8 viene tolto da ``utf-8-sig``.
    """
    with zipfile.ZipFile(percorso) as archivio:
        nomi_csv = [n for n in archivio.namelist() if n.lower().endswith(".csv")]
        if len(nomi_csv) != 1:
            raise ValueError(f"{percorso}: attesi un solo .csv nello zip, trovati {nomi_csv}")
        with archivio.open(nomi_csv[0]) as flusso:
            testo = io.TextIOWrapper(flusso, encoding="utf-8-sig", newline="")
            righe = [r for r in csv.reader(testo) if r and any(c.strip() for c in r)]
    if righe and not _e_numero(righe[0][0]):
        primo = righe[0][0].strip().lower()
        if primo not in NOMI_INTESTAZIONE:
            raise ValueError(
                f"{percorso}: la prima riga non e' ne' un dato ne' un'intestazione nota "
                f"({NOMI_INTESTAZIONE}): {righe[0]}"
            )
        righe = righe[1:]
    return righe


def normalizza_ts(valore: Union[str, int, float]) -> int:
    """Timestamp in ms: se il valore e' sopra 10**14 era in microsecondi."""
    ts = int(float(valore))
    if ts > SOGLIA_MICROSECONDI:
        ts //= 1000
    return ts


def candele_da_zip(percorso: Path) -> List[Candela]:
    """Candele di un file mensile klines o markPriceKlines, nell'ordine del file."""
    candele: List[Candela] = []
    for riga in righe_csv_da_zip(percorso):
        if len(riga) < 7:
            raise ValueError(f"{percorso}: riga con {len(riga)} campi, ne servono almeno 7: {riga}")
        candele.append(
            Candela(
                ts=normalizza_ts(riga[0]),
                open=float(riga[1]),
                high=float(riga[2]),
                low=float(riga[3]),
                close=float(riga[4]),
                volume=float(riga[5]),
                close_ts=normalizza_ts(riga[6]),
            )
        )
    return candele


def volume_usdt_da_zip(percorso: Path) -> Dict[int, float]:
    """Volume in USDT di ogni barra di un file mensile klines: {ts di apertura in ms: quote_volume}.

    Serve al filtro di liquidita' della Fase 0 (PROTOCOLLO.md, Fase 0 punto 3:
    il volume medio giornaliero in USDT si legge dalla colonna ``quote_volume``).
    ``Candela.volume`` e' in moneta base: moltiplicarlo per il close darebbe
    solo un'approssimazione (il prezzo si muove dentro la barra) da
    dichiarare, mentre la colonna 7 del CSV e' il numero contato da Binance.

    La lettura e' la stessa di ``candele_da_zip``: ``righe_csv_da_zip`` toglie
    BOM e intestazione (e solleva su una prima riga che non e' ne' un dato ne'
    un'intestazione nota), ``normalizza_ts`` riporta i microsecondi ai
    millisecondi. Cosi' le chiavi coincidono coi ``ts`` delle candele dello
    stesso file. Tra due righe con lo stesso ``ts`` vale la prima, come in
    ``carica_candele``, anche quando la prima non ha il volume: un doppione
    non deve prestare il suo volume a una barra che non e' la sua.

    Una riga senza la colonna (meno di 8 campi) o con la colonna vuota non ha
    il volume: la sua barra NON compare nel dizionario e chi lo usa (come
    ``carica_serie_allineate``) la conta come mancante. Uno zero al suo posto
    la farebbe sembrare illiquida, cioe' un numero inventato. Un valore che
    c'e' ma non e' un numero finito e non negativo e' invece un file corrotto
    e solleva ``ValueError``: un NaN passerebbe il filtro di liquidita'
    (``nan < soglia`` e' falso) e un negativo abbasserebbe la media del mese,
    in silenzio.

    Solo klines: il mark price e' un indice su cui nessuno scambia, le sue
    colonne di volume non misurano niente. Un percorso che passa da una
    cartella ``markPriceKlines`` (o ``fundingRate``) solleva ``ValueError``.
    """
    parti = Path(percorso).parts
    for tipo_vietato in ("markPriceKlines", "fundingRate"):
        if tipo_vietato in parti:
            raise ValueError(
                f"{percorso}: il volume in USDT si legge solo dai file klines, non da {tipo_vietato}"
            )
    volumi: Dict[int, float] = {}
    visti = set()
    for riga in righe_csv_da_zip(percorso):
        ts = normalizza_ts(riga[0])
        if ts in visti:
            continue
        visti.add(ts)
        if len(riga) <= COLONNA_QUOTE_VOLUME or not riga[COLONNA_QUOTE_VOLUME].strip():
            continue
        testo = riga[COLONNA_QUOTE_VOLUME]
        try:
            valore = float(testo)
        except ValueError:
            raise ValueError(f"{percorso}: quote_volume non numerico {testo!r} nella riga {riga}") from None
        if not math.isfinite(valore) or valore < 0:
            raise ValueError(f"{percorso}: quote_volume non valido {testo!r} nella riga {riga}")
        volumi[ts] = valore
    return volumi


def funding_da_zip(percorso: Path) -> List[Tuple[int, int, float]]:
    """Righe (ts ms, intervallo in ore, tasso) di un file mensile fundingRate.

    Con 2 colonne (file vecchi: calc_time, last_funding_rate) l'intervallo
    vale ``ORE_FUNDING_DEFAULT``; con 3 e' la colonna centrale.
    """
    righe: List[Tuple[int, int, float]] = []
    for riga in righe_csv_da_zip(percorso):
        if len(riga) >= 3:
            ts, ore, tasso = normalizza_ts(riga[0]), int(float(riga[1])), float(riga[2])
        elif len(riga) == 2:
            ts, ore, tasso = normalizza_ts(riga[0]), ORE_FUNDING_DEFAULT, float(riga[1])
        else:
            raise ValueError(f"{percorso}: riga di funding con {len(riga)} campi: {riga}")
        righe.append((ts, ore, tasso))
    return righe


# ---------------------------------------------------------------------------
# Caricamento (dal disco) con ordinamento, deduplica e filtro
# ---------------------------------------------------------------------------


def ms_da_data(giorno: date) -> int:
    """Mezzanotte UTC del giorno, in ms."""
    return int(datetime(giorno.year, giorno.month, giorno.day, tzinfo=timezone.utc).timestamp() * 1000)



def periodi_campagna(primo_giorno: date) -> Dict[str, object]:
    """Le date di costruzione e validazione della Fase 0, calcolate con numeri interi.

    Regola del protocollo (Fase 0, punto 1): l'inizio e' il primo giorno del
    primo mese di dati della scheda; i giorni si contano dall'inizio al
    2023-12-31 compreso; la costruzione dura (70 x giorni) // 100 giorni; la
    validazione va dal giorno dopo al 2023-12-31. Tutto con interi: in virgola
    mobile 0,70 x 1430 fa 1000,999... e la costruzione verrebbe un giorno piu'
    corta (revisione del 7 ott 2026).

    Ritorna ``inizio``, ``fine_costruzione``, ``inizio_validazione`` e
    ``fine_validazione`` (date), ``giorni``, ``giorni_costruzione``, e in
    millisecondi ``inizio_ts`` (mezzanotte UTC dell'inizio),
    ``fine_costruzione_ts`` (le 23:59:59.999 dell'ultimo giorno di costruzione:
    e' l'argomento di ``motore.conta_trade``) e ``inizio_validazione_ts``.
    """
    fine = date(2023, 12, 31)
    if primo_giorno > fine:
        raise ValueError("il primo giorno di dati e' dopo la fine dell'in-sample")
    giorni = (fine - primo_giorno).days + 1
    giorni_costruzione = (70 * giorni) // 100
    fine_costruzione = primo_giorno + timedelta(days=giorni_costruzione - 1)
    inizio_validazione = fine_costruzione + timedelta(days=1)
    return {
        "inizio": primo_giorno,
        "giorni": giorni,
        "giorni_costruzione": giorni_costruzione,
        "fine_costruzione": fine_costruzione,
        "inizio_validazione": inizio_validazione,
        "fine_validazione": fine,
        "inizio_ts": ms_da_data(primo_giorno),
        "fine_costruzione_ts": ms_da_data(inizio_validazione) - 1,
        "inizio_validazione_ts": ms_da_data(inizio_validazione),
    }


def periodi_gruppo(primi_giorni: Mapping[str, date]) -> Dict[str, object]:
    """Il taglio comune fra costruzione e validazione della campagna di gruppo e le date di ogni moneta (``campagne/GRUPPO/regole.md``, sezione 1, punto 3).

    ``primi_giorni`` e' {simbolo: primo giorno del primo mese di dati della
    scheda} (``leggi_scheda_gruppo(s)["primo_mese"]``). Tutto con numeri interi,
    come ``periodi_campagna``:

    * i giorni-moneta di una moneta sono i giorni dal suo primo giorno al
      2023-12-31 compreso; ``giorni_moneta`` e' la loro somma su tutte le monete;
    * l'obiettivo e' (70 x ``giorni_moneta``) // 100 (``gruppo.quota_costruzione``
      di ``parametri.yaml``, 0,70, scritta come intero per non perdere un
      giorno in virgola mobile);
    * il taglio D e' il PRIMO giorno in cui la somma, su tutte le monete, dei
      giorni dal primo giorno di dati a D compreso raggiunge l'obiettivo (una
      moneta che comincia dopo D non conta prima del suo inizio);
    * per tutte le monete la costruzione finisce a D, alle 23:59:59.999 UTC
      (``fine_costruzione_ts``, l'argomento di ``motore.conta_trade``), e la
      validazione va da D + 1 al 2023-12-31.

    Sulle 80 schede del gruppo: D = 2023-01-16, 349 giorni di validazione,
    93.167 giorni-moneta, obiettivo 65.216, 65.247 di costruzione, costruzione
    da 412 a 1.112 giorni per moneta (regola 1.3; lo ripete il test). Con una
    moneta sola il taglio e' quello di ``periodi_campagna``.

    ValueError (TypeError per una data che non e' una ``date`` pura: un
    ``datetime`` porterebbe un'ora) se non c'e' nessuna moneta, se un simbolo e'
    vuoto, se un primo giorno e' dopo il 2023-12-31, se una moneta comincia dopo
    il taglio (non avrebbe costruzione) o se non resta nessun giorno di
    validazione.

    Ritorna un dizionario con:

    * ``fine_costruzione`` (D), ``inizio_validazione`` (D + 1),
      ``fine_validazione`` (2023-12-31), come ``date``;
    * ``fine_costruzione_ts`` (D 23:59:59.999 UTC) e ``inizio_validazione_ts``
      (D + 1 00:00 UTC) in ms;
    * ``giorni_validazione`` (uguale per tutte le monete), ``giorni_moneta``,
      ``giorni_moneta_obiettivo``, ``giorni_moneta_costruzione`` (la somma a D,
      che puo' superare l'obiettivo di meno delle monete attive in D) e
      ``giorni_moneta_validazione``;
    * ``monete``: {simbolo: date della moneta}, in ordine dei caratteri, con le
      chiavi di ``periodi_campagna`` (``inizio``, ``giorni``,
      ``giorni_costruzione``, ``fine_costruzione``, ``inizio_validazione``,
      ``fine_validazione``, ``inizio_ts``, ``fine_costruzione_ts``,
      ``inizio_validazione_ts``) piu' ``giorni_validazione``.
    """
    if not primi_giorni:
        raise ValueError("periodi_gruppo: nessuna moneta")
    fine = FINE_IN_SAMPLE
    for simbolo, primo in primi_giorni.items():
        if not isinstance(simbolo, str) or not simbolo:
            raise ValueError(f"periodi_gruppo: simbolo non valido {simbolo!r}")
        if isinstance(primo, datetime) or not isinstance(primo, date):
            raise TypeError(f"periodi_gruppo: il primo giorno di {simbolo} deve essere una date, non {primo!r}")
        if primo > fine:
            raise ValueError(f"periodi_gruppo: il primo giorno di {simbolo} ({primo}) e' dopo la fine dell'in-sample")
    simboli = sorted(primi_giorni)
    giorni = {s: (fine - primi_giorni[s]).days + 1 for s in simboli}
    giorni_moneta = sum(giorni.values())
    obiettivo = (70 * giorni_moneta) // 100

    # Si scorre il calendario dal primo giorno piu' antico: ogni giorno aggiunge
    # una unita' per ogni moneta che ha gia' dati. A fine 2023 la somma e' tutta
    # ``giorni_moneta`` >= obiettivo, quindi il ciclo si ferma entro il 2023-12-31.
    inizi = sorted(primi_giorni.values())
    taglio = inizi[0]
    attive = 0
    prossima = 0
    somma = 0
    while True:
        while prossima < len(inizi) and inizi[prossima] <= taglio:
            attive += 1
            prossima += 1
        somma += attive
        if somma >= obiettivo:
            break
        taglio += timedelta(days=1)

    giorni_validazione = (fine - taglio).days
    if giorni_validazione < 1:
        raise ValueError(f"periodi_gruppo: taglio al {taglio}, nessun giorno di validazione")
    tardive = [s for s in simboli if primi_giorni[s] > taglio]
    if tardive:
        raise ValueError(
            f"periodi_gruppo: {', '.join(tardive)} comincia dopo il taglio ({taglio}): nessun giorno di costruzione"
        )
    inizio_validazione = taglio + timedelta(days=1)
    inizio_validazione_ts = ms_da_data(inizio_validazione)
    fine_costruzione_ts = inizio_validazione_ts - 1
    monete: Dict[str, Dict[str, object]] = {}
    for s in simboli:
        primo = primi_giorni[s]
        monete[s] = {
            "inizio": primo,
            "giorni": giorni[s],
            "giorni_costruzione": (taglio - primo).days + 1,
            "giorni_validazione": giorni_validazione,
            "fine_costruzione": taglio,
            "inizio_validazione": inizio_validazione,
            "fine_validazione": fine,
            "inizio_ts": ms_da_data(primo),
            "fine_costruzione_ts": fine_costruzione_ts,
            "inizio_validazione_ts": inizio_validazione_ts,
        }
    return {
        "fine_costruzione": taglio,
        "fine_costruzione_ts": fine_costruzione_ts,
        "inizio_validazione": inizio_validazione,
        "inizio_validazione_ts": inizio_validazione_ts,
        "fine_validazione": fine,
        "giorni_validazione": giorni_validazione,
        "giorni_moneta": giorni_moneta,
        "giorni_moneta_obiettivo": obiettivo,
        "giorni_moneta_costruzione": somma,
        "giorni_moneta_validazione": giorni_moneta - somma,
        "monete": monete,
    }


# ---------------------------------------------------------------------------
# Parametri del progetto e schede del gruppo
# ---------------------------------------------------------------------------


def _leggi_parametri(percorso: Optional[Path] = None) -> Dict[str, object]:
    """Il contenuto di ``parametri.yaml`` (di norma ``PERCORSO_PARAMETRI``, letto a ogni chiamata; ``campagne/GRUPPO/regole.md``, sezione 0, punto 5)."""
    import yaml  # qui: il resto del modulo non ne ha bisogno

    with open(percorso if percorso is not None else PERCORSO_PARAMETRI, encoding="utf-8") as flusso:
        contenuto = yaml.safe_load(flusso)
    if not isinstance(contenuto, dict):
        raise ValueError(f"{percorso or PERCORSO_PARAMETRI}: atteso un dizionario YAML")
    return contenuto


def _numero_positivo(valore: object, dove: str) -> float:
    """Un numero finito e positivo letto da ``parametri.yaml``; ValueError per tutto il resto, anche un booleano (``campagne/GRUPPO/regole.md``, sezione 0, punto 5)."""
    if isinstance(valore, bool) or not isinstance(valore, (int, float)) or not math.isfinite(valore) or valore <= 0:
        raise ValueError(f"parametri.yaml, {dove}: atteso un numero positivo, trovato {valore!r}")
    return float(valore)


def liquidita_minima_usdt_giorno(percorso_parametri: Optional[Path] = None) -> float:
    """La soglia del filtro di liquidita': ``scelte_dati.liquidita_minima_usdt_giorno`` di ``parametri.yaml`` (``campagne/GRUPPO/regole.md``, sezione 2, punto 7).

    Oggi 20.000.000 USDT al giorno. Si legge dal ``parametri.yaml`` del progetto
    (``PERCORSO_PARAMETRI``), mai da sotto l'argomento ``radice`` delle funzioni
    dei dati: e' il file congelato di cui la prova a placebo registra
    l'impronta (regole.md, sezione 11, punto 1). ``percorso_parametri`` serve
    solo ai test del lettore. ValueError se la chiave manca o non e' un numero
    positivo.
    """
    parametri = _leggi_parametri(percorso_parametri)
    scelte = parametri.get("scelte_dati")
    if not isinstance(scelte, dict) or "liquidita_minima_usdt_giorno" not in scelte:
        raise ValueError("parametri.yaml: manca scelte_dati.liquidita_minima_usdt_giorno")
    return _numero_positivo(scelte["liquidita_minima_usdt_giorno"], "scelte_dati.liquidita_minima_usdt_giorno")


def fasce_slippage_per_lato(percorso_parametri: Optional[Path] = None) -> Tuple[float, ...]:
    """Gli slippage per lato delle fasce di ``scelte_dati.slippage_per_lato`` di ``parametri.yaml``, nell'ordine del file (``campagne/GRUPPO/regole.md``, sezione 2, punto 8).

    Servono a ``leggi_scheda_gruppo`` per controllare che la fascia scritta
    nella scheda sia una di quelle approvate. Stesso file e stesse regole di
    ``liquidita_minima_usdt_giorno``.
    """
    parametri = _leggi_parametri(percorso_parametri)
    scelte = parametri.get("scelte_dati")
    fasce = scelte.get("slippage_per_lato") if isinstance(scelte, dict) else None
    if not isinstance(fasce, list) or not fasce:
        raise ValueError("parametri.yaml: manca scelte_dati.slippage_per_lato")
    valori: List[float] = []
    for fascia in fasce:
        if not isinstance(fascia, dict) or "slippage" not in fascia:
            raise ValueError(f"parametri.yaml: fascia di slippage senza 'slippage': {fascia!r}")
        valori.append(_numero_positivo(fascia["slippage"], "scelte_dati.slippage_per_lato"))
    return tuple(valori)


#: (chiave, inizio del nome del campo) delle righe della tabella di una scheda del gruppo.
_CAMPI_SCHEDA_GRUPPO = (
    ("simbolo", "Simbolo"),
    ("primo_mese", "Primo mese di dati"),
    ("slippage", "Fascia di slippage per lato"),
    ("fine_in_sample", "Fine dell'in-sample"),
)
_PRIMO_MESE = re.compile(r"(\d{4})-(\d{2})-01")
_PERCENTUALE = re.compile(r"(\d+(?:\.\d+)?)%")


def leggi_scheda_gruppo(simbolo: str, radice: Path = RADICE_DEFAULT) -> Dict[str, object]:
    """Primo mese di dati e fascia di slippage di una moneta del gruppo, dalla sua scheda (``campagne/GRUPPO/regole.md``, sezione 1, punto 2, e sezione 2, punto 8).

    Legge ``<radice>/campagne/GRUPPO/schede/<SIMBOLO>.md``, la tabella con una
    riga per campo (``| Campo | Valore |``). Ogni campo deve comparire in UNA
    sola riga, riconosciuta dall'inizio del nome:

    * «Simbolo»: il valore (tra apici inversi) deve essere ``simbolo``;
    * «Primo mese di dati»: ``AAAA-MM-01``, il primo giorno del primo mese di
      dati, cioe' l'inizio dell'in-sample e della costruzione;
    * «Fascia di slippage per lato»: una percentuale (``0.0500%``), convertita in
      frazione per lato con l'aritmetica decimale (``0.0500%`` -> 0.0005,
      ``0.1000%`` -> 0.001: gli stessi float di ``parametri.yaml``), che deve
      essere una delle fasce di ``scelte_dati.slippage_per_lato``
      (``fasce_slippage_per_lato``);
    * «Fine dell'in-sample»: deve essere 2023-12-31.

    ``simbolo`` deve essere ``[A-Z0-9]+`` (mai un percorso). Il file mancante
    alza l'errore del sistema (``FileNotFoundError``); un campo mancante,
    doppio o diverso da quanto sopra alza ValueError.

    Ritorna {``simbolo``, ``primo_mese`` (``date``, il giorno 1: l'argomento di
    ``periodi_gruppo``), ``slippage_per_lato`` (float, per ``Parametri``),
    ``fine_in_sample`` (``date``)}.
    """
    if not isinstance(simbolo, str) or not re.fullmatch(r"[A-Z0-9]+", simbolo):
        raise ValueError(f"leggi_scheda_gruppo: simbolo non valido {simbolo!r}")
    percorso = Path(radice) / CARTELLA_SCHEDE_GRUPPO / f"{simbolo}.md"
    testo = percorso.read_text(encoding="utf-8")
    trovati: Dict[str, List[str]] = {chiave: [] for chiave, _ in _CAMPI_SCHEDA_GRUPPO}
    for riga in testo.splitlines():
        riga = riga.strip()
        if len(riga) < 2 or not (riga.startswith("|") and riga.endswith("|")):
            continue
        celle = [cella.strip() for cella in riga[1:-1].split("|")]
        if len(celle) != 2:
            continue
        nome, valore = celle
        for chiave, inizio_nome in _CAMPI_SCHEDA_GRUPPO:
            if nome.startswith(inizio_nome):
                trovati[chiave].append(valore)
    valori: Dict[str, str] = {}
    for chiave, inizio_nome in _CAMPI_SCHEDA_GRUPPO:
        if len(trovati[chiave]) != 1:
            raise ValueError(f"{percorso}: attesa una riga «{inizio_nome}», trovate {len(trovati[chiave])}")
        valori[chiave] = trovati[chiave][0]

    if valori["simbolo"].strip("`").strip() != simbolo:
        raise ValueError(f"{percorso}: la scheda e' di {valori['simbolo']!r}, non di {simbolo!r}")
    corrispondenza = _PRIMO_MESE.fullmatch(valori["primo_mese"])
    if not corrispondenza:
        raise ValueError(f"{percorso}: primo mese {valori['primo_mese']!r} non e' nella forma AAAA-MM-01")
    primo_mese = date(int(corrispondenza.group(1)), int(corrispondenza.group(2)), 1)
    if primo_mese > FINE_IN_SAMPLE:
        raise ValueError(f"{percorso}: primo mese {primo_mese} dopo la fine dell'in-sample")
    if valori["fine_in_sample"] != FINE_IN_SAMPLE.isoformat():
        raise ValueError(f"{percorso}: fine dell'in-sample {valori['fine_in_sample']!r}, attesa {FINE_IN_SAMPLE}")
    corrispondenza = _PERCENTUALE.fullmatch(valori["slippage"])
    if not corrispondenza:
        raise ValueError(f"{percorso}: fascia di slippage {valori['slippage']!r} non e' una percentuale")
    slippage = float(Decimal(corrispondenza.group(1)) / Decimal(100))
    fasce = fasce_slippage_per_lato()
    if slippage not in fasce:
        raise ValueError(f"{percorso}: slippage {slippage} non e' una fascia di parametri.yaml {fasce}")
    return {
        "simbolo": simbolo,
        "primo_mese": primo_mese,
        "slippage_per_lato": slippage,
        "fine_in_sample": FINE_IN_SAMPLE,
    }


def _percorsi_presenti(
    simbolo: str, tipo: str, intervallo: Optional[str], inizio: date, fine: date, radice: Path
) -> List[Path]:
    """I file del periodo che esistono su disco. Il controllo del vault viene prima, poi quello della campagna."""
    mesi = list(mesi_del_periodo(inizio, fine))
    controlla_vault(fine, radice)
    controlla_simbolo_in_campagna(simbolo, f"caricamento di {tipo}")
    percorsi = [percorso_mese(simbolo, tipo, intervallo, anno, mese, radice) for anno, mese in mesi]
    return [p for p in percorsi if p.is_file()]


def carica_candele(
    simbolo: str,
    intervallo: str,
    inizio: date,
    fine: date,
    radice: Path = RADICE_DEFAULT,
    tipo: str = "klines",
) -> List[Candela]:
    """Candele dal disco tra ``inizio`` e ``fine`` (giorni inclusi, UTC), ordinate e senza duplicati.

    Legge solo i file gia' scaricati (``scarica_periodo`` va chiamata prima):
    un mese senza file e' saltato, perche' la fonte puo' non averlo (contratto
    non ancora listato o gia' delistato). Tra due candele con lo stesso ``ts``
    si tiene la prima letta.

    Una candela entra solo se sta TUTTA nel periodo: apre da ``inizio`` in poi
    e chiude entro la fine di ``fine``. Una candela che apre l'ultimo giorno
    ma chiude dopo (es. la '3d' che apre il 2023-12-31 e chiude il
    2024-01-02) porterebbe high, low e close presi oltre il confine: a vault
    chiuso sarebbero dati del vault, quindi si scarta.
    """
    if tipo not in ("klines", "markPriceKlines"):
        raise ValueError(f"carica_candele accetta klines o markPriceKlines, non {tipo!r}")
    da_ms, a_ms = ms_da_data(inizio), ms_da_data(fine + timedelta(days=1))
    per_ts: Dict[int, Candela] = {}
    for percorso in _percorsi_presenti(simbolo, tipo, intervallo, inizio, fine, radice):
        for candela in candele_da_zip(percorso):
            if da_ms <= candela.ts and candela.close_ts < a_ms and candela.ts not in per_ts:
                per_ts[candela.ts] = candela
    return [per_ts[ts] for ts in sorted(per_ts)]


def carica_funding_dettaglio(
    simbolo: str, inizio: date, fine: date, radice: Path = RADICE_DEFAULT
) -> List[Tuple[int, int, float]]:
    """Righe (ts ms, ore, tasso) di funding dal disco, ordinate, senza duplicati, nel periodo.

    L'istante di ogni settlement si arrotonda per difetto al secondo. Nei file di
    Binance il ``calc_time`` e' spesso qualche millisecondo dopo l'ora piena (per
    BTCUSDT 2020-2023: 2.233 settlement su 4.383, fino a 47 ms; campagna BTCUSDT,
    8 ott 2026). Senza l'arrotondamento il motore non riconosce il settlement che
    cade all'apertura di una barra (momento ambiguo della sezione 7): all'ingresso
    lo conta anche se e' un incasso, all'uscita per «chiudi» lo perde anche se e'
    un costo.
    """
    da_ms, a_ms = ms_da_data(inizio), ms_da_data(fine + timedelta(days=1))
    per_ts: Dict[int, Tuple[int, int, float]] = {}
    for percorso in _percorsi_presenti(simbolo, "fundingRate", None, inizio, fine, radice):
        for ts, ore, tasso in funding_da_zip(percorso):
            ts -= ts % 1000
            if da_ms <= ts < a_ms and ts not in per_ts:
                per_ts[ts] = (ts, ore, tasso)
    return [per_ts[ts] for ts in sorted(per_ts)]


def carica_funding(
    simbolo: str, inizio: date, fine: date, radice: Path = RADICE_DEFAULT
) -> List[Tuple[int, float]]:
    """Coppie (ts ms, tasso) di funding dal disco, ordinate, senza duplicati, nel periodo."""
    return [(ts, tasso) for ts, _ore, tasso in carica_funding_dettaglio(simbolo, inizio, fine, radice)]


def intervallo_funding(righe: Sequence[Tuple]) -> List[Tuple[int, float]]:
    """Gli intervalli di funding (ore) presenti nel tempo: lista di (ts da cui vale, ore).

    Accetta sia le righe di ``carica_funding_dettaglio`` (ts, ore, tasso), dove
    le ore sono quelle dichiarate dal file, sia quelle di ``carica_funding``
    (ts, tasso), dove le ore si ricavano dalla distanza al settlement
    successivo (l'ultima riga non ha un successivo e non contribuisce). Le ore
    uguali consecutive si comprimono: il risultato cambia solo quando cambia
    l'intervallo. Serve a sapere se nel periodo Binance e' passata da 8 a 4 ore
    (o altro), cosa che il motore deve sapere per il costo del funding.
    """
    ore_per_ts: List[Tuple[int, float]] = []
    for i, riga in enumerate(righe):
        if len(riga) >= 3:
            ore_per_ts.append((int(riga[0]), float(riga[1])))
        elif i + 1 < len(righe):
            ore_per_ts.append((int(riga[0]), (int(righe[i + 1][0]) - int(riga[0])) / MS_ORA))
    segmenti: List[Tuple[int, float]] = []
    for ts, ore in ore_per_ts:
        if not segmenti or segmenti[-1][1] != ore:
            segmenti.append((ts, ore))
    return segmenti


# ---------------------------------------------------------------------------
# Aggregazione di timeframe
# ---------------------------------------------------------------------------

_UNITA_MS = {"m": 60_000, "h": MS_ORA, "d": MS_GIORNO, "w": 7 * MS_GIORNO}
#: Il 1970-01-01 (epoca) era un giovedi': le settimane di Binance partono dal lunedi'.
_SCARTO_LUNEDI_MS = 4 * MS_GIORNO


def durata_intervallo(intervallo: str) -> int:
    """Durata in ms di un intervallo scritto alla Binance: '1m', '15m', '1h', '4h', '1d', '1w'."""
    if len(intervallo) < 2 or intervallo[-1] not in _UNITA_MS or not intervallo[:-1].isdigit():
        raise ValueError(f"intervallo non riconosciuto: {intervallo!r} (es. '15m', '1h', '1d')")
    return int(intervallo[:-1]) * _UNITA_MS[intervallo[-1]]


def aggrega_candele(candele: Sequence[Candela], intervallo: str, solo_complete: bool = True) -> List[Candela]:
    """Costruisce candele di ``intervallo`` da candele piu' corte (es. da 1m o 15m a 1h).

    Ogni gruppo e' allineato al multiplo dell'intervallo in UTC (le ore piene,
    la mezzanotte UTC; le settimane dal lunedi', come fa Binance): open del
    primo, high massimo, low minimo, close dell'ultimo, volume somma;
    ``close_ts`` = inizio + durata - 1. La durata di partenza si legge dalla
    prima candela e deve dividere esattamente quella richiesta. Con
    ``solo_complete`` i gruppi con meno candele del dovuto (buchi nei dati o
    bordi del periodo) si scartano: una candela a meta' falserebbe i segnali.

    Le candele con lo stesso ``ts`` si contano una volta sola (si tiene la
    prima): la completezza del gruppo si misura sui ``ts`` distinti, altrimenti
    un duplicato coprirebbe un buco vero e raddoppierebbe il volume. Questa
    funzione e' pubblica e riceve anche liste costruite altrove, quindi non
    puo' contare sulla deduplica di ``carica_candele``.
    """
    if not candele:
        return []
    durata = durata_intervallo(intervallo)
    per_ts: Dict[int, Candela] = {}
    for candela in candele:
        per_ts.setdefault(candela.ts, candela)
    ordinate = [per_ts[ts] for ts in sorted(per_ts)]
    durata_sorgente = ordinate[0].close_ts - ordinate[0].ts + 1
    if durata_sorgente <= 0 or durata % durata_sorgente != 0:
        raise ValueError(
            f"la durata di partenza ({durata_sorgente} ms) non divide quella richiesta ({durata} ms)"
        )
    attese = durata // durata_sorgente
    scarto = _SCARTO_LUNEDI_MS if intervallo.endswith("w") else 0

    gruppi: Dict[int, List[Candela]] = {}
    for candela in ordinate:
        inizio = (candela.ts - scarto) // durata * durata + scarto
        gruppi.setdefault(inizio, []).append(candela)

    risultato: List[Candela] = []
    for inizio in sorted(gruppi):
        gruppo = gruppi[inizio]
        if solo_complete and len(gruppo) != attese:
            continue
        risultato.append(
            Candela(
                ts=inizio,
                open=gruppo[0].open,
                high=max(c.high for c in gruppo),
                low=min(c.low for c in gruppo),
                close=gruppo[-1].close,
                volume=sum(c.volume for c in gruppo),
                close_ts=inizio + durata - 1,
            )
        )
    return risultato


# ---------------------------------------------------------------------------
# Last e mark allineati (il caricatore unico della Fase 0)
# ---------------------------------------------------------------------------


def carica_serie_allineate(
    simbolo: str,
    intervallo: str,
    inizio: date,
    fine: date,
    radice: Path = RADICE_DEFAULT,
    aggrega_da: Optional[str] = None,
) -> Dict[str, object]:
    """Last e mark price dal disco sugli STESSI ``ts``, con le barre tolte elencate e il volume in USDT.

    E' il caricatore unico chiesto dal rapporto della prova di processo: il
    motore (``esegui``, tramite ``allinea_serie``) vuole il mark allineato
    barra per barra alle candele dei segnali e solleva se ne manca una; il
    mark ha buchi che il last non ha e viceversa, in giorni diversi da moneta
    a moneta (anche giorni interi), e nella prova tre campagne hanno scritto
    tre regole diverse per allinearli. Con questa funzione la regola e' una
    sola, uguale per tutte le campagne, ed e' scritta qui invece che nel
    codice delle varianti.

    La regola e' l'INTERSEZIONE: si tengono solo i ``ts`` presenti in
    entrambe le serie, in ordine. Non si riempie in avanti il mark (ne' si
    usa il last al suo posto) perche' sul mark il motore valuta la
    liquidazione e prende il prezzo del funding: una barra di mark inventata
    (piatta sul close precedente, o copiata dal last, che ha ombre diverse)
    sposterebbe la liquidazione, facendola sparire dove il mark vero l'avrebbe
    toccata o comparire dove non l'ha toccata. Senza il mark la barra non si
    puo' valutare, quindi si toglie. Una barra tolta diventa per il motore un
    buco, che lui conta (``n_buchi_dati``); i settlement di funding caduti nel
    buco con posizione aperta si addebitano sull'ultimo mark disponibile e si
    contano a parte (``n_funding_in_buco``). Le barre tolte (quante e quali,
    da una parte e dall'altra) si dichiarano in ``fase0_dati.md``.

    Le due serie si leggono con ``carica_candele`` (``klines`` per il last,
    ``markPriceKlines`` per il mark): stessi file, stesso filtro per date,
    stessa deduplica. Il blocco del vault si controlla comunque all'inizio,
    con ``controlla_vault(fine, radice)``, PRIMA di qualunque accesso al
    disco. La serie dello stop non si carica: per il protocollo e' il last
    (``serie_stop`` di parametri.yaml, ``candele_stop=None`` nel motore).

    Con ``aggrega_da`` (es. ``"1m"`` o ``"15m"``) si leggono i file di
    quell'intervallo e ENTRAMBE le serie si aggregano a ``intervallo`` con
    ``aggrega_candele(..., solo_complete=True)`` prima dell'intersezione: un
    gruppo incompleto in una serie non esiste per quella serie. Quindi
    un'ora completa nel last ma monca nel mark finisce in ``tolte_last``;
    un'ora monca in tutte e due non finisce in nessuna lista (e' un buco di
    entrambe), ma si vede nei conteggi ``n_gruppi_incompleti_*``.

    Il volume in USDT viene dalla colonna ``quote_volume`` dei file klines
    (``volume_usdt_da_zip``), solo per le barre tenute. Con ``aggrega_da`` e'
    la somma dei quote_volume delle barre di partenza del gruppo (quelle con
    ``ts`` fra apertura e chiusura della barra aggregata, cioe' esattamente il
    gruppo di ``aggrega_candele``). Se una barra tenuta (o una sola barra del
    suo gruppo) non ha il quote_volume, il valore e' ``None`` e si conta in
    ``n_volume_mancante``: mai uno zero, che la farebbe sembrare illiquida.
    Attenzione: per il filtro di liquidita' mensile il protocollo usa le
    candele GIORNALIERE del last; le giornate tolte dall'intersezione qui non
    hanno il volume. Chi vuole la media su tutti i giorni del last legge i
    file ``1d`` con ``volume_usdt_da_zip``.

    Se una delle due serie e' vuota (nessun file, o nessuna barra nel
    periodo) il risultato e' vuoto ma i conteggi ci sono: nessuna eccezione,
    cosi' la campagna lo vede e lo dichiara.

    In una sessione di campagna un simbolo fuori dall'insieme ammesso (per
    GRUPPO: fuori da ``monete.csv`` e da BTCUSDT) alza ``VietatoInCampagna``
    dopo il controllo del vault, prima di leggere un file
    (``controlla_simbolo_in_campagna``; regole del gruppo, sezione 12, punto 4).

    Ritorna un dizionario con:

    * ``candele``: il last sulle barre tenute (lista di ``Candela``, ``ts``
      strettamente crescenti), da passare a ``esegui`` come ``candele``;
    * ``candele_mark``: il mark sugli stessi ``ts``, da passare come
      ``candele_mark``;
    * ``tolte_last``: i ``ts`` presenti nel last ma non nel mark, ordinati;
    * ``tolte_mark``: i ``ts`` presenti nel mark ma non nel last, ordinati;
    * ``n_tolte_last``, ``n_tolte_mark``: le loro lunghezze;
    * ``volume_usdt``: {ts: volume in USDT o ``None``} per le barre tenute;
    * ``n_volume_mancante``: quante barre tenute hanno ``None``;
    * ``n_gruppi_incompleti_last``, ``n_gruppi_incompleti_mark``: con
      ``aggrega_da``, i gruppi scartati perche' incompleti in ciascuna serie
      (0 senza ``aggrega_da``).
    """
    controlla_vault(fine, radice)
    controlla_simbolo_in_campagna(simbolo, "carica_serie_allineate")
    sorgente = aggrega_da or intervallo
    last_sorgente = carica_candele(simbolo, sorgente, inizio, fine, radice, tipo="klines")
    mark_sorgente = carica_candele(simbolo, sorgente, inizio, fine, radice, tipo="markPriceKlines")

    n_incompleti_last = n_incompleti_mark = 0
    if aggrega_da:
        last = aggrega_candele(last_sorgente, intervallo, solo_complete=True)
        mark = aggrega_candele(mark_sorgente, intervallo, solo_complete=True)
        # Stessa funzione senza il filtro: i gruppi in piu' sono quelli scartati perche' monchi.
        n_incompleti_last = len(aggrega_candele(last_sorgente, intervallo, solo_complete=False)) - len(last)
        n_incompleti_mark = len(aggrega_candele(mark_sorgente, intervallo, solo_complete=False)) - len(mark)
    else:
        last, mark = last_sorgente, mark_sorgente

    mark_per_ts = {c.ts: c for c in mark}
    ts_last = {c.ts for c in last}
    candele = [c for c in last if c.ts in mark_per_ts]
    candele_mark = [mark_per_ts[c.ts] for c in candele]
    tolte_last = [c.ts for c in last if c.ts not in mark_per_ts]
    tolte_mark = [c.ts for c in mark if c.ts not in ts_last]

    volume_usdt: Dict[int, Optional[float]] = {}
    if candele:
        volumi_sorgente: Dict[int, float] = {}
        for percorso in _percorsi_presenti(simbolo, "klines", sorgente, inizio, fine, radice):
            for ts, valore in volume_usdt_da_zip(percorso).items():
                volumi_sorgente.setdefault(ts, valore)  # come carica_candele: vale il primo file letto
        ts_sorgente = [c.ts for c in last_sorgente]
        for candela in candele:
            if aggrega_da:
                da = bisect.bisect_left(ts_sorgente, candela.ts)
                a = bisect.bisect_right(ts_sorgente, candela.close_ts)
                membri = ts_sorgente[da:a]
            else:
                membri = [candela.ts]
            valori = [volumi_sorgente.get(ts) for ts in membri]
            volume_usdt[candela.ts] = None if any(v is None for v in valori) else sum(valori)
    n_volume_mancante = sum(1 for v in volume_usdt.values() if v is None)

    return {
        "candele": candele,
        "candele_mark": candele_mark,
        "tolte_last": tolte_last,
        "tolte_mark": tolte_mark,
        "n_tolte_last": len(tolte_last),
        "n_tolte_mark": len(tolte_mark),
        "volume_usdt": volume_usdt,
        "n_volume_mancante": n_volume_mancante,
        "n_gruppi_incompleti_last": n_incompleti_last,
        "n_gruppi_incompleti_mark": n_incompleti_mark,
    }


# ---------------------------------------------------------------------------
# Filtro di liquidita' (regole del gruppo, sezione 2, punto 7)
# ---------------------------------------------------------------------------


def mese_utc(ts_ms: int) -> Tuple[int, int]:
    """(anno, mese) in UTC dell'istante ``ts_ms`` (ms), con aritmetica intera (``campagne/GRUPPO/regole.md``, sezione 2, punto 7).

    «Il mese di una barra e' quello della sua apertura in UTC»: si passa il
    ``ts`` di apertura. Niente fusi orari locali e niente virgola mobile: i
    giorni sono ``ts_ms // MS_GIORNO`` dal 1970-01-01. Un ``ts`` non intero alza
    TypeError (``operator.index``).
    """
    giorno = date(1970, 1, 1) + timedelta(days=operator.index(ts_ms) // MS_GIORNO)
    return giorno.year, giorno.month


def liquidita_mensile(
    simbolo: str, inizio: date, fine: date, radice: Path = RADICE_DEFAULT
) -> Dict[Tuple[int, int], Dict[str, object]]:
    """Il volume medio giornaliero in USDT di ogni mese e se e' sotto la liquidita' minima (``campagne/GRUPPO/regole.md``, sezione 2, punto 7; Fase 0, punto 3, del protocollo).

    La regola, tutta qui (la sessione non scrive il filtro):

    * il volume si legge dai file ``1d`` del LAST (``klines``) con
      ``volume_usdt_da_zip``, cioe' dalla colonna ``quote_volume``; tra due righe
      con lo stesso ``ts`` vale la prima letta (mesi in ordine), come in
      ``carica_serie_allineate``;
    * ogni candela giornaliera va nel mese della sua apertura in UTC
      (``mese_utc``);
    * la media e' sui giorni PRESENTI nel mese: la somma dei volumi diviso il
      numero dei giorni con il volume. Un giorno senza candela, o con la candela
      ma senza la colonna del volume, non entra ne' nella somma ne' nel
      conteggio (mai uno zero inventato);
    * un mese e' sotto la soglia se la media e' strettamente sotto
      ``liquidita_minima_usdt_giorno()`` (20.000.000 USDT, ``parametri.yaml``);
      un mese senza nessun giorno con il volume (senza candele giornaliere) e'
      sotto la soglia.

    I mesi sono quelli toccati da [``inizio``, ``fine``] (``mesi_del_periodo``),
    e ogni mese si giudica INTERO, su tutti i suoi giorni presenti, qualunque
    sia il giorno di ``inizio`` e ``fine``: cosi' lo stesso mese ha lo stesso
    verdetto in costruzione e in validazione (gennaio 2023, che il taglio del
    gruppo divide, e' uno solo). Il blocco del vault si controlla sull'ultimo
    giorno dell'ultimo mese, prima di ogni accesso al disco; in campagna vale
    ``controlla_simbolo_in_campagna``.

    Ritorna {(anno, mese): {``giorni``: giorni presenti con il volume,
    ``volume_medio_usdt``: la media (``None`` senza giorni),
    ``sotto_soglia``: bool}} per ogni mese, in ordine.
    """
    mesi = list(mesi_del_periodo(inizio, fine))
    primo_giorno = date(mesi[0][0], mesi[0][1], 1)
    ultimo_giorno = _ultimo_giorno_del_mese(*mesi[-1])
    controlla_vault(ultimo_giorno, radice)
    controlla_simbolo_in_campagna(simbolo, "liquidita_mensile")
    soglia = liquidita_minima_usdt_giorno()

    volumi: Dict[int, float] = {}
    for percorso in _percorsi_presenti(simbolo, "klines", "1d", primo_giorno, ultimo_giorno, radice):
        for ts, valore in volume_usdt_da_zip(percorso).items():
            volumi.setdefault(ts, valore)
    per_mese: Dict[Tuple[int, int], List[float]] = {mese: [] for mese in mesi}
    for ts in sorted(volumi):
        mese = mese_utc(ts)
        if mese in per_mese:
            per_mese[mese].append(volumi[ts])

    risultato: Dict[Tuple[int, int], Dict[str, object]] = {}
    for mese in mesi:
        valori = per_mese[mese]
        media = sum(valori) / len(valori) if valori else None
        risultato[mese] = {
            "giorni": len(valori),
            "volume_medio_usdt": media,
            "sotto_soglia": media is None or media < soglia,
        }
    return risultato


def mesi_sotto_liquidita(
    simbolo: str, inizio: date, fine: date, radice: Path = RADICE_DEFAULT
) -> List[Tuple[int, int]]:
    """I mesi (anno, mese) sotto la liquidita' minima, in ordine (``campagne/GRUPPO/regole.md``, sezione 2, punto 7).

    E' la sola funzione che dice quali mesi sono sotto la soglia: la usa
    ``gruppo.py`` per ``conta_trade``, il test, la (a), la (b) e le sfasate, e la
    sessione per i mesi scritti in ``fase0_dati.md``. La regola e' quella di
    ``liquidita_mensile`` (file ``1d`` del last, media sui giorni presenti,
    soglia di ``parametri.yaml``, mese senza candele giornaliere sotto la
    soglia, mesi interi).
    """
    return [mese for mese, voce in liquidita_mensile(simbolo, inizio, fine, radice).items() if voce["sotto_soglia"]]


def barra_vietata_liquidita(ts_apertura: int, mesi_sotto: Collection[Tuple[int, int]]) -> bool:
    """True se la barra che apre a ``ts_apertura`` (ms) cade in un mese sotto la liquidita' minima (``campagne/GRUPPO/regole.md``, sezione 2, punto 7).

    Il mese di una barra e' quello della sua APERTURA in UTC (``mese_utc``),
    anche se la barra chiude nel mese dopo. ``mesi_sotto`` e' il risultato di
    ``mesi_sotto_liquidita`` (coppie (anno, mese); vanno bene anche liste di
    due interi, come tornano da un JSON). Su una barra vietata la variante non
    apre posizioni dai suoi segnali; una posizione gia' aperta esce con la sua
    uscita. Funzione pura.
    """
    return mese_utc(ts_apertura) in {(int(a), int(m)) for a, m in mesi_sotto}


def barre_vietate_liquidita(
    candele: Sequence[Union[Candela, int]], mesi_sotto: Collection[Tuple[int, int]]
) -> List[Tuple[int, int]]:
    """Gli indici delle barre di ``candele`` nei mesi sotto la liquidita' minima, come intervalli (``campagne/GRUPPO/regole.md``, sezione 2, punto 7).

    ``candele`` sono le barre della serie (``Candela``, o direttamente i ``ts``
    di apertura); ogni barra si giudica con ``barra_vietata_liquidita``.
    Ritorna intervalli (inizio incluso, fine esclusa) di indici consecutivi,
    nel formato di ``motore.barre_vietate_segnale_non_valido``: si passano
    cosi' come sono in ``barre_vietate`` di ``motore.simula_baseline_casuale``
    e ``motore.simula_sfasamento_comune`` (insieme alle altre barre vietate),
    cosi' la (b) e le sfasate vietano le stesse barre del filtro. Funzione pura.
    """
    mesi = {(int(a), int(m)) for a, m in mesi_sotto}
    vietate: List[Tuple[int, int]] = []
    for i, candela in enumerate(candele):
        ts = candela.ts if isinstance(candela, Candela) else candela
        if mese_utc(ts) in mesi:
            if vietate and vietate[-1][1] == i:
                vietate[-1] = (vietate[-1][0], i + 1)
            else:
                vietate.append((i, i + 1))
    return vietate


# ---------------------------------------------------------------------------
# Impronte (SHA-256) dei file scaricati
# ---------------------------------------------------------------------------


def impronta_file(percorso: Path) -> str:
    """SHA-256 esadecimale del file, letto a blocchi."""
    sha = hashlib.sha256()
    with open(percorso, "rb") as flusso:
        for blocco in iter(lambda: flusso.read(1 << 20), b""):
            sha.update(blocco)
    return sha.hexdigest()


def _cartella_insample(simbolo: str, radice: Path) -> Path:
    return Path(radice) / "data" / "insample" / simbolo


def calcola_impronte(simbolo: str, radice: Path = RADICE_DEFAULT) -> Dict[str, str]:
    """{nome relativo: sha256} di tutti gli .zip in-sample della moneta, in ordine di nome.

    Il nome e' relativo a ``data/insample/<SIMBOLO>`` con le barre in avanti
    (es. ``klines/1h/BTCUSDT-1h-2023-01.zip``), cosi' e' uguale su ogni macchina.
    Solo i dati in-sample: quelli del vault non fanno parte della campagna.
    In una sessione di campagna un simbolo fuori dall'insieme ammesso alza
    ``VietatoInCampagna`` (``controlla_simbolo_in_campagna``), anche per
    ``registra_impronte`` e ``verifica_impronte``, che passano da qui.
    """
    controlla_simbolo_in_campagna(simbolo, "calcola_impronte")
    cartella = _cartella_insample(simbolo, radice)
    if not cartella.is_dir():
        return {}
    return {
        p.relative_to(cartella).as_posix(): impronta_file(p)
        for p in sorted(cartella.rglob("*.zip"))
    }


def registra_impronte(simbolo: str, radice: Path = RADICE_DEFAULT) -> Dict[str, str]:
    """Calcola le impronte e le scrive in ``data/insample/<SIMBOLO>/impronte.json``.

    Il dict ritornato e' quello che la campagna copia in ``fase0_dati.md``: da
    li' in poi e' lui la verita', il file json e' solo una comodita' locale.
    """
    impronte = calcola_impronte(simbolo, radice)
    cartella = _cartella_insample(simbolo, radice)
    cartella.mkdir(parents=True, exist_ok=True)
    (cartella / "impronte.json").write_text(json.dumps(impronte, indent=2, sort_keys=True) + "\n")
    return impronte


def verifica_impronte(simbolo: str, radice: Path, attese: Dict[str, str]) -> List[str]:
    """Confronta i file su disco con le impronte attese; lista vuota = tutto uguale.

    Ogni differenza e' una frase: ``mancante: <nome>`` se il file atteso non
    c'e', ``diversa: <nome>`` se c'e' ma il contenuto e' cambiato. Un file in
    piu' su disco non e' una differenza: non altera i dati della campagna.
    Se la lista non e' vuota il protocollo dice STOP e segnalalo.
    """
    trovate = calcola_impronte(simbolo, radice)
    differenze: List[str] = []
    for nome in sorted(attese):
        if nome not in trovate:
            differenze.append(f"mancante: {nome}")
        elif trovate[nome] != attese[nome]:
            differenze.append(f"diversa: {nome} (attesa {attese[nome][:12]}..., trovata {trovate[nome][:12]}...)")
    return differenze


# ---------------------------------------------------------------------------
# Lista dei contratti (eccezione del Passo 1, solo coordinamento)
# ---------------------------------------------------------------------------


def _scarica_exchange_info(scarica: Fetch) -> bytes:
    """Prova gli URL di ``URL_EXCHANGE_INFO_TUTTI`` in ordine e ritorna il primo JSON letto.

    Si passa all'URL successivo per un errore HTTP diverso da 404 (es. il 451
    dell'host delle API da alcune reti) o per un errore di rete. Un 404
    invece ferma subito: dice che il PERCORSO non esiste piu', e l'altro host
    serve lo stesso percorso, quindi non lo avrebbe comunque. Se falliscono
    tutti si solleva ``RuntimeError`` che li nomina uno per uno, con l'errore
    di ciascuno, concatenato all'ultimo.
    """
    errori: List[str] = []
    ultimo: Optional[BaseException] = None
    for url in URL_EXCHANGE_INFO_TUTTI:
        try:
            contenuto = scarica(url)
        except urllib.error.HTTPError as errore:
            if errore.code == 404:
                raise RuntimeError(
                    f"{url}: risposta 404, il percorso della lista dei contratti non esiste piu'"
                ) from errore
            errori.append(f"{url}: HTTP {errore.code} ({errore.reason})")
            ultimo = errore
            continue
        except OSError as errore:  # URLError, timeout, connessione chiusa: tutti OSError
            errori.append(f"{url}: errore di rete ({errore})")
            ultimo = errore
            continue
        if contenuto is None:
            raise RuntimeError(f"{url}: risposta 404, il percorso della lista dei contratti non esiste piu'")
        return contenuto
    raise RuntimeError("lista dei contratti non leggibile da nessun URL: " + "; ".join(errori)) from ultimo


def lista_contratti(fetch: Optional[Fetch] = None) -> List[Dict[str, object]]:
    """La lista dei contratti USDS-M con date di listing e di delisting.

    NON e' soggetta al blocco del vault: e' un'eccezione prevista dalla
    sezione 4 del protocollo, e la usa SOLO la sessione di coordinamento al
    Passo 1 per selezionare le monete. Le date di delisting restano sul
    branch di coordinamento: una sessione di campagna non deve chiamarla.

    Si legge da ``URL_EXCHANGE_INFO`` e, se quello risponde con un errore
    HTTP diverso da 404 o con un errore di rete, da
    ``URL_EXCHANGE_INFO_ALTERNATIVO`` (stesso JSON, altro host): l'host delle
    API risponde 451 da alcune reti, tra cui quella delle sessioni di
    lavoro. Se falliscono entrambi ``RuntimeError`` li nomina tutti e due.

    Per ogni simbolo ritorna: symbol, status, contractType, onboardDate (ms),
    deliveryDate (ms), quoteAsset; le date mancanti restano ``None``. I campi
    ``maintMarginPercent`` e ``liquidationFee`` (``CAMPI_CONTRATTO_FACOLTATIVI``)
    compaiono solo se la fonte li manda, col valore grezzo cosi' come arriva
    (stringa decimale): convertirli a float farebbe perdere le cifre dichiarate.

    Con il marcatore di una sessione di campagna (qualunque simbolo) alza
    ``VietatoInCampagna`` prima di toccare la rete (``controlla_fuori_campagna``;
    regole del gruppo, sezione 2, punto 4, e sezione 12, punto 4).
    """
    controlla_fuori_campagna(
        "lista_contratti", "la lista dei contratti di oggi dice quali monete sono ancora negoziate"
    )
    contenuto = _scarica_exchange_info(fetch or fetch_http)
    risposta = json.loads(contenuto)
    contratti: List[Dict[str, object]] = []
    for voce in risposta.get("symbols", []):
        contratto: Dict[str, object] = {
            "symbol": voce.get("symbol"),
            "status": voce.get("status"),
            "contractType": voce.get("contractType"),
            "onboardDate": None if voce.get("onboardDate") is None else int(voce["onboardDate"]),
            "deliveryDate": None if voce.get("deliveryDate") is None else int(voce["deliveryDate"]),
            "quoteAsset": voce.get("quoteAsset"),
        }
        for campo in CAMPI_CONTRATTO_FACOLTATIVI:
            if campo in voce:
                contratto[campo] = voce[campo]
        contratti.append(contratto)
    return contratti


# ---------------------------------------------------------------------------
# Elenco dei simboli nell'archivio (eccezione del Passo 1, solo coordinamento)
# ---------------------------------------------------------------------------


def url_indice_archivio(prefisso: str, marker: Optional[str] = None) -> str:
    """URL di una pagina dell'indice S3 del bucket, al livello delle cartelle sotto ``prefisso``.

    ``delimiter=/`` fa raggruppare le chiavi per cartella (``CommonPrefixes``),
    cosi' la risposta elenca i simboli e non i file; ``marker`` e' da dove
    riprendere (paginazione S3 classica, 1000 voci per pagina). Le barre
    restano barre: e' la forma verificata contro il bucket vero.
    """
    parametri = {"delimiter": "/", "prefix": prefisso}
    if marker:
        parametri["marker"] = marker
    return URL_INDICE_ARCHIVIO + "?" + urllib.parse.urlencode(parametri, safe="/")


def _nome_locale(tag: str) -> str:
    """Il nome di un tag XML senza namespace: ``{http://...}Prefix`` -> ``Prefix``."""
    return tag.rsplit("}", 1)[-1]


def _leggi_pagina_indice(contenuto: bytes) -> Tuple[List[str], bool, Optional[str]]:
    """(prefissi comuni, e' troncata, marker da cui continuare) di una pagina ListBucketResult.

    Si usa un parser XML vero e non una regex perche' la pagina ha DUE tipi di
    ``<Prefix>``: quello in cima (l'eco del prefisso richiesto) e quelli dentro
    ``<CommonPrefixes>`` (le cartelle): contano solo i secondi. I namespace si
    ignorano (S3 ne mette uno di default). Senza ``NextMarker`` si continua
    dall'ultima voce restituita (prefisso o chiave, la maggiore), come
    prevede l'API quando c'e' il delimitatore.
    """
    radice = ET.fromstring(contenuto)
    prefissi: List[str] = []
    chiavi: List[str] = []
    troncata = False
    prossimo: Optional[str] = None
    for elemento in radice:
        nome = _nome_locale(elemento.tag)
        if nome == "CommonPrefixes":
            for figlio in elemento:
                if _nome_locale(figlio.tag) == "Prefix" and figlio.text and figlio.text.strip():
                    prefissi.append(figlio.text.strip())
        elif nome == "Contents":
            for figlio in elemento:
                if _nome_locale(figlio.tag) == "Key" and figlio.text and figlio.text.strip():
                    chiavi.append(figlio.text.strip())
        elif nome == "IsTruncated":
            troncata = (elemento.text or "").strip().lower() == "true"
        elif nome == "NextMarker" and elemento.text and elemento.text.strip():
            prossimo = elemento.text.strip()
    if troncata and prossimo is None:
        ultime = prefissi + chiavi
        prossimo = max(ultime) if ultime else None
    return prefissi, troncata, prossimo


def elenca_simboli_archivio(fetch: Optional[Fetch] = None, prefisso: str = PREFISSO_KLINES_ARCHIVIO) -> List[str]:
    """I simboli che hanno una cartella nell'archivio mensile, delistati compresi, in ordine.

    SOLO PER IL COORDINAMENTO (Passo 1 del protocollo): e' l'elenco dei
    contratti con dati, e la fonte conserva anche quelli non piu' negoziati,
    percio' serve a contarli e a farli entrare nella selezione. Rivela quali
    contratti esistono OGGI, cioe' informazione successiva al 2023-12-31: una
    sessione di campagna NON deve chiamarla (sezione 4 del protocollo).

    L'indice vero del bucket non e' su data.binance.vision (quella pagina e'
    HTML) ma sull'endpoint S3 ``URL_INDICE_ARCHIVIO``, con la paginazione
    classica: 1000 voci per pagina, ``IsTruncated`` quando ce ne sono altre,
    si continua col ``marker``. Si legge solo il livello delle cartelle dei
    simboli, mai i file dentro: i nomi dei file mensili direbbero fino a
    quando ogni contratto ha dati. Ritorna i soli nomi delle cartelle (es.
    ``BTCUSDT``), ordinati e senza doppioni. Un 404 sull'indice solleva; una
    pagina troncata il cui marker non avanza solleva (mai un giro infinito).

    Con il marcatore di una sessione di campagna (qualunque simbolo) alza
    ``VietatoInCampagna`` prima di toccare la rete (``controlla_fuori_campagna``;
    regole del gruppo, sezione 2, punto 4, e sezione 12, punto 4).
    """
    controlla_fuori_campagna(
        "elenca_simboli_archivio", "l'indice dell'archivio dice quali contratti esistono oggi"
    )
    scarica = fetch or fetch_http
    simboli = set()
    marker: Optional[str] = None
    for _pagina in range(MAX_PAGINE_INDICE):
        url = url_indice_archivio(prefisso, marker)
        contenuto = scarica(url)
        if contenuto is None:
            raise RuntimeError(f"{url}: risposta 404, impossibile leggere l'indice dell'archivio")
        prefissi, troncata, prossimo = _leggi_pagina_indice(contenuto)
        for voce in prefissi:
            if voce.startswith(prefisso):
                nome = voce[len(prefisso):].strip("/")
                if nome:
                    simboli.add(nome)
        if not troncata:
            return sorted(simboli)
        if not prossimo or (marker is not None and prossimo <= marker):
            raise RuntimeError(f"{url}: pagina troncata ma senza un marker che avanzi (marker {marker!r})")
        marker = prossimo
    raise RuntimeError(f"indice dell'archivio ancora troncato dopo {MAX_PAGINE_INDICE} pagine: {url}")
