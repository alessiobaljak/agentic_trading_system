"""IL PAPER ESPLORATIVO (25 set 2026, backlog F1bis — il proprietario ha detto si').

Cosa si protegge. Le coppie che passano il gate per un pelo (quasi-passaggi) si
operano in paper a un quarto della size, marcate `esplorativa`, FUORI dal
learning che governa le validate (pesi, keep del trailing, deriva, calibrazione)
e DENTRO cio' che il gate rilegge (referti, scala, keep). Il metro
dell'esperimento e' la storia del registro esplorativo: dopo 100 trade
esplorativi, quante coppie sono poi passate il gate contro quante scartate.

Un pezzo per ogni anello, ognuno col suo test:
  * GATE: la selezione (mancato piu' piccolo, una per coin, non validate, spec
    generata nota, coin nell'universo, tetto 20), il ciclo di vita (resta 2
    giri, validata -> storia, scartata dopo l'assenza, storia tagliata a 200),
    la scrittura fail-open e il campo `giro.esplorative` del documento del gate;
  * BOT: adaptation carica e espone (mai fuori dal paper), l'orchestratore da'
    la precedenza alle validate e applica il tetto di aperte (rifiuto contato),
    main moltiplica la size per 0,25 e passa la marca, l'executor la persiste,
    la ripristina e la mette sul trade chiuso;
  * LEARNING: pesi, keep, deriva e calibrazione la ignorano; i referti la
    contano; il controllo orario la tiene a parte; `trades` e `gate` la stampano.
"""
from __future__ import annotations

import inspect
import types

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient, decode_pairs, encode_pairs
from bot.core.models import (AssetSnapshot, Direction, ExitReason, IndicatorSnapshot,
                             OrchestratorDecision, Regime)
from bot.execution.executor import ExecutionEngine
from bot.learning import controllo as c
from bot.learning import metrics
from bot.learning.adaptation import AdaptationEngine
from bot.learning.calibration import calibrate
from bot.learning.drift import compute_drift
from bot.learning.referti import aggrega_referti
from bot.orchestrator.orchestrator import MOTIVI_RIFIUTO, Orchestrator, motivo_rifiuto
from scripts import discover_strategies as d
from scripts import gate_progress as g
from scripts import trade_stats as ts

