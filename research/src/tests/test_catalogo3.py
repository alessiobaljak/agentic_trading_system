"""Test di ``research/src/catalogo3.py`` contro ``research/PROTOCOLLO_3.md`` (sezioni 7.1-7.8 e 9.6).

* Indicatori della 7.2 confrontati con un'implementazione di riferimento indipendente
  (``riferimento3.py``, cicli Python scritti dalle formule del protocollo) su 900 candele di
  una passeggiata casuale con seme fisso, tolleranza relativa 1e-9 e NaN nelle stesse
  posizioni (Passo 0, punto 6), piu' esempi calcolati a mano.
* Definizione di incrocio (7.2), segnali E1-E12, filtri F1-F7, conferme C1-C3 su serie
  costruite apposta, long e short, e sulla passeggiata casuale contro il riferimento.
* ``normalizza``: valori del catalogo ammessi, tutto il resto rifiutato.
* Riscaldamento (7.8) e buchi nei dati (9.6).

Nessun file di dati: tutte le serie sono costruite in memoria.
"""

from __future__ import annotations

import itertools
import math

import numpy as np
import pytest

from research.src import catalogo3 as c3
from research.src.catalogo3 import Serie, VarianteNonValida, compila, normalizza, riscaldamento
from research.src.tests import riferimento3 as rif

MIN = 60_000
ORA = 60 * MIN
GIORNO = 24 * ORA
LUN = 1_609_718_400_000  # lunedi' 4 gennaio 2021, 00:00 UTC
VEN = 1_610_064_000_000  # venerdi' 8 gennaio 2021, 00:00 UTC
LUN_2024 = 1_704_067_200_000  # lunedi' 1 gennaio 2024, 00:00 UTC


# ---------------------------------------------------------------------------
# costruzione delle serie
# ---------------------------------------------------------------------------


def serie_da(tf, o, h, l, c, v=None, ts=None, t0=LUN, funding_ts=(), funding_tasso=()) -> Serie:
    c = np.asarray(c, dtype=float)
    n = len(c)
    durata = c3.TIMEFRAME_MS[tf]
    o = np.asarray(o, dtype=float)
    h = np.asarray(h, dtype=float)
    l = np.asarray(l, dtype=float)
    v = np.ones(n) if v is None else np.asarray(v, dtype=float)
    ts = t0 + durata * np.arange(n, dtype=np.int64) if ts is None else np.asarray(ts, dtype=np.int64)
    assert np.all(h >= np.maximum(o, c)) and np.all(l <= np.minimum(o, c)), "candele incoerenti"
    return Serie(tf, ts, o, h, l, c, v, o.copy(), h.copy(), l.copy(), c.copy(),
                 np.asarray(funding_ts, dtype=np.int64), np.asarray(funding_tasso, dtype=float))


def da_chiusure(tf, c, v=None, margine=0.5, **kw) -> Serie:
    """Apertura = chiusura precedente; massimo e minimo a +/- ``margine`` dal corpo."""
    c = np.asarray(c, dtype=float)
    o = np.concatenate([[c[0]], c[:-1]])
    return serie_da(tf, o, np.maximum(o, c) + margine, np.minimum(o, c) - margine, c, v, **kw)


