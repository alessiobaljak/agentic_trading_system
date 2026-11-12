"""La sezione di sola lettura dello stato con esecuzioni, commissioni e funding del conto demo (scripts/state_snapshot.py, backlog P33):
le righe attese, un errore di Binance che non ferma lo stato, solo GET verso i tre indirizzi elencati. Nessuna rete: cliente finto."""
import calendar

import pytest

from bot.portafoglio.demo_binance import ClienteDemo, LimiteBinance
from scripts import state_snapshot as ss

AMMESSI = {"/fapi/v1/userTrades", "/fapi/v1/commissionRate", "/fapi/v1/income"}


def _ms(g, h, m=0):
    a, me, d = (int(x) for x in g.split("-"))
    return calendar.timegm((a, me, d, h, m, 0)) * 1000


ORA = _ms("2026-11-12", 10) / 1000
FUNDING = [
    {"symbol": "AAAUSDT", "incomeType": "FUNDING_FEE", "income": "0.5", "asset": "USDT", "time": _ms("2026-11-10", 0), "tranId": 1},
    {"symbol": "AAAUSDT", "incomeType": "FUNDING_FEE", "income": "0.3", "asset": "USDT", "time": _ms("2026-11-10", 8), "tranId": 2},
    {"symbol": "AAAUSDT", "incomeType": "FUNDING_FEE", "income": "0.2", "asset": "USDT", "time": _ms("2026-11-10", 16), "tranId": 3},
    {"symbol": "BBBUSDT", "incomeType": "FUNDING_FEE", "income": "-0.4", "asset": "USDT", "time": _ms("2026-11-10", 8), "tranId": 4},
    {"symbol": "CCCUSDT", "incomeType": "FUNDING_FEE", "income": "0.1", "asset": "USDT", "time": _ms("2026-11-11", 4), "tranId": 5},
    {"symbol": "AAAUSDT", "incomeType": "FUNDING_FEE", "income": "0.25", "asset": "USDT", "time": _ms("2026-11-12", 8), "tranId": 6},
]
COMMISSIONI = [
    {"symbol": "AAAUSDT", "incomeType": "COMMISSION", "income": "-0.10", "asset": "USDT", "time": _ms("2026-11-10", 0, 30), "tranId": 7},
    {"symbol": "BBBUSDT", "incomeType": "COMMISSION", "income": "-0.05", "asset": "USDT", "time": _ms("2026-11-11", 0, 20), "tranId": 8},
]
ESECUZIONI = {
    "AAAUSDT": [{"id": 1, "symbol": "AAAUSDT", "quoteQty": "100", "commission": "0.02", "commissionAsset": "USDT", "maker": True,
                 "time": _ms("2026-11-10", 0, 30)},
                {"id": 2, "symbol": "AAAUSDT", "quoteQty": "50", "commission": "-0.025", "commissionAsset": "USDT", "maker": False,
                 "time": _ms("2026-11-10", 1, 10)}],
    "BBBUSDT": [{"id": 3, "symbol": "BBBUSDT", "quoteQty": "200", "commission": "0.04", "commissionAsset": "USDT", "maker": True,
                 "time": _ms("2026-11-11", 0, 20)}],
}
FIREBASE = {
    "/paper_g1/posizioni": {"AAAUSDT": 0.05, "DDDUSDT": -0.02, "EEEUSDT": 0.0},
    "/paper_g1/diario": {"2026-11-10": {"equity": 1000, "long": 30, "short": 28}},
    "/demo_binance/ribilanciamenti": {
        "2026-11-01": {"monete_mancanti_sul_demo": ["VECCHIAUSDT"]},
        "2026-11-09": {"monete_mancanti_sul_demo": ["IRYSUSDT"], "rifiutati": [{"simbolo": "龙虾USDT", "errore": "-1121"}]},
        "2026-11-10": {"monete_mancanti_sul_demo": ["IRYSUSDT"], "rifiutati": [{"simbolo": "龙虾USDT", "errore": "-1121"}]},
        "2026-11-10-eventi-0130": {"solo_eventi": True, "monete_mancanti_sul_demo": ["EVENTIUSDT"]},
    },
}


