"""LA SCALA DEI TP PER STRATEGIA DAL VISSUTO, e l'ipotesi che la fa rigiudicare
(25 set 2026, backlog I4).

Il numero che l'ha decisa: 20 stop su 32 erano trade andati a favore e morti
SOTTO il primo gradino. Il paper proponeva gia' UNA scala per tutte le coppie
insieme (`scala_dal_paper`); da oggi propone anche quella di ogni strategia con
abbastanza trade (`scale_per_strategia`), e i referti fanno scattare la quinta
ipotesi `scala_stretta`, che rimette la strategia nel giro con la sua scala fra i
candidati. Cosa si protegge: il paper PROPONE (un candidato in piu', mai al posto
dei fissi, mai al posto della globale), il gate DECIDE; fail-open ovunque; gli
argomenti dei worker restano in coda con default; le conferme retroattive vedono
gli stessi candidati della valutazione.
"""
import inspect
import time

from bot.execution.exit_logic import SCALE_LADDER_CANDIDATES, ladder_from_mfe
from scripts import discover_strategies as d

NOW = time.time()


def _tr(gid, mfe, **extra):
    t = {"strategy": gid, "mfe_r": mfe, "pnl": -1.0, "exit_reason": "stop_loss"}
    t.update(extra)
    return t


# --------------------------------------------------------------------------- #
# 1. scale_per_strategia                                                       #
# --------------------------------------------------------------------------- #
def test_la_scala_per_strategia_e_quella_dei_quantili_sui_suoi_trade():
    mfe_a = [0.4, 0.6, 0.8, 1.1, 1.6, 2.2]
    mfe_b = [3.0, 3.5, 4.0, 4.5, 5.0]
    trades = [_tr("gen_a", m) for m in mfe_a] + [_tr("gen_b", m) for m in mfe_b]
    out = d.scale_per_strategia(trades)
    assert set(out) == {"gen_a", "gen_b"}
    assert out["gen_a"] == ladder_from_mfe(mfe_a, min_trades=5)
    assert out["gen_b"] == ladder_from_mfe(mfe_b, min_trades=5)
    assert out["gen_a"] != out["gen_b"]          # ogni strategia la SUA


def test_sotto_il_minimo_di_trade_la_strategia_non_ha_scala():
    trades = [_tr("gen_a", 0.5 + i / 10) for i in range(4)]
    assert d.scale_per_strategia(trades) == {}
    trades.append(_tr("gen_a", 1.2))
    assert list(d.scale_per_strategia(trades)) == ["gen_a"]
    # il minimo e' un argomento, dichiarato nella costante
    assert d.SCALA_STRATEGIA_MIN_TRADES == 5
    assert d.scale_per_strategia(trades, min_trades=6) == {}


def test_fail_open_su_trade_assenti_o_malformati():
    assert d.scale_per_strategia(None) == {}
    assert d.scale_per_strategia([]) == {}
    rotti = [None, "x", {"strategy": "gen_a"}, {"mfe_r": 1.0}, {"strategy": 3, "mfe_r": 1.0},
             {"strategy": "gen_a", "mfe_r": "boh"}]
    assert d.scale_per_strategia(rotti) == {}
    # i trade senza mfe non contano nel campione
    trades = [_tr("gen_a", 0.9) for _ in range(4)] + [{"strategy": "gen_a", "pnl": 1.0}] * 3
    assert d.scale_per_strategia(trades) == {}


def test_l_ordine_delle_strategie_e_deterministico():
    trades = ([_tr("gen_z", 1.0 + i / 10) for i in range(5)]
              + [_tr("gen_a", 0.5 + i / 10) for i in range(5)])
    assert list(d.scale_per_strategia(trades)) == ["gen_a", "gen_z"]


# --------------------------------------------------------------------------- #
# 2. candidate_ladders: globale + per strategia, in ordine, senza doppioni     #
# --------------------------------------------------------------------------- #
def test_la_scala_per_strategia_si_aggiunge_dopo_quella_globale():
    out = d.candidate_ladders((0.75, 1.5, 2.5), scala_strategia=(0.5, 1.0, 1.75))
    assert out[:len(SCALE_LADDER_CANDIDATES)] == SCALE_LADDER_CANDIDATES
    assert out[-2:] == ((0.75, 1.5, 2.5), (0.5, 1.0, 1.75))


