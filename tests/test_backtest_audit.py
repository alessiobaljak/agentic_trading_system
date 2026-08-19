"""REVISIONE DEL BACKTESTING — un test per ogni difetto trovato il 19 agosto.

Non e' un file di test tematico: e' il verbale di un controllo sistematico, fatto
dopo che le correzioni mirate avevano gia' lasciato passare due volte qualcosa. Ogni
test qui sotto e' scritto per FALLIRE sul codice di prima. Se un giorno tornano a
passare tutti tranne uno, quello dice esattamente cosa e' rientrato.

Il piu' importante e' `test_two_coins_do_not_share_the_same_1h_frame`: e' l'unico
difetto che sporcava i NUMERI invece del tempo, e lo faceva in silenzio.
"""
from datetime import datetime, timedelta, timezone

import pytest

from backtesting.engine import Backtester, gate_verdict
from bot.config import settings
from bot.core.models import Candle


def _series(px0: float, n: int = 400, minutes: int = 15) -> list[Candle]:
    """Serie deterministica sulla GRIGLIA CONDIVISA: stesso inizio, stessa fine,
    stessa lunghezza per ogni coin — che e' esattamente la situazione reale."""
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    out, px = [], px0
    for k in range(n):
        px *= (1 + (0.002 if k % 7 else -0.004))
        out.append(Candle(open_time=t0 + timedelta(minutes=minutes * k), open=px,
                          high=px * 1.01, low=px * 0.99, close=px, volume=1000.0))
    return out


# --------------------------------------------------------------------------- #
# 1. LA COLLISIONE DELLA CACHE 1h — il difetto che sporcava i numeri            #
# --------------------------------------------------------------------------- #
def test_two_coins_do_not_share_the_same_1h_frame():
    """La chiave della cache 1h era (prima_candela, ultima_candela, quante).

    Tutte le coin condividono la griglia temporale: chiesta la stessa storia con lo
    stesso timeframe, quelle tre cose sono IDENTICHE per BTCUSDT e per qualunque
    altra coin quotata da prima di --start. Quindi la seconda coin di ogni worker
    riceveva la 1h della prima, e la prima era sempre BTC (il contesto cross-asset
    si costruisce all'avvio del worker). Regime di mercato e conferma dual-timeframe
    calcolati sul grafico di bitcoin per quasi tutto l'universo, in ogni finestra e
    in ogni holdout, senza una riga di log.
    """
    bt = Backtester(window=200, interval_hours=0.25)
    btc, alt = _series(50_000.0), _series(0.85)
    f_btc, _ = bt._htf_for("BTCUSDT", btc)
    f_alt, _ = bt._htf_for("ALTUSDT", alt)

    assert (btc[0].open_time, btc[-1].open_time, len(btc)) == \
           (alt[0].open_time, alt[-1].open_time, len(alt)), \
        "premessa del test: la griglia e' davvero identica"
    assert f_btc is not f_alt, "due coin, due frame 1h: la cache non deve confonderle"
    assert float(f_alt.iloc[-1]["close"]) == pytest.approx(alt[-1].close, rel=1e-9), \
        "la 1h della alt deve venire dalla ALT, non da bitcoin"


def test_the_1h_cache_still_works_within_one_coin():
    """La correzione non deve buttare via il riuso: dentro una coin l'optimizer
    richiama la stessa slice decine di volte, e ricalcolarla ogni volta costerebbe
    piu' della grid search."""
    bt = Backtester(window=200, interval_hours=0.25)
    c = _series(100.0)
    assert bt._htf_for("XUSDT", c) is bt._htf_for("XUSDT", c)


# --------------------------------------------------------------------------- #
# 2. LA CONSISTENZA SU UNA SOLA FINESTRA                                       #
# --------------------------------------------------------------------------- #
def _good(**over) -> dict:
    base = dict(window_pnls=[0.2, 0.2, 0.2], n_trades=settings.GATE_MIN_TRADES + 10,
                pf=settings.GATE_PF_THRESHOLD + 0.3,
                win_rate=settings.GATE_WIN_RATE_FLOOR + 0.1,
                total_return=settings.GATE_MIN_TOTAL_RETURN + 0.2)
    base.update(over)
    return base


def test_all_trades_in_one_window_is_not_a_walk_forward():
    """Il criterio di consistenza guarda solo le finestre CON trade — giusto, una
    finestra senza segnali non e' una perdita. Ma da solo lasciava un buco: una
    candidata che concentra tutti i suoi trade in una sola delle tre finestre
    superava la consistenza con UNA osservazione, e il gate dichiarava
    'profittevole in ogni finestra OOS' avendone vista una.

    Non e' un dettaglio statistico: e' la differenza fra un walk-forward e un
    backtest normale con un nome altisonante."""
    v = gate_verdict(**_good(window_pnls=[0.6]))
    assert not v.ok
    assert "oos_windows" in v.failed


def test_two_populated_windows_are_enough():
    """La soglia e' 2 su 3, non 3 su 3: una finestra puo' legittimamente non avere
    segnali, e pretenderle tutte punirebbe le strategie selettive."""
    assert gate_verdict(**_good(window_pnls=[0.3, 0.3])).ok


def test_the_windows_criterion_is_not_tunable_by_the_supervisor():
    """Non e' una soglia di severita': e' la definizione di walk-forward. Un
    supervisore che potesse abbassarla si comprerebbe passaggi cancellando proprio
    la prova che il gate esiste per raccogliere."""
    from bot.learning.supervisor import TUNABLES
    assert "oos_windows" not in TUNABLES
    assert "GATE_MIN_OOS_WINDOWS" not in {t.name for t in TUNABLES.values()}


