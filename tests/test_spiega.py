"""LA REGOLA SPIEGATA E LA DECISIONE SULLA CHIUSURA (27 set 2026, backlog J12).

Ops 0308 ha trovato due cose che il bot faceva senza che nessuno potesse
vederlo: (1) `gen_6d06dca0` apriva trade su ORCAUSDT/VETUSDT che il motore non
apre, e la regola non scattava nemmeno sui valori scritti dal paper — senza uno
strumento che dica QUALE feature frena, resta «ignoto»; (2) il bot valutava la
regola sul prezzo VIVO della candela in formazione mentre il motore la valuta
sulla chiusura dell'ultima candela chiusa: 5 trade decisi da 1-4 decimillesimi.

Qui si difende:
  * `spiega` e `generate_signal` sono la STESSA valutazione (200 snapshot a caso,
    spec di ogni tipo: base, mercato, 1h, solo un lato, filtri);
  * `spiega` e' in sola lettura e dice quale feature frena, con i suoi numeri;
  * con `DECISIONE_SU_CHIUSURA` la regola decide su `close_chiusa` e non sul
    prezzo vivo (che resta per stop e ingresso); spento, torna com'era;
  * il motore non cambia di un trade con l'interruttore acceso o spento;
  * `price_agent.build_snapshot` riempie `close_chiusa` con la chiusura
    dell'ultima candela CHIUSA del timeframe primario.
"""
import random
from datetime import datetime, timedelta, timezone

from backtesting.engine import Backtester
from bot.config import settings
from bot.core.indicators import compute_indicator_frame
from bot.core.models import AssetSnapshot, Candle, Direction, IndicatorSnapshot, Regime
from bot.strategies.base import StrategyContext
from bot.strategies.generated import GeneratedStrategy


def _ind(tf="15m", **kw) -> IndicatorSnapshot:
    base = dict(rsi=50.0, atr=2.0, close=100.0, bb_lower=95.0, bb_upper=105.0, bb_mid=100.0,
                ema_fast=100.0, ema_slow=100.0, macd=0.0, macd_signal=0.0, macd_hist=0.0,
                vwap=100.0, volume=1000.0, volume_sma=1000.0, adx=25.0, stoch_k=50.0, stoch_d=50.0)
    base.update(kw)
    return IndicatorSnapshot(timeframe=tf, **base)


def _asset(price=100.0, close_chiusa=None, ind=None, ind1h=None) -> AssetSnapshot:
    inds = {"15m": ind or _ind()}
    if ind1h is not None:
        inds["1h"] = ind1h
    return AssetSnapshot(symbol="XUSDT", price=price, close_chiusa=close_chiusa,
                         regime=Regime.SIDEWAYS, indicators=inds)


def _snapshot_a_caso(rng: random.Random) -> tuple[AssetSnapshot, StrategyContext]:
    """Uno snapshot con valori a caso, a volte con un indicatore mancante e a
    volte con un prezzo vivo diverso dalla chiusura; piu' un contesto BTC a
    volte assente."""
    px = rng.uniform(50, 150)
    kw = dict(rsi=rng.uniform(0, 100), atr=rng.uniform(0.1, 5), close=px,
              bb_lower=px * rng.uniform(0.9, 1.0), bb_upper=px * rng.uniform(1.0, 1.1), bb_mid=px,
              ema_fast=px * rng.uniform(0.97, 1.03), ema_slow=px * rng.uniform(0.97, 1.03),
              macd=rng.uniform(-1, 1), macd_signal=rng.uniform(-1, 1), macd_hist=rng.uniform(-1, 1),
              vwap=px * rng.uniform(0.98, 1.02), volume=rng.uniform(0, 3000), volume_sma=1000.0,
              adx=rng.uniform(0, 60), stoch_k=rng.uniform(0, 100), stoch_d=rng.uniform(0, 100))
    if rng.random() < 0.1:
        kw[rng.choice(list(kw))] = None
    ind = IndicatorSnapshot(timeframe="15m", **kw)
    ind1h = IndicatorSnapshot(timeframe="1h", ema_fast=px * rng.uniform(0.95, 1.05),
                              ema_slow=px * rng.uniform(0.95, 1.05)) if rng.random() < 0.8 else None
    vivo = px * rng.uniform(0.995, 1.005)
    a = AssetSnapshot(symbol="XUSDT", price=vivo, close_chiusa=(px if rng.random() < 0.7 else None),
                      regime=Regime.SIDEWAYS, indicators={"15m": ind, **({"1h": ind1h} if ind1h else {})})
    assets = {"XUSDT": a}
    if rng.random() < 0.7:
        bp = rng.uniform(50000, 70000)
        assets["BTCUSDT"] = AssetSnapshot(symbol="BTCUSDT", price=bp, indicators={
            "15m": IndicatorSnapshot(timeframe="15m", ema_fast=bp * rng.uniform(0.98, 1.02),
                                     ema_slow=bp * rng.uniform(0.98, 1.02))})
    return a, StrategyContext(assets, Regime.SIDEWAYS)


