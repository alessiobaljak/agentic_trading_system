"""GLI SPIKE — che il sistema li veda, e che il backtest dica quando li tronca.

Nasce da una domanda del proprietario: «bitcoin ha fatto +10%, e succede spesso —
nel backtest abbiamo strategie per questo?». La risposta ha due meta': quali
strategie sono ACCESE in quel momento (questo file), e quanto ci guadagnano davvero
(scripts/spike_response.py, che ha bisogno della rete verso gli exchange).
"""
from datetime import datetime, timedelta, timezone

from backtesting.engine import HORIZON_BARS, Backtester
from bot.core.models import Candle, Regime
from scripts.spike_response import trova_spike


def _serie(mosse: list[float]) -> list[Candle]:
    """Serie da una lista di variazioni per barra."""
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    out, px = [], 100.0
    for k, m in enumerate(mosse):
        nuovo = px * (1 + m)
        out.append(Candle(open_time=t0 + timedelta(hours=k), open=px,
                          high=max(px, nuovo), low=min(px, nuovo),
                          close=nuovo, volume=1000.0))
        px = nuovo
    return out


# ---- trovare gli eventi --------------------------------------------------- #
def test_a_ten_percent_move_is_found():
    c = _serie([0.0] * 5 + [0.10] + [0.0] * 5)
    assert len(trova_spike(c, 0.10, 1)) == 1


def test_a_crash_counts_as_much_as_a_pump():
    """Uno spike al ribasso e' un evento quanto uno al rialzo: il sistema puo'
    andare corto, e comunque deve sapere cosa gli e' successo attorno."""
    c = _serie([0.0] * 5 + [-0.12] + [0.0] * 5)
    assert len(trova_spike(c, 0.10, 1)) == 1


def test_one_long_move_is_one_event_not_many():
    """Un rialzo che dura tre barre, scorrendo barra per barra, verrebbe contato
    tre volte: la statistica direbbe «tre spike» dove ce n'e' stato uno, e ogni
    media calcolata sopra sarebbe sbagliata."""
    c = _serie([0.0] * 4 + [0.05, 0.05, 0.05] + [0.0] * 8)
    assert len(trova_spike(c, 0.09, 2)) == 1


def test_a_slow_climb_is_not_a_spike():
    """+1% per venti barre non e' uno spike: e' un trend, e lo prendono altre
    strategie. Confonderli renderebbe il conteggio inutile."""
    c = _serie([0.01] * 20)
    assert trova_spike(c, 0.10, 2) == []


# ---- CHI E' ACCESO: la meta' che non serve la rete ------------------------- #
def test_the_trend_strategies_are_off_in_high_uncertainty():
    """In HIGH_UNCERTAINTY `momentum`, `trend_following` e `momentum_cross_asset`
    sono spente. Il test fissa la mappa regime -> strategie accese, perche' e' quella
    che decide se il sistema puo' rispondere a un movimento.

    ATTENZIONE A NON DEDURNE TROPPO — e' l'errore che ho fatto io. Avevo scritto che
    "le tre strategie che esistono per cavalcare un movimento sono spente proprio
    quando il movimento c'e'". La misura sui dati veri (ops/results/0017-spike.md)
    dice il contrario: uno spike del 10% in 24h porta in HIGH_UNCERTAINTY solo il
    20% dei casi su BTC, il 21% su ETH, il 33% su SOL. L'ATR e' una media a 14
    periodi, quindi una giornata violenta da sola non lo sposta sopra il 2.5%.

    Nell'80% dei casi quelle tre strategie sono ACCESE, e sono anche le uniche in
    guadagno durante gli spike. La mappa qui sotto e' corretta; la conclusione che
    ne avevo tratto no. Un vincolo vero letto senza misurarne la frequenza porta a
    una conclusione sbagliata con la stessa sicurezza di una giusta.
    """
    strategie = {s.name: s for s in Backtester(window=200).strategies}
    spente = {n for n, s in strategie.items()
              if not s.is_active_in(Regime.HIGH_UNCERTAINTY)}
    assert {"momentum", "trend_following", "momentum_cross_asset"} <= spente

    # e queste invece ci sono: il sistema non e' cieco, risponde con altre
    accese = {n for n, s in strategie.items()
              if s.is_active_in(Regime.HIGH_UNCERTAINTY)}
    assert {"breakout", "liquidity_grab", "mean_reversion"} <= accese


def test_the_regime_is_read_from_bitcoin_in_live_and_from_the_coin_in_the_gate():
    """LA DIVERGENZA. `refresh_regime` (bot/main.py) costruisce lo snapshot di
    BTCUSDT e usa quell'etichetta per TUTTE le coin; il backtest la calcola per ogni
    coin sui dati della coin. Siccome il regime decide QUALI STRATEGIE SI ACCENDONO,
    le due letture possono far operare il gate e il bot in modo diverso sulla stessa
    barra.

    Il test non giudica quale sia giusta: fissa il fatto, cosi' che chi ne allinea
    una debba passare di qui."""
    import inspect
    from bot import main as live
    from backtesting import engine

    assert 'build_snapshot("BTCUSDT")' in inspect.getsource(live.TradingBot.refresh_regime)
    # nel motore il regime esce dallo snapshot della coin in esame
    assert "self.regime_detector.detect(snap)" in inspect.getsource(engine.Backtester._prepared)


# ---- il troncamento, ora misurabile --------------------------------------- #
def test_a_trade_records_how_long_it_stayed_open():
    """Senza questo campo non si distingue un'uscita VOLUTA (stop o target) da una
    chiusura d'ufficio all'orizzonte. Per uno spike che continua per giorni la
    differenza e' tutta: nel secondo caso il backtest non ha misurato il risultato,
    ne ha misurato un limite inferiore."""
    from backtesting.engine import SimTrade
    assert "bars_held" in SimTrade.__dataclass_fields__


def test_the_horizon_is_a_named_constant():
    """Era un 96 in mezzo al codice. Un confine della simulazione che gli strumenti
    di analisi devono poter leggere non puo' essere un numero magico."""
    assert HORIZON_BARS == 96
    import inspect
    from backtesting import engine
    assert "i + HORIZON_BARS" in inspect.getsource(engine.Backtester.run_strategy)
