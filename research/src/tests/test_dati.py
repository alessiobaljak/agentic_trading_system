"""Test del caricatore dei dati (research/src/dati.py), tutti SENZA rete.

Il fetch e' finto: costruisce zip in memoria con CSV scritti a mano, e conta
le chiamate, cosi' si verifica che il blocco del vault scatti PRIMA di ogni
accesso alla rete e che un file gia' su disco non si riscarichi.
"""

import io
import json
import zipfile
from datetime import date
from pathlib import Path

import pytest

from research.src import dati
from research.src.dati import VaultChiuso
from research.src.motore import Candela

ORA = 3_600_000
QUARTO = 15 * 60_000
#: 2023-01-01 00:00 UTC in ms (calcolato a mano: 19358 giorni * 86400000).
TS_2023_01_01 = 19358 * 86_400_000
#: 2023-02-01 00:00 UTC: 31 giorni dopo.
TS_2023_02_01 = TS_2023_01_01 + 31 * 86_400_000

INTESTAZIONE_KLINES = (
    "open_time,open,high,low,close,volume,close_time,quote_volume,count,"
    "taker_buy_volume,taker_buy_quote_volume,ignore"
)


def zip_in_memoria(nome_csv: str, testo: str) -> bytes:
    """Uno zip con un solo CSV dentro, come quelli di data.binance.vision."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archivio:
        archivio.writestr(nome_csv, testo)
    return buffer.getvalue()


def riga_kline(ts: int, o: float, h: float, l: float, c: float, v: float, durata: int = ORA, micro: bool = False) -> str:
    """Una riga klines di Binance; con ``micro`` i timestamp sono in microsecondi."""
    close_ts = ts + durata - 1
    if micro:
        ts, close_ts = ts * 1000, ts * 1000 + durata * 1000 - 1
    return f"{ts},{o},{h},{l},{c},{v},{close_ts},{v * c},10,{v / 2},{v * c / 2},0"


class FetchFinto:
    """fetch(url) -> bytes | None che serve da un dizionario url -> bytes e conta le chiamate."""

    def __init__(self, risposte=None):
        self.risposte = dict(risposte or {})
        self.chiamate = []

    def __call__(self, url):
        self.chiamate.append(url)
        return self.risposte.get(url)


def apri_vault(radice: Path) -> None:
    (radice / "vault").mkdir(parents=True, exist_ok=True)
    (radice / "vault" / "APERTURA.md").write_text("aperto nel test\n")


# ---------------------------------------------------------------------------
# (1) il blocco del vault scatta prima di ogni accesso alla rete
# ---------------------------------------------------------------------------


def test_vault_chiuso_rifiuta_prima_di_fetch(tmp_path):
    fetch = FetchFinto()
    assert dati.vault_aperto(tmp_path) is False
    with pytest.raises(VaultChiuso):
        dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2023, 12, 1), date(2024, 1, 1), tmp_path, fetch)
    assert fetch.chiamate == []  # nemmeno il mese lecito di dicembre 2023 e' stato chiesto
    # anche un solo mese e anche carica_candele sono bloccati
    with pytest.raises(VaultChiuso):
        dati.scarica_mese("BTCUSDT", "klines", "1h", 2024, 1, tmp_path, fetch)
    with pytest.raises(VaultChiuso):
        dati.carica_candele("BTCUSDT", "1h", date(2023, 12, 1), date(2024, 1, 1), tmp_path)
    assert fetch.chiamate == []
    assert not (tmp_path / "data").exists()


def test_vault_aperto_scarica(tmp_path):
    apri_vault(tmp_path)
    assert dati.vault_aperto(tmp_path) is True
    url = dati.url_mese("BTCUSDT", "klines", "1h", 2024, 1)
    fetch = FetchFinto({url: zip_in_memoria("BTCUSDT-1h-2024-01.csv", riga_kline(0, 1, 2, 0.5, 1.5, 3) + "\n")})
    percorsi = dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2024, 1, 1), date(2024, 1, 31), tmp_path, fetch)
    assert fetch.chiamate == [url]
    assert percorsi == [tmp_path / "data" / "vault" / "BTCUSDT" / "klines" / "1h" / "BTCUSDT-1h-2024-01.zip"]
    assert percorsi[0].is_file()


# ---------------------------------------------------------------------------
# (2) URL esatti, senza elenchi remoti
# ---------------------------------------------------------------------------


def test_url_dei_tre_tipi():
    assert (
        dati.url_mese("BTCUSDT", "klines", "1h", 2023, 3)
        == "https://data.binance.vision/data/futures/um/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-2023-03.zip"
    )
    assert (
        dati.url_mese("ETHUSDT", "markPriceKlines", "15m", 2022, 11)
        == "https://data.binance.vision/data/futures/um/monthly/markPriceKlines/ETHUSDT/15m/ETHUSDT-15m-2022-11.zip"
    )
    assert (
        dati.url_mese("BTCUSDT", "fundingRate", None, 2023, 1)
        == "https://data.binance.vision/data/futures/um/monthly/fundingRate/BTCUSDT/BTCUSDT-fundingRate-2023-01.zip"
    )
    with pytest.raises(ValueError):
        dati.url_mese("BTCUSDT", "trades", "1h", 2023, 1)


def test_scarica_mese_chiama_url_esatto_e_salva_in_insample(tmp_path):
    url = dati.url_mese("BTCUSDT", "fundingRate", None, 2023, 6)
    fetch = FetchFinto({url: zip_in_memoria("x.csv", "1,8,0.0001\n")})
    percorso = dati.scarica_mese("BTCUSDT", "fundingRate", None, 2023, 6, tmp_path, fetch)
    assert fetch.chiamate == [url]
    assert percorso == tmp_path / "data" / "insample" / "BTCUSDT" / "fundingRate" / "BTCUSDT-fundingRate-2023-06.zip"
    assert percorso.is_file()


# ---------------------------------------------------------------------------
# (3) parsing: con/senza intestazione, millisecondi e microsecondi
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("con_intestazione", [False, True])
@pytest.mark.parametrize("micro", [False, True])
def test_parsing_klines(tmp_path, con_intestazione, micro):
    # Timestamp veri (2023): un file in microsecondi si riconosce dalla grandezza
    # del numero, quindi il test deve usare valori realistici, non zero.
    t0 = TS_2023_01_01
    righe = [riga_kline(t0, 1, 2, 0.5, 1.5, 3, micro=micro), riga_kline(t0 + ORA, 1.5, 3, 1, 2, 4, micro=micro)]
    testo = (INTESTAZIONE_KLINES + "\n" if con_intestazione else "") + "\n".join(righe) + "\n"
    percorso = tmp_path / "a.zip"
    percorso.write_bytes(zip_in_memoria("a.csv", testo))
    candele = dati.candele_da_zip(percorso)
    assert candele == [
        Candela(ts=t0, open=1, high=2, low=0.5, close=1.5, volume=3, close_ts=t0 + ORA - 1),
        Candela(ts=t0 + ORA, open=1.5, high=3, low=1, close=2, volume=4, close_ts=t0 + 2 * ORA - 1),
    ]


def test_normalizza_ts():
    assert dati.normalizza_ts("1672531200000") == 1672531200000  # ms, resta uguale
    assert dati.normalizza_ts("1672531200000000") == 1672531200000  # microsecondi -> ms
    assert dati.normalizza_ts("1672531200000999") == 1672531200000  # i resti sotto il ms si troncano


# ---------------------------------------------------------------------------
# (4) carica_candele ordina, deduplica e filtra
# ---------------------------------------------------------------------------


def test_carica_candele_ordina_deduplica_filtra(tmp_path):
    # gennaio 2023: candele scritte in disordine e con un duplicato del 2 gennaio
    g1 = TS_2023_01_01
    g2 = TS_2023_01_01 + 86_400_000
    g3 = TS_2023_01_01 + 2 * 86_400_000
    gennaio = "\n".join(
        [
            riga_kline(g2, 20, 21, 19, 20.5, 1, durata=86_400_000),
            riga_kline(g1, 10, 11, 9, 10.5, 1, durata=86_400_000),
            riga_kline(g2, 99, 99, 99, 99, 9, durata=86_400_000),  # duplicato: si tiene il primo
            riga_kline(g3, 30, 31, 29, 30.5, 1, durata=86_400_000),
        ]
    )
    febbraio = riga_kline(TS_2023_02_01, 40, 41, 39, 40.5, 1, durata=86_400_000)
    fetch = FetchFinto(
        {
            dati.url_mese("BTCUSDT", "klines", "1d", 2023, 1): zip_in_memoria("g.csv", gennaio + "\n"),
            dati.url_mese("BTCUSDT", "klines", "1d", 2023, 2): zip_in_memoria("f.csv", febbraio + "\n"),
        }
    )
    dati.scarica_periodo("BTCUSDT", "klines", "1d", date(2023, 1, 1), date(2023, 2, 28), tmp_path, fetch)

    tutte = dati.carica_candele("BTCUSDT", "1d", date(2023, 1, 1), date(2023, 2, 28), tmp_path)
    assert [c.ts for c in tutte] == [g1, g2, g3, TS_2023_02_01]
    assert tutte[1].open == 20  # il duplicato (open 99) e' stato scartato

    # filtro inclusivo sui giorni: dal 2 al 3 gennaio
    parte = dati.carica_candele("BTCUSDT", "1d", date(2023, 1, 2), date(2023, 1, 3), tmp_path)
    assert [c.ts for c in parte] == [g2, g3]


# ---------------------------------------------------------------------------
# (5) funding con e senza colonna intervallo, intervallo_funding
# ---------------------------------------------------------------------------


def test_funding_con_e_senza_colonna_intervallo(tmp_path):
    t0 = TS_2023_01_01
    vecchio = f"{t0},0.0001\n{t0 + 8 * ORA},-0.0002\n"
    nuovo = f"calc_time,funding_interval_hours,last_funding_rate\n{t0 + 16 * ORA},8,0.0003\n{t0 + 24 * ORA},4,0.0004\n"
    p_vecchio, p_nuovo = tmp_path / "v.zip", tmp_path / "n.zip"
    p_vecchio.write_bytes(zip_in_memoria("v.csv", vecchio))
    p_nuovo.write_bytes(zip_in_memoria("n.csv", nuovo))
    assert dati.funding_da_zip(p_vecchio) == [(t0, 8, 0.0001), (t0 + 8 * ORA, 8, -0.0002)]
    assert dati.funding_da_zip(p_nuovo) == [(t0 + 16 * ORA, 8, 0.0003), (t0 + 24 * ORA, 4, 0.0004)]


def test_carica_funding_e_intervallo(tmp_path):
    t0 = TS_2023_01_01
    testo = (
        f"{t0},8,0.0001\n{t0 + 8 * ORA},8,0.0002\n{t0 + 16 * ORA},8,0.0003\n"
        f"{t0 + 24 * ORA},4,0.0004\n{t0 + 28 * ORA},4,0.0005\n{t0 + 8 * ORA},8,0.9\n"  # ultimo = duplicato
    )
    fetch = FetchFinto({dati.url_mese("BTCUSDT", "fundingRate", None, 2023, 1): zip_in_memoria("f.csv", testo)})
    dati.scarica_periodo("BTCUSDT", "fundingRate", None, date(2023, 1, 1), date(2023, 1, 31), tmp_path, fetch)

    coppie = dati.carica_funding("BTCUSDT", date(2023, 1, 1), date(2023, 1, 31), tmp_path)
    assert coppie == [
        (t0, 0.0001),
        (t0 + 8 * ORA, 0.0002),
        (t0 + 16 * ORA, 0.0003),
        (t0 + 24 * ORA, 0.0004),
        (t0 + 28 * ORA, 0.0005),
    ]
    # dalle ore dichiarate (dettaglio): 8 ore dall'inizio, 4 ore dal quarto settlement
    dettaglio = dati.carica_funding_dettaglio("BTCUSDT", date(2023, 1, 1), date(2023, 1, 31), tmp_path)
    assert dati.intervallo_funding(dettaglio) == [(t0, 8.0), (t0 + 24 * ORA, 4.0)]
    # dalle sole coppie: le ore si ricavano dalla distanza al settlement successivo
    # t0 -> +8h: 8; +8h -> +16h: 8; +16h -> +24h: 8; +24h -> +28h: 4; l'ultima non conta
    assert dati.intervallo_funding(coppie) == [(t0, 8.0), (t0 + 24 * ORA, 4.0)]
    assert dati.intervallo_funding([]) == []


# ---------------------------------------------------------------------------
# (6) impronte
# ---------------------------------------------------------------------------


def test_impronte_registra_verifica_modifica(tmp_path):
    fetch = FetchFinto(
        {
            dati.url_mese("BTCUSDT", "klines", "1h", 2023, 1): zip_in_memoria("a.csv", riga_kline(0, 1, 2, 0.5, 1.5, 3) + "\n"),
            dati.url_mese("BTCUSDT", "fundingRate", None, 2023, 1): zip_in_memoria("f.csv", "1,8,0.0001\n"),
        }
    )
    dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2023, 1, 1), date(2023, 1, 31), tmp_path, fetch)
    dati.scarica_periodo("BTCUSDT", "fundingRate", None, date(2023, 1, 1), date(2023, 1, 31), tmp_path, fetch)

    impronte = dati.registra_impronte("BTCUSDT", tmp_path)
    assert sorted(impronte) == ["fundingRate/BTCUSDT-fundingRate-2023-01.zip", "klines/1h/BTCUSDT-1h-2023-01.zip"]
    assert all(len(sha) == 64 for sha in impronte.values())
    scritte = json.loads((tmp_path / "data" / "insample" / "BTCUSDT" / "impronte.json").read_text())
    assert scritte == impronte
    assert dati.verifica_impronte("BTCUSDT", tmp_path, impronte) == []

    # file modificato -> differenza; file cancellato -> mancante
    percorso = tmp_path / "data" / "insample" / "BTCUSDT" / "klines" / "1h" / "BTCUSDT-1h-2023-01.zip"
    percorso.write_bytes(zip_in_memoria("a.csv", riga_kline(0, 1, 2, 0.5, 1.6, 3) + "\n"))
    differenze = dati.verifica_impronte("BTCUSDT", tmp_path, impronte)
    assert len(differenze) == 1 and differenze[0].startswith("diversa: klines/1h/BTCUSDT-1h-2023-01.zip")
    percorso.unlink()
    assert dati.verifica_impronte("BTCUSDT", tmp_path, impronte) == ["mancante: klines/1h/BTCUSDT-1h-2023-01.zip"]


def test_impronta_file_sha256_noto(tmp_path):
    percorso = tmp_path / "vuoto.bin"
    percorso.write_bytes(b"")
    # SHA-256 della stringa vuota, valore noto
    assert dati.impronta_file(percorso) == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


# ---------------------------------------------------------------------------
# (7) 404 -> None senza eccezione
# ---------------------------------------------------------------------------


def test_404_ritorna_none(tmp_path):
    fetch = FetchFinto()  # nessuna risposta: tutto 404
    assert dati.scarica_mese("NUOVAUSDT", "klines", "1h", 2023, 1, tmp_path, fetch) is None
    assert len(fetch.chiamate) == 1
    assert not (tmp_path / "data" / "insample" / "NUOVAUSDT" / "klines" / "1h" / "NUOVAUSDT-1h-2023-01.zip").exists()
    # in un periodo i mesi assenti semplicemente non compaiono
    url_feb = dati.url_mese("NUOVAUSDT", "klines", "1h", 2023, 2)
    fetch = FetchFinto({url_feb: zip_in_memoria("b.csv", riga_kline(0, 1, 2, 0.5, 1.5, 3) + "\n")})
    percorsi = dati.scarica_periodo("NUOVAUSDT", "klines", "1h", date(2023, 1, 1), date(2023, 2, 28), tmp_path, fetch)
    assert [p.name for p in percorsi] == ["NUOVAUSDT-1h-2023-02.zip"]
    assert len(fetch.chiamate) == 2


def test_altri_errori_di_rete_sollevano(tmp_path):
    def fetch_rotto(url):
        raise OSError("rete giu'")

    with pytest.raises(OSError):
        dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 1, tmp_path, fetch_rotto)


# ---------------------------------------------------------------------------
# (8) aggrega_candele da 15m a 1h, con numeri a mano
# ---------------------------------------------------------------------------


def c15(k: int, o, h, l, c, v) -> Candela:
    """Candela da 15 minuti numero k dall'epoca."""
    return Candela(ts=k * QUARTO, open=o, high=h, low=l, close=c, volume=v, close_ts=k * QUARTO + QUARTO - 1)


