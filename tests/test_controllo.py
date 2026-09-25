"""IL CONTROLLO AUTOMATICO — il documento orario `dashboard/controllo` (25 set 2026).

Il contratto e' docs/controllo_schema.md. Qui si verifica che il documento lo
rispetti: le chiavi di ogni sezione, la serializzazione (niente NaN/inf, niente
`. # $ [ ] /` nelle chiavi), la dimensione (< 30 KB con una fixture realistica),
ogni anomalia con la sua condizione, il fail-open per sezione, l'impronta e i
cambiamenti, le giornate in UTC, il PF nullo senza perdite, i contatori dei
rifiuti, il guard orario del bot (sul sorgente, come tests/test_referti.py),
`reconcile_equity` che scrive il capitale iniziale UNA volta.

Il Firebase e' quello in memoria di `FirebaseClient` (conftest svuota le
credenziali): stesse letture e scritture del bot, nessuna rete.
"""
from __future__ import annotations

import inspect
import json
import time
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from bot.config import settings
from bot.core.firebase_client import FirebaseClient, decode_pairs, encode_pairs
from bot.learning import controllo as c
from bot.learning.metrics import classi_stop
from bot.orchestrator.orchestrator import Orchestrator, motivo_rifiuto

# meta' giornata UTC: le giornate di `oggi` non scavallano la mezzanotte nei test
NOW = datetime(2026, 9, 25, 12, 0, tzinfo=timezone.utc).timestamp()


