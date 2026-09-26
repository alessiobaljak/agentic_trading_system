"""IL GIRO COMPLETO RIDOTTO e la ricarica del registro alla scrittura (26 set
2026, passo 3 del piano del 26 set 15:xx, backlog J10).

Il numero che l'ha fatto nascere: il primo giro completo con tutte le spec
(26 set, ops 0282-0284) ha fatto 134.994 valutazioni in 3h48; ~120.000 erano le
~502 spec NOTE rivalutate su tutte le ~240 coin. Da oggi nel giro completo le
spec note si valutano solo (a) sulle coin dove hanno una coppia viva e (b) su
una fetta rotante di 1/7 dell'universo; le candidate nuove restano su tutte.

E il bot ricarica il registro APPENA il gate lo scrive (`updated_at` diverso),
non un'ora dopo: una domanda al minuto, fail-open sulla ricarica oraria."""
from __future__ import annotations

import inspect
import os
import types

import pytest

from bot.core.firebase_client import FirebaseClient, encode_pairs
from bot.learning.adaptation import AdaptationEngine
from scripts import discover_strategies as d
from tests.test_doc_gate import _costruisci, _fixture_piccola, _run

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOW = 1_758_844_800.0 + 3 * 3600          # 2026-09-26 03:00 UTC: un giro completo di notte
COIN = [f"{c}USDT" for c in ("ZZZ", "AAA", "MMM", "BBB", "QQQ", "CCC", "DDD", "EEE",
                             "FFF", "GGG", "HHH", "III", "JJJ", "KKK", "LLL", "NNN",
                             "OOO", "PPP", "RRR", "SSS")]


def _spec(sid, **extra):
    return {"id": sid, "features": [{"kind": "rsi", "period": 14}], **extra}


def _rec(sym, sid, passi=1, **extra):
    r = {"symbol": sym, "strategy": sid, "generated": True, "pass_count": passi,
         "last_seen_at": NOW - 100}
    r.update(extra)
    return r


# --------------------------------------------------------------------------- #
# 1. la fetta rotante                                                          #
# --------------------------------------------------------------------------- #
def test_la_fetta_e_deterministica_e_copre_ogni_coin_una_volta_in_sette_giorni():
    viste = []
    for giorno in range(7):
        fetta = d.coin_della_fetta(COIN, NOW + giorno * 86400)
        assert fetta == d.coin_della_fetta(list(reversed(COIN)), NOW + giorno * 86400), \
            "l'ordine con cui arrivano le coin (il volume, che cambia) non deve contare"
        assert fetta == d.coin_della_fetta(COIN, NOW + giorno * 86400 + 4 * 3600), \
            "stesso giorno UTC, stessa fetta: il giro parte a ore diverse"
        viste.extend(sorted(fetta))
    assert sorted(viste) == sorted(COIN), "in sette giorni ogni coin entra esattamente una volta"
    assert d.coin_della_fetta(COIN, NOW + 7 * 86400) == d.coin_della_fetta(COIN, NOW)
    # 20 coin su 7 fette: fette da 2 o 3 coin, nessuna vuota
    assert all(2 <= len(d.coin_della_fetta(COIN, NOW + g * 86400)) <= 3 for g in range(7))


def test_la_fetta_del_giorno_non_salta_a_capodanno():
    from datetime import datetime, timezone
    ultimo = datetime(2026, 12, 31, 3, tzinfo=timezone.utc).timestamp()
    primo = datetime(2027, 1, 1, 3, tzinfo=timezone.utc).timestamp()
    assert (d.fetta_del_giorno(ultimo) + 1) % 7 == d.fetta_del_giorno(primo)
    assert 0 <= d.fetta_del_giorno(NOW) < 7
    assert d.RIDUZIONE_FETTE == 7 and d.RIDUZIONE_ENABLED is True


