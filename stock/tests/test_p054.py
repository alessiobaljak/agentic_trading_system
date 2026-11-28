"""Le parti senza rete della prova 54: i giorni dal comunicato, le settimane pari, le quote, i contanti e il conto (date finte)."""
from datetime import date, timedelta

import pandas as pd
import pytest

from stock.prove import p054


def feriali(dal, n):
    d, out = dal, []
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


CAL = feriali(date(2020, 1, 1), 90)
K = 5                                    # il primo comunicato è il sesto giorno di borsa
C1, C2 = CAL[K], CAL[K + 35]             # il secondo dopo 35 giorni: il suo giorno −1 (d 34) si attacca alla settimana 6


def test_giorni_dal_comunicato():
    d = p054.giorni_dal_comunicato(CAL, [C1, C2])
    assert d[CAL[K - 1]] is None                                  # prima del primo comunicato: nessun ciclo
    assert d[C1] == 0 and d[CAL[K + 13]] == 13 and d[C2] == 0
    with pytest.raises(ValueError):
        p054.giorni_dal_comunicato(CAL, [date(2020, 1, 4)])         # un sabato: non è un giorno di borsa


def test_settimane_pari_e_dispari():
    pari = p054.settimane_pari(CAL, [C1, C2])
    dentro = {k - K for k in range(len(CAL)) if pari[CAL[k]]}
    attese = {-1, 0, 1, 2, 3, *range(9, 14), *range(19, 24), *range(29, 34), 34, 35, 36, 37, 38, *range(44, 49), *range(54, 59),
              *range(64, 69)}
    assert {x for x in dentro if x < 70} == attese
    assert not pari[CAL[K - 2]]                                    # due giorni prima del comunicato: fuori
    dispari = p054.settimane_dispari(CAL, [C1, C2])
    assert [k - K for k in range(K, K + 30) if dispari[CAL[k]]] == [*range(4, 9), *range(14, 19), *range(24, 29)]
    assert not (pari & dispari).any()


def test_quote_comprate_il_giorno_prima_e_finestre_attaccate():
    q = p054.quote(p054.settimane_pari(CAL, [C1, C2]))
    assert q[CAL[K - 3]] == 0.0 and q[CAL[K - 2]] == p054.QUOTA     # si compra alla chiusura prima del giorno −1
    assert q[CAL[K + 2]] == p054.QUOTA and q[CAL[K + 3]] == 0.0     # si vende alla chiusura del giorno 3
    assert q[CAL[K + 8]] == p054.QUOTA                               # rientro alla chiusura del giorno 8
    assert all(q[CAL[k]] == p054.QUOTA for k in range(K + 28, K + 38))   # settimana 6, giorno −1 e settimana 0 dopo: una finestra
    assert CAL[-1] not in q.index                                    # l'ultimo giorno non ha quota


def test_contanti_dal_tasso_del_giorno_prima():
    cal = [date(2020, 1, 3), date(2020, 1, 6), date(2020, 1, 7)]   # venerdì, lunedì, martedì
    tassi = pd.Series({date(2020, 1, 3): 3.6, date(2020, 1, 6): 7.2})
    c = p054.contanti(cal, tassi)
    assert c[date(2020, 1, 6)] == pytest.approx(0.036 / 360 * 3)    # il tasso del venerdì per tre giorni di calendario
    assert c[date(2020, 1, 7)] == pytest.approx(0.072 / 360)        # il tasso del lunedì per un giorno


def test_conto_spy_in_mercato_e_contanti_fuori():
    cal = [date(2020, 1, d) for d in (6, 7, 8, 9)]
    ch = pd.Series([10.0, 11.0, 12.0, 6.0], index=cal)
    q = pd.Series({cal[0]: 0.98, cal[1]: 0.98, cal[2]: 0.0})
    cassa = pd.Series(0.001, index=cal[1:])
    g = p054.conto(ch, q, cassa, costi=False)
    assert g[cal[1]] == pytest.approx(0.98 * 0.1 + 0.02 * 0.001)     # comprato alla chiusura del primo giorno
    assert g[cal[2]] == pytest.approx(0.98 * (12 / 11 - 1) + 0.02 * 0.001)
    assert g[cal[3]] == pytest.approx(0.001)                          # venduto alla chiusura del 8: il crollo del 9 non si prende
    con = p054.conto(ch, q, cassa)
    assert con[cal[1]] < g[cal[1]] and con[cal[2]] < g[cal[2]]       # l'ingresso (pagato il giorno dopo) e l'uscita pagano i costi
    assert con[cal[3]] == pytest.approx(g[cal[3]])
