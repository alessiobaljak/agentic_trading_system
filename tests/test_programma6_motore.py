"""Il motore dei backtest del programma 6 (research/programma6/motore.py)."""
import numpy as np
import pandas as pd
import pytest

from research.programma6 import motore as mo


def _b(o, h, l, c):
    n = len(c)
    return pd.DataFrame({"open": o, "high": h, "low": l, "close": c, "funding_cum": np.zeros(n),
                         "minuto": np.arange(n) * 60})


def _segnali(n, lunghi=(), corti=()):
    sl, ss = np.zeros(n, bool), np.zeros(n, bool)
    sl[list(lunghi)] = True
    ss[list(corti)] = True
    return {"long": sl, "short": ss}


def test_ingresso_alla_apertura_dopo_e_stop():
    # segnale alla chiusura della barra 0; ingresso all'apertura della 1 a 100; stop a 2 ATR (ATR 1) = 98
    b = _b([100, 100, 100, 99], [100, 101, 100, 99], [100, 99.5, 97, 98], [100, 100, 98, 98.5])
    t = mo.simula(b, np.ones(4), _segnali(4, [0]), stop_k=2)
    assert len(t["R"]) == 1 and t["motivo"][0] == 0
    assert t["prezzo_in"][0] == 100 and t["prezzo_out"][0] == 98
    assert t["costo"][0] == pytest.approx(2 * (0.0005 + 0.0002))
    assert t["R"][0] == pytest.approx((-0.02 - 0.0014) / 0.02)


def test_obiettivo_e_stop_nella_stessa_barra_vale_lo_stop():
    b = _b([100, 100, 100], [100, 100, 104], [100, 100, 97], [100, 100, 100])
    t = mo.simula(b, np.ones(3), _segnali(3, [0]), stop_k=2, tp_k=3)
    assert t["motivo"][0] == 0


def test_obiettivo_a_limite_senza_scarto():
    b = _b([100, 100, 100], [100, 101, 104], [100, 99.5, 99], [100, 100, 103])
    t = mo.simula(b, np.ones(3), _segnali(3, [0]), stop_k=2, tp_k=3)
    assert t["motivo"][0] == 1 and t["prezzo_out"][0] == 103
    assert t["costo"][0] == pytest.approx(0.0005 + 0.0002 + 0.0002)


def test_ordine_limite_solo_ad_attraversamento():
    # limite a chiusura 100 - 1 ATR = 99: la barra 1 tocca 99 (niente), la barra 2 va a 98.9 (eseguito a 99)
    b = _b([100, 100, 99.5, 99.5, 99.5], [100, 100.5, 99.8, 101, 101],
           [100, 99, 98.9, 99.2, 99.2], [100, 99.6, 99.2, 100.5, 100.8])
    t = mo.simula(b, np.ones(5), _segnali(5, [0]), stop_k=5, limite_k=1, validita=3, max_barre=2)
    assert t["ingresso_i"][0] == 2 and t["prezzo_in"][0] == 99
    assert t["costo"][0] == pytest.approx(0.0002 + 0.0005 + 0.0002)


def test_stop_che_segue_e_uscita_per_segnale():
    c = [100, 100, 103, 106, 104, 104]
    b = _b(c, [x + 0.5 for x in c], [x - 0.5 for x in c], c)
    t = mo.simula(b, np.ones(6), _segnali(6, [0]), stop_k=3, trail_k=1)
    # stop iniziale 97; dopo la barra 3 lo stop sale a 105; la barra 4 apre gia' sotto (104): uscita all'apertura, «segue»
    assert t["motivo"][0] == 2 and t["prezzo_out"][0] == pytest.approx(104)
    s = _segnali(6, [0])
    s["esci_long"] = np.array([False, False, True, False, False, False])
    t2 = mo.simula(b, np.ones(6), s, stop_k=3)
    assert t2["motivo"][0] == 4 and t2["uscita_i"][0] == 3 and t2["prezzo_out"][0] == 106


def test_finestre_scelgono_solo_con_trade_chiusi_e_vicini():
    from research.programma6 import finestre as fi
    combo = [{"famiglia": "rottura", "segnali": {"N": 20, "filtro": "nessuno"}, "uscita": {}, "iu": 0, "tf": "1h",
              "ingresso": {}, "ii": 0},
             {"famiglia": "rottura", "segnali": {"N": 55, "filtro": "nessuno"}, "uscita": {}, "iu": 0, "tf": "1h",
              "ingresso": {}, "ii": 0}]
    vic = fi.vicini(combo)
    assert vic == [[1], [0]]
    da, a = fi._minuto(2020, 1), fi._minuto(2021, 1)
    rng = np.random.default_rng(1)
    righe = []
    for k, media in ((0, 0.3), (1, 0.1)):
        for i in range(150):
            m = da + i * 2000
            righe.append({"k": k, "simbolo": f"S{i % 5}USDT", "minuto": m, "uscita": m + 60, "R": media + rng.normal(0, 0.01)})
    # un trade enorme della combinazione 1 che entra prima e chiude DOPO la fine della finestra: non conta
    righe.append({"k": 1, "simbolo": "S0USDT", "minuto": a - 100, "uscita": a + 10, "R": 1000.0})
    tr = pd.DataFrame(righe)
    assert fi.scegli(tr, combo, vic, da, a) == 0


def test_pbo_basso_quando_la_migliore_resta_migliore():
    from research.programma6 import finestre as fi
    righe = []
    base = fi._minuto(2021, 1)
    for mese in range(32):
        for k in range(6):
            righe.append({"k": k, "minuto": base + mese * 31 * 1440, "R": 0.1 * k + 0.01 * ((mese * 7 + k) % 3)})
    assert fi.pbo(pd.DataFrame(righe), 6, blocchi=8) < 0.1
