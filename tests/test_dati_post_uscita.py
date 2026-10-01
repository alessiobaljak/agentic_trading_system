"""DOPO L'USCITA (1 ott 2026, la cattura dei dati mancanti), tre misure sulle
candele che `evaluate_pending_trailing` gia' scarica:
  3. il verdetto trailing alla maniera del GATE (ultimo gradino, stop
     ORIGINALE) accanto a quello del bot, che non cambia;
  4. cosa ha fatto il prezzo dopo l'uscita, per OGNI uscita (TP, orizzonte,
     manuale...), in R dello stop originale;
  5. il motore del gate rigiocato sullo stesso segnale.
"""
from __future__ import annotations

import pytest

from bot.config import settings
from bot.learning import cattura
from bot.learning.rifiutati import simula_segnale
from tests.test_memoria_trade_misure import NOW, _bot_verdetti, _c

B15 = 900.0


def _trail_trade(ex: float) -> dict:
    return {"trade_id": "t1", "symbol": "XUSDT", "exit_reason": "trailing_stop",
            "direction": "long", "timeframe": "15m", "entry_price": 100.0, "exit_price": 101.0,
            "orig_stop": 98.0, "stop_price": 101.0, "take_profit_price": 110.0,
            "tp_prices": [103.0, 106.0, 110.0], "exit_ts": ex, "duration_seconds": 4 * B15,
            "size": 1.0, "gross_pnl_usdt": 1.0, "profit_lock_keep": 0.5,
            "scale_r_mults": [1.5, 3.0, 5.0], "sl_to_breakeven": True}


# --------------------------------------------------------------------------- #
# 3) il verdetto trailing alla maniera del gate                                #
# --------------------------------------------------------------------------- #
def test_due_verdetti_due_domande():
    ex = NOW
    # dopo l'uscita a 101: scende a 99 (sotto lo stop FINALE 101, sopra
    # l'ORIGINALE 98), poi sale a 110,5 (oltre l'ultimo gradino)
    after = [_c(ex, 101.5, 100.5), _c(ex + B15, 100.0, 99.0), _c(ex + 2 * B15, 110.5, 100.0)]
    during = [_c(ex - 2 * B15, 103.5, 100.0), _c(ex - B15, 103.0, 100.8)]
    g = cattura.verdetto_trailing_gate(during, after, 100.0, 101.0, 98.0, [103.0, 106.0, 110.0], True)
    assert g == {"verdict": "premature", "miss_to_tp": pytest.approx(0.9)}
    assert cattura.verdetto_trailing_gate(during, after, 100.0, 101.0, None, [110.0], True) is None
    assert cattura.verdetto_trailing_gate(during, after, 100.0, 101.0, 98.0, [], True) is None


def test_evaluate_scrive_il_verdetto_del_gate_e_lascia_quello_del_bot():
    ex = NOW
    t = _trail_trade(ex)
    candles = [_c(ex - 4 * B15 + i * B15, 102.0, 100.5) for i in range(4)] + \
              [_c(ex, 101.5, 100.5), _c(ex + B15, 100.0, 99.0), _c(ex + 2 * B15, 110.5, 100.0)]
    b = _bot_verdetti(t, candles)
    b.evaluate_pending_trailing(ex + 3 * B15 + 5)
    doc = b.visto["doc"]
    # il verdetto di sempre: stop FINALE (101) e take_profit_price -> protetto
    assert doc["trailing_verdict"] == "protected"
    # quello del gate: stop ORIGINALE (98) e ultimo gradino (110) -> prematuro
    assert doc["trailing_verdict_gate"] == "premature"
    assert doc["trailing_miss_to_tp_gate"] == pytest.approx(0.9)
    assert doc[cattura.AT_GATE] == ex + 3 * B15 + 5
    # le 96 barre dopo l'uscita non ci sono ancora: post-uscita in attesa
    assert cattura.AT_POST not in doc