def test_aggrega_15m_in_1h_numeri_a_mano():
    # Un'ora piena: i quarti 4,5,6,7 (dalle 01:00 alle 01:59 UTC).
    #   open = 10 (primo), high = max(12, 15, 13, 11) = 15, low = min(9, 11, 8, 10) = 8,
    #   close = 10.5 (ultimo), volume = 1 + 2 + 3 + 4 = 10.
    ora_piena = [
        c15(4, 10, 12, 9, 11, 1),
        c15(5, 11, 15, 11, 14, 2),
        c15(6, 14, 13, 8, 12, 3),
        c15(7, 12, 11, 10, 10.5, 4),
    ]
    # Ora incompleta: solo i quarti 9 e 10 (manca 8 e 11): scartata se solo_complete.
    ora_monca = [c15(9, 1, 2, 0.5, 1.5, 1), c15(10, 1.5, 3, 1, 2, 1)]
    # In disordine di proposito: l'aggregazione ordina.
    risultato = dati.aggrega_candele(ora_monca + list(reversed(ora_piena)), "1h")
    assert risultato == [Candela(ts=4 * QUARTO, open=10, high=15, low=8, close=10.5, volume=10, close_ts=2 * ORA - 1)]
    assert risultato[0].ts == ORA  # allineata all'ora piena 01:00 UTC

    # senza il filtro, l'ora monca compare con i soli due quarti
    tutte = dati.aggrega_candele(ora_monca + ora_piena, "1h", solo_complete=False)
    assert [c.ts for c in tutte] == [ORA, 2 * ORA]
    assert tutte[1] == Candela(ts=2 * ORA, open=1, high=3, low=0.5, close=2, volume=2, close_ts=3 * ORA - 1)

    # un quarto d'ora che inizia alle 00:45 appartiene all'ora 00:00, non all'ora 01:00
    assert dati.aggrega_candele([c15(3, 1, 1, 1, 1, 1)], "1h", solo_complete=False)[0].ts == 0