# --------------------------------------------------------------------------- #
# 2. le spec note vanno per coin, le nuove restano comuni                       #
# --------------------------------------------------------------------------- #
def _caso():
    existing = {"gen_a": _spec("gen_a"), "gen_b": _spec("gen_b")}
    specs = [_spec("gen_a"), _spec("gen_b"), _spec("gen_new"), _spec("gen_ai", origine="ai")]
    pairs = {"AAAUSDT|gen_a": _rec("AAAUSDT", "gen_a", passi=1),
             "BBBUSDT|gen_a": _rec("BBBUSDT", "gen_a", passi=3),
             "CCCUSDT|gen_b": _rec("CCCUSDT", "gen_b", passi=0),            # mai passata: non conta
             "DDDUSDT|momentum": {"symbol": "DDDUSDT", "strategy": "momentum",
                                  "generated": False, "pass_count": 3},   # base: non e' una spec nota
             "XXXUSDT|gen_b": _rec("XXXUSDT", "gen_b", passi=2)}          # coin fuori universo
    return existing, specs, pairs


def test_le_spec_note_solo_su_coin_proprie_e_fetta_le_nuove_su_tutte():
    existing, specs, pairs = _caso()
    comuni, per_coin, rid = d.riduci_spec_note(specs, existing, pairs, COIN, {}, now=NOW)
    assert [s["id"] for s in comuni] == ["gen_new", "gen_ai"], "le nuove restano nella lista comune"
    fetta = d.coin_della_fetta(COIN, NOW)
    for sym in COIN:
        attese = []
        if sym in fetta or sym in ("AAAUSDT", "BBBUSDT"):
            attese.append("gen_a")
        if sym in fetta:
            attese.append("gen_b")
        assert [s["id"] for s in per_coin.get(sym, [])] == attese, sym
    assert "XXXUSDT" not in per_coin, "una coin fuori dall'universo non si valuta"
    assert rid["spec_note"] == 2
    assert rid["coin_proprie"] == 2                       # AAA e BBB (CCC a 0 pass non conta)
    assert rid["fetta"] == f"{d.fetta_del_giorno(NOW) + 1}/7"
    stimate = 2 * len(COIN) + sum(len(v) for v in per_coin.values())
    assert rid["valutazioni_stimate"] == stimate
    assert rid["_coin_note"] == len(fetta | {"AAAUSDT", "BBBUSDT"}) and rid["_nuove"] == 2
    # gli oggetti spec sono gli stessi (non copie): i worker li leggono e basta
    assert any(sp is specs[0] for sp in per_coin["AAAUSDT"])


def test_la_riduzione_taglia_davvero_il_lavoro():
    """Il conto che giustifica il passo: 500 spec note x 240 coin = 120.000; con
    coin proprie + fetta di 1/7 si scende a ~1/7 piu' le coppie vive."""
    existing = {f"gen_{i}": _spec(f"gen_{i}") for i in range(500)}
    specs = list(existing.values()) + [_spec(f"gen_new_{i}") for i in range(90)]
    coin = [f"C{i:03d}USDT" for i in range(240)]
    pairs = {f"{coin[i % 240]}|gen_{i}": _rec(coin[i % 240], f"gen_{i}") for i in range(500)}
    comuni, per_coin, rid = d.riduci_spec_note(specs, existing, pairs, coin, {}, now=NOW)
    assert len(comuni) == 90
    pieno = 590 * 240
    assert rid["valutazioni_stimate"] < pieno / 2, (rid, pieno)
    # 90 nuove x 240 + ~35 coin di fetta x 500 + 500 coppie proprie (meno quelle gia' in fetta)
    assert 90 * 240 + 34 * 500 <= rid["valutazioni_stimate"] <= 90 * 240 + 35 * 500 + 500


def test_le_figlie_dell_intorno_restano_per_coin_dopo_le_note():
    existing, specs, pairs = _caso()
    figlia = _spec("gen_figlia", origine="intorno", genitore="gen_a")
    comuni, per_coin, rid = d.riduci_spec_note(specs, existing, pairs, COIN,
                                               {"AAAUSDT": [figlia]}, now=NOW)
    ids = [s["id"] for s in per_coin["AAAUSDT"]]
    assert ids[-1] == "gen_figlia" and ids[0] == "gen_a"
    assert rid["valutazioni_stimate"] == 2 * len(COIN) + sum(len(v) for v in per_coin.values())


