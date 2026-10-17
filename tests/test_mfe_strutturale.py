"""IL LIVELLO STRUTTURALE ALL'INGRESSO (backlog A5, passo 1: misurare) — 24 set 2026.

I take profit sono multipli della distanza dello stop (R) e non guardano il
grafico. Prima di cambiarli si misura: il massimo/minimo recente viene raggiunto
piu' spesso del primo gradino? Qui si prova la funzione pura che trova quel
livello su candele sintetiche costruite a mano, e il conteggio del riepilogo.
Niente Firebase, niente rete: `livello_strutturale` e `riassunto_strutturale`
sono state estratte apposta per essere provate cosi'.
"""
from datetime import datetime, timedelta, timezone

import pytest

from bot.core.models import Candle
from scripts.mfe_report import (lettura_strutturale, livello_strutturale,
                                primo_gradino, riassunto_strutturale, stop_originale)

T0 = datetime(2026, 9, 1, tzinfo=timezone.utc)
PASSO = timedelta(minutes=15)


def _candele(n: int, high: float = 100.0, low: float = 90.0, inizio: datetime = T0) -> list[Candle]:
    """`n` candele a 15m, tutte con lo stesso range: il livello e' deciso dal test
    alzando o abbassando una candela precisa."""
    return [Candle(open_time=inizio + i * PASSO, open=95.0, high=high, low=low, close=95.0, volume=1.0)
            for i in range(n)]


def _ts(c: list[Candle], idx: int) -> float:
    """Epoch dell'open_time della candela `idx`: l'ingresso si mette LI'."""
    return c[idx].open_time.timestamp()


def test_long_finds_the_highest_high_above_entry_within_96_bars():
    c = _candele(300, high=100.0)
    c[250].high = 108.0          # dentro le ultime 96 prima dell'ingresso (idx 300-96=204)
    c[100].high = 120.0          # fuori dalle 96: NON deve contare
    out = livello_strutturale(c, _ts(c, 299) + 1, entry=101.0, stop=99.0, direction="long")
    # ingresso a 101 con stop a 99: R = 2. Livello 108 -> 3,5R.
    assert out == {"livello": 108.0, "lvl_r": pytest.approx(3.5), "barre": 96}


def test_long_falls_back_to_192_bars_when_96_have_nothing_above_entry():
    c = _candele(300, high=100.0)
    c[150].high = 105.0          # oltre le 96 (204..299) ma dentro le 192 (108..299)
    out = livello_strutturale(c, _ts(c, 299) + 1, entry=101.0, stop=99.0, direction="long")
    assert out == {"livello": 105.0, "lvl_r": pytest.approx(2.0), "barre": 192}


def test_short_uses_the_lowest_low_below_entry():
    c = _candele(300, low=90.0)
    c[260].low = 85.0
    out = livello_strutturale(c, _ts(c, 299) + 1, entry=89.0, stop=91.0, direction="short")
    # ingresso a 89, stop a 91: R = 2. Livello 85 -> 2R.
    assert out == {"livello": 85.0, "lvl_r": pytest.approx(2.0), "barre": 96}


def test_no_level_when_price_is_already_above_everything():
    c = _candele(300, high=100.0)
    assert livello_strutturale(c, _ts(c, 299) + 1, entry=101.0, stop=99.0, direction="long") is None


def test_zero_r_is_not_a_level():
    c = _candele(300, high=100.0)
    c[250].high = 108.0
    assert livello_strutturale(c, _ts(c, 299) + 1, entry=101.0, stop=101.0, direction="long") is None
    assert livello_strutturale(c, _ts(c, 299) + 1, entry=101.0, stop=None, direction="long") is None


def test_entry_before_the_first_candle_has_no_history():
    c = _candele(300, high=100.0)
    c[250].high = 108.0
    assert livello_strutturale(c, _ts(c, 0) - 1, entry=101.0, stop=99.0, direction="long") is None
    assert livello_strutturale([], _ts(c, 0), entry=101.0, stop=99.0, direction="long") is None