def test_aggrega_rifiuta_durate_non_divisibili():
    with pytest.raises(ValueError):
        dati.aggrega_candele([Candela(0, 1, 1, 1, 1, 1, 7 * 60_000 - 1)], "1h")  # 7 minuti non dividono 60
    with pytest.raises(ValueError):
        dati.durata_intervallo("1x")
    assert dati.durata_intervallo("15m") == QUARTO
    assert dati.durata_intervallo("4h") == 4 * ORA
    assert dati.durata_intervallo("1d") == 24 * ORA
    assert dati.aggrega_candele([], "1h") == []


# ---------------------------------------------------------------------------
# (9) file gia' su disco -> fetch non chiamato
# ---------------------------------------------------------------------------


def test_file_gia_su_disco_non_si_riscarica(tmp_path):
    url = dati.url_mese("BTCUSDT", "klines", "1h", 2023, 5)
    contenuto = zip_in_memoria("a.csv", riga_kline(0, 1, 2, 0.5, 1.5, 3) + "\n")
    primo = FetchFinto({url: contenuto})
    percorso = dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 5, tmp_path, primo)
    assert primo.chiamate == [url]

    secondo = FetchFinto({url: contenuto})
    assert dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 5, tmp_path, secondo) == percorso
    assert secondo.chiamate == []
    assert dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2023, 5, 1), date(2023, 5, 31), tmp_path, secondo) == [percorso]
    assert secondo.chiamate == []


