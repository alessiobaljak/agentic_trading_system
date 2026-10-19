"""Programma 6, seconda prova: la regola pubblicata, l'universo al tempo giusto, il conto del portafoglio
(research/programma6/SECONDA.md)."""
import numpy as np
import pandas as pd
import pytest

pytest.importorskip("numba")

from research.programma6 import seconda as sc  # noqa: E402


def test_modello_entra_sopra_il_massimo_ed_esce_sotto_lo_stop():
    c = np.array([10, 11, 10, 12, 13, 14, 13.4, 12.0, 11.0, 15.0])
    s = pd.Series(c)
    L = 3
    mx, mn = s.rolling(L).max(), s.rolling(L).min()
    mid = ((mx + mn) / 2).to_numpy()
    entra = (s > mx.shift(1)).to_numpy()
    st = sc._stato(c, entra, mid, 1)
    # giorno 3: 12 > max(10, 11, 10) = 11 -> dentro, stop = (12 + 10) / 2 = 11
    assert st[3] == 1 and st[:3].sum() == 0
    # giorno 4: stop -> (13 + 10) / 2 = 11.5; giorno 5: (14 + 12) / 2 = 13; giorno 6: 13.4 >= 13 resta, stop (14+13)/2=13.5
    assert st[4] == 1 and st[5] == 1 and st[6] == 1
    # giorno 7: 12 < 13.5 -> fuori
    assert st[7] == 0
    # giorno 9: 15 > max(13.4, 12, 11) -> di nuovo dentro
    assert st[9] == 1


def test_segnale_tutto_dentro_in_salita_e_tutto_short_in_discesa():
    su = np.exp(np.linspace(0, 3, 500))
    assert sc.segnale_moneta(su)[-1] == pytest.approx(1.0)
    giu = su[::-1].copy()
    assert sc.segnale_moneta(giu)[-1] == pytest.approx(0.0)
    assert sc.segnale_moneta(giu, short=True)[-1] == pytest.approx(-1.0)


def _pan(T=800, S=3, t0=None):
    t0 = sc.giorno(2020, 1, 1) if t0 is None else t0
    C = np.full((T, S), 100.0)
    V = np.full((T, S), 5e6)
    return {"t0": t0, "simboli": [f"M{j}USDT" for j in range(S)], "open": C.copy(), "high": C.copy(),
            "low": C.copy(), "close": C.copy(), "quote_volume": V, "funding": np.zeros((T, S))}


def test_universo_usa_solo_i_dati_di_allora():
    pan = _pan()
    # M1 nasce al giorno 300: per 365 giorni non e' ammessa
    for k in ("open", "high", "low", "close", "quote_volume"):
        pan[k][:300, 1] = np.nan
    # M2 ha un volume enorme solo dal giorno 500 in poi: prima resta dietro a M0
    pan["quote_volume"][:, 0] = 9e6
    pan["quote_volume"][500:, 2] = 1e9
    U = sc.universo(pan, 1)
    giorni = np.arange(800) + pan["t0"]
    mesi = pd.to_datetime(giorni * 86400, unit="s").to_period("M")
    # il mese che inizia dopo il giorno 500 + 30: M2 e' prima
    r = np.flatnonzero((mesi == mesi[560]))[0]
    assert U[r, 2] and not U[r, 0]
    # il mese che contiene il giorno 450 (prima del volume grande): M0
    r = np.flatnonzero((mesi == mesi[450]))[0]
    assert U[r, 0] and not U[r, 2]
    # M1 non e' mai ammessa prima del giorno 665 (300 + 365)
    assert not U[:665, 1].any()


def test_universo_salta_chi_non_ha_la_candela_di_ieri():
    pan = _pan(S=2)
    pan["quote_volume"][:, 1] = 9e6
    passo = np.exp(np.cumsum(np.random.default_rng(3).normal(0, 0.02, 800)))
    for k in ("open", "high", "low", "close"):
        pan[k][:, 1] = 100 * passo
    for k in ("open", "high", "low", "close", "quote_volume"):
        pan[k][600:, 1] = np.nan              # tolta dal listino al giorno 600
    U = sc.universo(pan, 1)
    giorni = np.arange(800) + pan["t0"]
    mesi = pd.to_datetime(giorni * 86400, unit="s").to_period("M")
    dopo = np.flatnonzero(mesi > mesi[600])[0]
    # l'universo vale per il mese: dal mese dopo la moneta tolta non c'e' piu', e c'e' l'altra
    assert U[600, 1] and not U[dopo:, 1].any() and U[dopo:, 0].all()
    # e il peso e' zero dal giorno in cui manca la candela di domani
    W = sc.pesi_regola(pan, "sempre", U)
    assert (W[599:, 1] == 0).all() and W[598, 1] > 0


