"""QUALITA' DI UN BACKTEST — le misure che dicono se un risultato vale qualcosa.

Il PF e il ritorno totale non bastano: due strategie con lo stesso guadagno
possono avere profili di rischio opposti, e un risultato costruito su trenta
trade e' un aneddoto, non un risultato.

Il test piu' importante e' `lookahead_is_detected`: e' un controllo di
COMPORTAMENTO, non di codice. Rileggere gli indicatori cercando l'uso del futuro
sfugge sempre a qualche caso; rigirare lo stesso backtest su dati TRONCATI e
verificare che i trade gia' conclusi siano identici e' invece una prova.
"""
import datetime as dt

import pytest

from backtesting.quality import (GREEN, RED, YELLOW, daily_returns,
                                 find_lookahead, max_drawdown_dated, sharpe,
                                 sortino, validation_light)


class _T:
    def __init__(self, pnl_pct, day=1, entry=100.0, exit_=101.0):
        self.pnl_pct = pnl_pct
        self.entry_ts = dt.datetime(2026, 1, day, tzinfo=dt.timezone.utc).timestamp()
        self.entry_price, self.exit_price = entry, exit_


# ---- aggregazione giornaliera ---------------------------------------------- #
def test_returns_are_bucketed_by_day():
    """Sharpe e Sortino vogliono una serie a passo costante: i trade non lo sono,
    e usarli come osservazioni equidistanti gonfia o sgonfia la volatilita' a
    seconda di quanto si trada."""
    r = daily_returns([_T(0.01, day=1), _T(0.02, day=1), _T(-0.01, day=2)])
    assert r["2026-01-01"] == pytest.approx(0.03)
    assert r["2026-01-02"] == pytest.approx(-0.01)


def test_trades_without_a_timestamp_are_ignored():
    """Attribuirli a un giorno arbitrario falserebbe proprio la dispersione che
    si sta misurando."""
    t = _T(0.05)
    t.entry_ts = 0
    assert daily_returns([t]) == {}


# ---- Sharpe e Sortino ------------------------------------------------------- #
def test_sharpe_is_none_when_it_cannot_be_computed():
    """None non e' zero: "non lo so" e "e' pessimo" sono cose diverse, e mostrare
    0 dove manca il dato farebbe scartare strategie mai misurate."""
    assert sharpe([_T(0.01, day=1)]) is None
    assert sharpe([_T(0.01, day=d) for d in (1, 2, 3)]) is None  # nessuna dispersione


def test_a_steadier_curve_scores_higher():
    regolare = [_T(0.01, day=d) for d in range(1, 21)]
    regolare[5].pnl_pct = 0.011
    ballerina = [_T(0.05 if d % 2 else -0.03, day=d) for d in range(1, 21)]
    assert sharpe(regolare) > sharpe(ballerina)


def test_sortino_ignores_upside_volatility():
    """Sotto scale-out i guadagni arrivano da poche corse lunghe: la deviazione
    standard totale penalizza i giorni buoni, che non sono un rischio."""
    # giorni quasi tutti piccoli e positivi, due perdite lievi, e UNA corsa
    # lunga: la deviazione standard totale esplode per colpa del giorno buono,
    # quella al ribasso no.
    trades = ([_T(0.01, day=d) for d in range(1, 13)]
              + [_T(-0.005, day=13), _T(-0.004, day=14), _T(0.30, day=15)])
    assert sortino(trades) > sharpe(trades)


def test_sortino_is_none_without_any_bad_day():
    assert sortino([_T(0.02, day=d) for d in range(1, 10)]) is None


# ---- drawdown con la data --------------------------------------------------- #
def test_drawdown_reports_when_it_happened():
    """Un drawdown concentrato in una settimana racconta un evento, uno spalmato
    su mesi racconta un'erosione: sono due problemi diversi."""
    dd, day = max_drawdown_dated([_T(0.10, day=1), _T(-0.04, day=2),
                                  _T(-0.03, day=3), _T(0.20, day=4)])
    assert dd == pytest.approx(0.07)
    assert day == "2026-01-03"


def test_drawdown_orders_by_time_not_by_arrival():
    a = max_drawdown_dated([_T(0.10, day=1), _T(-0.05, day=2)])
    b = max_drawdown_dated([_T(-0.05, day=2), _T(0.10, day=1)])
    assert a == b


# ---- semaforo ---------------------------------------------------------------- #
def test_a_good_backtest_is_green():
    v = validation_light(sharpe_ratio=1.4, max_dd=0.15, n_trades=200,
                         total_return=0.8, benchmark_return=0.3)
    assert v["level"] == GREEN and v["passed"] is True