# ---------------------------------------------------------------------------
# (10) lista_contratti parsa un exchangeInfo finto
# ---------------------------------------------------------------------------


def test_lista_contratti(tmp_path):
    finto = {
        "symbols": [
            {
                "symbol": "BTCUSDT",
                "status": "TRADING",
                "contractType": "PERPETUAL",
                "onboardDate": 1569398400000,
                "deliveryDate": 4133404800000,
                "quoteAsset": "USDT",
                "pricePrecision": 2,
            },
            {
                "symbol": "VECCHIOUSDT",
                "status": "SETTLING",
                "contractType": "PERPETUAL",
                "onboardDate": 1600000000000,
                "deliveryDate": 1700000000000,
                "quoteAsset": "USDT",
            },
        ]
    }
    fetch = FetchFinto({dati.URL_EXCHANGE_INFO: json.dumps(finto).encode()})
    contratti = dati.lista_contratti(fetch)
    assert fetch.chiamate == [dati.URL_EXCHANGE_INFO]
    assert contratti == [
        {
            "symbol": "BTCUSDT",
            "status": "TRADING",
            "contractType": "PERPETUAL",
            "onboardDate": 1569398400000,
            "deliveryDate": 4133404800000,
            "quoteAsset": "USDT",
        },
        {
            "symbol": "VECCHIOUSDT",
            "status": "SETTLING",
            "contractType": "PERPETUAL",
            "onboardDate": 1600000000000,
            "deliveryDate": 1700000000000,
            "quoteAsset": "USDT",
        },
    ]
    # la lista dei contratti non e' bloccata dal vault: nessun APERTURA.md in tmp_path
    assert not dati.vault_aperto(tmp_path)


