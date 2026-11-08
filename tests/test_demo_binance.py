"""G1 sul conto demo di Binance (bot/portafoglio/demo_binance.py) con un Binance finto: solo l'indirizzo demo, gli ordini giusti."""
from __future__ import annotations

import json
import re
import time
from urllib.parse import parse_qs, urlparse

import pytest

from bot.portafoglio import demo_binance as dm


class _Risposta:
    def __init__(self, dati, codice=200, headers=None):
        self.dati, self.status_code, self.text = dati, codice, json.dumps(dati)
        self.headers = headers or {}

    def json(self):
        return self.dati


def _rifiutata():
    """Una richiesta rifiutata da Binance. Fino al 7 novembre i test usavano un 429; dal problema 13 della revisione
    (reviews/reports/2026-11-07-primo-avvio.md) un 429 non e' piu' un rifiuto ma si riprova, e dal problema 44 (8 novembre) nemmeno
    l'errore d'orario -1021: qui un rifiuto qualunque."""
    return _Risposta({"code": -1000, "msg": "An unknown error occurred while processing the request."}, 400)


class _Demo:
    """Il conto demo finto: 10.000 USDT, due monete, gli ordini limite si eseguono solo su AUSDT."""

    PREZZI = {"AUSDT": "100.003", "BUSDT": "50.007", "CUSDT": "2.0", "BTCUSDT": "100000.0"}

    def __init__(self, simboli=("AUSDT", "BUSDT")):
        self.chiamate = []
        self.simboli = tuple(simboli)
        self.posizioni = {s: 0.0 for s in self.simboli}
        self.ordini = {}
        self.equity = "10000"
        self.separati = set()
        self.margine = {}
        self.entrate = []                               # righe di /fapi/v1/income: (tipo, ms, importo, valuta)
        self.posizioni_vive = False                     # se vero, gli ordini a mercato e i limite di AUSDT muovono le posizioni
        self.guasti = {}                                # (metodo, percorso, simbolo) -> eccezione o risposta, una volta sola
        self.guasti_dopo = {}                           # simbolo -> eccezione DOPO aver eseguito l'ordine (risposta persa)
        self.scarto_ora_ms = 0                          # l'orologio di Binance avanti di tanto su quello della macchina

    def __call__(self, metodo, url, headers=None, timeout=None):
        u = urlparse(url)
        assert u.hostname == "demo-fapi.binance.com"
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        self.chiamate.append((metodo, u.path, q))
        guasto = self.guasti.pop((metodo, u.path, q.get("symbol")), None)
        if isinstance(guasto, Exception):
            raise guasto
        if guasto is not None:
            return guasto
        if u.path == "/fapi/v1/time":
            return _Risposta({"serverTime": int(time.time() * 1000) + self.scarto_ora_ms})
        if u.path == "/fapi/v1/exchangeInfo":
            return _Risposta({"symbols": [{"symbol": s, "filters": [
                {"filterType": "PRICE_FILTER", "tickSize": "0.01"},
                {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
                {"filterType": "MIN_NOTIONAL", "notional": "5"}]} for s in self.simboli]})
        if u.path == "/fapi/v1/premiumIndex":
            return _Risposta([{"symbol": s, "markPrice": self.PREZZI[s]} for s in self.simboli])
        if u.path == "/fapi/v2/account":
            return _Risposta({"totalMarginBalance": self.equity, "totalWalletBalance": self.equity,
                              "positions": [{"symbol": s, "positionAmt": str(v), "isolated": s in self.separati}
                                            for s, v in self.posizioni.items()]})
        if u.path == "/fapi/v1/marginType":
            if q["symbol"] not in self.separati and q["symbol"] in self.margine:
                return _Risposta({"code": -4046, "msg": "No need to change margin type."}, 400)
            self.margine[q["symbol"]] = q["marginType"]
            self.separati.discard(q["symbol"])
            return _Risposta({"code": 200, "msg": "success"})
        if u.path == "/fapi/v1/income":
            da, a = int(q["startTime"]), int(q["endTime"])
            righe = [{"incomeType": t, "time": ms, "income": str(v), "asset": val} for t, ms, v, val in self.entrate
                     if t == q["incomeType"] and da <= ms <= a]
            return _Risposta(righe[: int(q["limit"])])
        if u.path == "/fapi/v1/positionSide/dual":
            return _Risposta({"dualSidePosition": False} if metodo == "GET" else {"code": 200})
        if u.path == "/fapi/v1/leverage":
            return _Risposta({"leverage": int(q["leverage"])})
        if u.path == "/fapi/v1/openOrders":
            return _Risposta([{"symbol": o["symbol"]} for o in self.ordini.values()
                              if not o.get("chiuso") and not o.get("eseguito") and o["type"] == "LIMIT"])
        if u.path == "/fapi/v1/allOpenOrders":
            for o in self.ordini.values():
                if o["symbol"] == q["symbol"]:
                    o["chiuso"] = True
            return _Risposta({"code": 200})
        if u.path == "/fapi/v1/order" and metodo == "POST":
            if not re.fullmatch(r"[.A-Z:/a-z0-9_-]{1,36}", q.get("newClientOrderId", "x")):
                return _Risposta({"code": -1100, "msg": "Illegal characters found in parameter 'newclientorderid'"}, 400)
            i = len(self.ordini) + 1
            self.ordini[i] = dict(q, orderId=i, eseguito=q["type"] == "LIMIT" and q["symbol"] == "AUSDT")
            if self.posizioni_vive and (q["type"] == "MARKET" or q["symbol"] == "AUSDT"):
                segno = 1.0 if q["side"] == "BUY" else -1.0
                self.posizioni[q["symbol"]] = round(self.posizioni.get(q["symbol"], 0.0) + segno * float(q["quantity"]), 10)
            dopo = self.guasti_dopo.pop(q["symbol"], None)
            if dopo is not None:
                raise dopo
            return _Risposta({"orderId": i})
        if u.path == "/fapi/v1/order" and metodo == "GET":
            if "origClientOrderId" in q:
                trovati = [o for o in self.ordini.values() if o.get("newClientOrderId") == q["origClientOrderId"]]
                if not trovati:
                    return _Risposta({"code": -2013, "msg": "Order does not exist."}, 400)
                return _Risposta({"orderId": trovati[0]["orderId"], "status": "FILLED"})
            o = self.ordini[int(q["orderId"])]
            pieno = o["symbol"] == "AUSDT"
            if o.get("chiuso") and not pieno:
                return _Risposta({"status": "CANCELED", "executedQty": "0"})
            return _Risposta({"status": "FILLED" if pieno else "NEW", "executedQty": o["quantity"] if pieno else "0"})
        if u.path == "/fapi/v1/order" and metodo == "DELETE":
            if "orderId" in q and int(q["orderId"]) in self.ordini:
                self.ordini[int(q["orderId"])]["chiuso"] = True
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
    finto.posizioni_vive = True                        # come Binance: un ordine eseguito muove la posizione
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
    assert mercato == [{"symbol": "BUSDT", "side": "SELL", "type": "MARKET", "quantity": "99.986",
                        "newClientOrderId": dm.id_mercato("2026-10-24", "BUSDT", int(20750 * 86400.0 + 400)),
                        **{k: mercato[0][k] for k in ("timestamp", "recvWindow", "signature")}}]
    assert fb.get_rtdb("/demo_binance/stato")["equity"] == 10000.0
    rib = fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")
    assert rib["entrate"] == 2 and rib["uscite"] == 0
    assert fb.get_rtdb("/demo_binance/diario/2026-10-24") == {"equity": 10000.0, "long": 1, "short": 1}


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
                                        "/demo_binance/errore": {"testo": "GET x: 401", "ora": 1.7e9},
                                        "/demo_binance/allarme": {"ora": 1.7e9, "testo": "fermo ma il conto non è vuoto",
                                                                  "posizioni": ["BUSDT"]}}))
    testo = "\n".join(righe)
    assert "acceso" in testo and "$5,010.00" in testo and "eseguiti a limite 38" in testo and "401" in testo
    assert "**ALLARME**" in testo and "fermo ma il conto non è vuoto (BUSDT)" in testo     # revisione del 7 nov, problema 39


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