def passeggiata(n=900, seme=2026, tf="1h", t0=LUN, togli=()) -> Serie:
    """Passeggiata casuale coerente (massimo >= apertura e chiusura >= minimo), volumi
    lognormali, funding ogni 8 ore con valori che toccano esattamente le soglie del catalogo.
    ``togli``: indici delle candele da togliere (buchi nei dati)."""
    rng = np.random.default_rng(seme)
    durata = c3.TIMEFRAME_MS[tf]
    # tratti di 60 candele in salita, piatti e in discesa, a turno: il prezzo resta limitato
    tendenza = np.repeat(np.tile([0.004, 0.0, -0.004, 0.0], n // 240 + 1), 60)[:n]
    close = 30_000.0 * np.exp(np.cumsum(rng.normal(0.0, 0.01, n) + tendenza))
    o = np.empty(n)
    o[0] = 30_000.0
    o[1:] = close[:-1] * (1.0 + rng.normal(0.0, 0.001, n - 1))
    h = np.maximum(o, close) * (1.0 + np.abs(rng.normal(0.0, 0.004, n)))
    l = np.minimum(o, close) * (1.0 - np.abs(rng.normal(0.0, 0.004, n)))
    v = rng.lognormal(3.0, 0.6, n)
    ts = t0 + durata * np.arange(n, dtype=np.int64)
    fts = np.arange(t0 - 8 * ORA, ts[-1] + durata + 8 * ORA, 8 * ORA, dtype=np.int64)
    ftasso = rng.choice([-0.0002, -0.0001, 0.0, 0.0001, 0.0002, 0.0003, 0.0004, 0.0005, 0.0006], len(fts))
    tieni = np.setdiff1d(np.arange(n), np.asarray(togli, dtype=np.int64))
    return serie_da(tf, o[tieni], h[tieni], l[tieni], close[tieni], v[tieni], ts=ts[tieni],
                    funding_ts=fts, funding_tasso=ftasso)


@pytest.fixture(scope="module")
def rw():
    return passeggiata()


@pytest.fixture(scope="module")
def rw15():
    return passeggiata(n=900, seme=7, tf="15m")


def solo(n, *indici) -> np.ndarray:
    out = np.zeros(n, dtype=bool)
    out[list(indici)] = True
    return out


def stessi_valori(modulo, riferimento, rtol=1e-9, cosa="", minimo=50):
    """Stesse posizioni dei NaN e |a - b| <= rtol x max(|b|, 1)."""
    a = np.asarray(modulo, dtype=float)
    b = np.asarray(riferimento, dtype=float)
    assert a.shape == b.shape, f"{cosa}: forme diverse {a.shape} {b.shape}"
    na, nb = np.isnan(a), np.isnan(b)
    diversi = np.flatnonzero(na != nb)
    assert diversi.size == 0, (f"{cosa}: NaN in posizioni diverse, prime: {diversi[:8].tolist()} "
                               f"(modulo {a[diversi[:3]].tolist()}, riferimento {b[diversi[:3]].tolist()})")
    d = ~na
    err = np.abs(a[d] - b[d])
    lim = rtol * np.maximum(np.abs(b[d]), 1.0)
    cattivi = np.flatnonzero(err > lim)
    assert cattivi.size == 0, (f"{cosa}: {cattivi.size} valori diversi; primo all'indice "
                               f"{np.flatnonzero(d)[cattivi[0]]}: modulo {a[d][cattivi[0]]!r}, "
                               f"riferimento {b[d][cattivi[0]]!r}")
    assert d.sum() >= minimo, f"{cosa}: troppo pochi valori definiti ({d.sum()})"


def stessi_booleani(modulo, atteso, cosa=""):
    a = np.asarray(modulo, dtype=bool)
    b = np.asarray(atteso, dtype=bool)
    assert a.shape == b.shape, cosa
    diversi = np.flatnonzero(a != b)
    assert diversi.size == 0, (f"{cosa}: {diversi.size} candele diverse, prime {diversi[:10].tolist()}; "
                               f"modulo vero a {np.flatnonzero(a)[:10].tolist()}, atteso vero a "
                               f"{np.flatnonzero(b)[:10].tolist()}")


S3 = {"codice": "S3", "pct": 0.01}
U1 = [{"codice": "U1", "k": 2}]


def var(ingresso, filtro=None, conferma=None, tf="1h", direzione="long", stop=None, uscite=None,
        tipo=None) -> dict:
    return {"timeframe": tf, "direzione": direzione, "filtro": filtro, "ingresso": ingresso,
            "conferma": conferma, "tipo_ingresso": tipo or {"codice": "M"}, "stop": stop or dict(S3),
            "uscite": uscite or [dict(u) for u in U1]}


# ---------------------------------------------------------------------------
# 7.2 - indicatori contro il riferimento, sulla passeggiata casuale (900 candele)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("n", [9, 20, 50, 100, 200])
def test_ema_come_riferimento(rw, n):
    stessi_valori(c3.ema(rw.close, n), rif.ema(rw.close, n), cosa=f"EMA({n})")


def test_ema_parte_dal_primo_valore_definito(rw):
    x = rw.close.copy()
    x[:25] = np.nan
    stessi_valori(c3.ema(x, 9), rif.ema(x, 9), cosa="EMA(9) con NaN iniziali")
    assert np.isnan(c3.ema(x, 9)[32]) and not np.isnan(c3.ema(x, 9)[33])


@pytest.mark.parametrize("n", [20, 50, 100, 200])
def test_sma_come_riferimento(rw, n):
    stessi_valori(c3.sma(rw.close, n), rif.sma(rw.close, n), cosa=f"SMA({n})")


@pytest.mark.parametrize("k", [2.0, 2.5])
def test_bollinger_come_riferimento(rw, k):
    stessi_valori(c3.deviazione_popolazione(rw.close, 20), rif.deviazione_popolazione(rw.close, 20),
                  cosa="deviazione di popolazione")
    inf, media, sup = rif.bollinger(rw.close, 20, k)
    m = c3.sma(rw.close, 20)
    d = c3.deviazione_popolazione(rw.close, 20)
    stessi_valori(m - k * d, inf, cosa=f"Bollinger inferiore k={k}")
    stessi_valori(m + k * d, sup, cosa=f"Bollinger superiore k={k}")


@pytest.mark.parametrize("n", [7, 14, 21])
def test_rsi_come_riferimento(rw, n):
    stessi_valori(c3.rsi(rw.close, n), rif.rsi(rw.close, n), cosa=f"RSI({n})")


def test_vero_range_e_atr_come_riferimento(rw):
    stessi_valori(c3.vero_range(rw.high, rw.low, rw.close), rif.vero_range(rw.high, rw.low, rw.close),
                  cosa="vero range")
    stessi_valori(c3.atr(rw.high, rw.low, rw.close, 14), rif.atr(rw.high, rw.low, rw.close, 14), cosa="ATR(14)")


def test_adx_come_riferimento(rw):
    stessi_valori(c3.adx(rw.high, rw.low, rw.close, 14), rif.adx(rw.high, rw.low, rw.close, 14), cosa="ADX(14)")


def test_stocastico_come_riferimento(rw):
    k, d = c3.stocastico(rw.high, rw.low, rw.close, 14, 3, 3)
    rk, rd = rif.stocastico(rw.high, rw.low, rw.close, 14, 3, 3)
    stessi_valori(k, rk, cosa="%K")
    stessi_valori(d, rd, cosa="%D")


def test_macd_come_riferimento(rw):
    linea, seg = c3.macd(rw.close, 12, 26, 9)
    rl, rs = rif.macd(rw.close, 12, 26, 9)
    stessi_valori(linea, rl, cosa="MACD linea")
    stessi_valori(seg, rs, cosa="MACD segnale")
    # linea definita dalla candela 25 (EMA 26), segnale dalla 33 (9 valori della linea)
    assert np.isnan(linea[24]) and not np.isnan(linea[25])
    assert np.isnan(seg[32]) and not np.isnan(seg[33])


@pytest.mark.parametrize("n", [20, 55])
def test_donchian_come_riferimento(rw, n):
    su, giu = c3.donchian(rw.high, rw.low, n)
    rs, rg = rif.donchian(rw.high, rw.low, n)
    stessi_valori(su, rs, cosa=f"Donchian({n}) massimo")
    stessi_valori(giu, rg, cosa=f"Donchian({n}) minimo")


def test_volume_relativo_come_riferimento(rw):
    stessi_valori(c3.volume_relativo(rw.volume, 20), rif.volume_relativo(rw.volume, 20), cosa="volume relativo")


def test_atr_percentile_come_riferimento(rw):
    a = c3.atr(rw.high, rw.low, rw.close, 14)
    stessi_valori(c3.atr_percentile(a, rw.close, 500),
                  rif.atr_percentile(rif.atr(rw.high, rw.low, rw.close, 14), rw.close, 500), cosa="ATR percentile")
    # primo valore: ATR definito dalla 14, 500 valori precedenti definiti dalla 514
    p = c3.atr_percentile(a, rw.close, 500)
    assert np.isnan(p[513]) and not np.isnan(p[514])


@pytest.mark.parametrize("quale", ["rw", "rw15"])
def test_vwap_e_range_asiatico_come_riferimento(quale, request):
    s = request.getfixturevalue(quale)
    stessi_valori(c3.vwap_giornaliero(s.ts, s.high, s.low, s.close, s.volume),
                  rif.vwap_giornaliero(s.ts, s.high, s.low, s.close, s.volume), cosa=f"VWAP {s.timeframe}")
    su, giu = c3.range_asiatico(s.ts, s.high, s.low, s.durata)
    rs, rg = rif.range_asiatico(s.ts, s.high, s.low)
    stessi_valori(su, rs, cosa=f"range asiatico massimo {s.timeframe}")
    stessi_valori(giu, rg, cosa=f"range asiatico minimo {s.timeframe}")


def test_funding_come_riferimento(rw):
    stessi_valori(c3.funding_regolato(rw.ts, rw.durata, rw.funding_ts, rw.funding_tasso),
                  rif.funding_regolato(rw.ts, rw.durata, rw.funding_ts, rw.funding_tasso), cosa="funding regolato")
    stessi_booleani(c3.prima_candela_dopo_regolamento(rw.ts, rw.funding_ts),
                    rif.prima_candela_dopo_regolamento(rw.ts, rw.funding_ts), "prima candela dopo il regolamento")
    # la prima candela dei dati: vale solo se un regolamento cade esattamente alla sua apertura
    assert c3.prima_candela_dopo_regolamento(np.array([LUN, LUN + ORA]), np.array([LUN]))[0]
    assert not c3.prima_candela_dopo_regolamento(np.array([LUN + ORA, LUN + 2 * ORA]), np.array([LUN]))[0]


def test_incroci_come_riferimento(rw):
    e9, e20 = c3.ema(rw.close, 9), c3.ema(rw.close, 20)
    stessi_booleani(c3.incrocio_su(e9, e20), rif.incrocio_su(e9, e20), "incrocio su fra due linee")
    stessi_booleani(c3.incrocio_giu(e9, e20), rif.incrocio_giu(e9, e20), "incrocio giu fra due linee")
    r = c3.rsi(rw.close, 7)
    for soglia in (20.0, 30.0, 50.0, 70.0, 80.0):
        stessi_booleani(c3.incrocio_su(r, soglia), rif.incrocio_su(r, soglia), f"RSI su {soglia}")
        stessi_booleani(c3.incrocio_giu(r, soglia), rif.incrocio_giu(r, soglia), f"RSI giu {soglia}")
    assert rif.incrocio_su(e9, e20).sum() >= 10  # il confronto non e' vuoto


# ---------------------------------------------------------------------------
# 7.2 - esempi calcolati a mano
# ---------------------------------------------------------------------------

# Sei candele (apertura, massimo, minimo, chiusura):
#   0: 10.0, 10.5,  9.5, 10   TR = NaN (nessuna chiusura precedente)
#   1: 10.2, 11.5, 10.0, 11   TR = max(1.5, 11.5-10=1.5, 10-10=0)       = 1.5
#   2: 11.2, 12.0, 11.0, 12   TR = max(1.0, 12-11=1.0, 11-11=0)         = 1.0
#   3: 12.6, 13.5, 12.5, 13   TR = max(1.0, 13.5-12=1.5, 12-12.5=-0.5)  = 1.5  (salto in su)
#   4: 12.4, 12.5, 11.0, 12   TR = max(1.5, 12.5-13=-0.5, 13-11=2.0)    = 2.0  (salto in giu)
#   5: 12.6, 14.5, 12.5, 14   TR = max(2.0, 14.5-12=2.5, 12-12.5=-0.5)  = 2.5
# EMA(3), alfa = 2/4 = 0.5: indice 2 = media(10, 11, 12) = 11; 3: 0.5x13 + 0.5x11 = 12;
#   4: 0.5x12 + 0.5x12 = 12; 5: 0.5x14 + 0.5x12 = 13.
# ATR(3) di Wilder sul TR (dalla seconda candela): indice 3 = media(1.5, 1.0, 1.5) = 4/3;
#   4: (4/3 x 2 + 2.0)/3 = 14/9; 5: (14/9 x 2 + 2.5)/3 = 50.5/27.
# RSI(3): variazioni +1, +1, +1, -1, +2. Indice 3: rialzi 1, ribassi 0 -> 100;
#   4: rialzi (1x2 + 0)/3 = 2/3, ribassi (0x2 + 1)/3 = 1/3, RS = 2 -> 100 - 100/3;
#   5: rialzi (2/3x2 + 2)/3 = 10/9, ribassi (1/3x2 + 0)/3 = 2/9, RS = 5 -> 100 - 100/6.
MANO_O = [10.0, 10.2, 11.2, 12.6, 12.4, 12.6]
MANO_H = [10.5, 11.5, 12.0, 13.5, 12.5, 14.5]
MANO_L = [9.5, 10.0, 11.0, 12.5, 11.0, 12.5]
MANO_C = [10.0, 11.0, 12.0, 13.0, 12.0, 14.0]


def test_ema3_a_mano():
    stessi_valori(c3.ema(np.array(MANO_C), 3), [np.nan, np.nan, 11.0, 12.0, 12.0, 13.0], rtol=1e-12, cosa="EMA(3)",
                  minimo=4)


def test_vero_range_e_atr3_a_mano():
    nan = np.nan
    tr = c3.vero_range(np.array(MANO_H), np.array(MANO_L), np.array(MANO_C))
    assert np.isnan(tr[0])
    np.testing.assert_allclose(tr[1:], [1.5, 1.0, 1.5, 2.0, 2.5], rtol=1e-12)
    a = c3.atr(np.array(MANO_H), np.array(MANO_L), np.array(MANO_C), 3)
    atteso = [nan, nan, nan, 4 / 3, 14 / 9, 50.5 / 27]
    assert np.array_equal(np.isnan(a), np.isnan(atteso))
    np.testing.assert_allclose(a[3:], atteso[3:], rtol=1e-12)


def test_rsi3_a_mano():
    r = c3.rsi(np.array(MANO_C), 3)
    assert np.all(np.isnan(r[:3]))
    np.testing.assert_allclose(r[3:], [100.0, 100 - 100 / 3, 100 - 100 / 6], rtol=1e-12)


def test_rsi_piatto_vale_50_e_stocastico_piatto_vale_50():
    c = np.full(40, 128.0)
    assert np.all(c3.rsi(c, 14)[14:] == 50.0) and np.all(np.isnan(c3.rsi(c, 14)[:14]))
    k, d = c3.stocastico(c, c, c)  # massimo = minimo: %K grezzo 50 (SCELTA)
    assert np.all(k[15:] == 50.0) and np.all(d[17:] == 50.0)
    assert np.all(np.isnan(k[:15])) and np.all(np.isnan(d[:17]))


def test_donchian_e_volume_relativo_escludono_la_candela_corrente():
    h = np.array([1.0, 2.0, 3.0, 9.0])
    l = np.array([0.5, 1.0, 2.0, 0.1])
    su, giu = c3.donchian(h, l, 3)
    assert np.isnan(su[2]) and su[3] == 3.0 and giu[3] == 0.5  # la candela 3 (9.0 / 0.1) non conta
    v = np.array([10.0, 20.0, 30.0, 60.0])
    rv = c3.volume_relativo(v, 3)
    assert np.isnan(rv[2]) and rv[3] == 60.0 / 20.0


def test_atr_percentile_conta_i_precedenti_strettamente_minori():
    # x = ATR / chiusura con chiusura 1: [1, 2, 2, 3, 2] e finestra 3.
    # indice 3: precedenti 1, 2, 2 -> tutti minori di 3 -> 100; indice 4: precedenti 2, 2, 3 -> nessuno < 2 -> 0
    a = np.array([1.0, 2.0, 2.0, 3.0, 2.0])
    p = c3.atr_percentile(a, np.ones(5), 3)
    assert np.all(np.isnan(p[:3])) and p[3] == 100.0 and p[4] == 0.0


def test_vwap_a_mano_e_azzerato_ogni_giorno_utc():
    # giorno 1: 0: (102, 98, 100) v 10 -> tipico 100 -> VWAP 100
    #           1: (106, 100, 103) v 30 -> tipico 103 -> VWAP (1000 + 3090)/40 = 102.25
    #           2: (104, 96, 97) v 20 -> tipico 99 -> VWAP (4090 + 1980)/60 = 101.1666...
    # giorno 2, candela 24: (112, 100, 105) v 1 -> tipico 105.666... -> VWAP 105.666... (azzerato)
    n = 25
    o = np.full(n, 100.0)
    h = np.full(n, 101.0)
    l = np.full(n, 99.0)
    c = np.full(n, 100.0)
    v = np.ones(n)
    o[:3], h[:3], l[:3], c[:3], v[:3] = [100, 100, 100], [102, 106, 104], [98, 100, 96], [100, 103, 97], [10, 30, 20]
    o[24], h[24], l[24], c[24], v[24] = 104, 112, 100, 105, 1
    s = serie_da("1h", o, h, l, c, v)
    vw = c3.vwap_giornaliero(s.ts, s.high, s.low, s.close, s.volume)
    np.testing.assert_allclose(vw[:3], [100.0, 102.25, 6070 / 60], rtol=1e-12)
    np.testing.assert_allclose(vw[24], 317 / 3, rtol=1e-12)
    # F7 sopra / sotto (7.4): uguaglianza = ne' sopra ne' sotto
    sopra = compila(var({"codice": "E10"}, filtro={"codice": "F7", "lato": "sopra"}), s).dettagli["filtro"]
    sotto = compila(var({"codice": "E10"}, filtro={"codice": "F7", "lato": "sotto"}), s).dettagli["filtro"]
    assert (sopra[0], sopra[1], sopra[2], sopra[24]) == (False, True, False, False)
    assert (sotto[0], sotto[1], sotto[2], sotto[24]) == (False, False, True, True)


def test_range_asiatico_a_mano_15m():
    # 15m: le candele da 00:00 a 07:45 fanno il range; la 07:45 ha il massimo (102) e il minimo (97)
    n = 40
    o = np.full(n, 100.0)
    c = np.full(n, 100.0)
    h = np.full(n, 100.5)
    l = np.full(n, 99.5)
    h[31], l[31] = 102.0, 97.0  # 07:45
    h[32] = 103.0  # 08:00: non fa parte del range
    s = serie_da("15m", o, h, l, c)
    su, giu = c3.range_asiatico(s.ts, s.high, s.low, s.durata)
    assert np.all(np.isnan(su[:32])) and np.all(np.isnan(giu[:32]))
    assert np.all(su[32:] == 102.0) and np.all(giu[32:] == 97.0)


def test_funding_regolato_alla_chiusura_della_candela():
    # regolamenti 00:00 (0.0001), 08:00 (0.0004), 16:00 (-0.0002)
    fts = [LUN, LUN + 8 * ORA, LUN + 16 * ORA]
    ft = [0.0001, 0.0004, -0.0002]
    ts1 = LUN + ORA * np.arange(24)
    f1 = c3.funding_regolato(ts1, ORA, fts, ft)
    assert np.all(f1[:8] == 0.0001) and np.all(f1[8:16] == 0.0004) and np.all(f1[16:] == -0.0002)
    # 12h: la candela 00:00-12:00 chiude dopo il regolamento delle 08:00
    ts12 = LUN + 12 * ORA * np.arange(2)
    f12 = c3.funding_regolato(ts12, 12 * ORA, fts, ft)
    assert f12[0] == 0.0004 and f12[1] == -0.0002
    # una candela che chiude prima di ogni regolamento: NaN
    assert np.isnan(c3.funding_regolato(np.array([LUN - ORA]), ORA, fts, ft)[0])


# ---------------------------------------------------------------------------
# 7.2 - "incrocia verso l'alto / verso il basso"
# ---------------------------------------------------------------------------


def test_incrocio_su_con_uguaglianze():
    a = np.array([1.0, 2.0, 2.0, 3.0, 1.0, 1.0, 2.0])
    # 1: 1<=2 ma 2>2 no; 2: 2<=2 ma 2>2 no; 3: 2<=2 e 3>2 SI (uguale prima conta);
    # 4: 3<=2 no; 5: 1>2 no; 6: arriva a 2 ma non lo supera -> no
    stessi_booleani(c3.incrocio_su(a, 2.0), solo(7, 3), "incrocio su con soglia")
    stessi_booleani(c3.incrocio_su(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 2.0])), solo(3, 2),
                    "incrocio su fra due linee uguali prima")
    assert not c3.incrocio_su(np.array([2.0, 3.0]), 2.0)[0]  # la prima candela non incrocia mai
    assert c3.incrocio_su(np.array([2.0, 3.0]), 2.0)[1]
    assert not c3.incrocio_su(np.array([np.nan, 3.0]), 2.0)[1]
    assert not c3.incrocio_su(np.array([1.0, 3.0]), np.array([np.nan, 2.0]))[1]


