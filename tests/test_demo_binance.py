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
        self.equity = "10000"
        self.separati = set()
        self.margine = {}
        self.entrate = []                               # righe di /fapi/v1/income: (tipo, ms, importo, valuta)

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
    rib = fb.get_rtdb("/demo_binance/ribilanciamenti/2026-10-24")
    assert rib["entrate"] == 2 and rib["uscite"] == 0
    assert fb.get_rtdb("/demo_binance/diario/2026-10-24") == {"equity": 10000.0, "long": 0, "short": 0}


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
    # il pulsante «riparti»: al giro dopo si torna ai pesi di G1
    fb.set_rtdb(dm.COMANDO_RIPARTI, True)
    d.tick(t0 + 8000)
    assert "fermo" not in d.carica() and fb.get_rtdb(dm.COMANDO_RIPARTI) is False
    d.tick(t0 + 8100)
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
