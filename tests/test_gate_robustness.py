"""ROBUSTEZZA: la strategia regge senza i suoi colpi migliori?

Sotto scale-out il risultato non e' distribuito: poche corse lunghe pagano tutte
le perdite. E' anche la statistica piu' instabile che esista, quindi scegliere il
meglio fra migliaia di candidate su una metrica che ne dipende seleziona la coda
piu' fortunata invece dell'edge.

Caso reale che ha motivato il criterio (BIRBUSDT|gen_472f85b8): holdout di 94
trade, +29.5%, PF 1.18 -> passava. Togliendo i 7 trade migliori gli altri 87
perdevano il 22.6%. Nel paper la stessa coppia ha fatto PF 0.16.
"""
import pytest

from backtesting.engine import passes_gate, pf_without_top
from bot.config import settings


class _T:
    def __init__(self, pnl_pct):
        self.pnl_pct = pnl_pct


def _trades(pnls):
    return [_T(p) for p in pnls]


def test_pf_without_top_removes_the_best_trades():
    # 19 perdite da -1 e un solo colpo da +30: PF ottimo, ma e' UN trade.
    t = _trades([-1.0] * 19 + [30.0])
    assert pf_without_top(t, 0.0) == pytest.approx(30 / 19)   # PF normale, buono
    assert pf_without_top(t, 0.05) == 0.0                     # tolto il colpo -> nulla


def test_pf_without_top_always_drops_at_least_one():
    # con 5 trade, int(5*0.05) = 0: senza il max(1,...) il test sarebbe inefficace
    t = _trades([-1.0, -1.0, -1.0, -1.0, 10.0])
    assert pf_without_top(t, 0.05) == 0.0


def test_pf_without_top_survives_a_broad_edge():
    # stesso PF complessivo ma distribuito: togliere il migliore non lo affonda
    t = _trades([-1.0] * 10 + [1.6] * 10)
    assert pf_without_top(t, 0.05) > 1.0


def test_pf_without_top_on_empty_and_all_winners():
    assert pf_without_top([], 0.05) == 0.0
    # nessuna perdita: PF "infinito" -> valore alto, non deve dividere per zero
    assert pf_without_top(_trades([1.0, 2.0, 3.0]), 0.05) > 100


def test_gate_rejects_a_strategy_carried_by_its_tail(monkeypatch):
    monkeypatch.setattr(settings, "GATE_MIN_PF_EX_TOP", 1.0)
    common = dict(window_pnls=[0.2, 0.2, 0.2], n_trades=100, pf=1.5,
                  win_rate=0.5, total_return=0.5, max_dd=0.1)
    # tutto il resto identico: passa o meno SOLO per la robustezza
    assert passes_gate(**common, pf_ex_top=1.4) is True
    assert passes_gate(**common, pf_ex_top=0.8) is False


def test_gate_unchanged_when_robustness_not_provided(monkeypatch):
    """Retro-compatibilita': chi non passa pf_ex_top non deve cambiare verdetto."""
    monkeypatch.setattr(settings, "GATE_MIN_PF_EX_TOP", 1.0)
    assert passes_gate([0.2, 0.2, 0.2], 100, 1.5, 0.5, 0.5, max_dd=0.1) is True


def test_robustness_can_be_disabled(monkeypatch):
    monkeypatch.setattr(settings, "GATE_MIN_PF_EX_TOP", 0.0)
    assert passes_gate([0.2, 0.2, 0.2], 100, 1.5, 0.5, 0.5,
                       max_dd=0.1, pf_ex_top=0.1) is True