def test_una_coppia_congelata_si_valuta_lo_stesso_se_la_coin_e_in_universo():
    """Il merge segna «vista» e giudica (fallita) ogni coppia generata con
    pass_count >= 1 la cui coin e' stata valutata e la cui spec era nel giro:
    escluderla dalla valutazione sarebbe un verdetto inventato."""
    pairs = {"AAAUSDT|gen_a": _rec("AAAUSDT", "gen_a", passi=2, last_seen_at=NOW - 30 * 86400)}
    assert d.coin_proprie_delle_spec(pairs) == {"gen_a": {"AAAUSDT"}}
    assert d.coin_proprie_delle_spec({"AAAUSDT|gen_a": _rec("AAAUSDT", "gen_a", passi=0)}) == {}
    assert d.coin_proprie_delle_spec({"AAAUSDT|gen_a": "rotto", "x": None}) == {}


def test_senza_spec_note_non_cambia_niente():
    specs = [_spec("gen_new")]
    comuni, per_coin, rid = d.riduci_spec_note(specs, {}, {}, COIN, {}, now=NOW)
    assert [s["id"] for s in comuni] == ["gen_new"] and per_coin == {}
    assert rid["spec_note"] == 0 and rid["valutazioni_stimate"] == len(COIN)


def test_la_riga_di_log():
    riga = d.riga_riduzione({"spec_note": 500, "_coin_note": 60, "fetta": "3/7", "_nuove": 90,
                             "valutazioni_stimate": 42000})
    assert riga.startswith("[discover] completa: 500 spec note su 60 coin (proprie + rotazione 3/7) "
                           "+ 90 candidate nuove su tutte")
    assert "42000 valutazioni stimate" in riga


def test_gate_progress_stampa_il_giro_ridotto_dal_doc_del_giro():
    """`gate` (ops) mette `giro.riduzione` accanto alle valutazioni fatte: e' il
    confronto del metro di J10. Chiave assente = codice precedente; None = giro
    non ridotto; dict = la riga con stima contro fatte. E `main` la stampa."""
    from scripts import gate_progress as g
    assert "non registrato" in g.riga_riduzione_giro({})
    assert "non registrato" in g.riga_riduzione_giro(None)
    r = g.riga_riduzione_giro({"riduzione": None, "reeval_modalita": "solo urgenti"})
    assert r.startswith("  GIRO RIDOTTO: no, tutte le spec") and "solo urgenti" in r
    r = g.riga_riduzione_giro({"riduzione": {"spec_note": 500, "coin_proprie": 62, "fetta": "3/7",
                                             "valutazioni_stimate": 42000}, "n_eval": 47000})
    assert r == ("  GIRO RIDOTTO: 500 spec note su 62 coin proprie + fetta 3/7 · "
                 "~42000 valutazioni stimate contro 47000 fatte")
    assert "print(riga_riduzione_giro(diag))" in inspect.getsource(g.main)


# --------------------------------------------------------------------------- #
# 3. il main: solo nel giro completo, prima dei worker, e lo scrive             #
# --------------------------------------------------------------------------- #
def test_il_main_riduce_solo_nel_giro_completo_e_prima_dei_worker():
    main = inspect.getsource(d.main)
    assert ('riduzione_attiva = bool(RIDUZIONE_ENABLED and _completa and not getattr(args, "symbols", "")'
            in main)
    assert "and args.num_shards <= 1)" in main
    assert "specs, specs_per_symbol, riduzione = riduci_spec_note(" in main
    assert "print(riga_riduzione(riduzione))" in main
    assert '"riduzione": riduzione,' in main
    # PRIMA dello sharding, della composizione delle candidate e dei worker
    i_rid = main.index("riduci_spec_note(")
    assert i_rid < main.index("symbols = full_symbols[args.shard::args.num_shards]")
    assert i_rid < main.index('candidate = {"totale": len(specs)')
    assert i_rid < main.index("parallel_map(")
    # e DOPO l'intorno, che riempie lo stesso canale per coin
    assert main.index("specs_per_symbol.setdefault(_sym, []).extend(_figlie)") < i_rid


