"""Test del caricatore unico per last e mark (``dati.carica_serie_allineate``) e del
volume in USDT (``dati.volume_usdt_da_zip``), tutti SENZA rete.

Gli zip sono finti, scritti a mano in una cartella temporanea nei percorsi in cui
li mette ``scarica_mese``. Si verifica:

1. l'intersezione delle barre quando last e mark hanno buchi in punti diversi
   (anche un giorno intero), con le barre tolte elencate e contate dalle due parti;
2. il volume in USDT letto dalla colonna ``quote_volume`` (indice 7), con e senza
   intestazione, con BOM e con ts in microsecondi; un volume assente e' ``None``
   e si conta, un volume corrotto solleva;
3. l'aggregazione da 15m a 1h: somma dei quote_volume del gruppo, gruppi
   incompleti scartati e contati;
4. il blocco del vault PRIMA di qualunque accesso al disco;
5. una serie vuota: risultato vuoto, conteggi presenti, nessuna eccezione.
"""

from datetime import date
from pathlib import Path
from typing import List, Optional, Sequence

import pytest

from research.src import dati
from research.src.dati import OltreIlVault, VaultChiuso
from research.src.motore import Candela, Parametri, esegui
from research.src.tests.test_dati import (
    INTESTAZIONE_KLINES,
    ORA,
    QUARTO,
    TS_2023_01_01,
    TS_2023_02_01,
    apri_vault,
    zip_in_memoria,
)

GIORNO = 24 * ORA
SIMBOLO = "BTCUSDT"


def riga(
    ts: int,
    prezzo: float,
    qv: Optional[object] = None,
    durata: int = ORA,
    micro: bool = False,
    volume: float = 2.0,
) -> str:
    """Una riga klines di Binance con il quote_volume scelto a mano.

    ``qv=None`` scrive una riga di soli 7 campi (manca la colonna del volume in
    USDT); una stringa (anche vuota) finisce nella colonna tale e quale. Con
    ``micro`` apertura e chiusura sono in microsecondi, come in alcuni file dal 2025.
    """
    close_ts = ts + durata - 1
    ts_testo, close_testo = (ts * 1000, close_ts * 1000 + 999) if micro else (ts, close_ts)
    campi: List[object] = [ts_testo, prezzo, prezzo + 1, prezzo - 1, prezzo + 0.5, volume, close_testo]
    if qv is not None:
        campi += [qv, 10, volume / 2, 0, 0]
    return ",".join(str(c) for c in campi)


def scrivi_mese(
    radice: Path,
    tipo: str,
    intervallo: str,
    anno: int,
    mese: int,
    righe: Sequence[str],
    intestazione: bool = False,
    bom: bool = False,
) -> Path:
    """Scrive lo zip del mese dove lo metterebbe ``scarica_mese`` e ne ritorna il percorso."""
    percorso = dati.percorso_mese(SIMBOLO, tipo, intervallo, anno, mese, radice)
    percorso.parent.mkdir(parents=True, exist_ok=True)
    testo = ("﻿" if bom else "") + (INTESTAZIONE_KLINES + "\n" if intestazione else "") + "\n".join(righe) + "\n"
    percorso.write_bytes(zip_in_memoria(percorso.stem + ".csv", testo))
    return percorso


def ora(k: int) -> int:
    """Apertura dell'ora numero ``k`` dal 2023-01-01 00:00 UTC."""
    return TS_2023_01_01 + k * ORA


def quarto(k: int) -> int:
    """Apertura del quarto d'ora numero ``k`` dal 2023-01-01 00:00 UTC."""
    return TS_2023_01_01 + k * QUARTO


GENNAIO = (date(2023, 1, 1), date(2023, 1, 31))


# ---------------------------------------------------------------------------
# (1) intersezione con buchi diversi nelle due serie
# ---------------------------------------------------------------------------


