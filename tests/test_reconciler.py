"""RECONCILER — i cinque scenari di divergenza, uno per uno.

Il bot tiene uno stato interno delle posizioni; quando diverge da quello vero
prende decisioni su un mondo che non esiste. In paper e' impossibile per
costruzione, coi soldi veri e' la modalita' di fallimento piu' pericolosa: e'
silenziosa, e ci si accorge dal saldo.

Il test piu' importante di questo file e' `exchange_unreachable_never_closes`:
confondere "non lo so" con "e' vuoto" farebbe chiudere posizioni sane a ogni
problema di rete — il reconciler diventerebbe la causa del danno che deve
prevenire.
"""
import pytest

from bot.config import settings
from bot.execution.reconciler import (BALANCE_MISMATCH, CANCEL_ORDER, CLOSE_NOW,
                                      DROP_LOCAL, DUPLICATE, EXCHANGE_DOWN, GHOST,
                                      HALT, MISSING_SL, WAIT, ExchangeState,
                                      Reconciler, blocks_trading, reconcile)


def _ex(**kw):
    d = dict(reachable=True, positions={"BTCUSDT": 1.0},
             protective_orders={"BTCUSDT": 1}, duplicate_orders={}, balance=1000.0)
    d.update(kw)
    return ExchangeState(**d)


INTERNAL = {"BTCUSDT": 1.0}


def test_everything_matches_means_no_findings():
    assert reconcile(INTERNAL, 1000.0, _ex()) == []


# ---- 1) posizione senza protezione ----------------------------------------- #
def test_position_without_stop_is_closed_immediately():
    """La divergenza peggiore: una posizione con leva e senza stop puo' perdere
    senza limite. L'uscita a mercato costa meno del rischio di restare."""
    f = reconcile(INTERNAL, 1000.0, _ex(protective_orders={}))
    assert len(f) == 1
    assert f[0].event == MISSING_SL and f[0].action == CLOSE_NOW and f[0].critical


# ---- 2) posizione fantasma -------------------------------------------------- #
def test_ghost_position_resets_local_state():
    f = reconcile(INTERNAL, 1000.0, _ex(positions={}))
    assert [x.event for x in f] == [GHOST]
    assert f[0].action == DROP_LOCAL and f[0].symbol == "BTCUSDT"


def test_a_ghost_is_not_also_reported_as_unprotected():
    """Una posizione che sull'exchange non esiste non puo' essere "senza stop":
    due allarmi per lo stesso fatto renderebbero illeggibile il quadro."""
    f = reconcile(INTERNAL, 1000.0, _ex(positions={}, protective_orders={}))
    assert [x.event for x in f] == [GHOST]


def test_a_position_the_bot_does_not_know_is_flagged_but_not_touched():
    """Potrebbe essere manuale o di un altro processo: non si tocca. Ma operare
    senza sapere cosa c'e' aperto significa sbagliare il rischio di portafoglio."""
    f = reconcile({}, 1000.0, _ex(positions={"ETHUSDT": 2.0}))
    assert f[0].event == GHOST and f[0].action == WAIT and f[0].critical


# ---- 3) ordine duplicato ---------------------------------------------------- #
def test_duplicate_orders_are_reported_with_both_ids():
    f = reconcile(INTERNAL, 1000.0, _ex(duplicate_orders={"BTCUSDT": [11, 22]}))
    dup = [x for x in f if x.event == DUPLICATE]
    assert dup and dup[0].action == CANCEL_ORDER
    assert dup[0].detail["order_ids"] == [11, 22]


def test_a_single_order_is_not_a_duplicate():
    assert reconcile(INTERNAL, 1000.0, _ex(duplicate_orders={"BTCUSDT": [11]})) == []


# ---- 4) exchange irraggiungibile -------------------------------------------- #
def test_exchange_unreachable_never_closes():
    """"Non lo so" non e' "e' vuoto". Senza risposte affidabili una chiusura al
    buio puo' duplicare posizioni o fallire a meta': si aspetta e si avvisa."""
    f = reconcile(INTERNAL, 1000.0, ExchangeState(reachable=False))
    assert len(f) == 1
    assert f[0].event == EXCHANGE_DOWN and f[0].action == WAIT
    assert not any(x.action == CLOSE_NOW for x in f)
    assert not any(x.action == DROP_LOCAL for x in f)


def test_exchange_unreachable_without_positions_is_not_an_alarm():
    assert reconcile({}, None, ExchangeState(reachable=False)) == []


# ---- 5) saldo discordante --------------------------------------------------- #
def test_balance_shortfall_halts_everything():
    f = reconcile({}, 1000.0, _ex(positions={}, balance=900.0))
    assert f[0].event == BALANCE_MISMATCH and f[0].action == HALT
    assert f[0].detail["gap_pct"] == pytest.approx(10.0)


def test_small_balance_differences_are_tolerated():
    """Sotto la tolleranza ci stanno fee non ancora contabilizzate e funding in
    corso: allarmare li' vorrebbe dire allarmare sempre."""
    assert reconcile({}, 1000.0, _ex(positions={}, balance=995.0)) == []


def test_a_larger_real_balance_is_not_an_alarm():
    """Piu' soldi del previsto non e' una perdita: puo' essere funding incassato."""
    assert reconcile({}, 1000.0, _ex(positions={}, balance=1100.0)) == []


