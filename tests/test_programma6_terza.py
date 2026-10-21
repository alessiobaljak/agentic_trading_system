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


def test_ottava_sigma_dei_trenta_giorni_prima():
    from research.programma6 import ottava as ot
    C = np.cumprod(np.r_[1.0, np.tile([1.01, 0.99], 30)])[:, None] * 100
    pan = {"close": C}
    s = ot.sigma_30(pan, np.array([10, 40]))
    assert np.isnan(s[0, 0])                     # meno di 20 giorni
    r = C[1:, 0] / C[:-1, 0] - 1
    assert s[1, 0] == pytest.approx(np.std(r[9:39], ddof=1))


def test_nona_segnali_g1_e_g2():
    from research.programma6 import nona as no
    T = 40
    C = np.cumprod(np.r_[1.0, np.tile([1.02, 0.99], 20)])[:T, None] * 100
    V = np.full((T, 1), 100.0)
    B = np.full((T, 1), 60.0)
    pan = {"close": C, "quote_volume": V, "taker_buy_quote_volume": B}
    assert no.g1(pan, np.array([35]))[0, 0] == pytest.approx(0.6)
    assert np.isnan(no.g1(pan, np.array([3]))[0, 0])
    assert no.g2(pan, np.array([35]))[0, 0] == pytest.approx(0.02)


def _pan_giovani():
    """Un pannello di 40 giorni (dal lunedi' 2021-01-04 meno 28) e 3 monete: una vecchia, una nata al giorno 10, una
    nata al giorno 10 ma con volume zero dal giorno 30 (tolta dal listino)."""
    T, S = 40, 3
    t0 = sc.giorno(2020, 12, 7)                      # un lunedi'
    C = np.full((T, S), np.nan)
    C[:, 0] = 100.0
    C[10:, 1] = 50.0
    C[10:, 2] = 20.0
    V = np.where(np.isfinite(C), 5e6, np.nan)
    V[30:, 2] = 0.0
    F = np.where(np.isfinite(C), 0.001, 0.0)
    return {"t0": t0, "simboli": ["A", "B", "C"], "close": C, "open": C.copy(), "high": C.copy(), "low": C.copy(),
            "quote_volume": V, "taker_buy_quote_volume": V / 2, "funding": F}


def test_zombi_funding_zero_nei_giorni_a_volume_zero():
    from research.programma6 import controllo_zombi as cz
    pan = _pan_giovani()
    z = cz.giorni_fermi(pan)
    assert z[:, 2].sum() == 10 and not z[:, :2].any()
    assert not z[:10, 1].any()                     # dove manca la candela non e' un giorno fermo


def test_diciottesima_eta_e_giovani():
    from research.programma6 import diciottesima as di
    pan = _pan_giovani()
    lun = np.array([14, 21, 28, 35])               # lunedi' (indici nel pannello)
    eta = di.eta_lunedi(pan, lun)
    assert eta[0].tolist() == [13, 3, 3]           # domenica 13: la vecchia 13 giorni, le nuove 3
    assert eta[2].tolist() == [27, 17, 17]
    G = di.giovani(pan, lun, 7, 60)
    assert G[:, 0].sum() == 4                      # la "vecchia" qui ha meno di 60 giorni
    assert G[:, 1].tolist() == [False, True, True, True]
    assert G[:, 2].tolist() == [False, True, True, False]   # volume zero la domenica 34: fuori


def test_diciottesima_pesi_con_tetto_e_lato_long_uguale():
    from research.programma6 import diciottesima as di
    W, S = 2, 30
    G = np.zeros((W, S), bool)
    G[0, :4] = True                                # 4 giovani: 10% ciascuna (tetto)
    G[1, :2] = True                                # 2 giovani: meno di 3, niente
    U = np.zeros((W, S), bool)
    U[:, 5:] = True
    sig = np.full((W, S), 0.05)
    sig[:, 5] = 0.10
    p = di.pesi(G, U, sig)
    assert p[0, :4].tolist() == [-0.1] * 4
    assert p[0, 5:].sum() == pytest.approx(0.4)
    assert p[0, 5] == pytest.approx(p[0, 6] / 2)
    assert not p[1].any()