def test_intersezione_con_buchi_diversi_e_conteggi(tmp_path):
    # last: ore 0..9 senza la 3; mark: ore 0..9 senza la 6 e la 7
    scrivi_mese(tmp_path, "klines", "1h", 2023, 1, [riga(ora(k), 100 + k, qv=1000 + k) for k in range(10) if k != 3])
    scrivi_mese(tmp_path, "markPriceKlines", "1h", 2023, 1, [riga(ora(k), 200 + k, qv=0) for k in range(10) if k not in (6, 7)])

    serie = dati.carica_serie_allineate(SIMBOLO, "1h", *GENNAIO, radice=tmp_path)

    tenute = [0, 1, 2, 4, 5, 8, 9]
    assert [c.ts for c in serie["candele"]] == [ora(k) for k in tenute]
    assert [c.ts for c in serie["candele_mark"]] == [ora(k) for k in tenute]
    # i prezzi vengono ciascuno dal suo file: last 100+k, mark 200+k
    assert [c.open for c in serie["candele"]] == [100 + k for k in tenute]
    assert [c.open for c in serie["candele_mark"]] == [200 + k for k in tenute]
    assert serie["tolte_last"] == [ora(6), ora(7)]  # nel last ma non nel mark
    assert serie["tolte_mark"] == [ora(3)]  # nel mark ma non nel last
    assert serie["n_tolte_last"] == 2 and serie["n_tolte_mark"] == 1
    assert serie["volume_usdt"] == {ora(k): 1000 + k for k in tenute}
    assert serie["n_volume_mancante"] == 0
    assert serie["n_gruppi_incompleti_last"] == 0 and serie["n_gruppi_incompleti_mark"] == 0

    # il motore le accetta cosi' come sono: nessuna barra manca ad allinea_serie,
    # e i buchi rimasti (ore 3, 6, 7) li conta lui
    risultato = esegui(serie["candele"], None, serie["candele_mark"], [], lambda storia, pos: None, Parametri())
    assert risultato.trades == []


def test_un_giorno_intero_senza_mark_in_un_altro_mese(tmp_path):
    # Gennaio: ultimi due giorni, completi in entrambe le serie. Febbraio: primi tre
    # giorni nel last; il mark non ha il 2 febbraio (24 ore) e ha in piu' un'ora del 4.
    gen = [TS_2023_02_01 - 2 * GIORNO + h * ORA for h in range(48)]
    feb_last = [TS_2023_02_01 + h * ORA for h in range(72)]
    feb_mark = [ts for ts in feb_last if not (GIORNO <= ts - TS_2023_02_01 < 2 * GIORNO)] + [TS_2023_02_01 + 72 * ORA]
    scrivi_mese(tmp_path, "klines", "1h", 2023, 1, [riga(ts, 10, qv=1) for ts in gen])
    scrivi_mese(tmp_path, "markPriceKlines", "1h", 2023, 1, [riga(ts, 10, qv=0) for ts in gen])
    scrivi_mese(tmp_path, "klines", "1h", 2023, 2, [riga(ts, 10, qv=1) for ts in feb_last])
    scrivi_mese(tmp_path, "markPriceKlines", "1h", 2023, 2, [riga(ts, 10, qv=0) for ts in feb_mark])

    serie = dati.carica_serie_allineate(SIMBOLO, "1h", date(2023, 1, 1), date(2023, 2, 28), radice=tmp_path)

    assert serie["n_tolte_last"] == 24
    assert serie["tolte_last"] == [TS_2023_02_01 + GIORNO + h * ORA for h in range(24)]
    assert serie["tolte_mark"] == [TS_2023_02_01 + 72 * ORA]
    assert len(serie["candele"]) == 48 + 72 - 24
    assert [c.ts for c in serie["candele"]] == [c.ts for c in serie["candele_mark"]]
    assert sum(serie["volume_usdt"].values()) == 48 + 72 - 24