# --------------------------------------------------------------------------- #
# attrezzi                                                                    #
# --------------------------------------------------------------------------- #
def _iso(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _trade(i: int, pnl: float, exit_reason: str = "stop_loss", sym: str = "AUSDT",
           strat: str = "gen_a", direction: str = "long", exit_ts: float | None = None,
           mfe_r: float | None = None, **extra) -> dict:
    exit_ts = (NOW - i * 5 * 3600) if exit_ts is None else exit_ts
    t = {"trade_id": f"t{i}", "symbol": sym, "strategy": strat, "direction": direction,
         "timeframe": settings.ORCHESTRATOR_TIMEFRAME,
         "entry_time": _iso(exit_ts - 7200), "exit_time": _iso(exit_ts),
         "entry_price": 100.0, "exit_price": 100.0 + pnl, "size": 1.0, "notional": 100.0,
         "leverage": 3.0, "pnl": pnl, "pnl_pct": pnl / 10, "exit_reason": exit_reason,
         "regime_at_entry": "sideways", "exit_ts": exit_ts, "duration_seconds": 7200,
         "is_win": pnl > 0, "scale_stage_reached": 1 if pnl > 0 else 0,
         "mfe_r": mfe_r if mfe_r is not None else (0.1 if pnl < 0 else 2.0),
         "total_cost_usdt": 0.2, "commission_usdt": 0.1, "spread_usdt": 0.1,
         "funding_paid_usdt": 0.0, "gross_pnl_usdt": pnl + 0.2, "costs_are_estimated": True,
         "confidence_at_entry": 60.0, "post_mortem": {"classe": "ingresso", "stop_largo": False,
                                                       "lock_mai_armato": True, "controtrend": False,
                                                       "verdetto": "x", "stop_pct": 0.02}}
    t.update(extra)
    return t


def _trades_realistici(n: int = 54) -> list[dict]:
    out = []
    for i in range(n):
        k = i % 6
        if k in (0, 1, 2):
            out.append(_trade(i, -5.0 - k, "stop_loss", sym=f"C{i % 9}USDT", strat=f"gen_{i % 7}",
                              direction="long" if i % 2 else "short", mfe_r=0.1 + 0.3 * k))
        elif k == 3:
            out.append(_trade(i, 8.0, "scale_out", sym=f"C{i % 9}USDT", strat=f"gen_{i % 7}",
                              trailing_verdict="premature", trailing_knockout_atr=0.5))
        elif k == 4:
            out.append(_trade(i, 3.0, "trailing_stop", sym=f"C{i % 9}USDT", strat=f"gen_{i % 7}",
                              trailing_verdict="protected"))
        else:
            out.append(_trade(i, 12.0, "take_profit", sym=f"C{i % 9}USDT", strat=f"gen_{i % 7}",
                              scale_stage_reached=3))
    return out


def _registro(n_pairs: int = 160) -> dict:
    pairs = {}
    for i in range(n_pairs):
        k = f"C{i % 40}USDT|gen_{i}"
        pairs[k] = {"generated": True, "pass_count": 3, "last_pf": 1.5 + (i % 5) / 10,
                    "last_pnl_pct": 0.3, "last_seen_at": NOW - 3600, "validated_at": NOW - 86400 * 3,
                    "last_params": {"scale_r_mults": [1.5, 3, 5] if i % 2 else [1.0, 2.0, 3.0],
                                    "profit_lock_keep": 0.5 if i % 3 else 0.25,
                                    "sl_to_breakeven": True}}
    if n_pairs > 5:
        pairs["C1USDT|gen_1"]["last_params"].pop("profit_lock_keep")   # non rivalutata
    return {"pairs": encode_pairs(pairs), "validated": sorted(pairs), "ready": True,
            "coverage": 0.7, "ready_fraction": 0.6, "coins_covered": 40, "universe_size": 57,
            "updated_at": NOW - 1800, "min_passes": 3}


def _pesi(n: int = 20) -> dict:
    ws = []
    for i in range(n):
        ws.append({"strategy": f"gen_{i % 7}", "regime": ["sideways", "bull_trending", "bear_trending"][i % 3],
                   "weight": round(0.2 + 0.05 * i, 4) if i < 8 else 1.0, "win_rate": 0.4, "avg_rr": 1.2,
                   "sample_size": 3 + i})
    return {"weights": ws, "updated_at": NOW - 600, "version": 41, "trade_count_used": 54}


def _drift(verdetto: str = "ok") -> dict:
    pairs = {}
    for i in range(30):
        v = "drift" if i < 3 else ("watch" if i < 10 else "ok")
        pairs[f"C{i}USDT|gen_{i % 7}"] = {"verdict": v, "reason": "PF 0.50 vs 1.60 atteso" if v != "ok" else "",
                                          "trades": 2 + i % 6, "live_pf": 0.5 if v != "ok" else 99.0,
                                          "expected_pf": 1.6, "pnl": -3.0, "mfe_median": 0.8, "first_rung_r": 1.5}
    glob = {"verdict": verdetto, "reason": "PF 0.64 vs 1.89 atteso" if verdetto == "drift" else "",
            "trades": 54, "live_pf": 0.64, "expected_pf": 1.89, "pnl": -46.65, "mfe_median": 0.84,
            "first_rung_r": 1.5}
    if verdetto == "drift":
        glob["dal"] = NOW - 3 * 86400
    return {"pairs": pairs, "strategies": {}, "global": glob,
            "serie": {"gen_1": 4, "gen_2": 2, "gen_3": 1}, "updated_at": NOW - 900}


def _gate() -> dict:
    return {"meta": {"versione_schema": 1, "stato": "finito", "fase": None, "errore": None,
                     "iniziato_at": NOW - 5400, "generato_at": NOW - 5400 + 2400, "durata_s": 2400,
                     "modalita": "solo urgenti", "generato_da": "discovery"},
            "registro": {"validate": 160, "occupazione": 1800, "limite": 3000, "pronto": True},
            "strategie": {"n_operate": 160, "n_senza_promessa": 10}}


def _popola(fb: FirebaseClient, trades=None, n_pos: int = 4, verdetto_drift: str = "ok") -> None:
    """Un Firebase «realistico»: 54 trade, 4 posizioni (12 nel test di dimensione:
    sopra il tetto di 5 il cap scatta, fuori parita'), 160 validate, 20 pesi.
    L'equity TORNA coi trade (1000 + somma dei pnl): la fixture e' sana."""
    trades = _trades_realistici() if trades is None else list(trades)
    fb.set_rtdb("/bot_status", {"state": "running", "regime": "sideways", "dry_run": True,
                                "updated_at": NOW - 1200, "fear_greed": 41, "price_stream": True,
                                "heartbeat": NOW - 22, "avviato_at": NOW - 86400 * 2,
                                "errori_ciclo_1h": 0, "btc_close": 60000.0, "regime_detail": {}})
    fb.set_rtdb("/bot_status/heartbeat", NOW - 22)
    fb.set_rtdb("/commands/kill_switch", False)
    fb.set_rtdb("/commands/maintenance", False)
    fb.set_rtdb("/decision_status", {"ts": NOW - 300, "outcome": "flat", "regime": "sideways",
                                     "reason": "nessun segnale valido sopra soglia",
                                     "assets_evaluated": 40, "signals_found": 3,
                                     "rifiuti_ciclo": [{"motivo": "cooldown", "n": 2}],
                                     "rifiuti_24h": [{"motivo": "cooldown", "n": 12},
                                                     {"motivo": "margine", "n": 3}],
                                     "rifiuti_24h_dal": NOW - 86400 * 2})
    fb.set_rtdb("/risk_state", {"daily_pnl_pct": -0.004, "day_key": "2026-09-25", "consecutive_sl": 1,
                                "paused_until_ts": 0.0, "macro_flat_until_ts": 0.0,
                                "halted_for_day": False, "notes": []})
    fb.set_rtdb("/adapt_state", {"coin_cooldown": {"AUSDT": NOW + 3600, "BUSDT": NOW - 10},
                                 "strat_streak": {"gen_1": 2},
                                 "strat_cooldown": {"gen_9": NOW + 7200}, "updated_at": NOW - 100})
    for i in range(n_pos):
        fb.set_rtdb(f"/positions/P{i}USDT", {
            "symbol": f"P{i}USDT", "strategy": f"gen_{i % 7}", "direction": "long" if i % 2 else "short",
            "entry_price": 10.0, "mark_price": 10.1, "quantity": 5.0, "leverage": 3.0,
            "stop_price": 9.8, "take_profit_price": 10.6, "unrealized_pnl": 0.5 - 0.1 * i,
            "realized_partial": 0.0, "risk_effective_pct": 0.004, "entry_time": _iso(NOW - 3600 * (i + 1)),
            "tp_ladder": [{"price": 10.3, "fraction": 0.5, "r": 1.5, "hit": False}] * 3,
            "indicators_at_entry": {"15m": {"rsi": 30.0, "atr": 0.2}}})
    fb.set_rtdb("/account/equity", round(1000.0 + sum(float(t["pnl"]) for t in trades), 2))
    fb.set_rtdb("/account/starting_equity", 1000.0)
    fb.set_rtdb("/account/paper_started_at", NOW - 10 * 86400)
    fb.set_rtdb("/avvii", [NOW - 86400 * 5, NOW - 86400 * 2])
    fb.set_rtdb("/btc_history", [{"ts": NOW - 3600 * (199 - i), "close": 60000.0 + 10.0 * i}
                                 for i in range(200)])
    fb.set_doc("dashboard", "gate", _gate())
    fb.set_doc("strategy_registry", "validated", _registro())
    fb.set_doc("strategy_weights", "current", _pesi())
    fb.set_doc("drift", "current", _drift(verdetto_drift))
    fb.set_doc("calibration", "current", {"verdict": "constant", "trades": 54, "correlation": None,
                                          "trust": 1.0, "note": "confidenza costante", "buckets": [],
                                          "updated_at": NOW - 900})
    fb.set_doc("learning", "referti", {
        "n_trades": 54, "n_con_referto": 40, "n_persi_con_referto": 25,
        "per_direzione": {"long": {"n": 30, "vinti": 12, "persi": 18, "pnl": -20.0, "ingresso": 9,
                                   "uscita": 4, "protezione": 1, "stop_largo": 2, "lock_mai": 7,
                                   "controtrend": 3},
                          "short": {"n": 24, "vinti": 10, "persi": 14, "pnl": -26.65, "ingresso": 6,
                                    "uscita": 3, "protezione": 2, "stop_largo": 1, "lock_mai": 5,
                                    "controtrend": 4}},
        "per_strategia": {}, "per_coin": {},
        "ipotesi": [{"strategia": "gen_1", "tipo": "solo_long", "motivo": "short 4/4 persi", "campione": 4}],
        "updated_at": NOW - 900})
    fb.set_doc("supervisor", "state", {"updated_at": NOW - 7200, "history": []})
    fb.set_doc("selector", "report", {"updated_at": _iso(NOW - 86400), "n_righe": 300,
                                      "verdetti": {"tutte": {"verdetto": "NON BATTE"}},
                                      "nota": "il bot NON usa il selettore"})
    for i in range(200):
        fb.set_doc("ai_shadow", str(i), {"at": NOW - 900 * i, "choice": None, "actual": None,
                                         "verdict": "agree" if i % 4 == 0 else "both_flat"})
    fb.set_doc("ai_hypotheses", "last", {"proposte": 20, "accettate": 14, "at": NOW - 5000})
    fb.set_doc("memory", "30", {"generated_at": _iso(NOW - 40000), "total_trades": 54})
    fb.set_doc("strategy_params", "discovered_last_run", {"started_at": NOW - 6000, "duration_s": 2400})
    for t in trades:
        fb.set_doc("trades", t["trade_id"], t)


def _fb(**kw) -> FirebaseClient:
    fb = FirebaseClient()
    _popola(fb, **kw)
    return fb


def _doc(fb=None, now: float = NOW, generato_da: str = "bot", durata_ms=None, **kw) -> dict:
    fb = fb or _fb(**kw)
    dati = c.carica_dati(fb, now)
    return c.costruisci_controllo(dati, now, generato_da, settings_da_bot=(generato_da == "bot"),
                                  durata_ms=durata_ms)


def _codici(doc: dict) -> dict:
    return {a["codice"]: a for a in doc["salute"]["anomalie"]}


# --------------------------------------------------------------------------- #
# 1. lo schema: le chiavi di ogni sezione                                       #
# --------------------------------------------------------------------------- #
META = {"versione_schema", "generato_at", "generato_da", "durata_ms", "precedente_at",
        "semaforo_sistema", "semaforo_paper", "errori", "fonte_impostazioni"}
TESTATA = {"computed_at", "fonti", "lettura", "errore"}
SALUTE = {"bot_stato", "heartbeat_at", "heartbeat_eta_s", "soglia_online_s", "avviato_at",
          "riavvii_24h", "errori_ciclo_1h", "price_stream", "dry_run", "kill_switch", "manutenzione",
          "regime", "fear_greed", "btc_24h_pct", "btc_7g_pct", "ultima_decisione_at",
          "ultima_decisione_esito", "ultima_decisione_motivo", "asset_valutati", "segnali_trovati",
          "rifiuti_ciclo", "rifiuti_24h", "rifiuti_24h_dal", "gate_ultimo_giro_at",
          "gate_ultimo_giro_eta_s", "gate_stato", "gate_modalita", "gate_pronto", "registro_at",
          "pesi_at", "deriva_at", "calibrazione_at", "referti_at", "supervisore_at", "freno_globale",
          "freno_globale_dal", "circuit_breaker", "cooldown_coin", "cooldown_strategie",
          "posizioni_aperte", "posizioni", "upnl_totale", "tetto_posizioni", "tetto_posizioni_attivo",
          "rischio_aperto_pct", "rischio_long_pct", "rischio_short_pct", "tetto_direzione_pct",
          "wal_non_vuoto", "rtdb_degradato_s", "controllo_precedente_eta_s", "anomalie"}
PAPER = {"equity", "equity_iniziale", "equity_iniziale_fonte", "paper_dal", "paper_dal_fonte",
         "giorni_paper", "rendimento_pct", "trades", "vinti", "perdite", "win_rate", "pnl_realizzato",
         "pf_vissuto", "expectancy", "ultimi_30g", "oggi", "giornate", "uscite", "gradini", "mfe",
         "stop", "direzione", "allineamento", "costi", "drawdown_portafoglio",
         "max_posizioni_insieme", "trailing", "benchmark"}
ATTIVO = {"freno_globale", "gate_pronto", "pesi", "tilt", "keep_per_coppia", "freno_serie", "tetti",
          "cooldown_attivi", "calibrazione_trust", "impronta", "cambiamenti_24h"}
MISURATO = {"deriva", "calibrazione", "trailing", "referti", "selettore", "ombra_ai", "ipotesi_ai",
            "notturno_at"}


def test_le_chiavi_di_ogni_sezione_sono_quelle_del_contratto():
    doc = _doc()
    assert doc["meta"]["errori"] == []
    assert set(doc) == {"meta", "salute", "paper", "learning", "manca"}
    assert set(doc["meta"]) == META
    assert TESTATA | SALUTE <= set(doc["salute"])
    assert TESTATA | PAPER <= set(doc["paper"])
    assert TESTATA | {"attivo", "misurato"} <= set(doc["learning"])
    assert TESTATA | ATTIVO <= set(doc["learning"]["attivo"])
    assert TESTATA | MISURATO <= set(doc["learning"]["misurato"])
    # sottochiavi con nomi fissati dal contratto
    assert set(doc["paper"]["stop"]) == {"totale", "sbagliati", "quasi", "oltre_primo_tp",
                                         "quasi_durata_mediana_h", "primo_gradino_r", "nota"}
    assert set(doc["paper"]["trailing"]) == {"verdetti_totali", "prematuri", "protetti", "neutri",
                                             "verdetti_per_proposta", "prematuri_tf", "protetti_tf",
                                             "proposta_paper", "soglia"}
    assert set(doc["paper"]["costi"]) == {"totale", "per_trade", "commissioni", "spread", "funding",
                                          "lordo", "netto", "break_even_pct", "stimati", "avvisi"}
    assert set(doc["learning"]["attivo"]["freno_globale"]) == {
        "attivo", "verdetto", "trades", "pf_vissuto", "pf_atteso", "pf_atteso_nota",
        "soglia_uscita_pf", "size_x", "leva_x_min", "motivo", "dal"}
    assert set(doc["learning"]["attivo"]["impronta"]) == {"freno", "panchina", "cooldown", "keep",
                                                          "validate", "gate_pronto"}
    assert set(doc["paper"]["direzione"]["long"]) == {"trade", "vinti", "pnl", "mfe_mediana"}
    assert [set(r) for r in doc["manca"]] == [{"evidenza", "perche", "come_avere"}] * 3
    assert doc["meta"]["fonte_impostazioni"] == "processo bot"
    assert doc["meta"]["versione_schema"] == 1


def test_i_numeri_della_fixture_arrivano_dove_dice_il_contratto():
    doc = _doc(n_pos=12)
    s, p, a, m = doc["salute"], doc["paper"], doc["learning"]["attivo"], doc["learning"]["misurato"]
    assert s["heartbeat_eta_s"] == 22 and s["bot_stato"] == "running"
    assert s["posizioni_aperte"] == 12 and len(s["posizioni"]) == 12
    assert set(s["posizioni"][0]) == {"coin", "direzione", "rischio_pct", "upnl"}
    assert s["rischio_aperto_pct"] == pytest.approx(4.8)
    assert s["gate_ultimo_giro_eta_s"] == 3000 and s["gate_modalita"] == "solo urgenti"
    assert s["gate_pronto"] is True and s["riavvii_24h"] == 0
    assert s["cooldown_coin"] == [{"nome": "AUSDT", "fino_a": NOW + 3600}]
    assert s["rifiuti_24h"][0] == {"motivo": "cooldown", "n": 12}
    assert s["btc_24h_pct"] == pytest.approx((61990 / 61750 - 1) * 100, abs=0.01)
    assert s["rtdb_degradato_s"] == 0.0
    assert p["equity"] == 1045.0 and p["equity_iniziale_fonte"] == "rtdb"
    assert p["giorni_paper"] == 10 and p["paper_dal_fonte"] == "rtdb"
    assert p["trades"] == 54 and p["vinti"] == 27 and p["perdite"] == 27
    assert p["rendimento_pct"] == pytest.approx(4.5, abs=0.01) and p["pnl_realizzato"] == 45.0
    assert p["ultimi_30g"]["pf"] == 0.64 and p["ultimi_30g"]["trades"] == 54
    assert p["stop"]["totale"] == 27 and p["stop"]["nota"].startswith("primo gradino per coppia")
    assert p["trailing"]["prematuri"] == 9 and p["trailing"]["protetti"] == 9
    assert p["trailing"]["prematuri_tf"] == 0 and p["trailing"]["protetti_tf"] == 9
    assert p["trailing"]["proposta_paper"] == 0.75      # 9/9 protetti >= 60% con >= 8 verdetti
    assert p["max_posizioni_insieme"] >= 1 and p["drawdown_portafoglio"] > 0
    assert p["uscite"][0]["motivo"] == "stop_loss" and p["uscite"][0]["etichetta"].startswith("Stop loss")
    assert a["pesi"]["in_panchina_n"] == 6 and a["pesi"]["combinazioni"] == 20
    assert a["keep_per_coppia"]["non_rivalutate"] == 1
    assert sum(k["n"] for k in a["keep_per_coppia"]["distribuzione"]) == 159
    assert a["impronta"]["validate"] == 160 and a["impronta"]["gate_pronto"] is True
    assert a["freno_serie"]["serie"][0] == {"strategia": "gen_1", "perdite": 4}
    assert a["calibrazione_trust"] == 1.0
    assert m["deriva"]["coppie_drift"] == 3 and m["deriva"]["coppie_watch"] == 7
    assert len(m["deriva"]["top"]) == 10 and m["deriva"]["top"][0]["verdetto"] == "drift"
    dr = _drift()
    dr["pairs"] = {"X|s": {"verdict": "ok", "trades": 3, "live_pf": 99.0, "expected_pf": 1.5, "reason": ""}}
    m2 = _con(c.carica_dati(_fb(), NOW), drift=dr)["learning"]["misurato"]
    assert m2["deriva"]["top"][0]["pf_vissuto"] is None          # 99 (senza perdite) -> null
    assert m["referti"]["lock_mai"] == 12 and m["referti"]["ipotesi"][0].startswith("gen_1: solo_long")
    assert m["ombra_ai"] == {"n": 200, "agree": 50, "ultimo_at": NOW}
    assert m["ipotesi_ai"] == {"proposte": 20, "accettate": 14, "at": NOW - 5000}
    assert m["selettore"]["verdetti"] == {"tutte": "NON BATTE"}
    assert m["notturno_at"] == pytest.approx(NOW - 40000)


def test_le_letture_sono_frasi_corte_da_regole():
    doc = _doc()
    for sez in ("salute", "paper", "learning"):
        assert 0 < len(doc[sez]["lettura"]) <= 140, doc[sez]["lettura"]
    assert doc["salute"]["lettura"] == ("Bot vivo (battito 22 s fa), gate 50 min fa (solo urgenti), "
                                        "4 posizioni, 1,6% a rischio. Nessun avviso.")
    assert doc["paper"]["lettura"].startswith("54 trade in 10 giorni, 50% vinti, +45,00 USDT (+4,5%).")
    assert "Stop nel 50% delle uscite" in doc["paper"]["lettura"]
    assert "Numeri piccoli" not in doc["paper"]["lettura"]
    assert doc["learning"]["lettura"].startswith("Attivo: 6 strategie in panchina, keep per coppia 0.25 ×54, 0.5 ×105, 2 cooldown.")
    assert "Solo misurato: deriva, calibrazione, 18 verdetti trailing" in doc["learning"]["lettura"]


def test_numeri_piccoli_e_niente_freno_nella_lettura_con_pochi_trade():
    doc = _doc(trades=_trades_realistici(5))
    assert "Numeri piccoli" in doc["paper"]["lettura"]
    assert doc["paper"]["trades"] == 5


# --------------------------------------------------------------------------- #
# 2. serializzazione e dimensione                                              #
# --------------------------------------------------------------------------- #
def test_pulisci_toglie_nan_inf_e_rifiuta_le_chiavi_vietate():
    out = c.pulisci({"a": float("nan"), "b": float("inf"), "c": (1, 2), "d": {1: {"x": -float("inf")}},
                     "e": datetime(2026, 9, 25, tzinfo=timezone.utc)})
    assert out["a"] is None and out["b"] is None and out["c"] == [1, 2]
    assert out["d"] == {"1": {"x": None}} and isinstance(out["e"], float)
    for k in ("a.b", "a#b", "a$b", "a[b", "a]b", "a/b"):
        with pytest.raises(ValueError):
            c.pulisci({"ok": {k: 1}})


def test_il_documento_si_serializza_e_sta_sotto_30_kb():
    doc = _doc(n_pos=12)
    testo = json.dumps(doc, allow_nan=False)      # esplode su NaN/inf: non ce ne devono essere
    assert len(testo.encode("utf-8")) < 30_000, len(testo)
    # niente liste di liste (Firestore le rifiuta)

    def _no_liste_annidate(o):
        if isinstance(o, list):
            assert not any(isinstance(x, list) for x in o)
            for x in o:
                _no_liste_annidate(x)
        elif isinstance(o, dict):
            for v in o.values():
                _no_liste_annidate(v)
    _no_liste_annidate(doc)


def test_pubblica_scrive_firestore_e_specchio_rtdb():
    fb = _fb()
    doc = _doc(fb)
    c.pubblica_controllo(fb, doc)
    assert fb.get_doc("dashboard", "controllo")["meta"]["generato_at"] == NOW
    assert fb.get_rtdb("/controllo")["meta"]["generato_at"] == NOW
    # il controllo dopo rilegge l'istante precedente e l'impronta (mezz'ora dopo:
    # il cooldown su AUSDT e' ancora vivo, quindi niente e' cambiato)
    doc2 = _doc(fb, now=NOW + 1800)
    assert doc2["meta"]["precedente_at"] == NOW
    assert doc2["salute"]["controllo_precedente_eta_s"] == 1800
    assert doc2["learning"]["attivo"]["cambiamenti_24h"] == []
    # un'ora dopo il cooldown e' scaduto: e' un cambiamento del learning
    doc3 = _doc(fb, now=NOW + 3600)
    assert doc3["learning"]["attivo"]["cambiamenti_24h"] == ["cooldown AUSDT finito"]


def test_carica_dati_legge_il_battito_come_figlio_con_una_chiamata_sua():
    fb = _fb()
    letti = []
    orig = fb.get_rtdb

    def _spia(path):
        letti.append(path)
        return orig(path)
    fb.get_rtdb = _spia
    d = c.carica_dati(fb, NOW)
    assert "/bot_status/heartbeat" in letti and "/bot_status" in letti
    assert d["heartbeat"] == NOW - 22
    assert d["trades"] and d["registro"]["validated"]


def test_la_sezione_paper_usa_i_trade_e_il_registro_passati():
    fb = _fb()
    mio = [_trade(0, +1.0, "take_profit")]
    d = c.carica_dati(fb, NOW, trades=mio, registro={})
    doc = c.costruisci_controllo(d, NOW, "bot", True)
    assert doc["paper"]["trades"] == 1
    assert doc["paper"]["stop"]["nota"].startswith("primo gradino GLOBALE")


# --------------------------------------------------------------------------- #
# 3. le anomalie, una per una                                                   #
# --------------------------------------------------------------------------- #
def _dati(fb=None, **kw) -> dict:
    return c.carica_dati(fb or _fb(**kw), NOW)


def _con(dati: dict, generato_da="bot", durata_ms=None, **cambia) -> dict:
    dati = dict(dati)
    dati.update(cambia)
    return c.costruisci_controllo(dati, NOW, generato_da, settings_da_bot=True, durata_ms=durata_ms)


def test_fixture_sana_non_ha_anomalie_e_i_semafori_sono_verdi():
    doc = _doc()
    assert doc["salute"]["anomalie"] == []
    assert doc["meta"]["semaforo_sistema"] == "verde" and doc["meta"]["semaforo_paper"] == "verde"


def test_bot_fermo_rosso_ma_non_in_manutenzione():
    d = _dati()
    doc = _con(d, heartbeat=NOW - 1000)
    a = _codici(doc)["BOT_FERMO"]
    assert a["gravita"] == "rosso" and a["famiglia"] == "sistema" and a["valore"] == 1000
    assert doc["meta"]["semaforo_sistema"] == "rosso"
    assert "bot fermo" in doc["salute"]["lettura"]
    doc = _con(d, heartbeat=NOW - 1000, maintenance=True)
    cod = _codici(doc)
    assert "BOT_FERMO" not in cod and cod["MANUTENZIONE"]["gravita"] == "info"
    assert doc["meta"]["semaforo_sistema"] == "verde"          # le info non colorano
    # battito mai visto: e' fermo, non «non misurato»
    doc = _con(d, heartbeat=None, bot_status={})
    assert _codici(doc)["BOT_FERMO"]["valore"] is None


def test_kill_switch_wal_cicli_e_riavvii():
    d = _dati()
    cod = _codici(_con(d, kill_switch=True, unlogged={"t1": {"pnl": 1}}, errori_ciclo_1h=4,
                       avvii=[NOW - 100, NOW - 200, NOW - 300, NOW - 400, NOW - 90000]))
    assert cod["KILL_SWITCH_ATTIVO"]["gravita"] == "giallo"
    assert cod["WAL_NON_VUOTO"]["gravita"] == "rosso" and cod["WAL_NON_VUOTO"]["valore"] == 1
    assert cod["CICLO_IN_ERRORE"]["valore"] == 4 and cod["CICLO_IN_ERRORE"]["soglia"] == 3
    assert cod["RIAVVII"]["valore"] == 4                     # quello di 25 ore fa non conta
    # sotto soglia: niente
    cod = _codici(_con(d, errori_ciclo_1h=3, avvii=[NOW - 100] * 3))
    assert "CICLO_IN_ERRORE" not in cod and "RIAVVII" not in cod


def test_gate_in_ritardo_sfora_fallito_non_pronto():
    d = _dati()
    g = _gate()
    g["meta"]["generato_at"] = NOW - 4 * 3600
    g["meta"]["durata_s"] = 600
    cod = _codici(_con(d, gate=g))
    assert cod["GATE_IN_RITARDO"]["gravita"] == "giallo" and cod["GATE_IN_RITARDO"]["soglia"] == 3 * 3600 + 600
    g["meta"]["generato_at"] = NOW - 7 * 3600
    assert _codici(_con(d, gate=g))["GATE_IN_RITARDO"]["gravita"] == "rosso"
    # entro «3 h + durata» il ritardo non e' un'anomalia
    g["meta"]["generato_at"] = NOW - 3 * 3600 - 300
    assert "GATE_IN_RITARDO" not in _codici(_con(d, gate=g))
    g = _gate()
    g["meta"]["durata_s"] = 4 * 3600
    g["meta"]["stato"] = "errore"
    cod = _codici(_con(d, gate=g))
    assert cod["GATE_SFORA"]["gravita"] == "giallo" and cod["GATE_FALLITO"]["gravita"] == "rosso"
    reg = dict(d["registro"])
    reg["ready"] = False
    doc = _con(d, registro=reg)
    assert _codici(doc)["GATE_NON_PRONTO"]["gravita"] == "rosso"
    assert doc["learning"]["attivo"]["gate_pronto"] is False
    assert "gate NON pronto" in doc["learning"]["lettura"]
    # gate mai visto -> nessun giudizio (null = non misurato), e il ripiego su discovered_last_run
    g = {}
    doc = _con(d, gate=g)
    assert doc["salute"]["gate_ultimo_giro_at"] == pytest.approx(NOW - 3600)
    doc = _con(d, gate={}, discovered_last_run={})
    assert doc["salute"]["gate_ultimo_giro_eta_s"] is None
    assert "GATE_IN_RITARDO" not in _codici(doc)


def test_controllo_vecchio_registro_calato_registro_pieno():
    d = _dati()
    assert _codici(_con(d, precedente_at=NOW - 8000))["CONTROLLO_VECCHIO"]["valore"] == 8000
    assert "CONTROLLO_VECCHIO" not in _codici(_con(d, precedente_at=NOW - 7000))
    prec = {"freno": False, "panchina": [], "cooldown": [], "keep": [], "validate": 230, "gate_pronto": True}
    assert _codici(_con(d, impronta_precedente=prec))["REGISTRO_CALATO"]["gravita"] == "rosso"
    prec["validate"] = 205
    assert _codici(_con(d, impronta_precedente=prec))["REGISTRO_CALATO"]["gravita"] == "giallo"
    prec["validate"] = 199
    assert "REGISTRO_CALATO" not in _codici(_con(d, impronta_precedente=prec))
    g = _gate()
    g["registro"]["occupazione"] = 2400
    assert _codici(_con(d, gate=g))["REGISTRO_PIENO"]["valore"] == 2400


def test_pesi_sospesi_stream_off_rtdb_degradato():
    d = _dati()
    w = dict(d["weights"])
    w["updated_at"] = NOW - 10000
    cod = _codici(_con(d, weights=w))
    assert cod["PESI_SOSPESI"]["gravita"] == "giallo"
    dr = dict(d["drift"])
    dr["updated_at"] = NOW - 10000
    assert "PESI_SOSPESI" not in _codici(_con(d, weights=w, drift=dr))
    st = dict(d["bot_status"])
    st["price_stream"] = False
    assert _codici(_con(d, bot_status=st))["STREAM_PREZZI_OFF"]["gravita"] == "giallo"
    assert _codici(_con(d, rtdb_degradato_s=120.0))["RTDB_DEGRADATO"]["valore"] == 120.0
    # il degrado del RTDB e' misurabile solo nel bot: da ops/github e' null
    doc = _con(d, rtdb_degradato_s=120.0, generato_da="ops")
    assert doc["salute"]["rtdb_degradato_s"] is None and "RTDB_DEGRADATO" not in _codici(doc)


def test_equity_non_torna():
    d = _dati()
    doc = _con(d)
    p = doc["paper"]
    # la fixture torna: 1000 + pnl realizzato = equity (a meno di 1 USDT)
    assert abs(p["equity"] - (p["equity_iniziale"] + p["pnl_realizzato"])) <= 1.0
    cod = _codici(_con(d, equity=p["equity"] + 50))
    assert cod["EQUITY_NON_TORNA"]["gravita"] == "giallo" and cod["EQUITY_NON_TORNA"]["valore"] == pytest.approx(50)


def test_pf_vissuto_basso_e_freno_globale():
    d = _dati()
    dr = _drift("drift")
    dr["global"]["live_pf"] = 0.3
    doc = _con(d, drift=dr)
    cod = _codici(doc)
    assert cod["PF_VISSUTO_BASSO"]["gravita"] == "rosso" and cod["PF_VISSUTO_BASSO"]["famiglia"] == "paper"
    assert cod["FRENO_GLOBALE"]["gravita"] == "giallo"
    assert doc["meta"]["semaforo_paper"] == "rosso" and doc["meta"]["semaforo_sistema"] == "verde"
    fg = doc["learning"]["attivo"]["freno_globale"]
    assert fg["attivo"] is settings.DRIFT_ENABLED and fg["dal"] == NOW - 3 * 86400
    assert fg["soglia_uscita_pf"] == pytest.approx(1.89 * settings.DRIFT_PF_RATIO)
    assert doc["salute"]["freno_globale"] is True and doc["salute"]["freno_globale_dal"] == NOW - 3 * 86400
    assert doc["learning"]["attivo"]["impronta"]["freno"] is settings.DRIFT_ENABLED
    # PF basso ma sotto i 20 trade: nessun rosso
    dr["global"]["trades"] = 19
    assert "PF_VISSUTO_BASSO" not in _codici(_con(d, drift=dr))


def test_rischio_alto_direzione_al_tetto_oltre_tetto_posizioni(monkeypatch):
    d = _dati()
    pos = {f"P{i}": {"symbol": f"P{i}", "direction": "long", "risk_effective_pct": 0.011,
                     "unrealized_pnl": 0.0} for i in range(6)}
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    monkeypatch.setattr(settings, "MAX_OPEN_POSITIONS", 5)
    monkeypatch.setattr(settings, "MAX_DIRECTIONAL_RISK_PCT", 0.03)
    cod = _codici(_con(d, positions=pos))
    assert cod["RISCHIO_ALTO"]["gravita"] == "rosso" and cod["RISCHIO_ALTO"]["valore"] == pytest.approx(6.6)
    assert cod["DIREZIONE_AL_TETTO"]["testo"].startswith("rischio long")
    assert cod["OLTRE_TETTO_POSIZIONI"]["valore"] == 6 and cod["OLTRE_TETTO_POSIZIONI"]["soglia"] == 5
    # in parita' il tetto sul numero e' spento (I6): niente anomalia
    monkeypatch.setattr(settings, "BACKTEST_PARITY", True)
    doc = _con(d, positions=pos)
    assert "OLTRE_TETTO_POSIZIONI" not in _codici(doc)
    assert doc["salute"]["tetto_posizioni_attivo"] is False


def test_circuit_breaker_nessun_trade_48h_senza_promessa_controllo_lento():
    d = _dati()
    assert _codici(_con(d, risk_state={"halted_for_day": True}))["CIRCUIT_BREAKER"]["gravita"] == "giallo"
    assert "CIRCUIT_BREAKER" in _codici(_con(d, risk_state={"paused_until_ts": NOW + 100}))
    assert "CIRCUIT_BREAKER" not in _codici(_con(d, risk_state={"paused_until_ts": NOW - 100}))
    vecchi = [_trade(i, -1.0, exit_ts=NOW - 3 * 86400 - i) for i in range(3)]
    cod = _codici(_con(d, trades=vecchi, positions={}))
    assert cod["NESSUN_TRADE_48H"]["gravita"] == "giallo"
    dec = dict(d["decision_status"])
    dec["signals_found"] = 0
    assert "NESSUN_TRADE_48H" not in _codici(_con(d, trades=vecchi, positions={}, decision_status=dec))
    # una posizione aperta da poco basta a non dirlo
    assert "NESSUN_TRADE_48H" not in _codici(_con(d, trades=vecchi))
    g = _gate()
    g["strategie"] = {"n_operate": 100, "n_senza_promessa": 40}
    assert _codici(_con(d, gate=g))["SENZA_PROMESSA"]["valore"] == 0.4
    assert _codici(_con(d, durata_ms=2500))["CONTROLLO_LENTO"]["valore"] == 2500
    assert "CONTROLLO_LENTO" not in _codici(_con(d, durata_ms=1500))


def test_le_anomalie_sono_ordinate_per_gravita():
    d = _dati()
    doc = _con(d, kill_switch=True, heartbeat=NOW - 1000, maintenance=False, durata_ms=3000)
    grav = [a["gravita"] for a in doc["salute"]["anomalie"]]
    assert grav == sorted(grav, key={"rosso": 0, "giallo": 1, "info": 2}.get)
    assert c.semaforo(doc["salute"]["anomalie"], "sistema") == "rosso"
    assert c.semaforo([], "paper") == "verde"


# --------------------------------------------------------------------------- #
# 4. fail-open per sezione                                                     #
# --------------------------------------------------------------------------- #
def test_una_sezione_che_fallisce_non_ferma_le_altre(monkeypatch):
    def _boom(*a, **k):
        raise RuntimeError("Firestore muto")
    monkeypatch.setattr(c, "_paper", _boom)
    doc = _doc()
    assert doc["meta"]["errori"] == ["paper"]
    assert doc["paper"]["errore"].startswith("RuntimeError: Firestore muto")
    assert doc["paper"]["lettura"].startswith("sezione non calcolata: RuntimeError: Firestore muto")
    assert doc["salute"]["errore"] is None and doc["salute"]["heartbeat_eta_s"] == 22
    assert doc["learning"]["attivo"]["errore"] is None
    assert doc["learning"]["misurato"]["trailing"] is None      # copiava da paper, che manca
    assert doc["meta"]["semaforo_sistema"] == "verde"            # le anomalie del paper non si inventano
    json.dumps(doc, allow_nan=False)


def test_anche_salute_e_learning_falliscono_da_soli(monkeypatch):
    def _boom(*a, **k):
        raise ValueError("chiave rotta")
    monkeypatch.setattr(c, "_salute", _boom)
    monkeypatch.setattr(c, "_attivo", _boom)
    doc = _doc()
    assert doc["meta"]["errori"] == ["salute", "learning.attivo"]
    assert doc["salute"]["lettura"].startswith("sezione non calcolata")
    assert doc["salute"]["anomalie"] == []                     # niente salute -> niente anomalie di sistema
    assert doc["learning"]["errore"].startswith("ValueError")
    assert doc["learning"]["lettura"].startswith("sezione non calcolata")
    assert doc["learning"]["misurato"]["deriva"]["coppie_drift"] == 3
    assert doc["paper"]["trades"] == 54


def test_una_lettura_firebase_fallita_finisce_in_meta_errori():
    fb = _fb()
    orig = fb.get_doc

    def _rotto(coll, doc_id):
        if coll == "calibration":
            raise RuntimeError("quota")
        return orig(coll, doc_id)
    fb.get_doc = _rotto
    doc = _doc(fb)
    assert doc["meta"]["errori"] == ["lettura: fs:calibration/current: quota"]
    assert doc["learning"]["misurato"]["calibrazione"]["verdetto"] is None


# --------------------------------------------------------------------------- #
# 5. impronta e cambiamenti                                                    #
# --------------------------------------------------------------------------- #
def test_cambiamenti_24h_descrivono_le_differenze():
    prima = {"freno": False, "panchina": ["gen_a|sideways"], "cooldown": ["AUSDT"],
             "keep": [{"valore": 0.5, "n": 31}], "validate": 160, "gate_pronto": True}
    dopo = {"freno": True, "panchina": ["gen_b|bull_trending"], "cooldown": [],
            "keep": [{"valore": 0.5, "n": 30}, {"valore": 0.25, "n": 2}], "validate": 172,
            "gate_pronto": False}
    assert c.cambiamenti_24h(dopo, prima) == [
        "freno globale ACCESO", "gen_b|bull_trending in panchina", "gen_a|sideways fuori dalla panchina",
        "cooldown AUSDT finito", "keep per coppia: 0.5 ×31 → 0.5 ×30, 0.25 ×2",
        "validate 160 → 172", "gate NON pronto: il bot resta flat"]
    assert c.cambiamenti_24h(dopo, dopo) == []
    assert c.cambiamenti_24h(dopo, None) == []          # primo controllo: niente con cui confrontare


def test_l_impronta_di_un_controllo_e_il_precedente_del_successivo():
    fb = _fb()
    c.pubblica_controllo(fb, _doc(fb))
    # nel frattempo il freno si accende e una coppia esce dal registro
    fb.set_doc("drift", "current", _drift("drift"))
    reg = fb.get_doc("strategy_registry", "validated")
    reg["validated"] = reg["validated"][:-1]
    fb.set_doc("strategy_registry", "validated", reg)
    doc2 = _doc(fb, now=NOW + 3600)
    cambi = doc2["learning"]["attivo"]["cambiamenti_24h"]
    assert "validate 160 → 159" in cambi
    assert ("freno globale ACCESO" in cambi) is settings.DRIFT_ENABLED


# --------------------------------------------------------------------------- #
# 6. funzioni pure: giornate/oggi in UTC, pf, uscite, gradini, mfe, cooldown     #
# --------------------------------------------------------------------------- #
def test_giornate_e_oggi_sono_in_utc():
    mezzanotte = datetime(2026, 9, 25, 0, 0, tzinfo=timezone.utc).timestamp()
    now = mezzanotte + 600                    # 00:10 UTC del 25
    trades = [_trade(1, +3.0, exit_ts=mezzanotte + 60),          # oggi
              _trade(2, -1.0, exit_ts=mezzanotte - 60),          # ieri alle 23:59
              _trade(3, +5.0, exit_ts=mezzanotte - 86400 * 3)]   # 22 set
    og = c.oggi(trades, now)
    assert og == {"trades": 1, "vinti": 1, "pnl": 3.0, "migliore": {"coin": "AUSDT", "pnl": 3.0},
                  "peggiore": {"coin": "AUSDT", "pnl": 3.0}}
    g = c.giornate(trades, now)
    assert g["con_trade"] == 3 and g["positive"] == 2 and g["negative"] == 1
    assert g["migliore"] == {"data": "2026-09-22", "pnl": 5.0}
    assert g["peggiore"] == {"data": "2026-09-24", "pnl": -1.0}
    assert [r["data"] for r in g["ultime_7"]] == [f"2026-09-{d}" for d in range(19, 26)]
    assert g["ultime_7"][-1] == {"data": "2026-09-25", "trades": 1, "pnl": 3.0}
    assert g["ultime_7"][-2] == {"data": "2026-09-24", "trades": 1, "pnl": -1.0}
    assert c.oggi([], now)["migliore"] is None and c.giornate([], now)["migliore"] is None


def test_pf_senza_perdite_e_null_con_perdite_zero():
    assert c.pf([_trade(0, 3.0), _trade(1, 2.0)]) is None
    assert c.pf([_trade(0, 3.0), _trade(1, -2.0)]) == 1.5
    assert c.pf([]) is None
    doc = _doc(trades=[_trade(0, 3.0, "take_profit"), _trade(1, 2.0, "take_profit")])
    assert doc["paper"]["pf_vissuto"] is None and doc["paper"]["perdite"] == 0
    assert doc["paper"]["ultimi_30g"]["pf"] == 0.64      # dal documento di deriva
    doc = _doc(trades=[_trade(0, 3.0, "take_profit")], verdetto_drift="ok")
    # senza il documento di deriva il PF a 30 giorni si calcola inline, e resta null
    fb = _fb(trades=[_trade(0, 3.0, "take_profit")])
    fb.set_doc("drift", "current", {})
    assert _doc(fb)["paper"]["ultimi_30g"] == {"trades": 1, "pnl": 3.0, "pf": None, "win_rate": 1.0}


def test_gli_esiti_esterni_non_contano_come_trade_della_strategia():
    trades = [_trade(0, -3.0, "manual"), _trade(1, +4.0, "take_profit"), _trade(2, -2.0, "kill_switch")]
    doc = _doc(trades=trades)
    p = doc["paper"]
    assert p["trades"] == 1 and p["vinti"] == 1 and p["perdite"] == 0
    assert p["pnl_realizzato"] == -1.0                    # su tutti: e' cio' che sta nell'equity
    assert sum(u["trades"] for u in p["uscite"]) == 3     # le uscite le conta tutte


def test_uscite_gradini_mfe_cooldown_panchina_keep():
    trades = [_trade(0, -1.0, "stop_loss"), _trade(1, -1.0, "stop_loss", mfe_r=0.9), _trade(2, 5.0, "scale_out",
                                                                                            scale_stage_reached=2)]
    u = c.uscite_per_motivo(trades)
    assert u[0] == {"motivo": "stop_loss", "etichetta": "Stop loss (prima di qualsiasi TP)", "trades": 2,
                    "quota": 0.667, "pnl": -2.0}
    assert c.gradini(trades) == [{"gradino": 0, "n": 2}, {"gradino": 2, "n": 1}]
    m = c.mfe_riassunto(trades)
    assert m["n"] == 3 and m["mediana_r"] == 0.9 and m["quota_1r"] == 0.333 and m["quota_3r"] == 0.0
    assert c.mfe_riassunto([])["mediana_r"] is None
    cd = c.cooldown_attivi({"coin_cooldown": {"A": NOW + 1, "B": NOW - 1}, "strat_cooldown": {"s": NOW + 5}}, NOW)
    assert cd == {"coin": [{"nome": "A", "fino_a": NOW + 1}], "strategie": [{"nome": "s", "fino_a": NOW + 5}]}
    p = c.panchina({"weights": [{"strategy": "a", "regime": "sideways", "weight": 0.0, "sample_size": 4},
                                {"strategy": "b", "regime": "sideways", "weight": 0.49},
                                {"strategy": "c", "regime": "sideways", "weight": 0.5}],
                    "updated_at": 5.0, "version": 3, "trade_count_used": 9}, soglia=0.5)
    assert p["in_panchina_n"] == 2 and p["spente_n"] == 1 and p["combinazioni"] == 3
    assert [r["strategia"] for r in p["in_panchina"]] == ["a", "b"] and p["at"] == 5.0
    k = c.keep_distribuzione({"x": {"last_params": {"profit_lock_keep": 0.5}},
                              "y": {"last_params": {"profit_lock_keep": 0.5}},
                              "z": {"last_params": {}}, "w": {}})
    assert k == {"distribuzione": [{"valore": 0.5, "n": 2}], "non_rivalutate": 2}


def test_btc_dall_anello_e_null_se_l_anello_e_fermo():
    ring = [{"ts": NOW - 3600 * (199 - i), "close": 100.0 + i} for i in range(200)]
    assert c._btc_pct(ring, NOW, 24 * 3600) == pytest.approx((299 / 275 - 1) * 100, abs=0.01)
    assert c._btc_pct(ring, NOW, 7 * 86400) == pytest.approx((299 / 131 - 1) * 100, abs=0.01)
    assert c._btc_pct(ring, NOW + 4 * 3600, 24 * 3600) is None      # ultimo punto di 4 ore fa
    assert c._btc_pct(ring[-5:], NOW, 24 * 3600) is None            # non copre l'orizzonte
    assert c._btc_pct(None, NOW, 24 * 3600) is None


# --------------------------------------------------------------------------- #
# 7. classi_stop (metrics)                                                     #
# --------------------------------------------------------------------------- #
def test_classi_stop_per_coppia_e_globale():
    trades = [_trade(0, -1.0, mfe_r=0.1, sym="A", strat="s"),
              _trade(1, -1.0, mfe_r=0.8, sym="A", strat="s", duration_seconds=3600),
              _trade(2, -1.0, mfe_r=1.2, sym="B", strat="s", duration_seconds=10800),
              _trade(3, +2.0, "take_profit", mfe_r=3.0)]
    g = classi_stop(trades)                                  # globale: primo gradino 1.5
    assert (g["totale"], g["sbagliati"], g["quasi"], g["oltre_primo_tp"]) == (3, 1, 2, 0)
    assert g["quasi_durata_mediana_h"] == 2.0 and g["primo_gradino_r"] == 1.5
    assert "GLOBALE" in g["nota"]
    p = classi_stop(trades, {"B|s": 1.0})                   # B ha la sua scala: 1,2R e' oltre
    assert (p["sbagliati"], p["quasi"], p["oltre_primo_tp"]) == (1, 1, 1)
    assert p["quasi_durata_mediana_h"] == 1.0 and p["nota"].startswith("primo gradino per coppia")
    f = classi_stop(trades, lambda t: 0.5)
    assert (f["sbagliati"], f["quasi"], f["oltre_primo_tp"]) == (1, 0, 2)
    assert classi_stop([])["totale"] == 0 and classi_stop([])["quasi_durata_mediana_h"] is None


# --------------------------------------------------------------------------- #
# 8. i contatori dei rifiuti                                                   #
# --------------------------------------------------------------------------- #
def test_motivo_rifiuto_normalizza_alle_nove_classi():
    casi = {"cooldown dopo stop (37m)": "cooldown", "tetto per coin al giorno: ...": "tetto per coin",
            "peso 0.30: confidenza 19 < soglia 30": "peso sotto soglia",
            "peso 0.00 (strategia spenta dal learning)": "strategia spenta",
            "veto di regime (sideways)": "veto di regime",
            "margine esaurito (conto pienamente investito)": "margine",
            "margine insufficiente (usato 900 + nuovo 200 > equity 1000)": "margine",
            "rischio direzionale 3.5% > tetto 3.0%": "rischio direzionale",
            "risk gate: stop troppo largo: 7.0% del prezzo > 6%": "stop troppo largo",
            "posizione gia' aperta su questa coin": "altro", "": "altro"}
    for testo, atteso in casi.items():
        assert motivo_rifiuto(testo) == atteso, testo


def test_i_contatori_del_ciclo_e_delle_24_ore():
    o = Orchestrator()
    o.nuovo_ciclo()
    o._rifiuto("AUSDT", "gen_a", "veto di regime (sideways)")
    o._rifiuto("AUSDT", "gen_a", "veto di regime (sideways)")     # doppione: come nel log, una volta
    o._rifiuto("BUSDT", "gen_a", "peso 0.30: confidenza 19 < soglia 30")
    o.conta_scarto("cooldown dopo stop (5m)", now=NOW)
    assert o.rifiuti_ciclo() == [{"motivo": "cooldown", "n": 1}, {"motivo": "peso sotto soglia", "n": 1},
                                 {"motivo": "veto di regime", "n": 1}]
    o.nuovo_ciclo()
    assert o.rifiuti_ciclo() == []
    o.conta_scarto("margine esaurito", now=NOW)
    o.conta_scarto("margine esaurito", now=NOW - 86400 - 1)       # fuori dalla finestra
    r24 = o.rifiuti_24h(now=NOW)
    assert {"motivo": "margine", "n": 1} in r24 and {"motivo": "cooldown", "n": 1} in r24
    assert o.rifiuti_24h_dal <= time.time()
    # `_stampa_rifiuti` svuota le righe da stampare ma NON i conteggi del ciclo
    o._stampa_rifiuti()
    assert o.rifiuti_ciclo() == [{"motivo": "margine", "n": 2}]


def test_decide_all_azzera_il_ciclo_e_conta_i_veti(monkeypatch, capsys):
    from bot.core.models import AssetSnapshot, IndicatorSnapshot, Regime
    monkeypatch.setattr(settings, "BACKTEST_PARITY", False)
    o = Orchestrator()
    o.adaptation._passed = {"BTCUSDT|mean_reversion"}
    o.adaptation._has_opt_data = True
    o.adaptation._weights = {f"mean_reversion|{r.value}": 0.3 for r in Regime}
    ind = IndicatorSnapshot(timeframe="15m", rsi=20.0, atr=2.0, close=94.0, bb_lower=95.0,
                            bb_upper=105.0, bb_mid=100.0)
    a = AssetSnapshot(symbol="BTCUSDT", price=94.0, regime=Regime.SIDEWAYS, indicators={"15m": ind})
    o.conta_scarto("cooldown")                       # residuo del ciclo prima
    assert o.decide_all({"BTCUSDT": a}, Regime.SIDEWAYS) == []
    assert o.rifiuti_ciclo() == [{"motivo": "peso sotto soglia", "n": 1}]
    assert capsys.readouterr().out.count("[rifiuto]") == 1


def test_main_pubblica_i_conteggi_e_try_open_li_alimenta():
    from bot import main as bot_main
    src = inspect.getsource(bot_main.TradingBot._publish_decision_status)
    assert 'status["rifiuti_ciclo"] = self.orchestrator.rifiuti_ciclo()' in src
    assert 'status["rifiuti_24h"] = self.orchestrator.rifiuti_24h()' in src
    assert 'status["rifiuti_24h_dal"]' in src
    src = inspect.getsource(bot_main.TradingBot._try_open)
    assert "self.orchestrator.conta_scarto(motivo, now)" in src
    # la riga [rifiuto] resta quella di prima (tests/test_rifiuti_nel_log.py la legge)
    assert 'print(f"[rifiuto] {decision.asset} {decision.strategy} "' in src


# --------------------------------------------------------------------------- #
# 9. il bot: gancio orario, guard, avvio, anello BTC, deriva.dal, equity          #
# --------------------------------------------------------------------------- #
def test_il_controllo_parte_solo_dal_ramo_orario_del_loop():
    from bot import main as bot_main
    run = inspect.getsource(bot_main.TradingBot.run)
    assert "self.refresh_weights(now, orario=True)" in run
    assert "self.refresh_weights(time.time())" in run              # dopo ogni chiusura: senza gancio
    assert run.count("refresh_weights(now, orario=True)") == 1 and "time.time(), orario" not in run
    rw = inspect.getsource(bot_main.TradingBot.refresh_weights)
    assert "if orario:" in rw and "self._publish_controllo(trades, now)" in rw
    assert '"/bot_status/errori_ciclo_1h"' in rw
    assert '[controllo] pubblicazione saltata' in rw
    pc = inspect.getsource(bot_main.TradingBot._publish_controllo)
    assert "if now - self._last_controllo_at < 3300:" in pc
    assert 'print(f"[controllo] pubblicazione saltata: {exc}")' in pc
    assert "self._registro_cache" in pc
    # l'avvio e il contatore errori
    assert "self._publish_avvio()" in run
    assert "self._errori_ciclo.append(time.time())" in run
    rr = inspect.getsource(bot_main.TradingBot.refresh_regime)
    for campo in ('"heartbeat": now', '"avviato_at": self._avviato_at', '"errori_ciclo_1h"', '"btc_close"'):
        assert campo in rr, campo


def _finto_bot(fb, trades=None, **extra):
    """Un TradingBot senza costruttore (troppo pesante): solo cio' che i metodi
    sotto toccano."""
    return SimpleNamespace(
        fb=fb, logger=SimpleNamespace(all_since=lambda since: list(trades or [])),
        executor=SimpleNamespace(open_positions={}), adaptation=SimpleNamespace(_drift={}),
        _last_controllo_at=0.0, _registro_cache=None, _avviato_at=NOW, _errori_ciclo=[], **extra)


def test_publish_controllo_rispetta_il_guard_e_pubblica(capsys):
    from bot.main import TradingBot
    fb = _fb()
    bot = _finto_bot(fb, trades=_trades_realistici())
    bot._last_controllo_at = NOW - 100
    TradingBot._publish_controllo(bot, [], now=NOW)
    assert fb.get_doc("dashboard", "controllo") is None            # troppo presto
    bot._last_controllo_at = NOW - 3300
    TradingBot._publish_controllo(bot, _trades_realistici(), now=NOW)
    doc = fb.get_doc("dashboard", "controllo")
    assert doc["meta"]["generato_da"] == "bot" and doc["meta"]["fonte_impostazioni"] == "processo bot"
    assert fb.get_rtdb("/controllo")["meta"]["generato_at"] == NOW
    assert bot._last_controllo_at == NOW
    assert "[controllo] pubblicato: sistema verde, paper verde" in capsys.readouterr().out


def test_publish_controllo_rilegge_l_all_time_se_il_paper_ha_piu_di_30_giorni():
    from bot.main import TradingBot
    fb = _fb()
    fb.set_rtdb("/account/paper_started_at", NOW - 40 * 86400)
    chiamate = []
    bot = _finto_bot(fb)
    bot.logger = SimpleNamespace(all_since=lambda since: chiamate.append(since) or _trades_realistici(10))
    TradingBot._publish_controllo(bot, _trades_realistici(3), now=NOW)
    assert chiamate == [0.0]
    assert fb.get_doc("dashboard", "controllo")["paper"]["trades"] == 10


def test_publish_controllo_non_solleva_mai(capsys):
    from bot.main import TradingBot
    fb = _fb()
    bot = _finto_bot(fb)
    bot.fb = SimpleNamespace(get_doc=lambda *a: (_ for _ in ()).throw(RuntimeError("giu'")),
                             get_rtdb=lambda p: None)
    TradingBot._publish_controllo(bot, [], now=NOW)
    assert "[controllo] pubblicazione saltata: giu'" in capsys.readouterr().out


def test_reconcile_equity_scrive_capitale_iniziale_e_inizio_paper_una_volta(capsys):
    from bot.main import TradingBot
    fb = FirebaseClient()
    trades = [_trade(0, -5.0, exit_ts=NOW - 86400), _trade(1, +3.0, exit_ts=NOW - 3600)]
    bot = _finto_bot(fb, trades=trades)
    assert TradingBot.reconcile_equity(bot) == 998.0
    assert fb.get_rtdb("/account/starting_equity") == 1000.0
    assert fb.get_rtdb("/account/paper_started_at") == pytest.approx(NOW - 86400 - 7200)
    # seconda volta: niente riscritture, anche se l'equity cambia
    fb.set_rtdb("/account/starting_equity", 500.0)
    fb.set_rtdb("/account/paper_started_at", 123.0)
    assert TradingBot.reconcile_equity(bot) == 498.0
    assert fb.get_rtdb("/account/starting_equity") == 500.0
    assert fb.get_rtdb("/account/paper_started_at") == 123.0
    # senza trade l'inizio del paper e' adesso
    fb2 = FirebaseClient()
    TradingBot.reconcile_equity(_finto_bot(fb2, trades=[]))
    assert abs(fb2.get_rtdb("/account/paper_started_at") - time.time()) < 5


def test_avvio_e_anello_btc_tengono_gli_ultimi_20_e_200():
    from bot.main import TradingBot
    fb = FirebaseClient()
    bot = _finto_bot(fb)
    for i in range(25):
        bot._avviato_at = NOW + i
        TradingBot._publish_avvio(bot)
    ring = fb.get_rtdb("/avvii")
    assert len(ring) == 20 and ring[-1] == NOW + 24 and ring[0] == NOW + 5
    assert fb.get_rtdb("/bot_status/avviato_at") == NOW + 24
    for i in range(205):
        TradingBot._btc_history(bot, 60000.0 + i, NOW + 3600 * i)
    hist = fb.get_rtdb("/btc_history")
    assert len(hist) == 200 and hist[-1] == {"ts": NOW + 3600 * 204, "close": 60204.0}
    assert TradingBot._errori_ciclo_1h(SimpleNamespace(_errori_ciclo=[NOW - 10, NOW - 4000]), NOW) == 1


def test_publish_drift_eredita_dal_del_primo_verdetto_drift(monkeypatch):
    from bot.main import TradingBot
    import bot.learning.drift as drift_mod
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    fb = FirebaseClient()
    fb.set_doc("strategy_registry", "validated", _registro(5))
    verdetto = {"v": "drift"}
    monkeypatch.setattr(drift_mod, "compute_drift",
                        lambda trades, pairs: {"pairs": {}, "strategies": {}, "serie": {},
                                               "global": {"verdict": verdetto["v"], "trades": 40}})
    bot = _finto_bot(fb)
    TradingBot._publish_drift(bot, [])
    d1 = fb.get_doc("drift", "current")
    assert d1["global"]["dal"] == d1["updated_at"]
    assert bot._registro_cache["validated"]                       # il registro resta in cache
    TradingBot._publish_drift(bot, [])
    d2 = fb.get_doc("drift", "current")
    assert d2["updated_at"] > d1["updated_at"] and d2["global"]["dal"] == d1["global"]["dal"]
    verdetto["v"] = "ok"
    TradingBot._publish_drift(bot, [])
    assert "dal" not in fb.get_doc("drift", "current")["global"]
    verdetto["v"] = "drift"
    TradingBot._publish_drift(bot, [])
    assert fb.get_doc("drift", "current")["global"]["dal"] > d1["global"]["dal"]


# --------------------------------------------------------------------------- #
# 10. i ripieghi: comando ops e snapshot GitHub                                  #
# --------------------------------------------------------------------------- #
def test_il_comando_ops_stampa_semafori_anomalie_e_letture(monkeypatch, capsys):
    from scripts import controllo as cli
    fb = _fb()
    monkeypatch.setattr("bot.core.firebase_client.get_firebase", lambda: fb)
    monkeypatch.setattr(c.time, "time", lambda: NOW)      # l'orologio della fixture
    assert cli.main([]) == 0
    out = capsys.readouterr().out
    assert "semaforo SISTEMA: VERDE" in out and "semaforo PAPER: VERDE" in out
    assert "ANOMALIE (0)" in out and "LETTURE:" in out and "Bot vivo (battito 22 s fa)" in out
    assert "generato da ops" in out
    assert fb.get_doc("dashboard", "controllo") is None            # sola lettura
    assert cli.main(["--publish"]) == 0
    doc = fb.get_doc("dashboard", "controllo")
    assert doc["meta"]["generato_da"] == "ops" and doc["meta"]["fonte_impostazioni"] == "default repo"
    assert "generato_da=ops" in capsys.readouterr().out


def test_il_comando_ops_gira_anche_senza_firebase(capsys):
    from scripts import controllo as cli
    assert cli.main([]) == 0
    out = capsys.readouterr().out
    assert "BOT_FERMO" in out and "letto lo store in memoria" in out


def test_lo_snapshot_pubblica_solo_se_il_controllo_del_bot_e_vecchio(monkeypatch, capsys):
    from scripts import state_snapshot as ss
    fb = _fb()
    monkeypatch.setattr(ss, "get_firebase", lambda: fb)
    assert ss.pubblica_controllo_se_vecchio(5400) is True
    doc = fb.get_doc("dashboard", "controllo")
    assert doc["meta"]["generato_da"] == "github"
    assert "ripiego GitHub pubblicato" in capsys.readouterr().out
    # appena pubblicato: il ripiego si ferma
    assert ss.pubblica_controllo_se_vecchio(5400) is False
    assert "niente ripiego" in capsys.readouterr().out
    # documento vecchio di due ore: si ripubblica
    fb.set_rtdb("/controllo/meta/generato_at", time.time() - 7200)
    assert ss.pubblica_controllo_se_vecchio(5400) is True
    # un errore non ferma lo snapshot
    monkeypatch.setattr(ss, "get_firebase", lambda: (_ for _ in ()).throw(RuntimeError("no")))
    assert ss.pubblica_controllo_se_vecchio(5400) is False
    assert "ripiego saltato" in capsys.readouterr().out


def test_il_workflow_e_la_lista_bianca_chiamano_il_ripiego():
    yml = open(".github/workflows/snapshot.yml", encoding="utf-8").read()
    assert "python -m scripts.state_snapshot --publish-controllo" in yml
    assert "git add docs/state.md" in yml                          # il commit resta com'era
    txt = open("ops/allowlist.example", encoding="utf-8").read()
    assert "controllo:    .venv/bin/python -m scripts.controllo" in txt
    assert "# controllo-publish: .venv/bin/python -m scripts.controllo --publish" in txt
    from scripts.ops_agent import parse_allowlist
    voci = parse_allowlist(txt)
    assert voci["controllo"]["cmd"].endswith("scripts.controllo") and not voci["controllo"]["args"]
    assert "controllo-publish" not in voci