class _Fb:
    def __init__(self, dati=None, rompi=False):
        self.dati, self.rompi = dati or {}, rompi

    def get_rtdb(self, ramo):
        if self.rompi:
            raise RuntimeError("firebase giù")
        return self.dati.get(ramo)


class _Cliente:
    """Il cliente finto del demo: registra ogni chiamata e risponde come Binance (righe dall'ora di inizio, al massimo ``limit``)."""

    def __init__(self, errori=None):
        self.chiamate, self.errori = [], errori or {}

    def chiedi(self, metodo, percorso, parametri=None, firmata=False):
        p = dict(parametri or {})
        self.chiamate.append((metodo, percorso, p, firmata))
        chiave = (percorso, p.get("incomeType") or p.get("symbol"))
        if chiave in self.errori:
            raise self.errori[chiave]
        if percorso in self.errori:
            raise self.errori[percorso]
        if percorso == "/fapi/v1/commissionRate":
            return {"symbol": "BTCUSDT", "makerCommissionRate": "0.000200", "takerCommissionRate": "0.000500"}
        righe = {"FUNDING_FEE": FUNDING, "COMMISSION": COMMISSIONI}.get(p.get("incomeType")) if percorso == "/fapi/v1/income" \
            else ESECUZIONI.get(p.get("symbol"), [])
        return [r for r in righe if p["startTime"] <= r["time"] <= p["endTime"]][: int(p.get("limit") or 500)]


def _sezione(cliente, fb=None, **kw):
    pause = []
    righe = ss.sezione_demo_esecuzioni(_Fb(FIREBASE) if fb is None else fb, cliente=cliente, now=ORA, dormi=pause.append, **kw)
    return "\n".join(righe), pause


def test_la_sezione_scrive_le_righe_attese():
    c = _Cliente()
    testo, pause = _sezione(c)
    assert testo.startswith("## G1 sul demo: esecuzioni, commissioni e funding")
    assert "Dal 2026-11-07 00:00 a 2026-11-12 10:00 UTC" in testo
    assert "- commissione del conto (BTCUSDT): maker 0.0200%, taker 0.0500%" in testo
    # le esecuzioni: valore, commissione (in valore assoluto), % del valore, quota maker e taker, numero
    assert "Esecuzioni (`userTrades`) lette per 2 monete su 2" in testo
    assert "| 2026-11-10 | 150.00 | 0.0450 | 0.0300% | 67% | 33% | 2 |" in testo
    assert "| 2026-11-11 | 200.00 | 0.0400 | 0.0200% | 100% | 0% | 1 |" in testo
    assert "| 2026-11-07 | 0 | 0 | — | — | — | 0 |" in testo
    assert "| 6 giorni | 350.00 | 0.0850 | 0.0243% | 86% | 14% | 3 |" in testo
    assert "commissioni dagli incassi 0.1500 USDT, dalle esecuzioni 0.0850 USDT" in testo
    # il funding per giorno e regolamento, con le monete pagate alle 16 sul demo e quelle del paper
    assert "| 2026-11-10 | +0.6000 | +0.5000 | -0.1000 | +0.2000 | +0.0000 | 1/58 |" in testo
    assert "| 2026-11-11 | +0.1000 | +0.0000 | +0.0000 | +0.0000 | +0.1000 | —/— |" in testo
    assert "| 2026-11-12 (in corso) | +0.2500 | +0.0000 | +0.2500 | +0.0000 | +0.0000 | 1/— |" in testo
    # le monete con il funding più grande nei giorni chiusi (oggi escluso), con il peso nel paper
    righe = testo.splitlines()
    i = righe.index("| moneta | 5 giorni | 00 | 08 | 16 | altre ore | peso paper |")
    assert righe[i + 2] == "| AAAUSDT | +1.0000 | +0.5000 | +0.3000 | +0.2000 | +0.0000 | +5.00% |"
    assert righe[i + 3].startswith("| BBBUSDT | -0.4000 |") and righe[i + 3].endswith("| — |")
    assert righe[i + 4].startswith("| CCCUSDT | +0.1000 |")
    # le monete del paper che il demo non ha avuto: solo i giorni della finestra, senza i ribilanciamenti dei soli eventi
    assert "IRYSUSDT mancante sul demo 2 giorni dal 2026-11-09" in testo and "龙虾USDT rifiutata 2 giorni dal 2026-11-09" in testo
    assert "VECCHIAUSDT" not in testo and "EVENTIUSDT" not in testo
    assert "senza funding sul demo dalle 02 UTC: 1 monete su 2, peso lordo 2.00%: DDDUSDT -2.00%" in testo
    # richieste e peso: commissione 20, due incassi 30, due monete 5
    assert "richieste a Binance di questa sezione: 5, peso 90" in testo
    assert [x[2].get("symbol") for x in c.chiamate if x[1] == "/fapi/v1/userTrades"] == ["AAAUSDT", "BBBUSDT"]
    assert pause == [ss.PAUSA_TRA_RICHIESTE_S] * 4
    assert len(testo.splitlines()) <= 60


