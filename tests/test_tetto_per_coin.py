"""TETTO DI PERDITA PER COIN AL GIORNO — la regola che chiude la fila.

21 set 2026: tre short consecutivi su USELESSUSDT, -1,74% del conto in quaranta
minuti da una coin sola. Il cooldown frena la fila; questo tetto la chiude.
"""
from datetime import datetime, timezone

from bot.risk.daily_cap import coin_bloccata, perdita_oggi

NOW = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc).timestamp()
OGGI = NOW - 3600
IERI = NOW - 86400 * 1.5


def _t(sym, pnl, ts):
    return {"symbol": sym, "pnl": pnl, "exit_ts": ts}


def test_somma_solo_le_perdite_di_oggi_di_quella_coin():
    tr = [_t("USELESSUSDT", -8.25, OGGI), _t("USELESSUSDT", -8.65, OGGI),
          _t("USELESSUSDT", -5.0, IERI), _t("MUBARAKUSDT", -3.0, OGGI)]
    assert perdita_oggi(tr, "USELESSUSDT", NOW) == 16.9


def test_le_vincite_NON_compensano():
    """Altrimenti una vincita da 5 permetterebbe altri cinque stop da 1: il tetto
    e' su quanto si e' perso, non sul netto."""
    tr = [_t("X", -8.0, OGGI), _t("X", +20.0, OGGI)]
    assert perdita_oggi(tr, "X", NOW) == 8.0


def test_il_caso_useless_viene_bloccato_al_terzo():
    """Equity 970, tetto 1,5% = 14,55: dopo -8,25 e -8,65 (16,90) la coin e'
    chiusa fino a mezzanotte. Il terzo short del 21 set non sarebbe partito."""
    tr = [_t("USELESSUSDT", -8.25, OGGI), _t("USELESSUSDT", -8.65, OGGI)]
    m = coin_bloccata(tr, "USELESSUSDT", NOW, equity=970.0, cap=0.015)
    assert m and "USELESSUSDT" in m and "1.50%" in m
    # dopo il primo solo, no
    assert coin_bloccata(tr[:1], "USELESSUSDT", NOW, 970.0, 0.015) is None


def test_zero_spegne_la_regola():
    tr = [_t("X", -100.0, OGGI)]
    assert coin_bloccata(tr, "X", NOW, 970.0, 0.0) is None


def test_exit_ts_in_formato_iso_viene_letto():
    """Lo stesso difetto del confronto gate/paper del 21 set: una data ISO che
    diventa zero farebbe sparire i trade dal conto, cioe' spegnerebbe il tetto in
    silenzio."""
    iso = datetime.fromtimestamp(OGGI, timezone.utc).isoformat()
    assert perdita_oggi([{"symbol": "X", "pnl": -4.0, "exit_ts": iso}], "X", NOW) == 4.0


def test_il_bot_lo_applica_anche_in_parita():
    import inspect

    from bot.main import TradingBot

    src = inspect.getsource(TradingBot._try_open)
    assert "coin_bloccata(" in src
    i = src.index("if settings.RISK_PER_COIN_DAY > 0:")
    assert "BACKTEST_PARITY" not in src[i:i + 500]
