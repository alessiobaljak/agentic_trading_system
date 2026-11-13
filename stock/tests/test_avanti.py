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


def test_cosa_fare_a_ogni_ora():
    t = lambda h: pd.Timestamp(f"2026-11-12 {h}", tz=NY)  # noqa: E731
    sed = {"apertura": t("09:30"), "chiusura": t("16:00")}
    f = av.cosa_fare
    assert f(t("03:00"), sed, False, False, False).startswith("niente: troppo presto")
    assert f(t("04:30"), sed, False, False, False) == "apri"            # avvio in anticipo: aspetta le 9:45
    assert f(t("09:58"), sed, False, False, False) == "apri"
    assert f(t("10:01"), sed, False, False, False).startswith("niente: oggi nessun ordine")   # in ritardo: mai entrare
    assert f(t("15:08"), sed, False, False, False).startswith("niente")                        # l'errore dell'11 novembre
    assert f(t("09:47"), sed, True, True, False).startswith("niente: troppo presto per la chiusura")
    assert f(t("10:40"), sed, True, True, False) == "chiudi"            # aspetta le 15:55
    assert f(t("15:58"), sed, True, False, False) == "chiudi"
    assert f(t("12:00"), sed, False, True, False) == "chiudi_subito"    # posizioni rimaste da un altro giorno: via subito
    assert f(t("07:40"), sed, False, True, False) == "fuori_orario"     # prima dell'apertura: ordini fuori orario
    assert f(t("16:03"), sed, True, True, False) == "fuori_orario"      # mai un ordine a mercato a seduta finita
    assert f(t("20:27"), sed, True, False, False) == "diario" and f(t("20:27"), sed, True, False, True).startswith("niente")
    assert f(t("11:00"), None, False, False, False).startswith("niente: oggi la borsa è chiusa")


def test_conto_condiviso_divide_il_guadagno_fra_le_due_strategie():
    from stock.avanti import conto
    diario = pd.DataFrame({"giorno": ["2026-11-12", "2026-11-13", "2026-11-13"], "guadagno": [500.0, 100.0, -40.0]})
    pos = [{"symbol": "SPY", "unrealized_pl": "300"}, {"symbol": "AAPL", "unrealized_pl": "-25"}]
    assert conto.valori(100_500.0, pos, diario, None) == (100_500.0, None)         # prima della partenza: tutto della prima candela
    stato = {"dal": "2026-11-12", "conto_alla_partenza": 100_500.0, "candela_alla_partenza": 100_500.0}
    candela, miscela = conto.valori(100_835.0, pos, diario, stato)
    assert candela == pytest.approx(100_500 + 60 - 25)                              # il 12 è già nella fotografia
    assert miscela == pytest.approx(100_000 + 335 - 35)                             # il resto della variazione del conto
    pc, pm = conto.separa(pos)
    assert [p["symbol"] for p in pc] == ["AAPL"] and [p["symbol"] for p in pm] == ["SPY"]
    # oggi, prima che il diario sia scritto: comprate 10 AAPL a 100, 4 già uscite allo stop a 99, le altre 6 valgono 101
    es = [{"symbol": "AAPL", "side": "buy", "qty": "10", "price": "100"}, {"symbol": "AAPL", "side": "sell", "qty": "4", "price": "99"},
          {"symbol": "SPY", "side": "buy", "qty": "5", "price": "600"}]
    aperte = [{"symbol": "AAPL", "market_value": "606", "unrealized_pl": "6"}, {"symbol": "SPY", "market_value": "3010"}]
    candela, miscela = conto.valori(100_502.0, aperte, diario, stato, oggi="2026-11-16", esecuzioni_oggi=es)
    assert candela == pytest.approx(100_500 + 60 + (-1000 + 396 + 606))             # +2: lo stop già preso conta
    assert miscela == pytest.approx(100_000 + 2 - 62)


