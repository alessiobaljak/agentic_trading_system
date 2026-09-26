"""IL DOCUMENTO DEL GATE, `dashboard/gate` (25 set 2026, docs/controllo_schema.md §2).

Richiesta del proprietario: «check di status, learning, paper, gate, strategie,
tutto in automatico, e le evidenze in dashboard ogni ora». La discovery scrive a
ogni giro un documento con tutto cio' che del gate finora si leggeva solo nel log
o con `gate_progress` dalla VPS. Qui si difende:
  * lo SCHEMA (i nomi dei campi sono il contratto con la dashboard);
  * `in_corso` fonde il solo `meta` e non cancella le sezioni del giro prima;
  * un giro caduto scrive `stato: errore` e rilancia;
  * l'intorno si ricopia dall'ultimo giro completo quando questo non lo e';
  * i numeri del keep nel documento sono quelli della riga del log;
  * i trade del paper per coppia escludono gli esiti esterni, e il PF senza
    perdite e' null;
  * la regola di robustezza e' la stessa di `adaptation._robust_only`;
  * le estrazioni in `bot/core/registry.py` stampano in `gate_progress` le
    STESSE righe di prima;
  * il documento con 300 coppie operate sta sotto 200 KB e passa la guardia di
    serializzazione (niente NaN, niente liste di liste, niente `. # $ [ ] /`).
"""
import inspect
import json
import math
import sys
import time

import pytest

from bot.config import settings
from bot.core import registry as r
from bot.core.firebase_client import decode_pairs, encode_pairs
from bot.learning import adaptation as _ad
from scripts import discover_strategies as d
from scripts import gate_progress as g
from scripts import optimize as o
from scripts.optimize import MIN_PASSES, NEW_DATA_MIN_S

NOW = 1_790_000_000.0


class _FB:
    """Firestore + RTDB finti. `rotto=True`: ogni lettura di `trades` esplode."""

    def __init__(self, docs=None, trades=None, rotto=False):
        self.docs = dict(docs or {})
        self.trades = list(trades or [])
        self.rotto = rotto
        self.rtdb = {}
        self.scritture = []

    def get_doc(self, c, n):
        return self.docs.get((c, n))

    def set_doc(self, c, n, data):
        self.docs[(c, n)] = data
        self.scritture.append((c, n))

    def query_collection(self, *a, **k):
        if self.rotto:
            raise RuntimeError("firestore giu'")
        return list(self.trades)

    def set_rtdb(self, path, data):
        self.rtdb[path] = data
        return True


def _rec(sym, strat, passi=MIN_PASSES, **extra):
    rec = {"symbol": sym, "strategy": strat, "generated": strat.startswith("gen_"),
           "pass_count": passi, "last_seen_at": NOW - 100, "window_start": NOW - 1000,
           "last_pf": 1.54, "last_pnl_pct": 0.45, "last_t": 2.31, "holdout": {"ok": True},
           "last_params": {"scale_r_mults": [1.5, 3.0, 5.0], "sl_to_breakeven": True,
                           "profit_lock_keep": 0.5},
           "direzione_pf": {"long": {"pf": 1.2, "n": 30}, "short": {"pf": 0.9, "n": 20}},
           "validated_at": NOW - 86400 * 3, "last_passed_at": NOW - 100}
    rec.update(extra)
    return rec


def _spec(sid, **extra):
    sp = {"id": sid, "features": [{"kind": "rsi_extreme", "low": 30.0, "high": 70.0}],
          "volume_mult": 0.0, "min_adx": 0.0, "atr_mult_stop": 1.5, "rr": 2.0}
    sp.update(extra)
    return sp


def _reg_doc(pairs, validated=None):
    validated = r.coppie_validate(pairs, NOW) if validated is None else validated
    return {"pairs": encode_pairs(pairs), "validated": validated, "ready": False,
            "ready_by": None, "coins_covered": len({pairs[k]["symbol"] for k in validated}),
            "universe_size": 200, "coverage": 0.05, "ready_fraction": 0.6, "max_pairs": 3000}


def _run(**extra):
    run = {"interval": "15m", "symbols": 3, "coin_valutate": 3, "started_at": NOW - 3600,
           "duration_s": 3600, "n_eval": 900, "n_passed": 2, "reeval_cap": 500,
           "reeval_modalita": "solo urgenti", "n_specs_note": 40, "n_specs_rivalutate": 12,
           "n_specs_con_conferme": 5, "n_specs_tagliate": 28,
           "passed": [{"symbol": "AUSDT", "id": "gen_a", "pf": 1.6, "pnl": 0.5}],
           "intorno": {}, "varianti": {},
           # il paper esplorativo (25 set 2026, F1bis): i conteggi del giro
           "esplorative": {"attive": 12, "nuove": 3, "validate_poi": 1, "scartate": 2,
                           "validate_giro": 0, "scartate_giro": 1},
           # le validate giudicate sulla propria configurazione (26 set 2026)
           "passate_solo_con_propria_config": 2, "validate_bocciate": 5,
           "declassate": {"totale": 1, "nuove": [], "tornate_piene": [], "bocciate_giro": 5,
                          "aggiornate": True},
           # il giro completo ridotto (26 set 2026, J10): spec note su coin proprie + fetta
           "riduzione": {"spec_note": 500, "coin_proprie": 60, "fetta": "3/7",
                         "valutazioni_stimate": 42000}}
    run.update(extra)
    return run


