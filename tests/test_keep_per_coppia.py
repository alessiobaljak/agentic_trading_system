"""IL KEEP DEL PROFIT-LOCK LO SCEGLIE IL GATE, PER COPPIA (25 set 2026).

Fino a oggi il `keep` (quanta parte del miglior guadagno si blocca quando il
profit-lock e' armato) era UNO per tutte le coppie (PROFIT_LOCK_KEEP=0,5), con un
adattamento dal paper per strategia che non e' mai scattato: servono 8 verdetti per
strategia, in 10 giorni ne sono usciti 14 su 21 strategie (backlog I3). E se fosse
scattato, il gate avrebbe continuato a simulare 0,5: paper e gate divergenti.

Il proprietario ha chiesto che «ogni dato raccolto arrivi al cervello e produca una
decisione». Il keep diventa quindi un PARAMETRO PER COPPIA come la scala dei TP
(`scale_r_mults`) e il break-even (`sl_to_breakeven`): il gate lo prova, lo scrive in
`last_params["profit_lock_keep"]`, e motore e bot leggono lo stesso numero.

Questi test difendono tre cose:
  * il contratto: `lock_keep(params)` legge la chiave, valida il range, e su
    assente/sbagliato torna None (= comportamento di prima);
  * il motore usa il keep dei params in ENTRAMBI i percorsi (TP unico e scale-out):
    e' cio' che permette al gate di simulare un keep diverso per coppia;
  * il bot: precedenza gate > imparato per strategia > globale, e il campo
    sopravvive al riavvio (Firebase) — un documento vecchio senza la chiave vale None.
"""
import datetime as dt
import inspect
import math

import pytest

from backtesting.engine import Backtester
from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Candle, Direction, EffectiveRiskParams, ExitReason, IndicatorSnapshot,
    Regime, StrategySignal,
)
from bot.execution.executor import ExecutionEngine
from bot.execution.exit_logic import (
    LOCK_KEEP_CANDIDATES, LOCK_KEEP_MAX, LOCK_KEEP_MIN, lock_keep, locked_stop,
)


# --------------------------------------------------------------------------- #
# 1) il contratto: lock_keep                                                   #
# --------------------------------------------------------------------------- #
def test_lock_keep_assente_vale_none():
    assert lock_keep(None) is None
    assert lock_keep({}) is None
    assert lock_keep({"scale_r_mults": [1, 2, 3]}) is None
    assert lock_keep({"profit_lock_keep": None}) is None


def test_lock_keep_valido_torna_il_numero():
    assert lock_keep({"profit_lock_keep": 0.65}) == pytest.approx(0.65)
    assert lock_keep({"profit_lock_keep": 0.35}) == pytest.approx(0.35)
    # i tre candidati che il gate prova stanno tutti nel range accettato
    for k in LOCK_KEEP_CANDIDATES:
        assert lock_keep({"profit_lock_keep": k}) == pytest.approx(k)
    assert LOCK_KEEP_MIN <= min(LOCK_KEEP_CANDIDATES) and max(LOCK_KEEP_CANDIDATES) <= LOCK_KEEP_MAX


def test_lock_keep_fuori_range_vale_none():
    """Un keep di 0,05 lascerebbe correre tutto, uno di 0,95 chiuderebbe al primo
    respiro: nessuno dei due e' un valore validato, meglio il default."""
    assert lock_keep({"profit_lock_keep": 0.1}) is None
    assert lock_keep({"profit_lock_keep": 0.9}) is None
    assert lock_keep({"profit_lock_keep": 0.0}) is None
    assert lock_keep({"profit_lock_keep": -0.5}) is None
    assert lock_keep({"profit_lock_keep": math.nan}) is None
    # i bordi sono inclusi
    assert lock_keep({"profit_lock_keep": LOCK_KEEP_MIN}) == pytest.approx(LOCK_KEEP_MIN)
    assert lock_keep({"profit_lock_keep": LOCK_KEEP_MAX}) == pytest.approx(LOCK_KEEP_MAX)


def test_lock_keep_non_numerico_vale_none():
    assert lock_keep({"profit_lock_keep": "alto"}) is None
    assert lock_keep({"profit_lock_keep": [0.5]}) is None
    assert lock_keep({"profit_lock_keep": {"v": 0.5}}) is None
    assert lock_keep({"profit_lock_keep": True}) is None     # bool non e' un keep
    # una stringa NUMERICA (registro passato da JSON) e' accettata, come per la scala
    assert lock_keep({"profit_lock_keep": "0.65"}) == pytest.approx(0.65)


