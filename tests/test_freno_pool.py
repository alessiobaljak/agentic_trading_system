"""IL FRENO PER GRUPPO CON USCITA, IL PAVIMENTO DELLA PANCHINA E LE DECLASSATE
(26 set 2026, passi 2 e 4 del piano del 26 set 15:xx).

Cosa si protegge, un pezzo per anello:
  * DRIFT: le funzioni pure (CUSUM a un lato, CUSUM di ripresa, SPRT di Wald,
    la macchina a fasi del pool) contro sequenze calcolate A MANO; le soglie
    sono costanti dichiarate nel modulo e nella configurazione, non numeri
    letti dal paper; i pool famiglia x regime e direzione x contesto BTC si
    costruiscono dai trade chiusi (R dallo stop originale, ripiego sul referto,
    altrimenti il trade si salta; «ignoto» non forma un pool); il riferimento
    e' la promessa del registro o 0.0 dichiarato;
  * il freno: `weight_factor` combina il pool col globale col MINIMO, mai col
    prodotto, e la ripresa lo toglie; `allocation` passa regime, contesto e
    direzione;
  * ORCHESTRATORE: un peso sotto soglia non rifiuta piu' ma riduce la size
    (`peso_size` = max(pavimento, peso), riga «[panchina]»); il peso 0 rifiuta
    ancora; col pavimento a 0 torna il rifiuto di prima; le classi dei motivi
    restano;
  * MAIN: il fattore delle declassate (min con l'esplorativa), il `peso_size`,
    i `size_factors`, le righe di log, il contesto BTC al freno (sul sorgente
    e con un TradingBot finto, come tests/test_paper_esplorativo.py);
  * EXECUTOR/ADAPTATION/CONTROLLO/TRADES: la marca `declassata` si persiste, si
    ripristina e arriva sul trade chiuso; `is_declassata` legge il registro,
    fail-open; `paper.declassate` nel controllo; la sezione DECLASSATE;
  * REPLAY: `scripts/replay_freno.py` con un Firebase finto: giorno
    dell'allarme contro il freno globale (dal documento o rigiocando la regola),
    PnL dopo l'allarme, ARL0 dal dataset del selettore, e uscita 0 senza dati.
"""
from __future__ import annotations

import inspect
import json
import os
import types

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient, encode_pairs
from bot.core.models import (AssetSnapshot, Direction, ExitReason, IndicatorSnapshot,
                             OrchestratorDecision, Regime)
from bot.execution.executor import ExecutionEngine
from bot.learning import drift as dr
from bot.learning.adaptation import AdaptationEngine
from bot.orchestrator.orchestrator import MOTIVI_RIFIUTO, Orchestrator, motivo_rifiuto
from scripts import replay_freno as rf
from scripts import trade_stats as ts