def _demo_semplice(tmp_path, finto, pesi=None, giorno=20750):
    from bot.core.firebase_client import _InMemoryStore
    fb = _InMemoryStore()
    (tmp_path / "acceso").write_text("si")
    g1 = tmp_path / "g1.json"
    g1.write_text(json.dumps({"ultimo_lunedi": giorno, "pesi": pesi or {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d = dm.DemoG1(fb, cliente=dm.ClienteDemo("chiave", "segreto", http=finto), file_stato=tmp_path / "st.json", file_g1=g1,
                  interruttore=tmp_path / "acceso")
    return d, fb


def _post(finto, percorso="/fapi/v1/order"):
    return [q for m, p, q in finto.chiamate if m == "POST" and p == percorso]


def test_margine_unico_chiesto_prima_della_leva(tmp_path):
    """Il proprietario, 1° novembre: il margine unico per tutto il conto, impostato dal codice (con la leva 5 e il margine separato
    una posizione si chiuderebbe a forza a −18%/−20%)."""
    finto = _Demo()
    d, _ = _demo_semplice(tmp_path, finto)
    d.tick(20750 * 86400.0 + 400)
    passi = [(p, q.get("symbol")) for m, p, q in finto.chiamate if m == "POST" and p in ("/fapi/v1/marginType", "/fapi/v1/leverage")]
    assert passi == [("/fapi/v1/marginType", "AUSDT"), ("/fapi/v1/leverage", "AUSDT"),
                     ("/fapi/v1/marginType", "BUSDT"), ("/fapi/v1/leverage", "BUSDT")]
    assert all(q["marginType"] == "CROSSED" for q in _post(finto, "/fapi/v1/marginType"))


def test_pulsante_chiude_tutto_poi_fermo_finche_non_riparte(tmp_path):
    finto = _Demo()
    finto.posizioni = {"AUSDT": 10.0, "BUSDT": -20.0}
    d, fb = _demo_semplice(tmp_path, finto)
    fb.set_rtdb(dm.COMANDO_CHIUDI, True)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    st = d.carica()
    assert st["fermo"]["motivo"] == "pulsante della dashboard" and fb.get_rtdb(dm.COMANDO_CHIUDI) is False
    chiusure = {q["symbol"]: (q["side"], q["type"], q["quantity"], q.get("reduceOnly")) for q in _post(finto)}
    assert chiusure == {"AUSDT": ("SELL", "MARKET", "10", "true"), "BUSDT": ("BUY", "MARKET", "20", "true")}
    assert fb.get_rtdb("/demo_binance/stato")["stato"].startswith("fermo")
    # fermo: la decisione nuova di G1 non manda ordini
    finto.posizioni = {"AUSDT": 0.0, "BUSDT": 0.0}
    n = len(_post(finto))
    d.tick(t0 + 4000)
    assert len(_post(finto)) == n and d.carica().get("fermo")
    # il pulsante «riparti»: dall'8 novembre (revisione della fase 1, decisione 3) il conto resta vuoto fino alla prossima decisione
    # di G1, come farà il conto vero (si compra alla mezzanotte), poi si torna ai pesi di G1
    fb.set_rtdb(dm.COMANDO_RIPARTI, True)
    d.tick(t0 + 8000)
    assert "fermo" not in d.carica() and fb.get_rtdb(dm.COMANDO_RIPARTI) is False
    d.tick(t0 + 8100)
    assert len(_post(finto)) == n                      # a metà giornata niente
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": 20751, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d.tick(20751 * 86400.0 + 400)
    assert {q["symbol"] for q in _post(finto)[n:] if q["type"] == "LIMIT"} == {"AUSDT", "BUSDT"}


def test_stop_sul_conto_a_meno_35_per_cento(tmp_path):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)                                         # ribilancio e prima valutazione: massimo 10.000
    assert d.carica()["massimo"] == 10000.0
    finto.posizioni = {"AUSDT": 50.0, "BUSDT": -100.0}
    finto.equity = "6600"                              # −34%: niente
    d.tick(t0 + 3700)
    assert "fermo" not in d.carica()
    finto.equity = "6400"                              # −36%: chiude tutto
    d.tick(t0 + 7400)
    st = d.carica()
    assert st["fermo"]["motivo"].startswith("stop sul conto: -36.0%")
    assert {q["symbol"] for q in _post(finto) if q["type"] == "MARKET" and q.get("reduceOnly") == "true"} >= {"AUSDT", "BUSDT"}


def test_margine_separato_si_chiude_e_passa_al_margine_unico(tmp_path):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    d.tick(t0 + 3601)                                  # ordini chiusi (eseguiti a limite o a mercato)
    finto.posizioni = {"AUSDT": 50.0, "BUSDT": -100.0}
    finto.separati = {"AUSDT"}
    d.tick(t0 + 7300)
    m = fb.get_rtdb("/demo_binance/margine")
    assert m["separati_trovati"] == ["AUSDT"] and m["sistemate"] == ["AUSDT"]
    assert any(q["symbol"] == "AUSDT" and q["type"] == "MARKET" and q.get("reduceOnly") == "true" for q in _post(finto))
    assert d.carica()["ultimo_giorno"] == 0             # si riapre subito ai pesi di oggi


def test_confronto_fra_posizioni_vere_e_volute(tmp_path):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    ob = d.carica()["obiettivi"]
    assert ob["AUSDT"] == pytest.approx(5000 / 100.003) and ob["BUSDT"] == pytest.approx(-5000 / 50.007)
    d.tick(t0 + 3601)                                  # ordini chiusi
    finto.posizioni = {"AUSDT": 30.0, "BUSDT": -99.986}
    d.tick(t0 + 7300)
    c = fb.get_rtdb("/demo_binance/confronto")
    assert [x["simbolo"] for x in c["differenze"]] == ["AUSDT"] and c["differenze"][0]["scarto"] == -0.2


def test_chiudi_tutto_e_riparti_con_il_file(tmp_path):
    """Lo stesso comando come file nel repository: una volta per ogni testo nuovo."""
    finto = _Demo()
    finto.posizioni = {"AUSDT": 10.0}
    finto.posizioni_vive = True                        # la chiusura svuota davvero il conto
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_chiudi, d.file_riparti = tmp_path / "chiudi", tmp_path / "riparti"
    d.file_chiudi.write_text("1 nov 2026 18:00")
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    assert d.carica()["fermo"]["motivo"] == "comando chiudi tutto"
    n = len(_post(finto))
    d.tick(t0 + 4000)                                  # lo stesso testo non si ripete
    assert len(_post(finto)) == n and d.carica().get("fermo")
    d.file_riparti.write_text("1 nov 2026 19:00")
    d.tick(t0 + 8000)
    assert "fermo" not in d.carica()



def test_entrate_vere_del_conto(tmp_path):
    finto = _Demo()
    g = 20755                                              # 5 giorni dopo il primo giorno del demo (24 ottobre = 20750)
    ms = lambda d, ora: (d * 86400 + ora * 3600) * 1000    # noqa: E731
    finto.entrate = [("FUNDING_FEE", ms(20750, 8), 1.5, "USDT"), ("FUNDING_FEE", ms(20750, 16), -0.5, "USDT"),
                     ("COMMISSION", ms(20750, 1), -0.2, "USDT"), ("COMMISSION", ms(20751, 1), -0.1, "BNB"),
                     ("FUNDING_FEE", ms(g, 0), 2.0, "USDT"), ("COMMISSION", ms(g, 0), -0.3, "USDT")]
    d, fb = _demo_semplice(tmp_path, finto, giorno=g)
    d.tick(g * 86400.0 + 400)
    primo = fb.get_rtdb("/demo_binance/diario/2026-10-24/entrate")
    assert primo["funding_incassato"] == pytest.approx(1.0) and primo["commissioni_pagate"] == pytest.approx(0.2)
    secondo = fb.get_rtdb("/demo_binance/diario/2026-10-25/entrate")
    assert secondo["altre_valute"] == 1 and secondo["commissioni_pagate"] == 0.0
    oggi = fb.get_rtdb("/demo_binance/diario/2026-10-29/entrate")
    assert oggi["funding_incassato"] == pytest.approx(2.0) and oggi["commissioni_pagate"] == pytest.approx(0.3)
    assert fb.get_rtdb("/demo_binance/diario/2026-10-29")["equity"] == 10000.0   # il diario del giorno resta intero
    assert d.carica()["entrate_chiuse_fino"] == g - 1
    n = sum(1 for m, p_, q in finto.chiamate if p_ == "/fapi/v1/income")
    d.tick(g * 86400.0 + 400 + 3700)                       # all'ora dopo: solo oggi, i giorni chiusi non si rileggono
    assert sum(1 for m, p_, q in finto.chiamate if p_ == "/fapi/v1/income") - n == 2


def test_entrate_che_non_si_leggono_non_fermano_niente(tmp_path):
    finto = _Demo()
    def rotto(*a, **k):
        raise RuntimeError("income non disponibile")
    d, fb = _demo_semplice(tmp_path, finto)
    d.tick(20750 * 86400.0 + 400)
    assert d.carica()["ultimo_giorno"] == 20750
    c = d.cliente()
    c.chiedi = rotto
    assert d._entrate(c, d.carica(), 20750 * 86400.0 + 5000)["ultimo_giorno"] == 20750


def test_conto_ridotto_come_un_conto_di_280(tmp_path, monkeypatch):
    """Il proprietario, 6 novembre 2026: «voglio partire con 250 euro» (280 USDT): il demo lavora come un conto di quella cifra, e la
    fase di prima passa in /demo_binance/fasi."""
    monkeypatch.setattr(dm, "filtri_veri", lambda: {})   # AUSDT e BUSDT esistono anche sul listino vero, con altri passi
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    fb.set_rtdb("/demo_binance/giorni/2026-11-05", 5232.79)
    (tmp_path / "capitale").write_text("280\n")
    d.file_capitale = tmp_path / "capitale"
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    st = d.carica()
    assert st["conto_ridotto"]["capitale"] == 280.0 and st["conto_ridotto"]["valore_vero_all_avvio"] == 10000.0
    assert st["capitale_iniziale"] == 280.0 and st["massimo"] == 280.0
    ordini = {q["symbol"]: float(q["quantity"]) for q in _post(finto) if q["type"] == "LIMIT"}
    assert ordini["AUSDT"] == pytest.approx(1.399) and ordini["BUSDT"] == pytest.approx(2.799)   # 140 USDT per lato, non 5.000
    stato = fb.get_rtdb("/demo_binance/stato")
    assert stato["equity"] == 280.0 and stato["conto_ridotto"] == 280.0 and stato["valore_vero_del_conto_demo"] == 10000.0
    assert fb.get_rtdb("/demo_binance/giorni/2026-11-05") is None
    fasi = fb.get_rtdb("/demo_binance/fasi")
    assert list(fasi) == [f"conto_intero_fino_al_{dm.time.strftime('%Y-%m-%d', dm.time.gmtime(t0))}"]
    # il guadagno del conto demo è il guadagno del conto ridotto; lo stop si misura sui 280
    finto.equity = "9905"                              # 185 USDT: −33,9%
    d.tick(t0 + 3700)
    assert "fermo" not in d.carica() and fb.get_rtdb("/demo_binance/stato")["equity"] == 185.0
    finto.equity = "9895"                              # 175 USDT: −37,5%, chiude tutto
    d.tick(t0 + 7400)
    assert d.carica()["fermo"]["motivo"].startswith("stop sul conto: -37.5%")


def test_filtri_severi_come_il_conto_vero():
    f = {"BTCUSDT": (0.1, 0.0001, 0.0001, 50.0), "LTCUSDT": (0.01, 0.001, 0.001, 5.0), "XUSDT": (0.01, 0.003, 0.003, 5.0),
         "YUSDT": (0.01, 1.0, 1.0, 5.0)}
    veri = {"BTCUSDT": {"passo": 0.001, "quantita_minima": 0.001, "valore_minimo": 50.0},
            "LTCUSDT": {"passo": 0.001, "quantita_minima": 0.001, "valore_minimo": 20.0},
            "XUSDT": {"passo": 0.004, "quantita_minima": 0.004, "valore_minimo": 5.0}}
    g = dm.piu_severi(f, veri)
    assert g["BTCUSDT"] == (0.1, 0.001, 0.001, 50.0)
    assert g["LTCUSDT"][3] == 20.0
    assert g["XUSDT"][1] == 0.003 and g["XUSDT"][2] == 0.004          # 0,004 non è un multiplo di 0,003: il passo resta
    assert g["YUSDT"] == f["YUSDT"]
    vero = dm.filtri_veri()
    assert vero["BTCUSDT"]["valore_minimo"] == 50.0 and vero["ETHUSDT"]["valore_minimo"] == 20.0 and len(vero) > 500


def test_senza_file_del_capitale_il_conto_resta_intero(tmp_path):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_capitale = tmp_path / "manca"
    d.tick(20750 * 86400.0 + 400)
    assert "conto_ridotto" not in d.carica() and fb.get_rtdb("/demo_binance/stato")["equity"] == 10000.0


def test_variazioni_sotto_il_minimo_contate(tmp_path, monkeypatch):
    """Prova 148: con 280 USDT molte variazioni restano sotto il minimo; il ribilancio le conta."""
    monkeypatch.setattr(dm, "filtri_veri", lambda: {})
    finto = _Demo(("AUSDT", "BUSDT", "CUSDT"))
    d, fb = _demo_semplice(tmp_path, finto, pesi={"AUSDT": 0.5, "BUSDT": -0.49, "CUSDT": -0.01})
    (tmp_path / "capitale").write_text("280")
    d.file_capitale = tmp_path / "capitale"
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    rib = fb.get_rtdb(f"/demo_binance/ribilanciamenti/{dm.time.strftime('%Y-%m-%d', dm.time.gmtime(20750 * 86400))}")
    assert rib["sotto_il_minimo"] == {"variazioni": 1, "valore_in_frazione_del_conto": 0.01}   # CUSDT: 2,8 USDT sotto i 5
    assert {q["symbol"] for q in _post(finto) if q["type"] == "LIMIT"} == {"AUSDT", "BUSDT"}
    assert dm.sotto_il_minimo({}, {}, {}, 280.0, {}) == {"variazioni": 0, "valore_in_frazione_del_conto": 0.0}


def test_capitale_nuovo_parte_alla_mezzanotte_dal_conto_vuoto(tmp_path, monkeypatch):
    """Il proprietario, 7 novembre 2026: «riparti a mezzanotte con il demo a 1000 [...] evita errore di apertura dei 280». Un capitale
    nuovo aspetta la decisione di G1 dopo; lì il demo chiude tutto, archivia la fase e riapre da zero."""
    monkeypatch.setattr(dm, "filtri_veri", lambda: {})
    monkeypatch.setattr(dm, "ATTESA_DOPO_CHIUSURA_S", 0.0)
    finto = _Demo(("AUSDT", "BUSDT", "CUSDT"))
    d, fb = _demo_semplice(tmp_path, finto)
    cap = tmp_path / "capitale"
    cap.write_text("280")
    d.file_capitale = cap
    g = 20750
    d.tick(g * 86400.0 + 400)                          # la fase da 280 parte con la decisione del giorno
    d.tick(g * 86400.0 + 4100)                         # finisce l'ora degli ordini limite
    assert d.carica()["conto_ridotto"]["capitale"] == 280.0
    finto.chiamate.clear()
    cap.write_text("1000")
    finto.posizioni = {"AUSDT": 0.0, "BUSDT": 0.0, "CUSDT": -3.0}
    d.tick(g * 86400.0 + 7400)                         # a metà giornata: niente parte, il capitale resta in attesa
    st = d.carica()
    assert st["conto_ridotto"]["capitale"] == 280.0 and st["capitale_in_attesa"] == 1000.0
    assert not _post(finto)
    assert fb.get_rtdb("/demo_binance/capitale_in_attesa")["capitale"] == 1000.0
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": g + 1, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d.tick((g + 1) * 86400.0 + 400)                    # la decisione della mezzanotte dopo
    st = d.carica()
    cr = st["conto_ridotto"]
    assert cr["capitale"] == 1000.0 and cr["da_zero"] and cr["chiuse_prima"] == 1 and "capitale_in_attesa" not in st
    assert st["capitale_iniziale"] == 1000.0 and st["massimo"] == 1000.0
    mercato = [q for q in _post(finto) if q["type"] == "MARKET"]
    assert [(q["symbol"], q["reduceOnly"]) for q in mercato] == [("CUSDT", "true")]          # prima si chiude
    limite = {q["symbol"]: float(q["quantity"]) for q in _post(finto) if q["type"] == "LIMIT"}
    assert limite["AUSDT"] == pytest.approx(4.999) and limite["BUSDT"] == pytest.approx(9.998)   # poi si apre su 1.000
    assert any(k.startswith("capitale_280_fino_al_") for k in fb.get_rtdb("/demo_binance/fasi"))
    assert fb.get_rtdb("/demo_binance/capitale_in_attesa") is None
    assert fb.get_rtdb("/demo_binance/stato")["capitale_in_attesa"] is None


# ---- la revisione del percorso degli ordini del 7 novembre 2026 (reviews/reports/2026-11-07-primo-avvio.md), problemi 1-4 ----

def _mercato(finto, simbolo=None):
    return [q for q in _post(finto) if q["type"] == "MARKET" and (simbolo is None or q["symbol"] == simbolo)]


def test_resto_a_mercato_non_parte_due_volte_dopo_un_errore(tmp_path):
    """Problema 1: l'ordine a mercato di CUSDT arriva a Binance ma la risposta si perde; al tentativo dopo né BUSDT né CUSDT
    ripartono, perché il resto si calcola dalla posizione vera e l'identificativo fisso si controlla prima."""
    import requests
    finto = _Demo(("AUSDT", "BUSDT", "CUSDT"))
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto, pesi={"AUSDT": 0.4, "BUSDT": -0.3, "CUSDT": -0.3})
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)                                         # A eseguito a limite, B e C in attesa
    finto.guasti_dopo["CUSDT"] = requests.exceptions.ReadTimeout("risposta persa")
    d.tick(t0 + 3700)                                  # B a mercato, C a mercato con la risposta persa: errore
    assert len(_mercato(finto, "BUSDT")) == 1 and len(_mercato(finto, "CUSDT")) == 1 and "ordini" in d.carica()
    d.tick(t0 + 3700 + dm.ATTESA_DOPO_ERRORE_S + 10)   # il tentativo dopo
    assert len(_mercato(finto, "BUSDT")) == 1 and len(_mercato(finto, "CUSDT")) == 1
    assert "ordini" not in d.carica()
    assert finto.posizioni["CUSDT"] == pytest.approx(-0.3 * 10000 / 2.0, abs=0.001)    # una volta sola, non il doppio


def test_pulsante_anche_durante_l_attesa_dopo_un_errore(tmp_path, monkeypatch):
    """Problema 2: dopo un errore il ribilancio aspetta 30 minuti, il pulsante no."""
    finto = _Demo()
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    def rotto(*a, **k):
        raise TimeoutError("rete")
    monkeypatch.setattr(d, "chiudi_ordini", rotto)
    d.tick(t0 + 3700)                                  # errore: il ribilancio aspetta
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("7 nov 2026 15:00")
    d.tick(t0 + 3760)                                  # un minuto dopo l'errore
    assert d.carica()["fermo"]["motivo"] == "comando chiudi tutto"
    assert finto.posizioni == {"AUSDT": 0.0, "BUSDT": 0.0}


def test_stop_sul_conto_ogni_minuto(tmp_path):
    """Problema 2: lo stop sul conto si guarda ogni minuto, non ogni ora."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    finto.equity = "6400"                              # −36%
    d.tick(t0 + 61)
    assert d.carica()["fermo"]["motivo"].startswith("stop sul conto: -36.0%")


def test_da_fermo_si_richiude_fino_al_conto_vuoto(tmp_path):
    """Problema 3: una chiusura rifiutata (troppe richieste) si ritenta ogni minuto; allarme dopo 3 tentativi a vuoto."""
    finto = _Demo()
    finto.posizioni = {"AUSDT": 10.0, "BUSDT": -5.0}
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("7 nov 2026 15:00")
    troppe = _rifiutata()
    finto.guasti[("POST", "/fapi/v1/order", "BUSDT")] = troppe
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    assert d.carica()["fermo"] and finto.posizioni == {"AUSDT": 0.0, "BUSDT": -5.0}
    d.tick(t0 + 61)                                    # si richiude quello che resta
    assert finto.posizioni == {"AUSDT": 0.0, "BUSDT": 0.0}
    d.tick(t0 + 122)
    assert d.carica()["fermo"].get("vuoto") and fb.get_rtdb("/demo_binance/allarme") is None
    # una moneta che non si chiude mai: allarme
    finto2 = _Demo()
    finto2.posizioni, finto2.posizioni_vive = {"BUSDT": -5.0}, True
    (tmp_path / "due").mkdir()
    d2, fb2 = _demo_semplice(tmp_path / "due", finto2)
    d2.file_chiudi = tmp_path / "chiudi"
    for k in range(3):
        finto2.guasti[("POST", "/fapi/v1/order", "BUSDT")] = troppe
        d2.tick(t0 + 61 * k)
    assert d2.carica()["fermo"]["tentativi"] == 3 and fb2.get_rtdb("/demo_binance/allarme")["posizioni"] == ["BUSDT"]


class _FbCheSbaglia:
    """Firebase con la scrittura di un percorso che non arriva (``set_rtdb`` restituisce False, come il client vero)."""

    def __init__(self):
        from bot.core.firebase_client import _InMemoryStore
        self.m, self.rotti = _InMemoryStore(), set()

    def set_rtdb(self, percorso, valore):
        if percorso in self.rotti:
            return False
        self.m.set_rtdb(percorso, valore)
        return True

    def get_rtdb(self, percorso):
        return self.m.get_rtdb(percorso)


def test_riparti_rimasto_vero_non_riaccende(tmp_path):
    """Problema 4: un «riparti» premuto prima dello stop non vale; un «riparti» che non si riesce a consumare non riaccende."""
    finto = _Demo()
    finto.posizioni_vive = True
    fb = _FbCheSbaglia()
    (tmp_path / "acceso").write_text("si")
    g1 = tmp_path / "g1.json"
    g1.write_text(json.dumps({"ultimo_lunedi": 20750, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d = dm.DemoG1(fb, cliente=dm.ClienteDemo("chiave", "segreto", http=finto), file_stato=tmp_path / "st.json", file_g1=g1,
                  interruttore=tmp_path / "acceso")
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    fb.set_rtdb(dm.COMANDO_RIPARTI, True)              # premuto mentre il demo gira: non fa niente
    finto.equity = "6400"
    d.tick(t0 + 61)                                    # stop sul conto: il «riparti» vecchio si pulisce
    assert d.carica()["fermo"] and fb.get_rtdb(dm.COMANDO_RIPARTI) is False
    d.tick(t0 + 122)
    assert d.carica().get("fermo")                     # non riparte da solo
    fb.set_rtdb(dm.COMANDO_RIPARTI, True)              # il proprietario preme «riparti», ma la scrittura del falso non arriva
    fb.rotti.add(dm.COMANDO_RIPARTI)
    d.tick(t0 + 183)
    assert d.carica().get("fermo")
    fb.rotti.clear()                                   # Firebase torna: il comando si consuma e il demo riparte
    finto.equity = "9000"                              # sopra il pavimento del problema 23 (65% del capitale di partenza)
    d.tick(t0 + 244)
    assert "fermo" not in d.carica()


# ---- la revisione delle correzioni del 7 novembre 2026 (reviews/reports/2026-11-07-correzioni-9-problemi.md), problemi 25-31 ----

def test_annullo_rifiutato_niente_a_mercato(tmp_path):
    """Problema 25: l'annullo di BUSDT è rifiutato e l'ordine limite resta aperto: niente a mercato finché non è chiuso davvero."""
    finto = _Demo()
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    finto.guasti[("DELETE", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    d.tick(t0 + 3700)
    assert _mercato(finto) == [] and "ordini" in d.carica()           # fermo il giro, l'ordine non segnato controllato
    d.tick(t0 + 3700 + dm.ATTESA_DOPO_ERRORE_S + 10)                   # l'annullo ora riesce: il resto a mercato, una volta
    assert len(_mercato(finto, "BUSDT")) == 1 and "ordini" not in d.carica()
    assert finto.posizioni["BUSDT"] == pytest.approx(-0.5 * 10000 / 50.007, abs=0.001)


def test_secondo_ribilancio_dello_stesso_giorno_manda_il_resto(tmp_path):
    """Problema 26: un secondo ribilancio nello stesso giorno manda il resto a mercato con un identificativo nuovo. Dall'8 novembre
    il «riparti» aspetta la decisione dopo (decisione 3), quindi il secondo ribilancio del giorno qui viene dal margine separato."""
    finto = _Demo()
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    d.tick(t0 + 3700)                                  # resto di BUSDT a mercato
    finto.separati = {"BUSDT"}
    d.tick(t0 + 7300)                                  # ogni ora: BUSDT a margine separato si chiude e si riapre oggi
    assert finto.posizioni["BUSDT"] == 0.0
    d.tick(t0 + 7360)                                  # ribilancio dello stesso giorno
    d.tick(t0 + 7360 + 3700)                           # resto a mercato del secondo ribilancio
    assert len(_mercato(finto, "BUSDT")) >= 3 and finto.posizioni["BUSDT"] == pytest.approx(-0.5 * 10000 / 50.007, abs=0.001)


def test_da_fermo_si_annullano_anche_gli_ordini_senza_posizioni(tmp_path):
    """Problema 31: da fermo, un ordine limite rimasto aperto senza posizioni si annulla."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)                                         # ordini limite: BUSDT resta aperto
    finto.guasti[("DELETE", "/fapi/v1/allOpenOrders", "BUSDT")] = _rifiutata()
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("chiudi 1")
    d.tick(t0 + 60)                                    # chiudi tutto: l'annullo di BUSDT rifiutato
    assert any(not o.get("chiuso") and o["symbol"] == "BUSDT" for o in finto.ordini.values())
    d.tick(t0 + 130)                                   # da fermo: si riannulla
    assert all(o.get("chiuso") for o in finto.ordini.values() if o["symbol"] == "BUSDT" and o["type"] == "LIMIT")


def test_riparti_a_file_anche_senza_firebase(tmp_path):
    """Problema 27: con Firebase che non conferma, il «riparti» a file funziona lo stesso."""
    finto = _Demo()
    finto.posizioni_vive = True
    fb = _FbCheSbaglia()
    fb.rotti.add(dm.COMANDO_RIPARTI)
    (tmp_path / "acceso").write_text("si")
    g1 = tmp_path / "g1.json"
    g1.write_text(json.dumps({"ultimo_lunedi": 20750, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d = dm.DemoG1(fb, cliente=dm.ClienteDemo("chiave", "segreto", http=finto), file_stato=tmp_path / "st.json", file_g1=g1,
                  interruttore=tmp_path / "acceso", file_chiudi=tmp_path / "chiudi", file_riparti=tmp_path / "riparti")
    (tmp_path / "riparti").write_text("vecchio")       # scritto prima dello stop: non vale
    (tmp_path / "chiudi").write_text("chiudi 1")
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    d.tick(t0 + 61)
    assert d.carica().get("fermo")
    (tmp_path / "riparti").write_text("nuovo")
    d.tick(t0 + 122)
    assert "fermo" not in d.carica()


def test_da_fermo_si_richiude_anche_senza_leggere_gli_ordini(tmp_path):
    """Problema 32 (revisione del 7 novembre 2026, reviews/reports/2026-11-07-correzioni-25-31.md): da fermo, con la lettura degli
    ordini aperti sempre in errore, la posizione rimasta si richiude lo stesso al minuto dopo."""
    finto = _Demo()
    finto.posizioni, finto.posizioni_vive = {"BUSDT": -20.0}, True
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("chiudi 1")
    t0 = 20750 * 86400.0 + 400
    finto.guasti[("POST", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    d.tick(t0)                                         # fermo, ma BUSDT non si è chiuso
    assert d.carica()["fermo"] and finto.posizioni["BUSDT"] == -20.0
    for k in range(1, 4):
        finto.guasti[("GET", "/fapi/v1/openOrders", None)] = _Risposta({"code": -1001, "msg": "servizio"}, 503)
        d.tick(t0 + 61 * k)
    assert finto.posizioni["BUSDT"] == 0.0


def test_ordine_che_non_si_annulla_da_allarme(tmp_path):
    """Problema 33: un ordine aperto che non va via blocca il resto a mercato; dopo 2 ore scatta un allarme."""
    finto = _Demo()
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    eterno = [o for o in finto.ordini.values() if o["symbol"] == "BUSDT"][0]
    for k in range(5):                                 # l'annullo di BUSDT non riesce mai: 5 tentativi, oltre 2 ore
        finto.guasti[("DELETE", "/fapi/v1/order", "BUSDT")] = _rifiutata()
        d.tick(t0 + 3700 + k * (dm.ATTESA_DOPO_ERRORE_S + 10))
        assert not eterno.get("chiuso")
    assert _mercato(finto) == []                       # niente posizione doppia
    allarme = fb.get_rtdb("/demo_binance/allarmi/ordini")   # l'ultimo giro è oltre 2 ore dopo il primo blocco; chiave sua (38)
    assert allarme and allarme["monete"] == ["BUSDT"] and fb.get_rtdb("/demo_binance/allarme") is None



# ---- fase 1 del conto vero (docs/conto_vero.md): i problemi rimasti delle revisioni del 7 novembre 2026 ----
# reviews/reports/2026-11-07-correzione-32.md (36-38) e reviews/reports/2026-11-07-primo-avvio.md (10, 12, 13, 15, 16, 21-23)

def _sempre(d, finto, metodo, percorso, errore, simbolo=None):
    """Un guasto che dura (``guasti`` del Binance finto vale una volta sola): ``errore`` è un'eccezione o una risposta."""
    def chiama(m, url, headers=None, timeout=None):
        u = urlparse(url)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        if m == metodo and u.path == percorso and (simbolo is None or q.get("symbol") == simbolo):
            finto.chiamate.append((m, u.path, q))
            if isinstance(errore, Exception):
                raise errore
            return errore
        return finto(m, url, headers, timeout)
    d._cliente.http = chiama


def test_36_da_fermo_lettura_degli_ordini_in_errore_niente_vuoto(tmp_path):
    """Prova k3: da fermo, nessuna posizione, un ordine limite rimasto su BUSDT e `openOrders` sempre in errore: il conto non si
    segna vuoto, si annulla sulle monete dell'ultimo ribilancio e al terzo tentativo c'è l'allarme; «vuoto» solo dopo una lettura
    riuscita, e si toglie se ricompare una posizione."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)                                         # ordini limite: BUSDT resta aperto, nessuna posizione
    finto.guasti[("DELETE", "/fapi/v1/allOpenOrders", "BUSDT")] = _rifiutata()
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("chiudi 1")
    d.tick(t0 + 60)                                    # chiudi tutto: l'annullo di BUSDT rifiutato
    busdt = [o for o in finto.ordini.values() if o["symbol"] == "BUSDT" and o["type"] == "LIMIT"][0]
    assert d.carica()["fermo"] and not busdt.get("chiuso")
    _sempre(d, finto, "GET", "/fapi/v1/openOrders", _Risposta({"code": -1001, "msg": "servizio"}, 503))
    d.tick(t0 + 130)
    assert not d.carica()["fermo"].get("vuoto") and busdt.get("chiuso")    # annullato lo stesso, dall'ultimo ribilancio
    d.tick(t0 + 200)
    assert "3 tentativi" in fb.get_rtdb("/demo_binance/allarme")["testo"]
    d._cliente.http = finto                            # la lettura torna: ora sì, il conto è vuoto
    d.tick(t0 + 270)
    assert d.carica()["fermo"].get("vuoto") and fb.get_rtdb("/demo_binance/allarme") is None
    finto.posizioni["AUSDT"], finto.posizioni_vive = 1.0, True     # ricompare una posizione: non è più vuoto
    d.tick(t0 + 340)
    assert not d.carica()["fermo"].get("vuoto") and finto.posizioni["AUSDT"] == 0.0


@pytest.mark.parametrize("guasto", ["rete", "503"])
def test_37_da_fermo_guasto_che_dura_sulla_lettura_degli_ordini(tmp_path, guasto):
    """Prova k4: `openOrders` sempre in timeout di rete (non un RuntimeError) o sempre 503: la posizione rimasta si richiude lo stesso."""
    import requests
    finto = _Demo()
    finto.posizioni, finto.posizioni_vive = {"BUSDT": -20.0}, True
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("chiudi 1")
    finto.guasti[("POST", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)                                         # fermo, ma BUSDT non si è chiuso
    assert d.carica()["fermo"] and finto.posizioni["BUSDT"] == -20.0
    errore = (requests.exceptions.ReadTimeout("lettura scaduta") if guasto == "rete"
              else _Risposta({"code": -1001, "msg": "servizio"}, 503))
    _sempre(d, finto, "GET", "/fapi/v1/openOrders", errore)
    for k in range(1, 3):
        d.tick(t0 + 61 * k)
    assert finto.posizioni["BUSDT"] == 0.0


def _ordine_bloccato(tmp_path):
    finto = _Demo()
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    return finto, d, fb, t0 + 3700


def test_38_l_allarme_degli_ordini_bloccati_si_spegne(tmp_path):
    """Prove h4b e h4c: l'allarme degli ordini che non si annullano ha una chiave sua e si toglie quando il ribilancio finisce."""
    finto, d, fb, t1 = _ordine_bloccato(tmp_path)
    passo = dm.ATTESA_DOPO_ERRORE_S + 10
    for k in range(5):                                 # oltre 2 ore di blocchi di fila
        finto.guasti[("DELETE", "/fapi/v1/order", "BUSDT")] = _rifiutata()
        d.tick(t1 + k * passo)
    assert fb.get_rtdb("/demo_binance/allarmi/ordini")["monete"] == ["BUSDT"]
    d.tick(t1 + 5 * passo)                             # l'annullo riesce: resto a mercato, ribilancio finito
    assert "ordini" not in d.carica() and len(_mercato(finto, "BUSDT")) == 1
    assert fb.get_rtdb("/demo_binance/allarmi/ordini") is None and "ordini" not in d.carica().get("allarmi", {})


def test_38_l_allarme_conta_solo_i_blocchi_di_fila(tmp_path):
    """Prova h5: un blocco, poi due ore di altri errori, poi un blocco nuovo: nessun allarme «da oltre 2 ore»."""
    import requests
    finto, d, fb, t1 = _ordine_bloccato(tmp_path)
    passo = dm.ATTESA_DOPO_ERRORE_S + 10
    finto.guasti[("DELETE", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    d.tick(t1)                                         # blocco
    assert d.carica()["ordini"]["bloccato_dal"] == t1
    for k in range(1, 4):                              # altri errori: la lettura dell'ordine di BUSDT non risponde
        finto.guasti[("GET", "/fapi/v1/order", "BUSDT")] = requests.exceptions.ReadTimeout("rete")
        d.tick(t1 + k * passo)
    finto.guasti[("DELETE", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    d.tick(t1 + 4 * passo)                             # blocco nuovo, oltre 2 ore dopo il primo
    assert d.carica()["ordini"]["bloccato_dal"] == t1 + 4 * passo
    assert fb.get_rtdb("/demo_binance/allarmi/ordini") is None and fb.get_rtdb("/demo_binance/allarme") is None


@pytest.mark.parametrize("pesi", [{"AUSDT": 1.5, "BUSDT": -1.5}, {"AUSDT": 0.7, "BUSDT": -0.5},
                                  {"AUSDT": float("nan"), "BUSDT": -0.5}, {"AUSDT": "mezzo", "BUSDT": -0.5}])
def test_10_pesi_fuori_dai_limiti_niente_ordini(tmp_path, pesi):
    """Problema 10: somma oltre il 250%, una moneta oltre il 60%, un peso non finito o non numerico: niente ordini e allarme."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto, pesi=pesi)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    assert _post(finto) == [] and "ultimo_giorno" not in d.carica()
    assert "niente ordini" in fb.get_rtdb("/demo_binance/allarmi/pesi")["testo"]
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": 20750, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d.tick(t0 + 60)                                    # pesi corretti: gli ordini partono, l'allarme si toglie
    assert {q["symbol"] for q in _post(finto) if q["type"] == "LIMIT"} == {"AUSDT", "BUSDT"}
    assert fb.get_rtdb("/demo_binance/allarmi/pesi") is None


def test_10_i_pesi_di_g1_stanno_nei_limiti():
    """I limiti sono larghi rispetto a G1: due lati da 1 (20 monete ciascuno), il 47,8% di una moneta, 5 operazioni a eventi."""
    lati = {f"L{i}USDT": 1 / 20 for i in range(20)} | {f"S{i}USDT": -1 / 20 for i in range(20)}
    assert dm.pesi_fuori_dai_limiti(lati, {}) is None
    concentrato = {"BLZUSDT": -0.478, **{f"S{i}USDT": -0.522 / 4 for i in range(4)}, **{f"L{i}USDT": 1 / 20 for i in range(20)}}
    assert dm.pesi_fuori_dai_limiti(concentrato, dm.pesi_eventi({str(i): {"simbolo": f"E{i}USDT"} for i in range(5)})) is None
    assert dm.pesi_fuori_dai_limiti(lati, lati) is not None                 # lo stesso peso contato due volte: 400%
    assert dm.pesi_fuori_dai_limiti(["AUSDT"], {}) == "pesi non leggibili"


def test_12_decisione_di_g1_piu_vecchia_di_26_ore_non_si_esegue(tmp_path):
    """Problema 12: la decisione di G1 vecchia di oltre 26 ore non manda ordini e scrive un allarme; quella nuova li manda."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    d.tick(20750 * 86400.0 + 27 * 3600)                # la decisione del 24 ottobre, 27 ore dopo
    assert _post(finto) == []
    assert "2026-10-24" in fb.get_rtdb("/demo_binance/allarmi/decisione_g1")["testo"]
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": 20751, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d.tick(20750 * 86400.0 + 27 * 3600 + 60)           # G1 decide di nuovo: gli ordini partono
    assert {q["symbol"] for q in _post(finto) if q["type"] == "LIMIT"} == {"AUSDT", "BUSDT"}
    assert fb.get_rtdb("/demo_binance/allarmi/decisione_g1") is None
    d.tick(20752 * 86400.0 + 3 * 3600)                 # il paper di G1 si ferma: dopo 27 ore l'allarme torna
    assert "2026-10-25" in fb.get_rtdb("/demo_binance/allarmi/decisione_g1")["testo"]


def _attese(monkeypatch):
    attese = []
    monkeypatch.setattr(dm.time, "sleep", attese.append)
    return attese


def test_13_un_429_si_riprova_con_attese_crescenti_e_retry_after(tmp_path, monkeypatch):
    """Problema 13: un 429 non diventa un rifiuto; si riprova dopo 1 e 2 secondi, o dopo il Retry-After di Binance."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    attese = _attese(monkeypatch)
    troppe = _Risposta({"code": -1003, "msg": "Too many requests"}, 429)
    risposte = [troppe, troppe]
    def chiama(m, url, headers=None, timeout=None):
        if m == "POST" and urlparse(url).path == "/fapi/v1/order" and "symbol=AUSDT" in url and risposte:
            return risposte.pop(0)
        return finto(m, url, headers, timeout)
    d._cliente.http = chiama
    d.tick(20750 * 86400.0 + 400)
    assert attese == [1.0, 2.0]
    assert {q["symbol"] for q in _post(finto) if q["type"] == "LIMIT"} == {"AUSDT", "BUSDT"}
    rib = fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")
    assert rib["rifiutati"] == [] and rib["ordini"] == 2
    attese.clear()
    finto.guasti[("GET", "/fapi/v1/premiumIndex", None)] = _Risposta({"code": -1003}, 429, headers={"Retry-After": "3"})
    assert d._cliente.chiedi("GET", "/fapi/v1/premiumIndex") and attese == [3.0]


def test_13_429_che_dura_ferma_il_giro_e_scrive_un_allarme(tmp_path, monkeypatch):
    """Problema 13: con il 429 che dura, dopo 3 ritentativi il giro si ferma (BUSDT non parte), nessuna richiesta per 2 minuti,
    allarme; poi si riprende e l'allarme si toglie."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    attese = _attese(monkeypatch)
    _sempre(d, finto, "POST", "/fapi/v1/order", _Risposta({"code": -1003, "msg": "Too many requests"}, 429), simbolo="AUSDT")
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    assert attese == [1.0, 2.0, 4.0] and not [q for q in _post(finto) if q["symbol"] == "BUSDT"]
    assert "limita le richieste" in fb.get_rtdb("/demo_binance/allarmi/limiti_binance")["testo"]
    n = len(finto.chiamate)
    d.tick(t0 + 61)                                    # dentro l'attesa: nessuna richiesta, nemmeno delle protezioni
    assert len(finto.chiamate) == n
    d._cliente.http = finto                            # Binance torna normale
    d.tick(t0 + dm.ATTESA_DOPO_LIMITE_S + 1)
    assert fb.get_rtdb("/demo_binance/allarmi/limiti_binance") is None
    d.tick(t0 + dm.ATTESA_DOPO_ERRORE_S + 10)          # il ribilancio riprova dopo la sua attesa
    assert {q["symbol"] for q in _post(finto) if q["type"] == "LIMIT"} == {"AUSDT", "BUSDT"}


def test_13_un_418_rispetta_il_retry_after_senza_riprovare_subito(tmp_path, monkeypatch):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    attese = _attese(monkeypatch)
    finto.guasti[("GET", "/fapi/v2/account", None)] = _Risposta({"code": -1003, "msg": "banned"}, 418, headers={"Retry-After": "300"})
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    assert attese == [] and fb.get_rtdb("/demo_binance/allarmi/limiti_binance")
    n = len(finto.chiamate)
    d.tick(t0 + 200)
    assert len(finto.chiamate) == n                    # bloccato: nessuna richiesta prima dei 300 secondi
    d.tick(t0 + 301)
    assert len(finto.chiamate) > n


def test_15_massimo_dello_stop_anche_su_firebase(tmp_path):
    """Problema 15: il file dello stato perso (ripartenza del bot) non fa ripartire il massimo dal valore di adesso; un massimo
    vecchio su Firebase (scrittura persa dopo un «riparti») non vale contro il file della serie nuova."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    finto.equity = "10500"
    d.tick(t0 + 61)
    assert fb.get_rtdb("/demo_binance/massimo")["valore"] == 10500.0
    (tmp_path / "st.json").unlink()                    # il file perso, il bot riparte
    finto.equity = "6800"                              # −35,2% dal massimo di 10.500 (dal valore di adesso sarebbe 0%)
    d2 = dm.DemoG1(fb, cliente=d._cliente, file_stato=tmp_path / "st.json", file_g1=tmp_path / "g1.json",
                   interruttore=tmp_path / "acceso")
    d2.tick(t0 + 122)
    assert d2.carica()["fermo"]["motivo"].startswith("stop sul conto: -35.2%")


def test_15_massimo_vecchio_su_firebase_non_vale_dopo_un_riparti(tmp_path):
    finto = _Demo()
    fb = _FbCheSbaglia()
    (tmp_path / "acceso").write_text("si")
    g1 = tmp_path / "g1.json"
    g1.write_text(json.dumps({"ultimo_lunedi": 20750, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    argomenti = dict(cliente=dm.ClienteDemo("chiave", "segreto", http=finto), file_stato=tmp_path / "st.json", file_g1=g1,
                     interruttore=tmp_path / "acceso", file_riparti=tmp_path / "riparti")
    d = dm.DemoG1(fb, **argomenti)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    finto.equity = "10500"
    d.tick(t0 + 61)
    finto.equity = "6600"                              # −37%: stop
    d.tick(t0 + 122)
    assert d.carica()["fermo"]
    fb.rotti.add("/demo_binance/massimo")              # la scrittura del massimo nuovo non arriva
    (tmp_path / "riparti").write_text("riparti 1")
    d.tick(t0 + 183)
    assert "fermo" not in d.carica() and fb.get_rtdb("/demo_binance/massimo")["valore"] == 10500.0
    fb.rotti.clear()
    d3 = dm.DemoG1(fb, **argomenti)                    # il bot riparte con il file buono
    d3.tick(t0 + 244)
    assert "fermo" not in d3.carica() and d3.carica()["massimo"] == 6600.0


@pytest.mark.parametrize("scritto", ["50000", "abc", "inf", "-280"])
def test_16_capitale_oltre_il_tetto_o_non_numerico_non_si_usa(tmp_path, monkeypatch, scritto):
    """Problema 16: un capitale sopra 10.000 USDT, non numerico o non positivo non si usa (resta quello in corso) e scrive un
    allarme; un capitale buono lo toglie."""
    monkeypatch.setattr(dm, "filtri_veri", lambda: {})
    monkeypatch.setattr(dm, "ATTESA_DOPO_CHIUSURA_S", 0.0)
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    cap = tmp_path / "capitale"
    cap.write_text("280")
    d.file_capitale = cap
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    assert d.carica()["conto_ridotto"]["capitale"] == 280.0
    cap.write_text(scritto)
    d.tick(t0 + 60)
    st = d.carica()
    assert st["conto_ridotto"]["capitale"] == 280.0 and "capitale_in_attesa" not in st
    assert "resta il capitale in corso" in fb.get_rtdb("/demo_binance/allarmi/capitale")["testo"]
    cap.write_text("1000")
    d.tick(t0 + 120)
    assert d.carica()["capitale_in_attesa"] == 1000.0 and fb.get_rtdb("/demo_binance/allarmi/capitale") is None


def test_16_filtri_del_conto_vero_piu_vecchi_di_30_giorni(tmp_path, monkeypatch):
    """Problema 16: i filtri del conto vero restano una copia fissa, ma con la data scritta nel codice; oltre 30 giorni, allarme."""
    monkeypatch.setattr(dm, "filtri_veri", lambda: {})
    monkeypatch.setattr(dm, "ATTESA_DOPO_CHIUSURA_S", 0.0)
    giorno = 20797                                     # 10 dicembre 2026: 34 giorni dopo la copia del 6 novembre
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto, giorno=giorno)
    (tmp_path / "capitale").write_text("280")
    d.file_capitale = tmp_path / "capitale"
    d.tick(giorno * 86400.0 + 400)
    assert d.carica()["conto_ridotto"]["capitale"] == 280.0
    assert "34 giorni" in fb.get_rtdb("/demo_binance/allarmi/filtri_veri")["testo"]
    # la data nel codice è quella del file: chi riscarica i filtri deve cambiarle insieme
    fonte = json.loads(dm.FILE_FILTRI_VERI.read_text(encoding="utf-8"))["fonte"]
    mesi = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre",
            "dicembre"]
    a, m, g = (int(x) for x in dm.DATA_FILTRI_VERI.split("-"))
    assert f"{g} {mesi[m - 1]} {a}" in fonte


def test_21_errori_senza_la_parte_firmata_dell_indirizzo(tmp_path, capsys):
    """Problema 21: un errore di rete riporta l'indirizzo con la firma; su Firebase e nel log restano solo metodo, percorso e codice."""
    import requests
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    firmato = ("HTTPSConnectionPool(host='demo-fapi.binance.com', port=443): Max retries exceeded with url: "
               "/fapi/v2/account?timestamp=1762600000000&recvWindow=5000&signature=deadbeef0123456789 (Caused by x)")
    finto.guasti[("GET", "/fapi/v2/account", None)] = requests.exceptions.ConnectionError(firmato)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)                                         # errore nelle protezioni
    testo = fb.get_rtdb("/demo_binance/errore")["testo"]
    assert "/fapi/v2/account" in testo and "deadbeef" not in testo and "signature" not in testo
    finto.guasti[("GET", "/fapi/v1/openOrders", None)] = requests.exceptions.ConnectionError(firmato.replace("v2/account",
                                                                                                             "v1/openOrders"))
    d.tick(t0 + 61)                                    # errore nel ribilancio
    testo = fb.get_rtdb("/demo_binance/errore")["testo"]
    assert "/fapi/v1/openOrders" in testo and "deadbeef" not in testo
    assert "deadbeef" not in capsys.readouterr().out
    finto.guasti[("GET", "/fapi/v2/account", None)] = requests.exceptions.ReadTimeout(firmato)
    with pytest.raises(requests.exceptions.ReadTimeout) as e:      # il tipo dell'errore resta (per chi lo prende)
        d._cliente.chiedi("GET", "/fapi/v2/account", firmata=True)
    assert "deadbeef" not in str(e.value)
    assert dm.senza_firma("POST /fapi/v1/order: 400 {\"code\": -2019}") == "POST /fapi/v1/order: 400 {\"code\": -2019}"


class _DemoFiltri(_Demo):
    """Il Binance finto con filtri di exchangeInfo scelti dal test, la leva per posizione e il modo a due lati."""

    def __init__(self, filtri_per_moneta, **k):
        super().__init__(**k)
        self.filtri_per_moneta, self.leve, self.due_lati = filtri_per_moneta, {}, False

    def __call__(self, metodo, url, headers=None, timeout=None):
        u = urlparse(url)
        if u.path == "/fapi/v1/exchangeInfo":
            self.chiamate.append((metodo, u.path, {}))
            return _Risposta({"symbols": [{"symbol": s, "filters": f} for s, f in self.filtri_per_moneta.items()]})
        if u.path == "/fapi/v1/positionSide/dual" and metodo == "GET":
            self.chiamate.append((metodo, u.path, {}))
            return _Risposta({"dualSidePosition": self.due_lati})
        r = super().__call__(metodo, url, headers, timeout)
        if u.path == "/fapi/v2/account":
            for x in r.dati["positions"]:
                if x["symbol"] in self.leve:
                    x["leverage"] = self.leve[x["symbol"]]
        return r


_BASE = [{"filterType": "PRICE_FILTER", "tickSize": "0.01"}, {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"},
         {"filterType": "MIN_NOTIONAL", "notional": "5"}]


def test_22_moneta_senza_valore_minimo_non_si_tratta(tmp_path):
    """Problema 22: senza il filtro del valore minimo la moneta non si tratta (prima: 5 USDT scritti a mano)."""
    finto = _DemoFiltri({"AUSDT": _BASE, "BUSDT": _BASE[:2]})
    d, fb = _demo_semplice(tmp_path, finto)
    d.tick(20750 * 86400.0 + 400)
    assert {q["symbol"] for q in _post(finto) if q["type"] == "LIMIT"} == {"AUSDT"}
    assert fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")["monete_mancanti_sul_demo"] == ["BUSDT"]


def test_22_filtri_degli_ordini_a_mercato_e_quantita_massima(tmp_path):
    """Problema 22: l'ordine limite non supera la quantità massima di LOT_SIZE; quello a mercato usa passo, minimo e massimo di
    MARKET_LOT_SIZE."""
    b = [_BASE[0], {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001", "maxQty": "80"}, _BASE[2],
         {"filterType": "MARKET_LOT_SIZE", "stepSize": "1", "minQty": "1", "maxQty": "50"}]
    finto = _DemoFiltri({"AUSDT": _BASE, "BUSDT": b})
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    assert [q["quantity"] for q in _post(finto) if q["symbol"] == "BUSDT" and q["type"] == "LIMIT"] == ["80"]   # voleva 99,986
    d.tick(t0 + 3700)
    assert [q["quantity"] for q in _mercato(finto, "BUSDT")] == ["50"]


def test_22_leva_e_modo_delle_posizioni_riletti_ogni_ora(tmp_path):
    """Problema 22: la leva si rilegge ogni ora e si rimette a 5 se è cambiata; il modo a due lati fa ricontrollare il modo."""
    finto = _DemoFiltri({"AUSDT": _BASE, "BUSDT": _BASE})
    finto.posizioni = {"AUSDT": 10.0, "BUSDT": -20.0}
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    finto.leve, finto.due_lati = {"AUSDT": "10", "BUSDT": "5"}, True
    d.tick(t0 + 3700)                                  # la valutazione dell'ora dopo
    leve = [q["symbol"] for q in _post(finto, "/fapi/v1/leverage")]
    assert leve.count("AUSDT") == 2 and leve.count("BUSDT") == 1
    margine = fb.get_rtdb("/demo_binance/margine")
    assert margine["leve_rimesse"] == ["AUSDT"] and margine["due_lati"] is True and "modo_controllato" not in d.carica()


def test_22_log_d_avvio_con_l_ambiente(tmp_path, capsys):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    d.tick(20750 * 86400.0 + 400)
    avvio = fb.get_rtdb("/demo_binance/avvio")
    assert avvio["indirizzo"] == "demo-fapi.binance.com" and avvio["leva"] == 5 and avvio["capitale_massimo"] == 10000.0
    assert "[demo_binance] avvio: indirizzo demo-fapi.binance.com" in capsys.readouterr().out


def test_23_riparti_sotto_il_pavimento_non_riaccende(tmp_path, monkeypatch):
    """Problema 23: dopo lo stop, con il conto sotto il 65% del capitale di partenza, «riparti» non riaccende e scrive un allarme;
    con un capitale nuovo del proprietario sì, e la decisione di G1 riparte da zero con quello."""
    monkeypatch.setattr(dm, "filtri_veri", lambda: {})
    monkeypatch.setattr(dm, "ATTESA_DOPO_CHIUSURA_S", 0.0)
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_riparti = tmp_path / "riparti"
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    finto.equity = "6400"                              # −36%: stop, e 64% del capitale di partenza
    d.tick(t0 + 61)
    assert d.carica()["fermo"]
    d.file_riparti.write_text("riparti 1")
    d.tick(t0 + 122)
    assert d.carica().get("fermo") and "non sopra il 65%" in fb.get_rtdb("/demo_binance/allarmi/riparti")["testo"]
    d.file_capitale = tmp_path / "capitale"
    d.file_capitale.write_text("5000")                 # il proprietario: un capitale nuovo, poi «riparti»
    d.file_riparti.write_text("riparti 2")
    d.tick(t0 + 183)
    assert "fermo" not in d.carica() and fb.get_rtdb("/demo_binance/allarmi/riparti") is None
    d.tick(t0 + 244)                                   # a metà giornata non riapre (decisione 3 dell'8 novembre)
    assert "conto_ridotto" not in d.carica()
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": 20751, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d.tick(20751 * 86400.0 + 400)                      # la decisione dopo: da zero con il capitale nuovo
    assert d.carica()["conto_ridotto"]["capitale"] == 5000.0


def test_sezione_del_conto_demo_con_gli_allarmi_nuovi():
    from scripts import state_snapshot as ss

    class Fb:
        def get_rtdb(self, k):
            return {"/demo_binance/stato": {"stato": "acceso", "equity": 1000.0, "capitale_iniziale": 1000.0},
                    "/demo_binance/allarmi": {"decisione_g1": {"ora": 1.7e9, "testo": "la decisione di G1 è del 2026-11-07"},
                                              "ordini": None}}.get(k)

    testo = "\n".join(ss.sezione_demo_binance(Fb()))
    assert "**ALLARME** decisione g1" in testo and "2026-11-07" in testo


# ---- seconda tornata della fase 1 (reviews/reports/2026-11-08-fase1-conto-vero.md): problemi 40-46 e decisioni 2-5 ----

_TROPPE = _Risposta({"code": -1003, "msg": "Too many requests"}, 429)


def test_40_stop_con_429_che_dura_resta_fermo(tmp_path, monkeypatch):
    """Prova p1: lo stop a −36% chiude AUSDT, la chiusura di BUSDT riceve 429 di fila. Il fermo è già scritto e salvato: anche se
    il conto risale a −34% il demo resta fermo, e BUSDT si chiude dopo l'attesa."""
    _attese(monkeypatch)
    finto = _Demo()
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    d.tick(t0 + 3700)                                  # ribilancio finito: AUSDT lungo, BUSDT corto
    assert finto.posizioni["AUSDT"] > 0 and finto.posizioni["BUSDT"] < 0
    finto.equity = "6400"
    _sempre(d, finto, "POST", "/fapi/v1/order", _TROPPE, simbolo="BUSDT")
    d.tick(t0 + 3761)
    st = d.carica()
    assert st["fermo"]["motivo"].startswith("stop sul conto") and st["fermo"]["tentativi"] == 1 and st["fermo"]["chiuse"] == 1
    assert fb.get_rtdb("/demo_binance/fermo")["motivo"].startswith("stop") and finto.posizioni["AUSDT"] == 0.0
    d._cliente.http = finto
    finto.equity = "6600"                              # risale a −34%
    for k in range(1, 6):
        d.tick(t0 + 3761 + 130 * k)
    assert d.carica().get("fermo") and finto.posizioni["BUSDT"] == 0.0


def test_40_da_fermo_con_429_che_dura_i_tentativi_crescono(tmp_path, monkeypatch):
    """Prova p3: da fermo, BUSDT non si chiude per un 429 che dura: i tentativi crescono e al terzo arriva l'allarme del fermo."""
    _attese(monkeypatch)
    finto = _Demo()
    finto.posizioni, finto.posizioni_vive = {"BUSDT": -20.0}, True
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("chiudi 1")
    finto.guasti[("POST", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)                                         # fermo con BUSDT aperto
    _sempre(d, finto, "POST", "/fapi/v1/order", _TROPPE, simbolo="BUSDT")
    for k in range(1, 11):
        d.tick(t0 + 61 * k)
    st = d.carica()
    assert st["fermo"]["tentativi"] >= 3 and "limiti di Binance" in st["fermo"]["errori"][-1]["errore"]
    assert "il conto non è vuoto dopo" in fb.get_rtdb("/demo_binance/allarme")["testo"] and finto.posizioni["BUSDT"] == -20.0


def test_41_capitale_oltre_il_valore_vero_del_conto_non_si_usa(tmp_path, monkeypatch):
    """Prova p10: conto demo da 5.000, nel file 9.999: il capitale non si usa (ordini come per il conto vero, non per il 197%)."""
    monkeypatch.setattr(dm, "filtri_veri", lambda: {})
    monkeypatch.setattr(dm, "ATTESA_DOPO_CHIUSURA_S", 0.0)
    finto = _Demo()
    finto.equity = "5000"
    d, fb = _demo_semplice(tmp_path, finto)
    (tmp_path / "capitale").write_text("9999")
    d.file_capitale = tmp_path / "capitale"
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    st = d.carica()
    assert "conto_ridotto" not in st and "capitale_in_attesa" not in st
    assert "sopra il valore vero" in fb.get_rtdb("/demo_binance/allarmi/capitale")["testo"]
    limite = {q["symbol"]: float(q["quantity"]) for q in _post(finto) if q["type"] == "LIMIT"}
    assert limite["AUSDT"] == pytest.approx(0.5 * 5000 / 100.003, abs=0.001)
    d.tick(t0 + 60)                                    # resta rifiutato, l'allarme resta
    assert "capitale_in_attesa" not in d.carica() and fb.get_rtdb("/demo_binance/allarmi/capitale")


def test_44_attesa_di_binance_con_un_tetto_di_10_minuti(tmp_path, monkeypatch):
    """Problema 44: un Retry-After di un giorno su un 429 ferma pulsante e stop al massimo 10 minuti, con l'allarme che lo dice."""
    _attese(monkeypatch)
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    finto.guasti[("GET", "/fapi/v2/account", None)] = _Risposta({"code": -1003}, 429, headers={"Retry-After": "86400"})
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    assert "chiedeva 86400 secondi" in fb.get_rtdb("/demo_binance/allarmi/limiti_binance")["testo"]
    n = len(finto.chiamate)
    d.tick(t0 + 599)
    assert len(finto.chiamate) == n
    d.tick(t0 + 601)                                   # dopo 10 minuti si riprova
    assert len(finto.chiamate) > n and fb.get_rtdb("/demo_binance/allarmi/limiti_binance") is None


@pytest.mark.parametrize("retry_after, attesa", [("86400", 86400), (None, 600)])
def test_44_un_418_rispetta_tutto_il_blocco_senza_tetto(tmp_path, monkeypatch, retry_after, attesa):
    """Problema 44, correzione dell'8 novembre: il tetto dei 10 minuti vale solo per il 429. Un 418 (indirizzo bloccato) si rispetta
    per intero, perché chi riprova durante il blocco lo allunga; senza Retry-After 10 minuti. L'allarme dice fino a quando, e che in
    quel tempo il bot non protegge il conto."""
    _attese(monkeypatch)
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    finto.guasti[("GET", "/fapi/v2/account", None)] = _Risposta({"code": -1003, "msg": "banned"}, 418,
                                                                 headers={"Retry-After": retry_after} if retry_after else None)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    testo = fb.get_rtdb("/demo_binance/allarmi/limiti_binance")["testo"]
    fino = dm.time.strftime("%H:%M:%S UTC del %Y-%m-%d", dm.time.gmtime(t0 + attesa))
    assert f"fino alle {fino}" in testo and "non può proteggere il conto" in testo
    n = len(finto.chiamate)
    d.tick(t0 + 601 if attesa > 601 else t0 + attesa - 1)
    d.tick(t0 + attesa - 1)
    assert len(finto.chiamate) == n                    # nessuna richiesta durante il blocco
    d.tick(t0 + attesa + 1)
    assert len(finto.chiamate) > n


def test_44_errore_d_orario_rilegge_l_ora_di_binance_e_riprova_una_volta(tmp_path):
    """Problema 44: con -1021 si legge l'ora di Binance e si riprova una volta con l'ora corretta; un secondo -1021 è un rifiuto."""
    finto = _Demo()
    finto.scarto_ora_ms = 3000                         # Binance avanti di 3 secondi
    c = dm.ClienteDemo("chiave", "segreto", http=finto)
    fuori = _Risposta({"code": -1021, "msg": "Timestamp for this request was 1000ms ahead of the server's time."}, 400)
    finto.guasti[("GET", "/fapi/v2/account", None)] = fuori
    assert c.chiedi("GET", "/fapi/v2/account", firmata=True)["totalMarginBalance"] == "10000"
    assert [p for m, p, q in finto.chiamate].count("/fapi/v1/time") == 1
    ultima = finto.chiamate[-1][2]
    assert abs(int(ultima["timestamp"]) - (time.time() * 1000 + 3000)) < 1000
    chiamate = []
    def sempre_fuori(m, url, **k):                     # l'orario resta fuori anche dopo la rilettura: una volta sola, poi rifiuto
        chiamate.append(urlparse(url).path)
        return fuori if "/fapi/v2/account" in url else finto(m, url, **k)
    c2 = dm.ClienteDemo("chiave", "segreto", http=sempre_fuori)
    with pytest.raises(RuntimeError, match="-1021"):
        c2.chiedi("GET", "/fapi/v2/account", firmata=True)
    assert chiamate == ["/fapi/v2/account", "/fapi/v1/time", "/fapi/v2/account"]


def test_45_decisione_di_g1_con_la_data_nel_futuro(tmp_path):
    """Problema 45: una decisione con la data nel futuro non si esegue (prima bloccava per sempre le decisioni vere); un giorno
    nel futuro rimasto nello stato si azzera."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto, giorno=99999)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    assert _post(finto) == [] and "nel futuro" in fb.get_rtdb("/demo_binance/allarmi/decisione_g1")["testo"]
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": 20750, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d.tick(t0 + 60)
    assert {q["symbol"] for q in _post(finto) if q["type"] == "LIMIT"} == {"AUSDT", "BUSDT"}
    assert fb.get_rtdb("/demo_binance/allarmi/decisione_g1") is None
    finto2 = _Demo()
    (tmp_path / "due").mkdir()
    d2, fb2 = _demo_semplice(tmp_path / "due", finto2)
    d2.salva({"ultimo_giorno": 99999})                 # lo stato di un demo che aveva eseguito una data nel futuro
    d2.tick(t0)
    assert {q["symbol"] for q in _post(finto2) if q["type"] == "LIMIT"} == {"AUSDT", "BUSDT"}


def test_42_pesi_di_g1_vuoti_niente_ordini_e_allarme(tmp_path):
    """Prova p9: G1 scrive pesi vuoti: prima il demo chiudeva tutto senza allarme; ora la decisione salta (come una moneta sopra il
    60%) e c'è l'allarme."""
    finto = _Demo()
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    d.tick(t0 + 3700)
    prima = dict(finto.posizioni)
    n = len(_post(finto))
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": 20751, "pesi": {}}))
    d.tick(20751 * 86400.0 + 400)
    assert len(_post(finto)) == n and finto.posizioni == prima
    assert "vuoti" in fb.get_rtdb("/demo_binance/allarmi/pesi")["testo"]
    assert dm.pesi_fuori_dai_limiti({}, {}) == "pesi di G1 vuoti"


def test_46_allarme_degli_ordini_spento_dal_pulsante(tmp_path):
    """Problema 46: l'allarme degli ordini bloccati si spegne quando il pulsante toglie gli ordini."""
    finto, d, fb, t1 = _ordine_bloccato(tmp_path)
    passo = dm.ATTESA_DOPO_ERRORE_S + 10
    for k in range(5):
        finto.guasti[("DELETE", "/fapi/v1/order", "BUSDT")] = _rifiutata()
        d.tick(t1 + k * passo)
    assert fb.get_rtdb("/demo_binance/allarmi/ordini")
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("chiudi 1")
    d.tick(t1 + 5 * passo)
    assert d.carica()["fermo"] and fb.get_rtdb("/demo_binance/allarmi/ordini") is None


def test_46_allarmi_gia_scritti_si_spengono_anche_con_lo_stato_perso(tmp_path):
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    fb.set_rtdb("/demo_binance/allarmi/decisione_g1", {"ora": 1.0, "testo": "la decisione di G1 è del 2026-10-20"})
    d.tick(20750 * 86400.0 + 400)                      # nessuno stato: la decisione è fresca, l'allarme vecchio si spegne
    assert fb.get_rtdb("/demo_binance/allarmi/decisione_g1") is None


def test_46_riparti_della_dashboard_non_si_perde_con_un_errore(tmp_path):
    """Problema 46: se il controllo del pavimento va in errore, il «riparti» della dashboard resta e vale al giro dopo."""
    import requests
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("chiudi 1")
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    assert d.carica()["fermo"]
    fb.set_rtdb(dm.COMANDO_RIPARTI, True)
    finto.guasti[("GET", "/fapi/v2/account", None)] = requests.exceptions.ReadTimeout("rete")
    d.tick(t0 + 61)                                    # il controllo del pavimento non legge il conto
    assert d.carica().get("fermo") and fb.get_rtdb(dm.COMANDO_RIPARTI) is True
    d.tick(t0 + 122)
    assert "fermo" not in d.carica() and fb.get_rtdb(dm.COMANDO_RIPARTI) is False


def test_46_blocchi_di_fila_non_al_confine_di_un_ora(tmp_path):
    """Problema 46: un blocco, un tentativo in mezzo con un altro errore, un blocco nuovo esattamente un'ora dopo: si riparte."""
    import requests
    finto, d, fb, t1 = _ordine_bloccato(tmp_path)
    finto.guasti[("DELETE", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    d.tick(t1)
    finto.guasti[("GET", "/fapi/v1/order", "BUSDT")] = requests.exceptions.ReadTimeout("rete")
    d.tick(t1 + dm.ATTESA_DOPO_ERRORE_S)
    finto.guasti[("DELETE", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    d.tick(t1 + 2 * dm.ATTESA_DOPO_ERRORE_S)
    assert d.carica()["ordini"]["bloccato_dal"] == t1 + 2 * dm.ATTESA_DOPO_ERRORE_S


def test_decisione_2_lo_stop_anche_al_pavimento_del_capitale(tmp_path):
    """Revisione dell'8 novembre, decisione 2: dopo un «riparti» lo stop scatta al più alto fra il −35% dal massimo e il 65% del
    capitale di partenza: la perdita totale resta entro il 35% del capitale (prima, dopo il «riparti» a 6.600 si arrivava a 4.290)."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_riparti = tmp_path / "riparti"
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    finto.equity = "10500"
    d.tick(t0 + 61)
    finto.equity = "6600"                              # −37% dal massimo: stop
    d.tick(t0 + 122)
    assert d.carica()["fermo"]["motivo"].startswith("stop sul conto: -37.1% dal massimo")
    d.file_riparti.write_text("riparti 1")             # 66% del capitale: «riparti» vale
    d.tick(t0 + 183)
    assert "fermo" not in d.carica() and d.carica()["massimo"] == 6600.0
    finto.equity = "6450"                              # −2,3% dal massimo nuovo, ma sotto il 65% del capitale
    d.tick(t0 + 244)
    assert d.carica()["fermo"]["motivo"] == "stop sul conto: -35.5% dal capitale di partenza della fase"
    assert dm.livello_di_stop({"massimo": 6600.0, "capitale_iniziale": 10000.0}) == pytest.approx(6500.0)


def test_decisione_3_dopo_riparti_si_aspetta_la_decisione_di_g1(tmp_path):
    """Revisione dell'8 novembre, decisione 3: dopo un «riparti» il conto resta vuoto fino alla prima decisione di G1 dopo il
    «riparti» (alle 00:02 la decisione delle 00:05 vale, quella di ieri no)."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_chiudi, d.file_riparti = tmp_path / "chiudi", tmp_path / "riparti"
    d.tick(20750 * 86400.0 + 400)
    d.file_chiudi.write_text("chiudi 1")
    d.tick(20751 * 86400.0 + 60)
    assert d.carica()["fermo"]
    n = len(_post(finto))
    d.file_riparti.write_text("riparti 1")
    d.tick(20751 * 86400.0 + 120)                      # 00:02: riparte, G1 non ha ancora deciso
    d.tick(20751 * 86400.0 + 180)
    assert "fermo" not in d.carica() and len(_post(finto)) == n
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": 20751, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    d.tick(20751 * 86400.0 + 300)                      # 00:05: la decisione nuova
    assert {q["symbol"] for q in _post(finto)[n:] if q["type"] == "LIMIT"} == {"AUSDT", "BUSDT"}
    assert "riparti_attende_g1" not in d.carica()


def test_decisione_4_i_limiti_del_demo_sono_fissi():
    """Revisione dell'8 novembre, decisione 4: i limiti restano costanti in demo_binance.py (in hard_limits.py serve l'ok del
    proprietario). Questo test li fissa: cambiarne uno deve essere una scelta, non un incidente."""
    assert (dm.LEVA, dm.STOP_CONTO, dm.PAVIMENTO_RIPARTI) == (5, 0.35, 0.65)
    assert (dm.SOMMA_PESI_MASSIMA, dm.PESO_MASSIMO_MONETA, dm.ETA_MASSIMA_DECISIONE_S) == (2.5, 0.60, 26 * 3600)
    assert (dm.CAPITALE_MASSIMO, dm.DATA_FILTRI_VERI, dm.ETA_MASSIMA_FILTRI_GIORNI) == (10_000.0, "2026-11-06", 30)
    assert (dm.RITENTATIVI_LIMITE, dm.ATTESE_LIMITE_S, dm.ATTESA_LIMITE_MAX_S) == (3, (1.0, 2.0, 4.0), 10.0)
    assert (dm.ATTESA_DOPO_LIMITE_S, dm.ATTESA_LIMITE_TETTO_S, dm.PEZZI_MASSIMI) == (120.0, 600.0, 20)
    assert dm.ATTESA_418_SENZA_RETRY_S == 600.0
    assert (dm.TENTATIVI_PRIMA_DELL_ALLARME, dm.OGNI_CONTROLLO_STOP_S, dm.HOST_DEMO) == (3, 60, "demo-fapi.binance.com")


def _demo_con_massimo_a_mercato(tmp_path):
    b = [_BASE[0], {"filterType": "LOT_SIZE", "stepSize": "0.001", "minQty": "0.001"}, _BASE[2],
         {"filterType": "MARKET_LOT_SIZE", "stepSize": "0.001", "minQty": "0.001", "maxQty": "120"}]
    finto = _DemoFiltri({"AUSDT": _BASE, "BUSDT": b})
    finto.posizioni, finto.posizioni_vive = {"AUSDT": 0.0, "BUSDT": -250.0, "CUSDT": 5.0}, True    # CUSDT non è nei filtri
    d, fb = _demo_semplice(tmp_path, finto)
    return finto, d, fb


def test_43_chiusure_divise_dentro_la_quantita_massima(tmp_path):
    """Problema 43: una chiusura oltre la quantità massima a mercato parte in pezzi (prima: un ordine solo, rifiutato ogni minuto)."""
    finto, d, fb = _demo_con_massimo_a_mercato(tmp_path)
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("chiudi 1")
    d.tick(20750 * 86400.0 + 400)
    assert [q["quantity"] for q in _mercato(finto, "BUSDT")] == ["120", "120", "10"]
    assert finto.posizioni["BUSDT"] == 0.0 and finto.posizioni["CUSDT"] == 0.0
    assert dm.pezzi_di_chiusura(-0.25, 0.1, 0.001) == [0.1, 0.1, 0.05] and dm.pezzi_di_chiusura(5, float("inf"), 1) == [5.0]


def test_43_posizione_su_una_moneta_senza_filtri_da_allarme(tmp_path):
    """Problema 43: il ribilancio non può ridurre una posizione su una moneta senza filtri: allarme (la chiude il pulsante)."""
    finto, d, fb = _demo_con_massimo_a_mercato(tmp_path)
    d.tick(20750 * 86400.0 + 400)
    assert "CUSDT" in fb.get_rtdb("/demo_binance/allarmi/monete_senza_filtri")["testo"]


# ---- terza tornata della fase 1 (reviews/reports/2026-11-08-fase1-conto-vero-2.md): problemi 47-49 ----

def test_47_pavimento_resta_con_le_posizioni_aperte_e_un_capitale_in_attesa(tmp_path):
    """Prova p11: dopo stop e «riparti» nella stessa fase, un capitale nuovo scritto di giorno non toglie il pavimento finché la fase
    vecchia ha le posizioni aperte: a 6.000 (sotto il 65% di 10.000) il demo si ferma."""
    finto = _Demo()
    finto.posizioni_vive = True
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_riparti = tmp_path / "riparti"
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    finto.equity = "11000"
    d.tick(t0 + 61)
    finto.equity = "7100"                              # −35,5% da 11.000: stop
    d.tick(t0 + 122)
    d.file_riparti.write_text("r1")
    d.tick(t0 + 183)
    assert "fermo" not in d.carica()
    (tmp_path / "g1.json").write_text(json.dumps({"ultimo_lunedi": 20751, "pesi": {"AUSDT": 0.5, "BUSDT": -0.5}}))
    t1 = 20751 * 86400.0 + 400
    d.tick(t1)                                         # riapre con la decisione dopo
    d.tick(t1 + 3700)
    assert finto.posizioni["AUSDT"] > 0 and finto.posizioni["BUSDT"] < 0
    (tmp_path / "capitale").write_text("2000")
    d.file_capitale = tmp_path / "capitale"
    d.tick(t1 + 3760)
    assert d.carica()["capitale_in_attesa"] == 2000.0 and dm.livello_di_stop(d.carica()) == pytest.approx(6500.0)
    finto.equity = "6000"
    d.tick(t1 + 3830)
    assert d.carica()["fermo"]["motivo"].endswith("dal capitale di partenza della fase")


def test_48_riparti_con_il_conto_non_vuoto_non_si_accetta(tmp_path):
    """Prova p16: una chiusura fallita lascia BUSDT aperto; il «riparti» non si accetta (il comando si consuma, allarme), il demo
    resta fermo e al minuto dopo richiude BUSDT."""
    finto = _Demo()
    finto.posizioni, finto.posizioni_vive = {"BUSDT": -20.0}, True
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_chiudi, d.file_riparti = tmp_path / "chiudi", tmp_path / "riparti"
    d.file_chiudi.write_text("chiudi 1")
    finto.guasti[("POST", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)                                         # fermo con BUSDT aperto
    d.file_riparti.write_text("r1")
    d.tick(t0 + 30)                                    # «riparti» prima del minuto dopo
    st = d.carica()
    assert st.get("fermo") and st["eseguito_riparti"] == "r1"
    assert "il conto non è vuoto (posizioni: BUSDT" in fb.get_rtdb("/demo_binance/allarmi/riparti")["testo"]
    d.tick(t0 + 61)
    assert d.carica().get("fermo") and finto.posizioni["BUSDT"] == 0.0
    d.file_riparti.write_text("r2")                    # ora il conto è vuoto: vale
    d.tick(t0 + 122)
    assert "fermo" not in d.carica() and fb.get_rtdb("/demo_binance/allarmi/riparti") is None


def test_48_riparti_al_livello_dello_stop_non_si_accetta(tmp_path):
    """Prova p12: un «riparti» con il conto esattamente al pavimento (6.500 su 10.000) non si accetta: prima ripartiva e al minuto dopo
    lo stop lo fermava di nuovo. Appena sopra si accetta e resta acceso."""
    finto = _Demo()
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_riparti = tmp_path / "riparti"
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    finto.equity = "6400"
    d.tick(t0 + 61)
    finto.equity = "6500"
    d.file_riparti.write_text("r1")
    d.tick(t0 + 122)
    assert d.carica().get("fermo") and "non sopra il 65%" in fb.get_rtdb("/demo_binance/allarmi/riparti")["testo"]
    finto.equity = "6501"
    d.file_riparti.write_text("r2")
    d.tick(t0 + 183)
    d.tick(t0 + 244)
    assert "fermo" not in d.carica()


def test_49_da_fermo_con_tutte_le_richieste_limitate_i_tentativi_crescono(tmp_path, monkeypatch):
    """Prova p13: da fermo, con un 429 su tutte le richieste (anche la lettura del conto), i tentativi crescono e al terzo arriva
    l'allarme del fermo."""
    _attese(monkeypatch)
    finto = _Demo()
    finto.posizioni, finto.posizioni_vive = {"BUSDT": -20.0}, True
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_chiudi = tmp_path / "chiudi"
    d.file_chiudi.write_text("chiudi 1")
    finto.guasti[("POST", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)
    d._cliente.http = lambda m, url, headers=None, timeout=None: _TROPPE
    for k in range(1, 11):
        d.tick(t0 + 61 * k)
    st = d.carica()
    assert st["fermo"]["tentativi"] >= 3
    assert "il conto non si legge" in fb.get_rtdb("/demo_binance/allarme")["testo"]


def test_49_niente_pezzo_oltre_i_20():
    """Problema 49: una chiusura si ferma a 20 pezzi (prima un ventunesimo con tutto il resto, oltre il massimo, rifiutato)."""
    assert dm.pezzi_di_chiusura(25, 1, 1) == [1.0] * dm.PEZZI_MASSIMI
    assert dm.pezzi_di_chiusura(21, 1, 1) == [1.0] * 20 and dm.pezzi_di_chiusura(20, 1, 1) == [1.0] * 20


def test_49_la_fotografia_dice_il_livello_vero_dello_stop():
    from scripts import state_snapshot as ss

    class Fb:
        def get_rtdb(self, k):
            return {"/demo_binance/stato": {"stato": "acceso", "equity": 6600.0, "capitale_iniziale": 10000.0, "massimo": 6600.0,
                                            "stop_a": 6500.0, "dal_massimo": 0.0}}.get(k)

    testo = "\n".join(ss.sezione_demo_binance(Fb()))
    assert "si chiude tutto sotto $6,500.00 (il più alto fra −35% dal massimo, $6,600.00, e il 65% del capitale" in testo


@pytest.mark.parametrize("dove", ["file", "dashboard"])
def test_50_riparti_in_attesa_con_gli_ordini_illeggibili_non_ferma_le_chiusure(tmp_path, dove):
    """Revisione dell'8 novembre 2026, problema 50: da fermo con BUSDT rimasto aperto e `openOrders` sempre in errore (503), un
    «riparti» in attesa non deve fermare le chiusure del minuto: BUSDT si richiude, il comando resta per il giro dopo e vale quando
    gli ordini tornano leggibili (prima l'errore della lettura nel controllo del «riparti» usciva prima della richiusura)."""
    finto = _Demo()
    finto.posizioni, finto.posizioni_vive = {"BUSDT": -20.0}, True
    d, fb = _demo_semplice(tmp_path, finto)
    d.file_chiudi, d.file_riparti = tmp_path / "chiudi", tmp_path / "riparti"
    d.file_chiudi.write_text("chiudi 1")
    finto.guasti[("POST", "/fapi/v1/order", "BUSDT")] = _rifiutata()
    t0 = 20750 * 86400.0 + 400
    d.tick(t0)                                         # fermo con BUSDT aperto (la chiusura è stata rifiutata)
    assert d.carica().get("fermo") and finto.posizioni["BUSDT"] == -20.0
    _sempre(d, finto, "GET", "/fapi/v1/openOrders", _Risposta({"code": -1001, "msg": "servizio"}, 503))
    if dove == "file":
        d.file_riparti.write_text("r1")
    else:
        fb.set_rtdb(dm.COMANDO_RIPARTI, True)
    for k in range(1, 4):
        d.tick(t0 + 61 * k)
    st = d.carica()
    assert finto.posizioni["BUSDT"] == 0.0             # le chiusure del minuto sono andate avanti
    assert st.get("fermo")                             # e il «riparti» non è stato accettato al buio
    if dove == "file":
        assert st.get("eseguito_riparti") != "r1"      # il comando del file resta da eseguire
    else:
        assert fb.get_rtdb(dm.COMANDO_RIPARTI) is True  # quello della dashboard non si è consumato
    d._cliente.http = finto                            # gli ordini tornano leggibili: il «riparti» vale
    d.tick(t0 + 61 * 5)
    assert "fermo" not in d.carica()