def test_rendimento_tolta_dal_listino_esce_alla_chiusura():
    pan = _pan(T=5, S=1)
    pan["open"][:, 0] = [100, 110, 120, 130, np.nan]
    pan["close"][:, 0] = [105, 115, 125, 128, np.nan]
    r = sc.rendimenti(pan)
    assert r[1, 0] == pytest.approx(120 / 110 - 1)
    assert r[3, 0] == pytest.approx(128 / 130 - 1)
    assert r[4, 0] == 0.0


def test_portafoglio_costi_sul_giro_e_funding_col_segno():
    pan = _pan(T=4, S=1)
    pan["simboli"] = ["BTCUSDT"]
    pan["open"][:, 0] = [100, 100, 110, 110]
    pan["close"][:, 0] = [100, 110, 110, 110]
    pan["funding"][:, 0] = [0, 0.001, 0.001, 0]
    W = np.array([[0.5], [0.5], [0.0], [0.0]])
    df = sc.portafoglio(pan, W)
    costo = sc.TAKER + 0.0001
    # giorno 1: si compra 0.5 all'apertura (giro 0.5), si guadagna 0.5 * 10% e si paga il funding del long
    assert df["giro"].iloc[1] == pytest.approx(0.5)
    assert df["lordo"].iloc[1] == pytest.approx(0.05)
    assert df["funding"].iloc[1] == pytest.approx(0.0005)
    assert df["netto"].iloc[1] == pytest.approx(0.05 - 0.5 * costo - 0.0005)
    # giorno 2: il peso derivato e' salito col prezzo; riportarlo a 0.5 costa il giro della differenza
    deriva = 0.5 * 1.1 / (1 + df["netto"].iloc[1])
    assert df["giro"].iloc[2] == pytest.approx(abs(0.5 - deriva))
    # giorno 3: si vende tutto
    assert df["lordo"].iloc[3] == 0.0 and df["giro"].iloc[3] > 0.49


def test_funding_del_regolamento_di_mezzanotte_va_al_giorno_prima(tmp_path, monkeypatch):
    import io
    import zipfile
    d = tmp_path / "XUSDT" / "funding"
    d.mkdir(parents=True)
    g = sc.giorno(2024, 1, 2)
    righe = "calc_time,funding_interval_hours,last_funding_rate\n" + "\n".join(
        f"{(g * 1440 + m) * 60_000 + 5},8,{x}" for m, x in ((0, 0.001), (480, 0.002), (960, 0.003), (1440, 0.004)))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("XUSDT-fundingRate-2024-01.csv", righe)
    (d / "XUSDT-fundingRate-2024-01.zip").write_bytes(buf.getvalue())
    monkeypatch.setattr(sc, "DATI", tmp_path)
    f = sc.funding_giorni("XUSDT")
    assert f[g - 1] == pytest.approx(0.001)
    assert f[g] == pytest.approx(0.002 + 0.003 + 0.004)


def test_riempi_funding_con_la_media_prima():
    f = np.array([0.001, 0.003, 0.0, 0.0])
    ok = np.array([True, True, True, True])
    coperti = np.array([True, True, False, False])
    out = sc.riempi_funding(f, ok, coperti)
    assert out[2] == pytest.approx(0.002) and out[3] == pytest.approx(0.002)


def test_pesi_regola_rispettano_universo_e_domani():
    pan = _pan(T=900, S=2)
    salita = np.exp(np.linspace(0, 2, 900))
    for k in ("open", "high", "low", "close"):
        pan[k][:, 0] = salita
        pan[k][:, 1] = salita
    pan["simboli"] = ["BTCUSDT", "M1USDT"]
    U = np.zeros((900, 2), bool)
    U[:, 0] = True
    W = sc.pesi_regola(pan, "A1", U)
    assert (W[:, 1] == 0).all()
    assert W[-2, 0] > 0 and W[-1, 0] == 0          # l'ultimo giorno non ha un domani
    assert W[-2, 0] <= sc.MOLT_MAX / sc.N_A + 1e-12


def test_bootstrap_blocchi_positivo_e_zero():
    x = np.full(500, 0.001) + np.random.default_rng(0).normal(0, 0.0001, 500)
    b = sc.bootstrap_blocchi(x, n=500)
    assert b["basso"] > 0
    y = np.random.default_rng(1).normal(0, 0.01, 500)
    b = sc.bootstrap_blocchi(y - y.mean(), n=500)
    assert b["basso"] < 0 < b["alto"]


def test_capitale_con_tetto_salta_i_trade_oltre():
    t = pd.DataFrame({"minuto": [0, 10, 20, 2000], "uscita": [1000, 1000, 1000, 3000],
                      "frazione_stop": [0.004, 0.004, 0.004, 0.004], "netto": [0.01, 0.01, 0.01, 0.01]})
    out = sc.capitale_tetto(t, rischio=0.01, tetto=5.0)
    # ogni trade vale 2.5 volte il capitale: due insieme si', il terzo no; il quarto dopo l'uscita si'
    assert out["trade_presi"] == 3
