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
campagna non deve chiamarle.

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
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Dict, Iterator, List, Optional, Sequence, Tuple, Union

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

MS_ORA = 3_600_000
MS_GIORNO = 24 * MS_ORA

Fetch = Callable[[str], Optional[bytes]]


class VaultChiuso(Exception):
    """Richiesta di dati oltre il 2023-12-31 senza il file vault/APERTURA.md."""


class OltreIlVault(ValueError):
    """Richiesta di dati oltre il 2026-09-30: e' il periodo del paper, mai dato di ricerca."""


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
    """
    _controlla_tipo(tipo)
    controlla_vault(date(anno, mese, 1), radice)
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
    """
    _controlla_tipo(tipo)
    mesi = list(mesi_del_periodo(inizio, fine))  # valida anche inizio <= fine
    controlla_vault(fine, radice)
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


def _percorsi_presenti(
    simbolo: str, tipo: str, intervallo: Optional[str], inizio: date, fine: date, radice: Path
) -> List[Path]:
    """I file del periodo che esistono su disco. Il controllo del vault viene prima."""
    mesi = list(mesi_del_periodo(inizio, fine))
    controlla_vault(fine, radice)
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
    """Righe (ts ms, ore, tasso) di funding dal disco, ordinate, senza duplicati, nel periodo."""
    da_ms, a_ms = ms_da_data(inizio), ms_da_data(fine + timedelta(days=1))
    per_ts: Dict[int, Tuple[int, int, float]] = {}
    for percorso in _percorsi_presenti(simbolo, "fundingRate", None, inizio, fine, radice):
        for riga in funding_da_zip(percorso):
            if da_ms <= riga[0] < a_ms and riga[0] not in per_ts:
                per_ts[riga[0]] = riga
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
    """
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
    """
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
    """
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
