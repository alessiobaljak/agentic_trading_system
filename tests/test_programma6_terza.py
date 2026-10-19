"""Programma 6, terza prova: gli indicatori di CTREND, i ranghi, le regressioni senza dati futuri, il conto
(research/programma6/TERZA.md)."""
import numpy as np
import pandas as pd
import pytest

pytest.importorskip("numba")
pytest.importorskip("sklearn")

from research.programma6 import seconda as sc  # noqa: E402
from research.programma6 import terza as te  # noqa: E402


def _col(nome):
    return te.NOMI.index(nome)


def test_indicatori_su_una_salita():
    n = 300
    c = np.linspace(100, 200, n)
    h, l = c + 1, c - 1
    v = np.full(n, 1e6)
    z = te.indicatori(c, h, l, c, v)
    assert z.shape == (n, 28)
    assert z[-1, _col("rsi")] == pytest.approx(100.0)
    assert z[-1, _col("sma_3d")] < 1 and z[-1, _col("sma_200d")] < z[-1, _col("sma_3d")]
    assert z[-1, _col("macd")] > 0
    assert z[-1, _col("volsma_20d")] == pytest.approx(1.0)
    assert np.isnan(z[100, _col("sma_200d")]) and np.isfinite(z[250, _col("sma_200d")])
    # chiusura sul massimo della giornata: Chaikin = +1
    z2 = te.indicatori(c, c, l, c, v)
    assert z2[-1, _col("chaikin")] == pytest.approx(1.0)
    # stocastico: chiusura sul massimo delle 14 giornate
    assert z2[-1, _col("stochK")] == pytest.approx(1.0)


def test_cci_e_bollinger():
    rng = np.random.default_rng(0)
    c = 100 + np.cumsum(rng.normal(0, 1, 100))
    z = te.indicatori(c, c + 0.5, c - 0.5, c, np.full(100, 1e6))
    s = pd.Series(c)
    mid, sd = s.rolling(20).mean().iloc[-1], s.rolling(20).std(ddof=0).iloc[-1]
    assert z[-1, _col("boll_mid")] == pytest.approx(mid / c[-1])
    assert z[-1, _col("boll_width")] == pytest.approx(4 * sd / mid)
    X = c[-20:]
    assert z[-1, _col("cci")] == pytest.approx((X[-1] - X.mean()) / (0.015 * np.abs(X - X.mean()).mean()))


def test_ranghi_fra_meno_e_piu_mezzo():
    Z = np.random.default_rng(1).normal(size=(3, 6, 2))
    Z[0, 2, 0] = np.nan
    U = np.ones((3, 6), bool)
    U[:, 5] = False
    r = te.ranghi(Z, U)
    assert r[1, :5, 0].min() == pytest.approx(-0.5) and r[1, :5, 0].max() == pytest.approx(0.5)
    assert r[0, 2, 0] == 0.0 and (r[:, 5] == 0).all()


def _sintetico(W=140, S=40, b=0.02, seme=2):
    rng = np.random.default_rng(seme)
    Zr = rng.uniform(-0.5, 0.5, (W, S, 28))
    R = b * Zr[:, :, 0] + rng.normal(0, 0.01, (W, S))
    U = np.ones((W, S), bool)
    peso = np.ones((W, S))
    return Zr, R, U, peso


def test_regressioni_ritrovano_la_pendenza():
    Zr, R, U, peso = _sintetico()
    coef = te.coefficienti(Zr, R, U, peso, True)
    assert np.nanmean(coef[:, 0, 1]) == pytest.approx(0.02, abs=0.003)
    assert abs(np.nanmean(coef[:, 5, 1])) < 0.003


def test_segnale_senza_dati_futuri_e_sceglie_l_indicatore_buono():
    Zr, R, U, peso = _sintetico()
    ct, tenute = te.segnale("C1", Zr, R, U, peso)
    w = 120
    assert np.isfinite(ct[w]).all()
    assert 0 in tenute[w]
    # cambiare i rendimenti dalla settimana w in poi non cambia il segnale di w
    R2 = R.copy()
    R2[w:] = -R2[w:] * 5
    ct2, _ = te.segnale("C1", Zr, R2, U, peso)
    assert np.allclose(ct[w], ct2[w])
    assert not np.allclose(ct[w + 1], ct2[w + 1])
    # prima di 104 settimane (52 per i coefficienti + 52 per la rete elastica) non c'e' segnale
    assert np.isnan(ct[:104]).all()
    ct3, _ = te.segnale("C2", Zr, R, U, peso)
    assert np.isnan(ct3[:52]).all() and np.isfinite(ct3[52]).all()


def test_portafoglio_quinti_e_conto():
    W, S = 2, 25
    ct = np.tile(np.arange(S, dtype=float), (W, 1))
    U = np.ones((W, S), bool)
    peso = np.ones((W, S))
    Wt = te.pesi_portafoglio(ct, U, peso, True)
    assert (Wt[0, -5:] == pytest.approx(0.2)) and (Wt[0, :5] == pytest.approx(-0.2))
    assert Wt[0].sum() == pytest.approx(0.0) and np.abs(Wt[0]).sum() == pytest.approx(2.0)
    R = np.zeros((W, S))
    R[0, -1] = 0.10           # il long migliore sale del 10%
    R[0, 0] = 0.10            # lo short peggiore sale del 10%
    F = np.zeros((W, S))
    F[0, 0] = 0.001           # funding positivo: lo short incassa
    costo = np.full(S, 0.0007)
    df = te.conto(Wt, R, F, costo)
    assert df["lordo"].iloc[0] == pytest.approx(0.2 * 0.1 - 0.2 * 0.1)
    assert df["funding"].iloc[0] == pytest.approx(-0.2 * 0.001)
    assert df["spese"].iloc[0] == pytest.approx(2.0 * 0.0007)
    assert df["long"].iloc[0] + df["short"].iloc[0] == pytest.approx(df["netto"].iloc[0])


def test_settimane_sono_lunedi():
    pan = {"t0": sc.giorno(2024, 1, 1), "close": np.ones((30, 1))}
    lun = te.settimane(pan) + pan["t0"]
    assert all(pd.Timestamp(int(x) * 86400, unit="s").weekday() == 0 for x in lun)
    assert len(lun) == 3      # 8, 15, 22 gennaio (il 29 non ha la settimana intera; l'1 non ha la domenica prima)


def test_sesta_funding_dei_sette_giorni_prima():
    from research.programma6 import sesta as se
    pan = {"funding": np.arange(20, dtype=float).reshape(20, 1)}
    s7 = se.funding_7(pan, np.array([10, 17]))
    assert s7[0, 0] == pytest.approx(sum(range(3, 10)))      # giorni 3..9, prima del lunedi' 10
    assert s7[1, 0] == pytest.approx(sum(range(10, 17)))
