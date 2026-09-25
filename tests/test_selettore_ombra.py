"""IL SELETTORE, PASSO 2 — l'ombra nel bot (25 set 2026).

Il verdetto del passo 1 e' NON BATTE, ma il proprietario vuole imparare da ogni
trade del paper: il bot annota su OGNI apertura la p del selettore (modello
pubblicato in `selector/current`), senza mai agire. Qui si verifica che:

* il report pubblica un documento JSON-safe che `prob` rilegge tale e quale
  (round trip), e lo fa in fail-open senza Firebase;
* il bot carica il modello, rifiuta un modello di un'altra versione, calcola p
  con le STESSE variabili del gate, logga «avrebbe / NON avrebbe aperto», e su
  qualunque errore risponde (None, None) con al massimo un avviso l'ora;
* nel percorso di apertura l'ombra viene DOPO tutti i rifiuti e PRIMA
  dell'ordine, e non puo' fermare niente;
* l'executor porta p e soglia sulla posizione, oltre il riavvio e sul trade
  chiuso;
* `trade_stats` legge la p contro l'esito, con e senza dati;
* la riga costruita dal vivo ha le stesse `feats` della riga del gate
  (`righe_selettore`) e produce lo stesso vettore: parita', come per il resto.
"""
from __future__ import annotations

import inspect
import io
import json
import math
import types
from contextlib import redirect_stdout

import numpy as np
import pytest

from bot.core.firebase_client import FirebaseClient
from bot.core.models import (
    AssetSnapshot, Direction, EffectiveRiskParams, IndicatorSnapshot, Regime,
)
from bot.execution.executor import ExecutionEngine
from bot.learning import selettore as sel
from bot.main import TradingBot
from scripts import selettore_report, trade_stats


# ---- fabbrica di righe del gate (stesso formato di righe_selettore) ---------- #
def _riga(i, rsi, win, pnl, direction="long", regime="sideways"):
    feats = {"rsi": rsi, "adx": 25.0 + (i % 5), "stoch_k": 50.0, "atr_pct": 0.02,
             "dist_ema": 0.0, "bb_pos": 0.5, "vol_ratio": 1.0, "stop_pct": 0.02,
             "r1": 1.0, "market_up": 1.0, "hour": i % 24}
    return {"symbol": f"C{i % 7}USDT", "strategy": "strat", "direction": direction,
            "regime": regime, "entry_ts": 1_650_000_000.0 + i * 6 * 3600.0,
            "pnl_pct": pnl, "pnl": pnl * 100, "is_win": bool(win), "mfe_r": 1.0,
            "bars_held": 4, "hour": i % 24, "famiglia": "reversion", "feats": feats,
            "run_end": "2026-09-24", "interval": "15m", "passed": True}


def _righe(n=900, seed=3):
    rng = np.random.RandomState(seed)
    out = []
    for i in range(n):
        rsi = rng.uniform(10, 90)
        win = rng.rand() < (0.8 if rsi < 40 else 0.25)
        pnl = rng.uniform(0.005, 0.03) if win else -rng.uniform(0.005, 0.02)
        out.append(_riga(i, rsi, win, pnl, direction="long" if rng.rand() < 0.5 else "short"))
    return out


def _doc(righe=None):
    righe = righe or _righe()
    report = sel.report_per_famiglia(righe, min_train=200)
    return selettore_report.documento_modello(righe, report), righe


class _FbVivo(FirebaseClient):
    """In memoria ma «connesso»: cosi' la pubblicazione scrive davvero."""
    @property
    def is_live(self) -> bool:
        return True


# --------------------------------------------------------------------------- #
# 1. il report pubblica selector/current, JSON-safe, round trip                #
# --------------------------------------------------------------------------- #
def test_documento_modello_e_json_safe_e_fa_il_round_trip():
    doc, righe = _doc()
    assert doc is not None
    # esattamente JSON: niente numpy, niente NaN
    json.dumps(doc, allow_nan=False)
    assert doc["stato"] == "ombra" and doc["famiglia"] == "tutte"
    assert doc["righe"] == len(righe)
    assert doc["verdetto"] in ("BATTE", "NON BATTE", "CAMPIONE INSUFFICIENTE")
    assert doc["soglia"] in sel.SOGLIE
    assert "generato_at" in doc and "nota" in doc
    m = doc["modello"]
    assert m["variabili"] == list(sel.VARIABILI)
    assert all(isinstance(x, float) for x in m["coef"] + m["media"] + m["scala"])
    # la p letta dal documento pubblicato e' la stessa del modello addestrato qui
    letto = sel.valida_pubblicato(json.loads(json.dumps(doc)))
    assert letto is not None and letto["soglia"] == doc["soglia"]
    diretto = sel.addestra(righe, famiglia="tutte")
    for r in righe[:25]:
        assert sel.prob(letto["modello"], r) == pytest.approx(sel.prob(diretto, r), abs=1e-9)