NOW = 1_790_000_000.0
SPEC_REV = {"id": "gen_a", "features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0}],
            "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
SPEC_MOM = {"id": "gen_m", "features": [{"kind": "ema_cross"}], "volume_mult": 0.0, "min_adx": 0.0,
            "atr_mult_stop": 1.5, "rr": 2.0}
SPECS = {"gen_a": SPEC_REV, "gen_m": SPEC_MOM}
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# --------------------------------------------------------------------------- #
# attrezzi                                                                     #
# --------------------------------------------------------------------------- #
def _t(i: int, r: float, sym="AUSDT", strat="gen_a", regime="sideways", direction="long",
       market_up=1.0, mfe=None, stop_da_referto=False, senza_stop=False, size=2.0, **extra) -> dict:
    """Un trade chiuso con R = `r` esatto: entry 100, stop originale 98 (2%),
    size 2 -> rischio 4 USDT -> pnl = 4 r. `mfe` in R (default: 2 se vince,
    0.3 se perde)."""
    t = {"trade_id": f"t{i}", "symbol": sym, "strategy": strat, "direction": direction,
         "entry_price": 100.0, "exit_price": 100.0 + 2.0 * r, "size": size, "pnl": 4.0 * r,
         "pnl_pct": 0.02 * r, "exit_reason": "stop_loss" if r < 0 else "take_profit",
         "regime_at_entry": regime, "exit_ts": NOW - (200 - i) * 3600.0,
         "mfe_r": (2.0 if r > 0 else 0.3) if mfe is None else mfe,
         "scale_r_mults": [1.5, 3.0, 5.0], "timeframe": settings.ORCHESTRATOR_TIMEFRAME,
         "feats_at_entry": {"market_up": market_up}}
    if not senza_stop:
        if stop_da_referto:
            t["post_mortem"] = {"stop_pct": 0.02}
        else:
            t["orig_stop"] = 98.0 if direction == "long" else 102.0
    t.update(extra)
    return t


def _pairs(pf=1.5, wr=0.5, **extra) -> dict:
    return {"AUSDT|gen_a": {"last_pf": pf, "last_win_rate": wr, "pass_count": 3, **extra}}


def _doc_pool(chiave="fam:reversion|sideways", allarme=True, ripresa=False, globale=False) -> dict:
    return {"global": {"verdict": "drift" if globale else "ok"},
            "pool": {chiave: {"allarme": allarme, "ripresa": ripresa, "n": 6}},
            "pool_famiglie": {"gen_a": "reversion"}}


@pytest.fixture
def freni(monkeypatch):
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    monkeypatch.setattr(settings, "POOL_BRAKE_ENABLED", True)
    monkeypatch.setattr(settings, "POOL_BRAKE_FACTOR", 0.5)
    monkeypatch.setattr(settings, "DRIFT_WEIGHT_FACTOR", 0.5)
    monkeypatch.setattr(settings, "DRIFT_WEIGHT_FLOOR", 0.25)
    monkeypatch.setattr(settings, "STREAK_BRAKE_ENABLED", False)
    monkeypatch.setattr(settings, "POOL_CUSUM_H", 4.0)
    monkeypatch.setattr(settings, "POOL_CUSUM_RIPRESA", 2.5)


# --------------------------------------------------------------------------- #
# 1. le funzioni pure, contro sequenze calcolate a mano                        #
# --------------------------------------------------------------------------- #
def test_cusum_a_un_lato_a_mano():
    # riferimento 0.2: quattro trade a -1R = deficit 1.2 l'uno -> 1.2, 2.4, 3.6, 4.8 >= 4 (indice 3);
    # poi +0.5R: 4.8 + (0.2 - 0.5) = 4.5
    assert dr.cusum_r([-1, -1, -1, -1, 0.5], 0.2) == (True, 4.5, 3)
    # sopra il riferimento la statistica torna a zero e non suona: 0, 0.7, 0.4
    assert dr.cusum_r([0.5, -0.5, 0.5], 0.2) == (False, 0.4, None)
    # la tolleranza k toglie a ogni passo: 0.7, 1.4, 2.1, 2.8 < 4
    assert dr.cusum_r([-1] * 4, 0.2, k=0.5) == (False, 2.8, None)
    # h piu' basso suona prima (indice 1: 1.2 + 1.2 = 2.4 >= 2)
    assert dr.cusum_r([-1] * 4, 0.2, h=2.0)[2] == 1
    assert dr.cusum_r([], 0.2) == (False, 0.0, None)


def test_cusum_di_ripresa_a_mano():
    # +1R quattro volte sopra 0.2: 0.8, 1.6, 2.4, 3.2 >= 2.5 all'indice 3
    assert dr.cusum_ripresa([1, 1, 1, 1], 0.2) == (True, 3.2, 3)
    # 0.3 poi 0.1: non si riprende
    assert dr.cusum_ripresa([0.5, 0.0], 0.2) == (False, 0.1, None)


def test_sprt_di_wald_a_mano():
    # miss: log(0.75/0.55) = +0.3102; A = log(19) = 2.944 -> 10 miss = 3.10 >= A: reject all'indice 9
    esito, llr, idx = dr.sprt_tp1([False] * 12)
    assert (esito, idx) == ("reject", 9) and llr == pytest.approx(3.1015, abs=1e-3)
    # hit: log(0.25/0.45) = -0.5878; 5 hit = -2.939 > B = -2.944, 6 hit = -3.527 <= B: accept all'indice 5
    esito, llr, idx = dr.sprt_tp1([True] * 8)
    assert (esito, idx) == ("accept", 5) and llr == pytest.approx(-3.5267, abs=1e-3)
    # alternati: resta in mezzo
    assert dr.sprt_tp1([True, False] * 3)[0] == "continue"
    # decisa una volta, la decisione resta (e' un SPRT, non una finestra scorrevole)
    assert dr.sprt_tp1([False] * 10 + [True] * 20) == ("reject", pytest.approx(3.1015, abs=1e-3), 9)
    # ipotesi degeneri: nessuna decisione
    assert dr.sprt_tp1([False] * 50, p0=0.25, p1=0.45) == ("continue", 0.0, None)


def test_la_macchina_a_fasi_del_pool_allarme_ripresa_e_secondo_allarme():
    st = dr.stato_pool([-1, -1, -1, -1, 1, 1, 1, 1, 0.0], 0.2)
    assert st["allarme"] and st["ripresa"] and st["indice_allarme"] == 3 and st["indice_ripresa"] == 7
    assert st["allarmi"] == 1 and st["cusum"] == pytest.approx(0.2)       # ripartita da zero dopo la ripresa
    st = dr.stato_pool([-1] * 4, 0.2)
    assert st["allarme"] and not st["ripresa"] and st["cusum_ripresa"] == 0.0
    st = dr.stato_pool([-1] * 4 + [1] * 4 + [-1] * 4, 0.2)
    assert st["allarmi"] == 2 and st["allarme"] and not st["ripresa"] and st["indice_allarme"] == 11
    assert dr.stato_pool([], 0.2) == {"allarme": False, "ripresa": False, "cusum": 0.0, "cusum_ripresa": 0.0,
                                      "indice_allarme": None, "indice_ripresa": None, "allarmi": 0}


def test_le_soglie_sono_costanti_dichiarate_nel_modulo_e_nella_config():
    assert (dr.CUSUM_H, dr.CUSUM_K, dr.CUSUM_RIPRESA) == (4.0, 0.0, 2.5)
    assert (dr.SPRT_P0, dr.SPRT_P1, dr.SPRT_ALPHA, dr.SPRT_BETA) == (0.45, 0.25, 0.05, 0.05)
    assert dr.POOL_GIORNI == 30
    assert settings.POOL_BRAKE_ENABLED is True and settings.POOL_BRAKE_FACTOR == 0.5
    assert settings.POOL_CUSUM_H == 4.0 and settings.POOL_CUSUM_RIPRESA == 2.5
    assert settings.POOL_SPRT_P0 == 0.45 and settings.POOL_SPRT_P1 == 0.25
    assert settings.PANCHINA_PAVIMENTO == 0.25
    assert settings.DECLASSATE_ENABLED is True and settings.DECLASSATA_SIZE_MULT == 0.25
    assert settings.DECLASSATA_NOTTI == 2
    # le funzioni pure hanno i default del modulo, non leggono il paper
    assert inspect.signature(dr.cusum_r).parameters["h"].default == 4.0
    assert inspect.signature(dr.sprt_tp1).parameters["p1"].default == 0.25


# --------------------------------------------------------------------------- #
# 2. R, TP1, contesto, chiavi                                                  #
# --------------------------------------------------------------------------- #
def test_r_dallo_stop_originale_ripiego_sul_referto_altrimenti_si_salta():
    assert dr.r_multiplo(_t(0, -1.0)) == pytest.approx(-1.0)
    assert dr.r_multiplo(_t(0, 2.5, stop_da_referto=True)) == pytest.approx(2.5)
    # short col referto: stop sopra l'entry
    s = _t(0, -1.0, direction="short", stop_da_referto=True)
    assert dr.stop_originale(s) == pytest.approx(102.0) and dr.r_multiplo(s) == pytest.approx(-1.0)
    assert dr.r_multiplo(_t(0, -1.0, senza_stop=True)) is None
    assert dr.r_multiplo(_t(0, -1.0, size=0.0)) is None
    assert dr.stop_originale({"entry_price": 0}) is None
    assert dr.stop_originale({"entry_price": 100.0, "stop_price": 98.0}) is None   # stop finale: NON vale


def test_tocca_tp1_e_contesto_btc():
    assert dr.tocca_tp1(_t(0, 1.0, mfe=1.6)) is True
    assert dr.tocca_tp1(_t(0, 1.0, mfe=1.4)) is False
    assert dr.tocca_tp1({"mfe_r": None}) is None
    assert dr.tocca_tp1({"mfe_r": 1.6}) is (min(settings.SCALE_OUT_R_MULTIPLES) <= 1.6)
    assert dr.contesto_btc(1.0) == "btc_su" and dr.contesto_btc(0) == "btc_giu"
    assert dr.contesto_btc(None) is None and dr.contesto_btc("x") is None


def test_le_chiavi_dei_pool_e_la_famiglia():
    fam = {"gen_a": "reversion"}
    assert dr.chiavi_pool(_t(0, 1.0), fam) == ["fam:reversion|sideways", "dir:long|btc_su"]
    assert dr.chiavi_pool(_t(0, 1.0, market_up=None), fam) == ["fam:reversion|sideways"]   # ignoto: fuori
    assert dr.chiavi_pool(_t(0, 1.0, strat="zz", regime="Regime.BULL_TRENDING", direction="short",
                             market_up=0), fam) == ["fam:altro|bull_trending", "dir:short|btc_giu"]
    assert dr.chiavi_pool({"strategy": "gen_a"}, fam) == []
    assert dr.famiglia_di("gen_a", SPECS) == "reversion" and dr.famiglia_di("gen_m", SPECS) == "momentum"
    assert dr.famiglia_di("mean_reversion", SPECS) == "altro" and dr.famiglia_di("x", None) == "altro"
    assert dr.chiave_pool_famiglia("reversion", Regime.SIDEWAYS) == "fam:reversion|sideways"
    assert dr.chiave_pool_famiglia("reversion", None) is None
    assert dr.chiave_pool_direzione(Direction.LONG, 1.0) == "dir:long|btc_su"
    assert dr.chiave_pool_direzione("short", "btc_giu") == "dir:short|btc_giu"
    assert dr.chiave_pool_direzione("long", None) is None and dr.chiave_pool_direzione(None, 1.0) is None


def test_il_riferimento_viene_dalla_promessa_del_registro_o_e_zero_dichiarato():
    # (1 - wr) * (PF - 1): 0.5 * 0.5 = 0.25
    assert dr.expectancy_r({"last_pf": 1.5, "last_win_rate": 0.5}) == pytest.approx(0.25)
    assert dr.expectancy_r({"last_pf": 1.5}) is None and dr.expectancy_r({"last_win_rate": 0.5}) is None
    fam = {"gen_a": "reversion", "gen_m": "momentum"}
    pairs = {"AUSDT|gen_a": {"last_pf": 1.5, "last_win_rate": 0.5},
             "BUSDT|gen_m": {"last_pf": 2.0, "last_win_rate": 0.5}, "CUSDT|gen_a": {"last_pf": 1.2}}
    rif, nota, n = dr.riferimento_pool("fam:reversion|sideways", pairs, fam)
    assert (rif, n) == (0.25, 1) and "validate del pool" in nota
    rif, nota, n = dr.riferimento_pool("dir:long|btc_su", pairs, fam)   # tutte le coppie
    assert (rif, n) == (pytest.approx(0.375), 2)
    rif, nota, n = dr.riferimento_pool("fam:breakout|sideways", pairs, fam)
    assert (rif, n) == (0.0, 0) and "non derivabile" in nota
    # solo le validate se la lista c'e'
    assert dr.riferimento_pool("dir:long|btc_su", pairs, fam, validated=["AUSDT|gen_a"])[:2][0] == 0.25


# --------------------------------------------------------------------------- #
# 3. compute_drift: i pool                                                      #
# --------------------------------------------------------------------------- #
def test_compute_drift_costruisce_i_pool_e_l_allarme_scatta_al_quarto_stop(freni):
    trades = [_t(i, -1.0) for i in range(6)]          # riferimento 0.25 -> deficit 1.25: suona al 4°
    doc = dr.compute_drift(trades, _pairs(), specs=SPECS, validated=["AUSDT|gen_a"], now=NOW)
    assert set(doc["pool"]) == {"fam:reversion|sideways", "dir:long|btc_su"}
    p = doc["pool"]["fam:reversion|sideways"]
    assert p["n"] == 6 and p["r_medio"] == -1.0 and p["allarme"] and not p["ripresa"]
    assert p["dal"] == trades[3]["exit_ts"] and p["riferimento"] == 0.25 and p["coppie_riferimento"] == 1
    # all'allarme (5.0 = 4 x 1.25) la statistica si ferma: da li' conta quella di ripresa
    assert p["cusum"] == pytest.approx(5.0) and p["cusum_ripresa"] == 0.0 and p["allarmi"] == 1
    assert p["sprt"] == "continue" and p["tp1_n"] == 6 and p["tp1_hit"] == 0
    assert doc["pool_famiglie"]["gen_a"] == "reversion"
    # le altre granularita' restano com'erano
    assert set(doc) == {"pairs", "strategies", "global", "serie", "pool", "pool_famiglie"}
    # e la ripresa: quattro vincite da +1R dopo l'allarme (0.75 l'una: 3.0 >= 2.5)
    doc = dr.compute_drift(trades + [_t(10 + i, 1.0) for i in range(4)], _pairs(), specs=SPECS, now=NOW)
    p = doc["pool"]["fam:reversion|sideways"]
    assert p["allarme"] and p["ripresa"] and p["n"] == 10


def test_i_pool_saltano_i_trade_senza_r_gli_esplorativi_i_vecchi_e_l_ignoto(freni):
    trades = ([_t(i, -1.0, senza_stop=True) for i in range(3)]              # niente R
              + [_t(10 + i, -1.0, esplorativa=True) for i in range(5)]       # fuori dal learning
              + [_t(20, -1.0, exit_ts=NOW - 40 * 86400.0)]                   # oltre i 30 giorni
              + [_t(30 + i, -1.0, market_up=None) for i in range(2)])        # solo il pool famiglia
    doc = dr.compute_drift(trades, _pairs(), specs=SPECS, now=NOW)
    assert set(doc["pool"]) == {"fam:reversion|sideways"}
    assert doc["pool"]["fam:reversion|sideways"]["n"] == 2
    assert dr.compute_drift([], _pairs(), now=NOW)["pool"] == {}
    # senza spec la famiglia e' «altro» e il riferimento 0.0 dichiarato
    doc = dr.compute_drift([_t(i, -1.0) for i in range(2)], {"AUSDT|gen_a": {"last_pf": 1.5}}, now=NOW)
    p = doc["pool"]["fam:altro|sideways"]
    assert p["riferimento"] == 0.0 and "non derivabile" in p["riferimento_nota"]


def test_un_errore_nei_pool_non_ferma_la_deriva(freni, monkeypatch, capsys):
    monkeypatch.setattr(dr, "compute_pools", lambda *a, **k: 1 / 0)
    doc = dr.compute_drift([_t(i, -1.0) for i in range(10)], _pairs(), now=NOW)
    assert doc["pool"] == {} and doc["pairs"]["AUSDT|gen_a"]["trades"] == 10
    assert "pool saltati" in capsys.readouterr().out


# --------------------------------------------------------------------------- #
# 4. il freno: MINIMO col globale, ripresa, interruttore, motivi, allocation     #
# --------------------------------------------------------------------------- #
def test_weight_factor_combina_il_pool_col_globale_col_minimo_mai_col_prodotto(freni, monkeypatch):
    doc = _doc_pool(globale=True)
    assert dr.weight_factor(doc, "AUSDT", "gen_a", regime=Regime.SIDEWAYS) == pytest.approx(0.5)   # non 0.25
    assert dr.weight_factor(_doc_pool(), "AUSDT", "gen_a", regime=Regime.SIDEWAYS) == pytest.approx(0.5)
    monkeypatch.setattr(settings, "POOL_BRAKE_FACTOR", 0.3)
    assert dr.weight_factor(doc, "AUSDT", "gen_a", regime="sideways") == pytest.approx(0.3)   # il minimo
    # il pavimento vale anche qui: coppia + strategia in deriva (0.25) e pool -> 0.25
    doc2 = {**_doc_pool(), "pairs": {"AUSDT|gen_a": {"verdict": "drift"}},
            "strategies": {"gen_a": {"verdict": "drift"}}}
    assert dr.weight_factor(doc2, "AUSDT", "gen_a", regime=Regime.SIDEWAYS) == pytest.approx(0.25)


def test_la_ripresa_toglie_il_freno_e_il_pool_giusto_e_quello_della_decisione(freni, monkeypatch):
    assert dr.weight_factor(_doc_pool(ripresa=True), "AUSDT", "gen_a", regime=Regime.SIDEWAYS) == 1.0
    assert dr.weight_factor(_doc_pool(allarme=False), "AUSDT", "gen_a", regime=Regime.SIDEWAYS) == 1.0
    # regime diverso, strategia di un'altra famiglia, regime ignoto: nessun freno
    assert dr.weight_factor(_doc_pool(), "AUSDT", "gen_a", regime=Regime.BULL_TRENDING) == 1.0
    assert dr.weight_factor(_doc_pool(), "AUSDT", "gen_zz", regime=Regime.SIDEWAYS) == 1.0
    assert dr.weight_factor(_doc_pool(), "AUSDT", "gen_a") == 1.0
    # il pool direzione x contesto
    doc = _doc_pool(chiave="dir:short|btc_su")
    assert dr.weight_factor(doc, "X", "y", contesto=1.0, direzione="short") == pytest.approx(0.5)
    assert dr.weight_factor(doc, "X", "y", contesto=0.0, direzione="short") == 1.0
    assert dr.weight_factor(doc, "X", "y", contesto=None, direzione="short") == 1.0
    assert dr.weight_factor(doc, "X", "y", contesto=1.0, direzione=Direction.LONG) == 1.0
    # interruttori: pool spento, deriva spenta, documento senza pool
    monkeypatch.setattr(settings, "POOL_BRAKE_ENABLED", False)
    assert dr.weight_factor(_doc_pool(), "AUSDT", "gen_a", regime=Regime.SIDEWAYS) == 1.0
    monkeypatch.setattr(settings, "POOL_BRAKE_ENABLED", True)
    monkeypatch.setattr(settings, "DRIFT_ENABLED", False)
    assert dr.weight_factor(_doc_pool(), "AUSDT", "gen_a", regime=Regime.SIDEWAYS) == 1.0
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    assert dr.weight_factor({"global": {"verdict": "ok"}}, "AUSDT", "gen_a", regime=Regime.SIDEWAYS) == 1.0


def test_i_motivi_nominano_il_pool_e_allocation_passa_regime_contesto_direzione(freni):
    doc = {**_doc_pool(globale=True), "pool": {**_doc_pool()["pool"],
                                              "dir:long|btc_su": {"allarme": True, "ripresa": False}}}
    assert dr.motivi_freno(doc, "AUSDT", "gen_a", regime=Regime.SIDEWAYS, contesto=1.0, direzione="long") == [
        "pool fam:reversion|sideways", "pool dir:long|btc_su", "deriva globale"]
    assert dr.motivi_freno(doc, "AUSDT", "gen_a") == ["deriva globale"]
    a = AdaptationEngine(FirebaseClient())
    a._drift = _doc_pool()
    r0, l0, _ = a.allocation("gen_a", Regime.SIDEWAYS, 60.0)
    r, l, nota = a.allocation("gen_a", Regime.SIDEWAYS, 60.0, drift_key=("AUSDT", "gen_a"))
    assert r == pytest.approx(r0 * 0.5) and l < l0 and "FRENO x0.50 (pool fam:reversion|sideways)" in nota
    a._drift = _doc_pool(chiave="dir:long|btc_su")
    r, _l, nota = a.allocation("gen_a", Regime.SIDEWAYS, 60.0, drift_key=("AUSDT", "gen_a"),
                               contesto=1.0, direzione="long")
    assert r == pytest.approx(r0 * 0.5) and "pool dir:long|btc_su" in nota
    r, _l, nota = a.allocation("gen_a", Regime.SIDEWAYS, 60.0, drift_key=("AUSDT", "gen_a"))
    assert r == pytest.approx(r0) and "FRENO" not in nota


# --------------------------------------------------------------------------- #
# 5. l'orchestratore: il pavimento della panchina                               #
# --------------------------------------------------------------------------- #
def _asset(sym="BTCUSDT") -> AssetSnapshot:
    ind = IndicatorSnapshot(timeframe="15m", rsi=20.0, atr=2.0, close=94.0,
                            bb_lower=95.0, bb_upper=105.0, bb_mid=100.0)
    return AssetSnapshot(symbol=sym, price=94.0, regime=Regime.SIDEWAYS, indicators={"15m": ind})


def _orch(symbols, peso) -> Orchestrator:
    o = Orchestrator()
    o.adaptation._passed = {f"{s}|mean_reversion" for s in symbols}
    o.adaptation._has_opt_data = True
    o.adaptation._weights = {f"mean_reversion|{r.value}": peso for r in Regime}
    return o


def test_un_peso_sotto_soglia_riduce_la_size_invece_di_rifiutare(monkeypatch, capsys):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "PANCHINA_PAVIMENTO", 0.25)
    o = _orch(["BTCUSDT"], 0.3)                       # conf 65 x 0.3 = 19.5 < 30
    dec = o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS)
    assert len(dec) == 1 and dec[0].peso_size == pytest.approx(0.3)
    assert dec[0].size_multiplier == 1.0             # il tilt resta a parte, non si moltiplica qui
    out = capsys.readouterr().out
    assert "[panchina] BTCUSDT mean_reversion: peso 0.30 -> size x0.30" in out
    assert "[rifiuto]" not in out and o.rifiuti_ciclo() == []
    # sotto il pavimento vale il pavimento
    o = _orch(["BTCUSDT"], 0.1)
    assert o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS)[0].peso_size == pytest.approx(0.25)
    assert "peso 0.10 -> size x0.25" in capsys.readouterr().out
    # sopra soglia: nessun peso_size, nessuna riga
    o = _orch(["BTCUSDT"], 1.0)
    assert o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS)[0].peso_size is None
    assert "[panchina]" not in capsys.readouterr().out