def test_incrocio_giu_con_uguaglianze():
    a = np.array([3.0, 2.0, 2.0, 1.0, 3.0, 3.0, 2.0])
    stessi_booleani(c3.incrocio_giu(a, 2.0), solo(7, 3), "incrocio giu con soglia")
    stessi_booleani(c3.incrocio_giu(np.array([3.0, 2.0, 1.0]), np.array([3.0, 2.0, 2.0])), solo(3, 2),
                    "incrocio giu fra due linee uguali prima")
    assert not c3.incrocio_giu(np.array([2.0, 2.0]), 2.0)[1]
    assert not c3.incrocio_giu(np.array([np.nan, 1.0]), 2.0)[1]


# ---------------------------------------------------------------------------
# 7.3 - segnali di ingresso su serie costruite apposta (long e short)
# ---------------------------------------------------------------------------


def ingresso(v, s):
    return compila(v, s).dettagli["ingresso"]


@pytest.mark.parametrize("direzione", ["long", "short"])
def test_E1_incrocio_di_medie(direzione):
    # long: 60 chiusure in discesa (200 -> 141; EMA 9 sotto la EMA 20), poi salto a 300: la veloce
    # passa sopra la lenta alla candela 60 e ci resta. Short: lo specchio.
    giu = [200.0 - i for i in range(60)] + [300.0] * 10
    su = [100.0 + i for i in range(60)] + [20.0] * 10
    e = {"codice": "E1", "media": "EMA", "veloce": 9, "lenta": 20}
    s_long, s_short = da_chiusure("1h", giu), da_chiusure("1h", su)
    if direzione == "long":
        stessi_booleani(ingresso(var(e), s_long), solo(70, 60), "E1 long")
        assert not ingresso(var(e, direzione="short"), s_long).any()
        cp = compila(var(e), s_long)
        assert cp.riscaldamento == 60 and cp.segnale[60]  # 60 = 3 x 20
    else:
        stessi_booleani(ingresso(var(e, direzione="short"), s_short), solo(70, 60), "E1 short")
        assert not ingresso(var(e), s_short).any()


@pytest.mark.parametrize("media", ["EMA", "SMA"])
def test_E2_prezzo_e_media(media):
    giu = [140.0 - i for i in range(40)] + [200.0] * 6
    su = [100.0 + i for i in range(40)] + [50.0] * 6
    e = {"codice": "E2", "media": media, "n": 20}
    stessi_booleani(ingresso(var(e), da_chiusure("1h", giu)), solo(46, 40), f"E2 {media} long")
    stessi_booleani(ingresso(var(e, direzione="short"), da_chiusure("1h", su)), solo(46, 40), f"E2 {media} short")
    assert not ingresso(var(e, direzione="short"), da_chiusure("1h", giu)).any()
    cp = compila(var(e), da_chiusure("1h", giu))
    # riscaldamento: SMA 20 -> 20 candele, EMA 20 -> 60 (ricorsiva): con la EMA il segnale della
    # candela 40 cade nel riscaldamento
    assert cp.segnale[40] == (media == "SMA")


def _canale(n, ultimo, prossimo):
    """30 candele fra 99.5 e 101.0, poi la candela 30 (``ultimo``) e la 31 (``prossimo``):
    tuple (apertura, massimo, minimo, chiusura)."""
    righe = [(100.0, 101.0, 99.5, 100.5) if i % 2 else (100.5, 101.0, 99.5, 100.0) for i in range(30)]
    return righe + [ultimo, prossimo]


@pytest.mark.parametrize("direzione", ["long", "short"])
def test_E3_rottura_di_donchian(direzione):
    # long: candela 30 chiude a 105 sopra il massimo delle 20 precedenti (101.0); il suo massimo
    # e' 105.5: se la candela corrente contasse nel canale la rottura non ci sarebbe. Candela 31
    # chiude a 104 < 105.5 (massimo della candela 30, ora nel canale): niente rottura.
    if direzione == "long":
        righe = _canale(30, (100.5, 105.5, 100.0, 105.0), (105.0, 105.2, 103.8, 104.0))
    else:
        righe = _canale(30, (100.0, 100.5, 94.5, 95.0), (95.0, 96.2, 94.8, 96.0))
    o, h, l, c = (np.array(x) for x in zip(*righe))
    s = serie_da("1h", o, h, l, c)
    e = {"codice": "E3", "n": 20}
    stessi_booleani(ingresso(var(e, direzione=direzione), s), solo(32, 30), f"E3 {direzione}")
    altra = "short" if direzione == "long" else "long"
    assert not ingresso(var(e, direzione=altra), s).any()
    cp = compila(var(e, direzione=direzione), s)
    assert cp.dettagli["donchian_su"][30] == 101.0 and cp.dettagli["donchian_giu"][30] == 99.5
    assert cp.segnale[30]


def _alternata(ultimi):
    """25 chiusure alternate 100 / 101 (pari 100, dispari 101), poi ``ultimi``."""
    return [100.0 if i % 2 == 0 else 101.0 for i in range(25)] + list(ultimi)


@pytest.mark.parametrize("k", [2.0, 2.5])
def test_E4_rottura_di_bollinger(k):
    # candela 25 = 110: media delle ultime 20 = 2019/20 = 100.95, deviazione = sqrt(90.95/20) = 2.13,
    # banda superiore 105.2 (k 2) o 106.3 (k 2.5): 110 la supera. Prima: bande 99.5 / 101.5 (k 2),
    # le chiusure 100 e 101 restano dentro. Candela 26 = 101: dentro.
    e = {"codice": "E4", "k": k}
    s_su = da_chiusure("1h", _alternata([110.0, 101.0]))
    s_giu = da_chiusure("1h", _alternata([91.0, 100.0]))
    stessi_booleani(ingresso(var(e), s_su), solo(27, 25), "E4 long")
    stessi_booleani(ingresso(var(e, direzione="short"), s_giu), solo(27, 25), "E4 short")
    assert not ingresso(var(e, direzione="short"), s_su).any()
    assert not ingresso(var(e), s_giu).any()


@pytest.mark.parametrize("k", [2.0, 2.5])
def test_E5_ritorno_da_bollinger(k):
    # long: candela 25 = 91 sotto la banda inferiore (media 100, deviazione 2.12 -> 95.8 o 94.7);
    # candela 26 = 100 di nuovo dentro (bande 95.8-104.2 o 94.7-105.3): segnale alla 26.
    # La 25 non lo e' (la 24 era dentro). Con la 26 ancora fuori (85) non c'e' segnale.
    e = {"codice": "E5", "k": k}
    stessi_booleani(ingresso(var(e), da_chiusure("1h", _alternata([91.0, 100.0]))), solo(27, 26), "E5 long")
    stessi_booleani(ingresso(var(e, direzione="short"), da_chiusure("1h", _alternata([110.0, 101.0]))),
                    solo(27, 26), "E5 short")
    assert not ingresso(var(e), da_chiusure("1h", _alternata([91.0, 85.0]))).any()
    assert not ingresso(var(e, direzione="short"), da_chiusure("1h", _alternata([110.0, 118.0]))).any()
    assert not ingresso(var(e, direzione="short"), da_chiusure("1h", _alternata([91.0, 100.0]))).any()


def _rsi_scende_poi_sale(x):
    # 20 chiusure in discesa di 1 (RSI 0), poi +x e piatto: RSI(14) = 100 x / (13 + x)
    return [120.0 - i for i in range(20)] + [101.0 + x] * 6


def _rsi_sale_poi_scende(x):
    # 20 chiusure in salita di 1 (RSI 100), poi -x e piatto: RSI(14) = 1300 / (13 + x)
    return [100.0 + i for i in range(20)] + [119.0 - x] * 6


