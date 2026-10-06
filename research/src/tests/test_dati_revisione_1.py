"""Revisione avversaria 1 del caricatore dati (research/src/dati.py).

Due gruppi di test, tutti senza rete (fetch finto):

* i test "guardia_*" documentano i tentativi di aggirare il blocco del vault
  che NON funzionano (devono passare: se un giorno falliscono, il blocco si e'
  rotto);
* i test "difetto_*" smascherano comportamenti sbagliati trovati nella
  revisione. Oggi FALLISCONO di proposito: restano qui per chi corregge, e
  diventano verdi quando il difetto e' sistemato. Ogni docstring dice cosa si
  e' visto e perche' e' un problema.

Lancio: python -m pytest research/src/tests/test_dati_revisione_1.py -q -p no:cacheprovider
"""

from __future__ import annotations

import io
import os
import zipfile
from datetime import date, datetime
from pathlib import Path
from typing import List, Sequence

import pytest

from research.src import dati
from research.src.motore import Candela

# ---------------------------------------------------------------------------
# Attrezzi
# ---------------------------------------------------------------------------


def _zip_con_csv(testo: str, nome: str = "dati.csv") -> bytes:
    """Uno zip in memoria con un solo CSV dentro, come quelli di Binance."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archivio:
        archivio.writestr(nome, testo)
    return buf.getvalue()


def _riga_kline(ts: int, close_ts: int, o=1.0, h=2.0, l=0.5, c=1.5, v=10.0) -> str:
    return f"{ts},{o},{h},{l},{c},{v},{close_ts},0,0,0,0,0"


class FetchFinto:
    """fetch iniettabile che conta le chiamate e risponde con uno zip fisso (o 404)."""

    def __init__(self, contenuto: bytes | None = None) -> None:
        self.contenuto = contenuto
        self.chiamate: List[str] = []

    def __call__(self, url: str) -> bytes | None:
        self.chiamate.append(url)
        return self.contenuto


def _apri_vault(radice: Path, testo: str = "aperto il 2026-10-06 12:00 UTC\ncandidati: ...\n") -> None:
    (radice / "vault").mkdir(parents=True, exist_ok=True)
    (radice / "vault" / "APERTURA.md").write_text(testo)


def _candela(ts: int, durata_ms: int, volume: float = 1.0) -> Candela:
    return Candela(ts=ts, open=1.0, high=2.0, low=0.5, close=1.5, volume=volume, close_ts=ts + durata_ms - 1)


MS_15M = 15 * 60_000
MS_1H = 3_600_000


# ---------------------------------------------------------------------------
# Guardie: tentativi di aggiramento che NON riescono (devono restare verdi)
# ---------------------------------------------------------------------------


def test_guardia_periodo_a_cavallo_del_confine_zero_fetch(tmp_path):
    """Un periodo che inizia nel 2023 e finisce il 2024-01-01 non scarica nemmeno la parte lecita."""
    fetch = FetchFinto(_zip_con_csv(""))
    with pytest.raises(dati.VaultChiuso):
        dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2023, 11, 1), date(2024, 1, 1), tmp_path, fetch)
    assert fetch.chiamate == []
    assert not (tmp_path / "data").exists(), "nessun accesso al disco prima del rifiuto"


def test_guardia_scarica_mese_diretto_gennaio_2024_rifiutato(tmp_path):
    """Chiamare scarica_mese direttamente con anno 2024 non aggira il blocco, per tutti i tipi."""
    fetch = FetchFinto(_zip_con_csv(""))
    for tipo, intervallo in (("klines", "1h"), ("markPriceKlines", "1h"), ("fundingRate", None)):
        with pytest.raises(dati.VaultChiuso):
            dati.scarica_mese("BTCUSDT", tipo, intervallo, 2024, 1, tmp_path, fetch)
    assert fetch.chiamate == []


def test_guardia_dicembre_2023_e_lecito_gennaio_2024_no(tmp_path):
    """Il confine e' esatto: 2023-12-31 passa, 2024-01-01 no."""
    fetch = FetchFinto(_zip_con_csv(""))
    dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2023, 12, 1), date(2023, 12, 31), tmp_path, fetch)
    assert len(fetch.chiamate) == 1
    with pytest.raises(dati.VaultChiuso):
        dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2024, 1, 1), date(2024, 1, 1), tmp_path, fetch)
    assert len(fetch.chiamate) == 1


def test_guardia_datetime_al_confine_non_aggira(tmp_path):
    """Passare un datetime (2023-12-31 23:59 o 2024-01-01 00:00) non apre una scappatoia: solleva."""
    for fine in (datetime(2023, 12, 31, 23, 59), datetime(2024, 1, 1, 0, 0)):
        with pytest.raises((dati.VaultChiuso, TypeError)):
            dati.controlla_vault(fine, tmp_path)


