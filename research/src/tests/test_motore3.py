"""Test del motore del protocollo 3 (``research/src/motore3.py``) con esempi calcolati a mano.

Fonte delle regole: ``research/PROTOCOLLO_3.md``, sezioni 6 (costi), 7.6 (stop e uscite), 7.7
(ingresso a mercato e limit, le 7 regole), 7.8 (regole fisse), 8.4 (stima dei trade) e 9 (9.1-9.9).
Il Passo 0, punto 5, chiede almeno un test per ogni regola di 7.7 e 9: ogni test dice quale regola
prova e porta nei commenti il conto fatto a mano.

Le serie sono costruite a mano: candele da 1 ora (o da 12 ore per il funding, cosi' un regolamento
puo' cadere DENTRO una candela), con ``ts`` multipli della durata, mark uguale al last se il test
non chiede altro. Le varianti si compilano con ``catalogo3.compila``; per far scattare un segnale in
una candela precisa si scrive a mano l'array ``segnale`` (o ``opposto`` per U4) della variante
compilata, e gli ATR (``atr_stop``, ``atr_limite``, ``atr_trailing``) si fissano a mano.

Le scelte che il protocollo lascia aperte seguono le ``SCELTA`` del motore (per esempio la serie
dello stop "last_e_mark", il mark del funding = apertura della candela mark che contiene T).

Costi normali: taker 0,0005, maker 0,0002, slippage 0,0001. Capitale 10.000, rischio 1% = 100 USDT.
"""

from __future__ import annotations

import datetime as dt

import numpy as np
import pytest

from research.src import catalogo3
from research.src import motore3
from research.src.catalogo3 import TIMEFRAME_MS, Serie, VarianteNonValida, compila, normalizza
from research.src.motore3 import (
    COSTI_DOPPI,
    COSTI_NORMALI,
    Regole,
    Risultato,
    Trade,
    drawdown_r,
    esegui,
    metriche,
    prezzo_liquidazione,
    profit_factor,
    simula_da,
    stima_trade,
)

ORA = 3_600_000
DODICI_ORE = 12 * ORA

#: candela "piatta": non tocca lo stop all'1% (99,0099 long, 100,9899 short) ne' il target a 2 R
P = (100.0, 100.5, 99.5, 100.0)
#: candela del segnale (il motore non la legge, salvo la chiusura per il limit)
SEG = (100.0, 101.0, 99.0, 100.0)

#: quantita' con stop S3 1% e ingresso a mercato a 100: long entra a 100,01, distanza 1,0001;
#: short entra a 99,99, distanza 0,9999
Q_LONG = 100 / 1.0001  # 99,990001
Q_SHORT = 100 / 0.9999  # 100,010001
#: limit a 99 con stop S3 1%: stop 98,01, distanza 0,99
Q_LIMIT = 100 / 0.99  # 101,010101


# ---------------------------------------------------------------------------
# strumenti
# ---------------------------------------------------------------------------


def candele(ohlc, tf="1h", t0=0, ts=None, mark=None, funding=()):
    """Una ``Serie`` dalle candele (apertura, massimo, minimo, chiusura). ``mark``: stesse candele
    del last se manca. ``funding``: coppie (istante in ms, tasso)."""
    d = TIMEFRAME_MS[tf]
    n = len(ohlc)
    if ts is None:
        ts = [t0 + k * d for k in range(n)]
    o, h, l, c = (np.array(x, dtype=float) for x in zip(*ohlc))
    if mark is None:
        mo, mh, ml, mc = o.copy(), h.copy(), l.copy(), c.copy()
    else:
        mo, mh, ml, mc = (np.array(x, dtype=float) for x in zip(*mark))
    f_ts = [int(f[0]) for f in funding]
    f_r = [float(f[1]) for f in funding]
    return Serie(tf, ts, o, h, l, c, np.ones(n), mo, mh, ml, mc, f_ts, f_r)


def variante(direzione="long", tipo=None, stop=None, uscite=None, tf="1h"):
    """Una variante del catalogo; l'ingresso E3 non conta, perche' il segnale si scrive a mano."""
    return {"timeframe": tf, "direzione": direzione, "filtro": None,
            "ingresso": {"codice": "E3", "n": 20}, "conferma": None,
            "tipo_ingresso": tipo or {"codice": "M"},
            "stop": stop or {"codice": "S3", "pct": 0.01},
            "uscite": uscite or [{"codice": "U1", "k": 2}]}


def limit(k=0.5, validita=1):
    return {"codice": "L", "k": k, "validita": validita}


def _array(n, valore):
    if np.isscalar(valore):
        return np.full(n, float(valore))
    a = np.asarray(valore, dtype=float)
    assert len(a) == n
    return a


def prepara(s, v, segnali=(), opposti=(), atr=None, atr_stop=None, atr_limite=None, atr_trailing=None):
    """Compila la variante e scrive a mano segnali, segnali opposti e ATR."""
    c = compila(v, s)
    n = len(s)
    c.segnale = np.zeros(n, dtype=bool)
    c.segnale[list(segnali)] = True
    c.opposto = np.zeros(n, dtype=bool)
    c.opposto[list(opposti)] = True
    for nome, val in (("atr_stop", atr_stop), ("atr_limite", atr_limite), ("atr_trailing", atr_trailing)):
        val = atr if val is None else val
        if val is not None and getattr(c, nome) is not None:
            setattr(c, nome, _array(n, val))
    return c


def sim(c, i=0, regole=Regole(), costi=COSTI_NORMALI, fine=None):
    return simula_da(c, i, regole, costi, len(c.serie) - 1 if fine is None else fine)


def r_atteso(long, q, ingresso, uscita, comm_in, comm_out=0.0005, funding=0.0, rischio=100.0):
    """R a mano (9.3, 9.7): (lato x Q x (uscita - ingresso) - commissioni + funding) / rischio."""
    sg = 1.0 if long else -1.0
    pnl = sg * q * (uscita - ingresso) - q * ingresso * comm_in - q * uscita * comm_out + funding
    return pnl / rischio


# ---------------------------------------------------------------------------
# 6 e 9.3: prezzi di esecuzione, commissioni, R
# ---------------------------------------------------------------------------


def test_ingresso_a_mercato_long_e_target():
    """9.3 ingresso a mercato long = apertura x 1,0001; target = target x 0,9999; taker 0,05% su
    ingresso e uscita; 9.4 quantita' = 100 / distanza; 9.7 R = USDT / rischio iniziale."""
    s = candele([SEG, P, (100.0, 103.0, 99.8, 102.5)])
    c = prepara(s, variante(), segnali=[0])
    es = sim(c)
    assert es.tipo == "trade"
    t = es.trade
    # ingresso = 100 x 1,0001 = 100,01
    assert t.prezzo_ingresso == pytest.approx(100.01, abs=1e-12)
    assert t.indice_ingresso == 1 and t.ts_ingresso == ORA
    # stop S3 1% dal prezzo EFFETTIVO: 100,01 x 0,99 = 99,0099 (non 99,0)
    assert t.stop_iniziale == pytest.approx(99.0099, abs=1e-12)
    # distanza 1,0001; target U1 2 R = 100,01 + 2 x 1,0001 = 102,0102
    assert t.target == pytest.approx(102.0102, abs=1e-12)
    # quantita' = 100 / 1,0001 = 99,990001; valore = 99,990001 x 100,01 = 10.000 (leva 1)
    assert t.quantita == pytest.approx(Q_LONG, rel=1e-12)
    assert t.quantita * t.prezzo_ingresso == pytest.approx(10_000.0, rel=1e-12)
    assert t.rischio_usdt == pytest.approx(100.0, rel=1e-12)
    assert not t.ridotto
    # candela 2: massimo 103 >= 102,0102 -> target; uscita 102,0102 x 0,9999 = 101,99999898
    assert t.motivo == "target" and t.indice_uscita == 2
    assert t.prezzo_uscita == pytest.approx(101.99999898, abs=1e-9)
    # commissioni: 10.000 x 0,0005 = 5 all'ingresso; 99,990001 x 101,99999898 x 0,0005 = 5,09949
    assert t.commissioni == pytest.approx(5.0 + 5.09949, abs=1e-6)
    # pnl = 99,990001 x (101,99999898 - 100,01) - 5 - 5,09949 = 198,98 - 10,09949 = 188,88051
    assert t.pnl == pytest.approx(188.88051, abs=1e-6)
    assert t.funding == 0.0
    # R = 188,88051 / 100 = 1,8888051
    assert t.r == pytest.approx(1.8888051, abs=1e-9)
    assert t.r == pytest.approx(r_atteso(True, Q_LONG, 100.01, 102.0102 * 0.9999, 0.0005), rel=1e-12)
    # candele in posizione: 1 (chiusa) + la candela dell'uscita = 2
    assert t.candele_in_posizione == 2


def test_ingresso_a_mercato_short_e_stop():
    """9.3 short: ingresso apertura x 0,9999; stop x 1,0001; S3 dal prezzo effettivo."""
    s = candele([SEG, (100.0, 100.5, 99.5, 100.2), (100.2, 101.2, 100.0, 101.0)])
    c = prepara(s, variante("short"), segnali=[0])
    t = sim(c).trade
    # ingresso 100 x 0,9999 = 99,99; stop 99,99 x 1,01 = 100,9899; distanza 0,9999
    assert t.prezzo_ingresso == pytest.approx(99.99, abs=1e-12)
    assert t.stop_iniziale == pytest.approx(100.9899, abs=1e-12)
    # target 99,99 - 2 x 0,9999 = 97,9902
    assert t.target == pytest.approx(97.9902, abs=1e-12)
    assert t.quantita == pytest.approx(Q_SHORT, rel=1e-12)
    # candela 2: massimo 101,2 >= 100,9899 -> stop; uscita 100,9899 x 1,0001 = 100,99999899
    assert t.motivo == "stop" and t.indice_uscita == 2
    assert t.prezzo_uscita == pytest.approx(100.99999899, abs=1e-9)
    # pnl = -100,010001 x (100,99999899 - 99,99) - 5 - 100,010001 x 100,99999899 x 0,0005
    #     = -101,01 - 5 - 5,050505 = -111,060505  ->  R = -1,11060505
    assert t.r == pytest.approx(-1.11060505, abs=1e-8)