def _esito():
    return {"intorno": {"madri": 4, "figlie_passate": 4, "promosse": ["AUSDT|gen_f"],
                        "senza_margine": 1, "madre_non_valutata": 1, "scartate": 1},
            "varianti": {"create": 3, "passate": 2, "retro_ok": 1, "promosse": ["AUSDT|gen_v"],
                         "scartate": 1,
                         "sostituzioni": [{"figlia": "AUSDT|gen_v", "madre": "AUSDT|gen_m"}]}}


def _fixture_piccola():
    pairs = {"AUSDT|gen_a": _rec("AUSDT", "gen_a"),
             # declassata (26 set 2026): bocciata due notti di fila, operata a un quarto
             "BUSDT|gen_b": _rec("BUSDT", "gen_b", last_pf=None, last_params={},
                                 bocciata_notti=2, declassata=True, declassata_at=NOW - 3600),
             "CUSDT|gen_c": _rec("CUSDT", "gen_c", passi=2),
             "AUSDT|gen_m": _rec("AUSDT", "gen_m", sostituita_da="gen_v"),
             "AUSDT|gen_v": _rec("AUSDT", "gen_v", nata_intorno_at=NOW - 10)}
    specs = {"gen_a": _spec("gen_a"),
             "gen_v": _spec("gen_v", origine="referto", genitore="gen_m", ipotesi="solo_long")}
    trades = [{"symbol": "AUSDT", "strategy": "gen_a", "pnl": 5.0, "exit_reason": "take_profit"},
              {"symbol": "AUSDT", "strategy": "gen_a", "pnl": -3.0, "exit_reason": "stop_loss"},
              {"symbol": "AUSDT", "strategy": "gen_a", "pnl": 2.0, "exit_reason": "trailing_stop",
               "timeframe": settings.ORCHESTRATOR_TIMEFRAME, "trailing_verdict": "premature"},
              {"symbol": "AUSDT", "strategy": "gen_a", "pnl": -9.0, "exit_reason": "kill_switch"},
              {"symbol": "BUSDT", "strategy": "gen_b", "pnl": 4.0, "exit_reason": "take_profit"}]
    drift = {"pairs": {"AUSDT|gen_a": {"verdict": "watch", "reason": "PF 0.67 vs 1.54 atteso"}},
             "global": {"trades": 5, "live_pf": 0.9, "expected_pf": 1.5}}
    return pairs, specs, trades, drift


def _costruisci(pairs, specs, trades, drift, doc_prec=None, intorno_girato=True, **kw):
    args = dict(reg_doc=_reg_doc(pairs), specs=specs, drift_doc=drift, trades=trades,
                esito=_esito(), run=_run(), keep_paper=0.25, scala_paper=(1.0, 2.0, 3.0),
                doc_prec=doc_prec or {}, now=NOW, iniziato_at=NOW - 3600,
                modalita="solo urgenti", intorno_girato=intorno_girato,
                candidate={"totale": 90, "ai": 5, "varianti_referti": 3, "intorno": 24,
                           "casuali": 40, "semi": 30, "gemelle_scartate": 2, "rivalutate": 12},
                keep_giro=d.conta_keep_giro({"AUSDT|gen_a": {"profit_lock_keep": 0.25}},
                                            ["AUSDT|gen_a"], 0.25),
                letture={"autopsia_discover": {"updated_at": NOW - 100, "evaluated": 900,
                                               "passed": 2, "diagnosed": 898,
                                               "binding": {"total_return": 600, "pf": 298},
                                               "near_miss_count": 7},
                         "autopsia_current": {"updated_at": NOW - 86400 * 4},
                         "supervisore": {"updated_at": NOW - 50,
                                         "history": [{"kind": "set_param", "reason": "x"},
                                                     {"kind": "none", "reason": "a"},
                                                     {"kind": "none", "reason": "b"}]},
                         "vite": {"events": [{"tipo": "promossa", "at": NOW - 86400},
                                             {"tipo": "rimossa", "at": NOW - 86400 * 2},
                                             {"tipo": "promossa", "at": NOW - 86400 * 9}]},
                         "run_1h": {"started_at": NOW - 7000, "duration_s": 600, "symbols": 5,
                                    "n_eval": 300, "n_passed": 1}},
                worker=4, rss_max_mb=812.5)
    args.update(kw)
    return d.costruisci_doc_gate(**args)


