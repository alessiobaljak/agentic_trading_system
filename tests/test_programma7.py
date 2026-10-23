"""Programma 7 (trading ogni giorno): i pezzi della prima prova."""
from __future__ import annotations

import numpy as np
import pandas as pd

from research.programma7 import prima as pr


def test_lunedi_e_universo_del_giorno():
    from research.programma6 import seconda as sc
    lun = sc.giorno(2026, 10, 19)
    giorni = np.arange(lun - 1, lun + 8)
    assert list(pr.lunedi_del_giorno(giorni)) == [lun - 7] + [lun] * 7 + [lun + 7]
    U = np.array([[True, False], [False, True], [True, True]])
    Ud = pr.universo_del_giorno(np.array([lun - 3, lun + 2, lun + 7]), np.array([lun - 7, lun, lun + 7]), U)
    assert (Ud == U).all()


def test_movimenti():
    W = np.array([[0.5, 0.0, -0.5], [0.5, 0.3, 0.0], [0.0, 0.3, 0.0], [0.0, 0.3, -0.2]])
    m = pr.movimenti(W)
    # entrate: 2 il primo giorno, poi la seconda moneta (giorno 2) e la terza di nuovo (giorno 4)
    assert (m["entrate"], m["uscite"]) == (4, 2)
    assert m["durata_media_giorni"] == (W != 0).sum() / 4
    assert m["giorni_con_operazioni"] == 3


def test_per_settimana_somma_i_giorni():
    from research.programma6 import seconda as sc
    lun = sc.giorno(2026, 10, 19)
    giorni = np.arange(lun, lun + 14)
    df = pd.DataFrame({c: np.ones(14) for c in pr.COLONNE} | {"monete": np.arange(14)})
    s = pr.per_settimana(df, giorni)
    assert list(s.index) == [lun, lun + 7] and (s["netto"] == 7).all() and list(s["monete"]) == [6, 13]


def _candele(chiusure, alti=None, bassi=None):
    c = np.array(chiusure, float)
    o = np.concatenate([[c[0]], c[:-1]])
    h = np.maximum(o, c) if alti is None else np.array(alti, float)
    l = np.minimum(o, c) if bassi is None else np.array(bassi, float)
    return o, h, l, c


def test_g2_operazione():
    from research.programma6.motore import MAKER
    from research.programma7 import seconda as g2
    # apertura 100; la candela delle 02:00 chiude a 99 sotto l'apertura -> short alle 03:00 a 99; stop al massimo fino a li'
    # (101), obiettivo 99 - 2*2 = 95, toccato alle 05:00
    c = [100, 101, 99, 99, 97, 94] + [94] * 19
    o, h, l, cc = _candele(c)
    o[0] = 100.0
    r = g2.operazione(o, h, l, cc, 0.0007, 0.0003)
    assert r["entrata"] == 99 and r["stop"] == 101 and r["motivo"] == "obiettivo"
    assert r["R_lordo"] == (99 - 95) / 2 and abs(r["costo_R"] - (0.0007 * 99 + MAKER * 95) / 2) < 1e-12
    assert r["funding_R"] == 0.0                                 # uscita alle 05:00, prima del regolamento delle 08:00
    # mai sotto l'apertura: nessuna operazione
    o, h, l, cc = _candele([100] + [101] * 24)
    assert g2.operazione(o, h, l, cc, 0.0007, 0.0) is None
    # entrata e poi il prezzo risale oltre lo stop: stop
    c = [100, 99.5, 99.5, 102] + [102] * 21
    o, h, l, cc = _candele(c)
    r = g2.operazione(o, h, l, cc, 0.0007, 0.0)
    assert r["motivo"] == "stop" and r["R_lordo"] < -1.0 + 1e-9
    # niente stop ne' obiettivo: uscita alle 00:00, attraversa i regolamenti delle 08:00 e delle 16:00
    c = [100, 99.8] + [99.7] * 23
    o, h, l, cc = _candele(c)
    r = g2.operazione(o, h, l, cc, 0.0007, 0.0003)
    assert r["motivo"] == "tempo" and r["uscita_ora"] == 24 and abs(r["funding_R"] - 2 * 0.0001 * r["entrata"] / (r["stop"] - r["entrata"])) < 1e-12


