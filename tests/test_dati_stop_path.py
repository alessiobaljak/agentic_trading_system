"""IL PERCORSO DELLO STOP (1 ott 2026, la cattura dei dati mancanti).

Quando il profit-lock si arma e a quanti R, i passi dello stop effettivo (>= 0,05
R, al massimo 20), l'ultimo peggioramento del MAE e il MAE prima del TP1. Solo
misura: persistiti con la posizione e copiati sul trade chiuso.
"""
from __future__ import annotations

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import Direction
from bot.execution.executor import ExecutionEngine
from bot.learning import cattura
from tests.test_memoria_trade_misure import _asset, _params


@pytest.fixture
def lock(monkeypatch):
    """TP unico, profit-lock acceso (si arma a meta' strada, keep 0,5)."""
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)
    monkeypatch.setattr(settings, "PROFIT_LOCK_ENABLED", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_TRIGGER", 0.5)
    monkeypatch.setattr(settings, "PROFIT_LOCK_KEEP", 0.5)


@pytest.fixture
def scala(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    monkeypatch.setattr(settings, "SCALE_OUT_FRACTIONS", (0.3, 0.3, 0.4))
    monkeypatch.setattr(settings, "PROFIT_LOCK_ENABLED", False)


def test_stop_in_r_e_passi():
    assert cattura.stop_in_r(98.0, 100.0, 98.0, True) == -1.0
    assert cattura.stop_in_r(100.0, 100.0, 98.0, True) == 0.0
    assert cattura.stop_in_r(101.0, 100.0, 98.0, True) == 0.5
    assert cattura.stop_in_r(99.0, 100.0, 102.0, False) == 0.5
    assert cattura.stop_in_r(99.0, 100.0, 100.0, True) is None
    passi: list = []
    assert cattura.passo_stop(passi, -1.0, 1.0) is False          # dove gia' era
    assert cattura.passo_stop(passi, -0.97, 2.0) is False         # meno di 0,05 R
    assert cattura.passo_stop(passi, -0.95, 3.0) is True
    assert cattura.passo_stop(passi, 0.5, 4.0) is True
    assert passi == [{"t_s": 3.0, "r": -0.95}, {"t_s": 4.0, "r": 0.5}]
    pieni = [{"t_s": float(i), "r": float(i)} for i in range(20)]
    assert cattura.passo_stop(pieni, 99.0, 1.0) is False and len(pieni) == 20


def test_il_lock_che_si_arma_viene_registrato(lock):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110))
    pos = eng.open_positions["BTCUSDT"]
    # +6 (oltre meta' strada verso 110): high_water 106 a fine tick
    assert eng.update_position("BTCUSDT", 105.0, high=106.0, low=104.0) is None
    assert pos.lock_armed_at is None                     # si arma dal tick DOPO
    assert eng.update_position("BTCUSDT", 105.0, high=105.5, low=104.5) is None
    assert pos.lock_armed_at is not None
    assert pos.lock_stop_first_r == pytest.approx(1.5)   # 100 + 0,5 x 6 = 103 -> +1,5 R
    assert pos.stop_moves[-1]["r"] == pytest.approx(1.5)
    # sale ancora: nuovo passo
    eng.update_position("BTCUSDT", 107.5, high=108.0, low=107.0)
    eng.update_position("BTCUSDT", 107.5, high=107.6, low=107.4)
    assert pos.stop_moves[-1]["r"] == pytest.approx(2.0)   # 100 + 0,5 x 8 = 104
    assert pos.lock_stop_first_r == pytest.approx(1.5)   # il primo resta il primo
    closed = eng.update_position("BTCUSDT", 103.0, high=103.5, low=103.0)
    assert closed is not None and closed.exit_reason.value == "trailing_stop"
    assert closed.lock_armed_at_s is not None and closed.lock_armed_at_s >= 0
    assert closed.lock_stop_first_r == pytest.approx(1.5)
    assert [m["r"] for m in closed.stop_moves] == pytest.approx([1.5, 2.0])
    assert closed.mae_before_tp1_r == closed.mae_r        # TP1 mai arrivato (TP unico)


def test_stop_pieno_senza_lock_niente_passi(lock):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110))
    eng.update_position("BTCUSDT", 99.0, high=100.5, low=99.0)
    closed = eng.update_position("BTCUSDT", 97.5, high=99.0, low=97.5)
    assert closed.exit_reason.value == "stop_loss"
    assert closed.lock_armed_at_s is None and closed.lock_stop_first_r is None
    assert closed.stop_moves == []
    assert closed.t_mae_s is not None and closed.mae_r == pytest.approx(0.5)