def test_soglia_e_la_mediana_delle_finestre_o_il_default():
    doc, righe = _doc()
    report = sel.report_per_famiglia(righe, min_train=200)
    soglie = [f["soglia"] for f in report["tutte"]["finestre"] if f.get("soglia") is not None]
    assert soglie and doc["soglia"] == selettore_report._mediana(soglie)
    assert selettore_report._mediana([0.4, 0.6, 0.5]) == 0.5
    assert selettore_report._mediana([0.4, 0.6]) == pytest.approx(0.5)
    # senza finestre valutate (campione insufficiente) resta la soglia consigliata
    # del modello su tutto, e in mancanza anche di quella il default 0.5
    poche = righe[:60]
    d2 = selettore_report.documento_modello(poche, sel.report_per_famiglia(poche, min_train=500))
    assert d2 is not None and 0 < d2["soglia"] < 1
    d3 = selettore_report.documento_modello(poche, {"tutte": {}})
    assert d3["soglia"] == sel.SOGLIA_DEFAULT
    # troppo poche righe: nessun documento, e la pubblicazione lo dice senza rompere
    assert selettore_report.documento_modello(righe[:10], {}) is None
    assert selettore_report.pubblica_modello(None) is False


def test_pubblica_modello_scrive_se_connesso_e_fail_open_altrimenti(capsys):
    doc, righe = _doc()
    fb = _FbVivo()
    assert selettore_report.pubblica_modello(doc, fb=fb) is True
    letto = sel.valida_pubblicato(fb.get_doc("selector", "current"))
    assert letto is not None
    assert sel.prob(letto["modello"], righe[0]) == pytest.approx(sel.prob(doc["modello"], righe[0]))
    # non connesso: stampa e continua (e' cosi' che gira nei test della allowlist)
    assert selettore_report.pubblica_modello(doc, fb=FirebaseClient()) is False
    assert "non connesso" in capsys.readouterr().out

    class _Rotto:
        is_live = True

        def set_doc(self, *a):
            raise RuntimeError("firestore giu'")

    assert selettore_report.pubblica_modello(doc, fb=_Rotto()) is False
    assert "saltata" in capsys.readouterr().out


def _scrivi(tmp_path, nome, righe):
    with open(tmp_path / nome, "w", encoding="utf-8") as f:
        for r in righe:
            f.write(json.dumps(r) + "\n")


def test_il_report_prova_a_pubblicare_selector_current(tmp_path, capsys):
    _scrivi(tmp_path, "2026-09-25_15m.jsonl", _righe(600, seed=5))
    assert selettore_report.main(["--cartella", str(tmp_path), "--min-train", "150"]) == 0
    out = capsys.readouterr().out
    assert "selector/current" in out
    assert "OMBRA" in out and "NON usa ancora il selettore" in out


# --------------------------------------------------------------------------- #
# 2. valida_pubblicato: mai una p su colonne sbagliate                         #
# --------------------------------------------------------------------------- #
def test_valida_pubblicato_rifiuta_altre_versioni_e_numeri_rotti():
    doc, _ = _doc()
    assert sel.valida_pubblicato(None) is None
    assert sel.valida_pubblicato({"modello": "x"}) is None
    altra = json.loads(json.dumps(doc))
    altra["modello"]["variabili"] = list(sel.VARIABILI)[:-1] + ["nuova"]
    assert sel.valida_pubblicato(altra) is None
    corta = json.loads(json.dumps(doc))
    corta["modello"]["coef"] = corta["modello"]["coef"][:-1]
    assert sel.valida_pubblicato(corta) is None
    nan = json.loads(json.dumps(doc))
    nan["modello"]["intercetta"] = float("nan")
    assert sel.valida_pubblicato(nan) is None
    # soglia assente o fuori da (0, 1): default, non un errore
    senza = json.loads(json.dumps(doc))
    senza["soglia"] = 7
    assert sel.valida_pubblicato(senza)["soglia"] == sel.SOGLIA_DEFAULT
    del senza["soglia"]
    assert sel.valida_pubblicato(senza)["soglia"] == sel.SOGLIA_DEFAULT