def test_diciottesima_conto_costo_per_settimana():
    from research.programma6 import diciottesima as di
    Wt = np.array([[-0.5, 0.5], [-0.5, 0.5]])
    R = np.array([[-0.10, 0.0], [0.0, 0.0]])
    F = np.array([[0.01, 0.0], [0.0, 0.0]])
    costo = np.array([[0.002, 0.001], [0.002, 0.001]])
    df = di.conto(Wt, R, F, costo)
    assert df.loc[0, "lordo"] == pytest.approx(0.05)
    assert df.loc[0, "spese"] == pytest.approx(0.5 * 0.002 + 0.5 * 0.001)
    assert df.loc[0, "funding_short"] == pytest.approx(-0.005)    # lo short riceve
    assert df.loc[0, "giovani"] == 1


def test_diciannovesima_premio_delle_168_ore_prima():
    from research.programma6 import diciannovesima as dn
    H = 24 * 20
    P = np.full((H, 2), np.nan, np.float32)
    P[:, 0] = np.arange(H, dtype=np.float32)
    P[24 * 7: 24 * 10, 1] = 1.0                  # solo 72 ore: meno di 120
    lun = np.array([7, 14])
    p7 = dn.premio_7(P, lun)
    assert p7[0, 0] == pytest.approx(np.arange(0, 168).mean())       # le ore 0..167, non la 168 del lunedi'
    assert p7[1, 0] == pytest.approx(np.arange(168, 336).mean())
    assert np.isnan(p7[1, 1])


def test_diciannovesima_settimane_pari():
    from research.programma6 import diciannovesima as dn
    S7 = np.array([np.arange(10, dtype=float), np.r_[np.zeros(9), 1.0]])
    U = np.ones((2, 10), bool)
    assert dn.settimane_pari(S7, U).tolist() == [False, True]


def test_ventesima_quota_a_pronti():
    from research.programma6 import ventesima as ve
    T = 20
    spot = np.full((T, 2), 1.0)
    perp = np.full((T, 2), 3.0)
    spot[:10, 1] = np.nan                         # coppia a pronti dal giorno 10
    q = ve.quota(spot, perp, np.array([7, 14]), 7, 5)
    assert q[0, 0] == pytest.approx(0.25) and q[1, 0] == pytest.approx(0.25)
    assert np.isnan(q[0, 1])                      # nessun giorno con tutti e due
    assert np.isnan(q[1, 1])                      # giorni 10-13: solo 4, meno di 5


def test_scarico_spot_nomi():
    from research.programma6 import scarico_spot as ss
    assert ss.nomi_a_pronti("1000PEPEUSDT") == ["1000PEPEUSDT", "PEPEUSDT"]
    assert ss.nomi_a_pronti("1MBABYDOGEUSDT") == ["1MBABYDOGEUSDT", "BABYDOGEUSDT"]
    assert ss.nomi_a_pronti("BTCUSDT") == ["BTCUSDT"]


def test_universo_senza_le_monete_a_volume_zero_la_domenica():
    T, S = 260, 3
    t0 = sc.giorno(2021, 1, 4)                     # un lunedi'
    C = np.full((T, S), 10.0)
    V = np.full((T, S), 5e6)
    V[250:, 2] = 0.0                               # la terza tolta dal listino dal giorno 250 (prezzo fermo)
    pan = {"t0": t0, "simboli": ["A", "B", "C"], "close": C, "open": C.copy(), "high": C.copy(), "low": C.copy(),
           "quote_volume": V, "taker_buy_quote_volume": V / 2, "funding": np.zeros((T, S))}
    ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
    lun = ps["lunedi"] - t0
    k_prima = int(np.flatnonzero(lun == 245)[0])
    k_dopo = int(np.flatnonzero(lun == 252)[0])
    assert ps["U"][k_prima].tolist() == [True, True, True]
    assert ps["U"][k_dopo].tolist() == [True, True, False]


