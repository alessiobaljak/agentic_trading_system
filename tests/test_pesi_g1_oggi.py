"""La sezione di sola lettura dello stato con i pesi di oggi di G1, moneta per moneta, nel paper e sul demo
(scripts/state_snapshot.py, sezione_pesi_g1_oggi; MIGLIORARE_G1.md voci 8, 10 e 11; backlog P33). Nessuna rete: cliente finto."""
import calendar

import pytest

from bot.portafoglio.demo_binance import ClienteDemo
from scripts import state_snapshot as ss

ORA = calendar.timegm((2026, 11, 14, 4, 20, 0))
FIREBASE = {
    "/paper_g1/posizioni": {"AAAUSDT": 0.05, "BBBUSDT": -0.03, "龙虾USDT": -0.032, "ZEROUSDT": 0.0},
    "/demo_binance/stato": {"equity": 1000.0},
}
POSIZIONI = [
    {"symbol": "AAAUSDT", "positionAmt": "10", "notional": "48.0"},
    {"symbol": "BBBUSDT", "positionAmt": "-3", "notional": "-31.0"},
    {"symbol": "CCCUSDT", "positionAmt": "1", "notional": "6.0"},       # sul demo ma non nel paper (resto sotto il minimo)
    {"symbol": "DDDUSDT", "positionAmt": "0", "notional": "0"},         # chiusa: non si scrive
]


class _Fb:
    def __init__(self, dati=None, rompi=False):
        self.dati, self.rompi = dati if dati is not None else FIREBASE, rompi

    def get_rtdb(self, ramo):
        if self.rompi:
            raise RuntimeError("firebase giù")
        return self.dati.get(ramo)


class _Cliente:
    def __init__(self, errore=None, posizioni=None):
        self.chiamate, self.errore, self.posizioni = [], errore, POSIZIONI if posizioni is None else posizioni

    def chiedi(self, metodo, percorso, parametri=None, firmata=False):
        self.chiamate.append((metodo, percorso, dict(parametri or {}), firmata))
        if self.errore:
            raise self.errore
        return self.posizioni


def _testo(cliente, fb=None, now=ORA):
    return "\n".join(ss.sezione_pesi_g1_oggi(_Fb() if fb is None else fb, cliente=cliente, now=now, dormi=lambda s: None))


def test_la_sezione_scrive_i_pesi_di_paper_e_demo():
    c = _Cliente()
    testo = _testo(c)
    assert testo.startswith("## G1 oggi, moneta per moneta: paper e demo (sola lettura)")
    assert "equity del conto ridotto (1,000.00 USDT)" in testo
    righe = testo.splitlines()
    celle = righe[2][2:].split(" · ")
    # in ordine di peso più grande fra i due; la moneta che il demo non ha e quella solo sul demo ci sono
    assert celle == ["AAAUSDT +5.00/+4.80", "龙虾USDT -3.20/+0.00", "BBBUSDT -3.00/-3.10", "CCCUSDT +0.00/+0.60"]
    assert "ZEROUSDT" not in testo and "DDDUSDT" not in testo
    assert "- monete: paper 3, demo 3; esposizione lorda paper 11.2%, demo 8.5%; somma delle differenze 4.1% del conto" in testo
    assert c.chiamate == [("GET", "/fapi/v2/positionRisk", {}, True)]


def test_molte_monete_vanno_a_righe_di_sei():
    fb = _Fb({"/paper_g1/posizioni": {f"M{i:02d}USDT": 0.01 * (i + 1) for i in range(13)}, "/demo_binance/stato": {"equity": 1000}})
    righe = _testo(_Cliente(posizioni=[]), fb=fb).splitlines()
    assert [len(r[2:].split(" · ")) for r in righe if r.startswith("- M")] == [6, 6, 1]
    assert "- monete: paper 13, demo 0;" in "\n".join(righe)


def test_nella_finestra_del_ribilancio_non_chiede_niente():
    c = _Cliente()
    testo = _testo(c, now=calendar.timegm((2026, 11, 14, 0, 30, 0)))
    assert "non letto: finestra del ribilancio del demo" in testo and c.chiamate == []


def test_senza_equity_del_demo_scrive_solo_il_paper():
    c = _Cliente()
    testo = _testo(c, fb=_Fb({"/paper_g1/posizioni": {"AAAUSDT": 0.05}}))
    assert "- demo: non letto: manca l'equity del demo" in testo
    assert "AAAUSDT +5.00/—" in testo and c.chiamate == []


def test_un_errore_di_binance_o_di_firebase_non_ferma_lo_stato():
    testo = _testo(_Cliente(RuntimeError("GET /fapi/v2/positionRisk: 500 errore")))
    assert "- demo: non letto: RuntimeError: GET /fapi/v2/positionRisk: 500" in testo
    assert "AAAUSDT +5.00/—" in testo
    testo = _testo(_Cliente(), fb=_Fb(rompi=True))
    assert "- demo: non letto: manca l'equity del demo" in testo and "nessuna posizione" in testo