NOW = 1_790_000_000.0
SPEC = {"id": "gen_x", "features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0}],
        "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}


# --------------------------------------------------------------------------- #
# attrezzi                                                                     #
# --------------------------------------------------------------------------- #
def _near(sym, gid, shortfall, binding="pf"):
    return {"key": f"{sym}|{gid}", "binding": binding, "shortfall": shortfall,
            "pf": 1.1, "trades": 40}


def _specs(*ids):
    return {i: {**SPEC, "id": i} for i in ids}


def _asset(sym="BTCUSDT") -> AssetSnapshot:
    """Condizioni che fanno scattare mean_reversion LONG e la spec rsi_extreme LONG
    (stesse di tests/test_rifiuti_nel_log.py): prezzo sotto BB inferiore, RSI 20."""
    ind = IndicatorSnapshot(timeframe="15m", rsi=20.0, atr=2.0, close=94.0,
                            bb_lower=95.0, bb_upper=105.0, bb_mid=100.0)
    return AssetSnapshot(symbol=sym, price=94.0, regime=Regime.SIDEWAYS, indicators={"15m": ind})


def _orch(validate: dict[str, set], esplorative: list[str]) -> Orchestrator:
    """Orchestratore con adattamento finto: `validate` {coin: {strategie base}},
    `esplorative` chiavi "COIN|gen_x" con la spec di prova."""
    o = Orchestrator()
    o.adaptation._passed = {f"{s}|{st}" for s, sts in validate.items() for st in sts}
    o.adaptation._has_opt_data = True
    o.adaptation._esplorative = {k: {"symbol": k.split("|")[0], "strategy": "gen_x"} for k in esplorative}
    o.adaptation._esplorative_specs = {"gen_x": SPEC}
    return o


def _t(pnl=-5.0, esplorativa=False, strat="gen_a", sym="AUSDT", reason="stop_loss", conf=60.0):
    t = {"symbol": sym, "strategy": strat, "regime_at_entry": "sideways", "direction": "long",
         "pnl": pnl, "pnl_pct": pnl / 100, "timeframe": settings.ORCHESTRATOR_TIMEFRAME,
         "exit_reason": reason, "mfe_r": 0.3 if pnl < 0 else 2.0, "confidence_at_entry": conf,
         "exit_ts": NOW - 3600, "trailing_verdict": "premature", "trailing_knockout_atr": 0.5}
    if esplorativa:
        t["esplorativa"] = True
    return t


# --------------------------------------------------------------------------- #
# 1. il gate sceglie                                                            #
# --------------------------------------------------------------------------- #
def test_la_selezione_prende_il_mancato_piu_piccolo_una_per_coin():
    near = [_near("AUSDT", "gen_a", -0.08), _near("AUSDT", "gen_b", -0.01),
            _near("BUSDT", "gen_c", -0.05), _near("CUSDT", "gen_d", -0.02)]
    out = d.seleziona_esplorative(near, validate=[], specs=_specs("gen_a", "gen_b", "gen_c", "gen_d"),
                                  universo={"AUSDT", "BUSDT", "CUSDT"}, max_n=20)
    # ordine: -0.01 (A|gen_b), -0.02 (C), -0.05 (B); A|gen_a cade: seconda sulla stessa coin
    assert [x["key"] for x in out] == ["AUSDT|gen_b", "CUSDT|gen_d", "BUSDT|gen_c"]
    assert out[0] == {"key": "AUSDT|gen_b", "symbol": "AUSDT", "strategy": "gen_b",
                      "shortfall": -0.01, "binding": "pf", "pf": 1.1, "trades": 40}


def test_la_selezione_esclude_validate_base_spec_ignote_e_coin_fuori_universo():
    near = [_near("AUSDT", "gen_a", -0.01), _near("BUSDT", "mean_reversion", -0.01),
            _near("CUSDT", "gen_c", -0.01), _near("DUSDT", "gen_d", -0.01),
            _near("EUSDT", "gen_e", None)]
    out = d.seleziona_esplorative(near, validate={"AUSDT|gen_a"}, specs=_specs("gen_a", "gen_d", "gen_e"),
                                  universo={"AUSDT", "BUSDT", "CUSDT", "EUSDT"})
    # A: gia' validata; B: strategia BASE; C: spec non nota; D: coin fuori universo;
    # E: shortfall assente (vale -9) -> resta, in fondo
    assert [x["key"] for x in out] == ["EUSDT|gen_e"]


def test_la_selezione_ha_il_tetto_di_settings(monkeypatch):
    monkeypatch.setattr(settings, "ESPLORATIVE_MAX", 20)
    near = [_near(f"C{i}USDT", f"gen_{i}", -0.001 * i) for i in range(30)]
    out = d.seleziona_esplorative(near, [], _specs(*[f"gen_{i}" for i in range(30)]),
                                  {f"C{i}USDT" for i in range(30)})
    assert len(out) == 20 and out[0]["key"] == "C0USDT|gen_0"
    assert d.seleziona_esplorative(near, [], _specs(*[f"gen_{i}" for i in range(30)]),
                                   {f"C{i}USDT" for i in range(30)}, max_n=5)[-1]["key"] == "C4USDT|gen_4"


# --------------------------------------------------------------------------- #
# 2. il ciclo di vita                                                          #
# --------------------------------------------------------------------------- #
def _sel(*keys):
    return [{"key": k, "symbol": k.split("|")[0], "strategy": k.split("|")[1],
             "shortfall": -0.02, "binding": "pf", "pf": 1.1, "trades": 40} for k in keys]


def test_una_coppia_nuova_entra_con_since_e_resta_due_giri_senza_essere_vista():
    doc1, st1 = d.aggiorna_esplorative(None, _sel("AUSDT|gen_a", "BUSDT|gen_b"), _specs("gen_a", "gen_b"),
                                       validate=[], now=NOW)
    assert st1 == {"attive": 2, "nuove": 2, "validate_poi": 0, "scartate": 0,
                   "validate_giro": 0, "scartate_giro": 0}
    assert doc1["pairs"]["AUSDT|gen_a"]["since"] == NOW and doc1["pairs"]["AUSDT|gen_a"]["esito"] == "in_corso"
    assert set(doc1["specs"]) == {"gen_a", "gen_b"}
    # giro dopo (3 h): B non e' piu' un quasi-passaggio ma e' stata vista 3 h fa -> resta
    doc2, st2 = d.aggiorna_esplorative(doc1, _sel("AUSDT|gen_a"), _specs("gen_a"), [], NOW + 3 * 3600)
    assert set(doc2["pairs"]) == {"AUSDT|gen_a", "BUSDT|gen_b"} and st2["nuove"] == 0
    assert doc2["pairs"]["AUSDT|gen_a"]["since"] == NOW          # `since` non si muove
    assert doc2["pairs"]["AUSDT|gen_a"]["last_seen"] == NOW + 3 * 3600
    assert doc2["specs"]["gen_b"] == {**SPEC, "id": "gen_b"}     # la spec resta con la coppia
    # terzo giro (6 h): ancora dentro le 8 ore
    doc3, _ = d.aggiorna_esplorative(doc2, _sel("AUSDT|gen_a"), _specs("gen_a"), [], NOW + 6 * 3600)
    assert "BUSDT|gen_b" in doc3["pairs"]
    # quarto giro (9 h dall'ultima vista): scartata, in storia
    doc4, st4 = d.aggiorna_esplorative(doc3, _sel("AUSDT|gen_a"), _specs("gen_a"), [], NOW + 9 * 3600)
    assert set(doc4["pairs"]) == {"AUSDT|gen_a"} and set(doc4["specs"]) == {"gen_a"}
    assert doc4["storia"]["BUSDT|gen_b"] == {"since": NOW, "fine": NOW + 9 * 3600, "esito": "scartata"}
    assert st4["scartate"] == 1 and st4["scartate_giro"] == 1 and st4["validate_poi"] == 0


def test_una_coppia_che_passa_il_gate_finisce_in_storia_come_validata():
    doc1, _ = d.aggiorna_esplorative(None, _sel("AUSDT|gen_a", "BUSDT|gen_b"), _specs("gen_a", "gen_b"), [], NOW)
    doc2, st2 = d.aggiorna_esplorative(doc1, _sel("BUSDT|gen_b"), _specs("gen_b"),
                                       validate=["AUSDT|gen_a"], now=NOW + 3600)
    assert set(doc2["pairs"]) == {"BUSDT|gen_b"}
    assert doc2["storia"]["AUSDT|gen_a"] == {"since": NOW, "fine": NOW + 3600, "esito": "validata"}
    assert (st2["validate_poi"], st2["validate_giro"], st2["scartate"]) == (1, 1, 0)
    # anche se il gate la riselezionasse come quasi-passaggio nello stesso giro
    doc3, _ = d.aggiorna_esplorative(doc2, _sel("AUSDT|gen_a"), _specs("gen_a"), ["AUSDT|gen_a"], NOW + 7200)
    assert "AUSDT|gen_a" not in doc3["pairs"] and doc3["storia"]["AUSDT|gen_a"]["esito"] == "validata"


def test_la_storia_e_tagliata_alle_200_voci_piu_recenti():
    storia = {f"C{i}USDT|gen_{i}": {"since": 0, "fine": float(i), "esito": "scartata"} for i in range(205)}
    prec = {"pairs": encode_pairs({}), "specs": encode_pairs({}), "storia": encode_pairs(storia)}
    doc, st = d.aggiorna_esplorative(prec, [], {}, [], NOW)
    assert len(doc["storia"]) == d.ESPLORATIVE_STORIA_MAX == 200
    assert "C0USDT|gen_0" not in doc["storia"] and "C204USDT|gen_204" in doc["storia"]
    assert st["scartate"] == 200


def test_il_documento_precedente_si_legge_codificato_come_il_registro():
    doc1, _ = d.aggiorna_esplorative(None, _sel("AUSDT|gen_a"), _specs("gen_a"), [], NOW)
    codificato = {"updated_at": NOW, "pairs": encode_pairs(doc1["pairs"]),
                  "specs": encode_pairs(doc1["specs"]), "storia": encode_pairs(doc1["storia"])}
    doc2, st = d.aggiorna_esplorative(codificato, _sel("AUSDT|gen_a"), {}, [], NOW + 3600)
    assert st["attive"] == 1 and st["nuove"] == 0 and doc2["specs"]["gen_a"]["id"] == "gen_a"


# --------------------------------------------------------------------------- #
# 3. la scrittura, fail-open                                                    #
# --------------------------------------------------------------------------- #
class _FB(FirebaseClient):
    def __init__(self, rotto=False):
        super().__init__()
        self.rotto = rotto

    def set_doc(self, coll, did, data):
        if self.rotto and coll == "strategy_registry":
            raise RuntimeError("firestore giu'")
        super().set_doc(coll, did, data)


def test_pubblica_scrive_il_documento_codificato_e_stampa_la_riga(capsys):
    fb = _FB()
    st = d.pubblica_esplorative(fb, [_near("AUSDT", "gen_a", -0.01), _near("BUSDT", "gen_b", -0.03)],
                                validate=[], specs=_specs("gen_a", "gen_b"),
                                universo={"AUSDT", "BUSDT"}, now=NOW)
    assert st["attive"] == 2 and st["nuove"] == 2
    doc = fb.get_doc("strategy_registry", "esplorative")
    assert doc["updated_at"] == NOW
    assert set(decode_pairs(doc["pairs"])) == {"AUSDT|gen_a", "BUSDT|gen_b"}
    assert set(decode_pairs(doc["specs"])) == {"gen_a", "gen_b"} and decode_pairs(doc["storia"]) == {}
    assert "[cervello] esplorative: 2 attive (2 nuove), validate poi 0, scartate 0" in capsys.readouterr().out
    # il giro dopo: A validata, B ancora quasi-passaggio
    st2 = d.pubblica_esplorative(fb, [_near("BUSDT", "gen_b", -0.03)], validate=["AUSDT|gen_a"],
                                 specs=_specs("gen_b"), universo={"AUSDT", "BUSDT"}, now=NOW + 3600)
    assert (st2["attive"], st2["validate_poi"]) == (1, 1)
    assert "validate poi 1, scartate 0" in capsys.readouterr().out


def test_pubblica_non_solleva_mai_e_rispetta_l_interruttore(monkeypatch, capsys):
    st = d.pubblica_esplorative(_FB(rotto=True), [_near("AUSDT", "gen_a", -0.01)], [], _specs("gen_a"),
                                {"AUSDT"}, now=NOW)
    assert st is None
    assert "[cervello] esplorative: non aggiornate (RuntimeError" in capsys.readouterr().out
    monkeypatch.setattr(settings, "ESPLORATIVE_ENABLED", False)
    fb = _FB()
    assert d.pubblica_esplorative(fb, [_near("AUSDT", "gen_a", -0.01)], [], _specs("gen_a"), {"AUSDT"}) is None
    assert fb.get_doc("strategy_registry", "esplorative") is None
    assert "spente" in capsys.readouterr().out


def test_il_main_della_discovery_pubblica_dopo_il_merge_e_il_gate_doc_lo_espone():
    src = inspect.getsource(d.main)
    assert src.index("merge_into_registry(") < src.index("pubblica_esplorative(") < src.index("riga_cervello_intorno(")
    assert '"esplorative": stats_esplorative' in src
    from tests.test_doc_gate import _costruisci, _fixture_piccola, _run
    doc = _costruisci(*_fixture_piccola())
    assert doc["giro"]["esplorative"] == {"attive": 12, "validate_poi": 1, "scartate": 2}
    run = _run()
    run.pop("esplorative")
    assert _costruisci(*_fixture_piccola(), run=run)["giro"]["esplorative"] is None


# --------------------------------------------------------------------------- #
# 4. il bot: adaptation                                                        #
# --------------------------------------------------------------------------- #
def _fb_bot(validated=("AUSDT|gen_a",), esplorative=("BUSDT|gen_x", "AUSDT|gen_x"), ready=True):
    fb = FirebaseClient()
    pairs = {k: {"symbol": k.split("|")[0], "strategy": k.split("|")[1], "generated": True,
                 "pass_count": 3, "last_params": {}} for k in validated}
    fb.set_doc("strategy_registry", "validated", {"pairs": encode_pairs(pairs),
                                                  "validated": list(validated), "ready": ready})
    fb.set_doc("discovered_strategies", "specs", {"specs": encode_pairs({"gen_a": {**SPEC, "id": "gen_a"}})})
    fb.set_doc("strategy_registry", "esplorative", {
        "updated_at": NOW,
        "pairs": encode_pairs({k: {"symbol": k.split("|")[0], "strategy": "gen_x", "esito": "in_corso"}
                               for k in esplorative}),
        "specs": encode_pairs({"gen_x": {**SPEC, "timeframe": "1h"}}), "storia": encode_pairs({})})
    return fb


def test_adaptation_carica_le_esplorative_e_le_marca(monkeypatch):
    monkeypatch.setattr(settings, "DRY_RUN", True)
    monkeypatch.setattr(settings, "ESPLORATIVE_ENABLED", True)
    eng = AdaptationEngine(_fb_bot())
    strats = eng.esplorative_for("BUSDT")
    assert [s.name for s in strats] == ["gen_x"] and strats[0].esplorativa is True
    assert eng.is_esplorativa("BUSDT", "gen_x") is True
    assert eng.is_esplorativa("BUSDT", "gen_a") is False
    # le generate validate NON sono marcate, e restano dove erano
    assert all(not getattr(s, "esplorativa", False) for s in eng.generated_strategies_for("AUSDT"))
    assert eng.timeframe_for("gen_x") == "1h"          # la spec esplorativa e' nota anche qui


def test_una_esplorativa_diventata_validata_si_opera_solo_come_validata(monkeypatch):
    monkeypatch.setattr(settings, "DRY_RUN", True)
    eng = AdaptationEngine(_fb_bot(validated=("AUSDT|gen_x",), esplorative=("AUSDT|gen_x", "BUSDT|gen_x")))
    assert eng.esplorative_for("AUSDT") == [] and eng.is_esplorativa("AUSDT", "gen_x") is False
    assert [s.name for s in eng.esplorative_for("BUSDT")] == ["gen_x"]


def test_fuori_dal_paper_o_spente_o_registro_non_pronto_niente_esplorative(monkeypatch):
    monkeypatch.setattr(settings, "DRY_RUN", False)
    monkeypatch.setattr(settings, "ESPLORATIVE_ENABLED", True)
    assert AdaptationEngine(_fb_bot()).esplorative_for("BUSDT") == []
    monkeypatch.setattr(settings, "DRY_RUN", True)
    monkeypatch.setattr(settings, "ESPLORATIVE_ENABLED", False)
    assert AdaptationEngine(_fb_bot()).esplorative_for("BUSDT") == []
    monkeypatch.setattr(settings, "ESPLORATIVE_ENABLED", True)
    monkeypatch.setattr(settings, "REQUIRE_GATE1_READY", True)
    assert AdaptationEngine(_fb_bot(ready=False)).esplorative_for("BUSDT") == []


def test_un_registro_esplorativo_rotto_non_ferma_il_caricamento(capsys):
    fb = _fb_bot()
    fb.set_doc("strategy_registry", "esplorative", {"pairs": "{non json", "specs": 12})
    eng = AdaptationEngine(fb)
    assert eng._esplorative == {} and eng.esplorative_for("BUSDT") == []
    assert eng.is_enabled("AUSDT", "gen_a") is True


# --------------------------------------------------------------------------- #
# 5. l'orchestratore: precedenza e tetto                                        #
# --------------------------------------------------------------------------- #
def test_la_validata_vince_sulla_stessa_coin_e_l_esplorativa_apre_altrove(monkeypatch, capsys):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "DRY_RUN", True)
    o = _orch({"BTCUSDT": {"mean_reversion"}}, ["BTCUSDT|gen_x", "ETHUSDT|gen_x"])
    dec = o.decide_all({"BTCUSDT": _asset("BTCUSDT"), "ETHUSDT": _asset("ETHUSDT")}, Regime.SIDEWAYS)
    per_coin = {x.asset: x for x in dec}
    assert per_coin["BTCUSDT"].strategy == "mean_reversion" and per_coin["BTCUSDT"].esplorativa is False
    assert per_coin["ETHUSDT"].strategy == "gen_x" and per_coin["ETHUSDT"].esplorativa is True
    assert "[rifiuto]" not in capsys.readouterr().out        # la precedenza non e' un rifiuto