def test_annunci_sigle_e_monitoraggio():
    from research.programma6 import annunci as an
    assert an._sigle("BICO & CVC") == ["BICO", "CVC"]
    assert an._sigle("ACT, BLUR, PIVX & QKC") == ["ACT", "BLUR", "PIVX", "QKC"]
    assert an._sigle("MTP, SLX (SLIMEX), CAI") == ["MTP", "SLX", "CAI"]
    assert an.perpetuo("PEPE", ["1000PEPEUSDT", "BTCUSDT"]) == "1000PEPEUSDT"
    assert an.perpetuo("XYZ", ["BTCUSDT"]) == ""


def test_ventunesima_rendimento_short_contro_btc():
    from research.programma6 import ventunesima as vu
    T = 12
    O = np.ones((T, 2))
    O[:, 0] = np.r_[[100.0] * 3, [80.0] * (T - 3)]     # la moneta scende del 20% dal giorno 3
    O[:, 1] = 50.0                                     # il Bitcoin fermo
    F = np.zeros((T, 2))
    F[:, 0] = 0.001                                    # funding positivo: lo short riceve
    pan = {"open": O, "close": O.copy(), "funding": F}
    r = vu.rendimento(pan, 0, 1, 2, 7)
    assert r == pytest.approx(0.20 - vu.COSTO_MONETA - vu.COSTO_BTC + 0.007)


def test_ventitreesima_media_dei_ranghi():
    from research.programma6 import ventitreesima as vt
    U = np.ones((1, 4), bool)
    P1 = np.array([[1.0, 2.0, 3.0, 4.0]])
    P2 = np.array([[40.0, 30.0, 20.0, 10.0]])
    m = vt.media_ranghi([P1, P2], U)
    assert np.allclose(m, 0.0)                    # ranghi opposti: la media e' il centro
    m1 = vt.media_ranghi([P1, P1 * 10], U)
    assert m1[0, 3] == pytest.approx(0.5) and m1[0, 0] == pytest.approx(-0.5)


def test_ventiquattresima_banda():
    from research.programma6 import ventiquattresima as vq
    S = 25
    U = np.ones((2, S), bool)
    sig = np.full((2, S), 0.05)
    ct = np.vstack([np.arange(S, dtype=float), np.arange(S, dtype=float)])
    ct[1, 24] = 16.0          # la migliore scende al 66° percentile: resta (sopra il 60%)
    ct[1, 23] = 5.0           # la seconda scende sotto il 40%: esce
    W = vq.pesi_banda(ct, U, sig)
    assert set(np.flatnonzero(W[0] > 0)) == {20, 21, 22, 23, 24}
    assert set(np.flatnonzero(W[0] < 0)) == {0, 1, 2, 3, 4}
    assert 24 in set(np.flatnonzero(W[1] > 0)) and 23 not in set(np.flatnonzero(W[1] > 0))
    assert W[1][W[1] > 0].sum() == pytest.approx(1.0) and W[1][W[1] < 0].sum() == pytest.approx(-1.0)


def test_ventiseiesima_long_contro_btc():
    from research.programma6 import ventiseiesima as vs
    from research.programma6 import ventunesima as vu
    T = 12
    O = np.ones((T, 2))
    O[:, 0] = np.r_[[100.0] * 3, [120.0] * (T - 3)]     # la moneta sale del 20%
    O[:, 1] = 50.0
    F = np.zeros((T, 2))
    F[:, 0] = -0.001                                   # funding negativo: il long riceve
    pan = {"open": O, "close": O.copy(), "funding": F}
    assert vs.rendimento(pan, 0, 1, 2, 7, 1) == pytest.approx(0.20 - vu.COSTO_MONETA - vu.COSTO_BTC + 0.007)
    assert vs.rendimento(pan, 0, 1, 2, 7, -1) == pytest.approx(vu.rendimento(pan, 0, 1, 2, 7))