@pytest.mark.parametrize("soglie", [[30, 70], [20, 80]])
def test_E6_rsi_dagli_estremi(soglie):
    e = {"codice": "E6", "n": 14, "soglie": soglie}
    # x = 10: RSI da 0 a 43.5 (sopra 30 e 20) alla candela 20; poi resta 43.5
    stessi_booleani(ingresso(var(e), da_chiusure("1h", _rsi_scende_poi_sale(10.0))), solo(26, 20), "E6 long")
    # x = 10: RSI da 100 a 56.5 (sotto 70 e 80)
    stessi_booleani(ingresso(var(e, direzione="short"), da_chiusure("1h", _rsi_sale_poi_scende(10.0))),
                    solo(26, 20), "E6 short")
    # x = 2: RSI 13.3, sotto entrambe le soglie basse: nessun incrocio
    assert not ingresso(var(e), da_chiusure("1h", _rsi_scende_poi_sale(2.0))).any()
    np.testing.assert_allclose(c3.rsi(np.array(_rsi_scende_poi_sale(10.0)), 14)[20], 1000 / 23, rtol=1e-9)


def test_E7_rsi_e_meta():
    e = {"codice": "E7", "n": 14}
    # x = 10: RSI 43.5 < 50: niente; x = 20: RSI 60.6: incrocio su 50 alla 20
    assert not ingresso(var(e), da_chiusure("1h", _rsi_scende_poi_sale(10.0))).any()
    stessi_booleani(ingresso(var(e), da_chiusure("1h", _rsi_scende_poi_sale(20.0))), solo(26, 20), "E7 long")
    # short: x = 10 -> 56.5 (sopra 50): niente; x = 20 -> 39.4: incrocio giu
    assert not ingresso(var(e, direzione="short"), da_chiusure("1h", _rsi_sale_poi_scende(10.0))).any()
    stessi_booleani(ingresso(var(e, direzione="short"), da_chiusure("1h", _rsi_sale_poi_scende(20.0))),
                    solo(26, 20), "E7 short")


def _stoc_discesa(ultima):
    """30 candele in discesa con chiusura = minimo (%K grezzo 0), poi ``ultima``."""
    righe = [(131.0 - i, 131.0 - i, 130.0 - i, 130.0 - i) for i in range(30)]  # o, h, l, c
    return righe + [ultima]


def _stoc_salita(ultima):
    righe = [(99.0 + i, 100.0 + i, 99.0 + i, 100.0 + i) for i in range(30)]
    return righe + [ultima]


def test_E8_stocastico():
    e = {"codice": "E8"}

    def s(righe):
        o, h, l, c = (np.array(x) for x in zip(*righe))
        return serie_da("1h", o, h, l, c)

    # long: alla 30 chiude a 102 (minimo 14 = 101, massimo 14 = 114): grezzo 100 x 1/13 = 7.7,
    # %K = 2.6 > %D = 0.85, prima entrambi 0 (uguali): incrocio con %K sotto 20
    lo = s(_stoc_discesa((101.0, 102.5, 101.0, 102.0)))
    k, d = c3.stocastico(lo.high, lo.low, lo.close)
    assert k[29] == 0.0 and d[29] == 0.0 and k[30] < 20 and k[30] > d[30]
    stessi_booleani(ingresso(var(e), lo), solo(31, 30), "E8 long")
    assert not ingresso(var(e, direzione="short"), lo).any()
    # incrocio con %K sopra 20 (chiusura a 114: grezzo 13/13.5 x 100 = 96, %K = 32): nessun segnale
    assert not ingresso(var(e), s(_stoc_discesa((101.0, 114.5, 101.0, 114.0)))).any()
    # short: salita con chiusura = massimo (grezzo 100), alla 30 chiude a 128: %K 97.3 < %D 99.1
    sh = s(_stoc_salita((129.0, 129.0, 127.5, 128.0)))
    stessi_booleani(ingresso(var(e, direzione="short"), sh), solo(31, 30), "E8 short")
    assert not ingresso(var(e), sh).any()
    # incrocio giu con %K sotto 80 (chiusura a 117): nessun segnale short
    assert not ingresso(var(e, direzione="short"), s(_stoc_salita((129.0, 129.0, 116.5, 117.0)))).any()


def test_E9_macd():
    # discesa che accelera (300 - 0.03 i^2: la linea scende e resta sotto il segnale), poi salto a 250:
    # la linea passa sopra il segnale alla candela 80. Short: lo specchio.
    giu = [300.0 - 0.03 * i * i for i in range(80)] + [250.0] * 6
    su = [100.0 + 0.03 * i * i for i in range(80)] + [150.0] * 6
    e = {"codice": "E9"}
    stessi_booleani(ingresso(var(e), da_chiusure("1h", giu)), solo(86, 80), "E9 long")
    stessi_booleani(ingresso(var(e, direzione="short"), da_chiusure("1h", su)), solo(86, 80), "E9 short")
    assert not ingresso(var(e, direzione="short"), da_chiusure("1h", giu)).any()
    assert compila(var(e), da_chiusure("1h", giu)).riscaldamento == 78


def _giorni_e10(togli=()):
    """Tre giorni di candele 1h dal lunedi' 4 gennaio 2021.

    giorno 0: range asiatico 99-101; 08:00 chiude 100.8 (dentro), 09:00 chiude 101.5 (prima
              rottura: segnale long), 10:00 chiude 102 (secondo: niente); 16:00 chiude 98.5
              (sotto il minimo ma fuori orario: niente short).
    giorno 1: range 95-105; 12:00 chiude 94 (short), 13:00 chiude 93 (secondo short: niente);
              15:00 chiude 106 (long, ultima candela che apre prima delle 16:00); 16:00 chiude 107.
    giorno 2: range 99-101; dalle 08:00 alle 15:00 chiusure dentro; 16:00 chiude 103 (fuori orario).
    """
    righe = []
    for g in range(3):
        for ora in range(24):
            righe.append([100.0, 100.0])  # apertura, chiusura
    o = np.array([r[0] for r in righe])
    c = np.array([r[1] for r in righe])
    h = np.maximum(o, c) + 0.2
    l = np.minimum(o, c) - 0.2
    # giorno 0, Asia: massimo 101, minimo 99
    h[3], l[5] = 101.0, 99.0
    c[8], h[8] = 100.8, 100.9
    c[9], h[9] = 101.5, 101.8
    c[10], h[10] = 102.0, 102.3
    c[16], l[16] = 98.5, 98.3
    # giorno 1 (24-47), Asia: massimo 105, minimo 95
    h[24 + 2], l[24 + 6] = 105.0, 95.0
    c[24 + 12], l[24 + 12] = 94.0, 93.8
    c[24 + 13], l[24 + 13] = 93.0, 92.8
    c[24 + 15], h[24 + 15] = 106.0, 106.2
    c[24 + 16], h[24 + 16] = 107.0, 107.2
    # giorno 2 (48-71)
    h[48 + 1], l[48 + 4] = 101.0, 99.0
    c[48 + 16], h[48 + 16] = 103.0, 103.2
    ts = LUN + ORA * np.arange(len(c))
    k = np.setdiff1d(np.arange(len(c)), np.asarray(togli, dtype=np.int64))
    return serie_da("1h", o[k], h[k], l[k], c[k], ts=ts[k])


def test_E10_rottura_del_range_asiatico_un_segnale_al_giorno():
    s = _giorni_e10()
    e = {"codice": "E10"}
    stessi_booleani(ingresso(var(e), s), solo(72, 9, 24 + 15), "E10 long")
    stessi_booleani(ingresso(var(e, direzione="short"), s), solo(72, 24 + 12), "E10 short")


def test_E10_e_F7_in_un_giorno_con_candele_mancanti():
    # SCELTA del modulo (giorno_completo, non etichettata SCELTA): E10 e F7 valgono solo se dalle
    # 00:00 UTC alla candela corrente non manca nessuna candela del giorno.
    # Manca la 03:00 del giorno 0 (quella con il massimo asiatico 101): il range "visto" sarebbe
    # 100.2 e la 08:00 (100.8) sembrerebbe una rottura. Il modulo non da' segnali quel giorno.
    s = _giorni_e10(togli=[3])
    su, _ = c3.range_asiatico(s.ts, s.high, s.low, s.durata)
    assert su[7] == 100.2  # 08:00 del giorno 0 (indice 7 nella serie accorciata)
    lo = ingresso(var({"codice": "E10"}), s)
    assert not lo[:23].any()
    stessi_booleani(lo, solo(len(s), 23 + 15), "E10 long, giorno 0 incompleto")
    # Manca la 10:00 del giorno 1: dalla 11:00 in poi il giorno non e' completo -> niente short alla 12:00
    # e niente long alla 15:00; il giorno 0 resta com'era
    s1 = _giorni_e10(togli=[24 + 10])
    stessi_booleani(ingresso(var({"codice": "E10"}), s1), solo(len(s1), 9), "E10 long, buco alle 10:00")
    assert not ingresso(var({"codice": "E10"}, direzione="short"), s1).any()
    # F7: falso dalla candela dopo il buco fino alla fine del giorno; il giorno dopo torna normale
    f7 = compila(var({"codice": "E3", "n": 20}, filtro={"codice": "F7", "lato": "sotto"}), s1).dettagli["filtro"]
    vw = c3.vwap_giornaliero(s1.ts, s1.high, s1.low, s1.close, s1.volume)
    grezzo = s1.close < vw
    assert grezzo[24 + 10:47].any() and not f7[24 + 10:47].any()
    stessi_booleani(f7[:24 + 10], grezzo[:24 + 10], "F7 prima del buco")
    stessi_booleani(f7[47:], grezzo[47:], "F7 il giorno dopo")