def test_esempio_della_sezione_6_costi_di_un_trade_piatto():
    """Sezione 6, esempio: posizione da 10.000, stop 1%: 5 + 5 di commissioni e 1 + 1 di slippage
    = 12 USDT = 0,12 R; con ingresso limit 2 di commissione d'ingresso e niente slippage = 0,08 R."""
    # a mercato: entra a 100,01, esce (segnale opposto) all'apertura 100 x 0,9999 = 99,99
    s = candele([SEG, P, P, P])
    c = prepara(s, variante(uscite=[{"codice": "U4"}]), segnali=[0], opposti=[1])
    t = sim(c).trade
    assert t.motivo == "segnale_opposto" and t.prezzo_uscita == pytest.approx(99.99, abs=1e-12)
    # 99,990001 x (99,99 - 100,01) = -1,9998; commissioni 5 + 99,990001 x 99,99 x 0,0005 = 4,999
    # totale -11,9988 USDT = -0,119988 R (circa 0,12 R)
    assert t.r == pytest.approx(-0.119988, abs=1e-6)
    # limit: chiusura 100, ATR 2, k 0,5 -> limit 99; eseguito nella candela 1 (minimo 98,8 < 99)
    s = candele([SEG, (99.5, 99.8, 98.8, 99.0), (99.0, 99.4, 98.6, 99.0), P])
    c = prepara(s, variante(tipo=limit(), uscite=[{"codice": "U4"}]), segnali=[0], opposti=[1], atr=2.0)
    t = sim(c).trade
    # Q = 100 / 0,99 = 101,0101; commissione maker 10.000 x 0,0002 = 2; uscita 99 x 0,9999 = 98,9901
    # 101,0101 x (98,9901 - 99) = -1,0; commissione d'uscita 101,0101 x 98,9901 x 0,0005 = 4,9995
    # totale -7,9995 USDT = -0,079995 R (circa 0,08 R)
    assert t.prezzo_ingresso == 99.0
    assert t.r == pytest.approx(-0.079995, abs=1e-6)


def test_costi_doppi_valori():
    """Sezione 6, costi doppi: taker 0,10%, maker 0,04%, slippage 0,02%."""
    assert (COSTI_DOPPI.taker, COSTI_DOPPI.maker, COSTI_DOPPI.slippage) == (0.0010, 0.0004, 0.0002)
    assert (COSTI_NORMALI.taker, COSTI_NORMALI.maker, COSTI_NORMALI.slippage) == (0.0005, 0.0002, 0.0001)


def test_costi_doppi_a_mercato():
    """Costi doppi, ingresso a mercato: slippage 0,0002 a ogni lato, taker 0,001."""
    s = candele([SEG, P, (100.0, 103.0, 99.8, 102.5)])
    c = prepara(s, variante(), segnali=[0])
    t = sim(c, costi=COSTI_DOPPI).trade
    # ingresso 100 x 1,0002 = 100,02; stop 100,02 x 0,99 = 99,0198; distanza 1,0002
    assert t.prezzo_ingresso == pytest.approx(100.02, abs=1e-12)
    assert t.stop_iniziale == pytest.approx(99.0198, abs=1e-12)
    # target 100,02 + 2 x 1,0002 = 102,0204; uscita 102,0204 x 0,9998 = 101,99999592
    assert t.prezzo_uscita == pytest.approx(101.99999592, abs=1e-9)
    # Q = 100 / 1,0002; valore 10.000; commissioni 10 + Q x 101,99999592 x 0,001 = 10 + 10,19796
    # pnl = Q x 1,97999592 - 20,19796 = 197,96 - 20,19796 = 177,76204 -> R = 1,7776204
    assert t.r == pytest.approx(1.7776204, abs=1e-7)
    assert t.r == pytest.approx(r_atteso(True, 100 / 1.0002, 100.02, 102.0204 * 0.9998, 0.001, 0.001), rel=1e-12)


def test_costi_doppi_con_ingresso_limit():
    """Costi doppi, ingresso limit: maker 0,04%, nessuno slippage d'ingresso; uscita taker 0,10% e
    slippage 0,02%."""
    s = candele([P, (98.5, 99.5, 98.2, 99.2), (99.2, 101.5, 99.0, 101.0)])
    c = prepara(s, variante(tipo=limit()), segnali=[0], atr=2.0)
    t = sim(c, costi=COSTI_DOPPI).trade
    # limit 100 - 0,5 x 2 = 99, prezzo d'ingresso 99 senza slippage; target 99 + 2 x 0,99 = 100,98
    assert t.prezzo_ingresso == 99.0
    # uscita al target 100,98 x 0,9998 = 100,959804
    assert t.prezzo_uscita == pytest.approx(100.959804, abs=1e-9)
    # commissioni: 10.000 x 0,0004 = 4 + Q x 100,959804 x 0,001 = 10,197960
    assert t.commissioni == pytest.approx(4.0 + Q_LIMIT * 100.959804 * 0.001, abs=1e-9)
    # pnl = 101,0101 x 1,959804 - 14,19796 = 197,96 - 14,19796 = 183,76204 -> R 1,8376204
    assert t.r == pytest.approx(1.8376204, abs=1e-7)


# ---------------------------------------------------------------------------
# 9.2 e 9.3: uscite dentro la candela
# ---------------------------------------------------------------------------


def test_salto_oltre_lo_stop_esce_all_apertura():
    """9.2 punto 1 e 9.3: se la candela apre oltre lo stop, uscita all'apertura x (1 - 0,0001)."""
    # long: stop 99,0099; la candela 2 apre a 98,5
    s = candele([SEG, (100.0, 100.5, 99.5, 99.6), (98.5, 99.0, 97.0, 98.0)])
    t = sim(prepara(s, variante(), segnali=[0])).trade
    assert t.motivo == "stop_salto" and t.indice_uscita == 2
    # uscita 98,5 x 0,9999 = 98,49015 (non lo stop 99,0099 x 0,9999)
    assert t.prezzo_uscita == pytest.approx(98.49015, abs=1e-9)
    # pnl = 99,990001 x (98,49015 - 100,01) - 5 - 99,990001 x 98,49015 x 0,0005
    #     = -151,9698 - 5 - 4,9240 = -161,8938 -> R = -1,618938
    assert t.r == pytest.approx(-1.6189381812, abs=1e-8)
    # uscita all'apertura: ts dell'uscita = apertura della candela 2, 1 sola candela chiusa
    assert t.ts_uscita == 2 * ORA and t.candele_in_posizione == 1
    # short: stop 100,9899; la candela 2 apre a 101,5 -> uscita 101,5 x 1,0001 = 101,510150
    s = candele([SEG, (100.0, 100.5, 99.5, 100.4), (101.5, 102.0, 101.0, 101.8)])
    t = sim(prepara(s, variante("short"), segnali=[0])).trade
    assert t.motivo == "stop_salto"
    assert t.prezzo_uscita == pytest.approx(101.51015, abs=1e-9)
    assert t.r == pytest.approx(r_atteso(False, Q_SHORT, 99.99, 101.51015, 0.0005), rel=1e-12)


def test_target_con_apertura_oltre_il_target_esce_al_target():
    """9.3: l'uscita al target e' sempre target x (1 - 0,0001), anche se la candela apre oltre."""
    s = candele([SEG, P, (103.0, 104.0, 102.8, 103.5)])
    t = sim(prepara(s, variante(), segnali=[0])).trade
    # target 102,0102 -> 101,99999898 (non l'apertura 103 x 0,9999)
    assert t.motivo == "target"
    assert t.prezzo_uscita == pytest.approx(101.99999898, abs=1e-9)
    assert t.r == pytest.approx(1.8888051, abs=1e-9)


def test_stop_e_target_nella_stessa_candela():
    """9.2: stop e target nella stessa candela -> vale lo stop; con intrabarra "target_prima"
    (Fase 4, verifica 9) vale il target."""
    s = candele([SEG, P, (100.0, 103.0, 98.9, 101.0)])  # minimo 98,9 <= 99,0099; massimo 103 >= 102,0102
    c = prepara(s, variante(), segnali=[0])
    t = sim(c).trade
    assert t.motivo == "stop"
    # uscita 99,0099 x 0,9999 = 99,0099 - 0,00990099 = 98,99999901
    assert t.prezzo_uscita == pytest.approx(98.99999901, abs=1e-9)
    # pnl = 99,990001 x (98,99999901 - 100,01) - 5 - 99,990001 x 98,99999901 x 0,0005
    #     = -100,9899 - 5 - 4,9496 = -110,93951 -> R = -1,1093951
    assert t.r == pytest.approx(r_atteso(True, Q_LONG, 100.01, 99.0099 * 0.9999, 0.0005), rel=1e-12)
    assert t.r == pytest.approx(-1.1093951, abs=1e-6)
    t = sim(c, regole=Regole(intrabarra="target_prima")).trade
    assert t.motivo == "target"
    assert t.r == pytest.approx(1.8888051, abs=1e-9)


def test_serie_dello_stop_last_e_mark():
    """9.1: lo stop si confronta con la serie del bot. SCELTA "last_e_mark": basta che lo tocchi
    una delle due. Il prezzo d'uscita resta stop x 0,9999."""
    last = [SEG, P, (100.0, 100.4, 99.6, 100.1)]
    mark = [SEG, P, (100.0, 100.4, 99.0, 100.1)]  # solo il mark scende a 99,0 <= 99,0099
    s = candele(last, mark=mark)
    c = prepara(s, variante(), segnali=[0])
    t = sim(c).trade  # predefinito: last_e_mark
    assert t.motivo == "stop" and t.indice_uscita == 2
    assert t.prezzo_uscita == pytest.approx(99.0099 * 0.9999, abs=1e-12)
    t = sim(c, regole=Regole(serie_stop="mark")).trade
    assert t.motivo == "stop" and t.indice_uscita == 2
    # solo il last: il minimo 99,6 non tocca lo stop -> la posizione arriva alla fine dei dati
    t = sim(c, regole=Regole(serie_stop="last")).trade
    assert t.motivo == "fine_dati"


