"""Test degli attrezzi del collaudo del protocollo 3 (``research/collaudo_3/collaudo.py``): le serie senza
direzione (13bis.1, correzione 2) e il vantaggio inserito (13bis.3), su candele sintetiche."""
from __future__ import annotations

import numpy as np
import pytest

from research.collaudo_3 import collaudo as co
from research.src import catalogo3 as cat


def _serie(n=3000, seme=5):
    r = np.random.default_rng(seme)
    ts = np.arange(n, dtype=np.int64) * 3_600_000 + 1_577_836_800_000
    c = 30000 * np.exp(np.cumsum(r.normal(0.0002, 0.006, n)))
    o = np.concatenate([[c[0]], c[:-1]]) * np.exp(r.normal(0, 0.0005, n))
    h = np.maximum(o, c) * np.exp(np.abs(r.normal(0, 0.003, n)))
    l = np.minimum(o, c) * np.exp(-np.abs(r.normal(0, 0.003, n)))
    v = r.uniform(1, 10, n)
    return cat.Serie("1h", ts, o, h, l, c, v, o * 1.0002, h * 1.0003, l * 0.9998, c * 1.0001, ts[::8],
                     np.full(len(ts[::8]), 0.0001))


def test_senza_direzione_tiene_grandezze_ordine_e_coerenza():
    s = _serie()
    g = co.senza_direzione(s, 3)
    assert np.array_equal(g.ts, s.ts) and np.array_equal(g.volume, s.volume)
    assert np.array_equal(g.funding_ts, s.funding_ts) and np.array_equal(g.funding_tasso, s.funding_tasso)
    # le grandezze dei movimenti restano, candela per candela, nello stesso ordine
    for a, b in ((np.log(g.close[1:] / g.open[1:]), np.log(s.close[1:] / s.open[1:])),
                 (np.log(g.open[1:] / g.close[:-1]), np.log(s.open[1:] / s.close[:-1])),
                 (np.log(g.high[1:] / g.low[1:]), np.log(s.high[1:] / s.low[1:]))):
        assert np.allclose(np.abs(a), np.abs(b), atol=1e-12)
    # candele valide: il massimo sopra apertura e chiusura, il minimo sotto
    assert np.all(g.high >= np.maximum(g.open, g.close) * (1 - 1e-12))
    assert np.all(g.low <= np.minimum(g.open, g.close) * (1 + 1e-12))
    # il mark resta coerente con il last della sua candela (stesse quote, girate insieme)
    q_s = np.log(s.mark_high[1:] / s.mark_low[1:])
    q_g = np.log(g.mark_high[1:] / g.mark_low[1:])
    assert np.allclose(q_s, q_g, atol=1e-12)
    # circa meta' delle candele girate, e la direzione della chiusura non e' quella vera
    girate = np.sign(np.log(g.close[1:] / g.open[1:])) != np.sign(np.log(s.close[1:] / s.open[1:]))
    assert 0.45 < girate.mean() < 0.55
    # stesso seme, stessa serie; seme diverso, serie diversa
    assert np.array_equal(co.senza_direzione(s, 3).close, g.close)
    assert not np.array_equal(co.senza_direzione(s, 4).close, g.close)


def test_senza_direzione_toglie_la_tendenza():
    s = _serie(n=20000, seme=8)
    g = co.senza_direzione(s, 1)
    # la serie vera ha una tendenza (+0,0002 per candela); quella senza direzione no
    assert np.log(s.close[-1] / s.close[0]) > 2.0
    assert abs(np.log(g.close[-1] / g.close[0])) < 1.5


@pytest.mark.parametrize("nome", ["B1", "B2", "B3"])
def test_vantaggio_inserito_sui_segnali_veri(nome):
    s = co.senza_direzione(_serie(), 2)
    for p in co.AMPIEZZE_B:
        ns, piantati = co.pianta_vantaggio(s, co.REGOLE_B[nome], p)
        c = cat.compila(co.REGOLE_B[nome], ns)
        assert [int(i) for i in np.flatnonzero(c.segnale)] == piantati
    assert co.AMPIEZZE_B == (0.0, 0.6, 1.2) and co.AMPIEZZA_RISERVA_B == 1.8