def test_g3_operazione_specchio():
    from research.programma7 import seconda as g2
    # lo specchio del primo caso di G2: prezzi riflessi intorno a 100
    c = [100, 99, 101, 101, 103, 106] + [106] * 19
    o, h, l, cc = _candele(c)
    r = g2.operazione(o, h, l, cc, 0.0007, 0.0003, verso=1)
    assert r["entrata"] == 101 and r["stop"] == 99 and r["motivo"] == "obiettivo"
    assert r["R_lordo"] == (105 - 101) / 2
    c = [100, 100.2] + [100.3] * 23
    o, h, l, cc = _candele(c)
    r = g2.operazione(o, h, l, cc, 0.0007, 0.0003, verso=1)
    assert r["motivo"] == "tempo" and r["funding_R"] < 0           # il long paga il funding positivo


def test_tetto_per_moneta():
    from research.programma7 import quinta as q
    w = q.con_tetto(np.array([0.5, 0.2, 0.1] + [0.2 / 12] * 12))
    assert abs(w.sum() - 1) < 1e-12 and w.max() <= 0.1 + 1e-12
    # l'ordine resta: chi pesava di piu' pesa ancora almeno quanto gli altri
    assert all(w[i] >= w[i + 1] - 1e-12 for i in range(len(w) - 1))
    assert np.allclose(q.con_tetto(np.full(5, 0.2)), 0.2)         # meno di 10 monete: pesi uguali
    Wt = q.applica_tetto(np.hstack([np.array([[0.5] + [0.5 / 11] * 11]), -np.array([[1 / 12] * 12])]), 0.10)
    assert abs(Wt[0, :12].sum() - 1) < 1e-12 and abs(Wt[0, 12:].sum() + 1) < 1e-12 and Wt[0, :12].max() <= 0.1 + 1e-12


def test_g5_eventi():
    from research.programma7 import sesta as g5
    giorni = np.arange(g5.DA - 40, g5.DA + 40)
    r = np.zeros((len(giorni), 2))
    r[45, 0] = 0.35            # salita
    r[50, 0] = 0.40            # troppo vicina alla prima: non conta
    r[45, 1] = 0.50            # moneta troppo giovane
    vivo_da = np.array([g5.DA - 40, g5.DA + 2])
    vol = np.full(r.shape, 5e6)
    ev = g5.eventi(r, vivo_da, vol, giorni)
    assert ev == [(0, int(giorni[45]) + 1)]
    vol[45, 0] = 1e6           # volume troppo basso: la prima non conta, e allora conta la seconda
    assert g5.eventi(r, vivo_da, vol, giorni) == [(0, int(giorni[50]) + 1)]


def test_g7_eventi_e_operazione():
    import pandas as pd
    from research.programma7 import ottava as g7
    g = np.arange(g7.DA - 40, g7.DA + 80)
    o = np.full(len(g), 10.0)
    o[45:] = 13.5                                   # tra il giorno 44 e il 45 +35%
    c = pd.DataFrame({"open": o, "close": o, "high": o, "low": o, "volume": 1.0}, index=g)
    assert g7.eventi(c, 10 ** 9) == [int(g[45])]
    assert g7.eventi(c, int(g[45])) == []           # gia' su Binance all'ingresso: fuori
    cb = pd.DataFrame({"open": 100.0, "close": 100.0, "high": 100.0, "low": 100.0, "volume": 1.0}, index=g)
    vuoto = pd.Series(dtype=float)
    r = g7.operazione(c, cb, vuoto, vuoto, int(g[45]), True)
    assert not r["fermata"] and abs(r["r"] + g7.vu.COSTO_MONETA + g7.vu.COSTO_BTC) < 1e-12
    c.loc[int(g[50]), "low"] = 13.5 * 0.69          # il minimo va sotto il −30%: uscita
    r = g7.operazione(c, cb, vuoto, vuoto, int(g[45]), True)
    assert r["fermata"] and abs(r["r"] - (0.7 * 0.99 - 1 - g7.vu.COSTO_MONETA - g7.vu.COSTO_BTC)) < 1e-12