def test_ventisettesima_eventi_e_buchi():
    from research.programma6 import ventisettesima as vt
    h = 3600
    ts = [0, 8 * h, 16 * h - 3, 20 * h, 24 * h + 2, 72 * h, 76 * h]   # 8, 8 (scarto di secondi), 4 (evento), 4, 48 (buco), 4
    righe = [[str(t), "0.001"] for t in ts]
    ev = vt.eventi_contratto(righe)
    assert [t for t, _ in ev] == [20 * h]
    f = vt.funding_giorni([[str(86400 + 60), "0.002"], [str(86400 * 2), "0.003"]])
    assert f.loc[1] == pytest.approx(0.005)                  # il regolamento alle 00:00 del giorno 2 chiude il giorno 1


def test_ventisettesima_salto_di_scala():
    from research.programma6 import ventisettesima as vt
    c = pd.DataFrame({"close": [1.0, 1.1, 0.9, 80.0, 81.0]}, index=[10, 11, 12, 13, 14])
    assert vt.salto(c, 11, 14) and not vt.salto(c, 10, 12)


def test_ventinovesima_rendimento_in_piu():
    from research.programma6 import ventinovesima as vn
    R = np.array([[0.1, 0.0, -0.1, np.nan], [0.0] * 4])
    U = np.array([[True, True, True, True], [True, False, False, False]])
    out = vn.rendimento_in_piu(R, U)
    assert np.nansum(out[0]) == pytest.approx(0.0) and np.isnan(out[0, 3])
    assert np.isnan(out[1]).all()                  # una moneta sola: niente


def test_trentesima_uscita_di_protezione():
    from research.programma6 import trentesima as tr
    from research.programma6 import ventunesima as vu
    e = 100
    h = np.arange(e * 24, (e + 31) * 24)
    c = pd.DataFrame({"open": 10.0, "high": 10.0, "close": 10.0}, index=h)
    c.loc[e * 24 + 5, "high"] = 13.5                     # +35% alla sesta ora: scatta l'uscita a +30%
    cb = pd.DataFrame({"open": 100.0, "high": 100.0, "close": 100.0}, index=h)
    vuoto = pd.Series(dtype=float)
    con = tr.operazione(c, cb, vuoto, vuoto, e, True)
    assert con["fermata"] and con["r"] == pytest.approx(-(1.3 * 1.01 - 1) - vu.COSTO_MONETA - vu.COSTO_BTC)
    senza = tr.operazione(c, cb, vuoto, vuoto, e, False)
    assert not senza["fermata"] and senza["r"] == pytest.approx(-vu.COSTO_MONETA - vu.COSTO_BTC)


def test_trentaquattresima_simulazione_stop_e_uscita_mobile():
    from research.programma6 import trentaquattresima as tq
    n = 60
    c = np.r_[np.full(30, 100.0), np.linspace(101, 130, 20), np.linspace(129, 100, 10)]
    o, h, l = c.copy(), c + 0.5, c - 0.5
    atr = np.full(n, 2.0)
    lungo = np.zeros(n, bool)
    lungo[30] = True
    corto = np.zeros(n, bool)
    op = tq._simula(o, h, l, c, lungo, corto, atr)
    i, e, u, verso, p0, p1, motivo = op[0]
    assert (i, e, verso) == (30, 31, 1) and motivo == 2          # esce con l'uscita mobile, non con lo stop
    # il livello e' 3 ATR sotto la chiusura migliore (124); la candela dopo apre gia' sotto (122,56): si esce all'apertura
    assert p1 == pytest.approx(np.linspace(129, 100, 10)[2]) and p1 < 130.0 - 3 * 2.0


