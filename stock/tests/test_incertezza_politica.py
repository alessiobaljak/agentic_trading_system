"""Le parti senza rete della prova 50: la lettura dell'indice e le decisioni mensili."""
from datetime import date, timedelta

import pandas as pd

from stock.prove import p050
from stock.prove.p049 import ALTA, BASSA


def _giorni(dal, al):
    out, d = [], dal
    while d <= al:
        out.append(d)
        d += timedelta(days=1)
    return out


def test_leggi_indice():
    s = p050.leggi_indice("day,month,year,daily_policy_index\n2,1,1985,120.5\n1,1,1985,100\n3,1,1985,\n")
    assert list(s.index) == [date(1985, 1, 1), date(1985, 1, 2)] and s.iloc[1] == 120.5


def test_decisione_del_mese_eseguita_il_primo_giorno_di_borsa_dopo():
    tutti = _giorni(date(2018, 12, 1), date(2020, 2, 29))
    indice = pd.Series(100.0, index=tutti)
    for d in tutti:
        if d.year == 2020 and d.month == 1:
            indice.loc[d] = 150.0                                    # gennaio 2020 sopra la media dei 12 mesi prima
    chiusi = {date(2020, 1, 1), date(2020, 2, 3)}                    # capodanno e un lunedì chiuso (finto)
    borsa = [d for d in tutti if d.weekday() < 5 and d not in chiusi]
    dec = p050.decisioni(indice, borsa)
    assert dec[date(2020, 2, 4)] == ALTA                             # primo giorno di borsa dopo il 31 gennaio
    assert dec[date(2020, 1, 2)] == BASSA                            # dicembre 2019 uguale alla media: bassa
    assert min(dec) == date(2020, 1, 2)                              # prima servono 12 mesi interi