# --------------------------------------------------------------------------- #
# 2) la parte pura: locked_stop con keep diversi                               #
# --------------------------------------------------------------------------- #
@pytest.fixture
def lock_on(monkeypatch):
    monkeypatch.setattr(settings, "PROFIT_LOCK_ENABLED", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_TRIGGER", 0.5)
    monkeypatch.setattr(settings, "PROFIT_LOCK_KEEP", 0.5)


def test_locked_stop_cambia_con_il_keep(lock_on):
    """Entry 100, TP 104, miglior prezzo 103 (armato: 3 >= 0,5 x 4). Il keep decide
    QUANTO del guadagno di 3 si blocca."""
    assert locked_stop(100.0, 104.0, True, 103.0, 98.0, keep=0.35) == pytest.approx(101.05)
    assert locked_stop(100.0, 104.0, True, 103.0, 98.0, keep=0.5) == pytest.approx(101.5)
    assert locked_stop(100.0, 104.0, True, 103.0, 98.0, keep=0.65) == pytest.approx(101.95)
    # None -> il default globale (0,5): e' il comportamento di prima
    assert locked_stop(100.0, 104.0, True, 103.0, 98.0, keep=None) == pytest.approx(101.5)
    # short: simmetrico
    assert locked_stop(100.0, 96.0, False, 97.0, 102.0, keep=0.65) == pytest.approx(98.05)


# --------------------------------------------------------------------------- #
# 3) il motore usa il keep dei params della strategia                          #
# --------------------------------------------------------------------------- #
class _AlwaysLong:
    """LONG a ogni barra, stop a -2% e target a +4% dal prezzo dello snapshot.
    `params` e' cio' che il gate scrive nel registro: qui lo fissiamo a mano."""
    name = "always_long"

    def __init__(self, params=None):
        self.params = dict(params or {})

    def is_active_in(self, regime) -> bool:
        return True

    def generate_signal(self, asset, ctx=None):
        p = asset.price
        return StrategySignal(
            strategy=self.name, symbol=asset.symbol, direction=Direction.LONG,
            confidence=60.0, reasoning="test",
            suggested_stop=p * 0.98, suggested_target=p * 1.04,
        )


def _serie_keep(n_warmup: int = 201, n_tail: int = 120) -> list[Candle]:
    """Serie costruita APPOSTA perche' il keep decida l'esito del primo trade.

    Riscaldamento a ~100 senza salti fra chiusura e apertura (cosi' il timing
    d'ingresso non conta): 201 barre, perche' il motore parte da `i = window` (200)
    e la barra del segnale, che chiude a 100, deve essere proprio quella.
    Poi, con ingresso a 100 (stop 98, target 104):
      * barra +1: massimo 103 -> guadagno 3 >= 0,5 x 4: il lock si ARMA (vale dalla
        barra dopo, come nel bot: il miglior prezzo entra a fine barra);
      * barra +2: minimo 101,2 -> sotto lo stop bloccato con keep 0,65 (101,95) e
        con 0,5 (101,5), ma SOPRA quello con keep 0,35 (101,05);
      * barra +3: massimo 104,5 -> chi e' ancora dentro prende il target.
    Poi piatta, per lasciare all'orizzonte il tempo di chiudersi."""
    t0 = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    out: list[Candle] = []
    close = 100.0
    for k in range(n_warmup):
        op = close
        # respiro minimo attorno a 100, senza deriva: il segnale c'e' comunque
        close = 100.0 + (0.2 if k % 2 == 0 else -0.2)
        hi, lo = max(op, close) + 0.1, min(op, close) - 0.1
        out.append(Candle(open_time=t0 + dt.timedelta(minutes=15 * k),
                          open=op, high=hi, low=lo, close=close, volume=1_000_000.0))
    # la barra del segnale chiude ESATTAMENTE a 100
    out[-1] = Candle(open_time=out[-1].open_time, open=out[-1].open, high=100.3, low=99.7,
                     close=100.0, volume=1_000_000.0)
    scripted = [
        # (open, high, low, close)
        (100.0, 103.0, 99.6, 102.5),
        (102.5, 102.6, 101.2, 101.5),
        (101.5, 104.5, 101.4, 104.2),
    ]
    k = n_warmup
    for op, hi, lo, cl in scripted:
        out.append(Candle(open_time=t0 + dt.timedelta(minutes=15 * k),
                          open=op, high=hi, low=lo, close=cl, volume=1_000_000.0))
        k += 1
    for _ in range(n_tail):
        out.append(Candle(open_time=t0 + dt.timedelta(minutes=15 * k),
                          open=104.2, high=104.3, low=104.1, close=104.2, volume=1_000_000.0))
        k += 1
    return out


def _primo_trade(params, monkeypatch, scale_out: bool):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", scale_out)
    monkeypatch.setattr(settings, "BACKTEST_ENTRY_NEXT_OPEN", False)
    monkeypatch.setattr(settings, "MAX_STOP_PCT", 0.06)
    bt = Backtester(window=200, capital=10_000.0, interval_hours=0.25)
    stats = bt.run_strategy(_AlwaysLong(params), "TESTUSDT", _serie_keep())
    assert stats.trades, "la serie deve produrre almeno un trade"
    t = stats.trades[0]
    assert t.entry_price == pytest.approx(100.0)
    return t


def test_motore_tp_unico_il_keep_dei_params_decide_l_uscita(lock_on, monkeypatch):
    """Stessa serie, tre keep: tre uscite diverse. Il gate puo' finalmente simulare
    un keep per coppia invece di dare per scontato 0,5."""
    alto = _primo_trade({"profit_lock_keep": 0.65}, monkeypatch, scale_out=False)
    basso = _primo_trade({"profit_lock_keep": 0.35}, monkeypatch, scale_out=False)
    # keep 0,65: stop bloccato a 100 + 0,65 x 3 = 101,95, toccato dal minimo 101,2
    assert alto.exit_price == pytest.approx(101.95)
    assert alto.trailing_verdict is not None      # uscita trailing: ha un verdetto
    # keep 0,35: stop bloccato a 101,05, NON toccato -> si arriva al target 104
    assert basso.exit_price == pytest.approx(104.0)
    assert basso.pnl_pct > alto.pnl_pct


def test_motore_senza_params_usa_il_default_globale(lock_on, monkeypatch):
    """Coppia non ancora rivalutata dal gate: si comporta ESATTAMENTE come prima
    (keep 0,5 -> stop bloccato a 101,5, toccato dal minimo 101,2)."""
    prima = _primo_trade({}, monkeypatch, scale_out=False)
    assert prima.exit_price == pytest.approx(101.5)
    # ... e un valore fuori range vale come assente, non come un keep strano
    strano = _primo_trade({"profit_lock_keep": 5.0}, monkeypatch, scale_out=False)
    assert strano.exit_price == pytest.approx(101.5)


def test_motore_scale_out_usa_lo_stesso_keep(lock_on, monkeypatch):
    """Anche nel percorso scale-out (quello in produzione) il keep dei params
    conta: con scala 2/4/6 (R = 2 -> primo gradino 104) il lock si ancora a 104 e
    si arma a +2; il massimo 103 lo arma senza riempire nulla."""
    base = {"scale_r_mults": [2.0, 4.0, 6.0], "sl_to_breakeven": False}
    alto = _primo_trade({**base, "profit_lock_keep": 0.65}, monkeypatch, scale_out=True)
    basso = _primo_trade({**base, "profit_lock_keep": 0.35}, monkeypatch, scale_out=True)
    # 0,65: stop bloccato a 101,95, toccato -> tutto il residuo esce li'
    assert alto.exit_price == pytest.approx(101.95)
    assert alto.trailing_verdict is not None
    # 0,35: non toccato -> la barra dopo riempie il primo gradino a 104
    assert basso.exit_price != pytest.approx(101.95)
    assert basso.pnl_pct > alto.pnl_pct


def test_motore_passa_il_keep_a_entrambe_le_chiamate():
    """Due chiamate a `locked_stop` nel motore (scale-out e TP unico): tutte e due
    devono portare il keep, altrimenti un percorso simula una cosa e l'altro
    un'altra."""
    src = inspect.getsource(Backtester.run_strategy)
    chiamate = [ln for ln in src.splitlines() if "locked_stop(" in ln]
    assert len(chiamate) == 2
    assert all("keep=keep" in ln for ln in chiamate)
    assert 'keep = lock_keep(getattr(strategy, "params", None))' in src


# --------------------------------------------------------------------------- #
# 4) il bot: precedenza gate > imparato > globale, e persistenza               #
# --------------------------------------------------------------------------- #
def _asset(price=100.0):
    return AssetSnapshot(
        symbol="BTCUSDT", price=price, regime=Regime.BULL_TRENDING,
        indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=2.0, close=price)},
    )