def test_uscite_dentro_la_candela_prima_di_quelle_alla_chiusura():
    """9.2: i controlli dentro la candela (punto 1) vengono prima di quelli alla chiusura (punto 4):
    con U2 n = 6, se lo stop si tocca proprio nella sesta candela si esce per stop."""
    righe = [SEG] + [P] * 8
    righe[6] = (100.0, 100.5, 98.9, 99.5)  # sesta candela dall'ingresso (1..6): tocca lo stop 99,0099
    s = candele(righe)
    t = sim(prepara(s, variante(uscite=[{"codice": "U2", "n": 6}]), segnali=[0])).trade
    assert t.motivo == "stop" and t.indice_uscita == 6


# ---------------------------------------------------------------------------
# 7.6: stop
# ---------------------------------------------------------------------------


def test_stop_s1_dal_prezzo_effettivo_con_atr_del_segnale():
    """S1: ingresso EFFETTIVO -/+ k x ATR(14) della candela del SEGNALE."""
    s = candele([SEG, P, P, P])
    atr = [2.0, 5.0, 5.0, 5.0]  # l'ATR della candela del segnale (0) e' 2; dopo e' 5
    c = prepara(s, variante(stop={"codice": "S1", "k": 1.5}), segnali=[0], atr_stop=atr)
    t = sim(c).trade
    # long: 100,01 - 1,5 x 2 = 97,01 (con l'ATR della candela d'ingresso sarebbe 92,51)
    assert t.stop_iniziale == pytest.approx(97.01, abs=1e-12)
    # distanza 3 -> Q = 100 / 3 = 33,333; target 100,01 + 2 x 3 = 106,01
    assert t.quantita == pytest.approx(100 / 3.0, rel=1e-12)
    assert t.target == pytest.approx(106.01, abs=1e-12)
    c = prepara(s, variante("short", stop={"codice": "S1", "k": 1.5}), segnali=[0], atr_stop=atr)
    t = sim(c).trade
    # short: 99,99 + 3 = 102,99; target 99,99 - 6 = 93,99
    assert t.stop_iniziale == pytest.approx(102.99, abs=1e-12)
    assert t.target == pytest.approx(93.99, abs=1e-12)


def test_stop_s2_estremo_delle_ultime_n_candele_compresa_quella_del_segnale():
    """S2: minimo (long) o massimo (short) delle ultime n candele, compresa quella del segnale."""
    minimi = [90.0, 91.0, 97.0, 98.5, 98.0, 97.5, 96.5]
    righe = [(m + 1.5, m + 3.0, m, m + 1.5) for m in minimi] + [(100.0, 100.5, 99.6, 100.0), P]
    s = candele(righe)
    c = prepara(s, variante(stop={"codice": "S2", "n": 5}), segnali=[6])
    # n = 5, segnale alla candela 6: minimo dei minimi 2..6 = min(97; 98,5; 98; 97,5; 96,5) = 96,5
    # (senza la candela del segnale sarebbe min(1..5) = 91)
    assert c.estremo_s2[6] == 96.5
    t = sim(c, i=6).trade
    assert t.stop_iniziale == 96.5
    # distanza 100,01 - 96,5 = 3,51 -> Q = 100 / 3,51
    assert t.quantita == pytest.approx(100 / 3.51, rel=1e-12)
    massimi = [110.0, 109.0, 103.0, 101.5, 102.0, 102.5, 103.5]
    righe = [(m - 1.5, m, m - 3.0, m - 1.5) for m in massimi] + [(100.0, 100.4, 99.5, 100.0), P]
    s = candele(righe)
    c = prepara(s, variante("short", stop={"codice": "S2", "n": 5}), segnali=[6])
    # short: massimo dei massimi 2..6 = 103,5
    assert c.estremo_s2[6] == 103.5
    t = sim(c, i=6).trade
    assert t.stop_iniziale == 103.5
    # distanza 103,5 - 99,99 = 3,51
    assert t.quantita == pytest.approx(100 / 3.51, rel=1e-12)


def test_stop_s3_percentuale_dal_prezzo_effettivo():
    """S3: percentuale fissa dal prezzo di ingresso effettivo."""
    s = candele([SEG, P, P])
    t = sim(prepara(s, variante(stop={"codice": "S3", "pct": 0.02}), segnali=[0])).trade
    # 100,01 x 0,98 = 98,0098
    assert t.stop_iniziale == pytest.approx(98.0098, abs=1e-12)
    t = sim(prepara(s, variante("short", stop={"codice": "S3", "pct": 0.03}), segnali=[0])).trade
    # 99,99 x 1,03 = 102,9897
    assert t.stop_iniziale == pytest.approx(102.9897, abs=1e-12)


def test_stop_minimo_a_mercato():
    """7.6: stop a meno dello 0,3% del prezzo di ingresso (effettivo) -> il trade non si apre."""
    s = candele([SEG, P, P])
    v = variante(stop={"codice": "S1", "k": 1.0})
    # ATR 0,29: distanza 0,29 / 100,01 = 0,28997% < 0,3% -> niente trade
    es = sim(prepara(s, v, segnali=[0], atr_stop=0.29))
    assert es.tipo == "stop_troppo_vicino" and es.trade is None and es.libero_da == 1
    # ATR 0,30002: 0,30002 / 100,01 = 0,29999% < 0,3% -> niente trade (sull'apertura grezza 100
    # sarebbe 0,30002%: il controllo e' sul prezzo effettivo dopo lo slippage)
    es = sim(prepara(s, v, segnali=[0], atr_stop=0.30002))
    assert es.tipo == "stop_troppo_vicino"
    # ATR 0,31: 0,31 / 100,01 = 0,30997% -> trade aperto
    es = sim(prepara(s, v, segnali=[0], atr_stop=0.31))
    assert es.tipo == "trade"
    assert es.trade.stop_iniziale == pytest.approx(100.01 - 0.31, abs=1e-12)


def test_stop_minimo_con_ingresso_limit_sul_prezzo_limit():
    """7.6 e 7.7: per il limit il controllo si fa quando si inserisce l'ordine, sul prezzo limit;
    se lo stop non e' oltre il limit di almeno lo 0,3%, l'ordine non si inserisce."""
    s = candele([P, (99.5, 99.8, 98.9, 99.2), P])
    v = variante(tipo=limit(), stop={"codice": "S1", "k": 1.0})
    # limit = 100 - 0,5 x 2 = 99. ATR dello stop 0,29: 0,29 / 99 = 0,2929% -> ordine non inserito
    es = sim(prepara(s, v, segnali=[0], atr_limite=2.0, atr_stop=0.29))
    assert es.tipo == "ordine_non_inserito" and es.libero_da == 1
    # ATR dello stop 0,299: 0,299 / 99 = 0,30202% >= 0,3% -> ordine inserito (sulla chiusura 100
    # sarebbe 0,299%: il controllo e' sul prezzo limit); eseguito nella candela 1 (minimo 98,9 < 99)
    es = sim(prepara(s, v, segnali=[0], atr_limite=2.0, atr_stop=0.299))
    assert es.tipo == "trade"
    # stop = 99 - 0,299 = 98,701, dal prezzo limit
    assert es.trade.stop_iniziale == pytest.approx(98.701, abs=1e-12)
    assert es.trade.prezzo_ingresso == 99.0


# ---------------------------------------------------------------------------
# 7.6: uscite
# ---------------------------------------------------------------------------


def test_u2_uscita_a_tempo_la_candela_di_ingresso_e_la_prima():
    """U2 n = 6: uscita all'apertura della candela dopo la sesta candela chiusa; la candela di
    ingresso e' la prima. Ingresso alla 1 -> chiuse 1..6 -> uscita all'apertura della 7."""
    righe = [SEG] + [P] * 8
    righe[7] = (100.3, 100.5, 99.5, 100.0)
    s = candele(righe)
    t = sim(prepara(s, variante(uscite=[{"codice": "U2", "n": 6}]), segnali=[0])).trade
    assert t.motivo == "tempo"
    assert t.indice_uscita == 7 and t.ts_uscita == 7 * ORA
    # 9.3: uscita a tempo all'apertura x 0,9999 = 100,3 x 0,9999 = 100,28997
    assert t.prezzo_uscita == pytest.approx(100.28997, abs=1e-9)
    assert t.candele_in_posizione == 6


def test_u2s_uscita_alla_prima_candela_delle_21_utc():
    """U2s: uscita all'apertura della prima candela che inizia alle 21:00 UTC o dopo."""
    righe = [SEG, P, P, (100.2, 100.5, 99.5, 100.0), P]
    s = candele(righe, t0=18 * ORA)  # candele delle 18, 19, 20, 21, 22
    t = sim(prepara(s, variante(uscite=[{"codice": "U2s"}]), segnali=[0])).trade
    # segnale alle 18, ingresso alle 19, uscita all'apertura delle 21 (indice 3)
    assert t.motivo == "fine_giornata"
    assert t.indice_uscita == 3 and t.ts_uscita == 21 * ORA
    assert t.prezzo_uscita == pytest.approx(100.2 * 0.9999, abs=1e-12)


