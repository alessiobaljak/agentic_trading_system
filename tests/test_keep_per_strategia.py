"""IL KEEP DEL PROFIT-LOCK PROPOSTO PER STRATEGIA DAI VERDETTI TRAILING (27 set
2026, backlog I3, si' del proprietario).

Dal 25 set il paper propone UN keep per tutte le coppie insieme
(`keep_dal_paper`, regola `metrics.proposta_keep`). Ma «il lock taglia i
vincitori» puo' essere vero per una strategia e falso per un'altra, e i verdetti
portano gia' il perche' (`trailing_knockout_atr`: rumore sotto un ATR, o
inversione vera). Da oggi il paper propone anche un keep per OGNI strategia con
almeno 5 verdetti trailing, con la regola dichiarata in
`metrics.proposta_keep_strategia`: allargare (0.25) solo se i prematuri sono al
60% E almeno meta' da rumore; stringere (0.75) se i protetti sono al 60%.
La stessa strada della scala per strategia (`scale_per_strategia`, I4).

Cosa si protegge: la regola (soglie, condizione del rumore, le due direzioni,
sotto campione -> None, altri timeframe/uscite ignorati); la misura del tragitto
lasciato sul tavolo (solo stampata); il raggruppamento per id; l'ordine e la
de-dup dei candidati con tre fonti; gli argomenti dei worker in coda con default;
le conferme retroattive che vedono gli stessi candidati; la riga `[paper]`; il
documento del gate e la sua parita' con lo schema; il blocco di `trade_stats`.
"""
import inspect
from types import SimpleNamespace

from bot.config import settings
from bot.execution.exit_logic import LOCK_KEEP_CANDIDATES
from bot.learning import metrics as m
from scripts import discover_strategies as d
from scripts import trade_stats

TF = settings.ORCHESTRATOR_TIMEFRAME


def _v(verdetto, ko=None, gid="gen_x", tf=TF, exit_reason="trailing_stop", miss=None):
    t = {"strategy": gid, "symbol": "AUSDT", "pnl": 1.0, "exit_reason": exit_reason,
         "timeframe": tf, "trailing_verdict": verdetto, "trailing_knockout_atr": ko}
    if miss is not None:
        t["trailing_miss_to_tp"] = miss
    return t


# --------------------------------------------------------------------------- #
# 1. la regola per strategia                                                   #
# --------------------------------------------------------------------------- #
def test_le_costanti_sono_dichiarate_e_non_toccano_la_regola_globale():
    assert m.KEEP_STRATEGIA_MIN_VERDETTI == 5
    assert m.KEEP_STRATEGIA_QUOTA_RUMORE == 0.5
    assert m.KEEP_STRATEGIA_RUMORE_ATR == 1.0
    # la regola globale resta com'era (25 set): 8 verdetti, 60%, 0.25 / 0.75
    assert m.KEEP_PAPER_MIN_VERDETTI == 8
    assert m.proposta_keep(10, 6, 4) == 0.25 and m.proposta_keep(10, 4, 6) == 0.75
    assert m.proposta_keep(7, 7, 0) is None


def test_sotto_cinque_verdetti_nessuna_proposta():
    quattro = [_v("premature", 0.3)] * 4
    assert m.proposta_keep_strategia(quattro) is None
    assert m.proposta_keep_strategia(quattro + [_v("premature", 0.3)]) == 0.25
    assert m.proposta_keep_strategia([]) is None
    assert m.proposta_keep_strategia(None) is None
    # i «neutral» non contano nel campione
    assert m.proposta_keep_strategia(quattro + [_v("neutral")] * 3) is None


