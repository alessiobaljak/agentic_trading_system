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


def test_g8_ora_di_entrata():
    import pandas as pd
    from research.programma7 import nona as g8
    e = 20000
    ore = np.arange(e * 24, e * 24 + 24)
    c = pd.DataFrame({"open": 10.0, "high": 10.0, "close": 10.0}, index=ore)
    assert g8.ora_di_entrata(c, e) == e * 24 + 21           # mai sopra l'apertura: alle 21:00
    c.loc[e * 24 + 3, "close"] = 10.2
    assert g8.ora_di_entrata(c, e) == e * 24 + 4             # la candela delle 03:00 chiude sopra: entrata alle 04:00
    assert g8.ora_di_entrata(c, e + 1) is None


def test_massimo_30():
    from research.programma7 import decima as dm
    r = np.full((60, 2), 0.01)
    r[35, 0] = 0.5
    r[:, 1] = np.nan
    m = dm.massimo_30(r, np.array([40, 70]))
    assert m[0, 0] == 0.5 and np.isnan(m[0, 1])
    assert m[1, 0] == 0.01                                     # il 0,5 del giorno 35 e' fuori dai 30 giorni prima del 70


def test_g9_pesi_inversione():
    from research.programma7 import undicesima as g9
    ieri = np.array([np.linspace(-0.1, 0.1, 25)])
    U = np.ones((1, 25), dtype=bool)
    sig = np.ones((1, 25))
    W = g9.pesi_inversione(ieri, U, sig)
    assert (W[0, :5] > 0).all() and (W[0, -5:] < 0).all() and (W[0, 5:20] == 0).all()
    assert abs(W[0, :5].sum() - 1) < 1e-12 and abs(W[0, -5:].sum() + 1) < 1e-12


def test_g10_ore_cme_e_operazione():
    from datetime import datetime, timezone
    import pandas as pd
    from research.programma7 import dodicesima as g10
    # venerdi' 9 ottobre 2026 (ora legale a Chicago): chiusura 21:00 UTC, riapertura domenica 22:00 UTC
    h_c, h_r = g10.ore_cme(datetime(2026, 10, 9, tzinfo=timezone.utc))
    assert datetime.fromtimestamp(h_c * 3600, timezone.utc).hour == 21 and datetime.fromtimestamp(h_r * 3600, timezone.utc).hour == 22
    h_c2, h_r2 = g10.ore_cme(datetime(2026, 1, 9, tzinfo=timezone.utc))   # inverno: 22:00 e 23:00 UTC
    assert datetime.fromtimestamp(h_c2 * 3600, timezone.utc).hour == 22 and datetime.fromtimestamp(h_r2 * 3600, timezone.utc).hour == 23
    ore = np.arange(h_c, h_r + 200)
    b = pd.DataFrame({"open": 100.0, "high": 100.0, "low": 100.0, "close": 100.0}, index=ore)
    b.loc[h_r:, ["open", "high", "low", "close"]] = 102.0          # buco del 2% in su
    b.loc[h_r + 5, "low"] = 99.9                                   # torna sotto la chiusura del venerdi': obiettivo
    r = g10.operazione(b, h_c, h_r, h_r + 150, pd.Series(dtype=float))
    assert r["verso"] == -1 and r["motivo"] == "obiettivo" and abs(r["R_lordo"] - 1.0) < 1e-12


def test_le_prove_del_programma7_entrano_nel_conto():
    from research.programma6 import asticella as ast
    s = ast.serie_nuove()
    for n in ("57 G1", "58 G2", "59 G4", "60 G3", "61 F5T", "61 G1T", "62 G5", "63 G6", "63 G1+G6", "64 G7", "65 G8", "66 MAX",
              "67 G9", "68 G10", "69 G11", "70 G12", "71 G13", "72 G14", "73 S1", "73 S2"):
        assert n in s and len(s[n]) > 50, n


