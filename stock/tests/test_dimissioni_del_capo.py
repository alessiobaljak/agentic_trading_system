"""Le parti senza rete della prova 46: la scelta delle notizie con le parole, il giorno dell'annuncio, i posti, il conto."""
from datetime import date

import pandas as pd
import pytest

from stock.prove import p046

CAL = [date(2019, 3, d) for d in (4, 5, 6, 7, 8, 11)]


def ny(s):
    return pd.Timestamp(s, tz="America/New_York").tz_convert("UTC")


def test_parole_uscita_del_capo_non_pensionamenti_ne_ex():
    assert p046.parola("Acme CEO John Smith Resigns Effective Immediately") == "resigns"
    assert p046.parola("Acme says chief executive to step down after probe") == "step down"
    assert p046.parola("Acme CEO to retire at year end; successor named, steps down in June") is None     # pensionamento
    assert p046.parola("Former CEO of Acme resigns from board of Beta") is None                          # un ex capo
    assert p046.parola("Acme CEO says demand is strong") is None                                         # nessuna uscita
    assert p046.parola("Acme CFO resigns") is None                                                        # non è il capo


def test_giorno_dell_annuncio():
    assert p046.giorno_annuncio(ny("2019-03-05 08:00"), CAL) == date(2019, 3, 5)         # prima dell'apertura: lo stesso giorno
    assert p046.giorno_annuncio(ny("2019-03-05 15:59"), CAL) == date(2019, 3, 5)
    assert p046.giorno_annuncio(ny("2019-03-05 16:30"), CAL) == date(2019, 3, 6)         # dopo la chiusura: il giorno dopo
    assert p046.giorno_annuncio(ny("2019-03-09 10:00"), CAL) == date(2019, 3, 11)        # sabato: il lunedì


def test_scelta_un_solo_membro_e_niente_doppioni():
    n = pd.DataFrame({"creata": [ny("2019-03-05 08:00"), ny("2019-03-06 08:00"), ny("2019-03-07 08:00"), ny("2019-03-07 09:00")],
                      "simboli": [["AAA"], ["AAA"], ["AAA", "BBB"], ["CCC", "X", "Y", "Z"]],
                      "testo": ["AAA CEO resigns", "AAA CEO resignation: more details", "AAA and BBB: CEO leaves AAA for BBB",
                                "CEO departs CCC"]})
    ann, conta = p046.scegli_notizie(n, lambda g: {"AAA", "BBB", "CCC"}, CAL)
    assert list(ann["simbolo"]) == ["AAA"] and conta["doppioni (60 giorni)"] == 1
    assert conta["due o più membri"] == 1 and conta["più di 3 simboli"] == 1


def op(s, gi, gu, p_in=100.0, p_out=90.0, s_in=200.0, s_out=200.0):
    return p046.Operazione(s, gi, gi, p_in, 1.0, gu, p_out, 1.0, s_in, 1.0, s_out, 1.0)


def test_conto_vendita_coperta_senza_costi():
    o = op("AAA", CAL[1], CAL[4])
    r = p046.conto([o], CAL, costi=False)
    # 100 azioni vendute a 100 (10'000, il 10% di 100'000) che scendono del 10%: +1'000; 50 SPY fermi: 0
    assert r[CAL[4]] == pytest.approx(1_000 / 100_000) and r[CAL[1]] == 0.0
    assert p046.conto([o], CAL)[CAL[4]] < r[CAL[4]]


def test_posti_liberi_il_giorno_dopo_l_uscita():
    a, b, c = op("AAA", CAL[0], CAL[2]), op("BBB", CAL[2], CAL[4]), op("CCC", CAL[3], CAL[5])
    assert p046.scegli_ingressi([a, b, c], massimo=1) == [a, c]                          # b entra il giorno in cui a esce: niente posto