# --------------------------------------------------------------------------- #
# 3. il bot: carica, calcola p, logga, non alza mai                            #
# --------------------------------------------------------------------------- #
def _ind(tf="15m", rsi=28.0, **kw):
    base = dict(timeframe=tf, rsi=rsi, adx=30.0, stoch_k=20.0, atr=2.0, ema_fast=101.0,
                ema_slow=99.0, bb_upper=104.0, bb_lower=96.0, volume=1000.0,
                volume_sma=800.0, close=100.0)
    base.update(kw)
    return IndicatorSnapshot(**base)


def _asset(sym="XUSDT", price=100.0, **kw):
    return AssetSnapshot(symbol=sym, price=price, regime=Regime.BULL_TRENDING,
                         indicators={"15m": _ind(**kw)})


def _btc(up=True):
    return AssetSnapshot(symbol="BTCUSDT", price=50_000.0,
                         indicators={"1h": IndicatorSnapshot(timeframe="1h", ema_fast=51.0 if up else 49.0,
                                                             ema_slow=50.0)})


def _bot(fb=None, doc=None):
    b = types.SimpleNamespace()
    b.fb = fb or FirebaseClient()
    if doc is not None:
        b.fb.set_doc("selector", "current", doc)
    b._selettore = None
    b._btc_snap = _btc()
    b._selettore_avviso_at = 0.0
    b.regime = Regime.BULL_TRENDING
    b._load_selettore = types.MethodType(TradingBot._load_selettore, b)
    b._ombra_selettore = types.MethodType(TradingBot._ombra_selettore, b)
    return b


def _decisione(direction=Direction.LONG):
    return types.SimpleNamespace(asset="XUSDT", strategy="gen_x", direction=direction)


def _params(stop=98.0):
    return types.SimpleNamespace(stop_price=stop)


def test_load_selettore_carica_rifiuta_e_tiene_il_vecchio_se_firebase_tace(capsys):
    doc, _ = _doc()
    b = _bot(doc=doc)
    b._load_selettore()
    assert b._selettore is not None and b._selettore["soglia"] == doc["soglia"]
    assert "modello caricato" in capsys.readouterr().out
    # stesso documento: nessuna nuova riga nel log (non e' un evento)
    b._load_selettore()
    assert "modello caricato" not in capsys.readouterr().out
    # documento di un'altra versione -> ombra spenta, detto nel log
    altra = json.loads(json.dumps(doc))
    altra["modello"]["variabili"] = ["x"] * len(sel.VARIABILI)
    b.fb.set_doc("selector", "current", altra)
    b._load_selettore()
    assert b._selettore is None and "ombra spenta" in capsys.readouterr().out
    # Firebase che non risponde: si tiene cio' che si aveva, mai un'eccezione
    b = _bot(doc=doc)
    b._load_selettore()
    b.fb.get_doc = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("giu'"))
    b._load_selettore()
    assert b._selettore is not None
    assert "fallita" in capsys.readouterr().out
    # senza documento: ombra spenta in silenzio (e' il caso normale prima del report)
    b = _bot()
    b._load_selettore()
    assert b._selettore is None


def test_ombra_calcola_p_e_logga_il_verdetto_senza_agire(capsys):
    doc, _ = _doc()
    b = _bot(doc=doc)
    b._load_selettore()
    capsys.readouterr()
    p, soglia = b._ombra_selettore(_decisione(), _asset(), _params(), {}, "15m", 1_758_800_000.0)
    assert p is not None and 0.0 < p < 1.0 and soglia == doc["soglia"]
    out = capsys.readouterr().out
    assert "[selettore] XUSDT gen_x long p=" in out and "soglia=" in out
    assert ("avrebbe aperto" in out) and ("apre comunque" in out)
    assert ("NON avrebbe aperto" in out) == (p < soglia)
    # short: la direzione e' nella riga (is_long e le interazioni cambiano p)
    p2, _ = b._ombra_selettore(_decisione(Direction.SHORT), _asset(), _params(102.0), {}, "15m", 1_758_800_000.0)
    assert p2 is not None and p2 != p