# ---------------------------------------------------------------------------
# (2) volume in USDT dalla colonna quote_volume
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("con_intestazione", [False, True])
@pytest.mark.parametrize("micro", [False, True])
def test_volume_usdt_da_quote_volume(tmp_path, con_intestazione, micro):
    # quote_volume scelti diversi da volume x close: se si leggesse un'altra colonna, il test lo vede
    righe = [riga(ora(0), 100, qv=1234.5, micro=micro), riga(ora(1), 101, qv=678.25, micro=micro)]
    percorso = scrivi_mese(tmp_path, "klines", "1h", 2023, 1, righe, intestazione=con_intestazione)
    assert dati.volume_usdt_da_zip(percorso) == {ora(0): 1234.5, ora(1): 678.25}
    # le chiavi sono gli stessi ts delle candele dello stesso file
    assert [c.ts for c in dati.candele_da_zip(percorso)] == [ora(0), ora(1)]


def test_volume_usdt_con_bom_senza_intestazione_non_perde_la_prima_riga(tmp_path):
    percorso = scrivi_mese(tmp_path, "klines", "1h", 2023, 1, [riga(ora(0), 100, qv=7), riga(ora(1), 100, qv=8)], bom=True)
    assert dati.volume_usdt_da_zip(percorso) == {ora(0): 7.0, ora(1): 8.0}


def test_volume_usdt_assente_non_e_zero_e_doppione_non_presta_il_suo(tmp_path):
    righe = [
        riga(ora(0), 100, qv=5),
        riga(ora(1), 100, qv=None),  # 7 campi: la colonna manca
        riga(ora(2), 100, qv=""),  # colonna vuota
        riga(ora(1), 100, qv=99),  # doppione dell'ora 1: vale la prima riga, senza volume
    ]
    percorso = scrivi_mese(tmp_path, "klines", "1h", 2023, 1, righe)
    assert dati.volume_usdt_da_zip(percorso) == {ora(0): 5.0}


@pytest.mark.parametrize("valore", ["abc", "nan", "inf", "-1"])
def test_volume_usdt_corrotto_solleva(tmp_path, valore):
    percorso = scrivi_mese(tmp_path, "klines", "1h", 2023, 1, [riga(ora(0), 100, qv=1), riga(ora(1), 100, qv=valore)])
    with pytest.raises(ValueError, match="quote_volume"):
        dati.volume_usdt_da_zip(percorso)


def test_volume_usdt_solo_dai_file_klines(tmp_path):
    percorso = scrivi_mese(tmp_path, "markPriceKlines", "1h", 2023, 1, [riga(ora(0), 100, qv=1)])
    with pytest.raises(ValueError, match="markPriceKlines"):
        dati.volume_usdt_da_zip(percorso)


def test_barra_tenuta_senza_volume_e_none_e_si_conta(tmp_path):
    scrivi_mese(tmp_path, "klines", "1h", 2023, 1, [riga(ora(0), 100, qv=3), riga(ora(1), 100, qv=None), riga(ora(2), 100, qv=4)])
    scrivi_mese(tmp_path, "markPriceKlines", "1h", 2023, 1, [riga(ora(k), 100, qv=0) for k in range(3)])
    serie = dati.carica_serie_allineate(SIMBOLO, "1h", *GENNAIO, radice=tmp_path)
    assert serie["volume_usdt"] == {ora(0): 3.0, ora(1): None, ora(2): 4.0}
    assert serie["n_volume_mancante"] == 1
    assert len(serie["candele"]) == 3  # la barra senza volume resta: manca il volume, non il prezzo


def test_volume_usdt_con_ts_in_microsecondi_dentro_il_caricatore(tmp_path):
    scrivi_mese(tmp_path, "klines", "1h", 2023, 1, [riga(ora(k), 100, qv=10 * (k + 1), micro=True) for k in range(3)], intestazione=True)
    scrivi_mese(tmp_path, "markPriceKlines", "1h", 2023, 1, [riga(ora(k), 100, qv=0) for k in range(3)])
    serie = dati.carica_serie_allineate(SIMBOLO, "1h", *GENNAIO, radice=tmp_path)
    assert serie["volume_usdt"] == {ora(0): 10.0, ora(1): 20.0, ora(2): 30.0}
    assert serie["n_tolte_last"] == 0 and serie["n_tolte_mark"] == 0