def test_il_peso_zero_rifiuta_ancora_e_col_pavimento_a_zero_torna_il_rifiuto(monkeypatch, capsys):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    o = _orch(["BTCUSDT"], 0.0)
    assert o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS) == []
    assert "spenta" in capsys.readouterr().out and o.rifiuti_ciclo() == [{"motivo": "strategia spenta", "n": 1}]
    monkeypatch.setattr(settings, "PANCHINA_PAVIMENTO", 0.0)
    o = _orch(["BTCUSDT"], 0.3)
    assert o.decide_all({"BTCUSDT": _asset()}, Regime.SIDEWAYS) == []
    assert "[rifiuto] BTCUSDT mean_reversion: peso 0.30" in capsys.readouterr().out
    assert o.rifiuti_ciclo() == [{"motivo": "peso sotto soglia", "n": 1}]
    # le classi dei motivi restano tutte
    assert "peso sotto soglia" in MOTIVI_RIFIUTO and "strategia spenta" in MOTIVI_RIFIUTO
    assert motivo_rifiuto("peso 0.30: confidenza 19 < soglia 30") == "peso sotto soglia"


def test_le_righe_panchina_hanno_il_tetto_e_non_si_accumulano(monkeypatch, capsys):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    syms = [f"C{i:02d}USDT" for i in range(25)]
    o = _orch(syms, 0.3)
    assert len(o.decide_all({s: _asset(s) for s in syms}, Regime.SIDEWAYS)) == 25
    righe = [r for r in capsys.readouterr().out.splitlines() if r.startswith("[panchina]")]
    assert len(righe) == 21 and righe[-1] == "[panchina] ... e altri 5"
    o.decide_all({"C00USDT": _asset("C00USDT")}, Regime.SIDEWAYS)
    assert len([r for r in capsys.readouterr().out.splitlines() if r.startswith("[panchina]")]) == 1


