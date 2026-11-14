"""Le parti nuove della prova 32: la data valida di FINRA, la scelta dal basso, il campionamento a blocchi."""
from datetime import date

import numpy as np
import pandas as pd

from stock.prove import p032


def test_data_valida_almeno_quattordici_giorni_prima():
    r = [date(2024, 1, 12), date(2024, 1, 31), date(2024, 2, 15), date(2024, 2, 29)]
    assert p032.data_valida(r, date(2024, 2, 29)) == date(2024, 2, 15)
    assert p032.data_valida(r, date(2024, 2, 28)) == date(2024, 1, 31)      # il 15 febbraio è a meno di 14 giorni
    assert p032.data_valida(r, date(2024, 1, 20)) is None


def test_scegli_il_venti_per_cento_con_meno_giorni():
    giorni = {f"S{i:03d}": float(i) for i in range(300)}
    assert p032.scegli(giorni, set(list(giorni)[:24])) == []
    s = p032.scegli(giorni, set(giorni))
    assert s == [f"S{i:03d}" for i in range(50)]
    s = p032.scegli(giorni, {f"S{i:03d}" for i in range(100)})
    assert s == [f"S{i:03d}" for i in range(20)]
    pari = {"B": 0.5, "A": 0.5, **{f"Z{i:02d}": 9.0 for i in range(28)}}          # 30 ammessi: se ne scelgono 6
    assert p032.scegli(pari, set(pari)) == ["A", "B", "Z00", "Z01", "Z02", "Z03"]


def test_simboli_delle_azioni_ordinarie():
    assert p032.ORDINARIE.fullmatch("AAPL") and p032.ORDINARIE.fullmatch("F") and p032.ORDINARIE.fullmatch("BRK.B")
    assert not p032.ORDINARIE.fullmatch("ABCDF") and not p032.ORDINARIE.fullmatch("ABC.W")


def test_campionamento_parte_buona_e_parte_cattiva():
    rng = np.random.default_rng(1)
    i = pd.RangeIndex(2000)
    m = pd.Series(rng.normal(0.0004, 0.01, 2000), index=i)
    buona = pd.Series(rng.normal(0.002, 0.005, 2000), index=i)       # guadagna molto e non si muove con la miscela
    cattiva = pd.Series(rng.normal(-0.002, 0.005, 2000), index=i)
    assert p032.campionamento(m, buona) > 0.95
    assert p032.campionamento(m, cattiva) < 0.05
