"""Regole di PORTAFOGLIO e metri del gate aggiunti il 24 set 2026.

Cosa si protegge: il tetto di rischio per direzione blocca il trade che porterebbe
il rischio aperto di un lato oltre il tetto (e non l'altro lato); la statistica t
finisce nel registro e `gate` la stampa senza usarla per decidere; le candidate
casuali della discovery hanno un tetto dichiarato.
"""
import inspect

from bot.core.models import Direction
from bot.risk.daily_cap import direzione_bloccata, rischio_direzione


class _Pos:
    def __init__(self, direction, risk):
        self.direction = direction
        self.risk_effective_pct = risk


def test_rischio_per_direzione_somma_solo_quel_lato():
    pos = [_Pos(Direction.SHORT, 0.01), _Pos(Direction.SHORT, 0.005),
           {"direction": "short", "risk_effective_pct": 0.01},
           _Pos(Direction.LONG, 0.01)]
    assert abs(rischio_direzione(pos, Direction.SHORT) - 0.025) < 1e-9
    assert abs(rischio_direzione(pos, "long") - 0.01) < 1e-9
    assert rischio_direzione([], "long") == 0.0


def test_tetto_per_direzione_blocca_la_quarta_short_non_il_long():
    tre_short = [_Pos(Direction.SHORT, 0.01) for _ in range(3)]
    motivo = direzione_bloccata(tre_short, Direction.SHORT, 0.03)
    assert motivo and "tetto per direzione" in motivo and "3.00%" in motivo
    assert direzione_bloccata(tre_short, Direction.LONG, 0.03) is None
    assert direzione_bloccata(tre_short[:2], Direction.SHORT, 0.03) is None   # la terza entra
    assert direzione_bloccata(tre_short, Direction.SHORT, 0) is None          # spento


def test_nel_bot_la_regola_per_direzione_e_una_sola():
    """Audit del 24 set: il tetto per direzione esisteva gia' dall'8 set
    (`_directional_risk_blocks`, MAX_DIRECTIONAL_RISK_PCT). La copia aggiunta il
    24 set e' stata tolta: nel bot deve restare UNA regola, e un solo parametro."""
    from bot import main as bot_main
    from bot.config import settings
    src = inspect.getsource(bot_main.TradingBot)
    assert "direzione_bloccata(" not in src
    assert src.count("_directional_risk_blocks(decision.direction") == 1
    assert not hasattr(settings, "MAX_RISK_PER_DIRECTION")
    assert settings.MAX_DIRECTIONAL_RISK_PCT == 0.03


def test_la_statistica_t_finisce_nel_registro():
    from bot.core.firebase_client import decode_pairs
    from scripts.discover_strategies import merge_into_registry

    class FB:
        def __init__(self): self.docs = {}
        def get_doc(self, c, d): return self.docs.get((c, d), {})
        def set_doc(self, c, d, data): self.docs[(c, d)] = data

    from bot.core.firebase_client import encode_pairs
    fb = FB()
    # la coppia e' GIA' validata: i campi descrittivi restano solo alle validate
    # (slim_registry), ed e' li' che la statistica serve
    fb.docs[("strategy_registry", "validated")] = {"pairs": encode_pairs(
        {"A|gen_t": {"pass_count": 3, "generated": True, "symbol": "A",
                     "strategy": "gen_t", "last_seen_at": 1e9, "window_start": 1e9}})}
    e = {"symbol": "A", "strategy": "gen_t", "params": {}, "oos_pf": 1.5,
         "oos_pnl_pct": 0.3, "oos_trades": 40, "oos_win_rate": 0.5, "passed": True,
         "holdout": {"ok": True}, "data_end": 1e9, "t_stat": 2.31}
    merge_into_registry(fb, {"A|gen_t": e}, ["A|gen_t"], evaluated_symbols={"A"})
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    assert pairs["A|gen_t"]["last_t"] == 2.31


def test_gate_progress_stampa_la_statistica_t_senza_deciderla():
    from scripts import gate_progress
    src = inspect.getsource(gate_progress.main)
    assert "STATISTICA t DELLE VALIDATE" in src and "non usata per decidere" in src


def test_le_candidate_casuali_hanno_un_tetto():
    from scripts import discover_strategies as d
    assert d.RANDOM_MAX == 40
    src = inspect.getsource(d.main)
    assert "min(args.generate - len(ai_specs) - len(varianti), RANDOM_MAX)" in src
