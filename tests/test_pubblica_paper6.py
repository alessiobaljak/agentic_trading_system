"""Il documento del paper del programma 6 per la dashboard (scripts/pubblica_paper6.py)."""
from scripts.pubblica_paper6 import documento


def test_documento_riduce_paper_json():
    paper = {
        "dati_fino_al": "2026-11-02", "funding_stimato_dal": "2026-11-01",
        "candidate": {
            "F3": {"settimane": {"2026-10-26": 0.012}, "periodi": 1, "totale": 0.012},
            "A1": {"giorni": {"2026-10-20": 0.001, "2026-10-21": -0.002}, "periodi": 2, "totale": -0.001, "sharpe": -1.0},
        },
        "adesso": {"F3": {"lunedi": "2026-11-02", "long": {"TRXUSDT": 0.3, "ATOMUSDT": 0.05},
                          "short": {"BNBUSDT": -0.14, "AEROUSDT": -0.04}}},
        "nuove_nell_universo": ["ARUSDT"],
    }
    d = documento(paper, adesso=123.0)
    assert d["meta"]["generato_at"] == 123.0
    f3 = next(c for c in d["candidate"] if c["nome"] == "F3")
    assert f3["unita"] == "settimane" and f3["ultimo"] == {"data": "2026-10-26", "netto": 0.012} and f3["sharpe"] is None
    a1 = next(c for c in d["candidate"] if c["nome"] == "A1")
    assert a1["unita"] == "giorni" and a1["ultimo"]["data"] == "2026-10-21"
    assert [x["moneta"] for x in d["posizioni"]["F3"]["long"]] == ["TRXUSDT", "ATOMUSDT"]
    assert [x["moneta"] for x in d["posizioni"]["F3"]["short"]] == ["BNBUSDT", "AEROUSDT"]
    assert d["posizioni"]["K1"]["long"] == [] and d["nuove_nell_universo"] == ["ARUSDT"]


def test_documento_vuoto():
    d = documento({}, adesso=1.0)
    assert d["candidate"] == [] and d["posizioni"]["F3"]["long"] == []


def test_documento_strategie_ed_eventi():
    paper = {"adesso": {"F5": {"lunedi": "2026-10-19", "long": {"ATOMUSDT": 0.04}, "short": {"BNBUSDT": -0.1}}},
             "eventi_N3": [{"mercato": "Binance", "simbolo": "XYZUSDT", "ingresso": "2026-10-28", "stato": "in corso"}],
             "eventi_E4": [{"simbolo": "ABCUSDT", "data": "2026-10-22", "r7": 0.05, "annuncio": 1}]}
    d = documento(paper, adesso=1.0)
    assert d["posizioni"]["F5"]["long"] == [{"moneta": "ATOMUSDT", "peso": 0.04}]
    assert d["eventi_n3"][0]["simbolo"] == "XYZUSDT" and d["eventi_n3"][0]["r"] is None
    assert d["eventi_e4"] == [{"simbolo": "ABCUSDT", "data": "2026-10-22", "r7": 0.05}]
    assert len(d["strategie"]) == 3 and "N3" in d["strategie"][0]["nome"]
