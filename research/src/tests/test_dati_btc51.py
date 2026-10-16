"""Test del caricatore per il protocollo 3 (``research/PROTOCOLLO_3.md``, regole 1 e 2, sezione 12,
Passo 0 punto 6):

* il vault si apre solo con ``vault/APERTURA_3.md`` (con un contenuto); ``APERTURA.md`` e
  ``APERTURA_2.md`` non aprono piu';
* in una sessione di campagna BTC51 il caricamento di dati dal 2022-10-01 e' rifiutato senza
  ``campagne/BTC51/via_libera_validazione.md`` (regola 2), PRIMA di leggere un file;
* fuori da quella campagna (coordinamento, test, campagne vecchie) il blocco non c'e';
* in campagna BTC51 si caricano solo i dati di BTCUSDT;
* ``serie_3`` produce una ``Serie`` del catalogo con last, mark e funding allineati.
"""
from __future__ import annotations

import io
import json
import zipfile
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from research.src import dati


@pytest.fixture
def progetto(tmp_path, monkeypatch):
    cartella = tmp_path / "progetto"
    (cartella / "research").mkdir(parents=True)
    monkeypatch.setattr(dati, "RADICE_PROGETTO", cartella)
    return cartella


def _sessione(progetto: Path, simbolo: str) -> None:
    (progetto / "research" / ".sessione").write_text(json.dumps({"tipo": "campagna", "simbolo": simbolo}))


def _zip(percorso: Path, righe: list) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(percorso.stem + ".csv", "\n".join(",".join(str(x) for x in r) for r in righe) + "\n")
    percorso.write_bytes(buf.getvalue())


def _mese_1h(radice: Path, simbolo: str, tipo: str, anno: int, mese: int, prezzo: float = 100.0) -> None:
    da = dati.ms_da_data(date(anno, mese, 1))
    a = dati.ms_da_data(date(anno + (mese == 12), mese % 12 + 1, 1))
    righe = []
    ts = da
    while ts < a:
        righe.append([ts, prezzo, prezzo + 1, prezzo - 1, prezzo, 10, ts + 3_599_999, 1000, 5, 0, 0, 0])
        ts += 3_600_000
    _zip(dati.percorso_mese(simbolo, tipo, "1h", anno, mese, radice), righe)


def _funding_mese(radice: Path, simbolo: str, anno: int, mese: int) -> None:
    da = dati.ms_da_data(date(anno, mese, 1))
    righe = [[da + k * 8 * 3_600_000, 8, 0.0001] for k in range(3)]
    _zip(dati.percorso_mese(simbolo, "fundingRate", None, anno, mese, radice), righe)


def test_vault_si_apre_solo_con_apertura_3(tmp_path):
    (tmp_path / "vault").mkdir()
    for vecchio in ("APERTURA.md", "APERTURA_2.md"):
        (tmp_path / "vault" / vecchio).write_text("aperto\n")
    with pytest.raises(dati.VaultChiuso):
        dati.controlla_vault(date(2024, 1, 1), tmp_path)
    (tmp_path / "vault" / "APERTURA_3.md").write_text("   \n")
    with pytest.raises(dati.VaultChiuso):
        dati.controlla_vault(date(2024, 1, 1), tmp_path)
    (tmp_path / "vault" / "APERTURA_3.md").write_text("APRI IL VAULT 3, 2026-xx-xx\n")
    dati.controlla_vault(date(2024, 1, 1), tmp_path)


def test_validazione_chiusa_in_campagna_btc51(progetto, tmp_path, monkeypatch):
    _sessione(progetto, "BTC51")
    radice = tmp_path / "research"
    letti = []
    vero = dati.candele_da_zip
    monkeypatch.setattr(dati, "candele_da_zip", lambda p: letti.append(p) or vero(p))
    _mese_1h(radice, "BTCUSDT", "klines", 2022, 9)
    _mese_1h(radice, "BTCUSDT", "klines", 2022, 10)
    # la costruzione si carica
    assert len(dati.carica_candele("BTCUSDT", "1h", date(2022, 9, 1), date(2022, 9, 30), radice)) == 720
    letti.clear()
    # un solo giorno della validazione basta per il rifiuto, prima di leggere un file
    for fine in (date(2022, 10, 1), date(2023, 12, 31)):
        with pytest.raises(dati.ValidazioneChiusa):
            dati.carica_candele("BTCUSDT", "1h", date(2022, 9, 1), fine, radice)
        with pytest.raises(dati.ValidazioneChiusa):
            dati.carica_funding("BTCUSDT", date(2022, 9, 1), fine, radice)
        with pytest.raises(dati.ValidazioneChiusa):
            dati.carica_serie_allineate("BTCUSDT", "1h", date(2022, 9, 1), fine, radice)
    assert letti == []
    # un via libera vuoto non vale; con un contenuto si'
    via = radice / "campagne" / "BTC51" / "via_libera_validazione.md"
    via.parent.mkdir(parents=True)
    via.write_text("\n")
    with pytest.raises(dati.ValidazioneChiusa):
        dati.carica_candele("BTCUSDT", "1h", date(2022, 10, 1), date(2022, 10, 31), radice)
    via.write_text("validazione autorizzata dall'utente il 2026-xx-xx\n")
    assert len(dati.carica_candele("BTCUSDT", "1h", date(2022, 10, 1), date(2022, 10, 31), radice)) == 744
    # il vault resta chiuso anche con il via libera
    with pytest.raises(dati.VaultChiuso):
        dati.carica_candele("BTCUSDT", "1h", date(2023, 12, 1), date(2024, 1, 1), radice)