def test_vwap_range_e_giorno_completo_con_buchi_e_inizio_a_meta_giornata():
    # la serie inizia alle 05:00 e ha due buchi; VWAP e range si calcolano sulle candele presenti
    s = passeggiata(n=400, t0=LUN + 5 * ORA, togli=[30, 31, 32, 150])
    stessi_valori(c3.vwap_giornaliero(s.ts, s.high, s.low, s.close, s.volume),
                  rif.vwap_giornaliero(s.ts, s.high, s.low, s.close, s.volume), cosa="VWAP con buchi")
    su, giu = c3.range_asiatico(s.ts, s.high, s.low, s.durata)
    rs, rg = rif.range_asiatico(s.ts, s.high, s.low)
    stessi_valori(su, rs, cosa="range asiatico con buchi")
    stessi_valori(giu, rg, cosa="range asiatico con buchi")
    gc = c3.giorno_completo(s.ts, s.durata)
    # giorno 0 (dalle 05:00, indici 0-18): mai completo; giorno 1: completo fino alle 10:00 (indice 29),
    # poi mancano le 11:00-13:00 (candele 30-32 originali): dalla 14:00 (indice 30) non piu'
    assert not gc[:19].any()
    assert gc[19:30].all() and s.ts[29] == LUN + GIORNO + 10 * ORA
    assert not gc[30:19 + 21].any() and s.ts[30] == LUN + GIORNO + 14 * ORA
    atteso = []
    for t in s.ts:
        g = (t // GIORNO) * GIORNO
        presenti = [x for x in s.ts if g <= x <= t]
        atteso.append(len(presenti) == (t - g) // ORA + 1)
    stessi_booleani(gc, np.array(atteso), "giorno completo")


def test_E10_15m_la_candela_0745_fa_parte_del_range():
    # 15m: la candela 07:45 (indice 31) ha il massimo 102; alle 08:00 chiude 101.5 (sotto 102:
    # niente), alle 08:15 chiude 102.5: segnale. Giorno 2: prima rottura alla 15:45 (segnale), poi 16:00.
    n = 192
    o = np.full(n, 100.0)
    c = np.full(n, 100.0)
    c[32], c[33], c[34] = 101.5, 102.5, 103.0
    c[96 + 63], c[96 + 64] = 101.0, 101.5
    h = np.maximum(o, c) + 0.1
    l = np.minimum(o, c) - 0.1
    h[31] = 102.0
    h[96 + 5] = 100.8
    s = serie_da("15m", o, h, l, c)
    stessi_booleani(ingresso(var({"codice": "E10"}, tf="15m"), s), solo(n, 33, 96 + 63), "E10 long 15m")


def _serie_funding(togli=()):
    """52 candele 1h dalle 20:00 di domenica 3 gennaio 2021; regolamenti alle 00, 08, 16."""
    t0 = LUN - 4 * ORA
    fts = [LUN - 8 * ORA, LUN, LUN + 8 * ORA, LUN + 16 * ORA, LUN + 24 * ORA, LUN + 32 * ORA, LUN + 40 * ORA]
    ft = [0.0001, 0.0004, 0.0001, -0.0002, 0.0003, 0.0006, 0.0]
    n = 52
    c = 100.0 + np.arange(n) * 0.0
    ts = t0 + ORA * np.arange(n)
    tieni = np.setdiff1d(np.arange(n), np.asarray(togli, dtype=np.int64))
    o = c[tieni]
    return serie_da("1h", o, o + 0.5, o - 0.5, o, ts=ts[tieni], funding_ts=fts, funding_tasso=ft)


@pytest.mark.parametrize("direzione", ["long", "short"])
def test_E11_funding_oltre_soglia(direzione):
    # candele "prime dopo un regolamento": 4 (00:00, 0.0004), 12 (08:00, 0.0001), 20 (16:00, -0.0002),
    # 28 (00:00, 0.0003 = soglia: non sopra), 36 (08:00, 0.0006), 44 (16:00, 0.0 = soglia: non sotto)
    s = _serie_funding()
    n = len(s)
    attesi = {0.0003: solo(n, 4, 36), 0.0005: solo(n, 36), 0.0: solo(n, 20), -0.0001: solo(n, 20)}
    for soglia, atteso in attesi.items():
        stessi_booleani(ingresso(var({"codice": "E11", "soglia": soglia}, direzione=direzione), s), atteso,
                        f"E11 soglia {soglia} {direzione}")


def test_E11_dopo_un_buco_vale_la_prima_candela_che_inizia_dopo():
    # manca la candela delle 08:00 del giorno 0 (indice 12): la prima che inizia dopo il regolamento
    # delle 08:00 e' quella delle 09:00 (indice 12 nella serie accorciata); il suo funding e' 0.0001
    s = _serie_funding(togli=[12])
    prima = c3.prima_candela_dopo_regolamento(s.ts, s.funding_ts)
    assert prima[12] and s.ts[12] == LUN + 9 * ORA
    assert prima.sum() == 6
    # 4h: le candele che aprono alle 00, 08, 16 sono le prime dopo un regolamento; le 04, 12, 20 no
    ts4 = LUN - 4 * ORA + 4 * ORA * np.arange(13)
    p4 = c3.prima_candela_dopo_regolamento(ts4, [LUN - 8 * ORA + 8 * ORA * i for i in range(8)])
    stessi_booleani(p4[1:], np.array([i % 2 == 1 for i in range(1, 13)]), "prima candela dopo, 4h")


def test_E12_volume_anomalo():
    # 20 candele con volume 100; candela 20: 150 (relativo 1.5 = soglia: non sopra), verde;
    # 21: 205 (205 / 102.5 = 2.0), verde; 22: 300 (300 / 107.75 = 2.78), rossa; 23: 300, chiusura = apertura
    n = 24
    v = np.full(n, 100.0)
    v[20:24] = [150.0, 205.0, 300.0, 300.0]
    o = np.full(n, 100.0)
    c = np.full(n, 100.0)
    c[20], c[21], c[22] = 101.0, 101.0, 99.0
    s = serie_da("1h", o, np.maximum(o, c) + 0.5, np.minimum(o, c) - 0.5, c, v)
    rv = c3.volume_relativo(s.volume, 20)
    assert rv[20] == 1.5 and rv[21] == 2.0
    stessi_booleani(ingresso(var({"codice": "E12", "soglia": 1.5}), s), solo(n, 21), "E12 1.5 long")
    stessi_booleani(ingresso(var({"codice": "E12", "soglia": 2.0}), s), solo(n, ), "E12 2.0 long")
    stessi_booleani(ingresso(var({"codice": "E12", "soglia": 1.5}, direzione="short"), s), solo(n, 22),
                    "E12 1.5 short")
    stessi_booleani(ingresso(var({"codice": "E12", "soglia": 2.0}, direzione="short"), s), solo(n, 22),
                    "E12 2.0 short")
    # C1 (7.5): solo il volume relativo, senza direzione
    for d in ("long", "short"):
        c1 = compila(var({"codice": "E10"}, conferma={"codice": "C1", "soglia": 1.5}, direzione=d), s)
        stessi_booleani(c1.dettagli["conferma"], solo(n, 21, 22, 23), "C1 1.5")
        c2 = compila(var({"codice": "E10"}, conferma={"codice": "C1", "soglia": 2.0}, direzione=d), s)
        stessi_booleani(c2.dettagli["conferma"], solo(n, 22, 23), "C1 2.0")


# ---------------------------------------------------------------------------
# 7.4 - filtri, 7.5 - conferme (serie costruite apposta)
# ---------------------------------------------------------------------------


def filtro(f, s, direzione="long"):
    return compila(var({"codice": "E3", "n": 20}, filtro=f, direzione=direzione, tf=s.timeframe), s).dettagli["filtro"]


@pytest.mark.parametrize("direzione", ["long", "short"])
def test_F1_chiusura_e_ema(direzione):
    # salita lineare: la EMA(50) (definita dalla 49, = 124.5) resta sotto la chiusura
    s = da_chiusure("1h", [100.0 + i for i in range(60)])
    stessi_booleani(filtro({"codice": "F1", "n": 50, "lato": "sopra"}, s, direzione), np.arange(60) >= 49, "F1 sopra")
    assert not filtro({"codice": "F1", "n": 50, "lato": "sotto"}, s, direzione).any()
    s2 = da_chiusure("1h", [200.0 - i for i in range(60)])
    stessi_booleani(filtro({"codice": "F1", "n": 50, "lato": "sotto"}, s2, direzione), np.arange(60) >= 49, "F1 sotto")


def test_F2_adx():
    # tendenza costante: +DM = 1, -DM = 0 a ogni candela -> DX = 100 -> ADX 100 (definito dalla 27)
    s = da_chiusure("1h", [100.0 + i for i in range(60)])
    a = c3.adx(s.high, s.low, s.close)
    assert np.all(np.isnan(a[:27])) and np.allclose(a[27:], 100.0)
    stessi_booleani(filtro({"codice": "F2", "regime": "tendenza"}, s), np.arange(60) >= 27, "F2 tendenza")
    assert not filtro({"codice": "F2", "regime": "laterale"}, s).any()
    # su e giu alternati della stessa ampiezza: +DM e -DM si equilibrano, ADX basso
    ca = np.array([100.0 + (i % 2) for i in range(80)])
    alt = serie_da("1h", ca, ca + 0.5, ca - 0.5, ca)
    a2 = c3.adx(alt.high, alt.low, alt.close)
    assert np.all(a2[27:] < 20)
    stessi_booleani(filtro({"codice": "F2", "regime": "laterale"}, alt), np.arange(80) >= 27, "F2 laterale")
    assert not filtro({"codice": "F2", "regime": "tendenza"}, alt).any()


def test_F3_atr_percentile():
    # escursione costante (TR = 1, ATR/chiusura = 0.01 sempre uguale): 0% di valori minori ->
    # sotto il 30esimo dalla 514; alla 540 una candela da 20 punti: ATR sopra tutti i precedenti
    # -> 100% (sopra il 70esimo) e resta sopra fino alla fine (i valori dopo la 540 restano > 0.01)
    n = 560
    o = np.full(n, 100.0)
    h = np.full(n, 100.5)
    l = np.full(n, 99.5)
    h[540], l[540] = 110.0, 90.0
    s = serie_da("1h", o, h, l, o.copy())
    i = np.arange(n)
    stessi_booleani(filtro({"codice": "F3", "regime": "bassa"}, s), (i >= 514) & (i < 540), "F3 bassa")
    stessi_booleani(filtro({"codice": "F3", "regime": "alta"}, s), i >= 540, "F3 alta")


def test_F4_funding():
    # funding alla chiusura: 0-3: 0.0001; 4-11: 0.0004; 12-19: 0.0001; 20-27: -0.0002;
    # 28-35: 0.0003 (= soglia, non sopra); 36-43: 0.0006; 44-51: 0.0 (= soglia, non sotto)
    s = _serie_funding()
    i = np.arange(len(s))
    for d in ("long", "short"):
        stessi_booleani(filtro({"codice": "F4", "lato": "sopra"}, s, d), ((i >= 4) & (i < 12)) | ((i >= 36) & (i < 44)),
                        "F4 sopra")
        stessi_booleani(filtro({"codice": "F4", "lato": "sotto"}, s, d), (i >= 20) & (i < 28), "F4 sotto")


@pytest.mark.parametrize("sessione,inizio,fine", [("asia", 0, 8), ("europa", 7, 16), ("usa", 13, 21)])
def test_F5_sessioni_per_ora_di_apertura(sessione, inizio, fine):
    # 15m su un giorno intero: la candela e' nella sessione se APRE in [inizio, fine)
    s = da_chiusure("15m", np.full(96, 100.0))
    minuti = 15 * np.arange(96)
    atteso = (minuti >= inizio * 60) & (minuti < fine * 60)
    for d in ("long", "short"):
        stessi_booleani(filtro({"codice": "F5", "sessione": sessione}, s, d), atteso, f"F5 {sessione}")
    # 1h: la candela delle 07:00 e' in Asia (07:00-08:00) e in Europa
    s1 = da_chiusure("1h", np.full(24, 100.0))
    f1 = filtro({"codice": "F5", "sessione": sessione}, s1)
    stessi_booleani(f1, (np.arange(24) >= inizio) & (np.arange(24) < fine), f"F5 {sessione} 1h")


def test_F6_giorni_feriali_e_fine_settimana():
    # 1h dalle 22:00 di venerdi' 8 gennaio 2021 all'01:00 di lunedi' 11 gennaio 2021
    t0 = VEN + 22 * ORA
    n = 2 + 48 + 2
    s = da_chiusure("1h", np.full(n, 100.0), t0=t0)
    weekend = np.zeros(n, dtype=bool)
    weekend[2:50] = True  # sabato 00:00 -> domenica 23:00
    for d in ("long", "short"):
        stessi_booleani(filtro({"codice": "F6", "giorni": "fine_settimana"}, s, d), weekend, "F6 fine settimana")
        stessi_booleani(filtro({"codice": "F6", "giorni": "feriali"}, s, d), ~weekend, "F6 feriali")
    # una data nota: lunedi' 1 gennaio 2024 e' feriale; sabato 17 ottobre 2026 e' fine settimana
    s2 = da_chiusure("1d", np.full(1, 100.0), t0=LUN_2024)
    assert filtro({"codice": "F6", "giorni": "feriali"}, s2)[0]
    s3 = da_chiusure("1d", np.full(1, 100.0), t0=1_792_195_200_000)
    assert filtro({"codice": "F6", "giorni": "fine_settimana"}, s3)[0]


def test_C2_e_C3():
    o = np.array([100.0, 100.0, 101.0, 100.0])
    c = np.array([100.0, 101.0, 100.0, 100.0])  # 0: doji, 1: verde, 2: rossa, 3: doji
    s = serie_da("1h", o, np.maximum(o, c) + 0.5, np.minimum(o, c) - 0.5, c)
    lo = compila(var({"codice": "E10"}, conferma={"codice": "C2"}), s).dettagli["conferma"]
    sh = compila(var({"codice": "E10"}, conferma={"codice": "C2"}, direzione="short"), s).dettagli["conferma"]
    stessi_booleani(lo, solo(4, 1), "C2 long")
    stessi_booleani(sh, solo(4, 2), "C2 short")
    # C3: in salita RSI(14) = 100 dalla candela 14 (sopra 50); piatto: 50 (ne' sopra ne' sotto)
    sal = da_chiusure("1h", [100.0 + i for i in range(30)])
    stessi_booleani(compila(var({"codice": "E10"}, conferma={"codice": "C3"}), sal).dettagli["conferma"],
                    np.arange(30) >= 14, "C3 long")
    assert not compila(var({"codice": "E10"}, conferma={"codice": "C3"}, direzione="short"), sal).dettagli["conferma"].any()
    piatto = da_chiusure("1h", np.full(30, 128.0))
    for d in ("long", "short"):
        assert not compila(var({"codice": "E10"}, conferma={"codice": "C3"}, direzione=d), piatto).dettagli["conferma"].any()


def test_U2s_fine_giornata():
    s = da_chiusure("15m", np.full(100, 100.0))  # 00:00 del giorno 0 -> 00:45 del giorno 1
    cp = compila(var({"codice": "E10"}, tf="15m", uscite=[{"codice": "U2s"}]), s)
    minuti = (15 * np.arange(100)) % (24 * 60)
    stessi_booleani(cp.fine_giornata, minuti >= 21 * 60, "fine giornata 15m")
    assert not cp.fine_giornata[83] and cp.fine_giornata[84] and cp.fine_giornata[95] and not cp.fine_giornata[96]
    s1 = da_chiusure("1h", np.full(26, 100.0))
    f1 = compila(var({"codice": "E10"}, uscite=[{"codice": "U2s"}]), s1).fine_giornata
    stessi_booleani(f1, (np.arange(26) % 24) >= 21, "fine giornata 1h")


# ---------------------------------------------------------------------------
# 7.3-7.5 sulla passeggiata casuale, contro il riferimento (tutti i codici, long e short)
# ---------------------------------------------------------------------------

INGRESSI = (
    [{"codice": "E1", "media": m, "veloce": a, "lenta": b} for m, a, b in c3.COPPIE_E1]
    + [{"codice": "E2", "media": m, "n": n} for m in ("EMA", "SMA") for n in (20, 50, 100, 200)]
    + [{"codice": "E3", "n": n} for n in (20, 55)]
    + [{"codice": c, "k": k} for c in ("E4", "E5") for k in (2.0, 2.5)]
    + [{"codice": "E6", "n": n, "soglie": s} for n in (7, 14, 21) for s in ([30, 70], [20, 80])]
    + [{"codice": "E7", "n": n} for n in (7, 14, 21)]
    + [{"codice": "E8"}, {"codice": "E9"}, {"codice": "E10"}]
    + [{"codice": "E11", "soglia": x} for x in (0.0003, 0.0005, 0.0, -0.0001)]
    + [{"codice": "E12", "soglia": x} for x in (1.5, 2.0)]
)
FILTRI = (
    [{"codice": "F1", "n": n, "lato": la} for n in (50, 100, 200) for la in ("sopra", "sotto")]
    + [{"codice": "F2", "regime": r} for r in ("tendenza", "laterale")]
    + [{"codice": "F3", "regime": r} for r in ("alta", "bassa")]
    + [{"codice": "F4", "lato": la} for la in ("sopra", "sotto")]
    + [{"codice": "F5", "sessione": x} for x in ("asia", "europa", "usa")]
    + [{"codice": "F6", "giorni": x} for x in ("feriali", "fine_settimana")]
    + [{"codice": "F7", "lato": la} for la in ("sopra", "sotto")]
)
CONFERME = [{"codice": "C1", "soglia": 1.5}, {"codice": "C1", "soglia": 2.0}, {"codice": "C2"}, {"codice": "C3"}]


def _nome(d):
    return "-".join(str(x) for x in d.values()) if d else "nessuno"


@pytest.mark.parametrize("e", INGRESSI, ids=_nome)
@pytest.mark.parametrize("direzione", ["long", "short"])
def test_ingressi_come_riferimento(rw, e, direzione):
    v = var(e, direzione=direzione)
    cp = compila(v, rw)
    long = direzione == "long"
    atteso = rif.condizione_ingresso(cp.variante["ingresso"], long, rw)
    stessi_booleani(cp.dettagli["ingresso"], atteso, f"{_nome(e)} {direzione}")
    opposto = rif.condizione_ingresso(cp.variante["ingresso"], not long, rw)
    w = rif.riscaldamento(cp.variante)
    stessi_booleani(cp.opposto, opposto & rif.ammessa(rw.ts, rw.durata, w), "opposto (U4)")
    assert atteso.sum() >= 1, "il caso di prova non produce nessun segnale: confronto vuoto"


@pytest.mark.parametrize("quale", ["rw", "rw15"])
@pytest.mark.parametrize("f", FILTRI, ids=_nome)
def test_filtri_come_riferimento(quale, f, request):
    s = request.getfixturevalue(quale)
    atteso = rif.condizione_filtro(f, s)
    for d in ("long", "short"):
        cp = compila(var({"codice": "E3", "n": 20}, filtro=f, direzione=d, tf=s.timeframe), s)
        stessi_booleani(cp.dettagli["filtro"], atteso, f"{_nome(f)} {d} {s.timeframe}")
    assert 0 < atteso.sum() < len(s) or f["codice"] == "F3"


@pytest.mark.parametrize("cf", CONFERME, ids=_nome)
@pytest.mark.parametrize("direzione", ["long", "short"])
def test_conferme_come_riferimento(rw, cf, direzione):
    cp = compila(var({"codice": "E3", "n": 20}, conferma=cf, direzione=direzione), rw)
    stessi_booleani(cp.dettagli["conferma"], rif.condizione_conferma(cf, direzione == "long", rw), _nome(cf))


@pytest.mark.parametrize("combo", [
    ({"codice": "F1", "n": 200, "lato": "sopra"}, {"codice": "E6", "n": 14, "soglie": [30, 70]}, None),
    ({"codice": "F3", "regime": "alta"}, {"codice": "E3", "n": 20}, {"codice": "C1", "soglia": 1.5}),
    ({"codice": "F7", "lato": "sotto"}, {"codice": "E10"}, {"codice": "C2"}),
    ({"codice": "F2", "regime": "tendenza"}, {"codice": "E12", "soglia": 1.5}, {"codice": "C3"}),
    ({"codice": "F4", "lato": "sopra"}, {"codice": "E11", "soglia": 0.0003}, None),
    (None, {"codice": "E9"}, {"codice": "C1", "soglia": 2.0}),
], ids=lambda c: "+".join(_nome(x) for x in c))
@pytest.mark.parametrize("direzione", ["long", "short"])
def test_segnale_e_filtro_ingresso_conferma_e_riscaldamento(rw, combo, direzione):
    f, e, cf = combo
    cp = compila(var(e, filtro=f, conferma=cf, direzione=direzione), rw)
    long = direzione == "long"
    w = rif.riscaldamento(cp.variante)
    atteso = (rif.condizione_ingresso(cp.variante["ingresso"], long, rw) & rif.condizione_filtro(f, rw)
              & rif.condizione_conferma(cf, long, rw) & rif.ammessa(rw.ts, rw.durata, w))
    assert cp.riscaldamento == w
    stessi_booleani(cp.segnale, atteso, "segnale")


# ---------------------------------------------------------------------------
# normalizza (7.1-7.7)
# ---------------------------------------------------------------------------

TIPI = [{"codice": "M"}] + [{"codice": "L", "k": k, "validita": n} for k in (0.25, 0.5) for n in (1, 3)]
STOP = ([{"codice": "S1", "k": k} for k in (1.0, 1.5, 2.0, 3.0)] + [{"codice": "S2", "n": n} for n in (5, 10, 20)]
        + [{"codice": "S3", "pct": p} for p in (0.01, 0.02, 0.03)])
USCITE = ([{"codice": "U1", "k": k} for k in (1.5, 2.0, 3.0)] + [{"codice": "U2", "n": n} for n in (6, 12, 24, 48)]
          + [{"codice": "U2s"}] + [{"codice": "U3", "k": k} for k in (2.0, 3.0)] + [{"codice": "U4"}])


def base(**kw):
    v = var({"codice": "E3", "n": 20})
    v.update(kw)
    return v


def test_normalizza_accetta_tutto_il_catalogo():
    for tf in c3.TIMEFRAME:
        normalizza(base(timeframe=tf))
    for d in ("long", "short"):
        normalizza(base(direzione=d))
    for e in INGRESSI:
        normalizza(base(ingresso=e))
    for f in FILTRI + [None]:
        normalizza(base(filtro=f))
    for cf in CONFERME + [None]:
        normalizza(base(conferma=cf))
    for t in TIPI:
        normalizza(base(tipo_ingresso=t))
    for s in STOP:
        normalizza(base(stop=s))
    for u in USCITE:
        normalizza(base(uscite=[u]))
    fam = c3.FAMIGLIA_USCITA
    for a, b in itertools.combinations(USCITE, 2):
        if fam[a["codice"]] != fam[b["codice"]]:
            normalizza(base(uscite=[a, b]))
    # le due varianti scritte per intero della 7.9
    normalizza({"timeframe": "1h", "direzione": "long", "filtro": {"codice": "F1", "n": 200, "lato": "sopra"},
                "ingresso": {"codice": "E10"}, "conferma": {"codice": "C1", "soglia": 1.5},
                "tipo_ingresso": {"codice": "M"}, "stop": {"codice": "S2", "n": 5},
                "uscite": [{"codice": "U1", "k": 2}, {"codice": "U2s"}]})
    normalizza({"timeframe": "4h", "direzione": "long", "filtro": {"codice": "F1", "n": 200, "lato": "sopra"},
                "ingresso": {"codice": "E6", "n": 14, "soglie": [30, 70]}, "conferma": None,
                "tipo_ingresso": {"codice": "L", "k": 0.25, "validita": 3}, "stop": {"codice": "S1", "k": 1.5},
                "uscite": [{"codice": "U1", "k": 2}, {"codice": "U2", "n": 12}]})


def test_normalizza_scrive_i_parametri_fissi():
    n = normalizza(base(filtro={"codice": "F2", "regime": "tendenza"}))
    assert n["filtro"]["soglia"] == 25 and n["filtro"]["n"] == 14
    assert normalizza(base(filtro={"codice": "F2", "regime": "laterale"}))["filtro"]["soglia"] == 20
    assert normalizza(base(filtro={"codice": "F3", "regime": "alta"}))["filtro"]["soglia"] == 70
    f3 = normalizza(base(filtro={"codice": "F3", "regime": "bassa"}))["filtro"]
    assert f3["soglia"] == 30 and f3["finestra"] == 500 and f3["atr"] == 14
    assert normalizza(base(filtro={"codice": "F4", "lato": "sopra"}))["filtro"]["soglia"] == 0.0003
    assert normalizza(base(filtro={"codice": "F4", "lato": "sotto"}))["filtro"]["soglia"] == 0.0
    assert normalizza(base(ingresso={"codice": "E4", "k": 2.0}))["ingresso"]["n"] == 20
    e8 = normalizza(base(ingresso={"codice": "E8"}))["ingresso"]
    assert list(e8["parametri"]) == [14, 3, 3] and list(e8["soglie"]) == [20, 80]
    assert list(normalizza(base(ingresso={"codice": "E9"}))["ingresso"]["parametri"]) == [12, 26, 9]
    assert normalizza(base(ingresso={"codice": "E7", "n": 7}))["ingresso"]["meta"] == 50
    c3_ = normalizza(base(conferma={"codice": "C3"}))["conferma"]
    assert c3_["n"] == 14 and c3_["meta"] == 50
    for soglia, lato in ((0.0003, "sopra"), (0.0005, "sopra"), (0.0, "sotto"), (-0.0001, "sotto")):
        assert normalizza(base(ingresso={"codice": "E11", "soglia": soglia}))["ingresso"]["lato"] == lato
    # un parametro fisso scritto con il suo valore e' accettato
    normalizza(base(ingresso={"codice": "E9", "parametri": [12, 26, 9]}))
    normalizza(base(ingresso={"codice": "E4", "k": 2.5, "n": 20}))


FUORI_CATALOGO = [
    dict(timeframe="3h"), dict(timeframe="1w"), dict(direzione="entrambe"),
    dict(ingresso={"codice": "E1", "media": "EMA", "veloce": 9, "lenta": 50}),
    dict(ingresso={"codice": "E1", "media": "SMA", "veloce": 20, "lenta": 50}),
    dict(ingresso={"codice": "E1", "media": "EMA", "veloce": 20, "lenta": 9}),
    dict(ingresso={"codice": "E1", "media": "WMA", "veloce": 9, "lenta": 20}),
    dict(ingresso={"codice": "E2", "media": "EMA", "n": 9}),
    dict(ingresso={"codice": "E2", "media": "SMA", "n": 30}),
    dict(ingresso={"codice": "E3", "n": 50}),
    dict(ingresso={"codice": "E4", "k": 3.0}), dict(ingresso={"codice": "E5", "k": 1.5}),
    dict(ingresso={"codice": "E6", "n": 10, "soglie": [30, 70]}),
    dict(ingresso={"codice": "E6", "n": 14, "soglie": [25, 75]}),
    dict(ingresso={"codice": "E6", "n": 14, "soglie": [30, 80]}),
    dict(ingresso={"codice": "E7", "n": 9}),
    dict(ingresso={"codice": "E11", "soglia": 0.0004}), dict(ingresso={"codice": "E11", "soglia": 0.0001}),
    dict(ingresso={"codice": "E12", "soglia": 1.8}),
    dict(filtro={"codice": "F1", "n": 20, "lato": "sopra"}), dict(filtro={"codice": "F1", "n": 50, "lato": "su"}),
    dict(filtro={"codice": "F2", "regime": "forte"}), dict(filtro={"codice": "F3", "regime": "media"}),
    dict(filtro={"codice": "F5", "sessione": "londra"}), dict(filtro={"codice": "F6", "giorni": "lunedi"}),
    dict(conferma={"codice": "C1", "soglia": 3.0}),
    dict(tipo_ingresso={"codice": "L", "k": 0.3, "validita": 1}),
    dict(tipo_ingresso={"codice": "L", "k": 0.25, "validita": 2}),
    dict(stop={"codice": "S1", "k": 2.5}), dict(stop={"codice": "S2", "n": 15}),
    dict(stop={"codice": "S3", "pct": 0.015}), dict(stop={"codice": "S3", "pct": 1}),
    dict(uscite=[{"codice": "U1", "k": 2.5}]), dict(uscite=[{"codice": "U2", "n": 10}]),
    dict(uscite=[{"codice": "U3", "k": 1.0}]),
]
CODICI_SCONOSCIUTI = [
    dict(ingresso={"codice": "E13"}), dict(ingresso={"codice": "e1"}), dict(filtro={"codice": "F8"}),
    dict(conferma={"codice": "C4"}), dict(tipo_ingresso={"codice": "X"}), dict(stop={"codice": "S4", "k": 1}),
    dict(uscite=[{"codice": "U5"}]), dict(ingresso=None), dict(stop=None), dict(tipo_ingresso=None),
]
CHIAVI_IN_PIU = [
    dict(ingresso={"codice": "E3", "n": 20, "lato": "su"}), dict(filtro={"codice": "F6", "giorni": "feriali", "x": 1}),
    dict(conferma={"codice": "C2", "soglia": 1.5}), dict(tipo_ingresso={"codice": "M", "k": 0.25}),
    dict(stop={"codice": "S3", "pct": 0.01, "k": 1}), dict(uscite=[{"codice": "U4", "n": 6}]),
    dict(uscite=[{"codice": "U2s", "ora": 20}]), dict(ingresso={"codice": "E10", "ora": 9}),
]
USCITE_SBAGLIATE = [
    dict(uscite=[]), dict(uscite=None), dict(uscite={"codice": "U1", "k": 2}),
    dict(uscite=[{"codice": "U1", "k": 2}, {"codice": "U2", "n": 6}, {"codice": "U4"}]),
    dict(uscite=[{"codice": "U1", "k": 2}, {"codice": "U1", "k": 3}]),
    dict(uscite=[{"codice": "U2", "n": 6}, {"codice": "U2s"}]),
    dict(uscite=[{"codice": "U3", "k": 2}, {"codice": "U3", "k": 3}]),
    dict(uscite=[{"codice": "U4"}, {"codice": "U4"}]),
]


@pytest.mark.parametrize("modifica", FUORI_CATALOGO + CODICI_SCONOSCIUTI + CHIAVI_IN_PIU + USCITE_SBAGLIATE,
                         ids=lambda m: str(m)[:70])
def test_normalizza_rifiuta(modifica):
    with pytest.raises(VarianteNonValida):
        normalizza(base(**modifica))


def test_normalizza_rifiuta_chiavi_in_piu_nella_variante():
    v = base()
    v["leva"] = 3
    with pytest.raises(VarianteNonValida):
        normalizza(v)


@pytest.mark.parametrize("tf", ["2h", "4h", "6h", "8h", "12h", "1d"])
@pytest.mark.parametrize("modifica", [
    dict(ingresso={"codice": "E10"}), dict(filtro={"codice": "F5", "sessione": "asia"}),
    dict(filtro={"codice": "F7", "lato": "sopra"}), dict(uscite=[{"codice": "U2s"}]),
], ids=lambda m: str(m)[:40])
def test_elementi_solo_fino_a_1h(tf, modifica):
    with pytest.raises(VarianteNonValida):
        normalizza(base(timeframe=tf, **modifica))
    with pytest.raises(VarianteNonValida):
        normalizza(base(timeframe=tf, **modifica), solo_catalogo=False)
    for corto in ("15m", "30m", "1h"):
        normalizza(base(timeframe=corto, **modifica))


FISSI_SBAGLIATI = [
    (dict(ingresso={"codice": "E4", "k": 2.0, "n": 21}), ("ingresso", "n", 21)),
    (dict(ingresso={"codice": "E5", "k": 2.0, "n": 16}), ("ingresso", "n", 16)),
    (dict(ingresso={"codice": "E7", "n": 14, "meta": 55}), ("ingresso", "meta", 55)),
    (dict(ingresso={"codice": "E8", "parametri": [14, 3, 5]}), ("ingresso", "parametri", [14, 3, 5])),
    (dict(ingresso={"codice": "E8", "soglie": [25, 75]}), ("ingresso", "soglie", [25, 75])),
    (dict(ingresso={"codice": "E9", "parametri": [10, 26, 9]}), ("ingresso", "parametri", [10, 26, 9])),
    (dict(ingresso={"codice": "E12", "soglia": 1.5, "n": 30}), ("ingresso", "n", 30)),
    (dict(filtro={"codice": "F2", "regime": "tendenza", "n": 10}), ("filtro", "n", 10)),
    (dict(filtro={"codice": "F2", "regime": "tendenza", "soglia": 30}), ("filtro", "soglia", 30)),
    (dict(filtro={"codice": "F3", "regime": "alta", "finestra": 400}), ("filtro", "finestra", 400)),
    (dict(filtro={"codice": "F3", "regime": "alta", "atr": 10}), ("filtro", "atr", 10)),
    (dict(filtro={"codice": "F3", "regime": "bassa", "soglia": 20}), ("filtro", "soglia", 20)),
    (dict(filtro={"codice": "F4", "lato": "sopra", "soglia": 0.0005}), ("filtro", "soglia", 0.0005)),
    (dict(conferma={"codice": "C1", "soglia": 1.5, "n": 25}), ("conferma", "n", 25)),
    (dict(conferma={"codice": "C3", "n": 10}), ("conferma", "n", 10)),
    (dict(conferma={"codice": "C3", "meta": 55}), ("conferma", "meta", 55)),
    (dict(tipo_ingresso={"codice": "L", "k": 0.25, "validita": 1, "atr": 20}), ("tipo_ingresso", "atr", 20)),
    (dict(stop={"codice": "S1", "k": 1.0, "atr": 10}), ("stop", "atr", 10)),
]


@pytest.mark.parametrize("modifica,dove", FISSI_SBAGLIATI, ids=lambda m: str(m)[:60])
def test_parametri_fissi_solo_con_il_valore_fisso(modifica, dove):
    with pytest.raises(VarianteNonValida):
        normalizza(base(**modifica))
    out = normalizza(base(**modifica), solo_catalogo=False)
    parte, chiave, valore = dove
    letto = out[parte][chiave]
    if isinstance(valore, list):
        assert list(letto) == valore
    else:
        assert letto == valore


def test_uscita_trailing_con_atr_diverso_e_fuori_catalogo_solo_in_fase_4():
    m = dict(uscite=[{"codice": "U3", "k": 2.0, "atr": 10}])
    with pytest.raises(VarianteNonValida):
        normalizza(base(**m))
    assert normalizza(base(**m), solo_catalogo=False)["uscite"][0]["atr"] == 10
    # valori numerici fuori catalogo: ammessi solo con solo_catalogo=False
    for m in (dict(ingresso={"codice": "E2", "media": "SMA", "n": 30}), dict(stop={"codice": "S1", "k": 1.2}),
              dict(uscite=[{"codice": "U2", "n": 10}]), dict(tipo_ingresso={"codice": "L", "k": 0.3, "validita": 2})):
        with pytest.raises(VarianteNonValida):
            normalizza(base(**m))
        normalizza(base(**m), solo_catalogo=False)
    # ma la struttura resta: codici sconosciuti e chiavi in piu' sono rifiutati comunque
    for m in CODICI_SCONOSCIUTI + CHIAVI_IN_PIU + USCITE_SBAGLIATE:
        with pytest.raises(VarianteNonValida):
            normalizza(base(**m), solo_catalogo=False)


# ---------------------------------------------------------------------------
# 7.8 / 9.6 - riscaldamento e buchi nei dati
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("kw,atteso", [
    (dict(filtro={"codice": "F1", "n": 200, "lato": "sopra"}), 600),
    (dict(filtro={"codice": "F1", "n": 50, "lato": "sotto"}), 150),
    (dict(ingresso={"codice": "E9"}), 78),
    (dict(filtro={"codice": "F3", "regime": "alta"}), 3 * 14 + 500),
    (dict(filtro={"codice": "F2", "regime": "laterale"}), 42),
    (dict(ingresso={"codice": "E1", "media": "EMA", "veloce": 50, "lenta": 200}), 600),
    (dict(ingresso={"codice": "E1", "media": "EMA", "veloce": 9, "lenta": 20}), 60),
    (dict(ingresso={"codice": "E1", "media": "SMA", "veloce": 50, "lenta": 200}), 200),
    (dict(ingresso={"codice": "E2", "media": "SMA", "n": 100}), 100),
    (dict(ingresso={"codice": "E2", "media": "EMA", "n": 100}), 300),
    (dict(ingresso={"codice": "E3", "n": 55}), 55),
    (dict(ingresso={"codice": "E3", "n": 20}), 20),
    (dict(ingresso={"codice": "E4", "k": 2.0}), 20),
    (dict(ingresso={"codice": "E5", "k": 2.5}), 20),
    (dict(ingresso={"codice": "E6", "n": 21, "soglie": [20, 80]}), 63),
    (dict(ingresso={"codice": "E7", "n": 7}), 21),
    (dict(ingresso={"codice": "E7", "n": 7}, conferma={"codice": "C3"}), 42),
    (dict(ingresso={"codice": "E12", "soglia": 2.0}), 20),
    (dict(conferma={"codice": "C1", "soglia": 1.5}), 20),
    (dict(ingresso={"codice": "E8"}), 18),
    (dict(ingresso={"codice": "E10"}), 1),
    (dict(ingresso={"codice": "E11", "soglia": 0.0}), 1),
    (dict(filtro={"codice": "F1", "n": 200, "lato": "sopra"}, ingresso={"codice": "E10"},
          conferma={"codice": "C1", "soglia": 1.5}, stop={"codice": "S2", "n": 5},
          uscite=[{"codice": "U1", "k": 2}, {"codice": "U2s"}]), 600),  # V-012 della 7.9
    (dict(timeframe="4h", filtro={"codice": "F1", "n": 200, "lato": "sopra"},
          ingresso={"codice": "E6", "n": 14, "soglie": [30, 70]},
          tipo_ingresso={"codice": "L", "k": 0.25, "validita": 3}, stop={"codice": "S1", "k": 1.5},
          uscite=[{"codice": "U1", "k": 2}, {"codice": "U2", "n": 12}]), 600),  # V-021 della 7.9
    # 7.8: "indicatori ricorsivi DELLA VARIANTE": l'ATR(14) di stop S1, ingresso limit e trailing conta
    (dict(ingresso={"codice": "E10"}, stop={"codice": "S1", "k": 1.0}), 42),
    (dict(ingresso={"codice": "E10"}, tipo_ingresso={"codice": "L", "k": 0.5, "validita": 1}), 42),
    (dict(ingresso={"codice": "E10"}, uscite=[{"codice": "U3", "k": 2.0}]), 42),
    (dict(ingresso={"codice": "E3", "n": 20}, stop={"codice": "S1", "k": 2.0}), 42),
    # S2 non e' nominato in 7.8: SCELTA del modulo, minimo / massimo delle ultime n candele
    # (segnale compreso) definito dalla candela n - 1
    (dict(ingresso={"codice": "E10"}, stop={"codice": "S2", "n": 20}), 19),
], ids=lambda x: str(x)[:80] if isinstance(x, dict) else str(x))
def test_riscaldamento(kw, atteso):
    v = base(**kw)
    assert riscaldamento(normalizza(v)) == atteso
    assert rif.riscaldamento(normalizza(v)) == atteso  # il riferimento dice lo stesso


def _indicatori_usati(v: dict, s) -> list:
    """Gli array (del riferimento) che le condizioni della variante leggono, con un flag che dice
    se la condizione guarda anche la candela precedente (incroci, E5)."""
    out = []
    cl = s.close
    for parte in (v["filtro"], v["ingresso"], v["conferma"]):
        if not parte:
            continue
        c = parte["codice"]
        if c == "E1":
            m = rif.ema if parte["media"] == "EMA" else rif.sma
            out += [(m(cl, parte["veloce"]), True), (m(cl, parte["lenta"]), True)]
        elif c == "E2":
            out.append(((rif.ema if parte["media"] == "EMA" else rif.sma)(cl, parte["n"]), True))
        elif c == "E3":
            out += [(x, False) for x in rif.donchian(s.high, s.low, parte["n"])]
        elif c in ("E4", "E5"):
            out += [(x, c == "E5") for x in rif.bollinger(cl, 20, parte["k"])]
        elif c in ("E6", "E7"):
            out.append((rif.rsi(cl, parte["n"]), True))
        elif c == "E8":
            out += [(x, True) for x in rif.stocastico(s.high, s.low, cl)]
        elif c == "E9":
            out += [(x, True) for x in rif.macd(cl)]
        elif c in ("E12", "C1"):
            out.append((rif.volume_relativo(s.volume, 20), False))
        elif c == "C3":
            out.append((rif.rsi(cl, 14), False))
        elif c == "F1":
            out.append((rif.ema(cl, parte["n"]), False))
        elif c == "F2":
            out.append((rif.adx(s.high, s.low, cl), False))
        elif c == "F3":
            out.append((rif.atr_percentile(rif.atr(s.high, s.low, cl), cl, 500), False))
    if v["stop"]["codice"] == "S1":
        out.append((rif.atr(s.high, s.low, cl), False))
    return out


@pytest.mark.parametrize("e", INGRESSI, ids=_nome)
def test_dopo_il_riscaldamento_ogni_indicatore_e_definito(rw, e):
    for f in (None, {"codice": "F3", "regime": "alta"}, {"codice": "F2", "regime": "tendenza"}):
        v = normalizza(var(e, filtro=f, conferma={"codice": "C1", "soglia": 1.5}, stop={"codice": "S1", "k": 1.0}))
        w = riscaldamento(v)
        for arr, prec in _indicatori_usati(v, rw):
            primo = w - 1 if prec else w
            assert not np.isnan(arr[primo:]).any(), (f"{_nome(e)} con filtro {_nome(f)}: indicatore non definito "
                                                     f"dopo il riscaldamento w={w}")


def test_inizi_dei_tratti():
    s = passeggiata(n=300, togli=[100, 101, 102, 200])
    assert s.inizi_dei_tratti().tolist() == [0, 100, 197]
    assert passeggiata(n=50).inizi_dei_tratti().tolist() == [0]


def test_nessun_segnale_prima_del_riscaldamento_ne_dopo_un_buco():
    # 900 candele 1h; mancano le candele 400-404 (buco di 5 ore) e la 700 (una sola)
    s = passeggiata(n=900, togli=[400, 401, 402, 403, 404, 700])
    inizi = s.inizi_dei_tratti().tolist()
    assert inizi == [0, 400, 695]
    v = var({"codice": "E12", "soglia": 1.5}, filtro={"codice": "F1", "n": 50, "lato": "sopra"})
    cp = compila(v, s)
    w = cp.riscaldamento
    assert w == 150
    i = np.arange(len(s))
    atteso_ammessa = ((i >= 150) & (i < 400)) | ((i >= 550) & (i < 695)) | (i >= 845)
    stessi_booleani(cp.ammessa, atteso_ammessa, "ammessa")
    stessi_booleani(cp.ammessa, rif.ammessa(s.ts, s.durata, w), "ammessa (riferimento)")
    grezzo = cp.dettagli["ingresso"] & cp.dettagli["filtro"] & cp.dettagli["conferma"]
    # il caso e' significativo: condizioni vere dentro ogni zona di riscaldamento
    for a, b in ((0, 150), (400, 550), (695, 845)):
        assert grezzo[a:b].any(), f"nessuna condizione vera in [{a}, {b}): la prova non direbbe nulla"
    assert not cp.segnale[~atteso_ammessa].any()
    stessi_booleani(cp.segnale, grezzo & atteso_ammessa, "segnale = condizioni e riscaldamento")
    assert not cp.opposto[~atteso_ammessa].any()


def test_tratto_piu_corto_del_riscaldamento_non_da_segnali():
    s = passeggiata(n=900, togli=list(range(300, 310)) + list(range(400, 410)))
    v = var({"codice": "E3", "n": 20}, filtro={"codice": "F1", "n": 50, "lato": "sopra"})
    cp = compila(v, s)
    # tratto 300-389 (90 candele) < 150: mai ammesso
    assert s.inizi_dei_tratti().tolist() == [0, 300, 390]
    assert not cp.ammessa[300:390].any() and cp.ammessa[390 + 150:].all()


@pytest.mark.parametrize("combo", [
    ({"codice": "F7", "lato": "sopra"}, {"codice": "E10"}, None),
    ({"codice": "F4", "lato": "sotto"}, {"codice": "E11", "soglia": 0.0}, None),
    ({"codice": "F3", "regime": "bassa"}, {"codice": "E9"}, {"codice": "C3"}),
    ({"codice": "F5", "sessione": "europa"}, {"codice": "E8"}, {"codice": "C1", "soglia": 1.5}),
], ids=lambda c: "+".join(_nome(x) for x in c))
def test_troncamento_non_cambia_i_segnali(rw, combo):
    # 9.8: con i soli dati fino a t, segnali e condizioni fino a t sono gli stessi
    f, e, cf = combo
    for d in ("long", "short"):
        v = var(e, filtro=f, conferma=cf, direzione=d)
        intero = compila(v, rw)
        for t in (560, 641, 777, 899):
            parte = compila(v, rw.fino_a(t))
            for chiave in ("ingresso", "filtro", "conferma"):
                stessi_booleani(parte.dettagli[chiave], intero.dettagli[chiave][:t + 1], f"troncamento {chiave} {t}")
            stessi_booleani(parte.segnale, intero.segnale[:t + 1], f"troncamento segnale {t}")
