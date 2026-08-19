# 0009-test-dopo-revisione.req

_eseguito: 2026-08-19 19:37 UTC_

**richiesta:** `test`
**eseguito:** `.venv/bin/python -m pytest -q`
**esito:** codice 1 in 15.3s

```
........................................................................ [ 10%]
........................................................................ [ 21%]
................................................................F....FF. [ 31%]
........................................................................ [ 42%]
........................................................................ [ 53%]
........................................................................ [ 63%]
........................................................................ [ 74%]
.........................FF.F.F......................F.................. [ 84%]
........................................................................ [ 95%]
FFF............................                                          [100%]
=================================== FAILURES ===================================
__________________________ test_take_profit_full_exit __________________________

    def test_take_profit_full_exit():
        # allineato al backtest: al TP esce TUTTA la posizione (niente scale-out/trailing)
        eng = _engine()
        eng.open_position(_asset(100, atr=2.0), "breakout", Direction.LONG, _params(qty=2.0, stop=98, tp=104))
        closed = eng.update_position("BTCUSDT", 104.5)  # supera il TP
>       assert closed is not None
E       assert None is not None

tests/test_execution.py:67: AssertionError
----------------------------- Captured stdout call -----------------------------
[firebase] FIREBASE_SERVICE_ACCOUNT non impostato -> store IN-MEMORY
[DRY_RUN] OPEN long BTCUSDT qty=2.0000 @ 100.0 lev=3.0x SL=98.0000 TP=104.0000
[DRY_RUN] SCALE-OUT 0.6000 BTCUSDT @ 103.0 (netto +1.7040, residuo 1.4000)
__________________ test_profit_lock_protects_gains_on_retrace __________________

    def test_profit_lock_protects_gains_on_retrace():
        # la posizione va in profitto oltre il trigger (metà strada verso il TP) e poi
        # ritraccia: il profit-lock chiude IN PROFITTO (TRAILING_STOP), non la riporta in
        # perdita né aspetta che torni allo stop iniziale.
        eng = _engine()
        eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=10.0, stop=98, tp=110))
        # sale a 106: fav_move=6 >= trigger 0.5*10=5 -> il lock si armera'. Come nel motore
        # del gate, il miglior prezzo entra in high_water a FINE tick: lo stop bloccato e'
        # quindi in vigore dal tick DOPO (mai armato e fatto scattare dallo stesso range,
        # che e' un insieme non ordinato). Qui percio' trailing_active e' ancora False.
        assert eng.update_position("BTCUSDT", 106.0) is None
        assert eng.open_positions["BTCUSDT"].trailing_active is False
        assert eng.open_positions["BTCUSDT"].high_water == 106.0
        # ritraccia a 103: ORA lo stop bloccato (100+0.5*6=103) e' attivo -> esce in profitto
        closed = eng.update_position("BTCUSDT", 103.0)
        assert closed is not None
>       assert closed.exit_reason == ExitReason.TRAILING_STOP
E       AssertionError: assert <ExitReason.S...: 'scale_out'> == <ExitReason.T...railing_stop'>
E         
E         - trailing_stop
E         + scale_out

tests/test_execution.py:147: AssertionError
----------------------------- Captured stdout call -----------------------------
[firebase] FIREBASE_SERVICE_ACCOUNT non impostato -> store IN-MEMORY
[DRY_RUN] OPEN long BTCUSDT qty=10.0000 @ 100.0 lev=3.0x SL=98.0000 TP=110.0000
[DRY_RUN] SCALE-OUT 3.0000 BTCUSDT @ 103.0 (netto +8.5200, residuo 7.0000)
[DRY_RUN] SCALE-OUT 3.0000 BTCUSDT @ 106.0 (netto +17.5200, residuo 4.0000)
[DRY_RUN] CLOSE BTCUSDT @ 103.0 (scale_out)
___________________ test_profit_lock_not_armed_below_trigger ___________________

    def test_profit_lock_not_armed_below_trigger():
        # piccolo profitto sotto il trigger: lo stop resta quello iniziale (no arming).
        eng = _engine()
        eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(qty=10.0, stop=98, tp=110))
        assert eng.update_position("BTCUSDT", 103.0) is None         # fav 3 < trigger 5
        assert eng.open_positions["BTCUSDT"].trailing_active is False
        # ritraccia a 99 (sopra lo stop 98): resta aperta, non c'è ancora protezione
>       assert eng.update_position("BTCUSDT", 99.0) is None
E       AssertionError: assert ClosedTrade(trade_id='d13a7920-8a89-462a-a230-9ce698a1eb66', symbol='BTCUSDT', strategy='trend_following', direction=<...on_usdt=0.8, spread_usdt=0.8, funding_paid_usdt=0.0, total_cost_usdt=1.6, gross_pnl_usdt=9.0, costs_are_estimated=True) is None
E        +  where ClosedTrade(trade_id='d13a7920-8a89-462a-a230-9ce698a1eb66', symbol='BTCUSDT', strategy='trend_following', direction=<...on_usdt=0.8, spread_usdt=0.8, funding_paid_usdt=0.0, total_cost_usdt=1.6, gross_pnl_usdt=9.0, costs_are_estimated=True) = <bound method ExecutionEngine.update_position of <bot.execution.executor.ExecutionEngine object at 0x7c7ae443de50>>('BTCUSDT', 99.0)
E        +    where <bound method ExecutionEngine.update_position of <bot.execution.executor.ExecutionEngine object at 0x7c7ae443de50>> = <bot.execution.executor.ExecutionEngine object at 0x7c7ae443de50>.update_position

tests/test_execution.py:159: AssertionError
----------------------------- Captured stdout call -----------------------------
[firebase] FIREBASE_SERVICE_ACCOUNT non impostato -> store IN-MEMORY
[DRY_RUN] OPEN long BTCUSDT qty=10.0000 @ 100.0 lev=3.0x SL=98.0000 TP=110.0000
[DRY_RUN] SCALE-OUT 3.0000 BTCUSDT @ 103.0 (netto +8.5200, residuo 7.0000)
[DRY_RUN] CLOSE BTCUSDT @ 100.0 (scale_out)
_______________________ test_size_multiplier_scales_risk _______________________

    def test_size_multiplier_scales_risk():
        rm = RiskManager()
        user = RiskSettings(leverage=3.0, risk_per_trade=0.02)
        full = rm.evaluate(_decision(1.0), user, _asset(), 10_000)
        half = rm.evaluate(_decision(0.5), user, _asset(), 10_000)
>       assert half.quantity == pytest.approx(full.quantity / 2, rel=1e-6)
E       assert 30.0 == 15.0 ± 1.5e-05
E         
E         comparison failed
E         Obtained: 30.0
E         Expected: 15.0 ± 1.5e-05

tests/test_risk.py:72: AssertionError
____________________ test_circuit_breaker_daily_loss_halts _____________________

    def test_circuit_breaker_daily_loss_halts():
        cb = CircuitBreakers()
        cb.register_trade_result(-0.06, was_stop_loss=True)  # -6% del capitale > 5% limite
        rm = RiskManager(circuit_breakers=cb)
        params = rm.evaluate(_decision(), RiskSettings(), _asset(), 10_000)
>       assert params.approved is False
E       AssertionError: assert True is False
E        +  where True = EffectiveRiskParams(leverage=2.0, risk_per_trade=0.01, risk_effective_pct=0.006, capped_by_position_limit=True, notion... limitato dal cap posizione (10% equity): rischio effettivo 0.60% invece di 1.00%'], approved=True, reject_reason=None).approved

tests/test_risk.py:80: AssertionError
__________________ test_circuit_breaker_consecutive_sl_pause ___________________

    def test_circuit_breaker_consecutive_sl_pause():
        from bot.risk import hard_limits
        cb = CircuitBreakers()
        for _ in range(hard_limits.CONSECUTIVE_SL_LIMIT):
            cb.register_trade_result(-0.005, was_stop_loss=True)
>       assert cb.can_trade() is False
E       assert True is False
E        +  where True = <bound method CircuitBreakers.can_trade of <bot.risk.circuit_breakers.CircuitBreakers object at 0x7c7ae4366660>>()
E        +    where <bound method CircuitBreakers.can_trade of <bot.risk.circuit_breakers.CircuitBreakers object at 0x7c7ae4366660>> = <bot.risk.circuit_breakers.CircuitBreakers object at 0x7c7ae4366660>.can_trade

tests/test_risk.py:99: AssertionError
____________ test_uses_strategy_suggested_stop_target_over_defaults ____________

    def test_uses_strategy_suggested_stop_target_over_defaults():
        """PARITA' GATE 1: se la decisione porta suggested_stop/target (dagli stessi
        atr_mult_stop/rr validati out-of-sample), il risk manager li usa TALI E QUALI
        invece di ricalcolarli coi default fissi 1.5ATR/2RR."""
        rm = RiskManager()
        user = RiskSettings(leverage=3.0, risk_per_trade=0.02)
        dec = OrchestratorDecision(
            asset="BTCUSDT", strategy="gen_x", direction=Direction.LONG,
            size_multiplier=1.0, confidence=80,
            suggested_stop=95.0, suggested_target=110.0,
        )
        params = rm.evaluate(dec, user, _asset(price=100.0, atr=2.0), 10_000)
        # NON i default (100-1.5*2=97 / 100+3=103): esattamente quelli della strategia
        assert params.stop_price == pytest.approx(95.0)
        assert params.take_profit_price == pytest.approx(110.0)
        # e il sizing deriva dalla distanza dello stop della strategia (5.0/unit)
>       assert params.quantity == pytest.approx((10_000 * params.risk_per_trade) / 5.0, rel=1e-6)
E       assert 30.0 == 40.0 ± 4.0e-05
E         
E         comparison failed
E         Obtained: 30.0
E         Expected: 40.0 ± 4.0e-05

tests/test_risk.py:134: AssertionError
______ test_effective_risk_matches_the_request_when_the_cap_does_not_bite ______

monkeypatch = <_pytest.monkeypatch.MonkeyPatch object at 0x7c7ae44c6ab0>

    def test_effective_risk_matches_the_request_when_the_cap_does_not_bite(monkeypatch):
        # cap largo: la size la decide il rischio, come da progetto
        p = _compute(monkeypatch, frac=1.0)
>       assert p.capped_by_position_limit is False
E       AssertionError: assert True is False
E        +  where True = EffectiveRiskParams(leverage=2.0, risk_per_trade=0.01, risk_effective_pct=0.004, capped_by_position_limit=True, notion... limitato dal cap posizione (10% equity): rischio effettivo 0.40% invece di 1.00%'], approved=True, reject_reason=None).capped_by_position_limit

tests/test_sizing.py:68: AssertionError
_____________ test_wick_does_not_arm_profit_lock_within_same_tick ______________

    def test_wick_does_not_arm_profit_lock_within_same_tick():
        """CRITICO. Range 99..106 su entry 100 / TP 110: l'ombra alta (106) armerebbe il
        lock a 103 e l'ombra bassa (99) lo farebbe subito scattare -> uscita "in profitto"
        inventata, perche' non sappiamo quale delle due sia venuta prima. Il lock deve
        armarsi solo dal tick SUCCESSIVO (come best_fav a fine barra nel gate)."""
        eng = _open(tp=110.0)
        assert eng.update_position("BTCUSDT", 100.5, high=106.0, low=99.0) is None
        pos = eng.open_positions["BTCUSDT"]
        assert pos.high_water == 106.0        # l'ombra e' registrata per i tick futuri
        # tick successivo: ORA il lock e' armato (0.5*6=3 -> stop a 103) e scatta
        closed = eng.update_position("BTCUSDT", 102.0, high=102.5, low=101.0)
        assert closed is not None
>       assert closed.exit_reason == ExitReason.TRAILING_STOP
E       AssertionError: assert <ExitReason.S...: 'scale_out'> == <ExitReason.T...railing_stop'>
E         
E         - trailing_stop
E         + scale_out

tests/test_wick_parity.py:119: AssertionError
----------------------------- Captured stdout call -----------------------------
[firebase] FIREBASE_SERVICE_ACCOUNT non impostato -> store IN-MEMORY
[DRY_RUN] OPEN long BTCUSDT qty=1.0000 @ 100.0 lev=3.0x SL=98.0000 TP=110.0000
[DRY_RUN] SCALE-OUT 0.3000 BTCUSDT @ 103.0 (netto +0.8724, residuo 0.7000)
[DRY_RUN] SCALE-OUT 0.3000 BTCUSDT @ 106.0 (netto +1.7724, residuo 0.4000)
[DRY_RUN] CLOSE BTCUSDT @ 103.0 (scale_out)
_____________ test_range_is_widened_to_mark_so_no_trigger_is_lost ______________

    def test_range_is_widened_to_mark_so_no_trigger_is_lost():
        """Se high/low arrivassero stantii/incoerenti, il mark osservato resta sovrano:
        tutto cio' che scattava prima continua a scattare."""
        eng = _open(tp=104.0)
        closed = eng.update_position("BTCUSDT", 104.5, high=101.0, low=100.0)
>       assert closed is not None
E       assert None is not None

tests/test_wick_parity.py:129: AssertionError
----------------------------- Captured stdout call -----------------------------
[firebase] FIREBASE_SERVICE_ACCOUNT non impostato -> store IN-MEMORY
[DRY_RUN] OPEN long BTCUSDT qty=1.0000 @ 100.0 lev=3.0x SL=98.0000 TP=104.0000
[DRY_RUN] SCALE-OUT 0.3000 BTCUSDT @ 103.0 (netto +0.8724, residuo 0.7000)
__________________ test_without_hi_lo_behaviour_is_unchanged ___________________

    def test_without_hi_lo_behaviour_is_unchanged():
        """Omessi high/low -> vecchio comportamento su solo mark (retrocompatibilita')."""
        eng = _open(tp=104.0)
        assert eng.update_position("BTCUSDT", 103.0) is None      # sotto il TP: niente
        closed = eng.update_position("BTCUSDT", 104.0)
>       assert closed is not None
E       assert None is not None

tests/test_wick_parity.py:138: AssertionError
----------------------------- Captured stdout call -----------------------------
[firebase] FIREBASE_SERVICE_ACCOUNT non impostato -> store IN-MEMORY
[DRY_RUN] OPEN long BTCUSDT qty=1.0000 @ 100.0 lev=3.0x SL=98.0000 TP=104.0000
[DRY_RUN] SCALE-OUT 0.3000 BTCUSDT @ 103.0 (netto +0.8724, residuo 0.7000)
=========================== short test summary info ============================
FAILED tests/test_execution.py::test_take_profit_full_exit - assert None is n...
FAILED tests/test_execution.py::test_profit_lock_protects_gains_on_retrace - ...
FAILED tests/test_execution.py::test_profit_lock_not_armed_below_trigger - As...
FAILED tests/test_risk.py::test_size_multiplier_scales_risk - assert 30.0 == ...
FAILED tests/test_risk.py::test_circuit_breaker_daily_loss_halts - AssertionE...
FAILED tests/test_risk.py::test_circuit_breaker_consecutive_sl_pause - assert...
FAILED tests/test_risk.py::test_uses_strategy_suggested_stop_target_over_defaults
FAILED tests/test_sizing.py::test_effective_risk_matches_the_request_when_the_cap_does_not_bite
FAILED tests/test_wick_parity.py::test_wick_does_not_arm_profit_lock_within_same_tick
FAILED tests/test_wick_parity.py::test_range_is_widened_to_mark_so_no_trigger_is_lost
FAILED tests/test_wick_parity.py::test_without_hi_lo_behaviour_is_unchanged
11 failed, 668 passed in 14.52s
```
