"""MODALITA' REPLAY — confronto trade-per-trade fra paper e gate (Fase 1.1).

Il paper ha operato in giorni precisi; il gate viene rigirato sulla STESSA
finestra di calendario e i trade si accoppiano per vicinanza temporale. Il numero
che conta e' quanti trade paper NON trovano un segnale corrispondente: quella e'
divergenza di GENERAZIONE, la piu' grave delle tre (generazione / esecuzione /
uscite).

L'accoppiamento e' la parte fragile ed e' cio' che questi test difendono: un
segnale del gate puo' essere consumato una volta sola, altrimenti piu' trade
paper ravvicinati si accopperebbero tutti allo stesso e il conteggio dei
"non accoppiati" — cioe' la misura stessa — perderebbe significato.
"""
import datetime as dt

import pytest

from scripts.gate_vs_paper import _match, _price_move, _ts


class _Sim:
    """Minimo indispensabile di un SimTrade per l'accoppiamento."""
    def __init__(self, ts, entry_price=100.0, mfe_r=1.0, pnl_pct=0.01):
        self.entry_ts = ts
        self.entry_price = entry_price
        self.mfe_r = mfe_r
        self.pnl_pct = pnl_pct


def _p(ts, **kw):
    d = {"entry_time": dt.datetime.fromtimestamp(ts, dt.timezone.utc).isoformat(),
         "entry_price": 100.0, "exit_price": 101.0, "direction": "long"}
    d.update(kw)
    return d


# ---- lettura dei timestamp ------------------------------------------------- #
def test_ts_reads_iso_and_numbers_and_survives_garbage():
    iso = "2026-08-10T15:57:17.397554+00:00"
    assert _ts(iso) == pytest.approx(dt.datetime.fromisoformat(iso).timestamp())
    assert _ts(1_700_000_000.0) == 1_700_000_000.0
    assert _ts(None) == 0.0 and _ts("non una data") == 0.0


# ---- variazione di prezzo con segno ---------------------------------------- #
def test_price_move_signs_by_direction():
    # long che sale guadagna, short che sale perde
    assert _price_move(_p(0, entry_price=100.0, exit_price=110.0)) == pytest.approx(0.10)
    assert _price_move(_p(0, entry_price=100.0, exit_price=110.0,
                          direction="short")) == pytest.approx(-0.10)


def test_price_move_is_zero_without_a_usable_entry():
    assert _price_move({"entry_price": 0, "exit_price": 10}) == 0.0
    assert _price_move({}) == 0.0


# ---- accoppiamento --------------------------------------------------------- #
def test_match_pairs_by_time_proximity():
    base = 1_700_000_000
    paper = [_p(base), _p(base + 3600)]
    sim = [_Sim(base + 60), _Sim(base + 3660)]
    out = _match(paper, sim, tol_s=1800)
    assert [s.entry_ts for _, s in out] == [base + 60, base + 3660]


def test_unmatched_paper_trade_is_reported_not_dropped():
    """Un trade paper senza segnale del gate e' IL risultato: se sparisse dal
    conteggio, la divergenza piu' grave diventerebbe invisibile."""
    base = 1_700_000_000
    out = _match([_p(base)], [_Sim(base + 999_999)], tol_s=1800)
    assert len(out) == 1 and out[0][1] is None


def test_a_gate_signal_is_consumed_only_once():
    """Due trade paper vicini non possono accoppiarsi allo STESSO segnale:
    il secondo deve risultare non accoppiato."""
    base = 1_700_000_000
    paper = [_p(base), _p(base + 10)]
    out = _match(paper, [_Sim(base + 5)], tol_s=1800)
    assert sum(1 for _, s in out if s is not None) == 1
    assert sum(1 for _, s in out if s is None) == 1


def test_match_picks_the_nearest_available_signal():
    base = 1_700_000_000
    out = _match([_p(base)], [_Sim(base + 1500), _Sim(base + 100)], tol_s=1800)
    assert out[0][1].entry_ts == base + 100


def test_match_respects_the_tolerance_window():
    base = 1_700_000_000
    assert _match([_p(base)], [_Sim(base + 1799)], tol_s=1800)[0][1] is not None
    assert _match([_p(base)], [_Sim(base + 1801)], tol_s=1800)[0][1] is None


def test_match_handles_empty_sides():
    base = 1_700_000_000
    assert _match([], [_Sim(base)], tol_s=60) == []
    out = _match([_p(base)], [], tol_s=60)
    assert len(out) == 1 and out[0][1] is None
