"""Le parti nuove della prova 34: i giorni intorno al comunicato, i comunicati del mese, la scelta, il simbolo di allora."""
from datetime import date

from stock.dati import comunicati_piccole
from stock.prove import p034


def test_intorno_al_comunicato():
    cal = [date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 5), date(2024, 1, 8)]
    assert p034.intorno(cal, date(2024, 1, 3)) == (date(2024, 1, 2), date(2024, 1, 5))
    assert p034.intorno(cal, date(2024, 1, 6)) == (date(2024, 1, 5), date(2024, 1, 8))      # depositato di sabato
    assert p034.intorno(cal, date(2024, 1, 2)) is None
    assert p034.intorno(cal, date(2024, 1, 8)) is None


def test_del_mese_conta_l_ultimo_comunicato():
    ev = [("A", date(2024, 1, 10), 0.1), ("A", date(2024, 1, 25), -0.2), ("B", date(2024, 2, 1), 0.3), ("C", date(2023, 12, 29), 0.5)]
    assert p034.del_mese(ev, date(2023, 12, 29), date(2024, 1, 31)) == {"A": -0.2}


def test_scegli_il_venti_per_cento_piu_alto():
    r = {f"S{i:03d}": i / 100 for i in range(300)}
    assert p034.scegli(dict(list(r.items())[:24])) == []
    assert p034.scegli(r) == [f"S{i:03d}" for i in range(250, 300)]
    assert p034.scegli({f"S{i:03d}": i / 100 for i in range(100)}) == [f"S{i:03d}" for i in range(80, 100)]


def test_simbolo_di_allora_solo_moduli_prima():
    dm = [date(2019, 1, 1), date(2019, 6, 1), date(2019, 7, 1), date(2020, 3, 1)]
    sm = ["VECC", "NUOV", "NUOV", "DOPO"]
    assert comunicati_piccole.simbolo_di_allora(dm, sm, date(2020, 2, 1)) == "NUOV"
    assert comunicati_piccole.simbolo_di_allora(dm, sm, date(2019, 1, 1)) is None
    assert comunicati_piccole.simbolo_di_allora(dm, sm, date(2021, 6, 1)) is None              # più di 365 giorni prima