def test_g12_operazione():
    import pandas as pd
    from research.programma7 import quattordicesima as g12
    ore = np.arange(1000, 1000 + 200)
    c = pd.DataFrame({"open": 10.0}, index=ore)
    cb = pd.DataFrame({"open": 100.0}, index=ore)
    c.loc[1000 + 168, "open"] = 9.0                                # la moneta scende del 10% in 7 giorni
    vuoto = pd.Series(dtype=float)
    r = g12.operazione(c, cb, vuoto, vuoto, 1000)
    assert abs(r - (0.10 - g12.vu.COSTO_MONETA - g12.vu.COSTO_BTC)) < 1e-12
    assert g12.operazione(c, cb, vuoto, vuoto, 1100) is None      # manca l'ora d'uscita


def test_g13_sigle_del_titolo():
    from research.programma7 import quindicesima as g13
    assert g13.sigle_del_titolo("Binance Futures Will Delist 1000BTTC and YFII USDT-Margined Contracts") == ["1000BTTC", "YFII"]
    assert g13.sigle_del_titolo("Binance Futures Will Delist USDⓈ-Margined IPUSDT and IPUSDC Perpetual Contracts (2026-06-28)") == ["IP"]
    assert g13.sigle_del_titolo("Binance Futures Will Delist PTBUSDT and MITOUSDT USDⓈ-M Perpetual Contracts (2026-10-23)") == ["PTB", "MITO"]
    assert g13.sigle_del_titolo("Binance Futures Will Delist Multiple USDⓈ-M Perpetual Contracts (2026-10-05)") == []
    assert g13.sigle_del_titolo("Binance Futures Will Delist USDT-Margined ANC Perpetual Contract") == ["ANC"]


def test_g14_segnale_e_conto():
    import pandas as pd
    from research.programma7 import sedicesima as g14
    g = 20000
    ore = np.arange(g * 24 - 24, g * 24 + 24)
    bn = pd.Series(100.0, index=ore)
    cb = pd.Series(100.1, index=ore)                 # premio +0,1% tutto il giorno prima
    s = g14.segnale_giornaliero(cb, bn, np.array([g, g + 2]))
    assert abs(s[0] - 0.001) < 1e-12 and np.isnan(s[1])
    d = g14.conto(np.array([1.0, 1.0, -1.0]), np.array([0.01, -0.02, 0.03]), np.array([0.0001, 0.0001, 0.0001]))
    assert list(d["giro"]) == [1.0, 0.0, 2.0]
    assert abs(d["netto"].iloc[2] - (-0.03 - 2 * g14.COSTO + 0.0001)) < 1e-12


def test_g15_eventi_e_operazione():
    from research.programma7 import diciassettesima as g15
    x = {"circolante": [[99, 1000.0], [100, 1000.0], [130, 1100.0]],
         "gradini": [[100, "insiders", 30.0, "Team"], [100, "privateSale", 20.0, "Investors"], [100, "airdrop", 500.0, "Airdrop"],
                     [131, "insiders", 5.0, "Team"], [140, "insiders", 50.0, "Team"]]}
    ev = g15.eventi_del_protocollo(x)
    assert ev[0] == {"giorno": 100, "dimensione": 0.05, "categorie": "insiders+privateSale"}   # l'airdrop non conta
    assert len(ev) == 2 and abs(ev[1]["dimensione"] - 5 / 1100) < 1e-12                       # il 140 non ha l'offerta del giorno prima
    assert g15.prefisso("1000PEPEUSDT", "PEPE") == 1e3 and g15.prefisso("ARBUSDT", "ARB") == 1.0
    T, S = 60, 2
    pan = {k: np.full((T, S), 100.0) for k in ("open", "high", "close")}
    pan["funding"] = np.zeros((T, S))
    pan["open"][41, 0] = 90.0                                                                 # la moneta scende del 10%
    r = g15.operazione(pan, 0, 1, 10, 41)
    assert abs(r["r"] - (0.10 - g15.vu.COSTO_MONETA - g15.vu.COSTO_BTC)) < 1e-12 and not r["fermata"] and r["giorni"] == 31
    pan["high"][20, 0] = 131.0                                                                # tocca +30% il giorno 20
    r = g15.operazione(pan, 0, 1, 10, 41)
    assert r["fermata"] and r["giorni"] == 10
    assert abs(r["r"] - (-(1.3 * 1.01 - 1) - g15.vu.COSTO_MONETA - g15.vu.COSTO_BTC)) < 1e-12


