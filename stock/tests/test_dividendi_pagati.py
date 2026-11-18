"""Le parti nuove della prova 40: il giorno di pagamento, le azioni allo stacco, la misura, la soglia dell'anno prima, il conto."""
from datetime import date, timedelta

import numpy as np
import pandas as pd

from stock.prove import p040

CAL = [date(2024, 3, 1), date(2024, 3, 4), date(2024, 3, 5), date(2024, 3, 6)]


def test_giorno_di_borsa_e_pagamenti():
    assert p040.giorno_di_borsa(date(2024, 3, 2), CAL) == date(2024, 3, 4)        # sabato → lunedì
    assert p040.giorno_di_borsa(date(2024, 3, 7), CAL) is None
    div = pd.DataFrame({"pagamento": [date(2024, 2, 20), date(2024, 3, 2), date(2024, 3, 4), date(2024, 3, 6)],
                        "dollari": [999.0, 10.0, 5.0, 7.0]})
    p = p040.pagamenti(div, CAL)
    assert list(p.to_numpy()) == [0.0, 15.0, 0.0, 7.0]                               # febbraio, prima del calendario: fuori
    assert list(p040.misura(p).to_numpy()) == [0.0, 15.0, 15.0, 7.0]


def test_azioni_allo_stacco_con_deposito_prima_e_frazionamento():
    d = [(date(2024, 1, 20), date(2024, 1, 10), 100.0), (date(2024, 4, 20), date(2024, 4, 10), 120.0)]
    assert p040.azioni_allo_stacco(d, date(2024, 3, 1), {date(2024, 2, 1): 2.0}) == 200.0
    assert p040.azioni_allo_stacco(d, date(2024, 1, 20), {}) is None                 # il deposito dello stesso giorno non conta
    assert p040.azioni_allo_stacco(d, date(2024, 5, 1), {date(2024, 2, 1): 2.0}) == 120.0


def test_soglia_solo_dai_giorni_prima():
    giorni = [date(2020, 1, 1) + timedelta(days=k) for k in range(300)]
    d = pd.Series(np.arange(300, dtype=float), index=giorni)
    s = p040.soglie(d, 0.5, finestra=252)
    assert s.iloc[:252].isna().all() and abs(s.iloc[252] - np.median(np.arange(252))) < 1e-9
    w = p040.dentro(d, 0.5)
    assert w.iloc[:252].sum() == 0 and w.iloc[252:].all()                              # crescente: sempre sopra la mediana di prima


def test_conto_costi_solo_ai_cambi():
    i = CAL
    w = pd.Series([0.0, 1.0, 1.0, 0.0], index=i)
    r = pd.Series([0.01, 0.02, -0.01, 0.03], index=i)
    prezzo = pd.Series(400.0, index=i)
    senza = p040.conto(w, r, prezzo, costi=False)
    assert list(senza.to_numpy()) == [0.0, 0.02, -0.01, 0.0]
    con = p040.conto(w, r, prezzo)
    assert con.iloc[1] < 0.02 and con.iloc[2] == -0.01 and con.iloc[3] < 0              # costi all'entrata e all'uscita


def test_cambio_del_mese():
    cal = [date(2024, 1, 29), date(2024, 1, 30), date(2024, 1, 31), date(2024, 2, 1), date(2024, 2, 2), date(2024, 2, 5),
           date(2024, 2, 6)]
    assert p040.cambio_del_mese(cal) == {date(2024, 1, 31), date(2024, 2, 1), date(2024, 2, 2), date(2024, 2, 5)}