def test_la_validata_in_panchina_vince_ancora_sull_esplorativa(monkeypatch, capsys):
    from tests.test_paper_esplorativo import _orch as _orch_esp
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "DRY_RUN", True)
    o = _orch_esp({"BTCUSDT": {"mean_reversion"}}, ["BTCUSDT|gen_x"])
    o.adaptation._weights = {f"mean_reversion|{r.value}": 0.3 for r in Regime}
    dec = o.decide_all({"BTCUSDT": _asset("BTCUSDT")}, Regime.SIDEWAYS)
    assert [(d.strategy, d.esplorativa, d.peso_size) for d in dec] == [("mean_reversion", False, 0.3)]


# --------------------------------------------------------------------------- #
# 6. main: fattori di size, righe, contesto (sorgente + TradingBot finto)       #
# --------------------------------------------------------------------------- #
def test_il_sorgente_di_main_applica_declassata_peso_size_e_passa_il_contesto():
    from bot import main as bot_main
    src = inspect.getsource(bot_main.TradingBot._try_open)
    assert "rmult *= _f_rid" in src and "_f_rid = min(_f_esp, _f_dec)" in src
    assert "fattore_size_declassata(decision, self.adaptation)" in src
    assert "declassata=bool(_declassata)" in src and "[declassata]" in src
    assert "_peso_size = getattr(decision, \"peso_size\", None)" in src and "panchina x" in src
    assert "contesto=contesto_btc(getattr(self, \"_btc_snap\", None))" in src
    assert "direzione=decision.direction.value" in src
    assert "f_declassata=_f_dec, peso_size=_peso_size" in src
    src_d = inspect.getsource(bot_main.TradingBot._publish_drift)
    assert "specs=getattr(self.adaptation, \"_generated_specs\", None)" in src_d
    assert "validated=reg.get(\"validated\") or None" in src_d
    # il contesto BTC ha la stessa regola del gate: EMA veloce > lenta a 1h
    snap = AssetSnapshot(symbol="BTCUSDT", price=1.0, regime=Regime.SIDEWAYS,
                         indicators={"1h": IndicatorSnapshot(timeframe="1h", ema_fast=2.0, ema_slow=1.0)})
    assert bot_main.contesto_btc(snap) == 1.0
    snap.indicators["1h"].ema_fast = 0.5
    assert bot_main.contesto_btc(snap) == 0.0
    assert bot_main.contesto_btc(None) is None
    assert bot_main.contesto_btc(AssetSnapshot(symbol="BTCUSDT", price=1.0, regime=Regime.SIDEWAYS)) is None
    f = bot_main.fattori_size(OrchestratorDecision(asset="A", strategy="s", direction=Direction.LONG,
                                                   size_multiplier=1.0, confidence=60.0),
                              1.0, 1.0, "n", types.SimpleNamespace(), f_declassata=0.25, peso_size=0.3)
    assert f["declassata"] == 0.25 and f["peso_size"] == 0.3
    assert bot_main.fattori_size(None, 1.0, 1.0, "n", None)["peso_size"] is None