def test_prematuri_al_sessanta_per_cento_da_rumore_allargano_a_025():
    # 3 prematuri su 5 (60%), 2 dei 3 da rumore (>= meta') -> 0.25
    v = [_v("premature", 0.4), _v("premature", 0.9), _v("premature", 1.5),
         _v("protected", 2.0), _v("protected", 2.0)]
    assert m.proposta_keep_strategia(v) == 0.25
    # stessi prematuri ma da inversioni vere (knockout >= 1 ATR): allargare non
    # aiuterebbe -> nessuna proposta (e' la differenza dalla regola globale)
    v_inv = [_v("premature", 1.2), _v("premature", 1.5), _v("premature", 3.0),
             _v("protected", 2.0), _v("protected", 2.0)]
    assert m.proposta_keep_strategia(v_inv) is None
    assert m.proposta_keep(5, 3, 2, min_verdetti=5) == 0.25   # la globale non guarda il rumore
    # 1 su 3 da rumore: sotto la meta' -> None; knockout ignoto non e' rumore
    v_poco = [_v("premature", 0.4), _v("premature", None), _v("premature", 1.1),
              _v("protected", 2.0), _v("protected", 2.0)]
    assert m.proposta_keep_strategia(v_poco) is None
    # sotto il 60% di prematuri, anche se tutti da rumore -> None
    v_meta = [_v("premature", 0.2)] * 3 + [_v("protected", 2.0)] * 3
    assert m.proposta_keep_strategia(v_meta) is None


def test_protetti_al_sessanta_per_cento_stringono_a_075():
    v = [_v("protected", 2.0)] * 3 + [_v("premature", 0.2)] * 2
    assert m.proposta_keep_strategia(v) == 0.75
    v = [_v("protected", 2.0)] * 2 + [_v("premature", 0.2)] * 3
    assert m.proposta_keep_strategia(v) == 0.25          # 3/5 prematuri, tutti da rumore
    v = [_v("protected", 2.0)] * 5
    assert m.proposta_keep_strategia(v) == 0.75


def test_altro_timeframe_e_altre_uscite_non_contano():
    fuori = ([_v("premature", 0.2, tf="1h")] * 5
             + [_v("premature", 0.2, exit_reason="scale_out")] * 5
             + [_v("premature", 0.2, exit_reason="stop_loss")] * 5)
    assert m.conta_verdetti_strategia(fuori) == {"n": 0, "prematuri": 0,
                                                 "prematuri_rumore": 0, "protetti": 0}
    assert m.proposta_keep_strategia(fuori) is None
    dentro = fuori + [_v("premature", 0.2)] * 5
    assert m.conta_verdetti_strategia(dentro) == {"n": 5, "prematuri": 5,
                                                  "prematuri_rumore": 5, "protetti": 0}
    assert m.proposta_keep_strategia(dentro) == 0.25
    # trade malformati: ignorati, non esplodono
    assert m.proposta_keep_strategia(dentro + [None, "x", {"strategy": "gen_x"}]) == 0.25
    assert m.conta_verdetti_strategia([_v("premature", "boh")] * 5)["prematuri_rumore"] == 0


def test_soldi_sul_tavolo_e_una_misura_del_tragitto_verso_il_tp():
    v = [_v("premature", 0.2, miss=0.2), _v("premature", 0.2, miss=0.6),
         _v("protected", 2.0, miss=1.0), _v("premature", 0.2),               # senza misura
         _v("premature", 0.2, miss=0.1, tf="1h"),                            # altro timeframe
         _v("premature", 0.2, miss=0.1, exit_reason="scale_out")]            # altra uscita
    assert m.soldi_sul_tavolo(v) == {"n": 3, "miss_medio": 0.6}
    assert m.soldi_sul_tavolo([]) == {"n": 0, "miss_medio": None}
    assert m.soldi_sul_tavolo([_v("premature", 0.2, miss="x")]) == {"n": 0, "miss_medio": None}
    # e' una FRAZIONE del tragitto entry->TP, non un multiplo di R: la docstring lo dice
    assert "NON un multiplo di R" in inspect.getsource(m.soldi_sul_tavolo)
    # solo misurata: non entra nella regola
    assert "miss" not in inspect.getsource(m.proposta_keep_strategia)


