"""Le parti senza rete del calcolo della prova 42: da dove si entra, i filtri, i posti, il conto."""
from datetime import date

import pandas as pd
import pytest

from stock.prove import p042

CAL = [date(2019, 1, 14), date(2019, 1, 15), date(2019, 1, 16), date(2019, 1, 18)]


def ny(s):
    return pd.Timestamp(s, tz="America/New_York").tz_convert("UTC")


def test_ora_della_sec_in_utc():
    assert p042.accettato("20190115163012") == ny("2019-01-15 16:30:12")


def test_da_dove_si_entra():
    assert p042.piano(ny("2019-01-15 10:00:30"), CAL) == (date(2019, 1, 15), "seduta", ny("2019-01-15 10:03"))
    assert p042.piano(ny("2019-01-15 15:55:00"), CAL) == (date(2019, 1, 15), "seduta", ny("2019-01-15 15:57"))
    assert p042.piano(ny("2019-01-15 15:55:01"), CAL) == (date(2019, 1, 16), "asta", None)     # 15:58: troppo tardi
    assert p042.piano(ny("2019-01-15 07:00:00"), CAL) == (date(2019, 1, 15), "asta", None)     # prima dell'apertura: l'asta del giorno
    assert p042.piano(ny("2019-01-16 18:00:00"), CAL) == (date(2019, 1, 18), "asta", None)     # il 17 non è di borsa
    assert p042.piano(ny("2019-01-18 17:00:00"), CAL) is None


def test_prima_barra_in_seduta_fino_alle_15_59():
    idx = pd.DatetimeIndex([ny("2019-01-15 10:02"), ny("2019-01-15 10:05"), ny("2019-01-15 16:00")])
    b = pd.DataFrame({"open": [10.0, 10.5, 11.0]}, index=idx)
    assert p042.cerca_in_seduta(b, ny("2019-01-15 10:03")) == (ny("2019-01-15 10:05"), 10.5)
    assert p042.cerca_in_seduta(b, ny("2019-01-15 15:58")) is None                             # la barra delle 16:00 non vale
    assert p042.cerca_in_seduta(None, ny("2019-01-15 10:03")) is None


def test_filtri_cinque_dollari_e_due_milioni():
    giorni = pd.Index([date(2019, 1, 1 + i) for i in range(25)])
    c = pd.Series(10.0, index=giorni)
    v = pd.Series(3e6, index=giorni)
    assert p042.passa_i_filtri(c, v, date(2019, 1, 25))
    assert not p042.passa_i_filtri(c.where(c.index != date(2019, 1, 24), 4.9), v, date(2019, 1, 25))   # chiusura del giorno prima
    assert not p042.passa_i_filtri(c, v.iloc[:10], date(2019, 1, 25))                                   # meno di 20 sedute
    assert not p042.passa_i_filtri(c, v * 0.5, date(2019, 1, 25))


def op(s, ora, gin, gout, pin=100.0, pout=110.0, iin=200.0, iout=202.0, tipo="asta"):
    return p042.Operazione(s, ora, tipo, ora, gin, pin, 1.0, gout, pout, 1.0, iin, 1.0, iout, 1.0)


def test_posti_e_stesso_titolo():
    a = op("AAA", ny("2019-01-14 09:30"), date(2019, 1, 14), date(2019, 1, 16))
    b = op("AAA", ny("2019-01-15 09:30"), date(2019, 1, 15), date(2019, 1, 18))          # stesso titolo, posizione aperta: salta
    c = op("BBB", ny("2019-01-16 16:00"), date(2019, 1, 16), date(2019, 1, 18))          # A chiude alle 16:00 del 16: c'è posto
    assert p042.scegli_ingressi([b, a, c], massimo=1) == [a, c]


def test_conto_senza_costi_titolo_meno_iwm():
    o = op("AAA", ny("2019-01-14 09:30"), date(2019, 1, 14), date(2019, 1, 16))
    r = p042.conto([o], CAL, 0.001, 0.0001, costi=False)
    # 25 azioni da 100 (2'500 dollari, il 2,5% di 100'000), 12 di IWM da 200 (2'400): +250 − 24 = +226 il giorno dell'uscita
    assert r[date(2019, 1, 16)] == pytest.approx(226 / 100_000) and r[date(2019, 1, 14)] == 0.0
    con = p042.conto([o], CAL, 0.001, 0.0001)
    assert con[date(2019, 1, 16)] < r[date(2019, 1, 16)]                                 # all'asta niente scarto, ma il resto sì