# --------------------------------------------------------------------------- #
# 1. Lo schema                                                                 #
# --------------------------------------------------------------------------- #
def test_lo_schema_ha_le_chiavi_del_contratto():
    doc = _costruisci(*_fixture_piccola())
    assert set(doc) == {"meta", "giro", "registro", "cervello", "strategie"}
    assert set(doc["meta"]) == {"versione_schema", "stato", "fase", "errore", "iniziato_at",
                                "generato_at", "durata_s", "modalita", "generato_da"}
    assert doc["meta"]["stato"] == "finito" and doc["meta"]["generato_da"] == "discovery"
    assert doc["meta"]["durata_s"] == 3600 and doc["meta"]["versione_schema"] == 1
    for nome in ("giro", "registro", "cervello", "strategie"):
        sez = doc[nome]
        assert {"computed_at", "fonti", "lettura", "dettaglio", "errore"} <= set(sez), nome
        assert sez["errore"] is None, (nome, sez["errore"])
        assert 0 < len(sez["lettura"]) <= 140, (nome, sez["lettura"])
        assert all(isinstance(f, str) for f in sez["fonti"])
    assert {"coin_valutate", "valutazioni", "passate", "passate_lista", "spec_note",
            "spec_rivalutate", "spec_con_conferme", "spec_tagliate", "tetto_rivalutazione",
            "candidate", "passata_1h", "worker", "rss_max_mb", "paper_propone"} <= set(doc["giro"])
    assert doc["giro"]["paper_propone"] == {"scala": "1/2/3", "keep": 0.25, "verdetti_trailing": 1}
    assert doc["giro"]["passata_1h"]["coin"] == 5 and doc["giro"]["candidate"]["ai"] == 5
    assert {"validate", "coin_coperte", "universo", "copertura", "obiettivo_copertura", "pronto",
            "pronto_per", "distribuzione_pass", "congelate", "a_un_passo", "finestre_scadute",
            "coppie", "base", "generate", "occupazione", "limite", "alleggerito",
            "senza_promessa", "statistica_t", "validate_delta_giro"} <= set(doc["registro"])
    assert {"riga", "intorno", "varianti", "keep_giro", "keep_validate", "scala_validate",
            "breakeven_validate", "autopsia", "autopsia_base_congelata_da_s",
            "supervisore"} <= set(doc["cervello"])
    assert {"n_operate", "n_con_paper", "n_senza_promessa", "n_sostituite", "n_nate_intorno",
            "n_da_referto", "n_scadute_dal_giro", "operate", "per_famiglia", "per_coin",
            "promessa_vs_vissuto", "vite"} <= set(doc["strategie"])
    voce = doc["strategie"]["operate"][0]
    assert set(voce) == {"chiave", "coin", "strategia", "famiglia", "origine", "genitore",
                         "ipotesi", "pass", "validata_at", "ultimo_pass_at", "pf_promesso",
                         "pnl_promesso_pct", "t", "holdout_ok", "scala", "breakeven", "keep",
                         "direzione_pf", "paper"}       # niente sostituita_da: sarebbe sempre null
    assert set(voce["paper"]) == {"trades", "vinti", "pnl", "pf_vissuto", "perdite", "verdetto",
                                  "motivo"}
    # le distribuzioni sono liste di dizionari, la scala una stringa
    assert doc["registro"]["distribuzione_pass"][0].keys() == {"pass", "coppie", "coin"}
    # le validate sono 3: la madre sostituita (AUSDT|gen_m) non si opera e non conta
    assert doc["cervello"]["keep_validate"] == {"distribuzione": [{"valore": 0.5, "n": 2}],
                                                "non_rivalutate": 1}
    assert doc["cervello"]["scala_validate"] == [{"scala": "1.5/3/5", "n": 2},
                                                 {"scala": "nessuna", "n": 1}]
    assert doc["cervello"]["breakeven_validate"] == 2
    # le validate giudicate sulla propria configurazione e le declassate (26 set 2026)
    assert doc["giro"]["passate_solo_con_propria_config"] == 2
    assert doc["registro"]["declassate"] == 1
    assert doc["cervello"]["autopsia"]["criterio_principale"] == "total_return"
    assert doc["cervello"]["autopsia_base_congelata_da_s"] == 86400 * 4
    assert doc["cervello"]["supervisore"]["decisioni_none_di_fila"] == 2
    assert doc["cervello"]["riga"].startswith("IL CERVELLO NELL'ULTIMO GIRO: intorno 4 madri")
    assert doc["strategie"]["vite"] == {"promosse_7g": 1, "rimosse_7g": 1, "parziale": False}


def test_le_sezioni_falliscono_da_sole():
    """Fail-open PER SEZIONE: un registro storto rompe `registro`, non il documento."""
    pairs, specs, trades, drift = _fixture_piccola()
    doc = _costruisci(pairs, specs, trades, drift, letture={"supervisore": "non un dict"})
    assert doc["cervello"]["errore"] is None          # un accessorio storto si ignora
    doc = _costruisci(pairs, specs, trades, drift, esito={"intorno": "rotto"})
    assert doc["cervello"]["errore"] and "cervello" in doc["cervello"]["lettura"]
    assert doc["registro"]["errore"] is None and doc["strategie"]["errore"] is None


# --------------------------------------------------------------------------- #
# 2. in_corso fonde il solo meta                                               #
# --------------------------------------------------------------------------- #
def test_in_corso_tiene_le_sezioni_del_giro_precedente():
    prima = {"meta": {"versione_schema": 1, "stato": "finito", "fase": "discover",
                      "generato_at": NOW - 9000, "durata_s": 3000, "modalita": "completa",
                      "generato_da": "discovery", "errore": None, "iniziato_at": NOW - 12000},
             "giro": {"valutazioni": 900}, "registro": {"validate": 7},
             "cervello": {"intorno": {"madri": 2}}, "strategie": {"n_operate": 7}}
    fb = _FB({("dashboard", "gate"): prima})
    assert r.aggiorna_meta_gate(fb, {"stato": "in_corso", "fase": "optimize", "iniziato_at": NOW})
    dopo = fb.docs[("dashboard", "gate")]
    assert dopo["giro"] == {"valutazioni": 900} and dopo["registro"] == {"validate": 7}
    assert dopo["cervello"] == {"intorno": {"madri": 2}} and dopo["strategie"] == {"n_operate": 7}
    assert dopo["meta"]["stato"] == "in_corso" and dopo["meta"]["fase"] == "optimize"
    assert dopo["meta"]["iniziato_at"] == NOW
    assert dopo["meta"]["modalita"] == "completa"           # non toccato: si fonde
    assert fb.rtdb["/gate"] == dopo                         # e lo specchio RTDB