def test_solo_get_firmate_verso_i_tre_indirizzi():
    c = _Cliente()
    _sezione(c)
    assert c.chiamate and all(m == "GET" and firmata and p in AMMESSI for m, p, _, firmata in c.chiamate)
    for m, p, par, _ in c.chiamate:
        if p != "/fapi/v1/commissionRate":
            assert par["endTime"] - par["startTime"] < 7 * 86400_000      # userTrades: al massimo 7 giorni per richiesta


def test_un_errore_di_binance_non_ferma_lo_stato():
    # la commissione del conto risponde 500, il funding dà il limite di Binance: le richieste dopo non partono più
    c = _Cliente({"/fapi/v1/commissionRate": RuntimeError("GET /fapi/v1/commissionRate: 500 errore"),
                  ("/fapi/v1/income", "FUNDING_FEE"): LimiteBinance("GET /fapi/v1/income: 429 dopo 4 tentativi", 120.0)})
    testo, _ = _sezione(c)
    assert "- commissione del conto: non letta: RuntimeError: GET /fapi/v1/commissionRate: 500" in testo
    assert "- funding: non letto: LimiteBinance: GET /fapi/v1/income: 429" in testo
    assert "esecuzioni: non lette: servono gli incassi" in testo
    assert len(c.chiamate) == 2
    # una moneta che non risponde: le altre si leggono
    c = _Cliente({("/fapi/v1/userTrades", "AAAUSDT"): RuntimeError("GET /fapi/v1/userTrades: 400 {}")})
    testo, _ = _sezione(c)
    assert "lette per 1 monete su 2; non lette 1: RuntimeError: GET /fapi/v1/userTrades: 400" in testo
    assert "| 2026-11-11 | 200.00 | 0.0400 |" in testo
    # Firebase che non risponde e un cliente che esplode in modo inatteso: la sezione resta una lista di righe
    testo, _ = _sezione(_Cliente(), fb=_Fb(rompi=True))
    assert "| 6 giorni | 350.00 |" in testo and "monete del paper G1 che il demo non ha avuto (ribilanciamenti del demo): nessuna" in testo

    class Rotto:
        def chiedi(self, *a, **k):
            raise KeyError("strano")
    testo, _ = _sezione(Rotto())
    assert testo.startswith("## G1 sul demo") and "non lett" in testo


def test_tetto_di_peso():
    c = _Cliente()
    testo, _ = _sezione(c, peso_massimo=60)
    assert "incassi delle commissioni: non letti: tetto di peso della sezione (60)" in testo
    assert "non lette 3: tetto di peso della sezione (60)" in testo       # le monete dal funding, nessuna letta
    assert not [x for x in c.chiamate if x[1] == "/fapi/v1/userTrades"]
    assert "richieste a Binance di questa sezione: 2, peso 50" in testo