# --------------------------------------------------------------------------- #
# 2. keep_per_strategia: un keep per id, dai trade gia' letti                  #
# --------------------------------------------------------------------------- #
def _trades_tre_strategie():
    a = [_v("premature", 0.3, gid="gen_a")] * 4 + [_v("protected", 2.0, gid="gen_a")]
    b = [_v("protected", 2.0, gid="gen_b")] * 5
    c = [_v("premature", 0.3, gid="gen_c")] * 3           # sotto campione
    # 2 prematuri, 2 protetti, 1 neutro: 50/50 sotto il 60% da entrambi i lati -> nessuna
    e = ([_v("premature", 0.3, gid="gen_e")] * 2 + [_v("protected", 2.0, gid="gen_e")] * 2
         + [_v("neutral", gid="gen_e")])
    return a + b + c + e


def test_keep_per_strategia_raggruppa_per_id_e_propone_solo_dove_scatta():
    out = d.keep_per_strategia(_trades_tre_strategie())
    assert out == {"gen_a": 0.25, "gen_b": 0.75}
    assert list(out) == ["gen_a", "gen_b"]                  # ordinato per id
    assert d.keep_per_strategia([]) == {}
    assert d.keep_per_strategia(None) == {}
    assert d.keep_per_strategia([None, {"strategy": None}, {"strategy": ""},
                                 {"strategy": 3, "exit_reason": "trailing_stop"}]) == {}
    # col campione alzato, gen_a e gen_b non bastano piu'
    assert d.keep_per_strategia(_trades_tre_strategie(), min_verdetti=6) == {}


def test_gli_esplorativi_contano_come_gli_altri():
    """Come in `keep_dal_paper` e `scale_per_strategia`: un lock che taglia un
    vincitore lo fa a qualunque size."""
    v = [dict(_v("premature", 0.3, gid="gen_a"), esplorativa=True)] * 5
    assert d.keep_per_strategia(v) == {"gen_a": 0.25}


# --------------------------------------------------------------------------- #
# 3. candidate_keeps: tre fonti, ordine e de-dup                               #
# --------------------------------------------------------------------------- #
def test_candidate_keeps_ordine_fissi_globale_per_strategia_e_de_dup():
    assert d.candidate_keeps() == LOCK_KEEP_CANDIDATES
    assert d.candidate_keeps(None, None) == LOCK_KEEP_CANDIDATES
    assert d.candidate_keeps(0.25, 0.75) == LOCK_KEEP_CANDIDATES + (0.25, 0.75)
    assert d.candidate_keeps(None, 0.75) == LOCK_KEEP_CANDIDATES + (0.75,)
    assert d.candidate_keeps(0.25, keep_strategia=0.25) == LOCK_KEEP_CANDIDATES + (0.25,)
    assert d.candidate_keeps(0.5, 0.65) == LOCK_KEEP_CANDIDATES        # gia' fra i fissi
    assert d.candidate_keeps("boh", "x") == LOCK_KEEP_CANDIDATES       # malformati: ignorati
    assert d.candidate_keeps(None, "0.75") == LOCK_KEEP_CANDIDATES + (0.75,)
    # il comportamento del 25 set (una fonte sola) resta identico
    assert d.candidate_keeps(0.25) == LOCK_KEEP_CANDIDATES + (0.25,)


# --------------------------------------------------------------------------- #
# 4. dal main ai worker                                                        #
# --------------------------------------------------------------------------- #
def test_disc_init_riceve_i_keep_per_strategia_in_coda_con_default():
    sig = inspect.signature(d._disc_init)
    assert list(sig.parameters)[-1] == "keep_strategie"
    assert sig.parameters["keep_strategie"].default is None, \
        "initargs e' posizionale: il nuovo argomento va in coda, con default"
    assert "keep_strategie=dict(keep_strategie or {})" in inspect.getsource(d._disc_init)
    main = inspect.getsource(d.main)
    assert "keep_strategie = keep_per_strategia(trades_paper or [])" in main
    assert "print(riga_paper_keep_strategie(keep_strategie, trades_paper or []))" in main
    assert ("bocciate_ok, keep_paper, scale_strategie, config_validate,\n"
            "                      keep_strategie)") in main
    assert "riga_cervello_keep(out, passed_keys, keep_paper, keep_strategie)" in main
    assert "conta_keep_giro(out, passed_keys, keep_paper, keep_strategie)" in main
    assert "keep_strategie=keep_strategie)" in main


