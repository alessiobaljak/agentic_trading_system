"""Le parti nuove della prova 30: le settimane, la data prevista dall'anno prima, la scelta."""
from datetime import date, timedelta

from stock.prove import p030


def test_settimane_decisione_entrata_venerdi():
    # settimana con il lunedì festivo: si entra il martedì; il venerdì resta quello della settimana
    giorni = [date(2024, 1, 10), date(2024, 1, 12), date(2024, 1, 16), date(2024, 1, 19), date(2024, 1, 22)]
    s = p030.settimane(giorni)
    assert s[0] == (date(2024, 1, 12), date(2024, 1, 16), date(2024, 1, 19))
    assert s[1] == (date(2024, 1, 19), date(2024, 1, 22), date(2024, 1, 26))
    assert len(s) == 2


def test_previsti_dopo_l_entrata_e_fino_al_venerdi():
    entrata, venerdi = date(2024, 1, 22), date(2024, 1, 26)
    meno = lambda d: d - timedelta(days=364)  # noqa: E731
    date_c = {"LUN": [meno(entrata)], "MAR": [meno(date(2024, 1, 23))], "VEN": [meno(venerdi)],
              "DOPO": [meno(date(2024, 1, 29))], "PRIMA": [meno(date(2024, 1, 19))]}
    assert p030.previsti(date_c, entrata, venerdi) == {"MAR", "VEN"}   # il lunedì dell'entrata è escluso


def test_scegli_minimo_massimo_e_ordine_alfabetico():
    assert p030.scegli({f"S{i}" for i in range(9)}) == []
    tanti = {f"T{i:03d}" for i in range(80)}
    scelti = p030.scegli(tanti)
    assert len(scelti) == 50 and scelti == sorted(tanti)[:50]


def test_depositati_nella_settimana():
    date_c = {"A": [date(2024, 1, 24)], "B": [date(2024, 1, 29)]}
    assert p030.depositati(date_c, "A", date(2024, 1, 22), date(2024, 1, 26))
    assert not p030.depositati(date_c, "B", date(2024, 1, 22), date(2024, 1, 26))
