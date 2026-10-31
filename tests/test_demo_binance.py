"""G1 sul conto demo di Binance (bot/portafoglio/demo_binance.py) con un Binance finto: solo l'indirizzo demo, gli ordini giusti."""
from __future__ import annotations

import json
import re
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

    PREZZI = {"AUSDT": "100.003", "BUSDT": "50.007", "CUSDT": "2.0", "BTCUSDT": "100000.0"}

    def __init__(self, simboli=("AUSDT", "BUSDT")):
        self.chiamate = []
        self.simboli = tuple(simboli)
        self.posizioni = {s: 0.0 for s in self.simboli}
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
                {"filterType": "MIN_NOTIONAL", "notional": "5"}]} for s in self.simboli]})
        if u.path == "/fapi/v1/premiumIndex":
            return _Risposta([{"symbol": s, "markPrice": self.PREZZI[s]} for s in self.simboli])
        if u.path == "/fapi/v2/account":
            return _Risposta({"totalMarginBalance": "10000", "totalWalletBalance": "10000",
                              "positions": [{"symbol": s, "positionAmt": str(v)} for s, v in self.posizioni.items()]})
        if u.path == "/fapi/v1/positionSide/dual":
            return _Risposta({"dualSidePosition": False} if metodo == "GET" else {"code": 200})
        if u.path == "/fapi/v1/leverage":
            return _Risposta({"leverage": int(q["leverage"])})
        if u.path == "/fapi/v1/openOrders":
            return _Risposta([{"symbol": o["symbol"]} for o in self.ordini.values() if not o.get("chiuso") and o["type"] == "LIMIT"])
        if u.path == "/fapi/v1/allOpenOrders":
            for o in self.ordini.values():
                if o["symbol"] == q["symbol"]:
                    o["chiuso"] = True
            return _Risposta({"code": 200})
        if u.path == "/fapi/v1/order" and metodo == "POST":
            if not re.fullmatch(r"[.A-Z:/a-z0-9_-]{1,36}", q.get("newClientOrderId", "x")):
                return _Risposta({"code": -1100, "msg": "Illegal characters found in parameter 'newclientorderid'"}, 400)
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


def test_firma_dei_tre_tipi_di_chiave(tmp_path, monkeypatch):
    """La chiave generata dal sistema (HMAC) e quelle generate da sé (Ed25519, RSA) firmano in modo verificabile."""
    import base64
    import hashlib
    import hmac
    from urllib.parse import unquote

    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa

    q = "symbol=BTCUSDT&timestamp=1"
    assert dm.firmatore("segreto")(q) == hmac.new(b"segreto", q.encode(), hashlib.sha256).hexdigest()
    pem = lambda k: k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,  # noqa: E731
                                    serialization.NoEncryption()).decode()
    ke = ed25519.Ed25519PrivateKey.generate()
    ke.public_key().verify(base64.b64decode(unquote(dm.firmatore(pem(ke))(q))), q.encode())
    kr = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    kr.public_key().verify(base64.b64decode(unquote(dm.firmatore(pem(kr))(q))), q.encode(), padding.PKCS1v15(), hashes.SHA256())
    f = tmp_path / "demo.pem"
    f.write_text(pem(ke))
    monkeypatch.setenv("BINANCE_DEMO_PRIVATE_KEY_PATH", str(f))
    assert dm.segreto_dall_ambiente().startswith("-----BEGIN")
    monkeypatch.delenv("BINANCE_DEMO_PRIVATE_KEY_PATH")
    monkeypatch.setenv("BINANCE_DEMO_API_SECRET", pem(ke).replace("\n", "\\n"))
    assert "\n" in dm.segreto_dall_ambiente()


def test_sezione_del_conto_demo_nello_stato():
    from scripts import state_snapshot as ss

    class Fb:
        def __init__(self, d):
            self.d = d

        def get_rtdb(self, k):
            return self.d.get(k)

    assert "spento" in ss.sezione_demo_binance(Fb({}))[1]
    righe = ss.sezione_demo_binance(Fb({"/demo_binance/stato": {"stato": "acceso", "equity": 5010.0, "capitale_iniziale": 5000.0,
                                                                "rendimento": 0.002, "long": 20, "short": 20, "aggiornato": 1.7e9},
                                        "/demo_binance/ribilanciamenti": {"2026-10-24": {"ordini": 40, "limite": {"eseguiti_a_limite": 38,
                                                                                                                  "a_mercato": 2}}},
                                        "/demo_binance/errore": {"testo": "GET x: 401", "ora": 1.7e9}}))
    testo = "\n".join(righe)
    assert "acceso" in testo and "$5,010.00" in testo and "eseguiti a limite 38" in testo and "401" in testo