def test_il_verdetto_del_gate_neutral_aspetta_la_finestra():
    ex = NOW
    t = _trail_trade(ex)
    t["trailing_verdict"] = "protected"                 # quello di sempre gia' scritto
    after = [_c(ex + i * B15, 101.5, 100.5) for i in range(3)]
    out = dict(t)
    # nessuno dei due stop toccato, finestra non piena: «neutral» non si scrive
    assert cattura.cattura_dopo_uscita(out, after, [], after, ex + 3 * B15, "15m", B15,
                                       96 * B15, True) is False
    assert cattura.AT_GATE not in out and "trailing_verdict_gate" not in out
    # a finestra piena si'
    assert cattura.cattura_dopo_uscita(out, after, [], after, ex + 97 * B15, "15m", B15,
                                       96 * B15, True) is True
    assert out["trailing_verdict_gate"] == "neutral" and out[cattura.AT_GATE] == ex + 97 * B15


# --------------------------------------------------------------------------- #
# 4) il prezzo dopo l'uscita                                                   #
# --------------------------------------------------------------------------- #
def _serie(ex: float, n: int, base: float = 105.0, passo: float = 0.0):
    return [_c(ex + i * B15, base + passo * i + 0.5, base + passo * i - 0.5) for i in range(n)]


def test_misure_post_uscita_long_e_short():
    ex = NOW
    after = _serie(ex, 96)
    after[10] = _c(ex + 10 * B15, 109.0, 104.0)        # picco a favore: +2 R da 105
    after[20] = _c(ex + 20 * B15, 106.0, 102.0)        # minimo contro: -1,5 R
    m = cattura.misure_post_uscita(after, 105.0, 100.0, 98.0, True, ex)
    assert m["post_exit_mfe_r"] == pytest.approx(2.0)
    assert m["post_exit_mae_r"] == pytest.approx(1.5)
    assert m["post_exit_r_4b"] == pytest.approx(0.0)     # chiusura 105 = uscita
    assert m["post_exit_r_16b"] == pytest.approx(0.0)
    assert m["post_exit_r_96b"] == pytest.approx(0.0)
    assert m["t_post_mfe_s"] == pytest.approx(10 * B15)
    # short: lo stesso grafico e' tutto al contrario
    s = cattura.misure_post_uscita(after, 105.0, 100.0, 102.0, False, ex)
    assert s["post_exit_mfe_r"] == pytest.approx(1.5)
    assert s["post_exit_mae_r"] == pytest.approx(2.0)
    # poche candele: si aspetta
    assert cattura.misure_post_uscita(after[:50], 105.0, 100.0, 98.0, True, ex) is None
    # R non calcolabile: dict con None (non resta in attesa per sempre)
    vuoto = cattura.misure_post_uscita(after, 105.0, 100.0, None, True, ex)
    assert vuoto["post_exit_mfe_r"] is None and vuoto["post_exit_r_96b"] is None


def test_misure_post_uscita_chiusure_a_n_barre():
    ex = NOW
    after = _serie(ex, 96, base=100.0, passo=0.1)          # sale di 0,1 a barra
    m = cattura.misure_post_uscita(after, 100.0, 100.0, 98.0, True, ex)
    assert m["post_exit_r_4b"] == pytest.approx(0.15)        # close 100,3 -> +0,15 R
    assert m["post_exit_r_16b"] == pytest.approx(0.75)
    assert m["post_exit_r_96b"] == pytest.approx(4.75)


def _tp_trade(ex: float) -> dict:
    t = _trail_trade(ex)
    t.update({"exit_reason": "take_profit", "exit_price": 110.0, "stop_price": 100.0})
    return t