def test_u2s_ingresso_dopo_le_21_esce_alle_21_del_giorno_dopo():
    """U2s, caso che il protocollo non scrive (vedi il rapporto): ingresso alle 23:00. La candela
    delle 00:00 del giorno dopo non "inizia alle 21:00 o dopo" come ora del giorno, quindi il motore
    tiene la posizione fino alle 21:00 del giorno dopo. Il test fissa il comportamento del motore."""
    s = candele([SEG] + [P] * 25, t0=22 * ORA)  # indice k = ore 22 + k
    t = sim(prepara(s, variante(uscite=[{"codice": "U2s"}]), segnali=[0])).trade
    # ingresso all'indice 1 (23:00); 21:00 del giorno dopo = 22 + 23 ore -> indice 23
    assert t.indice_ingresso == 1
    assert t.motivo == "fine_giornata" and t.indice_uscita == 23
    assert (t.ts_uscita % (24 * ORA)) == 21 * ORA


def test_u3_trailing_sale_e_non_scende_mai():
    """U3 k = 2: a ogni chiusura stop = max(stop, massimo dall'ingresso - 2 x ATR); mai piu' basso."""
    righe = [SEG,
             (100.0, 101.0, 99.8, 100.8),   # 1 ingresso: max 101 -> 101 - 2 = 99 < 99,0099: resta 99,0099
             (100.8, 103.0, 100.5, 102.5),  # 2: max 103 -> 103 - 2 = 101 -> stop 101
             (102.5, 102.8, 101.5, 102.0),  # 3: minimo 101,5 > 101; ATR 1,5 -> 103 - 3 = 100 < 101: resta 101
             (102.0, 102.2, 100.9, 101.2),  # 4: minimo 100,9 <= 101 -> uscita
             P]
    s = candele(righe)
    atr = [1.0, 1.0, 1.0, 1.5, 1.0, 1.0]
    t = sim(prepara(s, variante(uscite=[{"codice": "U3", "k": 2}]), segnali=[0], atr_trailing=atr)).trade
    assert t.motivo == "trailing" and t.indice_uscita == 4
    # uscita 101 x 0,9999 = 100,9899
    assert t.prezzo_uscita == pytest.approx(100.9899, abs=1e-9)
    # il rischio iniziale resta quello dello stop iniziale 99,0099 (distanza 1,0001)
    assert t.stop_iniziale == pytest.approx(99.0099, abs=1e-12)
    # pnl = 99,990001 x (100,9899 - 100,01) - 5 - 99,990001 x 100,9899 x 0,0005 = 97,98 - 5 - 5,04900
    # -> R = 0,8793121
    assert t.r == pytest.approx(0.8793121188, abs=1e-8)


def test_u3_trailing_conta_il_massimo_della_candela_di_ingresso():
    """U3: il massimo "raggiunto dall'ingresso" comprende la candela di ingresso (SCELTA)."""
    righe = [SEG,
             (100.0, 104.0, 99.8, 103.5),   # 1 ingresso: max 104 -> 104 - 2 = 102 -> stop 102
             (103.5, 103.8, 101.9, 102.5),  # 2: minimo 101,9 <= 102 -> uscita a 102 x 0,9999
             P]
    s = candele(righe)
    t = sim(prepara(s, variante(uscite=[{"codice": "U3", "k": 2}]), segnali=[0], atr_trailing=1.0)).trade
    assert t.motivo == "trailing" and t.indice_uscita == 2
    assert t.prezzo_uscita == pytest.approx(101.9898, abs=1e-9)
    # R = (99,990001 x (101,9898 - 100,01) - 5 - 5,09898) / 100 = 1,8786122
    assert t.r == pytest.approx(1.8786122388, abs=1e-8)


def test_u3_trailing_short():
    """U3 short: stop = min(stop, minimo dall'ingresso + k x ATR)."""
    righe = [SEG,
             (100.0, 100.2, 99.0, 99.2),  # 1 ingresso 99,99, stop 100,9899: min 99 + 2 = 101 -> resta 100,9899
             (99.2, 99.5, 97.0, 97.5),    # 2: min 97 + 2 = 99 -> stop 99
             (97.5, 99.1, 97.2, 98.8),    # 3: massimo 99,1 >= 99 -> uscita a 99 x 1,0001 = 99,0099
             P]
    s = candele(righe)
    t = sim(prepara(s, variante("short", uscite=[{"codice": "U3", "k": 2}]), segnali=[0], atr_trailing=1.0)).trade
    assert t.motivo == "trailing" and t.indice_uscita == 3
    assert t.prezzo_uscita == pytest.approx(99.0099, abs=1e-9)
    # pnl = 100,010001 x (99,99 - 99,0099) - 5 - 100,010001 x 99,0099 x 0,0005 = 98,0198 - 5 - 4,95099
    assert t.r == pytest.approx(r_atteso(False, Q_SHORT, 99.99, 99.0099, 0.0005), rel=1e-12)
    assert t.r == pytest.approx(0.880688, abs=1e-5)


def test_u4_segnale_opposto_esce_all_apertura_dopo():
    """U4: quando alla chiusura di t e' vero il segnale opposto, uscita all'apertura di t+1."""
    righe = [SEG, P, P, P, (100.4, 100.5, 99.5, 100.0), P]
    s = candele(righe)
    t = sim(prepara(s, variante(uscite=[{"codice": "U4"}]), segnali=[0], opposti=[3])).trade
    assert t.motivo == "segnale_opposto"
    assert t.indice_uscita == 4 and t.ts_uscita == 4 * ORA
    # 100,4 x 0,9999 = 100,38996
    assert t.prezzo_uscita == pytest.approx(100.38996, abs=1e-9)
    assert t.candele_in_posizione == 3  # candele 1, 2, 3


# ---------------------------------------------------------------------------
# 7.7: ingresso limit (le 7 regole)
# ---------------------------------------------------------------------------


def test_limit_prezzo_esecuzione_al_limit_costi_maker():
    """7.7: prezzo = chiusura - k x ATR del segnale (long); regola 3: sempre il prezzo limit, anche
    se la candela apre oltre; regola 4: maker e niente slippage d'ingresso."""
    s = candele([P, (98.5, 99.5, 98.2, 99.2), (99.2, 101.5, 99.0, 101.0)])
    c = prepara(s, variante(tipo=limit()), segnali=[0], atr=[2.0, 7.0, 7.0])
    t = sim(c).trade
    # limit = 100 - 0,5 x 2 = 99 (ATR della candela del segnale); la candela 1 apre a 98,5 < 99 ma il
    # prezzo resta 99, mai migliore
    assert t.tipo_ingresso == "L"
    assert t.prezzo_ingresso == 99.0 and t.indice_ingresso == 1
    # stop S3 dal prezzo limit: 99 x 0,99 = 98,01; distanza 0,99; Q = 101,0101; valore 10.000
    assert t.stop_iniziale == pytest.approx(98.01, abs=1e-12)
    assert t.quantita == pytest.approx(Q_LIMIT, rel=1e-12)
    # target 99 + 2 x 0,99 = 100,98; nella candela 2 il massimo 101,5 lo tocca: 100,98 x 0,9999
    assert t.target == pytest.approx(100.98, abs=1e-12)
    assert t.motivo == "target" and t.indice_uscita == 2
    assert t.prezzo_uscita == pytest.approx(100.969902, abs=1e-9)
    # commissioni: maker 10.000 x 0,0002 = 2 + taker 101,0101 x 100,969902 x 0,0005 = 5,09949
    assert t.commissioni == pytest.approx(2.0 + 5.09949, abs=1e-6)
    # pnl = 101,0101 x (100,969902 - 99) - 7,09949 = 198,98 - 7,09949 = 191,88051 -> R 1,9188051
    assert t.r == pytest.approx(1.9188051, abs=1e-8)
    # short: limit = chiusura + k x ATR = 100 + 0,25 x 2 = 100,5; la candela apre a 100,6 (oltre):
    # prezzo 100,5
    s = candele([P, (100.6, 101.0, 100.2, 100.8), P])
    t = sim(prepara(s, variante("short", tipo=limit(k=0.25)), segnali=[0], atr=2.0)).trade
    assert t.prezzo_ingresso == 100.5
    # stop 100,5 x 1,01 = 101,505
    assert t.stop_iniziale == pytest.approx(101.505, abs=1e-12)
    assert t.commissioni > 0 and t.quantita * t.prezzo_ingresso == pytest.approx(10_000.0, rel=1e-12)


def test_limit_toccare_il_prezzo_non_basta():
    """7.7 regola 2: un long e' eseguito solo se il minimo scende SOTTO il limit; uno short solo se
    il massimo sale SOPRA. Toccarlo non basta."""
    v = variante(tipo=limit())
    s = candele([P, (99.5, 100.0, 99.0, 99.5), P])  # minimo = 99 = limit
    es = sim(prepara(s, v, segnali=[0], atr=2.0))
    assert es.tipo == "limite_non_eseguito" and es.libero_da == 1
    s = candele([P, (99.5, 100.0, 98.99, 99.5), P])  # minimo 98,99 < 99
    es = sim(prepara(s, v, segnali=[0], atr=2.0))
    assert es.tipo == "trade" and es.trade.prezzo_ingresso == 99.0
    vs = variante("short", tipo=limit(k=0.25))
    s = candele([P, (100.2, 100.5, 100.0, 100.3), P])  # massimo = 100,5 = limit
    assert sim(prepara(s, vs, segnali=[0], atr=2.0)).tipo == "limite_non_eseguito"
    s = candele([P, (100.2, 100.51, 100.0, 100.3), P])  # massimo 100,51 > 100,5
    es = sim(prepara(s, vs, segnali=[0], atr=2.0))
    assert es.tipo == "trade" and es.trade.prezzo_ingresso == 100.5


