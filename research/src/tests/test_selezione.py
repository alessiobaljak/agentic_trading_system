"""Passo 1: la selezione delle monete (research/src/selezione.py), funzioni pure.

Cosa si protegge: le fasce di slippage; la lettura dei mesi dai nomi dei file;
il volume medio sui giorni presenti (non su 365) e la copertura; i quattro
filtri con i motivi scritti; l'ordine per volume e il taglio alle prime N; i
conteggi della sopravvivenza; la scheda della moneta senza informazioni
successive al 2023; l'indice dei file con la paginazione (fetch finto).
"""
from datetime import date

import pytest

from research.src import selezione as sel

MS_G = 86_400_000
T2023 = 1_672_531_200_000   # 2023-01-01 00:00 UTC


def _cand(simbolo, oggi=True, listing=date(2020, 1, 1), ultimo=date(2023, 12, 31),
          volume=100e6, giorni=365, primo=date(2020, 1, 1)):
    return sel.Candidata(simbolo=simbolo, negoziata_oggi=oggi, listing=listing,
                         listing_da="exchangeInfo" if oggi else "archivio", primo_mese=primo,
                         ultimo_mese=ultimo, volume_medio_2023=volume, giorni_2023=giorni)


def test_fasce_di_slippage():
    assert sel.fascia_slippage(2e9) == 0.0001
    assert sel.fascia_slippage(1e9) == 0.0001          # soglia inclusa
    assert sel.fascia_slippage(500e6) == 0.0002
    assert sel.fascia_slippage(60e6) == 0.0005
    assert sel.fascia_slippage(20e6) == 0.0010
    assert sel.fascia_slippage(19.9e6) is None
    assert sel.fascia_slippage(None) is None


def test_perpetui_usdt():
    assert sel.e_perpetuo_usdt("BTCUSDT") and sel.e_perpetuo_usdt("1000SHIBUSDT")
    assert not sel.e_perpetuo_usdt("BTCUSDT_210326")   # trimestrale
    assert not sel.e_perpetuo_usdt("BTCUSDC") and not sel.e_perpetuo_usdt("ETHBTC")


def test_mesi_dai_nomi_e_primo_ultimo():
    chiavi = ["BTCUSDT-1d-2023-03.zip", "BTCUSDT-1d-2023-03.zip.CHECKSUM",
              "BTCUSDT-1d-2020-01.zip", "BTCUSDT-1d-2021-12.zip", "spazzatura.txt"]
    assert sel.mesi_dai_nomi(chiavi) == [(2020, 1), (2021, 12), (2023, 3)]
    assert sel.primo_e_ultimo_mese(chiavi) == (date(2020, 1, 1), date(2023, 3, 31))
    assert sel.primo_e_ultimo_mese([]) == (None, None)
    assert sel.fine_mese(2023, 2) == date(2023, 2, 28) and sel.fine_mese(2024, 2) == date(2024, 2, 29)
    assert sel.fine_mese(2023, 12) == date(2023, 12, 31)


def test_volume_quote_dalle_righe_csv():
    righe = [["1672531200000", "1", "2", "0.5", "1.5", "10", "1672617599999", "12345.5", "3", "1", "1", "0"],
             ["x", "1"], ["1672617600000", "1", "2", "0.5", "1.5", "10", "1672703999999", "abc"]]
    assert sel.volume_quote_giornaliero(righe) == [(1672531200000, 12345.5)]


def test_volume_medio_sui_giorni_presenti_e_copertura():
    giorni = [(T2023 + i * MS_G, 100.0) for i in range(10)] + [(T2023 - MS_G, 1e9), (T2023 + 400 * MS_G, 1e9)]
    media, n = sel.volume_medio_nella_finestra(giorni)
    assert media == 100.0 and n == 10              # fuori finestra ignorati, media sui presenti
    giorni2 = giorni + [(T2023, 100.0)]            # doppione: non raddoppia
    assert sel.volume_medio_nella_finestra(giorni2) == (100.0, 10)
    assert sel.volume_medio_nella_finestra([]) == (None, 0)


def test_filtri_con_motivi():
    assert sel.valuta(_cand("OKUSDT")).motivi_esclusione == []
    c = sel.valuta(_cand("NEWUSDT", listing=date(2022, 1, 1)))
    assert any("listing 2022-01-01" in m for m in c.motivi_esclusione)
    c = sel.valuta(_cand("DEADUSDT", oggi=False, ultimo=date(2023, 6, 30)))
    assert any("prima del 2023-12" in m for m in c.motivi_esclusione)
    c = sel.valuta(_cand("THINUSDT", volume=5e6))
    assert any("sotto" in m for m in c.motivi_esclusione)
    c = sel.valuta(_cand("HOLEUSDT", giorni=200))
    assert any("200 giorni" in m for m in c.motivi_esclusione)
    c = sel.valuta(_cand("NOVOLUSDT", volume=None, giorni=0))
    assert "nessun volume nel 2023" in c.motivi_esclusione
    c = sel.valuta(_cand("NOLISTUSDT", listing=None))
    assert "data di listing sconosciuta" in c.motivi_esclusione