def test_la_validata_vince_anche_se_il_suo_segnale_viene_rifiutato_per_peso(monkeypatch):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "DRY_RUN", True)
    o = _orch({"BTCUSDT": {"mean_reversion"}}, ["BTCUSDT|gen_x"])
    o.adaptation._weights = {f"mean_reversion|{r.value}": 0.3 for r in Regime}
    # dal 26 set 2026 (pavimento della panchina) il peso 0,3 non rifiuta: la
    # validata passa a size ridotta e l'esplorativa cade comunque
    dec = o.decide_all({"BTCUSDT": _asset("BTCUSDT")}, Regime.SIDEWAYS)
    assert [(d.strategy, d.peso_size) for d in dec] == [("mean_reversion", 0.3)]
    # col pavimento spento torna il rifiuto di prima, e la precedenza resta
    monkeypatch.setattr(settings, "PANCHINA_PAVIMENTO", 0.0)
    assert o.decide_all({"BTCUSDT": _asset("BTCUSDT")}, Regime.SIDEWAYS) == []


def test_il_tetto_di_esplorative_aperte_rifiuta_e_conta(monkeypatch, capsys):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "DRY_RUN", True)
    monkeypatch.setattr(settings, "ESPLORATIVE_MAX_APERTE", 3)
    coins = ["AUSDT", "BUSDT", "CUSDT", "DUSDT"]
    # una validata altrove: senza validate il bot e' flat e il paper esplorativo
    # non parte (regola di `esplorative_for`)
    o = _orch({"ZUSDT": {"mean_reversion"}}, [f"{s}|gen_x" for s in coins])
    dec = o.decide_all({s: _asset(s) for s in coins}, Regime.SIDEWAYS)
    assert len(dec) == 3 and all(x.esplorativa for x in dec)
    righe = [r for r in capsys.readouterr().out.splitlines() if r.startswith("[rifiuto]")]
    assert len(righe) == 1 and righe[0].endswith("gen_x: esplorative al tetto (3 aperte)")
    assert o.rifiuti_ciclo() == [{"motivo": "esplorative al tetto", "n": 1}]
    # con 3 gia' aperte (le passa main) non se ne apre nessuna
    dec = o.decide_all({s: _asset(s) for s in coins}, Regime.SIDEWAYS, esplorative_aperte=3)
    assert dec == [] and o.rifiuti_ciclo() == [{"motivo": "esplorative al tetto", "n": 4}]
    assert "esplorative al tetto" in MOTIVI_RIFIUTO
    assert motivo_rifiuto("esplorative al tetto (3 aperte)") == "esplorative al tetto"


