"""Le parti senza rete della prova 51: la lettura dei titoli, l'azienda comprata, l'uscita e il conto."""
from datetime import date, timedelta

import pytest

from stock.prove import p051


def test_leggi_solo_accordi_in_contanti():
    assert p051.leggi("Acme To Acquire Widget For $25.50 Per Share In Cash") == 25.5
    assert p051.leggi("Widget Enters Definitive Agreement To Be Acquired By Acme For $1,025/Share In Cash") == 1025.0
    assert p051.leggi("Acme To Acquire Widget For $25 Per Share In Cash And Stock") is None          # misto
    assert p051.leggi("Acme Proposes To Acquire Widget For $25 Per Share In Cash") is None           # proposta
    assert p051.leggi("Acme Reportedly In Talks To Acquire Widget For $25/Share In Cash") is None    # voce
    assert p051.leggi("Acme To Acquire Widget For $25 Per Share") is None                            # senza «cash»


def test_bersaglio_unico():
    assert p051.bersaglio(["ACME", "WID"], 25.0, {"ACME": 80.0, "WID": 19.0}) == "WID"
    assert p051.bersaglio(["A", "B"], 25.0, {"A": 20.0, "B": 21.0}) is None                          # due possibili
    assert p051.bersaglio(["A"], 25.0, {"A": 10.0}) is None                                          # più del doppio
    assert p051.bersaglio(["A"], 25.0, {"A": None}) is None


def _feriali(dal, al):
    out, d = [], dal
    while d <= al:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def test_uscita():
    cal = _feriali(date(2023, 1, 2), date(2024, 12, 31))
    gi = date(2023, 3, 1)
    sparito = [g for g in cal if gi <= g <= date(2023, 7, 14)]
    assert p051.uscita(gi, sparito, cal) == (date(2023, 7, 14), "sparito")
    resta = [g for g in cal if g >= gi]
    assert p051.uscita(gi, resta, cal) == (date(2024, 2, 29), "365 giorni")          # 2024 bisestile
    tardi = date(2024, 6, 3)
    assert p051.uscita(tardi, [g for g in cal if g >= tardi], cal) == (date(2024, 12, 31), "fine del periodo")


def test_scegli_e_conto():
    g = _feriali(date(2023, 1, 2), date(2023, 1, 13))
    a = p051.Affare("WID", g[0], g[1], g[4], "sparito", 0.05)
    prezzi = {"WID": {d: (0.0, 20.0 + (1.0 if d >= g[4] else 0.0), 1.0) for d in g}}
    s = p051.conto([a], prezzi, g, costi=False)
    assert s.loc[g[1]] == pytest.approx(0.0)
    n = int(0.05 * 100_000 / 20.0)
    assert s.loc[g[4]] == pytest.approx(n * 1.0 / 100_000)                                           # il salto all'uscita
    assert (1 + s).prod() - 1 == pytest.approx(n * 1.0 / 100_000)
    molti = [p051.Affare(f"S{i:02d}", g[0], g[1], g[5], "sparito", 0.05) for i in range(25)]
    assert len(p051.scegli(molti)) == 20