def test_il_worker_legge_le_note_dallo_stesso_canale_delle_figlie():
    """La riduzione non tocca i worker: `_disc_one` valuta `specs` (comuni) piu'
    `specs_per_symbol[sym]`, e li' ora ci sono anche le spec note della coin."""
    uno = inspect.getsource(d._disc_one)
    assert 'tutte = list(specs) + list((_W.get("specs_per_symbol") or {}).get(sym, []))' in uno


# --------------------------------------------------------------------------- #
# 4. il documento del gate e il contratto                                       #
# --------------------------------------------------------------------------- #
def test_il_documento_del_gate_porta_la_riduzione_o_null():
    doc = _costruisci(*_fixture_piccola())
    assert doc["giro"]["riduzione"] == {"spec_note": 500, "coin_proprie": 60, "fetta": "3/7",
                                        "valutazioni_stimate": 42000}
    doc = _costruisci(*_fixture_piccola(), run=_run(riduzione=None))
    assert doc["giro"]["riduzione"] is None
    doc = _costruisci(*_fixture_piccola(), run=_run(riduzione={"spec_note": "7", "fetta": 2}))
    assert doc["giro"]["riduzione"] == {"spec_note": 7, "coin_proprie": 0, "fetta": "2",
                                        "valutazioni_stimate": 0}
    assert "riduzione" in doc["giro"]["dettaglio"]


def test_contratto_e_tipi_conoscono_la_riduzione():
    with open(os.path.join(ROOT, "docs", "controllo_schema.md"), encoding="utf-8") as f:
        assert "| `riduzione` | {spec_note: int, coin_proprie: int, fetta: str, valutazioni_stimate: int}" in f.read()
    ts = os.path.join(ROOT, "dashboard", "app", "lib", "gate.ts")
    if os.path.exists(ts):
        with open(ts, encoding="utf-8") as f:
            src = f.read()
        assert "riduzione?: {" in src and "valutazioni_stimate?: number | null;" in src


# --------------------------------------------------------------------------- #
# 5. il bot ricarica il registro alla scrittura                                #
# --------------------------------------------------------------------------- #
def _registro(updated_at):
    return {"updated_at": updated_at, "pairs": encode_pairs({}), "validated": [], "ready": False}


def test_registro_cambiato_confronta_updated_at_con_l_ultima_lettura():
    fb = FirebaseClient()                                   # in memoria (nessun Firebase nei test)
    fb.set_doc("strategy_registry", "validated", _registro(1.0))
    a = AdaptationEngine(fb)
    assert a._registro_updated_at == 1.0
    assert a.registro_cambiato() is False
    fb.set_doc("strategy_registry", "validated", _registro(2.0))
    assert a.registro_cambiato() is True
    a.load_params()
    assert a._registro_updated_at == 2.0 and a.registro_cambiato() is False
    # formato vecchio senza updated_at: non si puo' dire, quindi no
    fb.set_doc("strategy_registry", "validated", {"pairs": encode_pairs({})})
    assert a.registro_cambiato() is False


def test_registro_cambiato_e_fail_open():
    class Rotto:
        _fs = None
        is_live = False

        def get_doc(self, c, k):
            if c == "strategy_registry":
                raise RuntimeError("giu'")
            return None

    a = AdaptationEngine.__new__(AdaptationEngine)
    a.fb = Rotto()
    a._registro_updated_at = 1.0
    assert a.registro_cambiato() is False


def test_sul_firestore_vero_si_chiede_un_solo_campo():
    """Il registro e' ~1 MB: ogni minuto si legge SOLO `updated_at` (proiezione
    lato server), non il documento intero."""
    visto = {}

    class Snap:
        exists = True

        def to_dict(self):
            return {"updated_at": 5.0}

    class Doc:
        def get(self, field_paths=None):
            visto["field_paths"] = list(field_paths or [])
            return Snap()

    class Coll:
        def document(self, k):
            visto["doc"] = k
            return Doc()

    class FS:
        def collection(self, c):
            visto["coll"] = c
            return Coll()

    class FB:
        _fs = FS()
        is_live = True

        def get_doc(self, c, k):
            raise AssertionError("sul Firestore vero non si legge il documento intero")

    a = AdaptationEngine.__new__(AdaptationEngine)
    a.fb = FB()
    a._registro_updated_at = 4.0
    assert a.registro_cambiato() is True
    assert visto == {"coll": "strategy_registry", "doc": "validated", "field_paths": ["updated_at"]}


