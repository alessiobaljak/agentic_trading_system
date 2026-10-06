"""Test delle tre aggiunte "di rete" del caricatore (research/src/dati.py), tutti SENZA rete.

Il fetch e' finto e iniettato: risponde da un dizionario url -> bytes, puo'
sollevare un errore HTTP o di rete su un URL preciso, e conta le chiamate.
Cosi' si verifica:

1. che ``lista_contratti`` passi al secondo URL solo per gli errori giusti
   (HTTP diverso da 404, errore di rete) e nomini tutti e due se falliscono;
2. che ``scarica_mese`` confronti lo sha256 col CHECKSUM remoto PRIMA di
   scrivere su disco: CHECKSUM giusto -> file scritto, sbagliato -> nessun
   file e ``IntegritaFallita``, assente -> file scritto e URL segnato;
3. che ``elenca_simboli_archivio`` segua tutte le pagine dell'indice S3 e
   non confonda il ``<Prefix>`` in cima alla pagina con le cartelle.
"""

import hashlib
import io
import json
import urllib.error
import zipfile
from datetime import date
from typing import Dict, List, Optional

import pytest

from research.src import dati
from research.src.dati import IntegritaFallita

PREFISSO = dati.PREFISSO_KLINES_ARCHIVIO


class FetchFinto:
    """fetch(url) -> bytes | None da un dizionario; su alcuni URL solleva; conta le chiamate."""

    def __init__(self, risposte: Optional[Dict[str, bytes]] = None, errori: Optional[Dict[str, BaseException]] = None):
        self.risposte = dict(risposte or {})
        self.errori = dict(errori or {})
        self.chiamate: List[str] = []

    def __call__(self, url: str) -> Optional[bytes]:
        self.chiamate.append(url)
        if url in self.errori:
            raise self.errori[url]
        return self.risposte.get(url)


def errore_http(url: str, codice: int, motivo: str) -> urllib.error.HTTPError:
    """L'eccezione che urllib solleva per una risposta HTTP non 2xx (senza corpo)."""
    return urllib.error.HTTPError(url, codice, motivo, None, None)


def zip_in_memoria(nome_csv: str, testo: str) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archivio:
        archivio.writestr(nome_csv, testo)
    return buffer.getvalue()


def checksum_di(contenuto: bytes, nome: str) -> bytes:
    """Il file CHECKSUM come lo pubblica Binance: ``<sha256>  <nome>`` con due spazi e newline finale."""
    return f"{hashlib.sha256(contenuto).hexdigest()}  {nome}\n".encode()


@pytest.fixture(autouse=True)
def checksum_mancanti_puliti():
    """``CHECKSUM_MANCANTI`` e' stato del modulo: ogni test parte e finisce con la lista vuota."""
    dati.azzera_checksum_mancanti()
    yield
    dati.azzera_checksum_mancanti()


# ---------------------------------------------------------------------------
# (1) lista_contratti: primo URL, poi l'alternativo
# ---------------------------------------------------------------------------

EXCHANGE_INFO_FINTO = {
    "symbols": [
        {
            "symbol": "BTCUSDT",
            "status": "TRADING",
            "contractType": "PERPETUAL",
            "onboardDate": 1569398400000,
            "deliveryDate": 4133404800000,
            "quoteAsset": "USDT",
            "maintMarginPercent": "2.5000",
            "liquidationFee": "0.012500",
            "pricePrecision": 2,
        },
        {
            # senza i campi facoltativi: nel risultato non devono comparire
            "symbol": "VECCHIOUSDT",
            "status": "SETTLING",
            "contractType": "PERPETUAL",
            "onboardDate": 1600000000000,
            "deliveryDate": 1700000000000,
            "quoteAsset": "USDT",
        },
    ]
}
JSON_FINTO = json.dumps(EXCHANGE_INFO_FINTO).encode()


