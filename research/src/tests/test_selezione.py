"""Passo 1: la selezione delle monete (research/src/selezione.py), funzioni pure.

Cosa si protegge: le fasce di slippage; la lettura dei mesi dai nomi dei file;
il volume medio sui giorni presenti (non su 365), il doppione riconosciuto per
giorno UTC e l'ultimo giorno presente; le righe corrotte (NaN, infinito,
negativo) scartate una per una; i filtri con i motivi scritti (storia minima su
listing E primo mese, fine dei dati al mese e al giorno, volume), che ``valuta``
AGGIUNGE ai motivi gia' presenti senza doppioni; la copertura del 2023 che si
segnala e non esclude; l'ordine per volume, il taglio alle prime N e i doppioni
di simbolo; i conteggi per codice di motivo (dichiarati sovrapposti) e le
sospette ridenominazioni; la scheda della moneta identica per una moneta viva
e una delistata; l'indice dei file con la paginazione (fetch finto), che
solleva invece di tornare a meta'.
"""
from datetime import date

import pytest

from research.src import selezione as sel

MS_G = 86_400_000
T2023 = 1_672_531_200_000   # 2023-01-01 00:00 UTC


def _cand(simbolo, oggi=True, listing=date(2020, 1, 1), ultimo=date(2023, 12, 31),
          volume=100e6, giorni=365, primo=date(2020, 1, 1), ultimo_giorno=None):
    return sel.Candidata(simbolo=simbolo, negoziata_oggi=oggi, listing=listing,
                         listing_da="exchangeInfo" if oggi else "archivio", primo_mese=primo,
                         ultimo_mese=ultimo, volume_medio_2023=volume, giorni_2023=giorni,
                         ultimo_giorno_2023=ultimo_giorno)


def test_fasce_di_slippage():
    assert sel.fascia_slippage(2e9) == 0.0001
    assert sel.fascia_slippage(1e9) == 0.0001          # soglia inclusa
    assert sel.fascia_slippage(500e6) == 0.0002
    assert sel.fascia_slippage(60e6) == 0.0005
    assert sel.fascia_slippage(20e6) == 0.0010
    assert sel.fascia_slippage(19.9e6) is None
    assert sel.fascia_slippage(None) is None
    # un volume non leggibile non ha fascia (inf starebbe nella prima)
    assert sel.fascia_slippage(float("nan")) is None and sel.fascia_slippage(float("inf")) is None


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


def _riga(ts, quote_volume):
    return [str(ts), "1", "2", "0.5", "1.5", "10", "0", str(quote_volume), "3", "1", "1", "0"]


def test_volume_quote_dalle_righe_csv():
    righe = [["1672531200000", "1", "2", "0.5", "1.5", "10", "1672617599999", "12345.5", "3", "1", "1", "0"],
             ["x", "1"], ["1672617600000", "1", "2", "0.5", "1.5", "10", "1672703999999", "abc"]]
    assert sel.volume_quote_giornaliero(righe) == [(1672531200000, 12345.5)]


def test_righe_corrotte_scartate_una_per_una():
    # NaN e infinito non sollevano in float(): entrerebbero nella media (NaN) o
    # metterebbero la moneta prima di BTC (inf); un negativo abbasserebbe l'anno;
    # un open_time infinito solleva OverflowError, che prima faceva saltare il file
    righe = [_riga(T2023, 100.0), _riga(T2023 + MS_G, "nan"), _riga(T2023 + 2 * MS_G, "inf"),
             _riga(T2023 + 3 * MS_G, "-5e9"), _riga("inf", 5.0), _riga("nan", 5.0),
             _riga(T2023 + 4 * MS_G, 7.0)]
    assert sel.volume_quote_giornaliero(righe) == [(T2023, 100.0), (T2023 + 4 * MS_G, 7.0)]