def test_ombra_e_la_stessa_p_del_modello_offline_sulla_stessa_riga():
    """Parita' col gate: la p del bot deve essere quella che `prob` da' alla riga
    costruita dalle STESSE feats (feats_ingresso) sullo stesso snapshot."""
    from backtesting.engine import feats_ingresso
    doc, _ = _doc()
    b = _bot(doc=doc)
    b._load_selettore()
    now = 1_758_800_000.0
    asset, params = _asset(), _params()
    with redirect_stdout(io.StringIO()):
        p, _ = b._ombra_selettore(_decisione(), asset, params, {"scale_r_mults": [2, 4]}, "15m", now)
    from datetime import datetime, timezone
    ora = datetime.fromtimestamp(now, tz=timezone.utc).hour   # si ricava, non si indovina
    feats = feats_ingresso(asset, "15m", 100.0, 98.0, types.SimpleNamespace(params={"scale_r_mults": [2, 4]}),
                           _btc(), hour=ora)
    riga = sel.riga_dal_vivo("XUSDT", "gen_x", "long", Regime.BULL_TRENDING, ora, feats, entry_ts=now)
    assert feats["r1"] == 2.0 and feats["market_up"] == 1.0
    assert p == pytest.approx(sel.prob(doc["modello"], riga), abs=1e-4)


def test_ombra_senza_modello_o_senza_variabili_da_none(capsys):
    doc, _ = _doc()
    b = _bot()
    assert b._ombra_selettore(_decisione(), _asset(), _params(), {}, "15m", 0.0) == (None, None)
    b = _bot(doc=doc)
    b._load_selettore()
    capsys.readouterr()
    # senza rsi sul grafico: p None e il log dice cosa manca
    assert b._ombra_selettore(_decisione(), _asset(rsi=None), _params(), {}, "15m", 0.0) == (None, None)
    out = capsys.readouterr().out
    assert "p non calcolabile" in out and "rsi" in out
    # senza il timeframe della strategia sullo snapshot: tutte le obbligatorie mancano
    assert b._ombra_selettore(_decisione(), _asset(), _params(), {}, "1h", 0.0) == (None, None)
    # senza snapshot BTC: market_up al neutro, p resta calcolabile (non si inventa)
    b._btc_snap = None
    p, _ = b._ombra_selettore(_decisione(), _asset(), _params(), {}, "15m", 0.0)
    assert p is not None


def test_ombra_su_errore_risponde_none_e_avvisa_una_volta_l_ora(capsys):
    doc, _ = _doc()
    b = _bot(doc=doc)
    b._load_selettore()
    capsys.readouterr()
    rotto = types.SimpleNamespace()          # niente stop_price -> AttributeError dentro
    now = 1_000_000.0
    assert b._ombra_selettore(_decisione(), _asset(), rotto, {}, "15m", now) == (None, None)
    assert "ombra fallita" in capsys.readouterr().out
    assert b._ombra_selettore(_decisione(), _asset(), rotto, {}, "15m", now + 100) == (None, None)
    assert "ombra fallita" not in capsys.readouterr().out
    assert b._ombra_selettore(_decisione(), _asset(), rotto, {}, "15m", now + 3601) == (None, None)
    assert "ombra fallita" in capsys.readouterr().out


def test_nel_percorso_di_apertura_l_ombra_viene_dopo_i_rifiuti_e_prima_dell_ordine():
    """Sul sorgente (un TradingBot intero e' troppo pesante): l'ombra e' l'ultima
    cosa prima di `open_position`, dopo l'ULTIMO rifiuto, e non ha un `return`
    tra se' e l'ordine — non puo' fermare niente."""
    src = inspect.getsource(TradingBot._try_open)
    i_ombra = src.index("self._ombra_selettore(")
    i_open = src.index("self.executor.open_position(")
    ultimo_rifiuto = src.rindex("_rifiuto(")
    assert ultimo_rifiuto < i_ombra < i_open
    assert "return" not in src[i_ombra:i_open]
    assert "selector_p=_sel_p, selector_soglia=_sel_soglia" in src
    # la ricarica oraria sta col registro, e all'avvio
    run = inspect.getsource(TradingBot.run)
    blocco = run[run.index("ADAPT_RELOAD_SECONDS"):]
    assert "self._load_selettore()" in blocco[:600]
    assert run.index("self._load_selettore()") < run.index("while max_iterations")
    # refresh_regime conserva lo snapshot BTC per il contesto di mercato
    assert "self._btc_snap = btc" in inspect.getsource(TradingBot.refresh_regime)


# --------------------------------------------------------------------------- #
# 4. executor: p e soglia sulla posizione, oltre il riavvio, sul trade chiuso   #
# --------------------------------------------------------------------------- #
def _eff_params(stop=98.0, tp=104.0):
    return EffectiveRiskParams(
        leverage=3.0, risk_per_trade=0.01, notional=100.0, quantity=1.0,
        stop_price=stop, take_profit_price=tp, user_leverage=3, user_risk_per_trade=0.01,
        safety_leverage_cap=5, safety_risk_cap=0.03, approved=True)