def test_lista_contratti_passa_al_secondo_url_dopo_un_451():
    """Il caso vero del 6 ott 2026: l'host delle API risponde 451, il sito serve lo stesso JSON."""
    fetch = FetchFinto(
        {dati.URL_EXCHANGE_INFO_ALTERNATIVO: JSON_FINTO},
        {dati.URL_EXCHANGE_INFO: errore_http(dati.URL_EXCHANGE_INFO, 451, "Unavailable For Legal Reasons")},
    )
    contratti = dati.lista_contratti(fetch)
    assert fetch.chiamate == [dati.URL_EXCHANGE_INFO, dati.URL_EXCHANGE_INFO_ALTERNATIVO]
    assert [c["symbol"] for c in contratti] == ["BTCUSDT", "VECCHIOUSDT"]
    # i due campi nuovi arrivano grezzi (stringhe), e solo se la fonte li manda
    assert contratti[0]["maintMarginPercent"] == "2.5000"
    assert contratti[0]["liquidationFee"] == "0.012500"
    assert "maintMarginPercent" not in contratti[1] and "liquidationFee" not in contratti[1]
    assert "pricePrecision" not in contratti[0]  # i campi non previsti restano fuori


def test_lista_contratti_primo_url_ok_non_prova_il_secondo():
    fetch = FetchFinto({dati.URL_EXCHANGE_INFO: JSON_FINTO, dati.URL_EXCHANGE_INFO_ALTERNATIVO: b"{}"})
    assert [c["symbol"] for c in dati.lista_contratti(fetch)] == ["BTCUSDT", "VECCHIOUSDT"]
    assert fetch.chiamate == [dati.URL_EXCHANGE_INFO]


def test_lista_contratti_passa_al_secondo_url_per_errore_di_rete():
    """Un errore di rete (URLError, timeout, connessione chiusa) vale come un errore HTTP non 404."""
    fetch = FetchFinto(
        {dati.URL_EXCHANGE_INFO_ALTERNATIVO: JSON_FINTO},
        {dati.URL_EXCHANGE_INFO: urllib.error.URLError("nome host non risolto")},
    )
    assert len(dati.lista_contratti(fetch)) == 2
    assert fetch.chiamate == [dati.URL_EXCHANGE_INFO, dati.URL_EXCHANGE_INFO_ALTERNATIVO]


def test_lista_contratti_se_falliscono_entrambi_il_messaggio_li_nomina_tutti_e_due():
    fetch = FetchFinto(
        errori={
            dati.URL_EXCHANGE_INFO: errore_http(dati.URL_EXCHANGE_INFO, 451, "Unavailable For Legal Reasons"),
            dati.URL_EXCHANGE_INFO_ALTERNATIVO: errore_http(dati.URL_EXCHANGE_INFO_ALTERNATIVO, 503, "Service Unavailable"),
        }
    )
    with pytest.raises(RuntimeError) as info:
        dati.lista_contratti(fetch)
    messaggio = str(info.value)
    assert dati.URL_EXCHANGE_INFO in messaggio and dati.URL_EXCHANGE_INFO_ALTERNATIVO in messaggio
    assert "451" in messaggio and "503" in messaggio
    assert fetch.chiamate == [dati.URL_EXCHANGE_INFO, dati.URL_EXCHANGE_INFO_ALTERNATIVO]


def test_lista_contratti_un_404_ferma_subito_senza_provare_il_secondo():
    """Un 404 dice che il PERCORSO non esiste piu': l'altro host serve lo stesso percorso, inutile provarlo."""
    fetch = FetchFinto({dati.URL_EXCHANGE_INFO_ALTERNATIVO: JSON_FINTO})  # il primo risponde None (404)
    with pytest.raises(RuntimeError) as info:
        dati.lista_contratti(fetch)
    assert dati.URL_EXCHANGE_INFO in str(info.value)
    assert fetch.chiamate == [dati.URL_EXCHANGE_INFO]
    # stessa cosa se il fetch solleva HTTPError 404 invece di ritornare None
    fetch = FetchFinto(
        {dati.URL_EXCHANGE_INFO_ALTERNATIVO: JSON_FINTO},
        {dati.URL_EXCHANGE_INFO: errore_http(dati.URL_EXCHANGE_INFO, 404, "Not Found")},
    )
    with pytest.raises(RuntimeError):
        dati.lista_contratti(fetch)
    assert fetch.chiamate == [dati.URL_EXCHANGE_INFO]


# ---------------------------------------------------------------------------
# (2) scarica_mese e il CHECKSUM remoto
# ---------------------------------------------------------------------------