def test_fuori_parita_decide_ignora_le_esplorative(monkeypatch):
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "DRY_RUN", True)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    o = _orch({"ZUSDT": {"mean_reversion"}}, ["AUSDT|gen_x"])
    assert o.decide({"AUSDT": _asset("AUSDT")}, Regime.SIDEWAYS) is None


# --------------------------------------------------------------------------- #
# 6. main: size a un quarto e la marca                                          #
# --------------------------------------------------------------------------- #
def _decision(esplorativa: bool) -> OrchestratorDecision:
    return OrchestratorDecision(asset="BTCUSDT", strategy="gen_x", direction=Direction.LONG,
                                size_multiplier=1.0, confidence=60.0, esplorativa=esplorativa)


def _bot(monkeypatch):
    """TradingBot minimo per `_try_open`: ogni controllo passa, e si registra
    cosa arriva al risk gate e all'executor."""
    from bot.main import TradingBot
    monkeypatch.setattr(settings, "RISK_PER_COIN_DAY", 0.0)
    monkeypatch.setattr(settings, "BACKTEST_PARITY", True)
    monkeypatch.setattr(settings, "AI_VETO_ENABLED", False)
    monkeypatch.setattr(settings, "SENTIMENT_TILT_ENABLED", False)
    monkeypatch.setattr(settings, "ESPLORATIVA_SIZE_MULT", 0.25)
    b = types.SimpleNamespace()
    b.visto = {}
    params = types.SimpleNamespace(approved=True, stop_price=92.0, take_profit_price=98.0,
                                   quantity=1.0, leverage=2.0)

    def evaluate(decision, user, asset, equity, **kw):
        b.visto["risk_mult"] = kw.get("risk_mult")
        b.visto["alloc_note"] = kw.get("alloc_note")
        return params

    def open_position(asset, strategy, direction, params, **kw):
        b.visto["open"] = kw
        return types.SimpleNamespace(symbol=asset.symbol, strategy=strategy, direction=direction,
                                     entry_price=asset.price, quantity=1.0, leverage=2.0,
                                     stop_price=92.0, take_profit_price=98.0)

    b.executor = types.SimpleNamespace(open_positions={}, open_position=open_position)
    b._coin_cooldown = {}
    b._used_margin = lambda: 0.0
    b.account_equity = lambda: 1000.0
    b.selected = {"BTCUSDT": _asset()}
    b._last_shadow = None
    b._correlation_blocks = lambda sym: None
    b.sentiment = types.SimpleNamespace(get_sentiment=lambda s: {})
    b.read_user_risk = lambda: None
    b.adaptation = types.SimpleNamespace(allocation=lambda *a, **k: (1.0, 1.0, "alloc"),
                                         params_for=lambda s: {}, timeframe_for=lambda s: None)
    b.risk = types.SimpleNamespace(evaluate=evaluate)
    b._volatility_sigma = lambda a: 0.0
    b.regime = Regime.SIDEWAYS
    b.regime_confidence = 0.8
    b._directional_risk_blocks = lambda d, r: None
    b._ombra_selettore = lambda *a, **k: (None, None)
    b._sync_stream_symbols = lambda: None
    b.stream = None
    b._publish_decision_status = lambda *a, **k: None
    b.notifier = types.SimpleNamespace(trade_opened=lambda *a, **k: None)
    b.orchestrator = types.SimpleNamespace(conta_scarto=lambda *a, **k: None)
    b.fattore_size_esplorativa = TradingBot.fattore_size_esplorativa
    b._try_open = types.MethodType(TradingBot._try_open, b)
    b._esplorative_aperte = types.MethodType(TradingBot._esplorative_aperte, b)
    return b