def test_in_corso_senza_documento_precedente_e_senza_rtdb_non_esplode(capsys):
    class _Solo:
        def __init__(self):
            self.docs = {}

        def get_doc(self, *a):
            raise RuntimeError("giu'")

        def set_doc(self, c, n, data):
            self.docs[(c, n)] = data

    fb = _Solo()
    assert r.aggiorna_meta_gate(fb, {"stato": "in_corso", "fase": "discover", "iniziato_at": 1.0})
    assert fb.docs[("dashboard", "gate")]["meta"]["versione_schema"] == 1
    assert "specchio RTDB /gate non scritto" in capsys.readouterr().out


def test_optimize_scrive_in_corso_all_avvio_e_il_tetto_nel_registro():
    src = inspect.getsource(o.main)
    assert 'aggiorna_meta_gate(fb, {"stato": "in_corso", "fase": "optimize"' in src
    assert src.index("_merge_shards(fb, args)") < src.index('"fase": "optimize"')
    fb = _FB({})
    reg = o.update_registry(fb, {}, [], universe=["AUSDT", "BUSDT"])
    assert reg["max_pairs"] == 3000
    assert fb.docs[("strategy_registry", "validated")]["max_pairs"] == 3000
    assert o.coppie_validate is r.coppie_validate       # una regola sola, ri-esportata


# --------------------------------------------------------------------------- #
# 3. Un giro caduto scrive errore e rilancia                                   #
# --------------------------------------------------------------------------- #
def test_un_giro_caduto_scrive_errore_e_rilancia(monkeypatch):
    prima = {"meta": {"stato": "finito"}, "registro": {"validate": 7}}
    fb = _FB({("dashboard", "gate"): prima})
    monkeypatch.setattr(d, "get_firebase", lambda: fb)
    monkeypatch.setattr(sys, "argv", ["discover", "--top", "1"])

    def _esplode(_fb):
        raise RuntimeError("boom del giro")

    monkeypatch.setattr(d, "prove_dal_paper", _esplode)
    with pytest.raises(RuntimeError, match="boom del giro"):
        d.main()
    meta = fb.docs[("dashboard", "gate")]["meta"]
    assert meta["stato"] == "errore" and "boom del giro" in meta["errore"]
    assert meta["fase"] == "discover" and meta["durata_s"] >= 0
    assert fb.docs[("dashboard", "gate")]["registro"] == {"validate": 7}   # sezioni intatte
    # e prima di cadere aveva dichiarato l'apertura, con la modalita'
    assert meta["modalita"] in ("completa", "solo urgenti") and meta["iniziato_at"] > 0


def test_la_discovery_pubblica_il_documento_in_coda_al_giro():
    src = inspect.getsource(d.main)
    assert 'aggiorna_meta_gate(fb, {"stato": "in_corso", "fase": fase_gate' in src
    assert "trades_paper = trades_del_paper(fb)" in src
    assert src.index("GIRO FINITO in") < src.index("pubblica_doc_gate(")
    assert 'if fase_gate == "discover":' in src          # la passata a 1h non chiude il giro
    assert src.rindex("except Exception as exc:") > src.index("pubblica_doc_gate(")
    assert '"stato": "errore"' in src and src.rstrip().endswith("raise")


# --------------------------------------------------------------------------- #
# 4. L'intorno dell'ultimo giro completo                                       #
# --------------------------------------------------------------------------- #
def test_l_intorno_si_ricopia_quando_il_giro_non_e_completo():
    pairs, specs, trades, drift = _fixture_piccola()
    prec = {"cervello": {"intorno": {"madri": 9, "figlie_passate": 3, "promosse": ["X|gen_1"],
                                     "senza_margine": 2, "madre_non_valutata": 0,
                                     "scartate": 0, "ultimo_completo_at": NOW - 86400}}}
    doc = _costruisci(pairs, specs, trades, drift, doc_prec=prec, intorno_girato=False)
    assert doc["cervello"]["intorno"] == prec["cervello"]["intorno"]
    assert "ultimo giro completo" in doc["cervello"]["lettura"]
    # senza documento precedente: null, non zeri che sembrerebbero un esito
    assert _costruisci(pairs, specs, trades, drift, intorno_girato=False)["cervello"]["intorno"] is None
    # nel giro completo: i numeri di questo giro e la data di oggi
    doc = _costruisci(pairs, specs, trades, drift, doc_prec=prec, intorno_girato=True)
    assert doc["cervello"]["intorno"]["madri"] == 4
    assert doc["cervello"]["intorno"]["ultimo_completo_at"] == NOW
    assert doc["cervello"]["varianti"]["sostituzioni"] == [{"figlia": "AUSDT|gen_v",
                                                            "madre": "AUSDT|gen_m"}]


