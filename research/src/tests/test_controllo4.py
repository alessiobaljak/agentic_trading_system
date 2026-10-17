"""Test dello strumento del coordinamento per le monete di controllo (`research/src/controllo4.py`;
`research/PROTOCOLLO_4.md`, sezione 4bis, regola 10, Fase 3 punto 4, verifica 12, 10.3)."""
from __future__ import annotations

import pytest

from research.src import controllo4 as ctl
from research.src.tests.test_statistica3 import V_VANTAGGIO, _ms, serie_casuale, serie_con_vantaggio

FINE = _ms("2022-10-01") - 1
VELOCE = {"n_simulazioni": 50}


def test_monete_e_costi():
    assert list(ctl.MONETE_CONTROLLO) == ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "BNBUSDT",
                                          "LTCUSDT", "MATICUSDT", "BCHUSDT"]
    assert ctl.costi_moneta("BTCUSDT").slippage == 0.0001
    assert ctl.costi_moneta("XRPUSDT").slippage == 0.0002
    doppi = ctl.costi_moneta("XRPUSDT", doppi=True)
    assert (doppi.taker, doppi.maker, doppi.slippage) == (0.0010, 0.0004, 0.0004)


def test_verifica_12_con_un_vantaggio_vero_su_tutte_le_monete():
    s = serie_con_vantaggio("4h")
    serie = {k: s for k in ctl.MONETE_CONTROLLO}
    esito = ctl.verifica_12_su_serie(V_VANTAGGIO, serie, FINE, **VELOCE)
    assert esito["battono"] == 9
    assert esito["media_r"] > 0
    assert esito["supera"] is True


def test_verifica_12_fallisce_se_battono_meno_di_7_monete():
    vero = serie_con_vantaggio("4h")
    senza = serie_casuale(6000, tf="4h", seme=3, inizio="2019-09-08", sigma=0.004)
    serie = {k: (vero if i < 6 else senza) for i, k in enumerate(ctl.MONETE_CONTROLLO)}
    esito = ctl.verifica_12_su_serie(V_VANTAGGIO, serie, FINE, **VELOCE)
    assert esito["battono"] <= 8
    if esito["battono"] < 7:
        assert esito["supera"] is False


def test_una_moneta_con_meno_di_30_trade_non_batte():
    s = serie_con_vantaggio("4h")
    corta = s.fino_a(400)  # poche settimane: pochi trade
    serie = {k: s for k in ctl.MONETE_CONTROLLO}
    serie["MATICUSDT"] = corta
    esito = ctl.verifica_12_su_serie(V_VANTAGGIO, serie, FINE, **VELOCE)
    assert esito["monete"]["MATICUSDT"]["trade"] < 30
    assert esito["monete"]["MATICUSDT"]["batte"] is False
    assert esito["battono"] == 8


def test_controllo_fase3():
    s = serie_con_vantaggio("4h")
    serie = {k: s for k in ctl.MONETE_CONTROLLO}
    stessa = ctl.controllo_fase3_su_serie(V_VANTAGGIO, V_VANTAGGIO, serie, serie, FINE)
    assert stessa["differenza"] == pytest.approx(0.0)
    assert stessa["supera"] is False
    peggiore = dict(V_VANTAGGIO, uscite=[{"codice": "U2", "n": 48}])
    esito = ctl.controllo_fase3_su_serie(V_VANTAGGIO, peggiore, serie, serie, FINE)
    assert esito["supera"] is (esito["differenza"] >= 0.05)


def test_validazione_controllo():
    s = serie_con_vantaggio("4h")
    serie = {k: s for k in ctl.MONETE_CONTROLLO}
    esito = ctl.validazione_controllo_su_serie(V_VANTAGGIO, serie, _ms("2021-10-01"), FINE, **VELOCE)
    assert esito["monete_che_contano"] == 9
    assert esito["vantaggio_medio"] >= 0.1 and esito["media_r"] > 0
    assert esito["supera"] is True
    assert esito["media_r_costi_doppi"] is not None
    # con meno di 5 monete che hanno 20 trade non si puo' superare
    corte = {k: s.fino_a(200) for k in ctl.MONETE_CONTROLLO}
    esito = ctl.validazione_controllo_su_serie(V_VANTAGGIO, corte, _ms("2019-10-01"), FINE, **VELOCE)
    assert esito["supera"] is False