def test_una_decisione_esplorativa_apre_a_un_quarto_e_marcata(monkeypatch, capsys):
    b = _bot(monkeypatch)
    b._try_open(_decision(True), NOW)
    assert b.visto["risk_mult"] == pytest.approx(0.25)
    assert "esplorativa x0.25" in b.visto["alloc_note"]
    assert b.visto["open"]["esplorativa"] is True
    assert "[esplorativa] BTCUSDT gen_x long size x0.25" in capsys.readouterr().out


def test_una_validata_apre_a_size_piena_e_senza_marca(monkeypatch, capsys):
    b = _bot(monkeypatch)
    b._try_open(_decision(False), NOW)
    assert b.visto["risk_mult"] == 1.0 and b.visto["open"]["esplorativa"] is False
    assert "[esplorativa]" not in capsys.readouterr().out


def test_gli_altri_controlli_restano_e_main_passa_le_aperte_all_orchestratore(monkeypatch):
    from bot.main import TradingBot
    b = _bot(monkeypatch)
    b.executor.open_positions = {"BTCUSDT": types.SimpleNamespace(esplorativa=True),
                                 "ETHUSDT": types.SimpleNamespace(esplorativa=False)}
    b._try_open(_decision(True), NOW)
    assert "open" not in b.visto                 # «posizione gia' aperta»: come per una validata
    assert b._esplorative_aperte() == 1
    src = inspect.getsource(TradingBot._try_open)
    # dal 26 set 2026 il fattore applicato e' il MINIMO fra esplorativa e declassata
    assert "rmult *= _f_rid" in src and "esplorativa=bool(getattr(decision, \"esplorativa\", False))" in src
    assert "esplorative_aperte=self._esplorative_aperte()" in inspect.getsource(TradingBot)
    assert TradingBot.fattore_size_esplorativa(types.SimpleNamespace()) == 1.0