def test_volume_medio_sui_giorni_presenti_copertura_e_ultimo_giorno():
    giorni = [(T2023 + i * MS_G, 100.0) for i in range(10)] + [(T2023 - MS_G, 1e9), (T2023 + 400 * MS_G, 1e9)]
    media, n, ultimo = sel.volume_medio_nella_finestra(giorni)
    assert media == 100.0 and n == 10              # fuori finestra ignorati, media sui presenti
    assert ultimo == T2023 + 9 * MS_G              # mezzanotte UTC dell'ultimo giorno presente
    giorni2 = giorni + [(T2023, 100.0)]            # doppione identico: non raddoppia
    assert sel.volume_medio_nella_finestra(giorni2) == (100.0, 10, T2023 + 9 * MS_G)
    # doppione dello stesso giorno con millisecondi diversi: un giorno solo, vince l'ultimo
    giorni3 = [(T2023, 100.0), (T2023 + 1, 300.0)]
    assert sel.volume_medio_nella_finestra(giorni3) == (300.0, 1, T2023)
    # mai piu' giorni dei giorni della finestra, anche con mille doppioni
    tanti = [(T2023 + (i % 365) * MS_G + (i // 365), 1.0) for i in range(365 * 3)]
    assert sel.volume_medio_nella_finestra(tanti)[1] == 365
    assert sel.volume_medio_nella_finestra([]) == (None, 0, None)


def test_filtri_con_motivi():
    assert sel.valuta(_cand("OKUSDT")).motivi_esclusione == []
    c = sel.valuta(_cand("NEWUSDT", listing=date(2022, 1, 1)))
    assert any("listing 2022-01-01" in m for m in c.motivi_esclusione)
    c = sel.valuta(_cand("NOLISTUSDT", listing=None))
    assert "data di listing sconosciuta" in c.motivi_esclusione
    # la storia minima e' sui dati: quotata nel 2021 ma con il primo file nel 2022 non basta
    c = sel.valuta(_cand("LATEUSDT", listing=date(2021, 6, 1), primo=date(2022, 6, 1)))
    assert any(m.startswith("dati nell'archivio che cominciano il 2022-06-01") for m in c.motivi_esclusione)
    c = sel.valuta(_cand("NOPRIMOUSDT", primo=None))
    assert "primo mese nell'archivio sconosciuto" in c.motivi_esclusione
    c = sel.valuta(_cand("DEADUSDT", oggi=False, ultimo=date(2023, 6, 30)))
    assert any("prima del 2023-12" in m for m in c.motivi_esclusione)
    # fine dei dati al giorno: il file 2023-12 c'e' ma l'ultima candela e' del 17
    c = sel.valuta(_cand("DECUSDT", oggi=False, giorni=351, ultimo_giorno=date(2023, 12, 17)))
    assert any(m.startswith("dati che finiscono il 2023-12-17") for m in c.motivi_esclusione)
    assert sel.valuta(_cand("FULLUSDT", ultimo_giorno=date(2023, 12, 31))).motivi_esclusione == []
    c = sel.valuta(_cand("THINUSDT", volume=5e6))
    assert any("sotto" in m for m in c.motivi_esclusione)
    c = sel.valuta(_cand("NANUSDT", volume=float("nan")))
    assert "volume 2023 non leggibile" in c.motivi_esclusione
    c = sel.valuta(_cand("NOVOLUSDT", volume=None, giorni=0))
    assert "nessun volume nel 2023" in c.motivi_esclusione


def test_copertura_del_2023_si_segnala_e_non_esclude():
    # ne' il protocollo ne' parametri.yaml fissano un minimo di giorni: 200 giorni
    # restano idonei, ma ``seleziona`` li elenca per lo STOP
    c = sel.valuta(_cand("HOLEUSDT", giorni=200))
    assert c.motivi_esclusione == []
    r = sel.seleziona([_cand("HOLEUSDT", giorni=200), _cand("OKUSDT", giorni=360),
                       _cand("THINUSDT", giorni=100, volume=1e6)], n=1)
    assert r["copertura_incompleta"] == ["HOLEUSDT"]        # solo le idonee
    assert r["conteggi"]["idonee_con_copertura_incompleta"] == 1
    assert r["conteggi"]["idonee"] == 2


def test_valuta_aggiunge_ai_motivi_e_non_duplica():
    c = _cand("ERRUSDT", volume=None, giorni=0)
    c.motivi_esclusione = [sel.MOTIVO_ERRORE_SCARICO + "zip rotto"]
    sel.valuta(c)
    # il motivo del chiamante resta, e «nessun volume» non si aggiunge: sarebbe falso
    assert c.motivi_esclusione == [sel.MOTIVO_ERRORE_SCARICO + "zip rotto"]
    # valutare due volte non raddoppia i motivi
    c = _cand("THINUSDT", volume=5e6, listing=date(2023, 1, 1))
    sel.valuta(c)
    prima = list(c.motivi_esclusione)
    sel.valuta(c)
    assert c.motivi_esclusione == prima and len(prima) == 2


def test_codici_dei_motivi():
    assert sel.codice_motivo("data di listing sconosciuta") == "listing_sconosciuto"
    assert sel.codice_motivo("listing 2022-03-01, non prima del 2022-01-01") == "listing"
    assert sel.codice_motivo("dati che finiscono prima del 2023-12") == "fine_dati"
    assert sel.codice_motivo("dati che finiscono il 2023-12-17 (prima del 2023-12-31)") == "fine_dati_giorno"
    assert sel.codice_motivo("errore nello scarico del 2023: x") == "errore_scarico"
    assert sel.codice_motivo("qualcosa d'altro") == sel.CODICE_ALTRO
    # nessun prefisso e' l'inizio di un altro con codice diverso
    for codice, prefisso in sel.CODICI_MOTIVO:
        for altro, altro_prefisso in sel.CODICI_MOTIVO:
            if codice != altro:
                assert not altro_prefisso.startswith(prefisso), (codice, altro)


def test_selezione_ordine_taglio_e_sopravvivenza():
    candidate = [_cand("AUSDT", volume=300e6), _cand("BUSDT", volume=900e6),
                 _cand("CUSDT", volume=50e6, oggi=False, ultimo=date(2024, 6, 30)),   # morta nel vault
                 _cand("DUSDT", volume=10e6), _cand("EUSDT", listing=date(2023, 1, 1), volume=5e9),
                 _cand("FUSDT", oggi=False, ultimo=date(2023, 3, 31), volume=1e9),     # morta prima del 2024
                 _cand("GUSDT", listing=None, volume=1e9)]                             # senza data
    r = sel.seleziona(candidate, n=2)
    assert [c.simbolo for c in r["campagna"]] == ["BUSDT", "AUSDT"]
    assert [c.simbolo for c in r["altre_idonee"]] == ["CUSDT"]
    assert {c.simbolo for c in r["escluse"]} == {"DUSDT", "EUSDT", "FUSDT", "GUSDT"}
    k = r["conteggi"]
    assert k["candidate"] == 7 and k["idonee"] == 3 and k["campagna"] == 2 and k["escluse"] == 4
    assert k["idonee_delistate_oggi"] == 1 and k["campagna_delistate_oggi"] == 0
    # i conteggi per motivo vanno per codice: la data sconosciuta non e' un listing tardivo
    assert k["escluse_per_listing"] == 1 and k["escluse_per_listing_sconosciuto"] == 1
    assert k["escluse_per_fine_dati"] == 1 and k["escluse_per_fine_dati_giorno"] == 0
    assert k["escluse_per_volume"] == 1 and k["escluse_per_errore_scarico"] == 0
    # a parita' di volume vince l'ordine alfabetico: scelta deterministica
    r2 = sel.seleziona([_cand("ZUSDT"), _cand("MUSDT")], n=1)
    assert r2["campagna"][0].simbolo == "MUSDT"


def test_conteggi_per_motivo_si_sovrappongono_e_lo_si_dichiara():
    r = sel.seleziona([_cand("XUSDT", listing=date(2023, 1, 1), volume=1e6)], n=1)
    k = r["conteggi"]
    assert k["escluse"] == 1 and k["escluse_per_listing"] == 1 and k["escluse_per_volume"] == 1
    assert "SOVRAPPONGONO" in sel.seleziona.__doc__


def test_doppione_di_simbolo_occupa_un_posto_solo():
    primo = _cand("AUSDT", volume=500e6)
    r = sel.seleziona([primo, _cand("AUSDT", volume=900e6), _cand("BUSDT", volume=50e6)], n=2)
    assert [c.simbolo for c in r["campagna"]] == ["AUSDT", "BUSDT"]
    assert r["campagna"][0] is primo                        # resta la prima occorrenza
    assert r["conteggi"]["candidate"] == 2 and r["conteggi"]["doppioni_scartati"] == 1


def test_sospette_ridenominazioni_si_elencano_e_non_si_cuciono():
    vecchia = _cand("OLDUSDT", oggi=False, ultimo=date(2023, 5, 31), volume=500e6, giorni=151)
    nuova = _cand("NEWUSDT", listing=date(2023, 6, 1), primo=date(2023, 6, 1), volume=500e6, giorni=214)
    morta_2021 = _cand("ANTICAUSDT", oggi=False, ultimo=date(2021, 8, 31), volume=None)
    morta_vault = _cand("DEADUSDT", oggi=False, ultimo=date(2024, 6, 30))
    senza_data = _cand("NODATEUSDT", listing=None, primo=date(2022, 2, 1))
    r = sel.seleziona([vecchia, nuova, morta_2021, morta_vault, senza_data, _cand("OKUSDT")], n=1)
    # nessuna cucitura automatica: le due meta' restano escluse, l'utente decide allo STOP
    assert {c.simbolo for c in r["escluse"]} >= {"OLDUSDT", "NEWUSDT"}
    s = r["sospette_ridenominazioni"]
    assert s["sparite_2022_2023"] == ["OLDUSDT"]              # non nel 2021, non nel vault
    assert s["listate_2022_2023"] == ["NEWUSDT", "NODATEUSDT"]  # senza listing vale il primo mese
    assert r["conteggi"]["sospette_sparite_2022_2023"] == 1 and r["conteggi"]["sospette_listate_2022_2023"] == 2
    assert all(c.serie_collegata == c.simbolo for c in r["escluse"] + r["campagna"])


def test_delisting_anni_storia_e_serie_collegata():
    viva = _cand("AUSDT"); morta = _cand("BUSDT", oggi=False, ultimo=date(2024, 6, 30))
    assert viva.delisting is None and morta.delisting == date(2024, 6, 30)
    assert _cand("X", listing=date(2022, 1, 1)).anni_storia == 2.0
    assert viva.serie_collegata == "AUSDT"                   # per default la serie e' il simbolo stesso
    assert "serie_collegata" in sel.COLONNE_CSV and "ultimo_giorno_2023" in sel.COLONNE_CSV


def test_riga_csv_con_volume_non_leggibile():
    riga = sel.riga_csv(sel.valuta(_cand("NANUSDT", volume=float("nan"))))
    assert riga["volume_medio_2023_usdt"] == "" and riga["fascia_slippage"] == ""
    assert riga["serie_collegata"] == "NANUSDT" and riga["ultimo_giorno_2023"] == ""
    assert sel.riga_csv(_cand("OKUSDT", ultimo_giorno=date(2023, 12, 31)))["ultimo_giorno_2023"] == "2023-12-31"


def test_scheda_moneta_senza_informazioni_dopo_il_2023():
    morta = _cand("AUSDT", oggi=False, ultimo=date(2024, 6, 30), volume=300e6)
    viva = _cand("AUSDT", oggi=True, volume=300e6)
    testo = sel.scheda_moneta(morta)
    assert "`AUSDT`" in testo and "2020-01-01" in testo and "0.0200%" in testo and "2023-12-31" in testo
    assert "2024" not in testo and "delist" not in testo.lower()
    # la fonte della data direbbe «delistata»: non c'e'; la riga sull'approssimazione e' per tutte
    assert "archivio" not in testo and "exchangeInfo" not in testo
    assert "La data di listing può essere approssimata al primo giorno del mese." in testo
    assert "serie" not in testo.lower()
    # stessi dati al 2023-12-31: stessa scheda, viva o morta che sia
    assert sel.scheda_moneta(viva) == testo


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
    # solo le chiavi sotto il prefisso: un altro simbolo non diventa un mese di questo
    altrove = "data/futures/um/monthly/klines/ETHUSDT/1d/ETHUSDT-1d-2019-12.zip"
    assert sel.elenca_file_archivio("BTCUSDT", fetch=lambda u: _pagina([altrove, p + "BTCUSDT-1d-2020-01.zip"])) \
        == ["BTCUSDT-1d-2020-01.zip"]
    # il funding non ha il livello dell'intervallo
    assert sel.prefisso_archivio("BTCUSDT", None, "fundingRate") == "data/futures/um/monthly/fundingRate/BTCUSDT/"
    with pytest.raises(ValueError):
        sel.prefisso_archivio("BTCUSDT", None, "klines")


def test_elenca_file_archivio_mai_una_lista_parziale_in_silenzio():
    p = "data/futures/um/monthly/klines/BTCUSDT/1d/"
    # un marker che non avanza: errore, non un elenco doppio
    with pytest.raises(RuntimeError):
        sel.elenca_file_archivio("BTCUSDT", fetch=lambda u: _pagina([p + "a.zip"], troncata=True, prossimo="z"))
    # un marker che torna indietro: errore subito, non 100 pagine
    chiamate = []

    def indietro(url):
        chiamate.append(url)
        return _pagina([p + "b.zip"], troncata=True, prossimo="y" if "marker=z" in url else "z")
    with pytest.raises(RuntimeError):
        sel.elenca_file_archivio("BTCUSDT", fetch=indietro)
    assert len(chiamate) == 2
    # una pagina troncata senza chiavi e senza marker: errore
    with pytest.raises(RuntimeError):
        sel.elenca_file_archivio("BTCUSDT", fetch=lambda u: _pagina([], troncata=True))
    # ancora troncata dopo il massimo di pagine: errore
    conta = [0]

    def infinita(url):
        conta[0] += 1
        return _pagina([p + f"{conta[0]:05d}.zip"], troncata=True)
    with pytest.raises(RuntimeError):
        sel.elenca_file_archivio("BTCUSDT", fetch=infinita)
    assert conta[0] == 100
