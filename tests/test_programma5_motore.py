"""Il motore comune del programma 5 (research/programma5/strumenti/motore5.py): simulatore, costi, funding, caso,
bootstrap e guardiano dei periodi."""
import numpy as np
import pandas as pd
import pytest

from research.programma5.strumenti import motore5 as m5


def _df(prezzi, alti=None, bassi=None, inizio=27_000_000):
    prezzi = np.asarray(prezzi, float)
    alti = prezzi if alti is None else np.asarray(alti, float)
    bassi = prezzi if bassi is None else np.asarray(bassi, float)
    idx = np.arange(inizio, inizio + len(prezzi))
    return pd.DataFrame({"open": prezzi, "high": alti, "low": bassi, "close": prezzi,
                         "volume": 1.0, "quote_volume": 1.0, "taker_buy_volume": 0.5, "periodo": True}, index=idx)


def test_uscita_a_tempo_con_i_costi_di_btc():
    df = _df([100, 100, 101, 102, 103, 104, 105])
    t = m5.simula(df, "BTCUSDT", np.array([0]), np.array([1]), m5.Uscita(minuti=3))
    # ingresso all'apertura del minuto 1 (100), uscita alla chiusura del minuto 3 (102)
    assert t.iloc[0]["lordo"] == pytest.approx(0.02)
    assert t.iloc[0]["costo"] == pytest.approx(2 * (0.0005 + 0.0001))
    assert t.iloc[0]["netto"] == pytest.approx(0.02 - 0.0012)
    assert t.iloc[0]["netto_doppio"] == pytest.approx(0.02 - 0.0024)


def test_stop_prima_del_target_nella_stessa_candela_e_scarto_doppio_nelle_esplosioni():
    df = _df([100, 100, 100, 100], alti=[100, 100, 103, 100], bassi=[100, 100, 97, 100])
    t = m5.simula(df, "DOGEUSDT", np.array([0]), np.array([1]), m5.Uscita(minuti=3, stop=0.02, target=0.02),
                  esplosione=np.array([True]))
    assert t.iloc[0]["motivo"] == "stop"
    assert t.iloc[0]["lordo"] == pytest.approx(-0.02)
    assert t.iloc[0]["costo"] == pytest.approx(2 * (0.0005 + 2 * 0.0002))


def test_short_e_funding_pagato_dal_long_e_incassato_dallo_short():
    df = _df([100] * 10)
    fund = pd.DataFrame({"ore": [8], "tasso": [0.001]}, index=[df.index[4]])
    lungo = m5.simula(df, "BTCUSDT", np.array([0]), np.array([1]), m5.Uscita(minuti=6), fund)
    corto = m5.simula(df, "BTCUSDT", np.array([0]), np.array([-1]), m5.Uscita(minuti=6), fund)
    assert lungo.iloc[0]["funding"] == pytest.approx(0.001)
    assert corto.iloc[0]["funding"] == pytest.approx(-0.001)
    # un regolamento fuori dal trade non conta
    fuori = pd.DataFrame({"ore": [8], "tasso": [0.001]}, index=[df.index[9]])
    assert m5.simula(df, "BTCUSDT", np.array([0]), np.array([1]), m5.Uscita(minuti=3), fuori).iloc[0]["funding"] == 0


def test_il_caso_tiene_mese_e_direzione():
    df = _df(np.linspace(100, 110, 5000))
    t = m5.simula(df, "BTCUSDT", np.array([10, 2000]), np.array([1, -1]), m5.Uscita(minuti=5))
    c = m5.caso(df, "BTCUSDT", t, m5.Uscita(minuti=5), ripetizioni=3)
    assert len(c) == 6 and set(c["direzione"]) == {1, -1}


def test_bootstrap_dice_p_piccolo_per_un_guadagno_netto_e_grande_per_zero():
    rng = np.random.default_rng(1)
    minuti = np.arange(0, 1440 * 300, 1440)
    buono = m5.bootstrap_giorni(rng.normal(0.01, 0.01, 300), minuti)
    nullo = m5.bootstrap_giorni(rng.normal(0.0, 0.01, 300), minuti)
    assert buono["p"] < 0.001 and buono["basso"] > 0
    assert nullo["p"] > 0.01


def test_il_guardiano_non_apre_la_validazione_senza_regola_congelata():
    with pytest.raises(m5.PeriodoChiuso):
        m5.controlla_periodo("V", "I-999")
    with pytest.raises(m5.PeriodoChiuso):
        m5.controlla_periodo("R", None)
    m5.controlla_periodo("C", None)


def test_i_file_giornalieri_e_mensili_si_riconoscono_per_data():
    from datetime import date
    assert m5._dentro("BTCUSDT-metrics-2020-09-01.zip", date(2020, 9, 1), date(2020, 9, 30))
    assert not m5._dentro("BTCUSDT-metrics-2023-01-01.zip", date(2020, 1, 1), date(2022, 12, 31))
    assert m5._dentro("BTCUSDT-1m-2022-12.zip", date(2020, 1, 1), date(2022, 12, 31))
    assert not m5._dentro("BTCUSDT-1m-2023-01.zip", date(2020, 1, 1), date(2022, 12, 31))
    assert m5._dentro("BTCUSDT-1m-2026-10-05.zip", date(2026, 10, 1), date(2099, 12, 31))