def _bot_pool(monkeypatch):
    """Il TradingBot finto di tests/test_paper_esplorativo.py: il fattore delle
    declassate e' una funzione di modulo, quindi non c'e' niente da legare."""
    from tests.test_paper_esplorativo import _bot
    b = _bot(monkeypatch)
    monkeypatch.setattr(settings, "DECLASSATE_ENABLED", True)
    monkeypatch.setattr(settings, "DECLASSATA_SIZE_MULT", 0.25)
    return b


def _decision(esplorativa=False, peso_size=None) -> OrchestratorDecision:
    return OrchestratorDecision(asset="BTCUSDT", strategy="gen_x", direction=Direction.LONG,
                                size_multiplier=1.0, confidence=60.0, esplorativa=esplorativa,
                                peso_size=peso_size)


def test_una_declassata_apre_a_un_quarto_marcata_e_con_la_riga(monkeypatch, capsys):
    b = _bot_pool(monkeypatch)
    b.adaptation.is_declassata = lambda sym, st: (sym, st) == ("BTCUSDT", "gen_x")
    b._try_open(_decision(), NOW)
    assert b.visto["risk_mult"] == pytest.approx(0.25) and "declassata x0.25" in b.visto["alloc_note"]
    assert b.visto["open"]["declassata"] is True and b.visto["open"]["esplorativa"] is False
    assert b.visto["open"]["size_factors"]["declassata"] == 0.25
    assert "[declassata] BTCUSDT gen_x long size x0.25" in capsys.readouterr().out