def test_limit_nella_candela_di_esecuzione_vale_solo_lo_stop():
    """7.7 regola 5 e 9.2 punto 2: nella candela di esecuzione conta solo lo stop; il target dalla
    candela dopo."""
    v = variante(tipo=limit())  # limit 99, stop 98,01, target 100,98
    # (a) la candela 1 esegue (minimo 98,5) e tocca il target (massimo 101,5): il target non conta;
    #     la candela 2 lo tocca (101,2) -> uscita al target nella candela 2
    s = candele([P, (99.5, 101.5, 98.5, 101.0), (101.0, 101.2, 100.5, 101.0), P])
    t = sim(prepara(s, v, segnali=[0], atr=2.0)).trade
    assert t.indice_ingresso == 1
    assert t.motivo == "target" and t.indice_uscita == 2
    # (b) la candela 1 esegue, tocca lo stop (97,9 <= 98,01) e il target: si chiude in perdita allo
    #     stop, anche con la regola intra-barra opposta
    s = candele([P, (99.5, 101.5, 97.9, 98.5), P])
    for regole in (Regole(), Regole(intrabarra="target_prima")):
        t = sim(prepara(s, v, segnali=[0], atr=2.0), regole=regole).trade
        assert t.motivo == "stop" and t.indice_uscita == 1
        assert t.prezzo_uscita == pytest.approx(98.01 * 0.9999, abs=1e-12)
    # (c) SCELTA: la candela di esecuzione apre gia' sotto lo stop (97,5): prezzo d'ingresso 99
    #     (regola 3) e uscita allo stop 98,01 x 0,9999 = 98,000199 (niente salto: si entra dentro)
    s = candele([P, (97.5, 99.2, 97.0, 98.0), P])
    t = sim(prepara(s, v, segnali=[0], atr=2.0)).trade
    assert t.prezzo_ingresso == 99.0 and t.motivo == "stop"
    assert t.prezzo_uscita == pytest.approx(98.000199, abs=1e-9)
    # pnl = 101,0101 x (98,000199 - 99) - 2 - 101,0101 x 98,000199 x 0,0005 = -100,99 - 2 - 4,9495
    assert t.r == pytest.approx(r_atteso(True, Q_LIMIT, 99.0, 98.000199, 0.0002), rel=1e-12)
    assert t.r == pytest.approx(-1.079396, abs=1e-5)


def test_limit_validita_e_cancellazione():
    """7.7 regola 1: ordine attivo dalla candela dopo il segnale per 1 o 3 candele; se non e'
    eseguito si cancella e il trade non c'e'."""
    righe = [P,
             (99.5, 100.0, 99.0, 99.5),   # 1: tocca soltanto 99
             (99.5, 99.8, 98.0, 99.0),    # 2: scende sotto 99
             P, P]
    s = candele(righe)
    # validita' 1: attivo solo nella candela 1 -> cancellato; la variante decide di nuovo alla
    # chiusura della candela 1
    es = sim(prepara(s, variante(tipo=limit(validita=1)), segnali=[0], atr=2.0))
    assert es.tipo == "limite_non_eseguito" and es.libero_da == 1
    # validita' 3: attivo nelle candele 1, 2, 3 -> eseguito nella 2
    es = sim(prepara(s, variante(tipo=limit(validita=3)), segnali=[0], atr=2.0))
    assert es.tipo == "trade" and es.trade.indice_ingresso == 2
    # validita' 3, eseguito alla terza candela attiva (la 3)
    righe3 = [P, (99.5, 100.0, 99.0, 99.5), (99.5, 100.0, 99.3, 99.5), (99.5, 100.0, 98.9, 99.5), P]
    es = sim(prepara(candele(righe3), variante(tipo=limit(validita=3)), segnali=[0], atr=2.0))
    assert es.tipo == "trade" and es.trade.indice_ingresso == 3
    # validita' 3, nessuna esecuzione nelle candele 1..3; la 4 scende sotto 99 ma l'ordine e' gia'
    # cancellato; si decide di nuovo alla chiusura della 3
    righe4 = [P, (99.5, 100.0, 99.0, 99.5), (99.5, 100.0, 99.3, 99.5), (99.5, 100.0, 99.1, 99.5),
              (99.0, 99.5, 98.0, 99.0), P]
    es = sim(prepara(candele(righe4), variante(tipo=limit(validita=3)), segnali=[0], atr=2.0))
    assert es.tipo == "limite_non_eseguito" and es.libero_da == 3


def _serie_ordine_in_attesa():
    """Segnali alle candele 0, 1, 2, 3; limit 99 (chiusura 100 - 0,5 x 2), validita' 3."""
    righe = [P,
             (100.0, 100.5, 99.0, 100.0),  # 1: segnale (da ignorare); tocca soltanto 99
             (100.0, 100.5, 99.2, 100.0),  # 2: segnale (da ignorare)
             (100.0, 100.5, 99.1, 100.0),  # 3: fine validita' del primo ordine; segnale -> nuovo ordine
             (99.5, 99.8, 98.5, 99.5),     # 4: eseguito il secondo ordine a 99
             (99.5, 101.2, 99.4, 101.0)]   # 5: target 100,98
    s = candele(righe)
    return prepara(s, variante(tipo=limit(validita=3)), segnali=[0, 1, 2, 3], atr=2.0)


def test_limit_ordine_in_attesa_ignora_i_nuovi_segnali():
    """7.7 regola 6: mentre l'ordine e' in attesa i nuovi segnali si ignorano; dopo la
    cancellazione (fine validita' alla candela 3) il segnale della candela 3 vale (9.2 punti 2 e 5)."""
    c = _serie_ordine_in_attesa()
    r = esegui(c)
    assert len(r.trade) == 1
    t = r.trade[0]
    # se il segnale della candela 1 non fosse ignorato, il suo ordine (attivo 2..4) sarebbe eseguito
    # nella 4 con indice_segnale 1
    assert (t.indice_segnale, t.indice_ingresso, t.indice_uscita, t.motivo) == (3, 4, 5, "target")
    assert r.contatori["segnali"] == 2
    assert r.contatori["ordini_inseriti"] == 2
    assert r.contatori["ordini_eseguiti"] == 1
    assert r.contatori["ordini_cancellati"] == 1
    # 9.7: ordini inseriti, eseguiti, cancellati e percentuale di esecuzione 1 / 2 = 50%
    m = metriche(r)
    assert (m["ordini_inseriti"], m["ordini_eseguiti"], m["ordini_cancellati"]) == (2, 1, 1)
    assert m["esecuzione"] == pytest.approx(0.5)


def test_limit_riempimento_severo():
    """Fase 4, verifica 8 (``scarto_riempimento`` = 0,0005): eseguito solo se il prezzo supera il
    limit di almeno lo 0,05%; il prezzo resta il limit."""
    severo = Regole(scarto_riempimento=0.0005)
    v = variante(tipo=limit())
    # long, limit 99: soglia 99 x 0,9995 = 98,9505
    s = candele([P, (99.5, 100.0, 98.96, 99.5), P])  # 98,96 < 99 ma > 98,9505
    assert sim(prepara(s, v, segnali=[0], atr=2.0)).tipo == "trade"
    assert sim(prepara(s, v, segnali=[0], atr=2.0), regole=severo).tipo == "limite_non_eseguito"
    s = candele([P, (99.5, 100.0, 98.95, 99.5), P])  # 98,95 < 98,9505
    es = sim(prepara(s, v, segnali=[0], atr=2.0), regole=severo)
    assert es.tipo == "trade" and es.trade.prezzo_ingresso == 99.0
    # short, limit 100,5: soglia 100,5 x 1,0005 = 100,55025
    vs = variante("short", tipo=limit(k=0.25))
    s = candele([P, (100.2, 100.55, 100.0, 100.3), P])
    assert sim(prepara(s, vs, segnali=[0], atr=2.0), regole=severo).tipo == "limite_non_eseguito"
    s = candele([P, (100.2, 100.56, 100.0, 100.3), P])
    es = sim(prepara(s, vs, segnali=[0], atr=2.0), regole=severo)
    assert es.tipo == "trade" and es.trade.prezzo_ingresso == 100.5


def test_limit_riempimento_severo_esattamente_allo_0_05_per_cento():
    """Fase 4, verifica 8: «eseguito solo se il prezzo supera il limit di ALMENO lo 0,05%».
    Limit 100 (chiusura 101 - 0,5 x 2); un minimo di 99,95 supera il limit esattamente dello 0,05%
    ((100 - 99,95) / 100 = 0,0005): per il testo l'ordine e' eseguito."""
    assert 100.0 * (1 - 0.0005) == 99.95  # la soglia del motore, in virgola mobile, e' proprio 99,95
    s = candele([(100.5, 101.5, 100.0, 101.0), (100.0, 100.5, 99.95, 100.2), P])
    es = sim(prepara(s, variante(tipo=limit()), segnali=[0], atr=2.0), regole=Regole(scarto_riempimento=0.0005))
    assert es.tipo == "trade"
    assert es.trade.prezzo_ingresso == 100.0


def test_limit_valori_della_variante():
    """7.7 regola 7: tipo d'ingresso, k e validita' fanno parte della variante e vengono dal
    catalogo (k 0,25 o 0,5; validita' 1 o 3)."""
    for k in (0.25, 0.5):
        for val in (1, 3):
            assert normalizza(variante(tipo=limit(k=k, validita=val)))["tipo_ingresso"] == {
                "codice": "L", "k": k, "validita": val, "atr": 14}
    with pytest.raises(VarianteNonValida):
        normalizza(variante(tipo=limit(k=0.3)))
    with pytest.raises(VarianteNonValida):
        normalizza(variante(tipo=limit(validita=2)))
    with pytest.raises(VarianteNonValida):
        normalizza(variante(tipo={"codice": "L", "k": 0.5, "validita": 1, "atr": 20}))


# ---------------------------------------------------------------------------
# 9.5: funding (candele da 12 ore: i regolamenti delle 08 e delle 16 cadono DENTRO una candela)
# ---------------------------------------------------------------------------

#: mark: apertura 100,0; 100,1; ...; 100,5 (diversa dal last, per vedere che si usa il mark)
MARK_APERTURE = [100.0, 100.1, 100.2, 100.3, 100.4, 100.5]
#: regolamenti ogni 8 ore (in ore dall'inizio) con i loro tassi
TASSI = {8: 0.0001, 16: 0.0002, 24: -0.0001, 32: 0.0003, 40: -0.0002, 48: 0.0001, 56: 0.0002, 64: -0.0001}