SPECS = [
    {"id": "s1", "features": [{"kind": "rsi_extreme", "low": 35.0, "high": 65.0}]},
    {"id": "s2", "features": [{"kind": "rsi_extreme", "low": 40.0, "high": 60.0}, {"kind": "bb_touch"}]},
    {"id": "s3", "features": [{"kind": "ema_cross"}, {"kind": "price_ema"}, {"kind": "not_stretched", "stretch_max": 2.0}]},
    {"id": "s4", "features": [{"kind": "macd_cross"}, {"kind": "market_trend"}]},
    {"id": "s5", "features": [{"kind": "stoch_extreme"}, {"kind": "htf_confirm"}]},
    {"id": "s6", "features": [{"kind": "rsi_momentum"}, {"kind": "htf_fade", "htf_gap": 0.01}], "solo": "short"},
    {"id": "s7", "features": [{"kind": "bb_break"}, {"kind": "volume_surge", "vol_mult_feat": 1.2}], "volume_mult": 0.8},
    {"id": "s8", "features": [{"kind": "vwap_reversion"}, {"kind": "adx_below", "adx_hi": 30.0}], "min_adx": 10.0},
    {"id": "s9", "features": [{"kind": "relative_strength", "rs_gap": 0.0}, {"kind": "rsi_extreme"}], "solo": "long"},
    {"id": "s10", "features": [{"kind": "price_bb_mid"}, {"kind": "trend_strength", "adx_lo": 20.0}]},
    {"id": "s11", "features": [{"kind": "feature_inventata"}]},
    {"id": "s12", "features": []},
]


def test_spiega_e_generate_signal_concordano_su_200_snapshot_a_caso():
    """Per ogni spec e per 200 snapshot: la direzione di `spiega` e' quella del
    segnale (o nessuna per entrambi). E' la garanzia che lo strumento degli
    ingressi spiega la regola VERA, non una copia."""
    rng = random.Random(27092026)
    confronti = con_segnale = 0
    for _ in range(200):
        a, ctx = _snapshot_a_caso(rng)
        for spec in SPECS:
            st = GeneratedStrategy(spec)
            prima = a.model_dump()
            v = st.spiega(a, ctx)
            assert a.model_dump() == prima, "spiega ha modificato lo snapshot"
            sig = st.generate_signal(a, ctx)
            atteso = None if sig is None else sig.direction.value.lower()
            assert v["direzione_finale"] == atteso, (spec["id"], v, sig)
            assert v["motivo"]
            confronti += 1
            con_segnale += sig is not None
    assert confronti == 200 * len(SPECS)
    assert con_segnale > 50, "il campione deve contenere segnali veri, non solo silenzi"