def test_only_candles_before_entry_are_used():
    """Una candela DOPO l'ingresso non e' struttura: e' futuro (look-ahead)."""
    c = _candele(300, high=100.0)
    c[299].high = 130.0
    out = livello_strutturale(c, _ts(c, 299), entry=101.0, stop=99.0, direction="long")
    assert out is None


def test_direction_accepts_the_enum_and_its_str_form():
    from bot.core.models import Direction
    c = _candele(300, low=90.0)
    c[260].low = 85.0
    a = livello_strutturale(c, _ts(c, 299) + 1, 89.0, 91.0, Direction.SHORT)
    b = livello_strutturale(c, _ts(c, 299) + 1, 89.0, 91.0, "Direction.SHORT")
    assert a == b and a["livello"] == 85.0


# --------------------------------------------------------------------------- #
# lo stop originale e il primo gradino, dal documento del trade                #
# --------------------------------------------------------------------------- #
def test_stop_originale_prefers_the_post_mortem_over_a_moved_stop_price():
    """Alla chiusura `stop_price` e' spesso gia' a break-even: da solo darebbe
    R = 0. Il referto conserva la distanza dello stop originale."""
    t = {"entry_price": 100.0, "stop_price": 100.0, "direction": "long",
         "post_mortem": {"stop_pct": 0.02}}
    assert stop_originale(t) == pytest.approx(98.0)
    t["direction"] = "short"
    assert stop_originale(t) == pytest.approx(102.0)
    t["orig_stop"] = 97.0
    assert stop_originale(t) == 97.0


def test_stop_originale_falls_back_to_stop_price_and_then_to_none():
    assert stop_originale({"entry_price": 100.0, "stop_price": 98.0, "direction": "long"}) == 98.0
    assert stop_originale({"entry_price": 100.0, "direction": "long"}) is None
    assert stop_originale({"entry_price": 0, "stop_price": 98.0}) is None


def test_primo_gradino_uses_the_trade_ladder_when_present(monkeypatch):
    from bot.config import settings
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    assert primo_gradino({"scale_r_mults": [1.0, 2.0]}) == 1.0
    assert primo_gradino({"scale_r_mults": None}) == 1.5
    assert primo_gradino({}) == 1.5


# --------------------------------------------------------------------------- #
# il riepilogo                                                                 #
# --------------------------------------------------------------------------- #
def test_riassunto_counts_tp1_level_and_the_nearest_of_the_two():
    righe = [
        {"r1": 1.5, "lvl_r": 0.8, "mfe_r": 1.0},   # livello si, TP1 no
        {"r1": 1.5, "lvl_r": 2.0, "mfe_r": 1.6},   # TP1 si, livello no
        {"r1": 1.5, "lvl_r": 0.5, "mfe_r": 0.2},   # nessuno dei due
        {"r1": 1.5, "lvl_r": 1.5, "mfe_r": 1.5},   # entrambi (uguaglianza inclusa)
    ]
    ri = riassunto_strutturale(righe)
    assert ri["n"] == 4
    assert ri["n_tp1"] == 2 and ri["n_livello"] == 2 and ri["n_min"] == 3
    assert ri["pct_tp1"] == 50 and ri["pct_livello"] == 50 and ri["pct_min"] == 75
    assert ri["mediana_lvl_r"] == pytest.approx(1.15)
    assert ri["mediana_r1"] == 1.5
    assert ri["n_livello_sotto_tp1"] == 2
    frase = lettura_strutturale(ri)
    assert "1.15R" in frase and "50%" in frase and "75%" in frase
    assert "indizio" in frase          # 4 trade non sono una misura


def test_riassunto_on_nothing_does_not_divide_by_zero():
    ri = riassunto_strutturale([])
    assert ri["n"] == 0 and ri["pct_tp1"] is None
    assert "nessun trade" in lettura_strutturale(ri)