# --------------------------------------------------------------------------- #
# 7. executor e modelli: la marca segue il trade                                #
# --------------------------------------------------------------------------- #
def _params():
    from bot.core.models import EffectiveRiskParams
    return EffectiveRiskParams(leverage=3.0, risk_per_trade=0.01, notional=100.0, quantity=1.0,
                               stop_price=98.0, take_profit_price=104.0, user_leverage=3,
                               user_risk_per_trade=0.01, safety_leverage_cap=5, safety_risk_cap=0.03,
                               approved=True)


def test_la_posizione_porta_la_marca_la_persiste_la_ripristina_e_la_mette_sul_trade():
    fb = FirebaseClient()
    eng = ExecutionEngine(firebase=fb, dry_run=True)
    asset = AssetSnapshot(symbol="BTCUSDT", price=100.0, regime=Regime.SIDEWAYS,
                          indicators={"15m": IndicatorSnapshot(timeframe="15m", atr=2.0, close=100.0)})
    pos = eng.open_position(asset, "gen_x", Direction.LONG, _params(), esplorativa=True)
    assert pos.esplorativa is True
    assert fb.get_rtdb("/positions/BTCUSDT")["esplorativa"] is True
    # dopo un riavvio (il costruttore ricarica da solo; la chiamata esplicita e' idempotente)
    eng2 = ExecutionEngine(firebase=fb, dry_run=True)
    eng2.restore_open_positions()
    assert eng2.open_positions["BTCUSDT"].esplorativa is True
    # documenti vecchi senza la chiave -> validata
    stato = dict(fb.get_rtdb("/positions/BTCUSDT"))
    stato.pop("esplorativa")
    assert eng2._position_from_state(stato).esplorativa is False
    # e il trade chiuso
    ct = eng2._build_closed_trade(eng2.open_positions["BTCUSDT"], 104.0, ExitReason.TAKE_PROFIT)
    assert ct.esplorativa is True
    pos_v = eng.open_position(AssetSnapshot(symbol="ETHUSDT", price=100.0, regime=Regime.SIDEWAYS),
                              "gen_a", Direction.LONG, _params())
    assert pos_v.esplorativa is False
    assert eng._build_closed_trade(pos_v, 98.0, ExitReason.STOP_LOSS).esplorativa is False
    assert OrchestratorDecision(asset="X", strategy="s", direction=Direction.LONG, size_multiplier=1,
                                confidence=50).esplorativa is False


