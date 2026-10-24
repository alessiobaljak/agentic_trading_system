"""L'universo «di allora» su un caso costruito a mano."""
from datetime import date

import pandas as pd

from stock.universo import costruisci as u


def test_dieci_di_allora_rispetta_indice_classi_e_storia(monkeypatch):
    monkeypatch.setattr(u, "GIORNI", 3)
    monkeypatch.setattr(u, "QUANTI", 2)
    giorni = [date(2020, 1, 29), date(2020, 1, 30), date(2020, 1, 31), date(2020, 2, 3), date(2020, 2, 28),
              date(2020, 3, 2)]
    comp = [(date(2019, 1, 1), frozenset({"AAA", "BBB", "GOOG", "GOOGL", "NUOVO"})),
            (date(2020, 2, 10), frozenset({"AAA", "BBB", "CCC"}))]
    s = lambda vals, gg=giorni: pd.Series(vals, index=gg)  # noqa: E731
    dollari = {
        "AAA": s([10, 10, 10, 10, 10, 10]),
        "BBB": s([5, 5, 5, 50, 50, 50]),
        "GOOG": s([30, 30, 30, 1, 1, 1]),
        "GOOGL": s([20, 20, 20, 1, 1, 1]),
        "NUOVO": pd.Series([99, 99], index=giorni[1:3]),   # storia incompleta: non entra
        "CCC": s([1, 1, 1, 100, 100, 100]),
        "FUORI": s([1000] * 6),                             # mai nell'indice
    }
    r = u.dieci_di_allora(dollari, comp, giorni, [pd.Period("2020-02", "M"), pd.Period("2020-03", "M")])
    feb = list(r[r.mese == "2020-02"].simbolo)
    mar = list(r[r.mese == "2020-03"].simbolo)
    # febbraio: finestra 29-31 gennaio, indice del 31 gennaio; GOOG batte GOOGL (stessa azienda), poi AAA
    assert feb == ["GOOG", "AAA"]
    # marzo: finestra 31 gen, 3 feb, 28 feb; indice del 28 feb (CCC dentro, GOOG fuori); CCC media 67, BBB 35
    assert mar == ["CCC", "BBB"]


def test_membri_al():
    comp = [(date(2020, 1, 1), frozenset({"A"})), (date(2020, 6, 1), frozenset({"B"}))]
    assert u.membri_al(comp, date(2020, 5, 31)) == {"A"}
    assert u.membri_al(comp, date(2020, 6, 1)) == {"B"}