def test_nessun_blocco_della_validazione_fuori_dalla_campagna_btc51(progetto, tmp_path):
    radice = tmp_path / "research"
    _mese_1h(radice, "BTCUSDT", "klines", 2022, 10)
    # senza marcatore (coordinamento, test)
    assert len(dati.carica_candele("BTCUSDT", "1h", date(2022, 10, 1), date(2022, 10, 31), radice)) == 744
    # una campagna del primo protocollo
    _sessione(progetto, "BTCUSDT")
    assert len(dati.carica_candele("BTCUSDT", "1h", date(2022, 10, 1), date(2022, 10, 31), radice)) == 744


def test_in_campagna_btc51_solo_btcusdt(progetto, tmp_path):
    _sessione(progetto, "BTC51")
    radice = tmp_path / "research"
    _mese_1h(radice, "ETHUSDT", "klines", 2022, 9)
    with pytest.raises(dati.VietatoInCampagna) as e:
        dati.carica_candele("ETHUSDT", "1h", date(2022, 9, 1), date(2022, 9, 30), radice)
    assert "PROTOCOLLO_3.md" in str(e.value)
    with pytest.raises(dati.VietatoInCampagna):
        dati.carica_candele("BTC51", "1h", date(2022, 9, 1), date(2022, 9, 30), radice)
    with pytest.raises(dati.VietatoInCampagna):
        dati.lista_contratti(fetch=lambda url: b"[]")


def test_scaricare_fino_al_2023_resta_permesso(progetto, tmp_path):
    """Il Passo 1 scarica tutti i file fino al 2023-12-31 e ne registra le impronte: il blocco
    della validazione riguarda il caricamento dei prezzi, non lo scarico."""
    _sessione(progetto, "BTC51")
    radice = tmp_path / "research"
    chiamati = []

    def finto(url):
        chiamati.append(url)
        return None  # mese assente

    dati.scarica_mese("BTCUSDT", "klines", "1h", 2023, 6, radice, finto)
    assert chiamati
    with pytest.raises(dati.VaultChiuso):
        dati.scarica_mese("BTCUSDT", "klines", "1h", 2024, 1, radice, finto)


def test_fatti_passo1_solo_conteggi(progetto, tmp_path):
    _sessione(progetto, "BTC51")
    radice = tmp_path / "research"
    for anno, mese in ((2022, 9), (2022, 10), (2023, 1)):
        _mese_1h(radice, "BTCUSDT", "klines", anno, mese)
        _mese_1h(radice, "BTCUSDT", "markPriceKlines", anno, mese)
        _funding_mese(radice, "BTCUSDT", anno, mese)
    fatti = dati.fatti_passo1_3("BTCUSDT", radice, timeframe=("1h",))
    voce = fatti["timeframe"]["1h"]["klines"]
    assert voce["costruzione"] == 720 and voce["validazione"] == 744 + 744
    assert voce["buchi"] and voce["buchi"][0]["candele_mancanti"] == 61 * 24  # novembre e dicembre 2022
    assert fatti["prima_candela"].startswith("2022-09-01T00:00")
    assert fatti["regolamenti_funding"] == 9
    testo = json.dumps(fatti)
    assert "100.0" not in testo and "101.0" not in testo  # nessun prezzo


def test_serie_3(tmp_path):
    radice = tmp_path / "research"
    _mese_1h(radice, "BTCUSDT", "klines", 2021, 1, prezzo=100.0)
    _mese_1h(radice, "BTCUSDT", "markPriceKlines", 2021, 1, prezzo=100.5)
    _funding_mese(radice, "BTCUSDT", 2021, 1)
    s = dati.serie_3("BTCUSDT", "1h", date(2021, 1, 1), date(2021, 1, 31), radice)
    assert len(s) == 744 and s.timeframe == "1h"
    assert np.all(s.close == 100.0) and np.all(s.mark_close == 100.5)
    assert list(s.funding_ts) == [dati.ms_da_data(date(2021, 1, 1)) + k * 8 * 3_600_000 for k in range(3)]
    assert len(s.inizi_dei_tratti()) == 1