def test_trentaquattresima_quattro_ore():
    from research.programma6 import trentaquattresima as tq
    h = pd.DataFrame({"open": np.arange(8.0), "high": np.arange(8.0) + 1, "low": np.arange(8.0) - 1,
                      "close": np.arange(8.0) + 0.5}, index=np.arange(8))
    b = tq.quattro_ore(h)
    assert b["open"].tolist() == [0.0, 4.0] and b["close"].tolist() == [3.5, 7.5] and b["high"].tolist() == [4.0, 8.0]


def test_trentacinquesima_rsi_e_obiettivo():
    from research.programma6 import trentacinquesima as tc
    c = np.r_[np.full(20, 100.0), np.linspace(100, 120, 10), np.linspace(119, 100, 15)]
    r = tc.rsi(c)
    assert np.nanmax(r) > 70 and r[-1] < 50
    n = len(c)
    o, h, l = c.copy(), c + 0.1, c - 0.1
    atr = np.full(n, 5.0)
    corto = np.zeros(n, bool)
    corto[29] = True
    op = tc._simula(o, h, l, c, np.zeros(n, bool), corto, atr, r)
    i, e, u, verso, p0, p1, motivo = op[0]
    assert verso == -1 and motivo == 2 and p1 < p0           # esce all'obiettivo (RSI a 50) in guadagno


def test_quarantesima_coppie(monkeypatch):
    from research.programma6 import quarantesima as qa
    from research.programma6.motore import TAKER
    assert [sc.data(g) for g in qa.primi_lunedi(sc.giorno(2021, 1, 1), sc.giorno(2021, 3, 31))] == \
        ["2021-01-04", "2021-02-01", "2021-03-01"]
    T, t0, s = 330, qa.DA - 250, 255
    rng = np.random.default_rng(1)
    lb = np.cumsum(rng.normal(0, 0.03, T)) + 5
    la = lb + 0.004 * np.sin(np.arange(T) * 1.3)
    la[s: s + 4] += 0.012                                     # A si allontana per quattro giorni, poi torna
    C = np.exp(np.vstack([la, lb]).T)
    pan = {"t0": t0, "simboli": ["AAAUSDT", "BBBUSDT"], "open": np.vstack([C[:1], C[:-1]]), "close": C,
           "quote_volume": np.tile([1.0, 10.0], (T, 1)), "funding": np.zeros((T, 2))}
    monkeypatch.setattr(qa, "A", qa.DA + 60)
    df, per_mese, lasciate = qa.operazioni(pan, np.ones((T, 2), bool))
    assert per_mese == {"2021-01": 1, "2021-02": 1, "2021-03": 1} and lasciate == 0
    assert df["simbolo"].iloc[0] == "AAAUSDT/BBBUSDT"         # A e' la meno scambiata
    assert (df["verso"] == -1).all() and df["data"].iloc[0] == sc.data(t0 + s + 1)   # short la cara, all'apertura dopo
    assert abs(df["b"].iloc[0] - 1) < 0.01 and df["correlazione"].iloc[0] > 0.9
    ultima = df.iloc[-1]
    assert ultima["motivo"] == "obiettivo" and ultima["r"] > 0.005
    assert ultima["costo"] == pytest.approx(2 * (TAKER + 0.0002) * (1 + min(ultima["b"], 2)))