def test_ogni_uscita_riceve_le_misure_solo_a_barre_complete():
    ex = NOW
    t = _tp_trade(ex)
    candles = [_c(ex - 4 * B15 + i * B15, 104.0 + 2 * i, 100.0) for i in range(4)] + \
        _serie(ex, 100, base=110.0)
    b = _bot_verdetti(t, candles)
    # prima delle 96 barre chiuse: nessuna candela scaricata per le sole misure nuove
    b.evaluate_pending_trailing(ex + 50 * B15)
    assert "interval" not in b.visto and "doc" not in b.visto
    b.evaluate_pending_trailing(ex + 98 * B15)
    doc = b.visto["doc"]
    assert doc[cattura.AT_POST] == ex + 98 * B15
    assert doc["post_exit_r_96b"] == pytest.approx(0.0)
    assert doc["post_exit_mfe_r"] == pytest.approx(0.25)
    # niente verdetti di sempre su un take_profit, e quello del gate non c'e'
    assert "trailing_verdict" not in doc and "trailing_verdict_gate" not in doc
    # il motore e' stato rigiocato sulle stesse candele
    assert doc[cattura.AT_MOTORE] == ex + 98 * B15 and doc["motore_esito"] is not None


def test_le_misure_nuove_hanno_un_budget_loro():
    ex = NOW
    trades = [dict(_tp_trade(ex), trade_id=f"t{i}") for i in range(5)]
    candles = _serie(ex - 4 * B15, 104, base=110.0)
    b = _bot_verdetti(trades[0], candles)
    b.logger.recent = lambda limit=100: trades
    chiamate = []
    b.price.get_candles = lambda s, tf, limit=200: chiamate.append(1) or candles
    b.evaluate_pending_trailing(ex + 98 * B15, max_nuovi=2)
    assert len(chiamate) == 2


# --------------------------------------------------------------------------- #
# 5) il motore rigiocato                                                       #
# --------------------------------------------------------------------------- #
def test_motore_sul_trade_e_lo_stesso_motore_dei_rifiutati(monkeypatch):
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    ex = NOW + 10 * B15
    t = _trail_trade(ex)
    t["signal_candle_ts"] = NOW                         # la candela d'ingresso apre a NOW
    candles = [_c(NOW - B15, 101.0, 99.0)] + [_c(NOW + i * B15, 101 + i, 99.5 + i) for i in range(12)]
    m = cattura.motore_sul_trade(candles, t, "15m", NOW + 20 * B15)
    atteso = simula_segnale(candles[1:], "long", 100.0, 98.0, 110.0, r_mults=[1.5, 3.0, 5.0],
                            keep=0.5, breakeven=True)
    assert m["motore_esito"] == atteso["esito"] and m["motore_pnl_r"] == atteso["pnl_r"]
    assert m["motore_barre"] == atteso["barre"] and m["motore_mfe_r"] == atteso["mfe_r"]
    assert m["bot_pnl_r_lordo"] == pytest.approx(0.5)          # 1 USDT / (2 x 1)


def test_motore_aspetta_o_rinuncia():
    t = _trail_trade(NOW + 10 * B15)
    t["signal_candle_ts"] = NOW
    # le candele non partono dalla candela d'ingresso: si aspetta
    assert cattura.motore_sul_trade([_c(NOW + B15, 101, 99)], t, "15m", NOW + 5 * B15) is None
    # ancora aperto per il motore (poche candele): si aspetta
    poche = [_c(NOW, 100.5, 99.5), _c(NOW + B15, 100.6, 99.6)]
    assert cattura.motore_sul_trade(poche, t, "15m", NOW + 5 * B15) is None
    # senza stop originale: non calcolabile, non si riprova
    senza = dict(t, orig_stop=None)
    assert cattura.motore_sul_trade(poche, senza, "15m", NOW + 5 * B15)["motore_esito"] == "non_calcolabile"


def test_cattura_dopo_uscita_chiude_cio_che_non_arrivera_mai():
    ex = NOW
    t = _tp_trade(ex)
    t["signal_candle_ts"] = NOW - 10 * B15
    # tre finestre dopo, nessuna candela utile: chiuso coi numeri a None
    assert cattura.cattura_dopo_uscita(t, [], [], [], ex + 300 * B15, "15m", B15, 96 * B15, True)
    assert t[cattura.AT_POST] and t["post_exit_mfe_r"] is None
    assert t["motore_esito"] == "non_calcolabile"
    assert cattura.pendenti(t) == set()
    # e una seconda passata non riscrive niente
    assert cattura.cattura_dopo_uscita(t, [], [], [], ex + 400 * B15, "15m", B15, 96 * B15, True) is False