def test_the_most_severe_criterion_wins():
    """Uno Sharpe eccellente non compensa trenta trade: con un campione piccolo
    lo Sharpe stesso e' rumore, e mediare i voti significherebbe farsi convincere
    dalla metrica meno affidabile."""
    v = validation_light(sharpe_ratio=3.0, max_dd=0.05, n_trades=30, total_return=1.0)
    assert v["level"] == RED and v["passed"] is False
    assert any("30 trade" in r for r in v["reasons"])


def test_losing_to_the_benchmark_is_red():
    v = validation_light(sharpe_ratio=1.2, max_dd=0.10, n_trades=300,
                         total_return=0.10, benchmark_return=0.40)
    assert v["level"] == RED
    assert any("benchmark" in r for r in v["reasons"])


def test_a_thin_sample_is_yellow_not_red():
    v = validation_light(sharpe_ratio=1.1, max_dd=0.20, n_trades=80, total_return=0.3)
    assert v["level"] == YELLOW and v["passed"] is True


def test_an_uncomputable_sharpe_is_a_warning_not_a_pass():
    v = validation_light(sharpe_ratio=None, max_dd=0.10, n_trades=300, total_return=0.5)
    assert v["level"] == YELLOW


# ---- look-ahead: la prova col dataset contaminato -------------------------- #
def _series(n=900, drift=0.0008):
    import datetime as _dt
    from bot.core.models import Candle
    out, close = [], 100.0
    t0 = _dt.datetime(2026, 1, 1, tzinfo=_dt.timezone.utc)
    for k in range(n):
        op = close
        close = op * (1 + (drift if (k // 37) % 2 == 0 else -drift))
        out.append(Candle(open_time=t0 + _dt.timedelta(minutes=15 * k), open=op,
                          high=max(op, close) * 1.003, low=min(op, close) * 0.997,
                          close=close, volume=1e6))
    return out


class _Honest:
    """Decide solo su cio' che vede nello snapshot della barra corrente."""
    name = "honest"
    params: dict = {}

    def is_active_in(self, regime):
        return True

    def generate_signal(self, asset, ctx=None):
        from bot.core.models import Direction, StrategySignal
        i = asset.ind("15m")
        if not i or i.rsi is None or i.rsi > 45:
            return None
        p = asset.price
        return StrategySignal(strategy=self.name, symbol=asset.symbol,
                              direction=Direction.LONG, confidence=60.0, reasoning="t",
                              suggested_stop=p * 0.98, suggested_target=p * 1.04)


def _contaminated_frame(candles):
    """Frame con un indicatore che LEGGE IL FUTURO.

    E' il difetto vero da cui ci si difende: un indicatore calcolato senza
    `shift`, che alla barra i porta gia' il valore della barra i+k. La strategia
    non sa di barare — usa l'RSI come sempre — ed e' esattamente cosi' che il
    look-ahead entra nei sistemi veri, senza che nessuno lo scriva apposta.
    """
    from bot.core.indicators import compute_indicator_frame
    f = compute_indicator_frame(candles)
    f["rsi"] = f["rsi"].shift(-20)       # <-- il futuro nel presente
    return f


def test_an_honest_strategy_passes_the_lookahead_check():
    from backtesting.engine import Backtester
    bt = Backtester(window=200, capital=10_000.0, interval_hours=0.25)
    candles = _series()
    assert find_lookahead(bt, _Honest, "TESTUSDT", candles) is None


def test_lookahead_is_detected_on_a_contaminated_dataset():
    """Il cuore del controllo. L'indicatore contaminato porta alla barra i un
    valore della barra i+20: troncando la serie quel valore cambia, e con esso
    cambiano trade gia' CONCLUSI nel passato. Il rilevatore se ne accorge senza
    sapere nulla di come e' fatta la strategia — misura l'effetto, non la causa."""
    from backtesting.engine import Backtester
    bt = Backtester(window=200, capital=10_000.0, interval_hours=0.25)
    msg = find_lookahead(bt, _Honest, "TESTUSDT", _series(),
                         frame_fn=_contaminated_frame)
    assert msg is not None and "LOOK-AHEAD" in msg
    assert "rsi" in msg, "deve dire QUALE indicatore, non solo che c'e' un problema"


def test_a_series_too_short_gives_no_verdict():
    """Meglio "non lo so" di un falso via libera su una prova senza margine."""
    from backtesting.engine import Backtester
    bt = Backtester(window=200, capital=10_000.0, interval_hours=0.25)
    assert find_lookahead(bt, _Honest, "TESTUSDT", _series(n=260)) is None
