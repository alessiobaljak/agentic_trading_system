"""FASE 5 — COSA SUCCEDE QUANDO SI ROMPE QUALCOSA.

Tre guasti che sulla VPS capiteranno, non "se" ma "quando": il WebSocket cade,
Binance rallenta, Firebase smette di rispondere. Il resto della suite verifica che
il sistema faccia la cosa giusta quando tutto funziona; qui si verifica che faccia
la cosa MENO PEGGIO quando non funziona.

Il criterio, uguale per tutti e tre: **una posizione aperta non resta mai senza
sorveglianza**. Un guasto puo' costare uno scan incompleto, una dashboard vecchia,
un'occasione persa. Non puo' costare uno stop che non scatta, perche' quello e'
l'unico errore che si paga in denaro e non si recupera.

Da cui la regola che ricorre nei tre scenari: in degrado si CONTINUA A GESTIRE cio'
che e' aperto e si SMETTE DI APRIRE. La gestione delle posizioni non ha bisogno del
componente rotto (i prezzi arrivano da Binance, lo stato vive in memoria); aprire
invece aggiunge rischio proprio mentre uno dei controlli e' cieco.
"""
from datetime import datetime, timedelta, timezone

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Candle, Direction, EffectiveRiskParams, ExitReason,
    IndicatorSnapshot, Regime,
)
from bot.execution.executor import ExecutionEngine
from bot.main import TradingBot


# --------------------------------------------------------------------------- #
# impalcatura comune                                                          #
# --------------------------------------------------------------------------- #
def _asset(price=100.0, atr=2.0):
    return AssetSnapshot(
        symbol="BTCUSDT", price=price, regime=Regime.BULL_TRENDING, volume_24h=5e8,
        indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=atr, close=price)},
    )


def _params(stop=98.0, tp=104.0):
    return EffectiveRiskParams(
        leverage=3.0, risk_per_trade=0.01, notional=100.0, quantity=1.0,
        stop_price=stop, take_profit_price=tp,
        user_leverage=3, user_risk_per_trade=0.01,
        safety_leverage_cap=5, safety_risk_cap=0.03, approved=True,
    )


def _engine_with_position():
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    eng.open_position(_asset(100.0), "trend_following", Direction.LONG, _params())
    eng.open_positions["BTCUSDT"].entry_time = datetime.now(timezone.utc)
    return eng


def _candle(minutes_from_now: int, high: float, low: float) -> Candle:
    t = datetime.now(timezone.utc) + timedelta(minutes=minutes_from_now)
    return Candle(open_time=t, open=(high + low) / 2, high=high, low=low,
                  close=(high + low) / 2, volume=1000.0,
                  close_time=t + timedelta(minutes=1))


class _StubPrice:
    """Agente prezzi finto. `candles=None` = il REST fallisce anche lui."""

    def __init__(self, candles=None, fail=False):
        self._candles = candles or []
        self.fail = fail

    def get_candles(self, symbol, interval, limit=200):
        if self.fail:
            raise ConnectionError("binance irraggiungibile")
        return self._candles[-limit:]


class _DeadStream:
    """WebSocket caduto: risponde a tutto, ma dichiara di non essere sano."""

    def __init__(self):
        self.take_calls = 0
        self.range_calls = 0

    def is_healthy(self):
        return False

    def take(self, symbol):
        self.take_calls += 1
        return [], None, None, False

    def take_range(self, symbol):
        self.range_calls += 1
        return (None, None)


class _FakeBot:
    """Il minimo per esercitare i metodi di TradingBot senza costruire il bot."""

    def __init__(self, price=None, stream=None, fb=None):
        self.price = price
        self.stream = stream
        self.fb = fb
        self._last_path_range = (None, None)

    _price_path = TradingBot._price_path
    _wick_range = TradingBot._wick_range
    _firebase_guard = TradingBot._firebase_guard


# =========================================================================== #
# 1. WEBSOCKET GIU' CON UNA POSIZIONE APERTA                                  #
# =========================================================================== #
# Lo stream serve a vedere l'ORDINE dei prezzi dentro il minuto. Se cade, quella
# precisione si perde — ma la sorveglianza no: si ricade sulle candele 1m via REST,
# che vedono gli estremi. Meno preciso, non cieco.

def test_dead_stream_gives_no_path_so_the_caller_falls_back():
    """Percorso vuoto = il chiamante usa il range aggregato. E' il bivio da cui
    dipende tutto il resto della degradazione."""
    bot = _FakeBot(stream=_DeadStream())
    assert bot._price_path("BTCUSDT", None) == []
    assert bot._last_path_range == (None, None)