def _exec_asset(price=100.0):
    return AssetSnapshot(symbol="BTCUSDT", price=price, regime=Regime.BULL_TRENDING,
                         indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=2.0, close=price)})


def test_executor_persiste_ripristina_e_porta_p_sul_trade_chiuso():
    fb = FirebaseClient()
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    pos = eng.open_position(_exec_asset(), "gen_x", Direction.LONG, _eff_params(),
                            selector_p=0.61, selector_soglia=0.45)
    assert pos.selector_p == 0.61 and pos.selector_soglia == 0.45
    eng._write_position_state(pos, 100.0)
    stato = fb.get_rtdb("/positions/BTCUSDT")
    assert stato["selector_p"] == 0.61 and stato["selector_soglia"] == 0.45
    # riavvio: l'executor nuovo rilegge da Firebase
    eng2 = ExecutionEngine(firebase=fb, dry_run=True)
    p2 = eng2.open_positions["BTCUSDT"]
    assert p2.selector_p == 0.61 and p2.selector_soglia == 0.45
    # documento di prima dell'ombra: None, non un errore
    vecchio = dict(stato)
    vecchio.pop("selector_p"); vecchio.pop("selector_soglia")
    p3 = eng2._position_from_state(vecchio)
    assert p3.selector_p is None and p3.selector_soglia is None
    # chiusura: il ClosedTrade porta p e soglia, e finiscono nel documento Firestore
    closed = eng2.update_position("BTCUSDT", 97.0)
    assert closed is not None and closed.selector_p == 0.61 and closed.selector_soglia == 0.45
    dump = closed.model_dump(mode="json")
    assert dump["selector_p"] == 0.61 and dump["selector_soglia"] == 0.45


def test_executor_senza_ombra_lascia_none():
    eng = ExecutionEngine(firebase=FirebaseClient(), dry_run=True)
    pos = eng.open_position(_exec_asset(), "gen_x", Direction.LONG, _eff_params())
    assert pos.selector_p is None and pos.selector_soglia is None
    closed = eng.update_position("BTCUSDT", 97.0)
    assert closed.selector_p is None and closed.selector_soglia is None


# --------------------------------------------------------------------------- #
# 5. trade_stats: la sezione SELETTORE IN OMBRA                                #
# --------------------------------------------------------------------------- #
def _t(p=None, soglia=0.5, pnl=1.0, i=0):
    t = {"strategy": "gen_x", "symbol": "AUSDT", "direction": "long", "pnl": pnl,
         "exit_reason": "take_profit" if pnl > 0 else "stop_loss",
         "exit_ts": 100.0 + i, "entry_ts": 90.0 + i}
    if p is not None:
        t["selector_p"] = p
        t["selector_soglia"] = soglia
    return t


def test_selettore_ombra_report_senza_e_con_dati():
    vuoto = trade_stats.selettore_ombra_report([_t(), _t(pnl=-1.0)])
    assert vuoto["n"] == 0 and vuoto["correlazione"] is None
    assert "2/3 finestre" in vuoto["regola"] and "40" in vuoto["regola"]
    # p alta vince, p bassa perde: la calibrazione non e' piatta
    trades = ([_t(p=0.7, pnl=2.0, i=i) for i in range(6)]
              + [_t(p=0.3, pnl=-1.0, i=10 + i) for i in range(6)]
              + [_t(p="boh", pnl=5.0, i=30), _t(pnl=9.0, i=31)])   # rotta e senza p
    rep = trade_stats.selettore_ombra_report(trades)
    assert rep["n"] == 12 and rep["n_vinti"] == 6 and rep["n_persi"] == 6
    assert rep["p_media_vinti"] == pytest.approx(0.7) and rep["p_media_persi"] == pytest.approx(0.3)
    assert rep["n_sopra"] == 6 and rep["pnl_sopra"] == pytest.approx(12.0)
    assert rep["pnl_tutti"] == pytest.approx(6.0)
    assert rep["correlazione"] == pytest.approx(1.0)
    # sotto i 10 trade la correlazione non si calcola (sarebbe rumore)
    assert trade_stats.selettore_ombra_report(trades[:8])["correlazione"] is None
    # soglia mancante -> 0.5; p costante -> correlazione None (serie costante)
    piatti = [dict(_t(p=0.6, pnl=(1.0 if i % 2 else -1.0), i=i), selector_soglia=None)
              for i in range(12)]
    rep2 = trade_stats.selettore_ombra_report(piatti)
    assert rep2["n_sopra"] == 12 and rep2["correlazione"] is None