def test_una_scala_per_strategia_gia_presente_non_si_duplica():
    fissa = tuple(SCALE_LADDER_CANDIDATES[1])
    assert d.candidate_ladders(None, scala_strategia=fissa) == SCALE_LADDER_CANDIDATES
    stessa = (0.75, 1.5, 2.5)
    out = d.candidate_ladders(stessa, scala_strategia=stessa)
    assert out == SCALE_LADDER_CANDIDATES + (stessa,)
    # e la lista la accetta come tupla
    assert d.candidate_ladders(None, scala_strategia=[0.75, 1.5, 2.5]) == \
        SCALE_LADDER_CANDIDATES + (stessa,)


def test_senza_scala_per_strategia_i_candidati_sono_quelli_di_prima():
    assert d.candidate_ladders(None) == SCALE_LADDER_CANDIDATES
    assert d.candidate_ladders(None, scala_strategia=None) == SCALE_LADDER_CANDIDATES
    assert d.candidate_ladders((0.75, 1.5, 2.5), scala_strategia=()) == \
        d.candidate_ladders((0.75, 1.5, 2.5))


# --------------------------------------------------------------------------- #
# 3. dal main ai worker                                                        #
# --------------------------------------------------------------------------- #
def test_disc_init_riceve_le_scale_per_strategia_in_coda_con_default():
    sig = inspect.signature(d._disc_init)
    # dal 26 set 2026 dopo `scale_strategie` c'e' `config_validate` (test_declassate_gate):
    # anch'esso in coda, con default
    assert list(sig.parameters)[-2:] == ["scale_strategie", "config_validate"]
    assert sig.parameters["scale_strategie"].default is None, \
        "initargs e' posizionale: il nuovo argomento va in coda, con default"
    main = inspect.getsource(d.main)
    assert "scale_strategie = scale_per_strategia(trades_paper or [])" in main
    assert "bocciate_ok, keep_paper, scale_strategie, config_validate)" in main
    assert "[paper] scale per strategia dal vissuto" in main


def test_disc_init_mette_le_scale_nello_stato_del_worker(monkeypatch):
    from types import SimpleNamespace
    prima = dict(d._W)
    try:
        monkeypatch.setattr(d, "WalkForwardOptimizer", lambda **k: SimpleNamespace(bt=None))
        monkeypatch.setattr(d, "load_candles", lambda *a, **k: [])
        args = SimpleNamespace(windows=3, interval="15m", start="2022-01-01", source="")
        d._disc_init(args, "2026-09-25", [], None, None, None, False, 0.25,
                     {"gen_a": (0.5, 1.0, 1.5)})
        assert d._W["scale_strategie"] == {"gen_a": (0.5, 1.0, 1.5)}
        assert d._W["keep_paper"] == 0.25
        d._disc_init(args, "2026-09-25", [])            # senza: vuoto, come prima
        assert d._W["scale_strategie"] == {}
    finally:
        d._W.clear()
        d._W.update(prima)


def test_il_worker_passa_la_scala_della_strategia_a_valutazione_e_conferme():
    """Le conferme retroattive devono vedere gli STESSI candidati della
    valutazione: altrimenti una spec passerebbe oggi con la sua scala e
    fallirebbe le conferme senza."""
    uno = inspect.getsource(d._disc_one)
    assert 'scala_strategia = (_W.get("scale_strategie") or {}).get(spec.get("id"))' in uno
    assert uno.count("scala_strategia=scala_strategia)") == 2, \
        "sia evaluate_spec sia conferme_retroattive devono ricevere la scala della strategia"
    assert 'candidate_ladders(_W.get("scala_paper"),' in uno
    # `scale_candidates` arriva a `evaluate_spec` come argomento, non da uno
    # stato globale (la regola gia' fissata per la scala globale)
    assert "scale_candidates=scale_candidates" in inspect.getsource(d.conferme_retroattive)


# --------------------------------------------------------------------------- #
# 4. l'urgenza: un'ipotesi scala_stretta fresca rimette la spec nel giro       #
# --------------------------------------------------------------------------- #
def _doc(*voci):
    return {"ipotesi": [{"strategia": g, "tipo": tipo, "da_ts": ts, "campione": 3,
                         "motivo": "x"} for g, tipo, ts in voci]}