def test_dead_stream_falls_back_to_rest_candles():
    eng = _engine_with_position()
    pos = eng.open_positions["BTCUSDT"]
    stream = _DeadStream()
    bot = _FakeBot(price=_StubPrice([_candle(+1, high=104.0, low=97.5)]), stream=stream)
    hi, lo = bot._wick_range("BTCUSDT", pos)
    assert (hi, lo) == (104.0, 97.5)
    # lo stream caduto non viene nemmeno interrogato: sarebbe una risposta inutile
    assert stream.range_calls == 0


def test_the_stop_still_fires_while_the_stream_is_down():
    """IL PUNTO DELL'INTERO SCENARIO. Stream morto, prezzo che sfonda lo stop: la
    posizione DEVE chiudersi lo stesso, sui dati REST. Un websocket caduto non puo'
    trasformarsi in uno stop non eseguito."""
    eng = _engine_with_position()
    pos = eng.open_positions["BTCUSDT"]
    bot = _FakeBot(price=_StubPrice([_candle(+1, high=100.5, low=97.0)]),
                   stream=_DeadStream())
    hi, lo = bot._wick_range("BTCUSDT", pos)
    closed = eng.update_position("BTCUSDT", 99.0, high=hi, low=lo)
    assert closed is not None
    assert closed.exit_reason is ExitReason.STOP_LOSS
    assert "BTCUSDT" not in eng.open_positions


def test_stream_down_and_rest_down_too_degrades_to_the_mark_price():
    """Doppio guasto: niente stream E niente candele. Si resta col solo mark price —
    la posizione e' gestita peggio, ma e' gestita, e nessuno solleva."""
    eng = _engine_with_position()
    pos = eng.open_positions["BTCUSDT"]
    bot = _FakeBot(price=_StubPrice(fail=True), stream=_DeadStream())
    assert bot._wick_range("BTCUSDT", pos) == (None, None)
    closed = eng.update_position("BTCUSDT", 97.0, high=None, low=None)
    assert closed is not None and closed.exit_reason is ExitReason.STOP_LOSS


def test_while_the_stream_is_down_the_bot_keeps_operating():
    """Durante il buco non ci si ferma: si lavora sulle candele REST. Fermarsi del
    tutto per un problema di rete e' peggio del problema."""
    from bot.agents.price_stream import PriceStream
    s = PriceStream()
    s._connected, s._down_since = False, 1000.0

    class Stub:
        pass
    b = Stub()
    b.stream, b._decision_interval_s, b._stream_recovered_at = s, 900, None
    assert TradingBot._stream_recovery_guard(b, 2000.0) is False


# =========================================================================== #
# 2. BINANCE LENTA (oltre 5 secondi a risposta)                               #
# =========================================================================== #
# Il pericolo qui non e' l'errore: e' l'ATTESA. Un sistema che aspetta all'infinito
# non da' segnali di guasto — sembra vivo e non fa niente. Ogni attesa va limitata,
# e ogni ciclo deve tornare a gestire le posizioni entro un tempo noto.

def test_every_rest_call_carries_a_timeout():
    """Senza timeout una socket appesa blocca il loop per sempre: nessuno gestisce
    piu' le posizioni e nemmeno l'heartbeat si aggiorna."""
    from bot.agents.price_agent import PriceAgent
    agent = PriceAgent()
    seen = {}

    class _Sess:
        def get(self, url, params=None, timeout=None):
            seen["timeout"] = timeout
            raise TimeoutError("troppo lenta")

    agent._session = _Sess()
    assert agent._get("/fapi/v1/klines", {}) is None      # degrada, non solleva
    assert seen["timeout"] == agent.timeout > 0


def test_a_slow_binance_is_retried_a_bounded_number_of_times():
    """504 = sovraccarico temporaneo: si riprova, ma un numero FINITO di volte e con
    attese crescenti. Insistere oltre significa solo farsi bandire."""
    from bot.execution.error_handler import Severity, call_with_retry, final_severity
    calls, waited = [], []

    def slow():
        calls.append(1)
        raise RuntimeError("APIError(code=504): gateway timeout")

    with pytest.raises(RuntimeError):
        call_with_retry(slow, attempts=3, base_delay=1.0, sleep=waited.append)
    assert len(calls) == 3
    assert waited == [1.0, 2.0]          # attese crescenti, e nessuna dopo l'ultimo
    # esauriti i tentativi NON e' piu' "riprovabile": rimetterlo in coda ripeterebbe
    # la stessa richiesta che l'exchange sta gia' rifiutando
    assert final_severity(RuntimeError("code=504"), 3) is Severity.STOP