def serie_12h(righe=None, tassi=None):
    righe = righe or [P] * 6
    mark = [(m, m + 0.2, m - 0.2, m) for m in MARK_APERTURE[:len(righe)]]
    tassi = TASSI if tassi is None else tassi
    return candele(righe, tf="12h", mark=mark, funding=[(h * ORA, r) for h, r in sorted(tassi.items())])


def test_funding_regolamenti_pieni_long_e_short():
    """9.5: un regolamento T vale per le posizioni aperte prima e dopo T: valore x tasso, pagato dal
    long e ricevuto dallo short se il tasso e' positivo; il mark e' l'apertura della candela mark che
    contiene T (SCELTA)."""
    s = serie_12h()
    v = variante(tf="12h", uscite=[{"codice": "U4"}])
    # segnale alla candela 0 (00:00), ingresso all'apertura della 1 (12:00), uscita all'apertura della
    # 4 (48:00). Regolamenti in (12, 48]: 16, 24, 32, 40, 48 (non le 08 e non le 56)
    # somma mark x tasso: 100,1 x 0,0002 + 100,2 x (-0,0001) + 100,2 x 0,0003 + 100,3 x (-0,0002)
    #                   + 100,4 x 0,0001 = 0,02002 - 0,01002 + 0,03006 - 0,02006 + 0,01004 = 0,03004
    t = sim(prepara(s, v, segnali=[0], opposti=[3])).trade
    assert t.indice_ingresso == 1 and t.indice_uscita == 4
    # long: -99,990001 x 0,03004 = -3,0037
    assert t.funding == pytest.approx(-Q_LONG * 0.03004, abs=1e-9)
    assert t.funding == pytest.approx(-3.0037, abs=1e-4)
    # il funding entra nell'R (9.7): (-11,9988 - 3,0037) / 100 = -0,150025
    assert t.r == pytest.approx(r_atteso(True, Q_LONG, 100.01, 99.99, 0.0005, funding=-Q_LONG * 0.03004), rel=1e-12)
    assert t.r == pytest.approx(-0.150025, abs=1e-5)
    # short: +100,010001 x 0,03004 = +3,0043
    t = sim(prepara(s, variante("short", tf="12h", uscite=[{"codice": "U4"}]), segnali=[0], opposti=[3])).trade
    assert t.funding == pytest.approx(Q_SHORT * 0.03004, abs=1e-9)


def test_funding_ingresso_all_apertura_di_T_non_lo_paga():
    """9.5: chi entra all'apertura di una candela che inizia esattamente a T non paga quel funding."""
    s = serie_12h()
    # segnale alla 1, ingresso all'apertura della 2 (24:00 = T), uscita all'apertura della 3 (36:00)
    # regolamenti in (24, 36]: solo le 32 -> long: -99,990001 x 100,2 x 0,0003 = -99,990001 x 0,03006
    # (le 24, con tasso -0,0001, non contano: per il long sarebbero un incasso, per lo short un costo)
    t = sim(prepara(s, variante(tf="12h", uscite=[{"codice": "U4"}]), segnali=[1], opposti=[2]), i=1).trade
    assert t.ts_ingresso == 24 * ORA
    assert t.funding == pytest.approx(-Q_LONG * 0.03006, abs=1e-9)
    t = sim(prepara(s, variante("short", tf="12h", uscite=[{"codice": "U4"}]), segnali=[1], opposti=[2]), i=1).trade
    assert t.funding == pytest.approx(Q_SHORT * 0.03006, abs=1e-9)


def test_funding_uscita_all_apertura_di_T_lo_paga():
    """9.5: chi esce all'apertura di una candela che inizia esattamente a T paga (o riceve) quel
    funding."""
    s = serie_12h()
    # ingresso alla 1 (12:00), uscita all'apertura della 2 (24:00 = T). Regolamenti in (12, 24]: 16, 24
    # long: -99,990001 x (100,1 x 0,0002 + 100,2 x (-0,0001)) = -99,990001 x 0,01 = -0,9999
    t = sim(prepara(s, variante(tf="12h", uscite=[{"codice": "U4"}]), segnali=[0], opposti=[1])).trade
    assert t.ts_uscita == 24 * ORA
    assert t.funding == pytest.approx(-Q_LONG * 0.01, abs=1e-9)


def test_funding_uscita_per_stop_con_T_dentro_la_candela_solo_se_costo():
    """9.5: posizione chiusa per stop nella candela in cui cade T (dentro): conta solo se e' un costo.
    Le 24 cadono all'APERTURA della candela d'uscita (24-36): la posizione era aperta prima e dopo,
    contano sempre (SCELTA, vedi il rapporto). Le 32 cadono dentro."""
    righe_long = [P, P, (100.0, 100.2, 98.9, 99.0), P, P, P]  # stop long 99,0099 toccato nella 2
    v = variante(tf="12h", uscite=[{"codice": "U4"}])
    # tasso delle 32 positivo (+0,0003): per il long e' un costo -> conta
    # -99,990001 x (0,02002 - 0,01002 + 0,03006) = -99,990001 x 0,04006
    t = sim(prepara(serie_12h(righe_long), v, segnali=[0])).trade
    assert t.motivo == "stop" and t.indice_uscita == 2
    assert t.funding == pytest.approx(-Q_LONG * 0.04006, abs=1e-9)
    # tasso delle 32 negativo (-0,0003): per il long sarebbe un incasso -> non conta
    # -99,990001 x (0,02002 - 0,01002) = -99,990001 x 0,01; le 24 (incasso per il long) contano
    t = sim(prepara(serie_12h(righe_long, {**TASSI, 32: -0.0003}), v, segnali=[0])).trade
    assert t.funding == pytest.approx(-Q_LONG * 0.01, abs=1e-9)
    # short, stop 100,9899 toccato nella 2; tasso delle 32 negativo = costo per lo short -> conta:
    # 100,010001 x (0,02002 - 0,01002 + 100,2 x (-0,0003)) = 100,010001 x (-0,02006)
    righe_short = [P, P, (100.0, 101.1, 99.8, 101.0), P, P, P]
    vs = variante("short", tf="12h", uscite=[{"codice": "U4"}])
    t = sim(prepara(serie_12h(righe_short, {**TASSI, 32: -0.0003}), vs, segnali=[0])).trade
    assert t.motivo == "stop" and t.indice_uscita == 2
    assert t.funding == pytest.approx(Q_SHORT * -0.02006, abs=1e-9)
    # short, tasso delle 32 positivo = incasso per lo short -> non conta: 100,010001 x 0,01
    t = sim(prepara(serie_12h(righe_short), vs, segnali=[0])).trade
    assert t.funding == pytest.approx(Q_SHORT * 0.01, abs=1e-9)


def test_funding_uscita_per_target_con_T_dentro_la_candela_solo_se_costo():
    """9.5: lo stesso per il target. Short con target 97,9902 toccato nella candela 2 (24-36)."""
    righe = [P, P, (100.0, 100.3, 97.9, 98.0), P, P, P]
    vs = variante("short", tf="12h")  # U1 k = 2
    # tasso delle 32 positivo: per lo short e' un incasso -> non conta: 100,010001 x 0,01
    t = sim(prepara(serie_12h(righe), vs, segnali=[0])).trade
    assert t.motivo == "target" and t.indice_uscita == 2
    assert t.funding == pytest.approx(Q_SHORT * 0.01, abs=1e-9)
    # tasso delle 32 negativo: per lo short e' un costo -> conta: 100,010001 x (0,01 - 0,03006)
    t = sim(prepara(serie_12h(righe, {**TASSI, 32: -0.0003}), vs, segnali=[0])).trade
    assert t.funding == pytest.approx(Q_SHORT * -0.02006, abs=1e-9)


def test_funding_ingresso_limit_con_T_dentro_la_candela_solo_se_costo():
    """9.5: ordine limit eseguito nella candela in cui cade T: conta solo se e' un costo. Segnale alla
    1 (12-24), limit 99 attivo dalla 2 (24-36), eseguito nella 2; uscita all'apertura della 4 (48)."""
    righe = [P, P, (99.5, 100.0, 98.9, 99.5), P, P, P]
    v = variante(tf="12h", tipo=limit(), uscite=[{"codice": "U4"}])
    # le 24 cadono all'apertura della candela di esecuzione: l'ordine e' eseguito dopo T -> non conta,
    # anche se e' un costo (tasso +0,0005 per il long, SCELTA coerente con «chi entra non paga»)
    # le 32 (dentro): tasso +0,0003 = costo -> conta; le 40 e le 48 contano piene
    # -101,0101 x (100,2 x 0,0003 + 100,3 x (-0,0002) + 100,4 x 0,0001) = -101,0101 x 0,02004
    tassi = {**TASSI, 24: 0.0005}
    t = sim(prepara(serie_12h(righe, tassi), v, segnali=[1], opposti=[3], atr=2.0), i=1).trade
    assert t.tipo_ingresso == "L" and t.indice_ingresso == 2 and t.indice_uscita == 4
    assert t.funding == pytest.approx(-Q_LIMIT * 0.02004, abs=1e-9)
    # le 32 con tasso -0,0003 = incasso per il long -> non conta
    # -101,0101 x (100,3 x (-0,0002) + 100,4 x 0,0001) = -101,0101 x (-0,01002) = +1,0121
    t = sim(prepara(serie_12h(righe, {**tassi, 32: -0.0003}), v, segnali=[1], opposti=[3], atr=2.0), i=1).trade
    assert t.funding == pytest.approx(Q_LIMIT * 0.01002, abs=1e-9)


# ---------------------------------------------------------------------------
# 9.4: dimensione, leva e liquidazione
# ---------------------------------------------------------------------------