# --------------------------------------------------------------------------- #
# 8. il learning: fuori dai pesi, dal keep, dalla deriva, dalla calibrazione;   #
#    dentro i referti                                                           #
# --------------------------------------------------------------------------- #
def test_i_pesi_e_il_keep_ignorano_i_trade_esplorativi(capsys):
    validate = [{**_t(-5.0), "regime_at_entry": "sideways"} for _ in range(4)]
    esplorativi = [_t(10.0, esplorativa=True) for _ in range(20)]
    w = metrics.compute_weights(validate + esplorativi)
    assert len(w) == 1 and w[0].sample_size == 4 and w[0].win_rate == 0.0
    assert "esplorativi: 20" in capsys.readouterr().out
    # keep del trailing: 20 verdetti prematuri esplorativi non muovono nulla
    trailing = [_t(3.0, esplorativa=True, reason="trailing_stop") for _ in range(20)]
    assert metrics.compute_trailing_keep(trailing) == {}
    assert metrics.esplorativo(trailing[0]) is True and metrics.esplorativo(_t()) is False


def test_la_deriva_globale_e_per_coppia_ignora_i_trade_esplorativi():
    pairs = {"AUSDT|gen_a": {"last_pf": 1.5, "last_params": {"scale_r_mults": [1.5, 3, 5]}}}
    esplorativi = [_t(-5.0, esplorativa=True, sym="AUSDT", strat="gen_a") for _ in range(40)]
    doc = compute_drift(esplorativi, pairs)
    assert doc["pairs"] == {} and doc["global"] == {} and doc["serie"] == {}
    misti = esplorativi + [_t(8.0, sym="AUSDT", strat="gen_a") for _ in range(3)]
    doc = compute_drift(misti, pairs)
    assert doc["pairs"]["AUSDT|gen_a"]["trades"] == 3 and doc["global"]["trades"] == 3
    assert doc["global"]["verdict"] == "ok"


def test_la_calibrazione_ignora_i_trade_esplorativi(monkeypatch):
    monkeypatch.setattr(settings, "CALIBRATION_MIN_TRADES", 30)
    esplorativi = [_t(-5.0 if i % 2 else 5.0, esplorativa=True, conf=40.0 + i) for i in range(40)]
    assert calibrate(esplorativi)["trades"] == 0
    assert calibrate(esplorativi + [_t(1.0, conf=50.0), _t(-1.0, conf=70.0)])["trades"] == 2


def test_i_referti_includono_i_trade_esplorativi_e_li_contano():
    trades = [_t(-5.0, esplorativa=True, strat="gen_x") for _ in range(3)] + [_t(-5.0, strat="gen_a")]
    doc = aggrega_referti(trades)
    assert doc["n_trades"] == 4 and doc["esplorative"] == 3
    assert doc["per_strategia"]["gen_x"]["n"] == 3
    # e l'ipotesi nasce anche da soli trade esplorativi (3 long tutti persi -> solo_short)
    assert any(h["strategia"] == "gen_x" and h["tipo"] == "solo_short" for h in doc["ipotesi"])
    assert aggrega_referti([_t()])["esplorative"] == 0