def _params(qty=10.0, stop=98.0, tp=110.0):
    return EffectiveRiskParams(
        leverage=3.0, risk_per_trade=0.01, notional=100.0, quantity=qty,
        stop_price=stop, take_profit_price=tp,
        user_leverage=3, user_risk_per_trade=0.01,
        safety_leverage_cap=5, safety_risk_cap=0.03, approved=True,
    )


@pytest.fixture
def tp_unico(lock_on, monkeypatch):
    """Percorso classico (TP unico) per isolare il keep: entry 100, TP 110, il lock
    si arma con un guadagno >= 5. A 106 il guadagno e' 6: stop bloccato a
    100 + keep x 6, cioe' 102,1 (0,35), 103 (0,5), 103,9 (0,65)."""
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", False)


def _arma(eng: ExecutionEngine) -> None:
    assert eng.update_position("BTCUSDT", 106.0) is None
    assert eng.open_positions["BTCUSDT"].high_water == 106.0


def test_bot_il_keep_del_gate_batte_quello_imparato(tp_unico):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.trailing_keep = {"trend_following": 0.35}          # imparato dal paper
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(),
                      profit_lock_keep=0.65)               # scelto dal gate
    assert eng.open_positions["BTCUSDT"].profit_lock_keep == pytest.approx(0.65)
    _arma(eng)
    # 103,5: sotto 103,9 (gate 0,65), ma sopra 102,1 (imparato 0,35) e 103 (globale)
    closed = eng.update_position("BTCUSDT", 103.5)
    assert closed is not None and closed.exit_reason == ExitReason.TRAILING_STOP
    assert closed.exit_price == pytest.approx(103.9)
    # il trade chiuso registra il keep che l'ha governato: un verdetto «prematuro»
    # si legge solo insieme a questo numero
    assert closed.profit_lock_keep == pytest.approx(0.65)