URL_GEN = dati.url_mese("BTCUSDT", "klines", "1h", 2023, 1)
URL_FEB = dati.url_mese("BTCUSDT", "klines", "1h", 2023, 2)
ZIP_GEN = zip_in_memoria("BTCUSDT-1h-2023-01.csv", "1,1,2,0.5,1.5,3,3599999,4.5,10,1.5,2.25,0\n")
ZIP_FEB = zip_in_memoria("BTCUSDT-1h-2023-02.csv", "2,1,2,0.5,1.5,3,3599999,4.5,10,1.5,2.25,0\n")


def percorso_gen(radice):
    return radice / "data" / "insample" / "BTCUSDT" / "klines" / "1h" / "BTCUSDT-1h-2023-01.zip"


def test_url_checksum():
    assert dati.url_checksum(URL_GEN) == URL_GEN + ".CHECKSUM"
    assert dati.url_checksum(URL_GEN).endswith("BTCUSDT-1h-2023-01.zip.CHECKSUM")


def test_checksum_giusto_scrive_il_file(tmp_path):
    fetch = FetchFinto({URL_GEN: ZIP_GEN, dati.url_checksum(URL_GEN): checksum_di(ZIP_GEN, "BTCUSDT-1h-2023-01.zip")})
    percorso = dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path, fetch, verifica_checksum=True)
    assert percorso == percorso_gen(tmp_path)
    assert percorso.read_bytes() == ZIP_GEN
    # prima lo zip, poi il CHECKSUM, con lo stesso fetch
    assert fetch.chiamate == [URL_GEN, dati.url_checksum(URL_GEN)]
    assert dati.CHECKSUM_MANCANTI == []


def test_checksum_sbagliato_solleva_e_non_scrive(tmp_path):
    altro = zip_in_memoria("BTCUSDT-1h-2023-01.csv", "1,9,9,9,9,9,3599999,0,0,0,0,0\n")
    fetch = FetchFinto({URL_GEN: ZIP_GEN, dati.url_checksum(URL_GEN): checksum_di(altro, "BTCUSDT-1h-2023-01.zip")})
    with pytest.raises(IntegritaFallita) as info:
        dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path, fetch, verifica_checksum=True)
    errore = info.value
    assert isinstance(errore, ValueError)
    assert errore.url == URL_GEN
    assert errore.attesa == hashlib.sha256(altro).hexdigest()
    assert errore.trovata == hashlib.sha256(ZIP_GEN).hexdigest()
    assert URL_GEN in str(errore) and errore.attesa in str(errore) and errore.trovata in str(errore)
    # nessun file su disco: ne' lo zip, ne' il temporaneo ".parziale", ne' la cartella
    assert not percorso_gen(tmp_path).exists()
    assert not percorso_gen(tmp_path).with_name("BTCUSDT-1h-2023-01.zip.parziale").exists()
    assert not (tmp_path / "data").exists()
    assert dati.CHECKSUM_MANCANTI == []


def test_checksum_assente_scrive_il_file_e_lo_segnala(tmp_path):
    fetch = FetchFinto({URL_GEN: ZIP_GEN})  # il CHECKSUM risponde None (404)
    percorso = dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path, fetch, verifica_checksum=True)
    assert percorso == percorso_gen(tmp_path) and percorso.read_bytes() == ZIP_GEN
    assert fetch.chiamate == [URL_GEN, dati.url_checksum(URL_GEN)]
    assert dati.CHECKSUM_MANCANTI == [URL_GEN]
    dati.azzera_checksum_mancanti()
    assert dati.CHECKSUM_MANCANTI == []


def test_checksum_illeggibile_solleva_e_non_scrive(tmp_path):
    """Il server dice di avere il CHECKSUM ma dentro non c'e' un'impronta: non si fa finta che manchi."""
    fetch = FetchFinto({URL_GEN: ZIP_GEN, dati.url_checksum(URL_GEN): b"<html>errore</html>\n"})
    with pytest.raises(IntegritaFallita) as info:
        dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path, fetch, verifica_checksum=True)
    assert info.value.attesa is None and info.value.url == URL_GEN
    assert not (tmp_path / "data").exists()
    assert dati.CHECKSUM_MANCANTI == []