def test_g16_segnale_e_uscite():
    import pandas as pd
    from research.programma7 import diciottesima as g16
    m = np.arange(0, 3000)
    w = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0, "dollari": 100.0}, index=m)
    # dal minuto 2000: +60% sul giorno prima, +5% nell'ultimo quarto d'ora, volume 10 volte
    w.loc[1986:2000, ["open", "high", "low", "close"]] = 1.55
    w.loc[2000, "close"] = 1.63
    w.loc[1986:2000, "dollari"] = 1000.0
    s = g16.segnali(w, np.arange(1500, 2100))
    assert 2000 in s and min(s) >= 1986 and max(s) <= 2000      # solo dentro la fiammata
    # obiettivo: dal minuto 2010 il minimo scende del 5% sotto l'entrata (apertura del 2001)
    w.loc[2001:, ["open", "high", "low", "close"]] = 1.60
    w.loc[2010, "low"] = 1.60 * 0.95
    op = g16.operazione(w, 2000, 0.001)
    assert op["motivo"] == "obiettivo" and op["minuti"] == 9 and abs(op["r_prezzo"] - 0.05) < 1e-12
    assert abs(op["costi"] - (0.001 + g16.MAKER)) < 1e-12
    # protezione prima dell'obiettivo
    w.loc[2005, "high"] = 1.60 * 1.31
    op = g16.operazione(w, 2000, 0.001)
    assert op["motivo"] == "protezione" and abs(op["r_prezzo"] - (-(1.3 * 1.01 - 1))) < 1e-12
    # senza protezione: arriva all'obiettivo
    assert g16.operazione(w, 2000, 0.001, protezione=False)["motivo"] == "obiettivo"


def test_g17_conto_con_quota_piccola():
    import pandas as pd
    from research.programma7 import diciannovesima as g17
    g = g17.DA + 10
    df = pd.DataFrame({"entrata_min": [g * 1440, g * 1440 + 10, (g + 1) * 1440], "uscita_min": [g * 1440 + 5, g * 1440 + 20, (g + 1) * 1440 + 5],
                       "r": [0.05, -3.0, 0.05]})
    sett, discesa, tenute = g17.conto(df, 0.01)
    assert tenute == 3 and abs(sett["netto"].sum() - 0.01 * (0.05 - 3.0 + 0.05)) < 1e-12
    assert abs(discesa - (-0.03)) < 1e-12           # dal massimo 1,0005 a 0,9705


def test_g18_segnale_e_uscite():
    import pandas as pd
    from research.programma7 import ventesima as g18
    n = 600
    p = np.linspace(100.0, 102.0, n)                       # sale del 2% in 600 minuti: alla fine sta in cima all'intervallo
    w = pd.DataFrame({"open": p, "high": p + 0.01, "low": p - 0.01, "close": p}, index=np.arange(n))
    s = g18.segnali(w)
    assert s.iloc[-1] == -1 and (s.iloc[:239] == 0).all()
    o = np.full(100, 100.0); h = o + 0.05; l = o - 0.05
    l[10] = 100.0 * (1 - g18.OBIETTIVO) - 0.01               # short: il minimo tocca l'obiettivo al minuto 10
    op = g18.operazione(o, h, l, 0, -1)
    assert op["motivo"] == "obiettivo" and op["minuti"] == 9 and abs(op["r_prezzo"] - g18.OBIETTIVO) < 1e-12
    h[5] = 100.0 * (1 + g18.PROTEZIONE) + 0.01               # prima tocca la protezione
    op = g18.operazione(o, h, l, 0, -1)
    assert op["motivo"] == "protezione" and abs(op["r_prezzo"] + g18.PROTEZIONE) < 1e-12
