"""DRAWDOWN DI PORTAFOGLIO — la buca vera, quella che il gate non vede.

Il gate valida UNA coppia alla volta e misura la buca che quella coppia scava da
sola; con `GATE_MIN_RECOVERY >= 2` promuove solo curve regolari. Ma il bot ne
tiene aperte 9-12 insieme, quasi tutte su crypto che si muovono con BTC: dieci
curve regolari che scendono negli stessi giorni scavano insieme una buca che
nessuno dei numeri per coppia mostrava. Da qui l'illusione che il portafoglio
erediti la regolarita' delle sue parti — e un -17% in cinque giorni con ogni
coppia "validata" a recovery >= 2.

La differenza sta tutta nell'ORDINAMENTO: per coppia i trade sono in sequenza,
nel portafoglio vanno ordinati nel TEMPO, cosi' le perdite che sono avvenute
insieme si sommano davvero.
"""
import pytest

from backtesting.engine import max_concurrent, max_drawdown, portfolio_drawdown


class _T:
    def __init__(self, pnl_pct):
        self.pnl_pct = pnl_pct


def test_sequential_and_portfolio_agree_on_a_single_stream():
    """Una coppia sola: i due numeri devono coincidere, altrimenti il confronto
    fra loro non significherebbe nulla."""
    trades = [_T(0.10), _T(-0.04), _T(0.06), _T(-0.08)]
    seq = max_drawdown(trades)
    dd, tot = portfolio_drawdown([(i, t.pnl_pct) for i, t in enumerate(trades)])
    assert dd == pytest.approx(seq)
    assert tot == pytest.approx(0.04)


def test_simultaneous_losses_stack_into_one_deep_hole():
    """Tre coppie che perdono NELLO STESSO giorno e recuperano dopo.

    Guardate una per una la buca e' -1 ciascuna; guardate insieme e' -3. E' la
    situazione reale su crypto, dove le coin scendono con BTC.
    """
    per_pair = [[(10, -1.0), (20, +2.0)] for _ in range(3)]
    for stream in per_pair:
        dd_single, _ = portfolio_drawdown(stream)
        assert dd_single == pytest.approx(1.0)
    dd_all, tot = portfolio_drawdown([e for s in per_pair for e in s])
    assert dd_all == pytest.approx(3.0)      # tre volte peggio di ogni singola
    assert tot == pytest.approx(3.0)


def test_staggered_losses_do_not_stack():
    """Controprova: se le perdite NON coincidono nel tempo, il portafoglio non
    peggiora. Senza questo test la funzione potrebbe limitarsi a sommare tutto."""
    events = [(10, -1.0), (11, +2.0), (20, -1.0), (21, +2.0), (30, -1.0), (31, +2.0)]
    dd, tot = portfolio_drawdown(events)
    assert dd == pytest.approx(1.0)
    assert tot == pytest.approx(3.0)


def test_events_are_ordered_by_time_not_by_arrival():
    """I trade arrivano raggruppati per coppia; se non si riordinasse per tempo la
    curva sarebbe un artefatto dell'ordine di iterazione."""
    disordinati = [(30, +2.0), (10, -1.0), (20, -1.0)]
    dd, tot = portfolio_drawdown(disordinati)
    assert dd == pytest.approx(2.0)          # -1, -2, poi risale
    assert tot == pytest.approx(0.0)


def test_portfolio_drawdown_on_empty_input():
    assert portfolio_drawdown([]) == (0.0, 0.0)


def test_portfolio_drawdown_ignores_events_without_a_timestamp():
    dd, tot = portfolio_drawdown([(None, -5.0), (10, -1.0)])
    assert tot == pytest.approx(-1.0)


# ---- concentrazione -------------------------------------------------------- #
def test_max_concurrent_counts_overlapping_positions():
    assert max_concurrent([(0, 10), (1, 11), (2, 12)]) == 3
    assert max_concurrent([(0, 10), (20, 30), (40, 50)]) == 1


def test_touching_intervals_are_not_overlapping():
    """Un trade che chiude nell'istante in cui un altro apre non e' una
    sovrapposizione: contarlo sarebbe un falso positivo sulla concentrazione."""
    assert max_concurrent([(0, 10), (10, 20)]) == 1


def test_still_open_position_counts_as_open():
    # chiusura None = posizione ancora aperta: deve pesare sulla concentrazione
    assert max_concurrent([(0, None), (5, 6)]) == 2


def test_max_concurrent_on_empty_and_broken_input():
    assert max_concurrent([]) == 0
    assert max_concurrent([(None, 5)]) == 0