def test_trade_stats_stampa_la_sezione_con_e_senza_p(monkeypatch, capsys):
    class _FakeFB:
        def __init__(self, trades):
            self._t = trades

        def query_collection(self, *a, **k):
            return self._t

        def get_rtdb(self, *a, **k):
            return None

    monkeypatch.setattr(trade_stats, "get_firebase",
                        lambda: _FakeFB([_t(pnl=-1.0, i=i) for i in range(3)]))
    assert trade_stats.main() == 0
    out = capsys.readouterr().out
    assert "SELETTORE IN OMBRA" in out and "nessun trade con p ancora" in out
    assert out.index("IPOTESI DAI REFERTI") < out.index("SELETTORE IN OMBRA")
    trades = ([_t(p=0.7, pnl=2.0, i=i) for i in range(6)]
              + [_t(p=0.3, pnl=-1.0, i=10 + i) for i in range(6)])
    monkeypatch.setattr(trade_stats, "get_firebase", lambda: _FakeFB(trades))
    assert trade_stats.main() == 0
    out = capsys.readouterr().out
    assert "trade con p: 12" in out
    assert "p media dei vinti: 0.700   p media dei persi: 0.300" in out
    assert "sopra la soglia: 6/12 trade, PnL +12.00 contro +6.00" in out
    assert "correlazione p/esito: +1.000" in out
    assert "entra solo se batte" in out


# --------------------------------------------------------------------------- #
# 6. parita' delle variabili: la riga del bot = la riga del gate                #
# --------------------------------------------------------------------------- #
def test_la_riga_dal_vivo_ha_le_stesse_feats_della_riga_del_gate():
    from backtesting.engine import SimTrade, feats_ingresso
    from scripts.discover_strategies import righe_selettore

    asset, ctx = _asset(), _btc()
    feats = feats_ingresso(asset, "15m", 100.0, 98.0, types.SimpleNamespace(params={}), ctx, hour=7)
    t = SimTrade(strategy="gen_x", regime="bull_trending", direction="long", entry_price=100.0,
                 exit_price=101.0, pnl_pct=0.01, max_adverse_pct=0.0, confidence=60,
                 is_win=True, pnl=1.0, symbol="XUSDT", hour_bucket=7,
                 regime_at_entry="bull_trending", mfe_r=1.0, bars_held=3,
                 entry_ts=1_758_800_000.0, feats=feats)
    riga_gate = righe_selettore([t], "XUSDT", {"id": "gen_x", "features": [{"kind": "rsi_extreme"}]},
                                run_end="2026-09-25", interval="15m")[0]
    riga_bot = sel.riga_dal_vivo("XUSDT", "gen_x", Direction.LONG, Regime.BULL_TRENDING, 7,
                                 feats, entry_ts=1_758_800_000.0)
    # stesse chiavi nelle feats (stessa funzione: cambiarla rompe entrambi allo stesso modo)
    assert set(riga_bot["feats"]) == set(riga_gate["feats"])
    assert set(riga_bot["feats"]) >= set(sel.VARIABILI[:sel._N_FEATS])
    # la riga del bot e' un SOTTOINSIEME della riga del gate: solo l'esito manca
    assert set(riga_bot) <= set(riga_gate)
    assert set(riga_gate) - set(riga_bot) == {"pnl_pct", "pnl", "is_win", "mfe_r", "bars_held",
                                              "famiglia", "passed", "run_end", "interval"}
    for k in riga_bot:
        assert riga_bot[k] == riga_gate[k], k
    # e quindi lo stesso vettore, cioe' la stessa p
    assert sel.vettore(riga_bot) == sel.vettore(riga_gate)
    assert not any(math.isnan(v) for v in sel.vettore(riga_bot))
    # senza contesto BTC, `market_up` e' None e il vettore prende il neutro: onesto
    feats2 = feats_ingresso(asset, "15m", 100.0, 98.0, None, None, hour=7)
    assert feats2["market_up"] is None
    r2 = sel.riga_dal_vivo("XUSDT", "gen_x", "long", "bull_trending", 7, feats2)
    assert sel.vettore(r2)[sel.VARIABILI.index("market_up")] == sel._NEUTRI["market_up"]
    assert sel.variabili_mancanti(r2) == []