# --------------------------------------------------------------------------- #
# 5. keep_giro = i numeri della riga del log                                   #
# --------------------------------------------------------------------------- #
def test_keep_giro_sono_i_numeri_di_riga_cervello_keep():
    out = {"A|x": {"profit_lock_keep": 0.25}, "B|x": {"profit_lock_keep": 0.5},
           "C|x": {"profit_lock_keep": 0.5}, "D|x": {"profit_lock_keep": 0.35},
           "E|x": {"profit_lock_keep": None}}
    chiavi = ["A|x", "B|x", "C|x", "D|x", "E|x"]
    k = d.conta_keep_giro(out, chiavi, keep_paper=0.25)
    assert k == {"scelti": [{"valore": 0.25, "n": 1}, {"valore": 0.35, "n": 1},
                            {"valore": 0.5, "n": 2}],
                 "non_scelto": 1, "dal_paper": 0.25, "dal_paper_n": 1}
    riga = d.riga_cervello_keep(out, chiavi, keep_paper=0.25)
    assert riga == ("[cervello] keep del lock scelto dal gate: 0.25 x1 · 0.35 x1 · 0.5 x2"
                    " · non scelto x1 (dal paper 0.25 x1)")
    assert d.conta_keep_giro({}, [], None) == {"scelti": [], "non_scelto": 0,
                                               "dal_paper": None, "dal_paper_n": 0}
    doc = _costruisci(*_fixture_piccola())
    assert doc["cervello"]["keep_giro"] == d.conta_keep_giro(
        {"AUSDT|gen_a": {"profit_lock_keep": 0.25}}, ["AUSDT|gen_a"], 0.25)


# --------------------------------------------------------------------------- #
# 6. Le operate: paper per coppia, robustezza, aggregati                       #
# --------------------------------------------------------------------------- #
def test_il_paper_per_coppia_esclude_gli_esiti_esterni_e_il_pf_senza_perdite_e_null():
    pairs, specs, trades, drift = _fixture_piccola()
    doc = _costruisci(pairs, specs, trades, drift)
    per = {v["chiave"]: v for v in doc["strategie"]["operate"]}
    # la madre sostituita non si opera; la figlia si'
    assert set(per) == {"AUSDT|gen_a", "BUSDT|gen_b", "AUSDT|gen_v"}
    a = per["AUSDT|gen_a"]
    assert a["paper"] == {"trades": 3, "vinti": 2, "perdite": 1, "pnl": 4.0,
                          "pf_vissuto": round(7 / 3, 3), "verdetto": "watch",
                          "motivo": "PF 0.67 vs 1.54 atteso"}     # il kill_switch non conta
    assert a["famiglia"] == "reversion" and a["scala"] == "1.5/3/5" and a["keep"] == 0.5
    assert a["direzione_pf"] == {"long": 1.2, "short": 0.9} and a["holdout_ok"] is True
    assert a["pnl_promesso_pct"] == 45.0 and a["t"] == 2.31
    b = per["BUSDT|gen_b"]
    assert b["paper"]["pf_vissuto"] is None and b["paper"]["perdite"] == 0
    assert b["paper"]["verdetto"] is None and b["pf_promesso"] is None
    assert b["scala"] is None and b["keep"] is None and b["breakeven"] is None
    v = per["AUSDT|gen_v"]
    assert v["origine"] == "referto" and v["genitore"] == "gen_m" and v["paper"] is None
    s = doc["strategie"]
    assert s["n_operate"] == 3 and s["n_con_paper"] == 2 and s["n_senza_promessa"] == 1
    assert s["n_sostituite"] == 1 and s["n_nate_intorno"] == 1 and s["n_da_referto"] == 1   # la madre gen_m
    assert s["n_scadute_dal_giro"] == 0
    assert s["per_coin"][0] == {"coin": "AUSDT", "coppie": 2, "paper_trades": 3, "paper_pnl": 4.0}
    fam = {f["famiglia"]: f for f in s["per_famiglia"]}
    assert fam["reversion"]["coppie"] == 2 and fam["reversion"]["paper_pf"] == round(7 / 3, 3)
    assert fam["ignota"]["coppie"] == 1 and fam["ignota"]["paper_pf"] is None
    assert s["promessa_vs_vissuto"] == {"pf_promesso_mediano_operate": 1.54,
                                        "pf_atteso_media_registro": 1.54,
                                        "pf_vissuto_30g": 0.9}


def test_senza_trade_i_campi_del_paper_sono_null_non_zero():
    pairs, specs, _, drift = _fixture_piccola()
    doc = _costruisci(pairs, specs, None, drift)
    s = doc["strategie"]
    assert s["n_con_paper"] is None
    assert all(v["paper"] is None for v in s["operate"])
    assert s["per_coin"][0]["paper_trades"] is None
    assert "NON disponibili" in s["dettaglio"]
    assert doc["giro"]["paper_propone"]["verdetti_trailing"] == 0