# --------------------------------------------------------------------------- #
# 9. il controllo orario: a parte, e l'equity torna                             #
# --------------------------------------------------------------------------- #
def test_il_controllo_tiene_il_paper_esplorativo_a_parte():
    from tests.test_controllo import NOW as NOW_C
    from tests.test_controllo import _fb, _trade
    esplorativi = [_trade(100 + i, 4.0 if i % 2 else -6.0, sym="EUSDT", strat="gen_x", esplorativa=True)
                   for i in range(5)]
    validate = [_trade(i, 5.0 if i % 3 else -4.0) for i in range(9)]
    fb = _fb(trades=validate + esplorativi)
    fb.set_rtdb("/positions/EUSDT", {"symbol": "EUSDT", "strategy": "gen_x", "direction": "long",
                                     "entry_price": 1.0, "quantity": 1.0, "leverage": 2.0,
                                     "unrealized_pnl": 0.0, "realized_partial": 0.0,
                                     "risk_effective_pct": 0.001, "esplorativa": True})
    fb.set_doc("strategy_registry", "esplorative", {
        "pairs": encode_pairs({"EUSDT|gen_x": {}, "FUSDT|gen_y": {}}), "specs": encode_pairs({}),
        "storia": encode_pairs({})})
    doc = c.costruisci_controllo(c.carica_dati(fb, NOW_C), NOW_C, "bot", settings_da_bot=True, durata_ms=10)
    p = doc["paper"]
    assert p["trades"] == 9 and p["pnl_realizzato"] == pytest.approx(sum(t["pnl"] for t in validate))
    assert p["esplorative"] == {"trades": 5, "vinti": 2, "pnl": -10.0, "aperte": 1, "coppie_attive": 2}
    assert "fs:strategy_registry/esplorative" in p["fonti"] and "esplorativ" in p["dettaglio"]
    codici = {a["codice"] for a in doc["salute"]["anomalie"]}
    assert "EQUITY_NON_TORNA" not in codici     # l'equity del conto comprende gli esplorativi
    # senza registro esplorativo: coppie null, non zero
    fb2 = _fb(trades=validate)
    p2 = c.costruisci_controllo(c.carica_dati(fb2, NOW_C), NOW_C, "bot", True, 10)["paper"]
    assert p2["esplorative"] == {"trades": 0, "vinti": 0, "pnl": 0.0, "aperte": 0, "coppie_attive": None}


# --------------------------------------------------------------------------- #
# 10. gli script: `trades` e `gate`                                             #
# --------------------------------------------------------------------------- #
def test_trade_stats_esclude_gli_esplorativi_e_stampa_la_sezione(monkeypatch, capsys):
    from tests.test_controllo import _trade
    validate = [_trade(i, 5.0) for i in range(3)]
    esplorativi = [_trade(10 + i, -2.0, sym="EUSDT", strat="gen_x", esplorativa=True) for i in range(4)]
    esplorativi.append(_trade(20, 9.0, sym="FUSDT", strat="gen_y", esplorativa=True))
    fb = FirebaseClient()
    for t in validate + esplorativi:
        fb.set_doc("trades", t["trade_id"], t)
    fb.set_doc("strategy_registry", "esplorative", {
        "pairs": encode_pairs({"EUSDT|gen_x": {}}), "specs": encode_pairs({}),
        "storia": encode_pairs({"GUSDT|gen_g": {"esito": "validata"}, "HUSDT|gen_h": {"esito": "scartata"},
                                "IUSDT|gen_i": {"esito": "scartata"}})})
    monkeypatch.setattr(ts, "get_firebase", lambda: fb)
    assert ts.main() == 0
    out = capsys.readouterr().out
    assert "Trade totali analizzati: 3 " in out
    assert "PAPER ESPLORATIVO" in out
    assert "coppie attive adesso: 1" in out
    assert "trade chiusi: 5 · vinti 1 · PnL +1.00" in out
    assert "EUSDT|gen_x" in out and "4 trade · 0 vinti · -8.00" in out
    assert "coppie esplorative poi validate 1 / scartate 2" in out
    rep = ts.esplorativo_report(validate + esplorativi, None)
    assert rep["validate_poi"] is None and rep["per_coppia"][0]["coppia"] == "EUSDT|gen_x"


def test_gate_progress_stampa_la_riga_delle_esplorative():
    assert g.riga_esplorative(None) == ("  ESPLORATIVE: registro non ancora scritto dal gate "
                                        "(paper esplorativo, F1bis)")
    doc = {"pairs": encode_pairs({"A|gen_a": {}, "B|gen_b": {}}),
           "storia": encode_pairs({"C|gen_c": {"esito": "validata"}, "D|gen_d": {"esito": "scartata"}})}
    assert g.riga_esplorative(doc) == "  ESPLORATIVE: 2 attive · validate poi 1 · scartate 1"
    assert "riga_esplorative(" in inspect.getsource(g.main)


def test_la_configurazione_e_quella_dichiarata_e_il_backlog_dice_fatto():
    assert settings.ESPLORATIVE_ENABLED is True
    assert settings.ESPLORATIVA_SIZE_MULT == 0.25
    assert settings.ESPLORATIVE_MAX_APERTE == 3 and settings.ESPLORATIVE_MAX == 20
    import os
    root = os.path.join(os.path.dirname(__file__), "..")
    with open(os.path.join(root, "docs", "backlog.md"), encoding="utf-8") as f:
        assert "### F1bis." in f.read() and True
    with open(os.path.join(root, "docs", "backlog.md"), encoding="utf-8") as f:
        riga = next(r for r in f if r.startswith("### F1bis."))
    assert "FATTO il 25 set" in riga