def test_guardia_carica_candele_e_funding_con_fine_nel_2024_su_file_gia_su_disco(tmp_path):
    """Anche se il file del 2024 e' gia' su disco (messo a mano), caricarlo a vault chiuso e' rifiutato."""
    p = dati.percorso_mese("BTCUSDT", "klines", "1h", 2024, 1, tmp_path)
    p.parent.mkdir(parents=True)
    ts = dati.ms_da_data(date(2024, 1, 1))
    p.write_bytes(_zip_con_csv(_riga_kline(ts, ts + MS_1H - 1) + "\n"))
    with pytest.raises(dati.VaultChiuso):
        dati.carica_candele("BTCUSDT", "1h", date(2023, 12, 1), date(2024, 1, 1), tmp_path)
    with pytest.raises(dati.VaultChiuso):
        dati.carica_candele("BTCUSDT", "1h", date(2024, 1, 1), date(2024, 1, 1), tmp_path)
    with pytest.raises(dati.VaultChiuso):
        dati.carica_funding("BTCUSDT", date(2023, 12, 1), date(2024, 1, 1), tmp_path)
    with pytest.raises(dati.VaultChiuso):
        dati.carica_funding_dettaglio("BTCUSDT", date(2023, 12, 1), date(2024, 1, 1), tmp_path)


def test_guardia_cartella_al_posto_del_file_non_apre(tmp_path):
    """Una cartella chiamata APERTURA.md non e' il file di apertura."""
    (tmp_path / "vault" / "APERTURA.md").mkdir(parents=True)
    assert dati.vault_aperto(tmp_path) is False
    with pytest.raises(dati.VaultChiuso):
        dati.scarica_mese("BTCUSDT", "klines", "1h", 2024, 1, tmp_path, FetchFinto(b""))


def test_guardia_radice_diversa_e_percorso_relativo(tmp_path, monkeypatch):
    """APERTURA.md in un'altra radice non apre questa; la radice relativa si risolve rispetto alla cwd."""
    altra = tmp_path / "altra"
    _apri_vault(altra)
    questa = tmp_path / "questa"
    questa.mkdir()
    with pytest.raises(dati.VaultChiuso):
        dati.scarica_mese("BTCUSDT", "klines", "1h", 2024, 1, questa, FetchFinto(b""))
    monkeypatch.chdir(tmp_path)
    assert dati.vault_aperto(Path("questa")) is False
    assert dati.vault_aperto(Path("altra")) is True
    assert dati.vault_aperto("altra") is True


def test_guardia_nessun_elenco_remoto(tmp_path):
    """Gli URL richiesti sono solo file mensili diretti: mai l'indice del bucket o un '?prefix='."""
    fetch = FetchFinto(None)
    dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2023, 1, 1), date(2023, 3, 31), tmp_path, fetch)
    dati.scarica_periodo("BTCUSDT", "fundingRate", None, date(2023, 1, 1), date(2023, 1, 31), tmp_path, fetch)
    assert len(fetch.chiamate) == 4
    for url in fetch.chiamate:
        assert url.endswith(".zip")
        assert "?" not in url and "prefix" not in url and "list" not in url.lower()


def test_guardia_zip_con_piu_csv_rifiutato(tmp_path):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as archivio:
        archivio.writestr("a.csv", _riga_kline(1, 2) + "\n")
        archivio.writestr("b.csv", _riga_kline(1, 2) + "\n")
    p = tmp_path / "due.zip"
    p.write_bytes(buf.getvalue())
    with pytest.raises(ValueError):
        dati.candele_da_zip(p)


# ---------------------------------------------------------------------------
# Difetti trovati (oggi falliscono: restano per chi corregge)
# ---------------------------------------------------------------------------


def test_difetto_candela_aperta_nel_2023_ma_chiusa_nel_2024_entra_a_vault_chiuso(tmp_path):
    """DIFETTO (gravita' media): carica_candele filtra solo sul ts di apertura.

    Il 2023-12-31 dista 19722 giorni dall'epoca, multiplo di 3: la candela '3d'
    di Binance che apre il 2023-12-31 chiude il 2024-01-02 23:59:59 e sta nel
    file mensile 2023-12 (in-sample). A vault chiuso, con fine=2023-12-31, il
    caricatore la consegna intera: high, low e close contengono i prezzi del
    1 e 2 gennaio 2024. Per la regola 1 del protocollo ("non carichi, non
    leggi" dati oltre il 2023-12-31) una candela che chiude oltre ``fine`` va
    scartata (o troncata), non consegnata.
    """
    assert (date(2023, 12, 31) - date(1970, 1, 1)).days % 3 == 0, "premessa: 2023-12-31 e' un confine 3d"
    ts = dati.ms_da_data(date(2023, 12, 31))
    close_ts = dati.ms_da_data(date(2024, 1, 3)) - 1
    p = dati.percorso_mese("BTCUSDT", "klines", "3d", 2023, 12, tmp_path)
    p.parent.mkdir(parents=True)
    p.write_bytes(_zip_con_csv(_riga_kline(ts, close_ts) + "\n"))

    candele = dati.carica_candele("BTCUSDT", "3d", date(2023, 12, 1), date(2023, 12, 31), tmp_path)
    limite = dati.ms_da_data(date(2024, 1, 1))
    assert all(c.close_ts < limite for c in candele), (
        f"consegnata una candela che chiude nel 2024 a vault chiuso: {candele}"
    )