def test_the_exchange_decides_how_long_to_wait_when_it_says_so():
    from bot.execution.error_handler import call_with_retry

    class _Resp:
        headers = {"Retry-After": "7"}

    class _Slow(RuntimeError):
        code = 429
        response = _Resp()

    waited = []
    with pytest.raises(_Slow):
        call_with_retry(lambda: (_ for _ in ()).throw(_Slow("rate limit")),
                        attempts=2, base_delay=1.0, sleep=waited.append)
    assert waited == [7.0]               # l'header vince sul backoff


def test_a_slow_error_while_placing_protection_is_always_critical():
    """Il caso peggiore: entry eseguita, e la protezione non parte perche' Binance
    e' lenta. Si resta con una posizione aperta e forse senza stop — e con la leva
    una posizione senza stop perde senza limite."""
    from bot.execution.error_handler import Severity, classify
    c = classify(RuntimeError("APIError(code=504)"), placing_protection=True)
    assert c.severity is Severity.CRITICAL


def test_the_scan_gives_up_instead_of_running_forever(monkeypatch):
    """Con Binance lenta uno scan da centoquaranta coin diventa di ore, e per tutto
    quel tempo il loop non torna alle posizioni aperte. Il budget lo impedisce: si
    tiene cio' che si e' raccolto e si va avanti."""
    import time as _time
    from bot.agents.market_scanner import MarketScanner

    class _SlowPrice:
        def build_snapshot(self, symbol):
            _time.sleep(0.03)            # una risposta lenta
            return _asset()

    monkeypatch.setattr(settings, "SCAN_MAX_SECONDS", 0.05)
    monkeypatch.setattr(settings, "SCAN_MIN_VOLUME_24H", 0.0)
    sc = MarketScanner(_SlowPrice(), sentiment_agent=object())
    syms = [f"C{i}USDT" for i in range(50)]
    t0 = _time.monotonic()
    res = sc.scan(symbols=syms)
    elapsed = _time.monotonic() - t0
    assert elapsed < 1.0                 # senza budget sarebbero stati ~1.5s
    assert 0 < len(res) < len(syms)      # parziale, non vuoto e non completo


def test_without_a_budget_nothing_changes(monkeypatch):
    """Il budget e' disattivabile (0) e allora lo scan e' quello di sempre: la
    degradazione non deve cambiare il comportamento normale."""
    from bot.agents.market_scanner import MarketScanner
    monkeypatch.setattr(settings, "SCAN_MAX_SECONDS", 0.0)
    monkeypatch.setattr(settings, "SCAN_MIN_VOLUME_24H", 0.0)

    class _Price:
        def build_snapshot(self, symbol):
            return _asset()

    sc = MarketScanner(_Price(), sentiment_agent=object())
    assert len(sc.scan(symbols=[f"C{i}USDT" for i in range(7)])) == 7


# =========================================================================== #
# 3. FIREBASE IRRAGGIUNGIBILE                                                 #
# =========================================================================== #
# Firebase non serve a GESTIRE le posizioni (vivono in memoria, si chiudono coi
# prezzi di Binance): serve a raccontarle. Ma stava sul percorso caldo del loop, e
# l'heartbeat sta in un `finally` — dove un'eccezione non e' intercettata da nessuno
# e termina il processo. Cioe': un buco di rete su Firebase spegneva il bot
# lasciando aperte le posizioni. Da qui la regola "il RTDB non solleva mai".

class _BrokenRef:
    def get(self):
        raise ConnectionError("firebase irraggiungibile")

    def set(self, value):
        raise ConnectionError("firebase irraggiungibile")

    def delete(self):
        raise ConnectionError("firebase irraggiungibile")


class _BrokenDb:
    def reference(self, path):
        return _BrokenRef()


def _broken_firebase() -> FirebaseClient:
    """Client CONFIGURATO (crede di essere vivo) ma con il database muto: e' il caso
    pericoloso, diverso da 'Firebase non configurato'."""
    fb = FirebaseClient()
    fb._live = True
    fb._db = _BrokenDb()
    return fb


def test_a_mute_rtdb_never_raises_on_write():
    fb = _broken_firebase()
    assert fb.set_rtdb("/account/equity", 1000.0) is False   # non durevole, dichiarato
    assert fb.set_rtdb("/positions/BTCUSDT", None) is False


def test_the_heartbeat_can_no_longer_kill_the_process():
    """L'heartbeat sta in un `finally`: un'eccezione li' non viene intercettata da
    nessuno e fa terminare run(). Era il modo in cui un guasto Firebase spegneva il
    bot con le posizioni aperte."""
    fb = _broken_firebase()
    fb.set_rtdb("/bot_status/heartbeat", 1234.0)             # non deve sollevare


def test_reads_fall_back_to_the_last_known_value():
    fb = _broken_firebase()
    fb.set_rtdb("/account/equity", 987.0)     # finita nello specchio in memoria
    assert fb.get_rtdb("/account/equity") == 987.0


