"""INGRESSI A LIMITE NEL PAPER (13 ott 2026, si' del proprietario).

La regola e' quella della prova research/esperimenti/ordini_limite/regole.md
(sezione 4, con la correzione 1 di risultati.md): ordine al prezzo della
chiusura della candela di segnale, valido una candela, riempito AL SUO prezzo se
il prezzo lo attraversa strettamente, altrimenti saltato. Costo del lato
d'ingresso: maker, scarto zero; uscite a mercato come prima. Senza
`signal_candle_ts` (chiamate dirette, test vecchi) l'ingresso resta a mercato.
"""
import time

from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Direction, EffectiveRiskParams, ExitReason, IndicatorSnapshot, Regime,
)
from bot.execution.executor import ExecutionEngine

BAR_S = 900.0  # 15m


def _asset(price=100.0, close_chiusa=100.0, atr=2.0, symbol="BTCUSDT"):
    return AssetSnapshot(
        symbol=symbol, price=price, close_chiusa=close_chiusa, regime=Regime.BULL_TRENDING,
        indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=atr, close=price)},
    )


def _params(qty=1.0, stop=98.0, tp=104.0):
    return EffectiveRiskParams(
        leverage=3.0, risk_per_trade=0.01, notional=100.0, quantity=qty,
        stop_price=stop, take_profit_price=tp,
        user_leverage=3, user_risk_per_trade=0.01,
        safety_leverage_cap=5, safety_risk_cap=0.03, approved=True,
    )


def _engine(fb=None):
    eng = ExecutionEngine(firebase=fb or FirebaseClient(), dry_run=True)
    eng.ingresso_limite = True
    eng.maker_fee = 0.0002
    return eng


def _ordine_long(eng, boundary, symbol="BTCUSDT", price=100.2, close_chiusa=100.0, stop=98.0, tp=110.0):
    pos = eng.open_position(_asset(price, close_chiusa, symbol=symbol), "trend_following", Direction.LONG,
                            _params(stop=stop, tp=tp), timeframe="15m", signal_candle_ts=boundary)
    return pos


def _contatori(eng):
    return eng.fb.get_rtdb("/paper/ordini_limite/contatori") or {}


def test_la_decisione_mette_un_ordine_e_non_apre():
    eng = _engine()
    b = time.time()
    assert _ordine_long(eng, b) is None
    assert "BTCUSDT" not in eng.open_positions
    o = eng.ordini_limite["BTCUSDT"]
    assert o.prezzo == 100.0 and o.scadenza == b + BAR_S
    assert o.pos.ingresso_tipo == "limite" and o.pos.entry_fee_frac == 0.0002
    assert eng.fb.get_rtdb("/ordini_limite/BTCUSDT")["ordine"]["prezzo"] == 100.0
    assert _contatori(eng)["messi"] == 1


def test_riempito_al_suo_prezzo_quando_il_minimo_scende_sotto():
    eng = _engine()
    b = time.time()
    _ordine_long(eng, b)
    # tick sopra il limite: niente
    assert eng.update_ordini_limite("BTCUSDT", 100.5, high=100.8, low=100.1, now=b + 60) is None
    assert "BTCUSDT" in eng.ordini_limite
    # tick che ATTRAVERSA: riempito a 100.0, non a 99.9
    pos = eng.update_ordini_limite("BTCUSDT", 100.3, high=100.6, low=99.9, now=b + 120)
    assert pos is not None and pos.entry_price == 100.0 and pos.ingresso_tipo == "limite"
    assert pos.limite_prezzo == 100.0 and pos.high_water == 100.0 and pos.low_water == 100.0
    assert "BTCUSDT" in eng.open_positions and "BTCUSDT" not in eng.ordini_limite
    assert eng.fb.get_rtdb("/ordini_limite/BTCUSDT") is None
    assert eng.fb.get_rtdb("/positions/BTCUSDT")["ingresso_tipo"] == "limite"
    c = _contatori(eng)
    assert c["messi"] == 1 and c["eseguiti"] == 1 and "saltati" not in c