def test_leggi_checksum_tollera_spazi_doppi_newline_crlf_e_maiuscole():
    sha = hashlib.sha256(ZIP_GEN).hexdigest()
    assert dati.leggi_checksum(f"{sha}  BTCUSDT-1h-2023-01.zip\n".encode()) == sha
    assert dati.leggi_checksum(f"{sha} BTCUSDT-1h-2023-01.zip".encode()) == sha  # uno spazio, senza newline
    assert dati.leggi_checksum(f"\r\n  {sha}\t BTCUSDT-1h-2023-01.zip\r\n\r\n".encode()) == sha
    assert dati.leggi_checksum(sha.upper().encode()) == sha  # solo l'impronta, in maiuscolo
    # il valore vero verificato il 6 ott 2026 per BTCUSDT-1h-2023-01.zip
    vero = b"b9ac60cc3ffc1e16db96ca2314120ff7531988108ebef1733ee54234f4fedf7f  BTCUSDT-1h-2023-01.zip\n"
    assert dati.leggi_checksum(vero) == "b9ac60cc3ffc1e16db96ca2314120ff7531988108ebef1733ee54234f4fedf7f"
    with pytest.raises(IntegritaFallita):
        dati.leggi_checksum(b"")
    with pytest.raises(IntegritaFallita):
        dati.leggi_checksum(b"abc  BTCUSDT-1h-2023-01.zip\n")  # troppo corta
    with pytest.raises(IntegritaFallita):
        dati.leggi_checksum(("z" * 64 + "  x.zip\n").encode())  # non esadecimale


def test_impronta_bytes_e_impronta_file_coincidono(tmp_path):
    percorso = tmp_path / "a.zip"
    percorso.write_bytes(ZIP_GEN)
    assert dati.impronta_bytes(ZIP_GEN) == dati.impronta_file(percorso) == hashlib.sha256(ZIP_GEN).hexdigest()


def test_file_gia_su_disco_non_si_riscarica_ne_si_ricontrolla(tmp_path):
    percorso = percorso_gen(tmp_path)
    percorso.parent.mkdir(parents=True)
    percorso.write_bytes(ZIP_GEN)
    fetch = FetchFinto({URL_GEN: ZIP_GEN, dati.url_checksum(URL_GEN): b"non deve essere letto\n"})
    assert dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path, fetch, verifica_checksum=True) == percorso
    assert fetch.chiamate == []


def test_404_sullo_zip_non_chiede_il_checksum(tmp_path):
    fetch = FetchFinto()
    assert dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path, fetch, verifica_checksum=True) is None
    assert fetch.chiamate == [URL_GEN]
    assert dati.CHECKSUM_MANCANTI == []


def test_con_fetch_iniettato_il_controllo_e_spento_salvo_richiesta(tmp_path):
    """Chi inietta un fetch decide lui se serve i CHECKSUM: di default non si chiede (i test del
    caricatore contano le chiamate e rispondono con lo stesso zip a qualsiasi URL)."""
    fetch = FetchFinto({URL_GEN: ZIP_GEN, dati.url_checksum(URL_GEN): b"zzz\n"})
    assert dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path, fetch) == percorso_gen(tmp_path)
    assert fetch.chiamate == [URL_GEN]
    percorso_gen(tmp_path).unlink()
    fetch = FetchFinto({URL_GEN: ZIP_GEN, dati.url_checksum(URL_GEN): b"zzz\n"})
    assert dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path, fetch, verifica_checksum=False) is not None
    assert fetch.chiamate == [URL_GEN]
    assert dati.CHECKSUM_MANCANTI == []


def test_con_lo_scarico_di_rete_il_controllo_e_sempre_acceso(tmp_path, monkeypatch):
    """Senza fetch passato si usa fetch_http (qui sostituito in memoria) e il CHECKSUM si legge sempre."""
    fetch = FetchFinto({URL_GEN: ZIP_GEN, dati.url_checksum(URL_GEN): checksum_di(ZIP_GEN, "BTCUSDT-1h-2023-01.zip")})
    monkeypatch.setattr(dati, "fetch_http", fetch)
    assert dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path) == percorso_gen(tmp_path)
    assert fetch.chiamate == [URL_GEN, dati.url_checksum(URL_GEN)]
    # e col CHECKSUM sbagliato il file non si scrive, anche senza chiedere nulla
    percorso_gen(tmp_path).unlink()
    fetch = FetchFinto({URL_GEN: ZIP_GEN, dati.url_checksum(URL_GEN): checksum_di(ZIP_FEB, "BTCUSDT-1h-2023-01.zip")})
    monkeypatch.setattr(dati, "fetch_http", fetch)
    with pytest.raises(IntegritaFallita):
        dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path)
    assert not percorso_gen(tmp_path).exists()