def test_spiega_dice_quale_feature_frena_e_con_quali_numeri():
    st = GeneratedStrategy({"id": "x", "features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0},
                                                    {"kind": "bb_touch"}]})
    # RSI basso (long ok) ma prezzo a meta' banda: e' bb_touch a fermare il long
    v = st.spiega(_asset(price=100.0, ind=_ind(rsi=20.0)))
    assert v["direzione_finale"] is None
    assert v["features"]["rsi_extreme"] == {"kind": "rsi_extreme", "long": True, "short": False,
                                            "valori": {"low": 30.0, "high": 70.0, "rsi": 20.0}}
    assert v["features"]["bb_touch"]["long"] is False and v["features"]["bb_touch"]["short"] is False
    assert v["features"]["bb_touch"]["valori"] == {"price": 100.0, "bb_lower": 95.0, "bb_upper": 105.0}
    assert "bb_touch" in v["motivo"] and "rsi_extreme" not in v["motivo"]
    # tutte d'accordo -> LONG, e il prezzo su cui ha deciso e' nel verdetto
    v = st.spiega(_asset(price=94.0, ind=_ind(rsi=20.0)))
    assert v["direzione_finale"] == "long" and v["prezzo"] == 94.0
    # dato mancante -> None sulla feature, motivo esplicito
    v = st.spiega(_asset(price=94.0, ind=_ind(rsi=None)))
    assert v["features"]["rsi_extreme"]["long"] is None and "senza dati" in v["motivo"]
    # feature sconosciuta e spec vuota
    assert "sconosciuta" in GeneratedStrategy({"id": "y", "features": [{"kind": "boh"}]}).spiega(_asset())["motivo"]
    assert "senza feature" in GeneratedStrategy({"id": "z", "features": []}).spiega(_asset())["motivo"]
    # lato escluso dalla spec
    solo = GeneratedStrategy({"id": "w", "features": [{"kind": "rsi_extreme"}], "solo": "short"})
    v = solo.spiega(_asset(price=94.0, ind=_ind(rsi=20.0)))
    assert v["direzione_finale"] is None and "solo short" in v["motivo"] and v["solo"] == "short"
    # filtri globali
    vol = GeneratedStrategy({"id": "v", "features": [{"kind": "rsi_extreme"}], "volume_mult": 2.0})
    v = vol.spiega(_asset(price=94.0, ind=_ind(rsi=20.0)))
    assert v["filtri"]["volume"]["ok"] is False and "volume" in v["motivo"]
    # il prezzo si puo' sovrascrivere senza toccare lo snapshot (per lo strumento)
    v = st.spiega(_asset(price=100.0, ind=_ind(rsi=20.0)), prezzo=94.0)
    assert v["direzione_finale"] == "long" and v["prezzo"] == 94.0 and v["prezzo_vivo"] == 100.0


def test_spiega_su_feature_di_mercato_e_di_1h_mostra_il_contesto():
    st = GeneratedStrategy({"id": "m", "features": [{"kind": "market_trend"}, {"kind": "htf_confirm"}]})
    a = _asset(ind1h=IndicatorSnapshot(timeframe="1h", ema_fast=101.0, ema_slow=100.0))
    v = st.spiega(a, None)
    assert v["features"]["market_trend"]["long"] is None and v["features"]["market_trend"]["valori"]["mercato"] is None
    assert "market_trend" in v["motivo"]
    assert v["features"]["htf_confirm"]["valori"]["1h"] == {"ema_fast": 101.0, "ema_slow": 100.0}
    btc = AssetSnapshot(symbol="BTCUSDT", price=60000.0, indicators={
        "15m": IndicatorSnapshot(timeframe="15m", ema_fast=60100.0, ema_slow=60000.0)})
    v = st.spiega(a, StrategyContext({"XUSDT": a, "BTCUSDT": btc}, Regime.SIDEWAYS))
    assert v["direzione_finale"] == "long"
    assert v["features"]["market_trend"]["valori"]["mercato"]["ema_fast"] == 60100.0


# --------------------------------------------------------------------------- #
# La decisione sulla chiusura                                                  #
# --------------------------------------------------------------------------- #
def test_la_regola_decide_sulla_chiusura_non_sul_prezzo_vivo(monkeypatch):
    """bb_touch: il prezzo vivo tocca la banda inferiore, la chiusura no. Con
    l'interruttore acceso nessun segnale; spento, il segnale nasce (com'era)."""
    st = GeneratedStrategy({"id": "b", "features": [{"kind": "bb_touch"}]})
    a = _asset(price=94.9, close_chiusa=96.0)        # vivo sotto la banda (95), chiusa sopra
    monkeypatch.setattr(settings, "DECISIONE_SU_CHIUSURA", True)
    assert st.generate_signal(a) is None
    v = st.spiega(a)
    assert v["prezzo"] == 96.0 and v["prezzo_vivo"] == 94.9 and v["close_chiusa"] == 96.0
    monkeypatch.setattr(settings, "DECISIONE_SU_CHIUSURA", False)
    sig = st.generate_signal(a)
    assert sig is not None and sig.direction == Direction.LONG
    assert st.spiega(a)["prezzo"] == 94.9
    # senza `close_chiusa` (snapshot vecchi, test) si decide sul vivo anche da acceso
    monkeypatch.setattr(settings, "DECISIONE_SU_CHIUSURA", True)
    assert st.generate_signal(_asset(price=94.9)).direction == Direction.LONG
    # e il verso opposto: chiusura sotto la banda, vivo rientrato -> segnale
    a2 = _asset(price=96.0, close_chiusa=94.9)
    assert st.generate_signal(a2).direction == Direction.LONG


