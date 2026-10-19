"""Programma 6, quarta prova: la regola congelata del rimbalzo dopo i crolli sulle ore (research/programma6/QUARTA.md)."""
import math

import numpy as np
import pandas as pd
import pytest

from research.programma6 import quarta as qa
from research.programma6 import seconda as sc


def _barre(n=900, crollo=800, ora0=1000):
    rng = np.random.default_rng(0)
    lc = np.cumsum(rng.normal(0, 0.01, n))
    lc[crollo - 3: crollo + 1] -= np.array([0.05, 0.10, 0.15, 0.20])   # crollo nelle 4 ore fino a `crollo`
    lc[crollo + 1:] -= 0.20
    c = np.exp(lc) * 100
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({"open": o, "high": np.maximum(o, c), "low": np.minimum(o, c), "close": c},
                        index=np.arange(ora0, ora0 + n))


def test_z4_usa_la_sigma_di_quattro_ore_prima():
    b = _barre()
    z = qa.z4(b["close"])
    lc = np.log(b["close"])
    sig = lc.diff().rolling(720, min_periods=500).std()
    t = 850
    assert z[t] == pytest.approx((lc.iloc[t] - lc.iloc[t - 4]) / (sig.iloc[t - 4] * 2))
    assert np.isnan(z[400])                     # meno di 500 ore di storia
    assert z[800] <= -5


def test_pausa_di_dodici_ore():
    cond = np.zeros(40, bool)
    cond[[3, 5, 14, 15, 30]] = True
    assert qa.sfoltisci(cond, 12).tolist() == [3, 15, 30]


def test_trade_ingresso_all_apertura_dopo_uscita_dopo_dodici_ore_e_funding():
    b = _barre()
    ora0 = int(b.index[0])
    pos = np.array([800])
    # un regolamento dentro la tenuta (minuto dell'ora 805) e uno all'ingresso esatto (non conta)
    f_min = np.array([(801 + ora0) * 60, (805 + ora0) * 60], np.int64)
    f_t = np.array([0.01, 0.001])
    t = qa.trade(b, pos, f_min, f_t)
    assert t["lordo"].iloc[0] == pytest.approx(b["close"].iloc[812] / b["open"].iloc[801] - 1)
    assert t["funding"].iloc[0] == pytest.approx(0.001)
    costi = 2 * (qa.TAKER + qa.SCARTO)
    assert t["netto"].iloc[0] == pytest.approx(t["lordo"].iloc[0] - costi - 0.001)
    assert t["netto_doppio"].iloc[0] == pytest.approx(t["lordo"].iloc[0] - 2 * costi - 0.001)
    # senza la chiusura dell'ora t+12 il trade si salta
    b2 = b.copy()
    b2.iloc[812, b2.columns.get_loc("close")] = np.nan
    assert qa.trade(b2, pos, f_min, f_t).empty


def test_caso_stesso_mese_e_stessa_tenuta():
    b = _barre(n=2000, crollo=1500, ora0=sc.giorno(2024, 3, 1) * 24)
    t = qa.trade(b, np.array([1500]), np.array([], np.int64), np.array([]))
    cs = qa.caso(b, t, np.array([], np.int64), np.array([]))
    assert len(cs) == qa.CASI
    mese = pd.to_datetime(cs["ora"].to_numpy() * 3600, unit="s").to_period("M").astype(str)
    mese_t = pd.to_datetime(t["ora"].to_numpy() * 3600, unit="s").to_period("M").astype(str)[0]
    assert (mese == mese_t).all()


def test_universo_esclude_le_monete_usate():
    T = 120
    t0 = sc.giorno(2021, 1, 1)
    C = np.full((T, 3), 1.0)
    V = np.full((T, 3), 2e7)
    V[:, 2] = 1e6
    pan = {"t0": t0, "simboli": ["BTCUSDT", "NUOVAUSDT", "PICCOLAUSDT"], "close": C, "quote_volume": V}
    um = qa.universo_mesi(pan, {"BTCUSDT"})
    assert um["2021-03"] == {"NUOVAUSDT"}
    assert "2021-01" not in um or um["2021-01"] == set()       # meno di 30 giorni di candele


def test_toccate_contiene_le_monete_del_programma_5():
    t = qa.toccate()
    assert {"BTCUSDT", "ETHUSDT", "SOLUSDT"} <= t and len(t) >= 100