def test_leva_massima_riduce_la_dimensione_e_conta_il_trade():
    """9.4: un trade che supererebbe la leva massima si riduce fino alla leva massima e si conta."""
    s = candele([SEG, (100.0, 100.4, 99.7, 100.0), (100.0, 100.2, 99.5, 99.8)])
    v = variante(stop={"codice": "S1", "k": 1.0})
    c = prepara(s, v, segnali=[0], atr_stop=0.4)
    # stop 100,01 - 0,4 = 99,61 (0,39996%); Q voluta 100 / 0,4 = 250, valore 25.002,5 > 10.000 x 2
    # -> Q = 20.000 / 100,01 = 199,980002; rischio 199,980002 x 0,4 = 79,992001
    t = sim(c).trade
    assert t.ridotto
    assert t.quantita == pytest.approx(20_000 / 100.01, rel=1e-12)
    assert t.rischio_usdt == pytest.approx(79.992001, abs=1e-6)
    # stop nella 2 a 99,61 x 0,9999 = 99,600039
    # pnl = 199,98 x (99,600039 - 100,01) - 199,98 x 100,01 x 0,0005 - 199,98 x 99,600039 x 0,0005
    #     = -81,9845 - 10 - 9,9590 = -101,9430; R = pnl / rischio iniziale in USDT = -1,274415
    assert t.r == pytest.approx(r_atteso(True, 20_000 / 100.01, 100.01, 99.61 * 0.9999, 0.0005,
                                          rischio=20_000 / 100.01 * 0.4), rel=1e-12)
    assert t.r == pytest.approx(-1.2744150, abs=1e-6)
    assert metriche(Risultato([t], 0, 2, {}))["ridotti"] == 1
    # con leva 5: valore 25.002,5 <= 50.000 -> non ridotto, Q = 250, rischio 100
    t = sim(c, regole=Regole(leva_max=5)).trade
    assert not t.ridotto and t.quantita == pytest.approx(250.0) and t.rischio_usdt == pytest.approx(100.0)


def test_prezzo_di_liquidazione_formula_binance():
    """9.4: margine isolato di Binance. Long, importo di mantenimento 0: EP x (1 - 1/L) / (1 - mmr);
    short: EP x (1 + 1/L) / (1 + mmr)."""
    # long EP 100, L 5, mmr 0,004: 100 x 0,8 / 0,996 = 80,3213
    assert prezzo_liquidazione(True, 100.0, 1.0, 5.0, 0.004) == pytest.approx(100 * 0.8 / 0.996, rel=1e-12)
    assert prezzo_liquidazione(True, 100.0, 1.0, 5.0, 0.004) == pytest.approx(80.3212851, abs=1e-6)
    # short: 100 x 1,2 / 1,004 = 119,5219
    assert prezzo_liquidazione(False, 100.0, 1.0, 5.0, 0.004) == pytest.approx(119.5219124, abs=1e-6)
    # non dipende dalla quantita'
    assert prezzo_liquidazione(True, 100.0, 7.0, 5.0, 0.004) == pytest.approx(80.3212851, abs=1e-6)
    # con importo di mantenimento 0,5 (Q = 1, margine 20): long (20 + 0,5 - 100) / (0,004 - 1) = 79,8193
    assert prezzo_liquidazione(True, 100.0, 1.0, 5.0, 0.004, 0.5) == pytest.approx(79.5 / 0.996, rel=1e-12)
    # short (20 + 0,5 + 100) / (0,004 + 1) = 120,0199
    assert prezzo_liquidazione(False, 100.0, 1.0, 5.0, 0.004, 0.5) == pytest.approx(120.5 / 1.004, rel=1e-12)


def test_violazione_della_distanza_di_liquidazione():
    """9.4: la distanza dello stop deve essere al massimo 0,8 volte quella della liquidazione; ogni
    violazione si conta. Con leva 50 (solo per il test): liquidazione long a
    100,01 x 0,98 / 0,996 = 98,40353, distanza 1,60647, 0,8 x = 1,28518."""
    s = candele([SEG, P, P])
    regole = Regole(leva_max=50)
    # S3 2%: distanza 2,0002 > 1,28518 -> violazione
    t2 = sim(prepara(s, variante(stop={"codice": "S3", "pct": 0.02}), segnali=[0]), regole=regole).trade
    assert t2.violazione_liquidazione
    # S3 1%: distanza 1,0001 <= 1,28518 -> nessuna violazione
    t1 = sim(prepara(s, variante(), segnali=[0]), regole=regole).trade
    assert not t1.violazione_liquidazione
    # con la leva 2 del bot: liquidazione a 100,01 x 0,5 / 0,996 = 50,206; nessuna violazione
    assert not sim(prepara(s, variante(stop={"codice": "S3", "pct": 0.02}), segnali=[0])).trade.violazione_liquidazione
    assert metriche(Risultato([t2, t1], 0, 2, {}))["violazioni_liquidazione"] == 1


def test_liquidazione_sul_mark_price():
    """9.1 e 9.4: la liquidazione si controlla sul mark price (SCELTA: prima dello stop). Leva 50,
    S3 2%: stop 98,0098, liquidazione 98,40353. Nella candela 2 il mark scende a 98,3, il last no."""
    last = [SEG, P, (100.0, 100.2, 99.5, 99.8)]
    mark = [SEG, P, (100.0, 100.2, 98.3, 99.8)]
    s = candele(last, mark=mark)
    t = sim(prepara(s, variante(stop={"codice": "S3", "pct": 0.02}), segnali=[0]), regole=Regole(leva_max=50)).trade
    assert t.motivo == "liquidazione" and t.indice_uscita == 2
    assert t.prezzo_uscita == pytest.approx(100.01 * 0.98 / 0.996, rel=1e-12)
    # Q = 100 / 2,0002; valore 5.000; margine 5.000 / 50 = 100; commissione d'ingresso 2,5
    # pnl = -100 - 2,5 = -102,5 -> R = -1,025
    assert t.r == pytest.approx(-1.025, abs=1e-9)


# ---------------------------------------------------------------------------
# 9.6: buchi nei dati
# ---------------------------------------------------------------------------


def test_buco_la_posizione_lo_attraversa_e_alla_prima_candela_vale_il_salto():
    """9.6: una posizione aperta attraversa il buco; alla prima candela disponibile si applica il
    controllo del salto di prezzo."""
    ts = [0, ORA, 2 * ORA, 5 * ORA, 6 * ORA]  # mancano le candele delle 3 e delle 4
    righe = [SEG, P, (100.0, 100.4, 99.6, 100.0), (98.0, 98.5, 97.5, 98.2), P]
    s = candele(righe, ts=ts)
    t = sim(prepara(s, variante(), segnali=[0])).trade
    # la candela delle 5 apre a 98 < stop 99,0099 -> uscita 98 x 0,9999 = 97,9902
    assert t.motivo == "stop_salto" and t.indice_uscita == 3 and t.ts_uscita == 5 * ORA
    assert t.prezzo_uscita == pytest.approx(97.9902, abs=1e-9)
    assert t.candele_in_posizione == 2


def test_buco_subito_dopo_il_segnale_niente_trade():
    """SCELTA: se manca la candela dopo il segnale, il trade non c'e'."""
    ts = [0, ORA, 2 * ORA, 5 * ORA, 6 * ORA]
    s = candele([SEG, P, SEG, P, P], ts=ts)
    c = prepara(s, variante(), segnali=[2])
    assert sim(c, i=2).tipo == "senza_candela"
    r = esegui(c)
    assert r.trade == [] and r.contatori["senza_candela"] == 1


def test_buco_il_riscaldamento_riparte():
    """9.6 e 7.8: dopo un buco nessun nuovo segnale finche' il riscaldamento non e' di nuovo
    completo. E3 n = 20 con S3: riscaldamento 20 candele (periodo pieno del Donchian)."""
    n = 60
    ts = [k * ORA if k < 30 else (k + 5) * ORA for k in range(n)]  # buco di 5 ore dopo la candela 29
    righe = [P] * n
    righe[35] = (100.0, 105.5, 99.5, 105.0)  # rottura del Donchian dentro il riscaldamento
    # rottura dopo il riscaldamento: chiusura 106 > massimo delle 20 candele prima (105,5 della 35)
    righe[55] = (100.0, 106.5, 99.5, 106.0)
    c = compila(variante(), candele(righe, ts=ts))
    assert c.riscaldamento == 20
    # primo tratto 0..29: ammesse dalla 20; secondo tratto dalla 30: ammesse dalla 50
    assert not c.ammessa[19] and c.ammessa[20] and c.ammessa[29]
    assert not c.ammessa[30:50].any() and c.ammessa[50:].all()
    assert c.dettagli["ingresso"][35] and not c.segnale[35]
    assert c.segnale[55]


# ---------------------------------------------------------------------------
# 7.8 e 9.2: una posizione alla volta, quando si decide di nuovo
# ---------------------------------------------------------------------------


def test_una_posizione_alla_volta_e_nuova_decisione_alla_chiusura_della_candela_di_uscita():
    """7.8: con una posizione aperta i segnali si ignorano. 9.2: uno stop dentro la candela t chiude
    la posizione al punto 1, quindi al punto 5 della stessa candela si puo' entrare di nuovo."""
    righe = [SEG,
             (100.0, 100.5, 99.5, 100.2),
             (100.2, 100.6, 99.6, 100.0),  # 2: segnale ignorato (posizione aperta)
             (100.0, 100.2, 98.5, 99.0),   # 3: stop 99,0099; segnale alla chiusura -> vale
             (99.0, 99.5, 98.7, 99.2),     # 4: ingresso 99 x 1,0001 = 99,0099; stop 98,018801
             (99.2, 101.2, 99.0, 101.0)]   # 5: target 99,0099 + 2 x 0,990099 = 100,990098
    s = candele(righe)
    c = prepara(s, variante(), segnali=[0, 2, 3])
    r = esegui(c)
    assert [(t.indice_segnale, t.indice_ingresso, t.indice_uscita, t.motivo) for t in r.trade] == [
        (0, 1, 3, "stop"), (3, 4, 5, "target")]
    assert r.contatori["segnali"] == 2
    assert r.trade[1].prezzo_ingresso == pytest.approx(99.0099, abs=1e-12)
    assert r.trade[1].target == pytest.approx(100.990098, abs=1e-9)
    # 9.7: tempo in posizione = (3 + 2) candele su 6 = 83,33%; trade al mese = 2 / (6 ore in mesi)
    m = metriche(r, s)
    assert m["tempo_in_posizione"] == pytest.approx(5 / 6)
    assert m["trade_al_mese"] == pytest.approx(2 / (6 / (24 * 365.25 / 12)))