def test_scarica_periodo_passa_il_controllo_e_raccoglie_i_mancanti(tmp_path):
    fetch = FetchFinto(
        {
            URL_GEN: ZIP_GEN,
            dati.url_checksum(URL_GEN): checksum_di(ZIP_GEN, "BTCUSDT-1h-2023-01.zip"),
            URL_FEB: ZIP_FEB,  # febbraio senza CHECKSUM
        }
    )
    percorsi = dati.scarica_periodo(
        "BTCUSDT", "klines", "1h", date(2023, 1, 1), date(2023, 2, 28), tmp_path, fetch, verifica_checksum=True
    )
    assert [p.name for p in percorsi] == ["BTCUSDT-1h-2023-01.zip", "BTCUSDT-1h-2023-02.zip"]
    assert fetch.chiamate == [URL_GEN, dati.url_checksum(URL_GEN), URL_FEB, dati.url_checksum(URL_FEB)]
    assert dati.CHECKSUM_MANCANTI == [URL_FEB]
    # riscaricare (dopo aver tolto il file) non raddoppia la voce
    percorsi[1].unlink()
    dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2023, 2, 1), date(2023, 2, 28), tmp_path, fetch, verifica_checksum=True)
    assert dati.CHECKSUM_MANCANTI == [URL_FEB]


def test_scarica_periodo_si_ferma_al_primo_file_corrotto_e_tiene_i_buoni(tmp_path):
    fetch = FetchFinto(
        {
            URL_GEN: ZIP_GEN,
            dati.url_checksum(URL_GEN): checksum_di(ZIP_GEN, "BTCUSDT-1h-2023-01.zip"),
            URL_FEB: ZIP_FEB,
            dati.url_checksum(URL_FEB): checksum_di(ZIP_GEN, "BTCUSDT-1h-2023-02.zip"),  # sbagliato
        }
    )
    with pytest.raises(IntegritaFallita) as info:
        dati.scarica_periodo(
            "BTCUSDT", "klines", "1h", date(2023, 1, 1), date(2023, 2, 28), tmp_path, fetch, verifica_checksum=True
        )
    assert info.value.url == URL_FEB
    assert percorso_gen(tmp_path).is_file()  # gennaio era buono e resta
    assert not percorso_gen(tmp_path).with_name("BTCUSDT-1h-2023-02.zip").exists()


# ---------------------------------------------------------------------------
# (3) elenca_simboli_archivio: indice S3 a pagine
# ---------------------------------------------------------------------------


def pagina_indice(prefisso: str, simboli, troncata: bool, next_marker: Optional[str] = None, chiavi=()) -> bytes:
    """Una pagina ListBucketResult come la manda S3: namespace di default, eco del prefisso in cima."""
    voci = "".join(f"<CommonPrefixes><Prefix>{prefisso}{s}/</Prefix></CommonPrefixes>" for s in simboli)
    contenuti = "".join(f"<Contents><Key>{k}</Key><Size>1</Size></Contents>" for k in chiavi)
    marker = f"<NextMarker>{next_marker}</NextMarker>" if next_marker else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
        f"<Name>data.binance.vision</Name><Prefix>{prefisso}</Prefix><Marker></Marker>{marker}"
        f"<MaxKeys>1000</MaxKeys><Delimiter>/</Delimiter>"
        f"<IsTruncated>{'true' if troncata else 'false'}</IsTruncated>{contenuti}{voci}</ListBucketResult>"
    ).encode()


def test_url_indice_archivio_ha_la_forma_verificata():
    assert (
        dati.url_indice_archivio(PREFISSO)
        == "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/um/monthly/klines/"
    )
    assert dati.url_indice_archivio(PREFISSO, PREFISSO + "ETHUSDT/") == (
        "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/"
        "&prefix=data/futures/um/monthly/klines/&marker=data/futures/um/monthly/klines/ETHUSDT/"
    )