def test_mae_prima_del_tp1_e_pareggio(scala):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110),
                      sl_to_breakeven=True)
    pos = eng.open_positions["BTCUSDT"]
    eng.update_position("BTCUSDT", 99.0, high=100.2, low=99.0)        # contro di 0,5 R
    eng.update_position("BTCUSDT", 103.0, high=103.2, low=100.0)      # TP1 (103)
    assert pos.t_tp1 is not None and pos.low_water_tp1 == 99.0
    eng.update_position("BTCUSDT", 101.0, high=101.5, low=100.5)
    eng.update_position("BTCUSDT", 100.6, high=100.8, low=100.4)
    # il pareggio (stop a 100 = 0 R) e' un passo dello stop
    assert [m["r"] for m in pos.stop_moves] == pytest.approx([0.0])
    closed = eng.update_position("BTCUSDT", 99.9, high=100.1, low=99.9)
    assert closed.exit_reason.value == "scale_out"
    assert closed.mae_before_tp1_r == pytest.approx(0.5)
    assert closed.mae_r == pytest.approx(0.5)


def test_il_percorso_sopravvive_al_riavvio(lock):
    fb = FirebaseClient()
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110))
    eng.update_position("BTCUSDT", 105.0, high=106.0, low=99.5)
    eng.update_position("BTCUSDT", 105.0, high=105.5, low=104.5)
    prima = eng.open_positions["BTCUSDT"]
    eng2 = ExecutionEngine(firebase=fb, dry_run=True)
    pos = eng2.open_positions["BTCUSDT"]
    assert pos.lock_armed_at == prima.lock_armed_at
    assert pos.lock_stop_first_r == prima.lock_stop_first_r
    assert pos.stop_moves == prima.stop_moves
    assert pos.t_mae == prima.t_mae


def test_documento_vecchio_si_ripristina_senza_le_chiavi(lock):
    fb = FirebaseClient()
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110))
    doc = dict(fb.get_rtdb("/positions/BTCUSDT"))
    for k in ("lock_armed_at", "lock_stop_first_r", "stop_moves", "t_mae", "low_water_tp1",
              "versione", "promessa_gate", "regime_globale", "ingresso", "expected_entry_price"):
        doc.pop(k, None)
    doc["stop_moves"] = "rotto"
    fb.set_rtdb("/positions/BTCUSDT", doc)
    pos = ExecutionEngine(firebase=fb, dry_run=True).open_positions["BTCUSDT"]
    assert pos.stop_moves == [] and pos.lock_armed_at is None and pos.versione is None


def _liste_annidate(v, percorso: str = "") -> list:
    """I percorsi in cui una lista sta DIRETTAMENTE dentro un'altra lista."""
    out = []
    if isinstance(v, dict):
        for k, x in v.items():
            out += _liste_annidate(x, f"{percorso}{k}.")
    elif isinstance(v, list):
        for i, x in enumerate(v):
            if isinstance(x, list):
                out.append(f"{percorso}{i}")
            out += _liste_annidate(x, f"{percorso}{i}.")
    return out


def test_il_trade_resta_scrivibile_su_firestore(lock):
    """Firestore rifiuta una lista dentro una lista: un documento rifiutato e'
    un trade NON registrato. Il trade chiuso con tutte le misure nuove non ne
    deve contenere (per questo `stop_moves` e' una lista di dizionari)."""
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100), "s", Direction.LONG, _params(stop=98, tp=110),
                      versione={"commit": "abc", "config_hash": "x"},
                      promessa_gate={"pass_count": 2})
    eng.update_position("BTCUSDT", 105.0, high=106.0, low=99.0)
    eng.update_position("BTCUSDT", 107.0, high=108.0, low=106.0)
    eng.update_position("BTCUSDT", 107.0, high=107.5, low=106.5)
    closed = eng.update_position("BTCUSDT", 103.0, high=103.5, low=103.0)
    assert closed.stop_moves                                   # ci sono passi
    doc = closed.model_dump(mode="json")
    assert _liste_annidate(doc) == []
    assert _liste_annidate({"x": [[1, 2]]}) == ["x.0"]         # il controllo funziona