def test_quarantunesima_eventi_e_operazione():
    from research.programma6 import quarantunesima as qu
    assert qu.multiplo("PEPEUSDT") == 1 and qu.multiplo("1000PEPEUSDT") == 1e3
    assert qu.multiplo("1000000MOGUSDT") == 1e6 and qu.multiplo("1MBABYDOGEUSDT") == 1e6
    t0 = sc.giorno(2022, 1, 1)
    T = 60
    close = np.full((T, 3), np.nan)
    close[:, 0] = 2.0                                          # AAAUSDT dal primo giorno, 2 dollari
    close[40:, 1] = 1.0                                        # BBBUSDT nato da poco
    close[:, 2] = 0.002                                        # 1000CCCUSDT: 0,000002 dollari a moneta
    pan = {"t0": t0, "simboli": ["AAAUSDT", "BBBUSDT", "1000CCCUSDT"], "close": close}
    q = [{"mercato": "KRW-AAA", "primo_mese": "2022-02-01", "primo_giorno": "2022-02-10", "prima_ora": "2022-02-10T05:00:00",
          "prezzo_primo_giorno": 2500.0},
         {"mercato": "KRW-BBB", "primo_mese": "2022-02-01", "primo_giorno": "2022-02-12", "prima_ora": "2022-02-12T05:00:00",
          "prezzo_primo_giorno": 1200.0},
         {"mercato": "KRW-CCC", "primo_mese": "2022-02-01", "primo_giorno": "2022-02-10", "prima_ora": "2022-02-10T05:00:00",
          "prezzo_primo_giorno": 2.5},                          # 1.250.000 won per dollaro: un omonimo
         {"mercato": "KRW-DDD", "primo_mese": "2022-02-01", "primo_giorno": "2022-02-10", "prima_ora": None}]
    ev, tolti = qu.eventi(pan, q)
    assert [x["simbolo"] for x in ev] == ["AAAUSDT"] and ev[0]["cambio"] == pytest.approx(1250.0)
    assert tolti["omonimo"] == 1 and tolti["perpetuo troppo giovane o dopo"] == 1 and tolti["senza ora d'arrivo"] == 1
    import pandas as pd
    ore = np.arange(1000, 1400)
    c = pd.DataFrame({"open": 100.0, "high": 101.0, "close": 100.0}, index=ore)
    cb = pd.DataFrame({"open": 50.0, "high": 50.0, "close": 50.0}, index=ore)
    c.loc[1100:, ["open", "close"]] = 90.0
    c.loc[1100:, "high"] = 91.0
    zero = pd.Series(0.0, index=np.arange(0, 100))
    o = qu.operazione(c, cb, zero, zero, 1010, 168, True)
    assert not o["fermata"] and o["uscita_h"] == 1178
    assert o["r"] == pytest.approx(0.10 - qu.vu.COSTO_MONETA - qu.vu.COSTO_BTC)     # short: la moneta scende del 10%
    c.loc[1050, "high"] = 131.0
    o = qu.operazione(c, cb, zero, zero, 1010, 168, True)
    assert o["fermata"] and o["uscita_h"] == 1050 and o["r"] < -0.30


def test_quarantaduesima_esposizione():
    import pandas as pd
    from research.programma6 import quarantaduesima as qd
    netto = pd.Series(np.r_[np.tile([0.02, -0.02], 10), np.tile([0.08, -0.08], 10)], index=np.arange(40) * 7)
    w = qd.esposizione(netto)
    assert (w.iloc[:8] == 1.0).all()                          # meno di 8 settimane: esposizione piena
    assert w.iloc[12] == pytest.approx(min(2.0, 0.30 / (netto.iloc[:12].std() * np.sqrt(52))))   # solo le settimane prima
    assert w.iloc[-1] < 0.6                                   # settimane agitate: si tiene meno
    f5 = pd.DataFrame({"netto": netto, "netto_doppio": netto - 0.001, "lordo": netto, "spese": 0.0, "funding": 0.0,
                       "giro": 1.0, "long": 0.0, "short": 0.0, "monete": 40}, index=netto.index)
    g = qd.gestita(f5)
    k = 25
    atteso = w.iloc[k] * netto.iloc[k] - abs(w.iloc[k] - w.iloc[k - 1]) * 2 * 0.0007
    assert g["netto"].iloc[k] == pytest.approx(atteso)


