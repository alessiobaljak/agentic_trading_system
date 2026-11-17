"""La sezione di sola lettura dello stato con il funding di G1 regolamento per regolamento, demo contro paper
(scripts/state_snapshot.py, sezione_funding_demo_paper; MIGLIORARE_G1.md voce 3). Nessuna rete: cliente finto."""
import calendar

from bot.portafoglio.demo_binance import ClienteDemo
from scripts import state_snapshot as ss


def _ms(g, h, m=0):
    a, me, d = (int(x) for x in g.split("-"))
    return calendar.timegm((a, me, d, h, m, 0)) * 1000


ORA = _ms("2026-11-17", 4, 20) / 1000
INCASSI = [
    {"symbol": "AAAUSDT", "incomeType": "FUNDING_FEE", "income": "0.30", "asset": "USDT", "time": _ms("2026-11-16", 0), "tranId": 1},
    {"symbol": "BBBUSDT", "incomeType": "FUNDING_FEE", "income": "0.10", "asset": "USDT", "time": _ms("2026-11-16", 0), "tranId": 2},
    {"symbol": "AAAUSDT", "incomeType": "FUNDING_FEE", "income": "0.20", "asset": "USDT", "time": _ms("2026-11-16", 8), "tranId": 3},
    {"symbol": "CCCUSDT", "incomeType": "FUNDING_FEE", "income": "-0.05", "asset": "USDT", "time": _ms("2026-11-16", 4), "tranId": 4},
    {"symbol": "AAAUSDT", "incomeType": "FUNDING_FEE", "income": "0.40", "asset": "USDT", "time": _ms("2026-11-17", 0), "tranId": 5},
    {"symbol": "DDDUSDT", "incomeType": "FUNDING_FEE", "income": "0.25", "asset": "USDT", "time": _ms("2026-11-17", 0), "tranId": 6},
]
FIREBASE = {
    "/paper_g1/funding": {
        "2026-11-15": {"16:00": {"incassato": 99.0, "monete": 9}},          # fuori dai giorni letti? no: dentro i 3 giorni
        "2026-11-16": {"00:00": {"incassato": 5.0, "monete": 40, "maggiori": {"AAAUSDT": 3.0, "BBBUSDT": 1.0}},
                       "04:00": {"incassato": -0.5, "monete": 2},
                       "08:00": {"incassato": 2.0, "monete": 38, "maggiori": {"AAAUSDT": 2.0}}},
        "2026-11-17": {"00:00": {"incassato": 6.0, "monete": 41, "maggiori": {"AAAUSDT": 4.0, "EEEUSDT": 1.5}}},
        "2026-11-01": {"00:00": {"incassato": 1.0, "monete": 1}},           # troppo vecchio: non si mostra
    },
    "/demo_binance/stato": {"equity": 1000.0},
    "/paper_g1/stato": {"equity": 10000.0},
}


class _Fb:
    def __init__(self, dati=None):
        self.dati = FIREBASE if dati is None else dati

    def get_rtdb(self, ramo):
        return self.dati.get(ramo)


class _Cliente:
    def __init__(self, errore=None):
        self.chiamate, self.errore = [], errore

    def chiedi(self, metodo, percorso, parametri=None, firmata=False):
        p = dict(parametri or {})
        self.chiamate.append((metodo, percorso, p, firmata))
        if self.errore:
            raise self.errore
        return [r for r in INCASSI if p["startTime"] <= r["time"] <= p["endTime"]][: int(p.get("limit") or 500)]


def _testo(cliente, fb=None, now=ORA):
    return "\n".join(ss.sezione_funding_demo_paper(_Fb() if fb is None else fb, cliente=cliente, now=now, dormi=lambda s: None))