def test_stop_target_e_prezzo_del_segnale_restano_sul_prezzo_vivo(monkeypatch):
    monkeypatch.setattr(settings, "DECISIONE_SU_CHIUSURA", True)
    st = GeneratedStrategy({"id": "b", "features": [{"kind": "bb_touch"}], "atr_mult_stop": 1.5, "rr": 2.0})
    a = _asset(price=94.0, close_chiusa=94.5)        # entrambi sotto la banda: segnale
    sig = st.generate_signal(a)
    assert sig is not None
    assert sig.suggested_stop == 94.0 - 1.5 * 2.0     # dal prezzo VIVO, non dalla chiusura
    assert sig.suggested_target == 94.0 + 2.0 * 1.5 * 2.0
    assert settings.DECISIONE_SU_CHIUSURA is True     # default acceso


def _serie(n: int = 600) -> list[Candle]:
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    out, px = [], 100.0
    rng = random.Random(7)
    for k in range(n):
        px *= 1 + (0.006 if (k // 20) % 2 == 0 else -0.006) + rng.uniform(-0.002, 0.002)
        out.append(Candle(open_time=t0 + timedelta(minutes=15 * k), open=px, high=px * 1.004,
                          low=px * 0.996, close=px, volume=1000.0 + (k % 5) * 10))
    return out


def test_il_motore_non_cambia_di_un_trade_con_l_interruttore(monkeypatch):
    """Nel motore `close_chiusa` E' il prezzo: acceso o spento, gli stessi trade."""
    candles = _serie()
    frame = compute_indicator_frame(candles)
    spec = {"id": "p", "features": [{"kind": "rsi_extreme", "low": 35.0, "high": 65.0}, {"kind": "bb_touch"}]}
    esiti = {}
    for flag in (True, False):
        monkeypatch.setattr(settings, "DECISIONE_SU_CHIUSURA", flag)
        bt = Backtester(window=200, interval_hours=0.25)
        st = bt.run_strategy(GeneratedStrategy(spec), "XUSDT", candles, frame=frame)
        esiti[flag] = [(t.entry_ts, t.direction, round(t.pnl_pct, 10)) for t in st.trades]
        snap = bt._snapshot_from_frame("XUSDT", frame, 300)
        assert snap.close_chiusa == snap.price == float(frame.iloc[300]["close"])
    assert esiti[True], "la serie deve produrre trade, altrimenti il confronto e' vuoto"
    assert esiti[True] == esiti[False]


def test_build_snapshot_riempie_close_chiusa_con_l_ultima_candela_chiusa(monkeypatch):
    from bot.agents.price_agent import PriceAgent
    now = datetime.now(timezone.utc)
    t0 = now - timedelta(hours=60)

    def _candles(symbol, interval, limit=200):
        n = 150
        out = []
        for k in range(n):
            px = 100.0 + (k % 7) * 0.1
            out.append(Candle(open_time=t0 + timedelta(minutes=15 * k), open=px, high=px + 0.2,
                              low=px - 0.2, close=px, volume=100.0,
                              close_time=t0 + timedelta(minutes=15 * (k + 1))))
        # l'ultima e' IN FORMAZIONE (close_time nel futuro) con un prezzo diverso
        out[-1] = out[-1].model_copy(update={"close": 123.45, "close_time": now + timedelta(minutes=10)})
        return out

    pa = PriceAgent.__new__(PriceAgent)
    pa.get_candles = _candles
    pa.get_premium = lambda symbol: {}
    pa.get_ticker_24h = lambda symbol: {}
    pa.get_open_interest = lambda symbol: None
    snap = pa.build_snapshot("XUSDT")
    assert snap is not None
    assert snap.price == 123.45                                   # vivo
    chiuse = _candles("XUSDT", settings.ORCHESTRATOR_TIMEFRAME)[:-1]
    assert snap.close_chiusa == chiuse[-1].close != snap.price    # chiusura dell'ultima chiusa
    assert snap.ind(settings.ORCHESTRATOR_TIMEFRAME).close == snap.close_chiusa