# ---- blocco delle nuove posizioni ------------------------------------------- #
def test_critical_findings_block_new_trades():
    assert blocks_trading(reconcile(INTERNAL, 1000.0, _ex(positions={}))) is True
    assert blocks_trading([]) is False
    # l'exchange giu' NON blocca: e' uno stato transitorio, non una divergenza
    assert blocks_trading(reconcile(INTERNAL, 1000.0,
                                    ExchangeState(reachable=False))) is False


# ---- il thread ------------------------------------------------------------- #
def test_reconciler_is_inert_in_dry_run(monkeypatch):
    monkeypatch.setattr(settings, "DRY_RUN", True)
    r = Reconciler(fetch=lambda: _ex(), snapshot=lambda: (INTERNAL, 1000.0))
    assert r.start() is False


def test_a_fetch_failure_is_treated_as_exchange_down_not_as_all_clear(monkeypatch):
    """Un'eccezione durante la lettura non deve MAI risultare "nessun problema":
    sarebbe il silenzio piu' pericoloso possibile."""
    def boom():
        raise RuntimeError("timeout")
    r = Reconciler(fetch=boom, snapshot=lambda: (INTERNAL, 1000.0))
    f = r.check_once(now=1000.0)
    assert [x.event for x in f] == [EXCHANGE_DOWN]


def test_downtime_start_is_remembered_then_cleared():
    state = {"up": False}
    r = Reconciler(fetch=lambda: _ex(reachable=state["up"]),
                   snapshot=lambda: (INTERNAL, 1000.0))
    r.check_once(now=1000.0)
    assert r._down_since == 1000.0
    r.check_once(now=1060.0)
    assert r._down_since == 1000.0, "la durata deve accumularsi, non azzerarsi"
    state["up"] = True
    r.check_once(now=1120.0)
    assert r._down_since is None


def test_alerts_are_rate_limited(monkeypatch):
    monkeypatch.setattr(settings, "RECONCILE_ALERT_COOLDOWN_S", 300)
    sent = []

    class N:
        def send(self, msg):
            sent.append(msg)
    r = Reconciler(fetch=lambda: _ex(positions={}), snapshot=lambda: (INTERNAL, 1000.0),
                   notifier=N())
    r.check_once(now=1000.0)
    r.check_once(now=1060.0)      # dentro il cooldown: niente secondo messaggio
    assert len(sent) == 1
    r.check_once(now=1400.0)
    assert len(sent) == 2


def test_findings_are_published_with_the_blocking_flag():
    class FB:
        def __init__(self):
            self.written = {}

        def set_rtdb(self, path, data):
            self.written[path] = data
    fb = FB()
    r = Reconciler(fetch=lambda: _ex(positions={}), snapshot=lambda: (INTERNAL, 1000.0),
                   firebase=fb)
    r.check_once(now=1000.0)
    doc = fb.written["/reconciliation"]
    assert doc["error"] is True and doc["findings"][0]["event"] == GHOST


# ---- applicazione delle azioni nel loop ------------------------------------ #
def test_the_loop_applies_the_actions_not_the_thread():
    """Le azioni che toccano le posizioni girano nel loop, non nel thread: mutarle
    da un thread mentre il loop le itera sarebbe una race condition, cioe' un
    secondo modo di divergere dalla realta' proprio nel componente che deve
    impedirlo. Qui si verifica che il fantasma venga rimosso dallo stato locale e
    la coin messa in quarantena, senza tentare chiusure."""
    from bot.core.firebase_client import FirebaseClient
    from bot.core.models import (AssetSnapshot, Direction, EffectiveRiskParams,
                                 IndicatorSnapshot, Regime)
    from bot.execution.executor import ExecutionEngine
    from bot.execution.reconciler import Finding
    from bot.main import TradingBot

    fb = FirebaseClient()
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    tf = settings.ORCHESTRATOR_TIMEFRAME
    asset = AssetSnapshot(symbol="BTCUSDT", price=100.0, regime=Regime.SIDEWAYS,
                          volume_24h=3e8, indicators={tf: IndicatorSnapshot(
                              timeframe=tf, atr=2.0, close=100.0)})
    eng.open_position(asset, "s", Direction.LONG, EffectiveRiskParams(
        leverage=2.0, risk_per_trade=0.01, notional=100.0, quantity=1.0,
        stop_price=98.0, take_profit_price=110.0, user_leverage=2,
        user_risk_per_trade=0.01, safety_leverage_cap=5, safety_risk_cap=0.03,
        approved=True))

    class Stub:
        pass
    bot = Stub()
    bot.executor, bot.fb = eng, fb
    bot._coin_cooldown = {}
    bot.reconciler = Reconciler(fetch=lambda: _ex(), snapshot=lambda: ({}, None))
    bot.reconciler.findings = [Finding(GHOST, DROP_LOCAL, "BTCUSDT", {}, True)]

    blocked = TradingBot._apply_reconciliation(bot)
    assert blocked is True
    assert "BTCUSDT" not in eng.open_positions
    assert bot._coin_cooldown.get("BTCUSDT", 0) > 0, "la coin deve andare in quarantena"


def test_no_findings_means_no_block_and_no_action():
    from bot.main import TradingBot

    class Stub:
        pass
    bot = Stub()
    bot.reconciler = Reconciler(fetch=lambda: _ex(), snapshot=lambda: ({}, None))
    bot.reconciler.findings = []
    assert TradingBot._apply_reconciliation(bot) is False
