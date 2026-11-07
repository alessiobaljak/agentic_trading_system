"""La misura in avanti: le regole pure, su casi costruiti a mano (nessun collegamento al conto)."""
import math

import pandas as pd
import pytest

from stock.avanti import avanti as av

NY = "America/New_York"


def _minuti(prezzi, inizio="2026-11-09 09:30"):
    idx = pd.date_range(pd.Timestamp(inizio, tz=NY), periods=len(prezzi), freq="min").tz_convert("UTC")
    return pd.DataFrame({"open": prezzi, "high": [p + 0.1 for p in prezzi], "low": [p - 0.1 for p in prezzi], "close": prezzi},
                        index=idx)


def test_candela_e_piano_di_acquisto():
    df = _minuti([100 + 0.1 * i for i in range(20)])
    c = av.candela(df, pd.Timestamp("2026-11-09 09:30", tz=NY))
    assert c["open"] == pytest.approx(100) and c["close"] == pytest.approx(101.4)
    assert c["low"] == pytest.approx(99.9) and c["high"] == pytest.approx(101.5)
    p = av.piano(c, 100_000)
    assert p["lato"] == "buy" and p["stop"] == pytest.approx(99.9)
    assert p["obiettivo"] == pytest.approx(101.4 + 10 * 1.5)
    assert p["quantita"] == math.floor(0.98 * 10_000 / 101.4)


def test_candela_incompleta_e_vendita():
    df = _minuti([100 - 0.1 * i for i in range(20)])
    assert av.candela(df.iloc[1:], pd.Timestamp("2026-11-09 09:30", tz=NY)) is None
    assert av.candela(df.iloc[:14], pd.Timestamp("2026-11-09 09:30", tz=NY)) is None
    p = av.piano(av.candela(df, pd.Timestamp("2026-11-09 09:30", tz=NY)), 100_000)
    assert p["lato"] == "sell" and p["stop"] == pytest.approx(100.1)


def test_operazioni_del_giorno_con_stop_e_saltati():
    ordini = [{"simbolo": "AAA", "lato": "buy", "quantita": 10, "stop": 99, "obiettivo": 120, "riferimento": 101, "id": "o1"},
              {"simbolo": "BBB", "nota": "saltato: rifiutato"}]
    es = [{"symbol": "AAA", "side": "buy", "qty": "10", "price": "101", "transaction_time": "t1", "order_id": "o1"},
          {"symbol": "AAA", "side": "sell", "qty": "10", "price": "99", "transaction_time": "t2", "order_id": "g1"}]
    r = av.operazioni_del_giorno("2026-11-09", ordini, es, {"g1": "stop"})
    assert r[0]["guadagno"] == pytest.approx(-20) and r[0]["uscita"] == "stop"
    assert r[0]["commissione_ib"] == pytest.approx(2.0)
    assert r[1]["nota"].startswith("saltato")
    a = av.riassunto(pd.DataFrame(r, columns=av.COLONNE))
    assert a["operazioni"] == 1 and a["saltate"] == 1 and a["dollari"] == pytest.approx(-20)


def test_vendita_allo_scoperto_chiusa_a_fine_giornata():
    ordini = [{"simbolo": "AAA", "lato": "sell", "quantita": 5, "stop": 110, "obiettivo": 50, "riferimento": 100, "id": "o1"}]
    es = [{"symbol": "AAA", "side": "sell_short", "qty": "5", "price": "100", "transaction_time": "t1", "order_id": "o1"},
          {"symbol": "AAA", "side": "buy", "qty": "5", "price": "98", "transaction_time": "t2", "order_id": "x"}]
    r = av.operazioni_del_giorno("2026-11-09", ordini, es, {})
    assert r[0]["guadagno"] == pytest.approx(10) and r[0]["uscita"] == "chiusura"