def test_una_validata_attiva_apre_piena_e_senza_metodo_o_spenta_e_fail_open(monkeypatch, capsys):
    b = _bot_pool(monkeypatch)                        # adaptation senza is_declassata
    b._try_open(_decision(), NOW)
    assert b.visto["risk_mult"] == 1.0 and b.visto["open"]["declassata"] is False
    assert "[declassata]" not in capsys.readouterr().out
    b.adaptation.is_declassata = lambda sym, st: 1 / 0
    b._try_open(_decision(), NOW)
    assert b.visto["risk_mult"] == 1.0
    b.adaptation.is_declassata = lambda sym, st: True
    monkeypatch.setattr(settings, "DECLASSATE_ENABLED", False)
    b._try_open(_decision(), NOW)
    assert b.visto["risk_mult"] == 1.0 and b.visto["open"]["declassata"] is False


def test_esplorativa_e_declassata_insieme_valgono_il_minimo_mai_il_prodotto(monkeypatch):
    b = _bot_pool(monkeypatch)
    # un'esplorativa non e' mai declassata (non e' validata): resta il quarto dell'esplorativa
    b.adaptation.is_declassata = lambda sym, st: True
    b._try_open(_decision(esplorativa=True), NOW)
    assert b.visto["risk_mult"] == pytest.approx(0.25) and b.visto["open"]["declassata"] is False
    # se mai lo fossero entrambe: il minimo (0.1), non 0.025
    from bot import main as bot_main
    monkeypatch.setattr(bot_main, "fattore_size_declassata", lambda d, a: (0.1, True))
    b._try_open(_decision(esplorativa=True), NOW)
    assert b.visto["risk_mult"] == pytest.approx(0.1)
    assert "esplorativa x0.25" in b.visto["alloc_note"] and "declassata x0.1" in b.visto["alloc_note"]


def test_il_peso_size_della_panchina_si_applica_alla_size_e_finisce_nei_fattori(monkeypatch):
    b = _bot_pool(monkeypatch)
    b._try_open(_decision(peso_size=0.3), NOW)
    assert b.visto["risk_mult"] == pytest.approx(0.3) and "panchina x0.30" in b.visto["alloc_note"]
    assert b.visto["open"]["size_factors"]["peso_size"] == 0.3
    b._try_open(_decision(), NOW)
    assert b.visto["risk_mult"] == 1.0 and b.visto["open"]["size_factors"]["peso_size"] is None


# --------------------------------------------------------------------------- #
# 7. executor, adaptation, controllo, trades                                    #
# --------------------------------------------------------------------------- #
def test_la_marca_declassata_si_persiste_si_ripristina_e_arriva_sul_trade_chiuso():
    from tests.test_paper_esplorativo import _params
    fb = FirebaseClient()
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    asset = AssetSnapshot(symbol="BTCUSDT", price=100.0, regime=Regime.SIDEWAYS,
                          indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=2.0, close=100.0)})
    pos = eng.open_position(asset, "gen_x", Direction.LONG, _params(), declassata=True)
    assert pos.declassata is True and pos.esplorativa is False
    assert fb.get_rtdb("/positions/BTCUSDT")["declassata"] is True
    eng2 = ExecutionEngine(firebase=fb, dry_run=True)
    eng2.restore_open_positions()
    assert eng2.open_positions["BTCUSDT"].declassata is True
    stato = dict(fb.get_rtdb("/positions/BTCUSDT"))
    stato.pop("declassata")
    assert eng2._position_from_state(stato).declassata is False
    ct = eng2._build_closed_trade(eng2.open_positions["BTCUSDT"], 104.0, ExitReason.TAKE_PROFIT)
    assert ct.declassata is True and ct.esplorativa is False
    pos_v = eng.open_position(AssetSnapshot(symbol="ETHUSDT", price=100.0, regime=Regime.SIDEWAYS),
                              "gen_a", Direction.LONG, _params())
    assert pos_v.declassata is False
    assert eng._build_closed_trade(pos_v, 98.0, ExitReason.STOP_LOSS).declassata is False
    assert OrchestratorDecision(asset="X", strategy="s", direction=Direction.LONG, size_multiplier=1,
                                confidence=50).peso_size is None