def test_la_sezione_confronta_i_regolamenti():
    c = _Cliente()
    testo = _testo(c)
    assert testo.startswith("## G1: il funding per regolamento, demo contro paper (sola lettura)")
    assert "Equity di oggi: demo 1,000.00 USDT, paper 10,000.00" in testo
    # demo 0,40/1000 = +0,0400%; paper 5/10000 = +0,0500%
    assert "| 2026-11-16 00 | +0.0400% | +0.0500% | -0.0100% | 2/40 |" in testo
    assert "| 2026-11-16 08 | +0.0200% | +0.0200% | +0.0000% | 1/38 |" in testo
    assert "| 2026-11-16 altre | -0.0050% | -0.0050% | +0.0000% | 1/2 |" in testo
    assert "| 2026-11-17 00 | +0.0650% | +0.0600% | +0.0050% | 2/41 |" in testo
    assert "| 2026-11-15 16 | +0.0000% | +0.9900% | -0.9900% | 0/9 |" in testo
    assert "2026-11-01" not in testo
    # l'ultimo regolamento: le monete più grandi, demo/paper; «—» se il paper non la mette fra le sue più grandi
    riga = next(r for r in testo.splitlines() if r.startswith("- regolamento 2026-11-17 00"))
    assert riga.endswith("AAAUSDT +0.0400/+0.0400 · DDDUSDT +0.0250/— · EEEUSDT +0.0000/+0.0150")
    assert "(— = non fra le 10 più grandi pubblicate dal paper)" in riga
    assert "| regolamento | demo | paper | demo meno paper | pagamenti demo/paper |" in testo
    assert [x[:2] for x in c.chiamate] == [("GET", "/fapi/v1/income")] and c.chiamate[0][3] is True
    assert c.chiamate[0][2]["incomeType"] == "FUNDING_FEE"


def test_nella_finestra_del_ribilancio_non_chiede_niente():
    c = _Cliente()
    assert "finestra del ribilancio" in _testo(c, now=_ms("2026-11-17", 0, 30) / 1000) and c.chiamate == []


def test_senza_funding_del_paper_o_senza_equity_non_chiede_niente():
    c = _Cliente()
    assert "non ancora" in _testo(c, fb=_Fb({"/demo_binance/stato": {"equity": 1000}, "/paper_g1/stato": {"equity": 10000}}))
    assert "manca l'equity" in _testo(c, fb=_Fb({**FIREBASE, "/paper_g1/stato": {"equity": float("nan")}}))
    assert c.chiamate == []


def test_un_errore_di_binance_non_ferma_lo_stato():
    testo = _testo(_Cliente(RuntimeError("GET /fapi/v1/income: 500 errore")))
    assert "- non letto: RuntimeError: GET /fapi/v1/income: 500" in testo


def test_dopo_un_429_non_parte_nessuna_richiesta():
    chiamate = []

    class _R:
        status_code, headers = 429, {}

        def json(self):
            return []
    c = ClienteDemo("k", "s", http=ss.SoloLettura(lambda m, u, **k: chiamate.append(u) or _R()))
    primo = _testo(c)
    secondo = _testo(c)
    assert len(chiamate) == 1 and "429" in primo and "429" in secondo


def test_la_sezione_e_in_fondo_allo_stato_con_lo_stesso_cliente():
    import inspect
    sorgente = inspect.getsource(ss.build)
    assert "sezione_funding_demo_paper(fb, cliente=cliente_demo)" in sorgente
    assert sorgente.index("sezione_funding_demo_paper(fb") > sorgente.index("sezione_pesi_g1_oggi(fb")


def test_firebase_che_non_risponde_e_non_letto():
    class _FbRotto:
        def get_rtdb(self, ramo):
            raise RuntimeError("firebase giù")
    c = _Cliente()
    testo = _testo(c, fb=_FbRotto())
    assert "- non letto: Firebase non risponde" in testo and "non ancora" not in testo and c.chiamate == []


def test_nella_riga_altre_si_contano_i_pagamenti():
    incassi = [{"symbol": "CCCUSDT", "income": "-0.01", "asset": "USDT", "time": _ms("2026-11-16", h), "tranId": h} for h in (4, 12, 20)]
    righe = ss.confronto_funding_regolamenti(incassi, {"2026-11-16": {"04:00": {"incassato": -0.1, "monete": 1},
                                                                      "12:00": {"incassato": -0.1, "monete": 1},
                                                                      "20:00": {"incassato": -0.1, "monete": 1}}},
                                             1000.0, 10000.0, ["2026-11-16"])
    assert any(r.startswith("| 2026-11-16 altre |") and r.endswith("| 3/3 |") for r in righe)