# ---------------------------------------------------------------------------
# (3) aggregazione da 15m a 1h
# ---------------------------------------------------------------------------


def test_aggregazione_15m_in_1h_somma_il_volume_e_scarta_i_gruppi_monchi(tmp_path):
    # Ore 0..3 = quarti 0..15.
    #   ora 0: completa nel last, nel mark manca il quarto 2   -> tolta dal last
    #   ora 1: completa in entrambe                              -> tenuta
    #   ora 2: nel last manca il quarto 9, completa nel mark     -> tolta dal mark
    #   ora 3: completa in entrambe, ma il quarto 13 non ha qv   -> tenuta, volume None
    qv = {k: float(k + 1) for k in range(16)}
    righe_last = [
        riga(quarto(k), 100 + k, qv=(None if k == 13 else qv[k]), durata=QUARTO) for k in range(16) if k != 9
    ]
    righe_mark = [riga(quarto(k), 500 + k, qv=0, durata=QUARTO) for k in range(16) if k != 2]
    scrivi_mese(tmp_path, "klines", "15m", 2023, 1, righe_last)
    scrivi_mese(tmp_path, "markPriceKlines", "15m", 2023, 1, righe_mark)

    serie = dati.carica_serie_allineate(SIMBOLO, "1h", *GENNAIO, radice=tmp_path, aggrega_da="15m")

    assert [c.ts for c in serie["candele"]] == [ora(1), ora(3)]
    assert [c.ts for c in serie["candele_mark"]] == [ora(1), ora(3)]
    # ora 1 dal last: quarti 4..7 (prezzo 100+k, high +1, low -1, close +0.5, volume 2 ciascuno)
    assert serie["candele"][0] == Candela(
        ts=ora(1), open=104, high=108, low=103, close=107.5, volume=8.0, close_ts=ora(2) - 1
    )
    assert serie["candele_mark"][0].open == 504 and serie["candele_mark"][0].close == 507.5
    assert serie["tolte_last"] == [ora(0)]
    assert serie["tolte_mark"] == [ora(2)]
    assert serie["n_tolte_last"] == 1 and serie["n_tolte_mark"] == 1
    # volume dell'ora 1 = qv dei quarti 4..7 = 5 + 6 + 7 + 8
    assert serie["volume_usdt"] == {ora(1): 26.0, ora(3): None}
    assert serie["n_volume_mancante"] == 1
    # un gruppo monco per serie: l'ora 2 nel last, l'ora 0 nel mark
    assert serie["n_gruppi_incompleti_last"] == 1
    assert serie["n_gruppi_incompleti_mark"] == 1


def test_aggregazione_gruppo_monco_in_entrambe_non_e_in_nessuna_lista(tmp_path):
    # ora 0 completa; ora 1 senza il quarto 5 in tutte e due le serie
    righe = [riga(quarto(k), 100, qv=1, durata=QUARTO) for k in range(8) if k != 5]
    scrivi_mese(tmp_path, "klines", "15m", 2023, 1, righe)
    scrivi_mese(tmp_path, "markPriceKlines", "15m", 2023, 1, righe)
    serie = dati.carica_serie_allineate(SIMBOLO, "1h", *GENNAIO, radice=tmp_path, aggrega_da="15m")
    assert [c.ts for c in serie["candele"]] == [ora(0)]
    assert serie["tolte_last"] == [] and serie["tolte_mark"] == []
    assert serie["n_gruppi_incompleti_last"] == 1 and serie["n_gruppi_incompleti_mark"] == 1
    assert serie["volume_usdt"] == {ora(0): 4.0}


# ---------------------------------------------------------------------------
# (4) blocco del vault prima del disco
# ---------------------------------------------------------------------------