def test_bot_senza_scelta_del_gate_vale_quello_imparato(tp_unico):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.trailing_keep = {"trend_following": 0.35}
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params())
    assert eng.open_positions["BTCUSDT"].profit_lock_keep is None
    _arma(eng)
    # 102,5: sopra 102,1 (imparato 0,35) -> resta aperta; col globale 0,5 (103)
    # sarebbe gia' uscita
    assert eng.update_position("BTCUSDT", 102.5) is None
    closed = eng.update_position("BTCUSDT", 102.0)
    assert closed is not None and closed.exit_reason == ExitReason.TRAILING_STOP
    assert closed.exit_price == pytest.approx(102.1)
    assert closed.profit_lock_keep == pytest.approx(0.35)     # quello imparato


def test_bot_senza_nulla_vale_il_default_globale(tp_unico):
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    assert eng.trailing_keep == {}
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params())
    _arma(eng)
    closed = eng.update_position("BTCUSDT", 102.5)     # sotto 103 (globale 0,5)
    assert closed is not None and closed.exit_reason == ExitReason.TRAILING_STOP
    assert closed.exit_price == pytest.approx(103.0)
    assert closed.profit_lock_keep == pytest.approx(0.5)      # il globale, esplicito


def test_bot_il_keep_del_gate_sopravvive_al_riavvio(tp_unico):
    """Stesso store Firebase = riavvio del processo. Il keep congelato all'ingresso
    deve tornare identico, altrimenti dopo un restart il trade cambierebbe piano."""
    fb = FirebaseClient()
    eng1 = ExecutionEngine(firebase=fb, dry_run=True)
    eng1.trailing_keep = {"trend_following": 0.35}
    eng1.open_position(_asset(100), "trend_following", Direction.LONG, _params(),
                       profit_lock_keep=0.65)
    _arma(eng1)
    state = fb.get_rtdb("/positions/BTCUSDT")
    assert state["profit_lock_keep"] == pytest.approx(0.65)
    assert eng1._position_from_state(state).profit_lock_keep == pytest.approx(0.65)

    eng2 = ExecutionEngine(firebase=fb, dry_run=True)
    eng2.trailing_keep = {"trend_following": 0.35}
    pos = eng2.open_positions["BTCUSDT"]
    assert pos.profit_lock_keep == pytest.approx(0.65)
    assert pos.high_water == 106.0
    # ... e si comporta col keep del gate, non con quello imparato
    closed = eng2.update_position("BTCUSDT", 103.5)
    assert closed is not None and closed.exit_price == pytest.approx(103.9)