# ---------------------------------------------------------------------------
# dettagli: percorsi, mesi del periodo, radice di default
# ---------------------------------------------------------------------------


def test_percorso_mese_separa_insample_e_vault(tmp_path):
    assert dati.percorso_mese("X", "klines", "1h", 2023, 12, tmp_path).parts[-5] == "insample"
    assert dati.percorso_mese("X", "klines", "1h", 2024, 1, tmp_path).parts[-5] == "vault"
    assert list(dati.mesi_del_periodo(date(2022, 11, 15), date(2023, 2, 1))) == [(2022, 11), (2022, 12), (2023, 1), (2023, 2)]
    with pytest.raises(ValueError):
        list(dati.mesi_del_periodo(date(2023, 2, 1), date(2023, 1, 1)))


def test_radice_default_e_la_cartella_research():
    assert dati.RADICE_DEFAULT.name == "research"
    assert (dati.RADICE_DEFAULT / "PROTOCOLLO.md").is_file()
    assert dati.FINE_IN_SAMPLE == date(2023, 12, 31)


# ---------------------------------------------------------------------------
# Correzioni dopo la revisione 1 (i test del revisore stanno in test_dati_revisione_1.py;
# qui restano i comportamenti nuovi che quel file non copre)
# ---------------------------------------------------------------------------