def _bot_finto(fb):
    from bot.main import TradingBot
    b = types.SimpleNamespace(fb=fb, adaptation=AdaptationEngine(fb), last_adapt_reload=0.0,
                              _registro_check_at=0.0, _registro_rileggi_spec=False)
    b.conta = {"selettore": 0, "generated": 0, "params": 0}
    b._load_selettore = lambda: b.conta.__setitem__("selettore", b.conta["selettore"] + 1)
    _lg, _lp = b.adaptation.load_generated, b.adaptation.load_params
    b.adaptation.load_generated = lambda: (b.conta.__setitem__("generated", b.conta["generated"] + 1), _lg())
    b.adaptation.load_params = lambda: (b.conta.__setitem__("params", b.conta["params"] + 1), _lp())
    b._ricarica_registro_se_cambiato = types.MethodType(TradingBot._ricarica_registro_se_cambiato, b)
    return b


def test_il_loop_ricarica_alla_scrittura_e_chiede_al_massimo_una_volta_al_minuto(capsys):
    from bot import main as bot_main
    fb = FirebaseClient()
    fb.set_doc("strategy_registry", "validated", _registro(1.0))
    b = _bot_finto(fb)
    letture = {"n": 0}
    _get = fb.get_doc

    def get_doc(c, k):
        if c == "strategy_registry":
            letture["n"] += 1
        return _get(c, k)
    fb.get_doc = get_doc

    assert b._ricarica_registro_se_cambiato(100.0) is False        # niente di nuovo
    assert letture["n"] == 1
    fb.set_doc("strategy_registry", "validated", _registro(2.0))    # il gate scrive
    assert b._ricarica_registro_se_cambiato(130.0) is False         # < 60 s: non si richiede
    assert letture["n"] == 1
    assert b._ricarica_registro_se_cambiato(161.0) is True          # 61 s dopo: si ricarica
    assert b.conta == {"selettore": 1, "generated": 1, "params": 1}
    assert b.last_adapt_reload == 161.0 and b._registro_rileggi_spec is True
    assert b.adaptation._registro_updated_at == 2.0
    # un minuto dopo: le spec si rileggono UNA volta ancora (persist_specs
    # arriva subito dopo il merge), il registro non e' cambiato -> niente ricarica
    assert b._ricarica_registro_se_cambiato(222.0) is False
    assert b.conta["generated"] == 2 and b.conta["params"] == 1 and b._registro_rileggi_spec is False
    assert b._ricarica_registro_se_cambiato(283.0) is False and b.conta["generated"] == 2
    out = capsys.readouterr().out
    assert "[main] registro riscritto dal gate: ricarico" in out
    assert bot_main.REGISTRO_CHECK_S == 60.0


def test_la_ricarica_alla_scrittura_e_fail_open():
    fb = FirebaseClient()
    fb.set_doc("strategy_registry", "validated", _registro(1.0))
    b = _bot_finto(fb)
    b.adaptation.registro_cambiato = lambda: (_ for _ in ()).throw(RuntimeError("giu'"))
    assert b._ricarica_registro_se_cambiato(100.0) is False
    assert b.conta == {"selettore": 0, "generated": 0, "params": 0} and b.last_adapt_reload == 0.0


def test_il_run_chiama_il_controllo_a_ogni_iterazione():
    from bot.main import TradingBot
    run = inspect.getsource(TradingBot.run)
    assert "self._ricarica_registro_se_cambiato(now)" in run
    # dentro il try del ciclo, dopo la ricarica oraria e prima del regime
    i = run.index("self._ricarica_registro_se_cambiato(now)")
    assert run.index("self.last_adapt_reload = now") < i < run.index("self.refresh_regime(now)")
    init = inspect.getsource(TradingBot.__init__)
    assert "self._registro_check_at = 0.0" in init and "self._registro_rileggi_spec = False" in init
    # e `load_params` cattura l'istante con cui si confronta
    assert 'self._registro_updated_at = reg.get("updated_at")' in inspect.getsource(AdaptationEngine.load_params)
