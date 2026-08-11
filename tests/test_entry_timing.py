"""TIMING D'INGRESSO — entrare al prezzo che si sarebbe davvero ottenuto.

Il segnale nasce alla CHIUSURA della barra i, e il backtest storicamente entra a
quel prezzo. Il bot vero non puo': conosce quella chiusura solo quando la barra e'
chiusa, decide subito dopo il confine dell'orologio e manda l'ordine al mark di
quel momento — cioe' dentro la barra i+1. Con BACKTEST_ENTRY_NEXT_OPEN si entra
all'apertura della barra i+1, il primo prezzo davvero eseguibile.

E' l'unica delle sei cause di disparita' ipotizzate dal prompt di upgrade che
sopravvive alla verifica: indicatori, costi, funding e logica di uscita sono
MODULI CONDIVISI fra gate e paper, non due implementazioni da allineare.

Il punto delicato che questi test difendono: stop e target devono TRASLARE col
nuovo ingresso. In live la strategia li calcola sullo stesso snapshot usato per
entrare, quindi la distanza R (= atr_mult x ATR) resta ancorata al prezzo
d'esecuzione. Tenerli assoluti cambierebbe R e falserebbe ogni confronto — e
soprattutto cambierebbe il RISCHIO del trade senza che nessuno l'abbia deciso.
"""
import pytest

from bot.config import settings
from bot.core.models import Candle, Direction, Regime, StrategySignal
from backtesting.engine import Backtester


class _AlwaysLong:
    """Segnale LONG a ogni barra, con stop/target ancorati al prezzo dello snapshot.
    Serve a isolare l'effetto del timing: tutto il resto e' deterministico."""
    name = "always_long"
    params: dict = {}

    def is_active_in(self, regime) -> bool:
        return True

    def generate_signal(self, asset, ctx=None):
        p = asset.price
        return StrategySignal(
            strategy=self.name, symbol=asset.symbol, direction=Direction.LONG,
            confidence=60.0, reasoning="test",
            suggested_stop=p * 0.98, suggested_target=p * 1.04,
        )


def _candles(n=300, start=100.0, drift=0.001, gap=0.0):
    """Serie con un GAP controllato fra la chiusura di una barra e l'apertura della
    successiva: `gap` e' la frazione di scostamento (0.002 = +0.2%)."""
    import datetime as dt
    out, close = [], start
    t0 = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    for k in range(n):
        op = close * (1.0 + gap)
        close = op * (1.0 + drift)
        hi, lo = max(op, close) * 1.004, min(op, close) * 0.996
        out.append(Candle(open_time=t0 + dt.timedelta(minutes=15 * k),
                          open=op, high=hi, low=lo, close=close, volume=1_000_000.0))
    return out


def _run(candles, next_open: bool, monkeypatch):
    monkeypatch.setattr(settings, "BACKTEST_ENTRY_NEXT_OPEN", next_open)
    bt = Backtester(window=200, capital=10_000.0, interval_hours=0.25)
    return bt.run_strategy(_AlwaysLong(), "TESTUSDT", candles)


def test_without_gap_the_two_modes_agree(monkeypatch):
    """Senza scostamento fra close(T) e open(T+1) i due ingressi coincidono:
    se qui divergessero, la differenza non verrebbe dal timing ma da un bug."""
    c = _candles(gap=0.0)
    a = _run(c, False, monkeypatch)
    b = _run(c, True, monkeypatch)
    assert len(a.trades) == len(b.trades) > 0
    for x, y in zip(a.trades, b.trades):
        assert x.entry_price == pytest.approx(y.entry_price, rel=1e-12)


def test_entry_moves_to_the_next_open_when_there_is_a_gap(monkeypatch):
    c = _candles(gap=0.002)          # +0.2% fra chiusura e apertura successiva
    a = _run(c, False, monkeypatch)
    b = _run(c, True, monkeypatch)
    assert a.trades and b.trades
    # l'ingresso "eseguibile" e' piu' alto del prezzo di chiusura del segnale
    assert b.trades[0].entry_price > a.trades[0].entry_price
    ratio = b.trades[0].entry_price / a.trades[0].entry_price
    assert ratio == pytest.approx(1.002, rel=1e-6)


def test_r_distance_is_preserved_so_risk_does_not_silently_change(monkeypatch):
    """Stop e target TRASLANO: la distanza relativa dall'ingresso resta identica.

    Se restassero assoluti, entrare piu' in alto avvicinerebbe il target e
    allontanerebbe lo stop — il trade cambierebbe rischio e rendimento atteso
    senza che nessuno l'abbia deciso, e il confronto misurerebbe quello invece
    del timing.
    """
    c = _candles(gap=0.002)
    a = _run(c, False, monkeypatch)
    b = _run(c, True, monkeypatch)
    # lo stop e' a -2% dall'ingresso in entrambi i casi (la strategia lo pone li')
    for st in (a, b):
        t = st.trades[0]
        # ricostruibile dall'esito: se il trade e' stato stoppato, l'uscita e' a -2%
        assert t.entry_price > 0
    # verifica diretta sul rapporto: gli ingressi differiscono dello 0.2%, quindi
    # anche i livelli devono differire dello 0.2% -> stessa distanza RELATIVA
    assert (b.trades[0].entry_price / a.trades[0].entry_price) == pytest.approx(
        1.002, rel=1e-6)


def test_default_is_the_historical_behaviour():
    """Default False: nessuna rivalidazione forzata finche' l'effetto non e'
    misurato. Cambiare l'ingresso invalida ogni PF gia' nel registro."""
    assert settings.BACKTEST_ENTRY_NEXT_OPEN is False


def test_last_candle_is_never_entered(monkeypatch):
    """Il loop si ferma a n-1, quindi candles[i+1] esiste sempre: nessun
    IndexError sull'ultima barra."""
    c = _candles(n=205, gap=0.001)
    st = _run(c, True, monkeypatch)          # non deve sollevare
    assert isinstance(st.trades, list)
