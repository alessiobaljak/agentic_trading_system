from datetime import UTC, datetime

from stock.dati import notizie


def test_non_si_scarica_nei_minuti_degli_ordini():
    # giovedì 12 novembre 2026: New York è a UTC-5
    assert notizie.ordini_in_corso(datetime(2026, 11, 12, 14, 45, tzinfo=UTC))        # 9:45
    assert notizie.ordini_in_corso(datetime(2026, 11, 12, 14, 6, tzinfo=UTC))         # 9:06
    assert notizie.ordini_in_corso(datetime(2026, 11, 12, 20, 55, tzinfo=UTC))        # 15:55
    assert not notizie.ordini_in_corso(datetime(2026, 11, 12, 11, 30, tzinfo=UTC))    # 6:30
    assert not notizie.ordini_in_corso(datetime(2026, 11, 12, 17, 0, tzinfo=UTC))     # 12:00
    assert not notizie.ordini_in_corso(datetime(2026, 11, 14, 14, 45, tzinfo=UTC))    # sabato


def test_la_pausa_copre_anche_banca_centrale_sera_della_miscela_prova_45_e_chiusure_anticipate():
    # 9 dicembre 2026: comunicato della banca centrale (la miscela vende alle 13:59); l'8 è la vigilia (compra alle 14:00)
    assert notizie.ordini_in_corso(datetime(2026, 12, 9, 18, 59, tzinfo=UTC))         # 13:59
    assert notizie.ordini_in_corso(datetime(2026, 12, 8, 19, 0, tzinfo=UTC))          # 14:00 della vigilia
    assert not notizie.ordini_in_corso(datetime(2026, 12, 10, 19, 0, tzinfo=UTC))     # il giorno dopo: niente
    assert notizie.ordini_in_corso(datetime(2026, 11, 12, 20, 29, tzinfo=UTC))        # 15:29: l'ingresso della prova 45
    assert notizie.ordini_in_corso(datetime(2026, 11, 13, 0, 5, tzinfo=UTC))          # 19:05: la sera della miscela
    assert notizie.ordini_in_corso(datetime(2026, 11, 12, 13, 30, tzinfo=UTC))        # 8:30: la riserva della sera
    assert notizie.ordini_in_corso(datetime(2026, 11, 27, 17, 30, tzinfo=UTC))        # 12:30 del 27 novembre (chiude alle 13)
    assert not notizie.ordini_in_corso(datetime(2026, 11, 30, 17, 30, tzinfo=UTC))    # 12:30 di un giorno normale


def test_i_mesi():
    assert len(notizie.mesi(2016, 2024)) == 108