def test_senza_chiave_niente_rete(monkeypatch):
    for k in ("BINANCE_DEMO_API_KEY", "BINANCE_DEMO_API_SECRET", "BINANCE_DEMO_PRIVATE_KEY_PATH"):
        monkeypatch.delenv(k, raising=False)
    import requests
    monkeypatch.setattr(requests, "request", lambda *a, **k: pytest.fail("nessuna richiesta senza chiave"))
    righe = ss.sezione_demo_esecuzioni(_Fb(), now=ORA)
    assert righe[1].startswith("- non letto: manca la chiave del conto demo")


class _Risposta:
    def __init__(self, dati, peso="42"):
        self.status_code, self.dati, self.headers, self.text = 200, dati, {"X-MBX-USED-WEIGHT-1M": peso}, ""

    def json(self):
        return self.dati


def test_la_funzione_di_sola_lettura_rifiuta_ordini_e_altri_indirizzi():
    chiamate = []
    c = ClienteDemo("k", "s", http=ss.SoloLettura(lambda m, u, **k: chiamate.append((m, u)) or _Risposta([])))
    for metodo, percorso in (("POST", "/fapi/v1/order"), ("DELETE", "/fapi/v1/allOpenOrders"), ("GET", "/fapi/v2/account"),
                             ("POST", "/fapi/v1/leverage"), ("GET", "/fapi/v1/openOrders")):
        with pytest.raises(ValueError, match="sola lettura"):
            c.chiedi(metodo, percorso, {"symbol": "BTCUSDT"}, firmata=True)
    assert chiamate == []
    assert c.chiedi("GET", "/fapi/v1/income", {"incomeType": "FUNDING_FEE"}, firmata=True) == []
    assert chiamate[0][0] == "GET" and chiamate[0][1].startswith("https://demo-fapi.binance.com/fapi/v1/income?")
    assert c.http.peso_usato == 42


def test_con_il_cliente_vero_del_demo_solo_get_sul_demo(monkeypatch):
    """Il percorso della macchina: chiavi dall'ambiente, ``ClienteDemo`` con la funzione di sola lettura; la rete è finta."""
    monkeypatch.setenv("BINANCE_DEMO_API_KEY", "chiave-finta")
    monkeypatch.setenv("BINANCE_DEMO_API_SECRET", "segreto-finto")
    monkeypatch.delenv("BINANCE_DEMO_PRIVATE_KEY_PATH", raising=False)
    from urllib.parse import parse_qs, urlparse
    viste = []

    def rete(metodo, url, **kw):
        u = urlparse(url)
        viste.append((metodo, u.hostname, u.path))
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        cliente = _Cliente()
        return _Risposta(cliente.chiedi(metodo, u.path, {k: (int(v) if k in ("startTime", "endTime", "limit") else v)
                                                          for k, v in q.items()}))
    import requests
    monkeypatch.setattr(requests, "request", rete)
    testo = "\n".join(ss.sezione_demo_esecuzioni(_Fb(FIREBASE), now=ORA, dormi=lambda s: None))
    assert viste and all(m == "GET" and h == "demo-fapi.binance.com" and p in AMMESSI for m, h, p in viste)
    assert "| 6 giorni | 350.00 | 0.0850 | 0.0243% | 86% | 14% | 3 |" in testo
    assert "peso usato dall'indirizzo nel minuto 42" in testo
    assert "chiave-finta" not in testo and "segreto-finto" not in testo and "signature" not in testo