def test_toccato_non_basta_e_alla_scadenza_e_saltato():
    eng = _engine()
    b = time.time()
    _ordine_long(eng, b)
    assert eng.update_ordini_limite("BTCUSDT", 100.2, high=100.9, low=100.0, now=b + 300) is None
    assert "BTCUSDT" in eng.ordini_limite  # low == P: toccato, non attraversato
    assert eng.update_ordini_limite("BTCUSDT", 100.4, high=101.0, low=100.05, now=b + BAR_S) is None
    assert "BTCUSDT" not in eng.ordini_limite and "BTCUSDT" not in eng.open_positions
    saltati = eng.fb.get_rtdb("/paper/ordini_limite/saltati")
    assert len(saltati) == 1
    rec = list(saltati.values())[0]
    assert rec["motivo"] == "scaduto" and rec["limite_prezzo"] == 100.0
    assert rec["lo_visto"] == 100.0 and rec["hi_visto"] == 101.0 and rec["symbol"] == "BTCUSDT"
    assert _contatori(eng)["saltati"] == 1


def test_short_simmetrico():
    eng = _engine()
    b = time.time()
    eng.open_position(_asset(99.8, 100.0), "trend_following", Direction.SHORT,
                      _params(stop=102.0, tp=94.0), timeframe="15m", signal_candle_ts=b)
    assert eng.update_ordini_limite("BTCUSDT", 99.7, high=100.0, low=99.2, now=b + 60) is None
    pos = eng.update_ordini_limite("BTCUSDT", 99.9, high=100.1, low=99.5, now=b + 120)
    assert pos is not None and pos.entry_price == 100.0 and pos.direction == Direction.SHORT


def test_tick_tutto_oltre_il_limite_riempie_al_limite_non_al_tick():
    # correzione 1: un ordine nel libro esegue al suo prezzo anche se il mercato apre piu' in basso
    eng = _engine()
    b = time.time()
    _ordine_long(eng, b)
    pos = eng.update_ordini_limite("BTCUSDT", 98.8, high=99.2, low=98.5, now=b + 30)
    assert pos is not None and pos.entry_price == 100.0


def test_costi_maker_sull_ingresso_e_meta_dello_spread():
    fb = FirebaseClient()
    eng = _engine(fb)
    b = time.time()
    # a mercato (nessuna candela di segnale): modello di sempre
    eng.ingresso_limite = False
    m = eng.open_position(_asset(100.0, 100.0, symbol="ETHUSDT"), "s", Direction.LONG, _params(stop=98, tp=104))
    assert m is not None and m.ingresso_tipo == "mercato" and m.entry_fee_frac is None
    tm = eng.update_position("ETHUSDT", 104.5, high=104.5, low=103.0)
    # a limite
    eng.ingresso_limite = True
    _ordine_long(eng, b, price=100.0, close_chiusa=100.0, stop=98.0, tp=104.0)
    pos = eng.update_ordini_limite("BTCUSDT", 100.0, high=100.2, low=99.9, now=b + 30)
    assert pos is not None
    tl = eng.update_position("BTCUSDT", 104.5, high=104.5, low=103.0)
    assert tm.exit_reason == ExitReason.TAKE_PROFIT and tl.exit_reason == ExitReason.TAKE_PROFIT
    notional = 100.0 * 1.0
    assert abs(tm.commission_usdt - 0.0008 * notional) < 1e-9
    assert abs(tl.commission_usdt - (0.0004 + 0.0002) * notional) < 1e-9
    assert abs(tm.spread_usdt - 0.0008 * notional) < 1e-9       # fascia sottile (volume ignoto)
    assert abs(tl.spread_usdt - 0.0004 * notional) < 1e-9
    assert tl.pnl > tm.pnl
    assert tl.ingresso_tipo == "limite" and tl.limite_prezzo == 100.0 and tl.attesa_ingresso_s is not None
    assert tm.ingresso_tipo == "mercato" and tm.limite_prezzo is None and tm.attesa_ingresso_s is None


def test_senza_candela_di_segnale_o_con_l_interruttore_giu_resta_a_mercato():
    eng = _engine()
    p1 = eng.open_position(_asset(100.0, 100.0), "s", Direction.LONG, _params(stop=98, tp=104))
    assert p1 is not None and p1.ingresso_tipo == "mercato" and not eng.ordini_limite
    eng.update_position("BTCUSDT", 97.0)
    eng.ingresso_limite = False
    p2 = eng.open_position(_asset(100.0, 100.0), "s", Direction.LONG, _params(stop=98, tp=104),
                           signal_candle_ts=time.time())
    assert p2 is not None and p2.ingresso_tipo == "mercato" and not eng.ordini_limite