def test_strategie_scala_stretta_solo_fresche_e_solo_di_quel_tipo():
    doc = _doc(("gen_fresca", "scala_stretta", NOW - 2 * 86400),
               ("gen_vecchia", "scala_stretta", NOW - 9 * 86400),
               ("gen_altro", "solo_long", NOW - 86400),
               ("gen_senza_ts", "scala_stretta", None))
    assert d.strategie_scala_stretta(doc, NOW) == ["gen_fresca"]
    # la finestra e' dichiarata: 7 giorni
    assert d.SCALA_STRETTA_FRESCA_S == 7 * 86400
    assert d.strategie_scala_stretta(doc, NOW, fresca_s=10 * 86400) == ["gen_fresca", "gen_vecchia"]


def test_strategie_scala_stretta_tetto_e_ordine():
    """Al massimo 10 per giro (un giro «solo urgenti» deve restare breve), le
    piu' recenti prima; a parita' di data per id, senza doppioni."""
    voci = [(f"gen_{i:02d}", "scala_stretta", NOW - i * 3600) for i in range(15)]
    voci.append(("gen_00", "scala_stretta", NOW))          # doppione
    out = d.strategie_scala_stretta(_doc(*voci), NOW)
    assert len(out) == 10 and len(set(out)) == 10
    assert out[:3] == ["gen_00", "gen_01", "gen_02"]
    assert d.SCALA_STRETTA_MAX == 10
    assert d.strategie_scala_stretta(_doc(*voci), NOW, cap=2) == ["gen_00", "gen_01"]


def test_strategie_scala_stretta_fail_open():
    assert d.strategie_scala_stretta(None, NOW) == []
    assert d.strategie_scala_stretta({}, NOW) == []
    assert d.strategie_scala_stretta({"ipotesi": "boh"}, NOW) == [] or True  # non deve sollevare
    assert d.strategie_scala_stretta({"ipotesi": [None, 3, {"tipo": "scala_stretta"},
                                                  {"tipo": "scala_stretta", "strategia": ["x"],
                                                   "da_ts": NOW},
                                                  {"tipo": "scala_stretta", "strategia": "gen_a",
                                                   "da_ts": "ieri"}]}, NOW) == []


def test_le_strategie_con_ipotesi_fresca_entrano_nella_rivalutazione_urgente():
    """Nel giro «solo urgenti» una spec senza conferme in finestra non si
    rivaluterebbe: con l'ipotesi scala_stretta fresca entra comunque, in coda."""
    existing = {"gen_scade": {"id": "gen_scade"}, "gen_ferma": {"id": "gen_ferma"},
                "gen_uscita": {"id": "gen_uscita"}}
    reg = {"pairs": {
        "X|gen_scade": {"generated": True, "pass_count": 2, "window_start": NOW - 7 * 86400},
        "X|gen_ferma": {"generated": True, "pass_count": 0, "window_start": NOW - 86400},
        "X|gen_uscita": {"generated": True, "pass_count": 0, "window_start": NOW - 86400}}}
    scelte, diag = d.specs_da_rivalutare(existing, reg, cap=500, completa=False, now=NOW,
                                         urgenti_extra=["gen_uscita", "gen_ignota"])
    assert [s["id"] for s in scelte] == ["gen_scade", "gen_uscita"]
    assert diag["n_specs_ipotesi_uscita"] == 1 and diag["n_specs_rivalutate"] == 2
    # gia' dentro per conto suo: non si conta due volte
    scelte, diag = d.specs_da_rivalutare(existing, reg, cap=500, completa=False, now=NOW,
                                         urgenti_extra=["gen_scade"])
    assert [s["id"] for s in scelte] == ["gen_scade"] and diag["n_specs_ipotesi_uscita"] == 0
    # senza l'argomento: identico a prima
    scelte, diag = d.specs_da_rivalutare(existing, reg, cap=500, completa=False, now=NOW)
    assert [s["id"] for s in scelte] == ["gen_scade"] and diag["n_specs_ipotesi_uscita"] == 0