def test_prima_riga_corrotta_solleva_invece_di_sparire(tmp_path):
    """Una prima riga che non e' ne' un numero ne' un'intestazione nota e' un errore, non una riga da saltare."""
    percorso = tmp_path / "corrotto.zip"
    percorso.write_bytes(zip_in_memoria("x.csv", "boh,1,2,3,4,5,6\n" + riga_kline(0, 1, 2, 0.5, 1.5, 10) + "\n"))
    with pytest.raises(ValueError):
        dati.candele_da_zip(percorso)


def test_fine_vault_rifiuta_il_periodo_del_paper_anche_a_vault_aperto(tmp_path):
    """Settembre 2026 passa a vault aperto; ottobre 2026 (paper) no, e senza nemmeno una richiesta."""
    apri_vault(tmp_path)
    fetch = FetchFinto()
    dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2026, 9, 1), date(2026, 9, 30), tmp_path, fetch)
    assert len(fetch.chiamate) == 1
    with pytest.raises(dati.OltreIlVault):
        dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2026, 9, 1), date(2026, 10, 1), tmp_path, fetch)
    with pytest.raises(dati.OltreIlVault):
        dati.scarica_mese("BTCUSDT", "fundingRate", None, 2026, 10, tmp_path, fetch)
    with pytest.raises(dati.OltreIlVault):
        dati.carica_candele("BTCUSDT", "1h", date(2026, 9, 1), date(2026, 10, 1), tmp_path)
    assert len(fetch.chiamate) == 1
