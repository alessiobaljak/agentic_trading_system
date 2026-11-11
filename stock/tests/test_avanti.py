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


def test_plancia_componi_forma_della_guida():
    from stock.avanti import plancia as pl
    ordini = [{"simbolo": "BRK.B", "lato": "buy", "quantita": 10, "stop": 99, "obiettivo": 120, "riferimento": 101, "id": "o1"}]
    es = [{"symbol": "BRK.B", "side": "buy", "qty": "10", "price": "101", "transaction_time": "t1", "order_id": "o1"},
          {"symbol": "BRK.B", "side": "sell", "qty": "10", "price": "103", "transaction_time": "t2", "order_id": "x"}]
    diario = pd.DataFrame(av.operazioni_del_giorno("2026-11-09", ordini, es, {}), columns=av.COLONNE)
    storia = {"timestamp": [int(pd.Timestamp("2026-11-06 05:00", tz="UTC").timestamp()),
                            int(pd.Timestamp("2026-11-09 05:00", tz="UTC").timestamp())], "equity": [100000, 100020]}
    d = pl.componi({"equity": "100020"}, [{"symbol": "BRK.B", "qty": "-5", "market_value": "-500"}], storia, diario,
                   {"giorno": "2026-11-09", "ordini": [{"inviato": "2026-11-09T09:45:30-05:00"}]}, 1_794_000_000.0)
    s = d["strategie"][pl.ID]
    assert s["pesi"] == {"BRK_B": pytest.approx(-0.005, abs=1e-4)} and s["vendute"] == 1 and s["comprate"] == 0
    assert s["giorni"] == {"2026-11-09": 100020}                      # prima del primo giorno della misura non si mostra
    assert s["rendimento"] == pytest.approx(0.0002) and s["tipo"] == "demo"
    assert s["operazioni"]["2026-11-09"][0]["guadagno"] == pytest.approx(20)
    assert s["ultimo_ribilancio"]["entrate"] == 1 and d["allarmi"] is None
    json_ok = __import__("json").dumps(d)                             # niente NaN o tipi che Firebase non accetta
    assert "NaN" not in json_ok


def test_miscela_regole():
    from datetime import date
    import numpy as np
    from stock.avanti import miscela as mi
    c = pd.Series(100 * np.cumprod(1 + np.r_[0, [0.01, -0.01] * 15]))
    v = float(c.iloc[-22:].pct_change().dropna().std(ddof=1) * np.sqrt(252))
    assert mi.quota_calma(c) == pytest.approx(min(0.16 / v, 1.5))
    sale = pd.Series(np.arange(1, 251, dtype=float))
    scende = pd.Series(np.arange(250, 0, -1, dtype=float))
    assert mi.ampiezza({"A": sale, "B": scende, "C": sale.iloc[:100]}) == pytest.approx(0.5)
    cal = [date(2026, 12, 7), date(2026, 12, 8), date(2026, 12, 9), date(2026, 12, 10)]
    assert mi.giorni_fed(date(2026, 12, 8), cal[1:]) == "vigilia" and mi.giorni_fed(date(2026, 12, 9), cal[2:]) == "giorno"
    assert mi.giorni_fed(date(2026, 12, 7), cal) is None
    stato = {"fed": 1.0, "calma": {"SPY": 1.5, "QQQ": 0.0}, "ampiezza": 0.49}
    e = mi.esposizione(stato)
    assert e["SPY"] == pytest.approx((0.98 + 1.47 + 0.49) / 6) and e["QQQ"] == pytest.approx((0.98 + 0.49) / 6)
    d = mi.ordini(60_000, {"SPY": 0.5, "QQQ": 0.0}, {"SPY": 500.0, "QQQ": 400.0}, {"SPY": 59, "QQQ": 10})
    assert d == {"QQQ": -10}                        # SPY: 60 voluti contro 59, sotto la soglia; QQQ a zero si chiude sempre
