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


def test_i_mesi():
    assert len(notizie.mesi(2016, 2024)) == 108
