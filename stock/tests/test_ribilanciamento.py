"""Le parti nuove della prova 37: il peso alla deriva, i segnali a fascia e di calendario, le posizioni, il conto."""
from datetime import date, timedelta

import numpy as np
import pandas as pd

from stock.prove import p037


def giorni_di_borsa(dal: date, n: int) -> list[date]:
    out, g = [], dal
    while len(out) < n:
        if g.weekday() < 5:
            out.append(g)
        g += timedelta(days=1)
    return out


def test_alla_deriva():
    assert abs(p037.alla_deriva(0.6, 0.0, 0.0) - 0.6) < 1e-12
    assert abs(p037.alla_deriva(0.6, 0.10, 0.0) - 0.66 / 1.06) < 1e-12


def test_segnale_fascia_zero_e_una_fascia():
    i = giorni_di_borsa(date(2024, 1, 1), 3)
    rs, rb = pd.Series([0.01, 0.01, 0.01], index=i), pd.Series([0.0, 0.0, 0.0], index=i)
    # fascia 0: torna al 60% ogni giorno, il segnale è la deriva di un giorno
    s0 = p037.segnale_fascia(rs, rb, [0.0])
    un_giorno = 0.606 / 1.006 - 0.6
    assert np.allclose(s0.to_numpy(), un_giorno)
    # fascia larga (10%): non torna mai, la deriva si accumula
    s1 = p037.segnale_fascia(rs, rb, [0.10])
    assert s1.iloc[2] > s1.iloc[1] > s1.iloc[0] > 0
    s2 = p037.segnale_fascia(rs, rb, [0.0, 0.10])
    assert np.allclose(s2.to_numpy(), (s0 + s1).to_numpy() / 2)


def test_segnale_calendario_riparte_dopo_la_fine_del_mese():
    i = [date(2024, 1, 30), date(2024, 1, 31), date(2024, 2, 1)]
    rs, rb = pd.Series([0.01, 0.01, 0.01], index=i), pd.Series(0.0, index=i)
    c = p037.segnale_calendario(rs, rb)
    assert c.iloc[1] > c.iloc[0]                                   # la deriva cresce nel mese
    assert abs(c.iloc[2] - c.iloc[0]) < 1e-12                      # il 31 gennaio torna al 60%: il 1° febbraio riparte


def test_posizioni_ultimi_cinque_giorni_e_primo_del_mese():
    i = giorni_di_borsa(date(2024, 1, 1), 30)                        # gennaio 2024 ha 23 giorni feriali, poi febbraio
    cal = pd.Series(np.linspace(0.001, 0.03, 30), index=i)          # sempre positivo: azioni sovrappesate
    fa = pd.Series(0.003, index=i)
    pf, pc = p037.posizioni(fa, cal)
    assert np.allclose(pf.to_numpy(), -0.2)
    gennaio = [k for k, g in enumerate(i) if g.month == 1]
    ultimi = gennaio[-5:]
    assert all(pc.iloc[k] == -1.0 for k in ultimi)                 # sovrappesate: corti sulle azioni a fine mese
    assert all(pc.iloc[k] == 0.0 for k in gennaio[:-5])
    primo = gennaio[-1] + 1
    assert pc.iloc[primo] == 1.0                                   # il rimbalzo: il segno del calendario di 4 giorni prima
    assert all(pc.iloc[k] == 0.0 for k in range(primo + 1, 30))


def test_conto_peso_del_giorno_prima_e_costi():
    i = giorni_di_borsa(date(2024, 1, 1), 3)
    w = pd.Series([0.5, 0.5, -2.0], index=i)
    rs, rb = pd.Series([0.0, 0.02, 0.01], index=i), pd.Series([0.0, 0.0, 0.03], index=i)
    p = pd.Series(100.0, index=i)
    r = p037.conto(w, rs, rb, p, p, costi=False)
    assert r.iloc[0] == 0.0 and abs(r.iloc[1] - 0.5 * 0.02) < 1e-12 and abs(r.iloc[2] - 0.5 * (0.01 - 0.03)) < 1e-12
    r2 = p037.conto(w, rs, rb, p, p)
    assert (r2 <= r + 1e-15).all() and r2.iloc[1] < r.iloc[1]     # il primo scambio (da 0 a 0,5) costa
    # il limite: il peso −2 diventa −1 il giorno dopo
    w2 = pd.Series([-2.0, 0.0, 0.0], index=i)
    r3 = p037.conto(w2, rs, rb, p, p, costi=False)
    assert abs(r3.iloc[1] - (-1.0) * 0.02) < 1e-12
    r4 = p037.conto(w2, rs, rb, p, p, costi=False, limite=None)
    assert abs(r4.iloc[1] - (-2.0) * 0.02) < 1e-12


def test_posizioni_dati_che_finiscono_a_fine_mese():
    i = giorni_di_borsa(date(2024, 1, 1), 23)                        # solo gennaio
    cal = pd.Series(0.01, index=i)
    _, senza = p037.posizioni(pd.Series(0.0, index=i), cal)
    _, con = p037.posizioni(pd.Series(0.0, index=i), cal, finisce_a_fine_mese=True)
    assert (senza == 0).all() and (con.iloc[-5:] == -1.0).all() and (con.iloc[:-5] == 0).all()