def test_stop_dalla_parte_sbagliata_del_limite_va_a_mercato_e_si_conta():
    eng = _engine()
    pos = eng.open_position(_asset(100.0, 97.0), "s", Direction.LONG, _params(stop=98, tp=104),
                            timeframe="15m", signal_candle_ts=time.time())
    assert pos is not None and pos.ingresso_tipo == "mercato" and not eng.ordini_limite
    assert _contatori(eng)["a_mercato_stop_oltre_il_limite"] == 1


def test_candela_gia_finita_va_a_mercato_e_si_conta():
    eng = _engine()
    pos = _ordine_long(eng, time.time() - 2 * BAR_S)
    assert pos is not None and pos.ingresso_tipo == "mercato"
    assert _contatori(eng)["a_mercato_candela_finita"] == 1


def test_un_segnale_nuovo_sullo_stesso_simbolo_sostituisce_l_ordine():
    eng = _engine()
    b = time.time()
    _ordine_long(eng, b, close_chiusa=100.0)
    _ordine_long(eng, b, close_chiusa=101.0, stop=99.0)
    assert eng.ordini_limite["BTCUSDT"].prezzo == 101.0
    c = _contatori(eng)
    assert c["messi"] == 2 and c["sostituiti"] == 1
    rec = list(eng.fb.get_rtdb("/paper/ordini_limite/saltati").values())[0]
    assert rec["motivo"] == "sostituito" and rec["limite_prezzo"] == 100.0


def test_ripristino_dopo_un_riavvio_e_scaduto_al_riavvio():
    fb = FirebaseClient()
    eng = _engine(fb)
    b = time.time()
    _ordine_long(eng, b)
    eng.update_ordini_limite("BTCUSDT", 100.4, high=100.7, low=100.1, now=b + 30)
    # un altro processo riparte sullo stesso Firebase: l'ordine e' ancora vivo
    eng2 = _engine(fb)
    o = eng2.ordini_limite["BTCUSDT"]
    assert o.prezzo == 100.0 and o.scadenza == b + BAR_S and o.hi_visto == 100.7 and o.lo_visto == 100.1
    assert o.pos.strategy == "trend_following" and o.pos.stop_price == 98.0 and o.pos.entry_fee_frac == 0.0002
    pos = eng2.update_ordini_limite("BTCUSDT", 100.0, high=100.2, low=99.8, now=b + 60)
    assert pos is not None and pos.entry_price == 100.0 and pos.ingresso_tipo == "limite"
    # un ordine scaduto mentre il bot era giu': saltato al riavvio, nessuna posizione
    fb2 = FirebaseClient()
    eng3 = _engine(fb2)
    _ordine_long(eng3, time.time() - BAR_S + 5)   # scade fra 5 secondi
    doc = fb2.get_rtdb("/ordini_limite/BTCUSDT")
    doc["ordine"]["scadenza"] = time.time() - 1
    fb2.set_rtdb("/ordini_limite/BTCUSDT", doc)
    eng4 = _engine(fb2)
    assert not eng4.ordini_limite and not eng4.open_positions
    assert fb2.get_rtdb("/paper/ordini_limite/contatori")["scaduti_al_riavvio"] == 1


def test_il_kill_switch_annulla_anche_gli_ordini_in_attesa():
    eng = _engine()
    _ordine_long(eng, time.time())
    assert eng.force_close_all({}, ExitReason.KILL_SWITCH) == []
    assert not eng.ordini_limite and _contatori(eng)["annullati"] == 1


def test_la_posizione_a_limite_si_ripristina_con_il_suo_costo():
    fb = FirebaseClient()
    eng = _engine(fb)
    b = time.time()
    _ordine_long(eng, b, price=100.0, close_chiusa=100.0, tp=104.0)
    eng.update_ordini_limite("BTCUSDT", 100.0, high=100.2, low=99.9, now=b + 30)
    eng2 = _engine(fb)
    p = eng2.open_positions["BTCUSDT"]
    assert p.ingresso_tipo == "limite" and p.limite_prezzo == 100.0 and p.entry_fee_frac == 0.0002
    t = eng2.update_position("BTCUSDT", 104.5, high=104.5, low=103.0)
    assert abs(t.commission_usdt - 0.0006 * 100.0) < 1e-9 and t.ingresso_tipo == "limite"