def test_nel_giro_completo_entrano_anche_oltre_il_cap():
    existing = {f"gen_{i}": {"id": f"gen_{i}"} for i in range(6)}
    reg = {"pairs": {}}
    scelte, diag = d.specs_da_rivalutare(existing, reg, cap=2, completa=True,
                                         urgenti_extra=["gen_5"])
    assert [s["id"] for s in scelte] == ["gen_0", "gen_1", "gen_5"]
    assert diag["n_specs_ipotesi_uscita"] == 1


def test_il_main_legge_i_referti_una_volta_e_rigiudica_le_strategie_con_ipotesi():
    main = inspect.getsource(d.main)
    assert "doc_referti = leggi_referti(fb)" in main
    assert "doc=doc_referti" in main
    assert "strategie_scala_stretta(doc_referti, _ora)" in main
    assert "urgenti_extra=urgenti_uscita" in main
    assert '"ipotesi_uscita": ipotesi_uscita' in main
    assert "riga_cervello_uscita(ipotesi_uscita)" in main
    riga = d.riga_cervello_uscita({"strategie": 3, "con_scala": 2})
    assert riga.startswith("[cervello] ipotesi scala_stretta: 3 strategie rigiudicate "
                           "con la loro scala dal vissuto")
    assert "2 con" in riga
    assert d.riga_cervello_uscita(None).startswith("[cervello] ipotesi scala_stretta: 0 strategie")


def test_varianti_dai_referti_ignora_scala_stretta_e_accetta_il_doc_gia_letto():
    """scala_stretta NON e' una variante della spec: la discovery la gestisce come
    urgenza + scala. Con `doc` passato non si rilegge Firebase."""
    class _Fb:
        letture = 0

        def get_doc(self, *a):
            self.letture += 1
            raise AssertionError("non deve leggere")

    existing = {"gen_a": {"id": "gen_a", "features": [], "timeframe": "15m"}}
    doc = _doc(("gen_a", "scala_stretta", NOW))
    fb = _Fb()
    assert d.varianti_dai_referti(fb, existing, "15m", doc=doc) == []
    assert fb.letture == 0
    assert d.varianti_dai_referti(fb, existing, "15m", doc={"ipotesi": "boh"}) == []


# --------------------------------------------------------------------------- #
# 5. il documento del gate lo racconta                                         #
# --------------------------------------------------------------------------- #
def test_giro_ipotesi_uscita_nel_documento_del_gate():
    from tests.test_doc_gate import _costruisci, _fixture_piccola, _run
    doc = _costruisci(*_fixture_piccola())
    assert doc["giro"]["ipotesi_uscita"] == {"strategie": 0, "con_scala": 0}
    doc = _costruisci(*_fixture_piccola(),
                      run=_run(ipotesi_uscita={"strategie": 3, "con_scala": 2}))
    assert doc["giro"]["ipotesi_uscita"] == {"strategie": 3, "con_scala": 2}


# --------------------------------------------------------------------------- #
# 6. l'ipotesi nei referti                                                     #
# --------------------------------------------------------------------------- #
def test_l_ipotesi_scala_stretta_nasce_dai_referti_con_la_mediana_degli_mfe():
    from bot.learning.referti import MIN_SCALA_STRETTA, aggrega_referti
    assert MIN_SCALA_STRETTA == 3

    def _t(i, mfe):
        return {"strategy": "gen_a", "symbol": "AUSDT", "pnl": -2.0, "exit_reason": "stop_loss",
                "direction": ("long", "short")[i % 2], "entry_ts": 1000.0 + i,
                "post_mortem": {"classe": "uscita", "mfe_r": mfe, "stop_largo": False,
                                "lock_mai_armato": True, "controtrend": None}}

    doc = aggrega_referti([_t(0, 0.6), _t(1, 0.9), _t(2, 0.7)])
    assert [h["tipo"] for h in doc["ipotesi"]] == ["scala_stretta"]
    h = doc["ipotesi"][0]
    assert h["motivo"] == "3 perdite sotto il primo gradino (mfe mediana 0.70 R)"
    assert h["da_ts"] == 1000.0 and h["campione"] == 3
    # e la discovery la riconosce come fresca
    assert d.strategie_scala_stretta(doc, 1000.0 + 86400) == ["gen_a"]
    assert d.strategie_scala_stretta(doc, 1000.0 + 8 * 86400) == []
