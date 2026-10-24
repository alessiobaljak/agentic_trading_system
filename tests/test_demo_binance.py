"""G1 sul conto demo di Binance (bot/portafoglio/demo_binance.py) con un Binance finto: solo l'indirizzo demo, gli ordini giusti."""
from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

import pytest

from bot.portafoglio import demo_binance as dm


class _Risposta:
    def __init__(self, dati, codice=200):
        self.dati, self.status_code, self.text = dati, codice, json.dumps(dati)

    def json(self):
        return self.dati


class _Demo:
    """Il conto demo finto: 10.000 USDT, due monete, gli ordini limite si eseguono solo su AUSDT."""

    def __init__(self):
        self.chiamate = []
        self.posizioni = {"AUSDT": 0.0, "BUSDT": 0.0}
        self.ordini = {}

    def __call__(self, metodo, url, headers=None, timeout=None):
        u = urlparse(url)
        assert u.hostname == "demo-fapi.binance.com"
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        self.chiamate.append((metodo, u.path, q))
        if u.path == "/fapi/v1/exchangeInfo":
            return _Risposta({"symbols": [{"symbol": s, "filters": [
                {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
                {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
                {"filterType": "MIN_NOTIONAL", "notional": "5"}]} for s in ("AUSDT", "BUSDT")]})
        if u.path == "/fapi/v1/premiumIndex":
            return _Risposta([{"symbol": "AUSDT", "markPrice": "100.003"}, {"symbol": "BUSDT", "markPrice": "50.007"}])
        if u.path == "/fapi/v2/account":
            return _Risposta({"totalMarginBalance": "10000", "totalWalletBalance": "10000",
                              "positions": [{"symbol": s, "positionAmt": str(v)} for s, v in self.posizioni.items()]})
        if u.path == "/fapi/v1/positionSide/dual":
            return _Risposta({"dualSidePosition": False} if metodo == "GET" else {"code": 200})
        if u.path == "/fapi/v1/leverage":
            return _Risposta({"leverage": int(q["leverage"])})
        if u.path == "/fapi/v1/order" and metodo == "POST":
            i = len(self.ordini) + 1
            self.ordini[i] = dict(q, orderId=i)
            return _Risposta({"orderId": i})
        if u.path == "/fapi/v1/order" and metodo == "GET":
            o = self.ordini[int(q["orderId"])]
            pieno = o["symbol"] == "AUSDT"
            return _Risposta({"status": "FILLED" if pieno else "NEW", "executedQty": o["quantity"] if pieno else "0"})
        if u.path == "/fapi/v1/order" and metodo == "DELETE":
            return _Risposta({"status": "CANCELED"})
        raise AssertionError(u.path)


def test_solo_l_indirizzo_demo():
    assert dm._url("/fapi/v1/order").startswith("https://demo-fapi.binance.com/")
    vecchio = dm.DEMO
    try:
        dm.DEMO = "https://fapi.binance.com"
        with pytest.raises(ValueError):
            dm._url("/fapi/v1/order")
    finally:
        dm.DEMO = vecchio


def test_arrotondamenti_e_numeri():
    assert dm.arrotonda(0.123456, 0.001) == 0.123 and dm.arrotonda(100.003, 0.01, "su") == 100.01
    assert dm.testo(0.00001) == "0.00001" and dm.testo(5.0) == "5"


def test_ordini_del_giorno():
    f = {"AUSDT": (0.01, 0.001, 0.001, 5.0), "BUSDT": (0.01, 0.001, 0.001, 5.0)}
    o = dm.ordini_del_giorno({"AUSDT": 0.5, "BUSDT": -0.5}, {"AUSDT": 0.0}, {"AUSDT": 100.0, "BUSDT": 50.0}, 10_000.0, f)
    assert o == [("AUSDT", "BUY", 50.0, 100.0, False), ("BUSDT", "SELL", 100.0, 50.0, False)]
    # chiudere una posizione che non e' piu' nei pesi: riduce
    o = dm.ordini_del_giorno({}, {"AUSDT": 10.0}, {"AUSDT": 100.0}, 10_000.0, f)
    assert o == [("AUSDT", "SELL", 10.0, 100.0, True)]
    # sotto il valore minimo: niente
    assert dm.ordini_del_giorno({"AUSDT": 0.0001}, {}, {"AUSDT": 100.0}, 10_000.0, f) == []


def test_decisione_di_g1_sul_demo(tmp_path):
    from bot.core.firebase_client import _InMemoryStore
    fb = _InMemoryStore()
    finto = _Demo()
    acceso = tmp_path / "acceso"
    acceso.write_text("si")
    g1 = tmp_path / "g1.json"
    g1.write_text(json.dumps({"ultimo_lunedi": 20750, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d = dm.DemoG1(fb, cliente=dm.ClienteDemo("chiave", "segreto", http=finto), file_stato=tmp_path / "st.json", file_g1=g1,
                  interruttore=acceso)
    d.tick(20750 * 86400.0 + 400)
    st = d.carica()
    assert st["ultimo_giorno"] == 20750 and len(st["ordini"]["lista"]) == 2
    post = [q for m, p, q in finto.chiamate if m == "POST" and p == "/fapi/v1/order"]
    assert {q["symbol"]: (q["side"], q["type"], q["quantity"], q["price"]) for q in post} == {
        "AUSDT": ("BUY", "LIMIT", "49.998", "100"), "BUSDT": ("SELL", "LIMIT", "99.986", "50.01")}
    assert all("signature" in q and "timestamp" in q for m, p, q in finto.chiamate if p.startswith("/fapi/v1/order"))
    # un'ora dopo: AUSDT eseguito a limite, BUSDT annullato e fatto a mercato
    d.tick(20750 * 86400.0 + 400 + 3601)
    st = d.carica()
    assert "ordini" not in st and st["limite_eseguiti"] == 1 and st["a_mercato"] == 1
    mercato = [q for m, p, q in finto.chiamate if m == "POST" and p == "/fapi/v1/order" and q["type"] == "MARKET"]
    assert mercato == [{"symbol": "BUSDT", "side": "SELL", "type": "MARKET", "quantity": "99.986", **{k: mercato[0][k] for k in ("timestamp", "recvWindow", "signature")}}]
    assert fb.get_rtdb("/demo_binance/stato")["equity"] == 10000.0


def test_senza_chiave_non_chiama_binance(tmp_path, monkeypatch):
    from bot.core.firebase_client import _InMemoryStore
    fb = _InMemoryStore()
    monkeypatch.delenv("BINANCE_DEMO_API_KEY", raising=False)
    acceso = tmp_path / "acceso"
    acceso.write_text("si")
    d = dm.DemoG1(fb, file_stato=tmp_path / "st.json", file_g1=tmp_path / "g1.json", interruttore=acceso)
    d.tick(1_800_000_000.0)
    assert fb.get_rtdb("/demo_binance/stato")["stato"].startswith("manca la chiave")