def test_quarantatreesima_minuti_e_funding():
    import pandas as pd
    from research.programma6 import quarantatreesima as qt
    F = np.zeros((3, 2))
    F[1, 0] = 0.0024                                           # funding del giorno 1 della moneta
    assert qt.funding_ore(F, 0, 0, 1440 + 720, 2 * 1440 + 720) == pytest.approx(0.0012)   # mezza giornata del giorno 1
    m = np.arange(1440, 1440 + 3000)
    c = pd.DataFrame({"open": 10.0, "high": 10.0, "low": 10.0, "close": 10.0}, index=m)
    cb = pd.DataFrame({"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0}, index=m)
    c.loc[1500:, ["open", "high", "low", "close"]] = 12.0
    o = qt.operazione(c, cb, (F, 0, 0, 1), 1445, 1440, 1)     # long: la moneta sale del 20%
    assert not o["fermata"] and o["uscita"] == 1445 + 1440
    funding = 0.0024 * (2880 - 1445) / 1440                   # il long paga il funding delle ore del giorno 1
    assert o["r"] == pytest.approx(0.20 - qt.COSTO_MONETA - qt.vu.COSTO_BTC - funding)
    c.loc[1600, "low"] = 6.9                                   # tocca il −30% dal prezzo d'entrata (10 → 7)
    o = qt.operazione(c, cb, (F, 0, 0, 1), 1445, 1440, 1)
    assert o["fermata"] and o["uscita"] == 1600 and o["r"] < -0.30


def test_quarantaquattresima_segnale_e_settimane(monkeypatch):
    import pandas as pd
    from research.programma6 import quarantaquattresima as qs
    lun = sc.giorno(2021, 1, 4)
    offerta = pd.Series({lun - 9: 100.0, lun - 2: 101.0, lun + 7 - 9: 101.0, lun + 7 - 2: 100.0})
    assert qs.segnale(offerta, lun) == pytest.approx(0.01)
    assert qs.segnale(offerta, lun + 7) < 0
    T, t0 = 40, lun - 10
    O = np.full((T, 1), 100.0)
    O[10 + 7:, 0] = 110.0                                     # la prima settimana il Bitcoin sale del 10%
    pan = {"t0": t0, "simboli": ["BTCUSDT"], "open": O, "funding": np.zeros((T, 1))}
    monkeypatch.setattr(qs, "A", lun + 7)
    df = qs.settimane(pan, offerta)
    assert df.loc[lun, "w"] == 1.0 and df.loc[lun, "netto"] == pytest.approx(0.10 - qs.COSTO)
    assert df.loc[lun + 7, "w"] == 0.0 and df.loc[lun + 7, "netto"] == pytest.approx(-qs.COSTO)   # esce: paga l'uscita


def test_quarantacinquesima_tendenza_e_rottura():
    from research.programma6 import quarantacinquesima as qc
    T = 40
    C = np.vstack([np.linspace(100, 140, T), np.linspace(140, 100, T)]).T          # una sale, l'altra scende
    pan = {"t0": 0, "close": C, "low": C - 1}
    t = qc.tendenza_domenica(pan, np.array([30]))
    assert t[0, 0] == 1.0 and t[0, 1] == -1.0
    # la banda: la moneta 0 ha il segnale per lo short ma la tendenza su → non entra; la 1 sì
    S = 25
    ct = np.tile(np.linspace(0, 1, S), (1, 1))
    tend = np.ones((1, S))
    tend[0, 1] = -1.0
    w = qc.pesi_banda_tendenza(ct, np.ones((1, S), bool), np.ones((1, S)), tend)
    assert w[0, 0] == 0.0 and w[0, 1] < 0 and w[0, -1] > 0
    # la prima chiusura sotto il minimo dei 5 giorni prima, dal 7° giorno d'età
    c = np.r_[np.full(10, 10.0), 9.0, np.full(30, 9.5)]
    pan = {"t0": 0, "close": c[:, None], "low": c[:, None] - 0.01}
    assert qc.prima_rottura(pan, 0, 0) == 10
    pan = {"t0": 0, "close": np.linspace(10, 20, 60)[:, None], "low": np.linspace(10, 20, 60)[:, None] - 0.01}
    assert qc.prima_rottura(pan, 0, 0) == -1                  # sempre in salita: nessuna rottura
