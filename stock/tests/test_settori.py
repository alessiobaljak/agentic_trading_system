"""Le parti nuove della prova 33: il segnale 12 mesi meno l'ultimo, la scelta dei 3 più alti e dei 3 più bassi, la fine dei mesi."""
from datetime import date, timedelta

import pandas as pd

from stock.prove import p033


def test_segnale_dodici_mesi_meno_l_ultimo():
    giorni = [date(2020, 1, 1) + timedelta(days=i) for i in range(300)]
    r = pd.Series([100.0 + i for i in range(300)], index=pd.Index(giorni))
    g = giorni[260]
    assert abs(p033.segnale(r, g) - ((100 + 260 - 21) / (100 + 260 - 252) - 1)) < 1e-12
    assert p033.segnale(r, giorni[251]) is None            # meno di 252 sedute prima
    assert p033.segnale(r, date(2030, 1, 1)) is None


def test_scegli_tre_alti_e_tre_bassi():
    seg = {"A": 0.5, "B": 0.4, "C": 0.3, "D": 0.2, "E": 0.1, "F": 0.0, "G": -0.1}
    assert p033.scegli(seg) == (["A", "B", "C"], ["E", "F", "G"])
    assert p033.scegli({"A": 1.0, "B": 0.0, "C": 0.5, "D": 0.2, "E": 0.1}) == ([], [])


def test_fine_dei_mesi():
    cal = [date(2024, 1, 30), date(2024, 1, 31), date(2024, 2, 1), date(2024, 2, 29), date(2024, 3, 1)]
    assert p033.fine_dei_mesi(cal) == [date(2024, 1, 31), date(2024, 2, 29), date(2024, 3, 1)]