def test_pagine_con_righe_alla_stessa_ora():
    righe = [{"id": i, "time": t} for i, t in enumerate([1, 2, 3, 4, 5])]

    class Lettore:
        def chiedi(self, percorso, p):
            return [r for r in righe if p["startTime"] <= r["time"] <= p["endTime"]][: p["limit"]]
    tutte, completo = ss._pagine(Lettore(), "/fapi/v1/income", {"startTime": 0, "endTime": 10}, lambda r: r["id"], limite=2)
    assert [r["id"] for r in tutte] == [0, 1, 2, 3, 4] and completo
    righe[:] = [{"id": i, "time": t} for i, t in enumerate([1, 1, 1, 2, 3])]
    tutte, completo = ss._pagine(Lettore(), "/fapi/v1/income", {"startTime": 0, "endTime": 10}, lambda r: r["id"], limite=2)
    assert not completo                      # una pagina intera alla stessa ora: si va avanti, e si dice che può mancare qualcosa
    assert {r["id"] for r in tutte} >= {0, 1, 3, 4}


@pytest.mark.parametrize("ora,vietata", [("23:49", False), ("23:50", True), ("00:24", True), ("01:44", True), ("01:45", False),
                                         ("10:00", False)])
def test_finestra_del_ribilancio_nessuna_richiesta(ora, vietata):
    """Revisione del 12 novembre 2026, problema 79: dalle 23:50 alle 01:45 UTC nessuna richiesta."""
    h, m = (int(x) for x in ora.split(":"))
    c = _Cliente()
    righe = ss.sezione_demo_esecuzioni(_Fb(FIREBASE), cliente=c, now=_ms("2026-11-12", h, m) / 1000, dormi=lambda s: None)
    if vietata:
        assert righe[1] == "- non letto: finestra del ribilancio del demo (23:50-01:45 UTC), richiedere dopo"
        assert c.chiamate == []
    else:
        assert c.chiamate and righe[1].startswith("- richieste a Binance di questa sezione:")


@pytest.mark.parametrize("codice", [429, 418])
def test_fermo_al_primo_429_o_418(codice, monkeypatch):
    """Problema 80: al primo 429 o 418 il filtro di sola lettura si ferma, senza ritentativi del cliente e senza attese."""
    chiamate = []

    def rete(metodo, url, **kw):
        chiamate.append(url)
        r = _Risposta({"code": -1003, "msg": "troppe"})
        r.status_code, r.headers = codice, {"Retry-After": "5"}
        return r
    import time as _time
    monkeypatch.setattr(_time, "sleep", lambda s: pytest.fail("nessuna attesa dentro il cliente"))
    c = ClienteDemo("k", "s", http=ss.SoloLettura(rete))
    with pytest.raises(ss.LimiteInLettura, match=f"Binance {codice} su GET /fapi/v1/income"):
        c.chiedi("GET", "/fapi/v1/income", {"incomeType": "FUNDING_FEE"}, firmata=True)
    assert len(chiamate) == 1
    # nella sezione: una sola richiesta, poi nessun'altra; la riga dice perché
    chiamate.clear()
    testo = "\n".join(ss.sezione_demo_esecuzioni(_Fb(FIREBASE), cliente=ClienteDemo("k", "s", http=ss.SoloLettura(rete)), now=ORA,
                                                 dormi=lambda s: None))
    assert len(chiamate) == 1
    assert f"- richieste a Binance di questa sezione: 1, peso 20 (userTrades 5, income 30, commissionRate 20); fermata: " \
           f"LimiteInLettura: Binance {codice} su GET /fapi/v1/commissionRate" in testo
    assert "funding: non letto: LimiteInLettura" in testo


def test_peso_usato_oltre_600_ferma_la_sezione():
    class Http:
        peso_usato = 601

    class Cliente(_Cliente):
        http = Http()
    c = Cliente()
    testo, _ = _sezione(c)
    assert len(c.chiamate) == 0 and "già usato 601 di peso nel minuto (oltre 600)" in testo


def test_monete_assenti_al_massimo_dieci():
    rib = {"2026-11-10": {"monete_mancanti_sul_demo": [f"M{i:02d}USDT" for i in range(13)]}}
    testo, _ = _sezione(_Cliente(), fb=_Fb({**FIREBASE, "/demo_binance/ribilanciamenti": rib}))
    assert "M09USDT" in testo and "M10USDT" not in testo and "e altre 3" in testo
