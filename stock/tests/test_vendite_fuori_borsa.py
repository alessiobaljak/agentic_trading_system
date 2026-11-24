"""Le parti senza rete della prova 49: le decisioni settimanali sul DIX e il conto."""
from datetime import date, timedelta

import pandas as pd
import pytest

from stock.prove import p049


def feriali(dal, al, chiusi=()):
    d, out = dal, []
    while d <= al:
        if d.weekday() < 5 and d not in chiusi:
            out.append(d)
        d += timedelta(days=1)
    return out


def test_leggi_dix():
    s = p049.leggi_dix("date,price,dix,gex\n2016-01-05,2000,0.41,1\n2016-01-04,1990,0.40,-1\n2016-01-06,2001,,3\n")
    assert list(s.index) == [date(2016, 1, 4), date(2016, 1, 5)] and s.iloc[1] == pytest.approx(0.41)


def test_decisione_alta_eseguita_il_primo_giorno_della_settimana_dopo():
    giorni = feriali(date(2018, 12, 31), date(2020, 1, 17), chiusi={date(2020, 1, 6)})       # lunedì 6 gennaio chiuso (finto)
    valori = [0.40] * len(giorni)
    dix = pd.Series(valori, index=giorni)
    # la settimana del 30 dicembre 2019 - 3 gennaio 2020 sopra la media: si esegue martedì 7 (lunedì 6 chiuso)
    for g in giorni:
        if date(2019, 12, 30) <= g <= date(2020, 1, 3):
            dix.loc[g] = 0.45
    dec = p049.decisioni(dix, giorni)
    assert dec[date(2020, 1, 7)] == p049.ALTA
    assert dec[date(2020, 1, 13)] == p049.BASSA                                            # la settimana dopo torna uguale
    assert min(dec) == date(2020, 1, 7)                                                     # prima servono 52 settimane intere


def test_uguale_alla_media_vuol_dire_bassa():
    giorni = feriali(date(2019, 1, 7), date(2020, 1, 31))
    dec = p049.decisioni(pd.Series(0.4, index=giorni), giorni)
    assert dec and set(dec.values()) == {p049.BASSA}


def test_conto_quota_dalla_chiusura_dell_esecuzione_e_costi_sul_cambio():
    giorni = feriali(date(2020, 1, 6), date(2020, 1, 10))
    ch = pd.Series([100.0, 101.0, 102.0, 101.0, 103.0], index=giorni)
    es = {date(2020, 1, 7): p049.ALTA, date(2020, 1, 9): p049.BASSA}
    g = p049.conto(ch, es, costi=False)
    assert g.loc[date(2020, 1, 7)] == 0.0                                                   # fuori fino alla chiusura del 7
    assert g.loc[date(2020, 1, 8)] == pytest.approx(0.98 * (102 / 101 - 1))
    assert g.loc[date(2020, 1, 9)] == pytest.approx(0.98 * (101 / 102 - 1))                 # la quota nuova vale dal 9 sera
    assert g.loc[date(2020, 1, 10)] == pytest.approx(0.49 * (103 / 101 - 1))
    con = p049.conto(ch, es)
    assert con.loc[date(2020, 1, 9)] < g.loc[date(2020, 1, 9)]                              # il cambio paga i costi