def test_uscita_programmata_blocca_il_segnale_della_stessa_candela():
    """9.2 punto 5: niente nuovo ingresso con un'uscita programmata (U4 alla chiusura della 2, uscita
    all'apertura della 3); alla chiusura della 3 si decide di nuovo."""
    s = candele([SEG, P, P, P, P, P])
    c = prepara(s, variante(uscite=[{"codice": "U4"}]), segnali=[0, 2, 3], opposti=[2])
    r = esegui(c)
    assert [(t.indice_segnale, t.indice_ingresso, t.indice_uscita) for t in r.trade] == [(0, 1, 3), (3, 4, 5)]
    assert r.trade[0].motivo == "segnale_opposto"


# ---------------------------------------------------------------------------
# 9.7: metriche
# ---------------------------------------------------------------------------


def _ms(anno, mese, giorno):
    return int(dt.datetime(anno, mese, giorno, tzinfo=dt.timezone.utc).timestamp() * 1000)


def trade_finto(r, ts_uscita, candele_pos=1):
    return Trade("M", 0, 1, ts_uscita, 100.0, 99.0, None, 2, ts_uscita, 100.0, "stop", 1.0, 100.0, 0.0,
                 0.0, r * 100.0, r, False, False, candele_pos)


def test_metriche_calcolate_a_mano():
    """9.7: numero di trade, R medio, profit factor, % vincenti, R medio di vincenti e perdenti,
    drawdown massimo in R (somma cumulata), somma degli R per anno solare, contatori dei limit."""
    r = [2.0, -1.0, -1.0, 0.5, -1.5, 3.0]
    anni = [_ms(2021, 3, 1), _ms(2021, 6, 1), _ms(2021, 12, 31), _ms(2022, 1, 1), _ms(2022, 3, 1), _ms(2022, 9, 1)]
    ris = Risultato([trade_finto(x, a) for x, a in zip(r, anni)], 0, 99,
                    {"ordini_inseriti": 4, "ordini_eseguiti": 3, "ordini_cancellati": 1})
    m = metriche(ris)
    assert m["trade"] == 6
    # R medio = (2 - 1 - 1 + 0,5 - 1,5 + 3) / 6 = 2 / 6 = 0,3333
    assert m["r_medio"] == pytest.approx(1 / 3)
    # profit factor = (2 + 0,5 + 3) / (1 + 1 + 1,5) = 5,5 / 3,5 = 1,5714
    assert m["profit_factor"] == pytest.approx(5.5 / 3.5)
    # vincenti 3 su 6 = 50%
    assert m["vincenti"] == pytest.approx(0.5)
    # R medio vincenti 5,5 / 3 = 1,8333; perdenti -3,5 / 3 = -1,1667
    assert m["r_medio_vincenti"] == pytest.approx(5.5 / 3)
    assert m["r_medio_perdenti"] == pytest.approx(-3.5 / 3)
    # somma cumulata 2, 1, 0, 0,5, -1, 2; picco 2 -> drawdown massimo -3
    assert m["drawdown_max_r"] == pytest.approx(-3.0)
    # per anno (dall'uscita): 2021 = 2 - 1 - 1 = 0; 2022 = 0,5 - 1,5 + 3 = 2
    assert m["r_per_anno"] == {2021: pytest.approx(0.0), 2022: pytest.approx(2.0)}
    # limit: 4 inseriti, 3 eseguiti, 1 cancellato -> esecuzione 75%
    assert (m["ordini_inseriti"], m["ordini_eseguiti"], m["ordini_cancellati"]) == (4, 3, 1)
    assert m["esecuzione"] == pytest.approx(0.75)


def test_drawdown_e_profit_factor_casi_limite():
    # somma cumulata 1, -1, 2, 1, 0; picchi 1, 1, 2, 2, 2 -> drawdown -2
    assert drawdown_r([1.0, -2.0, 3.0, -1.0, -1.0]) == pytest.approx(-2.0)
    # il picco parte da 0: due perdite di 1 R -> -2
    assert drawdown_r([-1.0, -1.0]) == pytest.approx(-2.0)
    assert drawdown_r([]) == 0.0
    assert profit_factor([1.0, 2.0]) == float("inf")
    assert profit_factor([]) == 0.0
    assert profit_factor([-1.0, 0.5]) == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# 8.4: stima dei trade
# ---------------------------------------------------------------------------


def test_stima_trade_solo_conteggi_e_per_i_limit_solo_gli_eseguiti():
    """8.4: si contano i trade senza calcolarne il risultato; per i limit contano solo gli ordini
    eseguiti. Sulla serie con un ordine cancellato e uno eseguito: 1 trade."""
    c = _serie_ordine_in_attesa()
    st = stima_trade(c)
    assert st == {"trade": 1, "long": 1, "short": 0, "ordini_inseriti": 2, "ordini_eseguiti": 1}
    assert all(isinstance(x, int) for x in st.values())


# ---------------------------------------------------------------------------
# 9.8: test di troncamento
# ---------------------------------------------------------------------------

VARIANTE_TRONCAMENTO = {
    "timeframe": "1h", "direzione": "long",
    "filtro": {"codice": "F1", "n": 50, "lato": "sopra"},
    "ingresso": {"codice": "E1", "media": "EMA", "veloce": 9, "lenta": 20},
    "conferma": None,
    "tipo_ingresso": {"codice": "L", "k": 0.5, "validita": 3},
    "stop": {"codice": "S1", "k": 1.5},
    "uscite": [{"codice": "U1", "k": 2}, {"codice": "U3", "k": 2}],
}


def passeggiata(n=400, seme=7):
    rng = np.random.default_rng(seme)
    c = 100 * np.exp(np.cumsum(rng.normal(0, 0.01, n)))
    o = np.r_[100.0, c[:-1]]
    h = np.maximum(o, c) * (1 + rng.uniform(0, 0.004, n))
    l = np.minimum(o, c) * (1 - rng.uniform(0, 0.004, n))
    funding = [(k * 8 * ORA, 0.0001) for k in range(1, n // 8)]
    return candele(list(zip(o, h, l, c)), funding=funding)


def test_troncamento_variante_causale_nessuna_differenza():
    """9.8: 200 istanti, seme 2026: indicatori e segnali con i soli dati fino all'istante coincidono
    con quelli sull'intera serie."""
    s = passeggiata()
    c = compila(VARIANTE_TRONCAMENTO, s)
    assert c.segnale.sum() > 0 and c.opposto.sum() > 0  # la prova ha segnali da confrontare
    assert motore3.test_troncamento(VARIANTE_TRONCAMENTO, s, 0, len(s) - 1) == []


def test_troncamento_trova_un_lookahead(monkeypatch):
    """9.8: il test deve poter fallire. Una EMA che guarda il futuro (media centrata) cambia i
    segnali vicino alla fine della serie troncata: il test di troncamento la trova."""

    def ema_centrata(x, n):
        x = np.asarray(x, dtype=np.float64)
        meta = n // 2
        return np.array([x[max(0, i - meta): i + meta + 1].mean() for i in range(len(x))])

    s = passeggiata()
    monkeypatch.setattr(catalogo3, "ema", ema_centrata)
    differenze = motore3.test_troncamento(VARIANTE_TRONCAMENTO, s, 0, len(s) - 1)
    assert differenze, "il test di troncamento non ha visto la EMA che guarda il futuro"
    assert any("'segnale'" in d or "'opposto'" in d for d in differenze)


# ---------------------------------------------------------------------------
# 9.9: test del ritardo
# ---------------------------------------------------------------------------


def test_ritardo_di_una_candela_a_mercato():
    """9.9: con ``ritardo=1`` il segnale alla chiusura di t entra all'apertura di t+2."""
    righe = [SEG, (100.5, 101.0, 100.0, 100.6), (101.0, 101.5, 100.5, 101.0), P]
    s = candele(righe)
    c = prepara(s, variante(stop={"codice": "S1", "k": 1.5}), segnali=[0], atr_stop=[2.0, 9.0, 9.0, 9.0])
    t = sim(c, regole=Regole(ritardo=1)).trade
    # ingresso 101 x 1,0001 = 101,0101 alla candela 2; stop con l'ATR del segnale: 101,0101 - 3
    assert t.indice_ingresso == 2 and t.ts_ingresso == 2 * ORA
    assert t.prezzo_ingresso == pytest.approx(101.0101, abs=1e-12)
    assert t.stop_iniziale == pytest.approx(98.0101, abs=1e-12)
    # senza ritardo: candela 1, 100,5 x 1,0001
    t = sim(c).trade
    assert t.indice_ingresso == 1 and t.prezzo_ingresso == pytest.approx(100.51005, abs=1e-12)


def test_ritardo_di_una_candela_con_ingresso_limit():
    """9.9 con il limit: l'ordine e' attivo dalla candela t+2 (validita' 1)."""
    righe = [P, (99.5, 99.8, 98.0, 99.0), (99.0, 99.5, 98.5, 99.0), P]
    s = candele(righe)
    c = prepara(s, variante(tipo=limit()), segnali=[0], atr=2.0)
    # senza ritardo: eseguito nella candela 1 (98,0 < 99)
    assert sim(c).trade.indice_ingresso == 1
    # con ritardo: la candela 1 non conta; eseguito nella 2 (98,5 < 99) al prezzo 99
    t = sim(c, regole=Regole(ritardo=1)).trade
    assert t.indice_ingresso == 2 and t.prezzo_ingresso == 99.0