def test_selezione_ordine_taglio_e_sopravvivenza():
    candidate = [_cand("AUSDT", volume=300e6), _cand("BUSDT", volume=900e6),
                 _cand("CUSDT", volume=50e6, oggi=False, ultimo=date(2024, 6, 30)),   # morta nel vault
                 _cand("DUSDT", volume=10e6), _cand("EUSDT", listing=date(2023, 1, 1), volume=5e9),
                 _cand("FUSDT", oggi=False, ultimo=date(2023, 3, 31), volume=1e9)]      # morta prima del 2024
    r = sel.seleziona(candidate, n=2)
    assert [c.simbolo for c in r["campagna"]] == ["BUSDT", "AUSDT"]
    assert [c.simbolo for c in r["altre_idonee"]] == ["CUSDT"]
    assert {c.simbolo for c in r["escluse"]} == {"DUSDT", "EUSDT", "FUSDT"}
    k = r["conteggi"]
    assert k["candidate"] == 6 and k["idonee"] == 3 and k["campagna"] == 2
    assert k["idonee_delistate_oggi"] == 1 and k["campagna_delistate_oggi"] == 0
    assert k["escluse_per_listing"] == 1 and k["escluse_per_fine_dati"] == 1 and k["escluse_per_volume"] == 1
    # a parita' di volume vince l'ordine alfabetico: scelta deterministica
    r2 = sel.seleziona([_cand("ZUSDT"), _cand("MUSDT")], n=1)
    assert r2["campagna"][0].simbolo == "MUSDT"


def test_delisting_e_anni_storia():
    viva = _cand("AUSDT"); morta = _cand("BUSDT", oggi=False, ultimo=date(2024, 6, 30))
    assert viva.delisting is None and morta.delisting == date(2024, 6, 30)
    assert _cand("X", listing=date(2022, 1, 1)).anni_storia == 2.0


def test_scheda_moneta_senza_informazioni_dopo_il_2023():
    c = _cand("AUSDT", oggi=False, ultimo=date(2024, 6, 30), volume=300e6)
    testo = sel.scheda_moneta(c)
    assert "`AUSDT`" in testo and "2020-01-01" in testo and "0.0200%" in testo and "2023-12-31" in testo
    assert "2024" not in testo and "delist" not in testo.lower()


def _pagina(chiavi, troncata=False, prossimo=None):
    corpo = "".join(f"<Contents><Key>{k}</Key></Contents>" for k in chiavi)
    nm = f"<NextMarker>{prossimo}</NextMarker>" if prossimo else ""
    return (f'<?xml version="1.0"?><ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
            f"<Prefix>p</Prefix><IsTruncated>{'true' if troncata else 'false'}</IsTruncated>{nm}{corpo}"
            f"</ListBucketResult>").encode()


def test_elenca_file_archivio_pagina_e_url():
    p = "data/futures/um/monthly/klines/BTCUSDT/1d/"
    chiamate = []

    def fetch(url):
        chiamate.append(url)
        if "marker=" not in url:
            return _pagina([p + "BTCUSDT-1d-2020-01.zip", p + "BTCUSDT-1d-2020-01.zip.CHECKSUM"], troncata=True)
        return _pagina([p + "BTCUSDT-1d-2023-12.zip"])
    nomi = sel.elenca_file_archivio("BTCUSDT", "1d", fetch=fetch)
    assert nomi == ["BTCUSDT-1d-2020-01.zip", "BTCUSDT-1d-2020-01.zip.CHECKSUM", "BTCUSDT-1d-2023-12.zip"]
    assert len(chiamate) == 2 and chiamate[0].endswith("?prefix=" + p) and "marker=" in chiamate[1]
    assert sel.url_indice_file(p).startswith("https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?prefix=")
    with pytest.raises(RuntimeError):
        sel.elenca_file_archivio("XUSDT", fetch=lambda u: None)
    # un marker che non avanza non fa girare all'infinito
    assert sel.elenca_file_archivio("YUSDT", fetch=lambda u: _pagina([p + "a.zip"], troncata=True, prossimo="z" if "marker=z" not in u else "z")) == ["a.zip", "a.zip"]