def test_vault_chiuso_rifiuta_prima_di_toccare_il_disco(tmp_path, monkeypatch):
    # anche con i file in-sample gia' su disco, una fine nel 2024 non legge niente
    scrivi_mese(tmp_path, "klines", "1h", 2023, 12, [riga(TS_2023_01_01 + 364 * GIORNO, 100, qv=1)])

    def vietata(*args, **kwargs):
        raise AssertionError("accesso al disco prima del controllo del vault")

    monkeypatch.setattr(dati, "_percorsi_presenti", vietata)
    monkeypatch.setattr(dati, "carica_candele", vietata)
    monkeypatch.setattr(dati, "candele_da_zip", vietata)
    monkeypatch.setattr(dati, "volume_usdt_da_zip", vietata)
    with pytest.raises(VaultChiuso):
        dati.carica_serie_allineate(SIMBOLO, "1h", date(2023, 12, 1), date(2024, 1, 1), radice=tmp_path)
    with pytest.raises(VaultChiuso):
        dati.carica_serie_allineate(SIMBOLO, "1h", date(2023, 12, 1), date(2024, 1, 1), radice=tmp_path, aggrega_da="15m")


def test_vault_chiuso_senza_file_su_disco_non_crea_niente(tmp_path):
    with pytest.raises(VaultChiuso):
        dati.carica_serie_allineate(SIMBOLO, "1h", date(2024, 1, 1), date(2024, 1, 1), radice=tmp_path)
    assert not (tmp_path / "data").exists()


def test_oltre_il_vault_rifiutato_anche_a_vault_aperto(tmp_path):
    apri_vault(tmp_path)
    with pytest.raises(OltreIlVault):
        dati.carica_serie_allineate(SIMBOLO, "1h", date(2026, 9, 1), date(2026, 10, 1), radice=tmp_path)


# ---------------------------------------------------------------------------
# (5) serie vuote: tutto vuoto, conteggi presenti, nessuna eccezione
# ---------------------------------------------------------------------------


def test_mark_assente_tutto_vuoto_con_i_conteggi(tmp_path):
    scrivi_mese(tmp_path, "klines", "1h", 2023, 1, [riga(ora(k), 100, qv=1) for k in range(5)])
    serie = dati.carica_serie_allineate(SIMBOLO, "1h", *GENNAIO, radice=tmp_path)
    assert serie["candele"] == [] and serie["candele_mark"] == []
    assert serie["tolte_last"] == [ora(k) for k in range(5)] and serie["n_tolte_last"] == 5
    assert serie["tolte_mark"] == [] and serie["n_tolte_mark"] == 0
    assert serie["volume_usdt"] == {} and serie["n_volume_mancante"] == 0


def test_last_assente_tutto_vuoto_con_i_conteggi(tmp_path):
    scrivi_mese(tmp_path, "markPriceKlines", "1h", 2023, 1, [riga(ora(k), 100, qv=0) for k in range(3)])
    serie = dati.carica_serie_allineate(SIMBOLO, "1h", *GENNAIO, radice=tmp_path)
    assert serie["candele"] == [] and serie["candele_mark"] == []
    assert serie["tolte_mark"] == [ora(k) for k in range(3)] and serie["n_tolte_mark"] == 3
    assert serie["n_tolte_last"] == 0 and serie["volume_usdt"] == {}


def test_nessun_file_tutto_vuoto(tmp_path):
    for aggrega_da in (None, "15m"):
        serie = dati.carica_serie_allineate(SIMBOLO, "1h", *GENNAIO, radice=tmp_path, aggrega_da=aggrega_da)
        assert serie == {
            "candele": [],
            "candele_mark": [],
            "tolte_last": [],
            "tolte_mark": [],
            "n_tolte_last": 0,
            "n_tolte_mark": 0,
            "volume_usdt": {},
            "n_volume_mancante": 0,
            "n_gruppi_incompleti_last": 0,
            "n_gruppi_incompleti_mark": 0,
        }