def test_la_sola_lettura_ammette_positionrisk_solo_in_get():
    chiamate = []

    class _Risposta:
        status_code, headers = 200, {"X-MBX-USED-WEIGHT-1M": "7"}

        def json(self):
            return []

        @property
        def text(self):
            return "[]"
    c = ClienteDemo("k", "s", http=ss.SoloLettura(lambda m, u, **k: chiamate.append((m, u)) or _Risposta()))
    for metodo, percorso in (("POST", "/fapi/v2/positionRisk"), ("GET", "/fapi/v2/account"), ("POST", "/fapi/v1/order")):
        with pytest.raises(ValueError, match="sola lettura"):
            c.chiedi(metodo, percorso, {}, firmata=True)
    assert chiamate == []
    c.chiedi("GET", "/fapi/v2/positionRisk", {}, firmata=True)
    assert chiamate[0][0] == "GET" and chiamate[0][1].startswith("https://demo-fapi.binance.com/fapi/v2/positionRisk?")


def test_la_sezione_e_in_fondo_allo_stato():
    import inspect
    sorgente = inspect.getsource(ss.build)
    assert sorgente.index("sezione_pesi_g1_oggi(fb, cliente=cliente_demo)") > sorgente.index("_calibration_section(fb)")


def test_il_segno_viene_dalla_quantita():
    # problema 86: se Binance desse il valore della posizione senza segno, la posizione corta resta corta
    c = _Cliente(posizioni=[{"symbol": "BBBUSDT", "positionAmt": "-3", "notional": "31.0"},
                            {"symbol": "AAAUSDT", "positionAmt": "10", "notional": "-48.0"}])
    testo = _testo(c)
    assert "BBBUSDT -3.00/-3.10" in testo and "AAAUSDT +5.00/+4.80" in testo


def test_equity_assurda_o_vecchia():
    # problema 85: un'equity non sensata non si usa; una vecchia si dice
    for e in (float("nan"), float("inf"), 1e15, -5, "abc"):
        c = _Cliente()
        testo = _testo(c, fb=_Fb({"/paper_g1/posizioni": {"AAAUSDT": 0.05}, "/demo_binance/stato": {"equity": e}}))
        assert "o non è un numero sensato" in testo and c.chiamate == [] and "+nan" not in testo and "inf" not in testo
    vecchia = {"/paper_g1/posizioni": {"AAAUSDT": 0.05}, "/demo_binance/stato": {"equity": 1000, "aggiornato": ORA - 3 * 3600}}
    assert "attenzione: l'equity del demo è di 3.0 ore fa" in _testo(_Cliente(), fb=_Fb(vecchia))
    fresca = {"/paper_g1/posizioni": {"AAAUSDT": 0.05}, "/demo_binance/stato": {"equity": 1000, "aggiornato": ORA - 600}}
    assert "attenzione" not in _testo(_Cliente(), fb=_Fb(fresca))


class _RispostaHttp:
    def __init__(self, stato=200, corpo=None):
        self.status_code, self.headers, self._corpo = stato, {"X-MBX-USED-WEIGHT-1M": "10"}, corpo if corpo is not None else []

    def json(self):
        return self._corpo

    @property
    def text(self):
        return str(self._corpo)


def test_dopo_un_429_nessuna_sezione_chiede_piu():
    # problema 84: le due sezioni dello stato usano lo stesso cliente; dopo il primo 429 non parte più nessuna richiesta
    chiamate = []

    def rete(metodo, url, **kw):
        chiamate.append(url)
        return _RispostaHttp(429)
    c = ClienteDemo("k", "s", http=ss.SoloLettura(rete))
    fb = _Fb()
    prima = "\n".join(ss.sezione_demo_esecuzioni(fb, cliente=c, now=ORA, dormi=lambda s: None))
    dopo = "\n".join(ss.sezione_pesi_g1_oggi(fb, cliente=c, now=ORA, dormi=lambda s: None))
    assert len(chiamate) == 1 and "429" in prima
    assert "- demo: non letto:" in dopo and "429" in dopo
    assert "AAAUSDT +5.00/—" in dopo


def test_il_peso_usato_dall_indirizzo_vale_anche_per_la_seconda_sezione():
    chiamate = []

    def rete(metodo, url, **kw):
        chiamate.append(url)
        r = _RispostaHttp(200, [])
        r.headers = {"X-MBX-USED-WEIGHT-1M": str(ss.PESO_USATO_MASSIMO + 1)}
        return r
    c = ClienteDemo("k", "s", http=ss.SoloLettura(rete))
    c.chiedi("GET", "/fapi/v1/income", {"incomeType": "FUNDING_FEE"}, firmata=True)
    n = len(chiamate)
    dopo = "\n".join(ss.sezione_pesi_g1_oggi(_Fb(), cliente=c, now=ORA, dormi=lambda s: None))
    assert len(chiamate) == n and "già usato" in dopo


def test_un_errore_imprevisto_non_ferma_lo_stato(monkeypatch):
    def rotta(*a, **k):
        raise KeyError("imprevisto")
    monkeypatch.setattr(ss, "_pesi_g1_oggi", rotta)
    righe = ss.sezione_pesi_g1_oggi(_Fb(), cliente=_Cliente(), now=ORA)
    assert righe[0].startswith("## G1 oggi") and righe[1].startswith("- non letto: KeyError")


def test_lo_stato_passa_lo_stesso_cliente_alle_due_sezioni():
    import inspect
    sorgente = inspect.getsource(ss.build)
    assert "sezione_demo_esecuzioni(fb, cliente=cliente_demo)" in sorgente
    assert "sezione_pesi_g1_oggi(fb, cliente=cliente_demo)" in sorgente