def test_elenca_simboli_archivio_due_pagine_senza_next_marker():
    """Senza NextMarker si riparte dall'ultimo Prefix restituito, come verificato contro il bucket vero."""
    url1 = dati.url_indice_archivio(PREFISSO)
    url2 = dati.url_indice_archivio(PREFISSO, PREFISSO + "ETHUSDT/")
    fetch = FetchFinto(
        {
            url1: pagina_indice(PREFISSO, ["1000SHIBUSDT", "BTCUSDT", "ETHUSDT"], troncata=True),
            url2: pagina_indice(PREFISSO, ["SOLUSDT", "XRPUSDT", "BTCUSDT"], troncata=False),  # BTCUSDT doppio
        }
    )
    simboli = dati.elenca_simboli_archivio(fetch)
    assert simboli == ["1000SHIBUSDT", "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
    assert fetch.chiamate == [url1, url2]


def test_elenca_simboli_archivio_segue_il_next_marker_quando_c_e():
    url1 = dati.url_indice_archivio(PREFISSO)
    url2 = dati.url_indice_archivio(PREFISSO, PREFISSO + "ETHUSDT/")
    url3 = dati.url_indice_archivio(PREFISSO, PREFISSO + "SOLUSDT/")
    fetch = FetchFinto(
        {
            url1: pagina_indice(PREFISSO, ["BTCUSDT", "ETHUSDT"], troncata=True, next_marker=PREFISSO + "ETHUSDT/"),
            url2: pagina_indice(PREFISSO, ["SOLUSDT"], troncata=True, next_marker=PREFISSO + "SOLUSDT/"),
            url3: pagina_indice(PREFISSO, ["XRPUSDT"], troncata=False),
        }
    )
    assert dati.elenca_simboli_archivio(fetch) == ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
    assert fetch.chiamate == [url1, url2, url3]


def test_elenca_simboli_archivio_non_confonde_il_prefix_in_cima_con_le_cartelle():
    """Una pagina vuota ha comunque un <Prefix> (l'eco della richiesta): non e' un simbolo."""
    fetch = FetchFinto({dati.url_indice_archivio(PREFISSO): pagina_indice(PREFISSO, [], troncata=False)})
    assert dati.elenca_simboli_archivio(fetch) == []
    # e un file sciolto allo stesso livello (Contents) non e' un simbolo
    fetch = FetchFinto(
        {dati.url_indice_archivio(PREFISSO): pagina_indice(PREFISSO, ["BTCUSDT"], troncata=False, chiavi=[PREFISSO + "README"])}
    )
    assert dati.elenca_simboli_archivio(fetch) == ["BTCUSDT"]


def test_elenca_simboli_archivio_prefisso_diverso():
    prefisso = "data/futures/um/monthly/fundingRate/"
    url = dati.url_indice_archivio(prefisso)
    fetch = FetchFinto({url: pagina_indice(prefisso, ["ETHUSDT", "BTCUSDT"], troncata=False)})
    assert dati.elenca_simboli_archivio(fetch, prefisso) == ["BTCUSDT", "ETHUSDT"]
    assert fetch.chiamate == [url]


def test_elenca_simboli_archivio_404_solleva():
    fetch = FetchFinto()
    with pytest.raises(RuntimeError):
        dati.elenca_simboli_archivio(fetch)
    assert fetch.chiamate == [dati.url_indice_archivio(PREFISSO)]


def test_elenca_simboli_archivio_marker_che_non_avanza_solleva():
    """Mai un giro infinito: pagina troncata senza voci, o con un marker uguale al precedente."""
    url1 = dati.url_indice_archivio(PREFISSO)
    fetch = FetchFinto({url1: pagina_indice(PREFISSO, [], troncata=True)})
    with pytest.raises(RuntimeError):
        dati.elenca_simboli_archivio(fetch)
    assert fetch.chiamate == [url1]

    url2 = dati.url_indice_archivio(PREFISSO, PREFISSO + "BTCUSDT/")
    fetch = FetchFinto(
        {
            url1: pagina_indice(PREFISSO, ["BTCUSDT"], troncata=True),
            url2: pagina_indice(PREFISSO, ["BTCUSDT"], troncata=True),  # stesso marker di prima
        }
    )
    with pytest.raises(RuntimeError):
        dati.elenca_simboli_archivio(fetch)
    assert fetch.chiamate == [url1, url2]