def test_id_degli_ordini_e_ordini_rimasti_aperti(tmp_path):
    """Il 24 ottobre Binance ha rifiutato l'ordine di una moneta con il nome in caratteri cinesi e il ribilancio si e' fermato:
    l'identificativo ora e' sempre ammesso, un rifiuto non ferma gli altri e gli ordini rimasti aperti si annullano prima."""
    from bot.core.firebase_client import _InMemoryStore
    assert dm.id_ordine(20750, "AUSDT", 1_792_800_400) == "g1d-20750-400-AUSDT"
    assert dm.id_ordine(20750, "AUSDT", 1) != dm.id_ordine(20750, "AUSDT", 2)          # un altro tentativo, un altro identificativo
    i = dm.id_ordine(20750, "币安人生USDT", 99_999)
    assert re.fullmatch(r"[.A-Z:/a-z0-9_-]{1,36}", i) and i != dm.id_ordine(20750, "别的USDT", 99_999)
    assert len(dm.id_ordine(20750, "1000000BABYDOGEUSDT", 99_999)) <= 36
    fb = _InMemoryStore()
    finto = _Demo()
    finto.ordini[99] = {"symbol": "AUSDT", "type": "LIMIT", "quantity": "1", "orderId": 99}        # rimasto da un tentativo
    acceso = tmp_path / "acceso"
    acceso.write_text("si")
    g1 = tmp_path / "g1.json"
    g1.write_text(json.dumps({"ultimo_lunedi": 20750, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d = dm.DemoG1(fb, cliente=dm.ClienteDemo("chiave", "segreto", http=finto), file_stato=tmp_path / "st.json", file_g1=g1,
                  interruttore=acceso)
    d.tick(20750 * 86400.0 + 400)
    assert finto.ordini[99].get("chiuso") and len(d.carica()["ordini"]["lista"]) == 2
    rib = fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24") or fb.get_rtdb("/demo_binance/ribilanciamenti")
    assert "AUSDT" in str(rib)


def test_pesi_degli_eventi():
    aperte = {"E4-CUSDT-20261031": {"tipo": "E4", "simbolo": "CUSDT"}, "N3-AUSDT-20261031": {"tipo": "N3", "simbolo": "AUSDT"}}
    w = dm.pesi_eventi(aperte)
    assert w == {"CUSDT": -0.05, "AUSDT": -0.05, "BTCUSDT": 0.10}
    assert dm.somma_pesi({"AUSDT": 0.5, "BUSDT": -0.5}, w) == {"AUSDT": 0.45, "BUSDT": -0.5, "CUSDT": -0.05, "BTCUSDT": 0.10}
    assert dm.somma_pesi({"AUSDT": 0.05}, {"AUSDT": -0.05}) == {}


def _demo_con_eventi(tmp_path, finto, aperte, eventi_accesi=True):
    from bot.core.firebase_client import _InMemoryStore
    fb = _InMemoryStore()
    (tmp_path / "acceso").write_text("si")
    if eventi_accesi:
        (tmp_path / "eventi_acceso").write_text("si")
    (tmp_path / "eventi.json").write_text(json.dumps({"aperte": aperte}))
    g1 = tmp_path / "g1.json"
    g1.write_text(json.dumps({"ultimo_lunedi": 20750, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d = dm.DemoG1(fb, cliente=dm.ClienteDemo("chiave", "segreto", http=finto), file_stato=tmp_path / "st.json", file_g1=g1,
                  interruttore=tmp_path / "acceso", file_eventi=tmp_path / "eventi.json",
                  interruttore_eventi=tmp_path / "eventi_acceso")
    return d, fb


def test_eventi_accanto_a_g1_nel_ribilancio_del_giorno(tmp_path):
    """Il proprietario, 31 ottobre: «ok aggiungi gli eventi sul demo accanto a G1». Un'operazione a eventi aperta si somma ai pesi
    di G1: short la moneta e long il Bitcoin per il 5% del conto."""
    finto = _Demo(("AUSDT", "BUSDT", "CUSDT", "BTCUSDT"))
    d, _ = _demo_con_eventi(tmp_path, finto, {"E4-CUSDT-20261031": {"tipo": "E4", "simbolo": "CUSDT"}})
    d.tick(20750 * 86400.0 + 400)
    post = {q["symbol"]: (q["side"], q["quantity"]) for m, p, q in finto.chiamate if m == "POST" and p == "/fapi/v1/order"}
    assert post["CUSDT"] == ("SELL", "250") and post["BTCUSDT"] == ("BUY", "0.005") and set(post) == {"AUSDT", "BUSDT", "CUSDT", "BTCUSDT"}
    assert d.carica()["eventi_firma"] == ["E4-CUSDT-20261031"]


def test_eventi_che_cambiano_dopo_g1_toccano_solo_le_loro_monete(tmp_path):
    finto = _Demo(("AUSDT", "BUSDT", "CUSDT", "BTCUSDT"))
    d, fb = _demo_con_eventi(tmp_path, finto, {})
    d.tick(20750 * 86400.0 + 400)                     # G1 del giorno, nessun evento
    d.tick(20750 * 86400.0 + 400 + 3601)              # dopo l'ora: gli ordini di G1 chiusi
    prima = len(finto.chiamate)
    (tmp_path / "eventi.json").write_text(json.dumps({"aperte": {"N3-CUSDT-20261031": {"tipo": "N3", "simbolo": "CUSDT"}}}))
    d.tick(20750 * 86400.0 + 400 + 7300)              # il paper apre un evento: solo CUSDT e il Bitcoin
    nuovi = [q["symbol"] for m, p, q in finto.chiamate[prima:] if m == "POST" and p == "/fapi/v1/order"]
    assert sorted(nuovi) == ["BTCUSDT", "CUSDT"]
    st = d.carica()
    assert st["ultimo_giorno"] == 20750 and st["eventi_firma"] == ["N3-CUSDT-20261031"] and "-eventi-" in st["ordini"]["chiave"]
    assert fb.get_rtdb(f"/demo_binance/ribilanciamenti/{st['ordini']['chiave']}")["solo_eventi"] is True


def test_eventi_spenti_non_cambiano_niente(tmp_path):
    finto = _Demo(("AUSDT", "BUSDT", "CUSDT", "BTCUSDT"))
    d, _ = _demo_con_eventi(tmp_path, finto, {"E4-CUSDT-20261031": {"tipo": "E4", "simbolo": "CUSDT"}}, eventi_accesi=False)
    d.tick(20750 * 86400.0 + 400)
    post = {q["symbol"] for m, p, q in finto.chiamate if m == "POST" and p == "/fapi/v1/order"}
    assert post == {"AUSDT", "BUSDT"} and d.carica()["eventi_firma"] == []

