"""Test di controllo del Passo 0 del protocollo 3 che usano le candele vere di BTCUSDT
(``research/PROTOCOLLO_3.md``, Passo 0, punto 6):

* buy and hold su tutto il 2021 restituisce il rendimento atteso;
* il test di troncamento (9.8) passa su una variante di prova (incrocio EMA 20/50 su 4h), solo per
  il test, senza calcolarne ne' registrarne il risultato.

Servono i file mensili di BTCUSDT in ``research/data/insample/BTCUSDT/`` (non sono in git: li
scarica il caricatore). Se mancano, i test si saltano e lo dicono.
"""
from __future__ import annotations

import zipfile
from datetime import date

import pytest

from research.src import dati
from research.src.motore3 import test_troncamento
from research.src.statistica3 import buy_and_hold

RADICE = dati.RADICE_DEFAULT


def _presenti(tipo: str, tf: str, mesi) -> bool:
    return all(dati.percorso_mese("BTCUSDT", tipo, tf, a, m, RADICE).is_file() for a, m in mesi)


MESI_2021 = [(2021, m) for m in range(1, 13)]
MESI_COSTRUZIONE = list(dati.mesi_del_periodo(date(2020, 1, 1), date(2022, 9, 30)))


@pytest.mark.skipif(not (_presenti("klines", "1d", MESI_2021) and _presenti("markPriceKlines", "1d", MESI_2021)),
                    reason="mancano i file 1d del 2021 di BTCUSDT")
def test_buy_and_hold_2021():
    s = dati.serie_3("BTCUSDT", "1d", date(2021, 1, 1), date(2021, 12, 31))
    # 360 giorni su 365: nei file del mark di BTCUSDT mancano 2021-07-01 e dal 24 al 27 luglio 2021,
    # e il caricatore tiene solo i giorni presenti in tutte e due le serie (fatto da riportare al Passo 1)
    assert s.ts[0] == dati.ms_da_data(date(2021, 1, 1)) and s.ts[-1] == dati.ms_da_data(date(2021, 12, 31))
    # il calcolo indipendente: apertura del 1 gennaio e chiusura del 31 dicembre lette dai file
    def riga(anno, mese, giorno):
        p = dati.percorso_mese("BTCUSDT", "klines", "1d", anno, mese, RADICE)
        with zipfile.ZipFile(p) as z:
            testo = z.read(z.namelist()[0]).decode()
        for linea in testo.splitlines():
            campi = linea.split(",")
            if campi[0].isdigit() and int(campi[0]) == dati.ms_da_data(date(anno, mese, giorno)):
                return campi
        raise AssertionError("candela non trovata")
    apertura = float(riga(2021, 1, 1)[1])
    chiusura = float(riga(2021, 12, 31)[4])
    atteso = chiusura / apertura - 1
    assert buy_and_hold(s, 0, len(s) - 1) == pytest.approx(atteso, rel=1e-12)
    # e il valore noto: BTC e' salito di circa il 60% nel 2021 (da circa 29.000 a circa 46.000 USDT)
    assert 0.55 < atteso < 0.65


@pytest.mark.skipif(not (_presenti("klines", "4h", MESI_COSTRUZIONE) and _presenti("markPriceKlines", "4h", MESI_COSTRUZIONE)),
                    reason="mancano i file 4h della costruzione di BTCUSDT")
def test_troncamento_su_variante_di_prova():
    s = dati.serie_3("BTCUSDT", "4h", date(2020, 1, 1), date(2022, 9, 30))
    variante = {"timeframe": "4h", "direzione": "long", "filtro": None,
                "ingresso": {"codice": "E1", "media": "EMA", "veloce": 20, "lenta": 50}, "conferma": None,
                "tipo_ingresso": {"codice": "M"}, "stop": {"codice": "S1", "k": 2.0},
                "uscite": [{"codice": "U1", "k": 2}]}
    assert test_troncamento(variante, s, 0, len(s) - 1) == []