# --------------------------------------------------------------------------- #
# 3. LA DERIVA CHE PURGAVA IN SEI ORE                                          #
# --------------------------------------------------------------------------- #
def test_drift_costs_one_failure_per_window_not_per_run():
    """Il ramo della deriva saltava judge_window e incrementava fail_count a OGNI
    run: col timer ogni tre ore una coppia smentita dal paper spariva in sei ore, e
    la redenzione promessa a parole ('se ripassa il gate su storia aggiornata il
    contatore si azzera') era irraggiungibile, perche' l'azzeramento avviene solo
    alla chiusura di una finestra e la coppia non ne vedeva mai una.

    E' lo stesso difetto dei due orologi che judge_window aveva chiuso altrove,
    rimasto vivo su questo ramo: la correzione mirata aveva sistemato il percorso
    principale e lasciato in piedi la scorciatoia."""
    from scripts.optimize import judge_window
    settimana = 168 * 3600.0
    t0 = 1_700_000_000.0
    rec = {"pass_count": 1, "window_start": t0, "passed_in_window": True}

    # 56 run in sette giorni, tutti con la coppia in deriva
    for i in range(56):
        rec["passed_in_window"] = False              # cio' che fa il ramo deriva
        judge_window(rec, t0 + i * 3 * 3600.0, False, settimana)
    assert rec.get("fail_count", 0) == 0, "dentro la finestra non si viene purgati"

    rec["passed_in_window"] = False
    judge_window(rec, t0 + settimana + 3600.0, False, settimana)
    assert rec["fail_count"] == 1, "un fallimento per finestra, non per run"


def test_a_pair_that_stops_drifting_can_redeem_itself():
    """La promessa scritta nella docstring deve essere eseguibile."""
    from scripts.optimize import judge_window
    settimana = 168 * 3600.0
    t0 = 1_700_000_000.0
    rec = {"pass_count": 1, "window_start": t0, "passed_in_window": False}
    judge_window(rec, t0 + settimana + 1, False, settimana)      # finestra in deriva
    assert rec["fail_count"] == 1
    judge_window(rec, t0 + settimana + 2, True, settimana)       # ripassa il gate
    judge_window(rec, t0 + 2 * settimana + 2, False, settimana)  # chiusura
    assert rec["fail_count"] == 0 and rec["pass_count"] == 2


# --------------------------------------------------------------------------- #
# 4. LE COIN DELISTATE NEL JOB CHE ALIMENTA IL REGISTRO                        #
# --------------------------------------------------------------------------- #
def test_the_production_gate_skips_delisted_coins():
    """`looks_delisted` esisteva da tempo, ma era cablato solo in
    backtesting/run.py — il report che si lancia a mano. I due job che riempiono il
    registro non lo chiamavano, quindi una coin con due anni di storia ferma a sei
    mesi fa veniva validata su un mercato che non esiste piu'."""
    import inspect
    from scripts import discover_strategies, optimize
    for mod in (optimize, discover_strategies):
        assert "looks_delisted" in inspect.getsource(mod), \
            f"{mod.__name__} valida anche cio' che non e' piu' quotato"


# --------------------------------------------------------------------------- #
# 5. IL PASSO DELLA CACHE DEDOTTO DALLA PRIMA COPPIA                           #
# --------------------------------------------------------------------------- #
def test_a_gap_at_the_start_does_not_invalidate_the_whole_cache():
    """Il passo veniva dedotto dalla PRIMA coppia di candele. Se proprio li' c'era un
    buco (manutenzione dell'exchange), tutte le coppie successive sembravano
    incoerenti e la serie veniva buttata: quattro anni di candele riscaricati per
    niente. Non produceva numeri sbagliati, solo ore di rete — che e' il difetto piu'
    difficile da notare, perche' somiglia alla lentezza normale."""
    from backtesting.data_loader import _merge_candles
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    def c(minuti):
        return Candle(open_time=t0 + timedelta(minutes=minuti), open=1.0, high=1.0,
                      low=1.0, close=1.0, volume=1.0)
    # buco iniziale (0 -> 60), poi passo regolare da 15 minuti
    base = [c(0), c(60), c(75), c(90)]
    tail = [c(105), c(120)]
    merged = _merge_candles(base, tail)
    assert merged is not None and len(merged) == 6


def test_two_series_with_different_timeframes_are_still_rejected():
    """Il controllo deve restare capace di dire no: unire una 15m e una 1h
    produrrebbe una storia che non e' mai esistita su nessun exchange."""
    from backtesting.data_loader import _merge_candles
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    def c(minuti):
        return Candle(open_time=t0 + timedelta(minutes=minuti), open=1.0, high=1.0,
                      low=1.0, close=1.0, volume=1.0)
    assert _merge_candles([c(0), c(15), c(30)], [c(40), c(50)]) is None


# --------------------------------------------------------------------------- #
# 6. IL CONFINE DELL'HOLDOUT                                                   #
# --------------------------------------------------------------------------- #
def test_the_holdout_never_counts_trades_from_before_the_cut():
    """L'holdout include il warmup degli indicatori PRIMA del taglio, e va bene: gli
    indicatori devono essere caldi. Ma se la storia e' piu' corta del warmup l'indice
    di partenza veniva bloccato a zero e i primi trade cadevano prima del taglio —
    l'holdout avrebbe verificato in parte su dati che la selezione aveva gia' visto,
    cioe' l'unica cosa che non deve fare."""
    import inspect
    from backtesting.optimizer import WalkForwardOptimizer
    src = inspect.getsource(WalkForwardOptimizer._holdout_check)
    assert "entry_ts" in src and "h0" in src, \
        "il filtro sul confine dell'holdout non c'e' piu'"