def test_la_regola_di_robustezza_e_quella_di_adaptation(monkeypatch):
    cls = next(v for v in vars(_ad).values() if isinstance(v, type) and hasattr(v, "_robust_only"))
    keys = ["A|breakout", "B|breakout", "C|breakout", "A|momentum", "D|gen_x", "E|gen_y",
            "senza_barra"]
    for n in (1, 2, 3):
        monkeypatch.setattr(settings, "MIN_COINS_PER_STRATEGY", n)
        assert r.coppie_robuste(keys) == cls._robust_only(keys), n
        assert r.coppie_robuste(keys, min_coins=n) == cls._robust_only(keys), n
    monkeypatch.setattr(settings, "MIN_COINS_PER_STRATEGY", 3)
    assert r.coppie_robuste(keys) == {"A|breakout", "B|breakout", "C|breakout", "D|gen_x", "E|gen_y"}
    pairs = {k: _rec(*k.split("|")) for k in keys if "|" in k}
    assert r.coppie_operate(pairs, NOW) == sorted(r.coppie_robuste(keys))


def test_le_operate_escludono_le_non_robuste_e_lo_contano():
    """Una base passata su una coin sola e' validata ma NON operata: entra in
    `n_scadute_dal_giro` (validate nel doc − operate)."""
    pairs = {"AUSDT|breakout": _rec("AUSDT", "breakout"), "BUSDT|gen_b": _rec("BUSDT", "gen_b")}
    doc = _costruisci(pairs, {}, [], {})
    assert [v["chiave"] for v in doc["strategie"]["operate"]] == ["BUSDT|gen_b"]
    assert doc["strategie"]["n_scadute_dal_giro"] == 1
    assert doc["strategie"]["operate"][0]["famiglia"] is None       # spec ignota: non si inventa


# --------------------------------------------------------------------------- #
# 7. Le estrazioni stampano in gate_progress le stesse righe                   #
# --------------------------------------------------------------------------- #
def _pairs_gate_progress(now):
    return {
        "AUSDT|gen_a": {"symbol": "AUSDT", "generated": True, "pass_count": 3, "last_seen_at": now - 100,
                        "window_start": now - 100, "last_t": 1.5,
                        "last_params": {"profit_lock_keep": 0.35}},
        "BUSDT|gen_b": {"symbol": "BUSDT", "generated": True, "pass_count": 3, "last_seen_at": now - 200,
                        "window_start": now - 200, "last_t": 2.3, "last_params": {}},
        "CUSDT|gen_c": {"symbol": "CUSDT", "generated": True, "pass_count": 1, "last_seen_at": now - 300,
                        "window_start": now - 10 * 86400},
        "DUSDT|gen_d": {"symbol": "DUSDT", "generated": True, "pass_count": 1, "last_seen_at": now - 400},
        "EUSDT|gen_e": {"symbol": "EUSDT", "generated": True, "pass_count": 2, "last_seen_at": now - 50,
                        "window_start": now - 8 * 86400},
        "ZUSDT|gen_z": {"symbol": "ZUSDT", "generated": True, "pass_count": 2,
                        "last_seen_at": now - 10 * 86400, "window_start": now - 8 * 86400},
        "FUSDT|breakout": {"symbol": "FUSDT", "generated": False, "pass_count": 0,
                           "last_seen_at": now - 10},
    }


def test_gate_progress_stampa_le_stesse_righe_di_prima(monkeypatch, capsys):
    """Le righe qui sotto sono quelle che il codice inline di gate_progress
    produceva prima dell'estrazione (25 set 2026): sono il contratto con chi le
    legge dal canale ops."""
    now = time.time()
    fb = _FB({("strategy_registry", "validated"): {"pairs": encode_pairs(_pairs_gate_progress(now)),
                                                   "ready": False}})
    monkeypatch.setattr(g, "get_firebase", lambda: fb)
    monkeypatch.setattr(sys, "argv", ["gate_progress"])
    assert g.main() == 0
    out = capsys.readouterr().out
    assert "[gate] 7 coppie nel registro · 6 ancora valutate · soglia 3 pass" in out
    assert ("  distribuzione pass (solo coppie vive): 0 pass: 1 su 1 coin · 1 pass: 2 su 2 coin"
            " · 2 pass: 1 su 1 coin · 3 pass: 2 su 2 coin") in out
    assert "  CONGELATE: 1 coppie non piu' valutate da oltre 3 giorni (1 avevano gia' un passaggio)." in out
    assert "  COMPOSIZIONE (vive): 1 base · 5 generate.  Nel registro intero: 1 base su 7, tetto 3000." in out
    assert "  VALIDATE ora: 2 su 2 coin distinte" in out
    assert "  FINESTRE APERTE: 4/5 coppie con almeno un passaggio." in out
    assert ("  STATISTICA t DELLE VALIDATE: 2 con misura · 1 reggerebbero t >= 2 · mediana 2.30"
            " · le piu' basse: AUSDT|gen_a (1.50), BUSDT|gen_b (2.30)") in out
    assert "  A UN PASSO DALLA VALIDAZIONE: 1 coppie a 2/3." in out
    assert "  Di queste, 1 su 1 coin hanno GIA' la finestra scaduta" in out
    assert "  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x1 · non ancora rivalutate x1" in out
    # e gli stessi numeri escono dalle estrazioni che il documento del gate usa
    dp = r.distribuzione_pass(_pairs_gate_progress(now), now)
    assert dp["distribuzione"] == [{"pass": 0, "coppie": 1, "coin": 1}, {"pass": 1, "coppie": 2, "coin": 2},
                                   {"pass": 2, "coppie": 1, "coin": 1}, {"pass": 3, "coppie": 2, "coin": 2}]
    assert (dp["congelate"], dp["congelate_con_conferme"], dp["a_un_passo"], dp["finestre_scadute"]) == (1, 1, 1, 1)
    st = r.statistica_t(_pairs_gate_progress(now))
    assert (st["misurate"], st["sopra_2"], st["sopra_3"], st["mediana"]) == (2, 1, 0, 2.3)
    assert st["piu_basse"] == [{"coppia": "AUSDT|gen_a", "t": 1.5}, {"coppia": "BUSDT|gen_b", "t": 2.3}]
    src = inspect.getsource(g.main)
    for chiamata in ("distribuzione_pass(pairs, now)", "statistica_t(pairs)",
                     "salute_registro(pairs)", "coppie_validate(pairs, now)"):
        assert chiamata in src, chiamata
    assert "conta_keep(" in inspect.getsource(g.riga_keep_validate)