def test_difetto_aggrega_candele_non_deduplica(tmp_path):
    """DIFETTO (gravita' bassa): un gruppo con un duplicato passa per completo.

    Tre candele 15m distinte piu' una copia della prima fanno 4 elementi: il
    controllo ``len(gruppo) == attese`` lo accetta e il volume risulta
    raddoppiato per quella candela, mentre manca davvero un quarto d'ora. Il
    docstring promette di scartare i gruppi incompleti: questo e' incompleto.
    """
    base = dati.ms_da_data(date(2023, 6, 1))
    gruppo = [
        _candela(base, MS_15M),
        _candela(base + MS_15M, MS_15M),
        _candela(base + 2 * MS_15M, MS_15M),
        _candela(base, MS_15M),  # duplicato della prima: il quarto d'oro manca davvero
    ]
    risultato = dati.aggrega_candele(gruppo, "1h")
    assert risultato == [], f"gruppo incompleto accettato come ora piena: {risultato}"


def test_difetto_bom_senza_intestazione_perde_la_prima_riga(tmp_path):
    """DIFETTO (gravita' bassa): la prima riga di dati sparisce in silenzio se il primo campo non e' numerico.

    L'intestazione si riconosce con "primo campo non numerico". Un BOM UTF-8
    in testa a un file SENZA intestazione rende non numerico il primo
    timestamp e la prima candela del mese viene scartata senza alcun errore.
    Binance oggi non mette il BOM, ma scartare in silenzio una riga di dati
    non e' mai accettabile: o si legge con 'utf-8-sig', o si riconosce
    l'intestazione dal nome del campo ('open_time', 'calc_time') e si solleva
    su tutto il resto.
    """
    ts = dati.ms_da_data(date(2023, 1, 1))
    testo = "﻿" + _riga_kline(ts, ts + MS_1H - 1) + "\n" + _riga_kline(ts + MS_1H, ts + 2 * MS_1H - 1) + "\n"
    p = tmp_path / "bom.zip"
    p.write_bytes(_zip_con_csv(testo))
    candele = dati.candele_da_zip(p)
    assert len(candele) == 2, f"persa la prima riga di dati: {candele}"


def test_difetto_apertura_md_vuoto_apre_il_vault(tmp_path):
    """DIFETTO (gravita' bassa): un APERTURA.md da 0 byte apre il vault.

    Il Passo 5 del protocollo dice che il file si crea "con data e ora e
    l'elenco dei candidati congelati, con l'hash SHA-256": un file vuoto
    (un ``touch`` per sbaglio, un editor che salva prima di scrivere) non e'
    un'apertura. Il caricatore guarda solo l'esistenza del file.
    """
    (tmp_path / "vault").mkdir()
    (tmp_path / "vault" / "APERTURA.md").touch()
    assert dati.vault_aperto(tmp_path) is False, "un file vuoto non e' un'apertura del vault"
    fetch = FetchFinto(_zip_con_csv(""))
    with pytest.raises(dati.VaultChiuso):
        dati.scarica_mese("BTCUSDT", "klines", "1h", 2024, 1, tmp_path, fetch)
    assert fetch.chiamate == []


def test_difetto_oltre_la_fine_del_vault_si_scarica_a_vault_aperto(tmp_path):
    """DIFETTO (gravita' bassa): FINE_VAULT (2026-09-30) e' dichiarata ma mai usata.

    A vault aperto, chiedere ottobre 2026 (il periodo in cui il bot sta
    facendo paper trading adesso) parte davvero verso la rete e salverebbe il
    file in data/vault/. Il protocollo definisce il vault "dal 2024-01-01 al
    2026-09-30": oltre quella data il caricatore dovrebbe rifiutare come fa
    per il confine del 2023, invece di lasciare entrare il periodo del paper.
    """
    _apri_vault(tmp_path)
    fetch = FetchFinto(None)
    with pytest.raises(Exception):
        dati.scarica_periodo("BTCUSDT", "klines", "1h", date(2026, 10, 1), date(2026, 10, 5), tmp_path, fetch)
    assert fetch.chiamate == [], f"richiesta partita oltre FINE_VAULT: {fetch.chiamate}"