def test_adaptation_legge_le_declassate_dal_registro_ogni_ricarica_fail_open(monkeypatch):
    monkeypatch.setattr(settings, "DECLASSATE_ENABLED", True)
    fb = FirebaseClient()
    pairs = {"AUSDT|gen_a": {"pass_count": 3, "declassata": True, "declassata_at": NOW, "bocciata_notti": 2},
             "BUSDT|gen_b": {"pass_count": 3, "declassata": False, "bocciata_notti": 1},
             "CUSDT|gen_c": {"pass_count": 3}}
    fb.set_doc("strategy_registry", "validated", {"ready": True, "validated": list(pairs),
                                                  "pairs": encode_pairs(pairs)})
    a = AdaptationEngine(fb)
    assert a.is_declassata("AUSDT", "gen_a") is True
    assert a.is_declassata("BUSDT", "gen_b") is False and a.is_declassata("CUSDT", "gen_c") is False
    assert a.is_declassata("ZUSDT", "gen_a") is False
    # il gate la rimette piena: la ricarica oraria lo vede
    pairs["AUSDT|gen_a"]["declassata"] = False
    fb.set_doc("strategy_registry", "validated", {"ready": True, "validated": list(pairs),
                                                  "pairs": encode_pairs(pairs)})
    a.load_params()
    assert a.is_declassata("AUSDT", "gen_a") is False
    monkeypatch.setattr(settings, "DECLASSATE_ENABLED", False)
    a._declassate = {"AUSDT|gen_a"}
    assert a.is_declassata("AUSDT", "gen_a") is False
    # registro assente: nessuna declassata, nessuna eccezione
    assert AdaptationEngine(FirebaseClient())._declassate == set()


def test_il_controllo_conta_le_declassate_a_parte_ma_dentro_le_validate():
    from bot.learning import controllo as c
    from tests.test_controllo import NOW as NOW_C
    from tests.test_controllo import _fb, _trade
    validate = [_trade(i, 5.0 if i % 3 else -4.0) for i in range(6)]
    declassate = [_trade(10 + i, -3.0, sym="DUSDT", strat="gen_d", declassata=True) for i in range(2)]
    fb = _fb(trades=validate + declassate)
    fb.set_rtdb("/positions/DUSDT", {"symbol": "DUSDT", "strategy": "gen_d", "direction": "long",
                                     "entry_price": 1.0, "quantity": 1.0, "leverage": 2.0,
                                     "unrealized_pnl": 0.0, "realized_partial": 0.0,
                                     "risk_effective_pct": 0.001, "declassata": True})
    doc = c.costruisci_controllo(c.carica_dati(fb, NOW_C), NOW_C, "bot", settings_da_bot=True, durata_ms=10)
    p = doc["paper"]
    assert p["declassate"] == {"trades": 2, "pnl": -6.0, "aperte": 1}
    assert p["trades"] == 8                                   # restano fra le validate
    p2 = c.costruisci_controllo(c.carica_dati(_fb(trades=validate), NOW_C), NOW_C, "bot", True, 10)["paper"]
    assert p2["declassate"] == {"trades": 0, "pnl": 0.0, "aperte": 0}


def test_trade_stats_stampa_le_declassate_contro_le_attive(capsys):
    trades = [_t(i, -1.0, declassata=True) for i in range(3)] + [_t(10 + i, 2.0) for i in range(2)]
    trades.append(_t(20, 1.0, esplorativa=True))                 # fuori
    trades.append(_t(21, 1.0, senza_stop=True))                  # attiva senza R
    rep = ts.declassate_report(trades)
    assert rep["declassate"] == {"trades": 3, "vinti": 0, "pnl": -12.0, "r_medio": -1.0, "r_n": 3}
    assert rep["attive"] == {"trades": 3, "vinti": 3, "pnl": 20.0, "r_medio": 2.0, "r_n": 2}
    ts.print_declassate(rep)
    out = capsys.readouterr().out
    assert "DECLASSATE" in out and "3 trade · 0 vinti · PnL -12.00 · R medio -1.000R su 3" in out
    assert "3 trade · 3 vinti · PnL +20.00 · R medio +2.000R su 2" in out
    ts.print_declassate(ts.declassate_report([]))
    assert "nessun trade chiuso da una declassata" in capsys.readouterr().out
    assert "print_declassate(declassate_report(trades))" in inspect.getsource(ts.main)


# --------------------------------------------------------------------------- #
# 8. il replay, con un Firebase finto                                           #
# --------------------------------------------------------------------------- #
def _fb_replay(trades, drift_doc=None, pairs=None) -> FirebaseClient:
    fb = FirebaseClient()
    for t in trades:
        fb.set_doc("trades", t["trade_id"], t)
    pairs = _pairs() if pairs is None else pairs
    fb.set_doc("strategy_registry", "validated", {"ready": True, "validated": list(pairs),
                                                  "pairs": encode_pairs(pairs)})
    fb.set_doc("discovered_strategies", "specs", {"specs": encode_pairs(SPECS)})
    if drift_doc is not None:
        fb.set_doc("drift", "current", drift_doc)
    return fb