def test_salute_registro_e_il_gemello_di_state_snapshot():
    from scripts.state_snapshot import _salute_registro
    now = time.time()
    pairs = _pairs_gate_progress(now)
    s = r.salute_registro(pairs)
    righe = "\n".join(_salute_registro(pairs))
    assert f"**{s['base']} base** · **{s['generate']} generate** (di cui {s['generate_con_conferme']} con" in righe
    assert f"occupazione: {s['coppie']}/{s['limite']}" in righe
    assert s == {"coppie": 7, "base": 1, "generate": 6, "generate_con_conferme": 6,
                 "occupazione": 7, "limite": 3000, "alleggerito": True}   # le validate senza pnl
    assert r.salute_registro({})["coppie"] == 0
    assert r.salute_registro({"A|gen_a": _rec("A", "gen_a")})["alleggerito"] is False


def test_le_altre_estrazioni():
    pairs = {"A|gen_a": _rec("A", "gen_a"), "B|gen_b": _rec("B", "gen_b", last_pf=0,
                                                             last_params={"profit_lock_keep": "0.35"}),
             "C|gen_c": _rec("C", "gen_c", last_params={"scale_r_mults": (1.0, 2.0),
                                                        "sl_to_breakeven": False})}
    val = ["A|gen_a", "B|gen_b", "C|gen_c"]
    assert r.conta_keep(pairs, val) == {"distribuzione": [{"valore": 0.35, "n": 1}, {"valore": 0.5, "n": 1}],
                                        "non_rivalutate": 1}
    assert r.scala_distribuzione(pairs, val) == [{"scala": "1.5/3/5", "n": 1}, {"scala": "1/2", "n": 1},
                                                 {"scala": "nessuna", "n": 1}]
    assert r.breakeven_n(pairs, val) == 1 and r.senza_promessa(pairs, val) == 1
    assert r.scala_str(None) is None and r.scala_str([1.5, 3, 5]) == "1.5/3/5"


# --------------------------------------------------------------------------- #
# 8. Il diario delle vite anche dalla discovery                                #
# --------------------------------------------------------------------------- #
def test_il_merge_registra_le_promozioni_nel_diario():
    fb = _FB({("strategy_registry", "validated"): {"pairs": encode_pairs({
        "AUSDT|gen_a": {"symbol": "AUSDT", "strategy": "gen_a", "generated": True, "pass_count": 2,
                        "window_start": 1e9 - NEW_DATA_MIN_S - 1, "last_seen_at": 1e9}})}})
    e = {"symbol": "AUSDT", "strategy": "gen_a", "params": {}, "oos_pf": 1.5, "oos_pnl_pct": 0.3,
         "oos_trades": 40, "oos_win_rate": 0.5, "passed": True, "data_end": 1e9}
    d.merge_into_registry(fb, {"AUSDT|gen_a": e}, ["AUSDT|gen_a"], evaluated_symbols={"AUSDT"})
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    assert pairs["AUSDT|gen_a"]["pass_count"] == MIN_PASSES and pairs["AUSDT|gen_a"]["validated_at"] > 0
    eventi = fb.docs[("gate_history", "lifecycle")]["events"]
    assert [(v["key"], v["tipo"]) for v in eventi] == [("AUSDT|gen_a", "promossa")]
    assert fb.docs[("strategy_registry", "validated")]["max_pairs"] == 3000
    # una gia' validata che ripassa NON e' una promozione: niente riga nuova
    d.merge_into_registry(fb, {"AUSDT|gen_a": e}, ["AUSDT|gen_a"], evaluated_symbols={"AUSDT"})
    assert len(fb.docs[("gate_history", "lifecycle")]["events"]) == 1


# --------------------------------------------------------------------------- #
# 9. I trade letti una volta                                                   #
# --------------------------------------------------------------------------- #
def test_scala_e_keep_usano_i_trade_gia_letti_senza_toccare_firebase():
    tf = settings.ORCHESTRATOR_TIMEFRAME
    verdetti = [{"exit_reason": "trailing_stop", "timeframe": tf, "trailing_verdict": "premature"}] * 6 \
        + [{"exit_reason": "trailing_stop", "timeframe": tf, "trailing_verdict": "protected"}] * 2
    rotto = _FB(rotto=True)
    assert d.keep_dal_paper(rotto, trades=verdetti) == 0.25
    assert d.conta_verdetti_trailing(verdetti, tf) == (6, 2)
    mfes = [{"mfe_r": 0.6}] * 20
    assert d.scala_dal_paper(rotto, trades=mfes) == d.scala_dal_paper(_FB(trades=mfes))
    assert d.trades_del_paper(rotto) is None          # e chi la riceve fa da se'
    assert d.keep_dal_paper(rotto) is None            # ...con il fail-open di prima
    assert d.trades_del_paper(_FB(trades=mfes)) == mfes


