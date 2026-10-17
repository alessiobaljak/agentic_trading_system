"""Test del caricatore per il protocollo 4 (`research/PROTOCOLLO_4.md`, regole 1, 2 e 10, sezioni
7.2, 9.6 e 12, Passo 0 punto 6):

* il vault si apre solo con `vault/APERTURA_4.md`; `APERTURA_3.md` (e i precedenti) non aprono;
* in campagna LINK6 si caricano solo i dati di LINKUSDT: le monete di controllo, BTCUSDT
  compresa, sono rifiutate;
* il blocco della validazione si toglie con `campagne/LINK6/via_libera_validazione.md`, non
  con quello di BTC51;
* `serie_4` toglie le candele in coda senza scambi (e il funding dopo), tiene quelle a volume
  zero in mezzo, e riporta il funding a 8 ore per i segnali;
* il segnale E11 usa il funding riportato a 8 ore, il risultato dei trade il tasso vero.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import pytest

from research.src import catalogo3 as cat
from research.src import dati
from research.src.tests.test_dati_btc51 import _funding_mese, _mese_1h, _sessione, _zip, progetto  # noqa: F401


def test_vault_si_apre_solo_con_apertura_4(tmp_path):
    (tmp_path / "vault").mkdir()
    for vecchio in ("APERTURA.md", "APERTURA_2.md", "APERTURA_3.md"):
        (tmp_path / "vault" / vecchio).write_text("aperto\n")
    assert dati.vault_aperto(tmp_path) is False
    with pytest.raises(dati.VaultChiuso):
        dati.controlla_vault(date(2024, 1, 1), tmp_path)
    (tmp_path / "vault" / "APERTURA_4.md").write_text("  \n")
    with pytest.raises(dati.VaultChiuso):
        dati.controlla_vault(date(2024, 1, 1), tmp_path)
    (tmp_path / "vault" / "APERTURA_4.md").write_text("APRI IL VAULT 4, 2026-xx-xx\n")
    dati.controlla_vault(date(2024, 1, 1), tmp_path)


def test_in_campagna_link6_solo_linkusdt(progetto, tmp_path):
    _sessione(progetto, "LINK6")
    radice = tmp_path / "research"
    _mese_1h(radice, "LINKUSDT", "klines", 2021, 3)
    assert len(dati.carica_candele("LINKUSDT", "1h", date(2021, 3, 1), date(2021, 3, 31), radice)) == 744
    for altra in ("BTCUSDT", "ETHUSDT", "SOLUSDT", "MATICUSDT", "LINK6"):
        _mese_1h(radice, altra, "klines", 2021, 3)
        with pytest.raises(dati.VietatoInCampagna, match="LINKUSDT"):
            dati.carica_candele(altra, "1h", date(2021, 3, 1), date(2021, 3, 31), radice)
        with pytest.raises(dati.VietatoInCampagna):
            dati.scarica_mese(altra, "klines", "1h", 2021, 3, radice, lambda url: None)


def test_validazione_chiusa_in_campagna_link6(progetto, tmp_path):
    _sessione(progetto, "LINK6")
    radice = tmp_path / "research"
    _mese_1h(radice, "LINKUSDT", "klines", 2022, 10)
    with pytest.raises(dati.ValidazioneChiusa, match="PROTOCOLLO_4.md"):
        dati.carica_candele("LINKUSDT", "1h", date(2022, 10, 1), date(2022, 10, 31), radice)
    # il via libera di un'altra campagna non vale
    altro = radice / "campagne" / "BTC51" / "via_libera_validazione.md"
    altro.parent.mkdir(parents=True)
    altro.write_text("si'\n")
    with pytest.raises(dati.ValidazioneChiusa):
        dati.carica_candele("LINKUSDT", "1h", date(2022, 10, 1), date(2022, 10, 31), radice)
    proprio = radice / "campagne" / "LINK6" / "via_libera_validazione.md"
    proprio.parent.mkdir(parents=True)
    proprio.write_text("validazione autorizzata\n")
    assert len(dati.carica_candele("LINKUSDT", "1h", date(2022, 10, 1), date(2022, 10, 31), radice)) == 744
    with pytest.raises(dati.VaultChiuso):
        dati.carica_candele("LINKUSDT", "1h", date(2023, 12, 1), date(2024, 1, 1), radice)


def _mese_con_coda_ferma(radice: Path, simbolo: str, anno: int, mese: int, ore_ferme: int) -> None:
    """Un mese di candele 1h; le ultime `ore_ferme` a prezzo fermo e volume zero, e una candela a
    volume zero a meta' mese."""
    da = dati.ms_da_data(date(anno, mese, 1))
    a = dati.ms_da_data(date(anno + (mese == 12), mese % 12 + 1, 1))
    n = (a - da) // 3_600_000
    righe = []
    for k in range(n):
        ts = da + k * 3_600_000
        fermo = k >= n - ore_ferme
        vol = 0 if (fermo or k == n // 2) else 10
        p = 50.0 if fermo else 100.0 + k * 0.01
        righe.append([ts, p, p + (0 if fermo else 1), p - (0 if fermo else 1), p, vol, ts + 3_599_999, vol * p,
                      5, 0, 0, 0])
    for tipo in ("klines", "markPriceKlines"):
        _zip(dati.percorso_mese(simbolo, tipo, "1h", anno, mese, radice), righe)


def test_serie_4_finisce_all_ultima_candela_con_scambi(tmp_path):
    radice = tmp_path / "research"
    _mese_con_coda_ferma(radice, "MATICUSDT", 2023, 4, ore_ferme=100)
    da = dati.ms_da_data(date(2023, 4, 1))
    # regolamenti ogni 8 ore per tutto il mese, anche dopo l'ultimo scambio
    righe = [[da + k * 8 * 3_600_000, 8, 0.0001] for k in range(90)]
    _zip(dati.percorso_mese("MATICUSDT", "fundingRate", None, 2023, 4, radice), righe)
    s, conteggi = dati.serie_4_con_conteggi("MATICUSDT", "1h", date(2023, 4, 1), date(2023, 4, 30), radice)
    assert conteggi["candele_ferme_in_coda_tolte"] == 100
    assert len(s.ts) == 720 - 100 == conteggi["candele"]
    assert s.volume[-1] > 0
    assert np.sum(s.volume == 0) == 1  # la candela a volume zero a meta' mese resta
    fine = s.ts[-1] + 3_600_000 - 1
    assert np.all(s.funding_ts <= fine)  # niente funding dopo l'ultima candela tenuta
    assert conteggi["intervalli_funding_ore"] == {8: len(s.funding_ts)}


def test_serie_4_riporta_il_funding_a_8_ore(tmp_path):
    radice = tmp_path / "research"
    _mese_1h(radice, "LINKUSDT", "klines", 2021, 5)
    _mese_1h(radice, "LINKUSDT", "markPriceKlines", 2021, 5)
    da = dati.ms_da_data(date(2021, 5, 1))
    righe = [[da, 8, 0.0002], [da + 8 * 3_600_000, 4, 0.0002], [da + 12 * 3_600_000, 4, -0.00005]]
    _zip(dati.percorso_mese("LINKUSDT", "fundingRate", None, 2021, 5, radice), righe)
    s, conteggi = dati.serie_4_con_conteggi("LINKUSDT", "1h", date(2021, 5, 1), date(2021, 5, 31), radice)
    assert list(s.funding_tasso) == [0.0002, 0.0002, -0.00005]
    assert np.allclose(s.funding_segnale, [0.0002, 0.0004, -0.0001])
    assert conteggi["intervalli_funding_ore"] == {4: 2, 8: 1}
    # la serie troncata si porta dietro il funding per i segnali
    t = s.fino_a(9)
    assert len(t.funding_segnale) == len(t.funding_ts) == 2


def test_e11_usa_il_funding_riportato_a_8_ore():
    n = 48
    ts = np.arange(n, dtype=np.int64) * 3_600_000 + dati.ms_da_data(date(2021, 1, 1))
    p = np.full(n, 100.0)
    f_ts = ts[::4]  # un regolamento ogni 4 ore
    vero = np.full(len(f_ts), -0.00006)  # sopra -0,01% cosi' com'e', sotto -0,01% riportato a 8 ore (-0,012%)
    base = dict(timeframe="1h", ts=ts, open=p, high=p + 1, low=p - 1, close=p, volume=np.full(n, 10.0),
                mark_open=p, mark_high=p + 1, mark_low=p - 1, mark_close=p, funding_ts=f_ts, funding_tasso=vero)
    variante = {"timeframe": "1h", "direzione": "long", "filtro": None,
                "ingresso": {"codice": "E11", "soglia": -0.0001, "lato": "sotto"}, "conferma": None,
                "tipo_ingresso": {"codice": "M"}, "stop": {"codice": "S3", "pct": 0.02},
                "uscite": [{"codice": "U2", "n": 6}]}
    senza = cat.compila(variante, cat.Serie(**base), solo_catalogo=False)
    con = cat.compila(variante, cat.Serie(**base, funding_segnale=vero * 2), solo_catalogo=False)
    assert not np.any(senza.segnale)
    assert np.any(con.segnale)