def test_bot_un_documento_vecchio_senza_la_chiave_vale_none(tp_unico):
    fb = FirebaseClient()
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params())
    state = dict(fb.get_rtdb("/positions/BTCUSDT"))
    state.pop("profit_lock_keep", None)          # scritto prima del 25 set 2026
    restored = eng._position_from_state(state)
    assert restored.profit_lock_keep is None
    # e da un documento con la chiave a null (Firebase toglie i null) idem
    state["profit_lock_keep"] = None
    assert eng._position_from_state(state).profit_lock_keep is None


# --------------------------------------------------------------------------- #
# 5) main passa il parametro dal registro all'executor                          #
# --------------------------------------------------------------------------- #
def test_main_passa_il_keep_del_registro_all_apertura():
    from bot import main as bot_main

    src = inspect.getsource(bot_main)
    assert "profit_lock_keep=lock_keep(_sparams)" in src
    assert "lock_keep" in inspect.getsource(bot_main).split("class TradingBot")[0], \
        "lock_keep va importato da exit_logic"


def test_bot_il_rischio_effettivo_sopravvive_al_riavvio(tp_unico):
    """25 set 2026 (ops 0245): dopo un riavvio le posizioni ricaricate tornavano a
    rischio 0.0 e la prima scrittura dello stato lo cancellava anche su RTDB; il
    primo controllo orario mostrava «4 posizioni, 0,0% a rischio»."""
    fb = FirebaseClient()
    eng1 = ExecutionEngine(firebase=fb, dry_run=True)
    eng1.open_position(_asset(100), "trend_following", Direction.LONG, _params())
    eng1.open_positions["BTCUSDT"].risk_effective_pct = 0.0042
    eng1._write_position_state(eng1.open_positions["BTCUSDT"], 100.0)
    eng2 = ExecutionEngine(firebase=fb, dry_run=True)      # ricarica da Firebase nel costruttore
    assert eng2.open_positions["BTCUSDT"].risk_effective_pct == pytest.approx(0.0042)
    # documento vecchio senza la chiave -> 0.0, non un'eccezione
    p = dict(fb.get_rtdb("/positions/BTCUSDT") or {})
    p.pop("risk_effective_pct", None)
    assert eng2._position_from_state(p).risk_effective_pct == 0.0


def test_il_trade_chiuso_ricorda_stop_originale_scala_e_regola(tp_unico):
    """25 set 2026, domanda del proprietario: «per ogni trade chiuso il sistema
    memorizza TP e SL configurati e le condizioni d'ingresso?». Lo stop salvato
    era quello finale (spostato dal trailing) e la scala non c'era."""
    fb = FirebaseClient()
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    eng.open_position(_asset(100), "trend_following", Direction.LONG, _params(),
                      scale_r_mults=(1.5, 3.0, 5.0), sl_to_breakeven=False,
                      feats_at_entry={"rsi": 27.0, "adx": 31.0}, regola="[gen] rsi<30 e adx>25")
    pos = eng.open_positions["BTCUSDT"]
    assert pos.feats_at_entry == {"rsi": 27.0, "adx": 31.0} and pos.regola.startswith("[gen]")
    # sopravvive al riavvio
    eng2 = ExecutionEngine(firebase=fb, dry_run=True)
    assert eng2.open_positions["BTCUSDT"].feats_at_entry == {"rsi": 27.0, "adx": 31.0}
    assert eng2.open_positions["BTCUSDT"].regola == "[gen] rsi<30 e adx>25"
    _arma(eng2)
    closed = eng2.update_position("BTCUSDT", 102.5)
    assert closed is not None
    assert closed.orig_stop == pytest.approx(98.0)          # l'originale, non quello spostato
    assert closed.exit_price > closed.orig_stop              # uscita col lock, non allo stop
    assert closed.scale_r_mults == [1.5, 3.0, 5.0] and closed.sl_to_breakeven is False
    assert closed.feats_at_entry == {"rsi": 27.0, "adx": 31.0}
    assert closed.regola == "[gen] rsi<30 e adx>25"
    if closed.tp_prices is not None:                         # scale-out acceso
        assert closed.tp_prices[0] == pytest.approx(103.0)   # 100 + 1.5 * 2


def test_main_passa_variabili_e_regola_alla_posizione():
    import inspect
    from bot import main as bot_main
    src = inspect.getsource(bot_main.TradingBot._try_open)
    assert "feats_at_entry=_feats" in src and 'regola=getattr(decision, "reasoning"' in src
    assert "variabili_ingresso(getattr(self, \"_btc_snap\", None), asset, params, _sparams" in src