def test_disc_init_mette_i_keep_nello_stato_del_worker(monkeypatch):
    prima = dict(d._W)
    try:
        monkeypatch.setattr(d, "WalkForwardOptimizer", lambda **k: SimpleNamespace(bt=None))
        monkeypatch.setattr(d, "load_candles", lambda *a, **k: [])
        args = SimpleNamespace(windows=3, interval="15m", start="2022-01-01", source="")
        d._disc_init(args, "2026-09-27", [], None, None, None, False, 0.25,
                     {"gen_a": (0.5, 1.0, 1.5)}, {}, {"gen_a": 0.25})
        assert d._W["keep_strategie"] == {"gen_a": 0.25}
        assert d._W["scale_strategie"] == {"gen_a": (0.5, 1.0, 1.5)}
        assert d._W["keep_paper"] == 0.25
        d._disc_init(args, "2026-09-27", [])            # senza: vuoto, come prima
        assert d._W["keep_strategie"] == {}
    finally:
        d._W.clear()
        d._W.update(prima)


def test_il_worker_passa_il_keep_della_strategia_a_valutazione_e_conferme():
    """Le conferme retroattive devono vedere gli STESSI candidati della
    valutazione (la regola gia' fissata per la scala per strategia)."""
    uno = inspect.getsource(d._disc_one)
    assert 'keep_strategia = (_W.get("keep_strategie") or {}).get(spec.get("id"))' in uno
    assert uno.count("keep_strategia=keep_strategia)") == 2, \
        "sia evaluate_spec sia conferme_retroattive devono ricevere il keep della strategia"
    assert uno.count('candidate_keeps(_W.get("keep_paper"),') == 2


# --------------------------------------------------------------------------- #
# 5. la riga [paper] del log                                                   #
# --------------------------------------------------------------------------- #
def test_la_riga_paper_dice_quante_strategie_un_esempio_e_il_tragitto_sul_tavolo():
    trades = _trades_tre_strategie()
    for t in trades:
        t["trailing_miss_to_tp"] = 0.5
    ks = d.keep_per_strategia(trades)
    riga = d.riga_paper_keep_strategie(ks, trades)
    assert riga.startswith("[paper] keep per strategia dal vissuto: 2 strategie con >= 5 "
                           "verdetti trailing (es. gen_a -> 0.25, prematuri da rumore 4/4)")
    assert riga.endswith("· tragitto lasciato sul tavolo medio 0.50 del tragitto entry->TP "
                         "su 18 trade")
    # con una proposta che stringe, l'esempio mostra i protetti
    riga_b = d.riga_paper_keep_strategie({"gen_b": 0.75}, trades)
    assert "(es. gen_b -> 0.75, protetti 5/5)" in riga_b
    # sempre, anche a zero
    assert d.riga_paper_keep_strategie({}, []) == (
        "[paper] keep per strategia dal vissuto: 0 strategie con >= 5 verdetti trailing "
        "· tragitto lasciato sul tavolo: nessun trade con la misura")