# --------------------------------------------------------------------------- #
# 10. Dimensione e guardia di serializzazione                                  #
# --------------------------------------------------------------------------- #
def _fixture_300():
    pairs, specs, trades, drift = {}, {}, [], {"pairs": {}, "global": {"trades": 900, "live_pf": 0.8}}
    for i in range(100):
        sym = f"C{i:03d}USDT"
        for j in range(3):
            sid = f"gen_{i:03d}{j}abcdef0123"
            key = f"{sym}|{sid}"
            pairs[key] = _rec(sym, sid, last_pf=1.5 + j / 10, last_t=2.0 + i / 100)
            specs[sid] = _spec(sid, origine="intorno", genitore=f"gen_madre{i:03d}",
                               ipotesi="intorno:rsi_extreme.low=25")
            trades += [{"symbol": sym, "strategy": sid, "pnl": p, "exit_reason": "take_profit"}
                       for p in (5.0, -3.0, 2.0)]
            drift["pairs"][key] = {"verdict": "watch", "reason": "PF 0.40 vs 1.54 atteso · mfe mediana 0.74R < primo TP 1.50R"}
    return pairs, specs, trades, drift


def test_con_300_operate_il_documento_sta_sotto_200_kb():
    pairs, specs, trades, drift = _fixture_300()
    doc = _costruisci(pairs, specs, trades, drift)
    assert doc["strategie"]["n_operate"] == 300 and len(doc["strategie"]["operate"]) == 300
    assert doc["strategie"]["operate_troncate"] == 0
    assert doc["strategie"]["n_con_paper"] == 300 and doc["registro"]["validate"] == 300
    pulito = r.pulisci_per_firestore(doc)
    n = len(json.dumps(pulito, ensure_ascii=False, allow_nan=False).encode("utf-8"))
    assert n < d.DOC_GATE_MAX_BYTES, n
    assert pulito == doc                                   # gia' pulito per costruzione


def test_la_guardia_di_serializzazione():
    sporco = {"a.b/c#d$e[f]": float("nan"), "inf": float("inf"), "tupla": (1, 2),
              "liste": [[1, 2], [3]], "ok": [{"valore": 0.5, "n": 1}], 3: "chiave numerica",
              "annidato": {"x": [(1.0, float("-inf"))]}, "bool": True, "none": None}
    pulito = r.pulisci_per_firestore(sporco)
    assert pulito["a_b_c_d_e_f_"] is None and pulito["inf"] is None
    assert pulito["tupla"] == [1, 2] and pulito["liste"] == [{"valori": [1, 2]}, {"valori": [3]}]
    assert pulito["ok"] == [{"valore": 0.5, "n": 1}] and pulito["3"] == "chiave numerica"
    assert pulito["annidato"] == {"x": [{"valori": [1.0, None]}]}
    assert pulito["bool"] is True and pulito["none"] is None
    json.dumps(pulito, allow_nan=False)                    # non solleva
    assert not any(c in k for k in pulito for c in ".#$[]/")


def test_scrivi_doc_gate_pulisce_e_non_solleva(capsys):
    class _Rifiuta(_FB):
        def set_doc(self, *a):
            raise RuntimeError("document exceeds maximum size")

    fb = _Rifiuta()
    assert r.scrivi_doc_gate(fb, {"meta": {"x": math.nan}}) is False
    assert fb.rtdb["/gate"] == {"meta": {"x": None}}      # lo specchio si scrive comunque
    assert "Firestore dashboard/gate non scritto" in capsys.readouterr().out


def test_pubblica_doc_gate_legge_il_registro_dopo_il_merge_e_scrive_tutto(capsys):
    pairs, specs, trades, drift = _fixture_piccola()
    fb = _FB({("strategy_registry", "validated"): _reg_doc(pairs),
              ("discovered_strategies", "specs"): {"specs": encode_pairs(specs)},
              ("drift", "current"): drift}, trades=trades)
    doc = d.pubblica_doc_gate(fb, trades=trades, esito=_esito(), run=_run(), keep_paper=None,
                              scala_paper=None, doc_prec={}, now=NOW, iniziato_at=NOW - 60,
                              modalita="completa", intorno_girato=True, candidate=None,
                              keep_giro=None)
    assert doc is not None and fb.docs[("dashboard", "gate")]["meta"]["stato"] == "finito"
    assert fb.rtdb["/gate"]["strategie"]["n_operate"] == 3
    assert fb.docs[("dashboard", "gate")]["cervello"]["keep_giro"]["scelti"] == []
    assert "[gate-doc] dashboard/gate scritto: finito (completa" in capsys.readouterr().out
    # un Firebase rotto non fa cadere il giro
    class _Giu:
        def get_doc(self, *a):
            raise RuntimeError("giu'")

    assert d.pubblica_doc_gate(_Giu(), trades=None, esito={}, run={}, keep_paper=None,
                               scala_paper=None, doc_prec={}, now=NOW, iniziato_at=NOW,
                               modalita="completa", intorno_girato=False) is None
    assert "documento del gate non costruito" in capsys.readouterr().out