def test_miscela_cosa_fare_a_ogni_ora():
    from datetime import date
    from stock.avanti import miscela as mi
    t = lambda g, h: pd.Timestamp(f"2026-12-{g:02d} {h}", tz=NY)  # noqa: E731
    sed = [{"giorno": date(2026, 12, g), "apertura": t(g, "09:30"), "chiusura": t(g, "16:00")} for g in (7, 8, 9, 10, 11)]
    st = {"fed": 0.0, "calma": {"SPY": 1.0, "QQQ": 1.0}, "ampiezza": 0.98, "ultima_sera": "2026-12-07"}
    f = lambda adesso, stato=st: mi.cosa_fare(adesso, sed, stato)[0]  # noqa: E731
    assert f(t(8, "08:30")).startswith("niente")                        # la sera del 7 è fatta, per la banca centrale è presto
    assert f(t(8, "09:00")) == "fed" and f(t(8, "14:10")) == "fed"      # vigilia del 9 dicembre: aspetta le 14:00
    assert f(t(8, "14:30")).startswith("niente: troppo tardi")
    assert f(t(8, "16:30")).startswith("niente: troppo presto per la sera")    # non resta acceso: esce, ci pensa un avvio dopo
    assert f(t(8, "19:05")) == "sera"                                   # dalle 19:00 Alpaca accetta gli ordini all'apertura
    assert f(t(9, "02:00")) == "sera" and f(t(9, "09:20")).startswith("niente: troppo tardi")   # fino a 15 minuti dall'apertura
    dentro = dict(st, fed=1.0, ultima_sera="2026-12-08")
    assert f(t(9, "10:00"), dentro) == "fed"                            # giorno del comunicato: vende alle 13:59
    assert f(t(9, "15:30"), dentro) == "fed"                            # l'uscita non si salta mai: in ritardo si vende subito
    assert f(t(10, "10:00"), dict(dentro, ultima_sera="2026-12-09")).startswith("niente")   # e se è mancata, la sera ha già venduto
    assert f(t(9, "10:00"), dict(st, ultima_sera="2026-12-08")).startswith("niente: la borsa è aperta")
    assert f(t(8, "16:30"), dict(st, ultima_sera="2026-12-08")).startswith("niente: la sera è già fatta")


def test_miscela_ordini_della_sera_solo_day_e_nome_nuovo():
    from stock.avanti import miscela as mi
    aperti = [{"id": "1", "client_order_id": "miscela-sera-2026-11-12-SPY", "time_in_force": "opg"},
              {"id": "2", "client_order_id": "miscela-sera-2026-11-12-g-QQQ", "time_in_force": "day"},
              {"id": "3", "client_order_id": "miscela-sera-2026-11-11-g-SPY", "time_in_force": "day"}]
    assert [o["id"] for o in mi.ordini_della_sera(aperti, "2026-11-12")] == ["2"]
    assert mi.TIF_SERA == "day" and mi.NOME_SERA.format(giorno="2026-11-12") == "sera-2026-11-12-g"


def test_miscela_un_ordine_scaduto_con_lo_stesso_nome_non_conta_come_mandato(monkeypatch):
    from stock import dati
    from stock.avanti import avanti as av
    from stock.avanti import miscela as mi

    def rifiuta(*a, **k):
        raise dati.alpaca.ErroreAlpaca("422 client_order_id must be unique")
    monkeypatch.setattr(av, "_richiesta", rifiuta)
    monkeypatch.setattr(av, "_ordine_per_nome", lambda nome: {"status": "expired"})
    fatti, bene = mi.manda({"SPY": 37}, "day", "sera-2026-11-12")
    assert not bene and "RIFIUTATO" in fatti[0]
    monkeypatch.setattr(av, "_ordine_per_nome", lambda nome: {"status": "accepted"})
    fatti, bene = mi.manda({"SPY": 37}, "day", "sera-2026-11-12")
    assert bene and "già mandato" in fatti[0]