# --------------------------------------------------------------------------- #
# 6. la decisione si vede: conta_keep_giro, riga del cervello, doc del gate    #
# --------------------------------------------------------------------------- #
def test_conta_keep_giro_conta_le_coppie_che_hanno_scelto_il_keep_della_loro_strategia():
    out = {"A|gen_a": {"profit_lock_keep": 0.25, "strategy": "gen_a"},
           "B|gen_a": {"profit_lock_keep": 0.5, "strategy": "gen_a"},
           "C|gen_b": {"profit_lock_keep": 0.75},                       # id dalla chiave
           "D|gen_c": {"profit_lock_keep": 0.25},                       # senza proposta propria
           "E|gen_a": {"profit_lock_keep": None}}
    chiavi = list(out)
    ks = {"gen_a": 0.25, "gen_b": 0.75}
    k = d.conta_keep_giro(out, chiavi, keep_paper=0.25, keep_strategie=ks)
    assert k["dal_paper_strategia_n"] == 2
    assert k["dal_paper_n"] == 2 and k["non_scelto"] == 1
    assert d.conta_keep_giro(out, chiavi, 0.25)["dal_paper_strategia_n"] == 0
    assert d.conta_keep_giro(out, chiavi, 0.25, "boh")["dal_paper_strategia_n"] == 0
    riga = d.riga_cervello_keep(out, chiavi, keep_paper=0.25, keep_strategie=ks)
    assert riga == ("[cervello] keep del lock scelto dal gate: 0.25 x2 · 0.5 x1 · 0.75 x1"
                    " · non scelto x1 (dal paper 0.25 x2 · dal paper per strategia x2)")
    # senza proposte per strategia la riga e' quella del 25 set
    assert d.riga_cervello_keep(out, chiavi, keep_paper=0.25).endswith("(dal paper 0.25 x2)")
    assert d.riga_cervello_keep(out, chiavi, None, ks).endswith(
        "non scelto x1 (dal paper per strategia x2)")


def test_il_documento_del_gate_conta_le_strategie_con_proposta():
    from tests.test_doc_gate import _costruisci, _fixture_piccola
    doc = _costruisci(*_fixture_piccola(), keep_strategie={"gen_a": 0.25, "gen_b": 0.75})
    assert doc["giro"]["errore"] is None
    assert doc["giro"]["paper_propone"]["keep_strategie"] == 2
    doc0 = _costruisci(*_fixture_piccola())
    assert doc0["giro"]["paper_propone"]["keep_strategie"] == 0
    # lo schema (docs/controllo_schema.md) e i tipi TS portano i campi nuovi
    import os
    radice = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    with open(os.path.join(radice, "docs", "controllo_schema.md"), encoding="utf-8") as f:
        schema = f.read()
    assert "keep_strategie: int" in schema and "dal_paper_strategia_n: int" in schema
    ts = os.path.join(radice, "dashboard", "app", "lib", "gate.ts")
    if os.path.exists(ts):
        with open(ts, encoding="utf-8") as f:
            src = f.read()
        assert "keep_strategie?: number | null" in src
        assert "dal_paper_strategia_n?: number | null" in src


# --------------------------------------------------------------------------- #
# 7. trade_stats: il blocco per strategia                                      #
# --------------------------------------------------------------------------- #
def test_trade_stats_stampa_il_keep_per_strategia(capsys):
    trades = _trades_tre_strategie()
    for t in trades:
        if t["strategy"] == "gen_a":
            t["trailing_miss_to_tp"] = 0.4
    righe = trade_stats.keep_per_strategia_report(trades)
    per = {r["strategia"]: r for r in righe}
    assert [r["strategia"] for r in righe] == ["gen_a", "gen_b", "gen_e", "gen_c"]   # 5, 5, 4, 3 verdetti
    assert per["gen_a"] == {"strategia": "gen_a", "n": 5, "prematuri": 4, "prematuri_rumore": 4,
                            "protetti": 1, "proposta": 0.25, "miss_n": 5, "miss_medio": 0.4}
    assert per["gen_c"]["proposta"] is None and per["gen_c"]["miss_medio"] is None
    assert per["gen_e"]["proposta"] is None
    trade_stats.print_keep_per_strategia(trades)
    out = capsys.readouterr().out
    assert "KEEP PER STRATEGIA (proposta dal vissuto" in out
    riga_a = next(r for r in out.splitlines() if r.strip().startswith("gen_a"))
    assert "4 (rumore 4)" in riga_a and "0.25" in riga_a and "0.40" in riga_a
    riga_c = next(r for r in out.splitlines() if r.strip().startswith("gen_c"))
    assert " - " in riga_c and "n/d" in riga_c
    trade_stats.print_keep_per_strategia([])
    assert "nessuna strategia con verdetti trailing" in capsys.readouterr().out
    assert "print_keep_per_strategia(trades_letti)" in inspect.getsource(trade_stats.main)
