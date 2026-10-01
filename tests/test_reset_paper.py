"""
`scripts/reset_paper.py` (1 ott 2026, backlog D5): il reset azzera anche
l'inizio del paper (`/account/paper_started_at`) e il prezzo BTC di partenza
(`/account/btc_inizio`), che il bot riscrive da solo al riavvio. Senza, dopo
un reset i giorni del paper e il confronto con BTC partirebbero dal paper
vecchio. Tutto su uno store in memoria: lo script vero non si esegue.
"""
from __future__ import annotations

from bot.core.firebase_client import FirebaseClient
from scripts import reset_paper


def _store() -> FirebaseClient:
    fb = FirebaseClient()          # senza credenziali: store in memoria
    fb.set_rtdb("/positions", {"AUSDT": {"symbol": "AUSDT"}})
    fb.set_rtdb("/account/equity", 931.0)
    fb.set_rtdb("/account/starting_equity", 1000.0)
    fb.set_rtdb("/account/paper_started_at", 1758000000.0)
    fb.set_rtdb("/account/btc_inizio", {"ts": 1758002400.0, "close": 115000.0})
    fb.set_doc("trades", "t1", {"trade_id": "t1", "pnl": -1.0})
    fb.set_doc("strategy_registry", "validated", {"ready": True})
    return fb


def test_il_reset_azzera_inizio_del_paper_e_btc_di_partenza(monkeypatch, capsys):
    fb = _store()
    monkeypatch.setattr(reset_paper, "get_firebase", lambda: fb)
    assert reset_paper.main(["--yes"]) == 0
    assert fb.get_rtdb("/account/paper_started_at") is None
    assert fb.get_rtdb("/account/btc_inizio") is None
    # il resto del reset come prima
    assert fb.get_rtdb("/account/equity") == 1000.0
    assert fb.get_rtdb("/positions") is None
    assert fb.list_doc_ids("trades") == []
    assert fb.get_doc("strategy_registry", "validated") == {"ready": True}   # GATE 1 resta
    out = capsys.readouterr().out
    assert "/account/paper_started_at, /account/btc_inizio" in out


def test_senza_yes_non_tocca_niente(monkeypatch, capsys):
    fb = _store()
    monkeypatch.setattr(reset_paper, "get_firebase", lambda: fb)
    assert reset_paper.main([]) == 0
    assert fb.get_rtdb("/account/paper_started_at") == 1758000000.0
    assert fb.get_rtdb("/account/btc_inizio") == {"ts": 1758002400.0, "close": 115000.0}
    assert "DRY-RUN" in capsys.readouterr().out


def test_i_due_percorsi_sono_quelli_che_il_bot_riscrive():
    import inspect

    from bot import main as bot_main
    assert reset_paper.INIZIO_PAPER == ("/account/paper_started_at", "/account/btc_inizio")
    src = inspect.getsource(bot_main)
    # il bot li riscrive quando mancano: e' quello che rende sicuro il None
    assert 'if not self.fb.get_rtdb("/account/paper_started_at"):' in src
    assert 'self.fb.set_rtdb("/account/btc_inizio", valore)' in src