def test_il_replay_dice_quando_il_pool_avrebbe_suonato_contro_il_globale(monkeypatch, capsys):
    # 6 stop poi 3 vincite: il CUSUM suona al 4° (indice 3); nei 7 giorni dopo il pool perde ancora 2 e vince 3
    trades = [_t(i, -1.0) for i in range(6)] + [_t(6 + i, 1.5) for i in range(3)]
    dal = trades[5]["exit_ts"]        # il globale «si accende» al 6° trade: il pool suona 2 trade prima
    fb = _fb_replay(trades, {"global": {"verdict": "drift", "dal": dal}})
    monkeypatch.setattr(rf, "get_firebase", lambda: fb)
    assert rf.main([]) == 0
    out = capsys.readouterr().out
    assert "trade del paper: 9" in out and "fonte: drift/current.global.dal" in out
    assert "fam:reversion|sideways" in out and "dir:long|btc_su" in out
    riga = next(r for r in out.splitlines() if r.strip().startswith("fam:reversion|sideways"))
    assert rf._giorno(trades[3]["exit_ts"]) in riga and "PRIMA" in riga
    assert "-8.00 (2 tr)" in riga or "+" in riga     # PnL dopo l'allarme, sui trade nella finestra
    assert "puo' solo BOCCIARE" in out and "ARL0" in out and "assente da qui" in out
    pools = rf.replay_pools(rf.trade_ordinati(trades), _pairs(), SPECS, ["AUSDT|gen_a"], 7.0)
    p = pools["fam:reversion|sideways"]
    assert p["cusum_allarme_ts"] == trades[3]["exit_ts"] and p["cusum_allarmi"] == 1 and p["ripresa"]
    assert p["n_dopo"] == 5 and p["pnl_dopo"] == pytest.approx(-8.0 + 18.0)
    assert p["sprt"] == "continue" and p["riferimento"] == 0.25


def test_il_replay_boccia_un_pool_che_suona_dopo_il_globale_e_rigioca_la_regola(monkeypatch, capsys):
    monkeypatch.setattr(settings, "DRIFT_MIN_TRADES_GLOBAL", 3)
    trades = [_t(i, -1.0) for i in range(6)]
    # senza `dal` nel documento: la regola globale (3 trade, PF 0 < 0.9) scatta al 3° trade, prima del CUSUM (4°)
    fb = _fb_replay(trades)
    monkeypatch.setattr(rf, "get_firebase", lambda: fb)
    assert rf.main([]) == 0
    out = capsys.readouterr().out
    assert "replay della regola globale (3 trade" in out and "BOCCIATO qui: suona dopo il globale" in out
    ts_g, fonte = rf.giorno_freno_globale(rf.trade_ordinati(trades), _pairs(), {})
    assert ts_g == trades[2]["exit_ts"] and "atteso da 1 coppie" in fonte
    ts_g, fonte = rf.giorno_freno_globale(rf.trade_ordinati(trades), {}, {})
    assert ts_g is None and "non rigiocabile" in fonte
    ts_g, fonte = rf.giorno_freno_globale(rf.trade_ordinati([_t(0, 2.0)]), _pairs(), {})
    assert ts_g is None and "mai soddisfatta" in fonte


def test_il_replay_misura_i_falsi_allarmi_sulla_storia_sana_del_gate(tmp_path, monkeypatch, capsys):
    righe = []
    for i in range(100):
        # storia sana: PF 2, R alternati +2 / -1: il CUSUM (rif 0.25) non deve suonare
        r = 2.0 if i % 2 else -1.0
        righe.append({"symbol": "AUSDT", "strategy": "gen_a", "direction": "long", "regime": "sideways",
                      "entry_ts": NOW - (200 - i) * 3600.0, "pnl_pct": 0.02 * r, "is_win": r > 0,
                      "mfe_r": 2.0, "bars_held": 3, "hour": 10, "famiglia": "reversion", "passed": True,
                      "feats": {"stop_pct": 0.02, "market_up": 1.0, "r1": 1.5}})
    # una coppia NON validata: fuori dall'ARL0
    righe.append({**righe[0], "strategy": "gen_zz", "entry_ts": NOW})
    (tmp_path / "20260926_15m.jsonl").write_text("\n".join(json.dumps(r) for r in righe), encoding="utf-8")
    arl0 = rf.arl0_storia_sana(righe, _pairs(), SPECS, ["AUSDT|gen_a"])
    assert arl0["fam:reversion|sideways"] == {"n": 100, "allarmi": 0, "per_100": 0.0, "riferimento": 0.25,
                                              "bocciata": False}
    # una storia «sana» che suona 8 volte su 100 boccia h
    male = [{**r, "pnl_pct": -0.02} for r in righe[:100]]
    a = rf.arl0_storia_sana(male, _pairs(), SPECS, ["AUSDT|gen_a"])["fam:reversion|sideways"]
    assert a["allarmi"] >= 1 and a["bocciata"] == (a["per_100"] > rf.MAX_FALSI_PER_100)
    fb = _fb_replay([_t(i, -1.0) for i in range(4)])
    monkeypatch.setattr(rf, "get_firebase", lambda: fb)
    assert rf.main(["--dir-selettore", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    # un trade sta in due pool (famiglia e direzione): la somma conta trade-pool, e lo dice
    assert "ARL0" in out and "fam:reversion|sideways" in out and "0 allarmi su 200 trade-pool" in out


def test_il_replay_senza_dati_esce_con_zero_e_la_voce_ops_e_in_lista(monkeypatch, capsys):
    monkeypatch.setattr(rf, "get_firebase", lambda: FirebaseClient())
    assert rf.main([]) == 0
    assert "niente da rigiocare" in capsys.readouterr().out
    with open(os.path.join(ROOT, "ops", "allowlist.example"), encoding="utf-8") as f:
        assert "replay:       .venv/bin/python -m scripts.replay_freno" in f.read()
    with open(os.path.join(ROOT, "docs", "controllo_schema.md"), encoding="utf-8") as f:
        assert "| `declassate` | {trades, pnl, aperte} |" in f.read()
    with open(os.path.join(ROOT, "dashboard", "app", "lib", "controllo.ts"), encoding="utf-8") as f:
        assert "declassate?: Declassate | null;" in f.read()