def test_a_successful_read_refreshes_the_mirror():
    """Cosi' quando il database smettera' di rispondere, il valore piu' fresco e'
    gia' in memoria invece dell'ultimo che avevamo scritto NOI."""
    class _OkRef:
        def get(self):
            return 4242.0

    class _OkDb:
        def reference(self, path):
            return _OkRef()

    fb = FirebaseClient()
    fb._live, fb._db = True, _OkDb()
    assert fb.get_rtdb("/account/equity") == 4242.0
    fb._db = _BrokenDb()
    assert fb.get_rtdb("/account/equity") == 4242.0


def test_the_outage_is_measured_in_time_not_in_errors():
    """Una richiesta persa e' rete, dieci minuti di silenzio sono un guasto: si
    giudica la durata."""
    fb = _broken_firebase()
    assert fb.degraded_for(now=1000.0) == 0.0        # ancora nessun fallimento
    fb._rtdb_down_since = 1000.0
    assert fb.degraded_for(now=1300.0) == 300.0


def test_recovery_clears_the_outage():
    fb = _broken_firebase()
    fb.get_rtdb("/x")                                 # fallisce -> degrado aperto
    assert fb.degraded_for() > 0 or fb._rtdb_down_since is not None

    class _OkDb:
        def reference(self, path):
            class _R:
                def get(self_inner):
                    return 1
            return _R()

    fb._db = _OkDb()
    fb.get_rtdb("/x")
    assert fb.degraded_for() == 0.0
    assert fb.health()["rtdb_failures"] == 0


def test_a_short_blip_does_not_stop_the_bot_from_opening(monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_DEGRADED_BLOCK_SECONDS", 300.0)
    fb = _broken_firebase()
    fb._rtdb_down_since = 1000.0
    assert _FakeBot(fb=fb)._firebase_guard(1010.0) == 0.0     # 10s: si opera


def test_a_sustained_outage_stops_new_positions(monkeypatch):
    """Col RTDB muto non si legge piu' /commands, e li' dentro c'e' il kill switch:
    aprire mentre il freno dell'utente e' scollegato aggiunge rischio che nessuno
    puo' piu' fermare."""
    monkeypatch.setattr(settings, "FIREBASE_DEGRADED_BLOCK_SECONDS", 300.0)
    fb = _broken_firebase()
    fb._rtdb_down_since = 1000.0
    assert _FakeBot(fb=fb)._firebase_guard(1400.0) == 400.0   # blocco, con la durata


def test_the_block_can_be_disabled(monkeypatch):
    monkeypatch.setattr(settings, "FIREBASE_DEGRADED_BLOCK_SECONDS", 0.0)
    fb = _broken_firebase()
    fb._rtdb_down_since = 1.0
    assert _FakeBot(fb=fb)._firebase_guard(99999.0) == 0.0


def test_open_positions_are_still_managed_with_firebase_down():
    """La meta' che conta della regola: si smette di APRIRE, non di GESTIRE. Lo stop
    scatta anche col database muto, perche' per eseguirlo servono il prezzo di
    Binance e lo stato in memoria — non Firebase."""
    eng = ExecutionEngine(firebase=_broken_firebase(), dry_run=True)
    eng.open_position(_asset(100.0), "trend_following", Direction.LONG, _params())
    closed = eng.update_position("BTCUSDT", 97.0)
    assert closed is not None and closed.exit_reason is ExitReason.STOP_LOSS


def test_firestore_still_raises_on_purpose():
    """Firestore NON viene reso silenzioso: li' ci sono i trade chiusi. Se una
    scrittura fallita passasse per riuscita, il WAL verrebbe cancellato subito dopo
    e quel trade sparirebbe per sempre. Meglio un ciclo interrotto che un trade
    perso."""
    class _BrokenFs:
        def collection(self, name):
            raise ConnectionError("firestore irraggiungibile")

    fb = FirebaseClient()
    fb._live, fb._fs = True, _BrokenFs()
    with pytest.raises(ConnectionError):
        fb.set_doc("trades", "t1", {"pnl": 1.0})


def test_an_unconfigured_firebase_is_not_a_degraded_one():
    """Due guasti diversi: 'non configurato' e' uno stato noto in partenza (store in
    memoria, tutto funziona), 'configurato e muto' e' un'emergenza. Confonderli
    significherebbe bloccare le aperture in ogni test e a ogni avvio locale."""
    fb = FirebaseClient()                 # nei test FIREBASE_SERVICE_ACCOUNT e' vuoto
    assert fb.is_live is False
    fb.set_rtdb("/account/equity", 500.0)
    assert fb.get_rtdb("/account/equity") == 500.0
    assert fb.degraded_for() == 0.0
