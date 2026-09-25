"""IL KEEP DEL PROFIT-LOCK: DAL PAPER AL GATE, E DAL GATE AL REGISTRO (25 set 2026).

Il paper scriveva da giorni un verdetto su ogni uscita trailing («premature»: il
lock ha tagliato un vincitore; «protected»: ha salvato dallo stop) e nessuna
decisione ne usciva: l'adattamento per strategia nel bot non e' mai scattato (8
verdetti PER STRATEGIA, in 10 giorni ne sono usciti 14 su 21 strategie, backlog
I3), e il gate comunque simulava 0,5 per tutte. Il proprietario ha chiesto che
«ogni dato raccolto arrivi al cervello e produca una decisione».

Il lato motore/bot (`lock_keep`, `locked_stop(keep=)`) e' in
tests/test_keep_per_coppia.py. Qui si difende il lato GATE:
  * `evaluate_spec` prova i keep candidati SOLO se la spec passa, sulla scala e sul
    BE gia' scelti, e ritorna il vincitore (a parita' vince il default 0,5); le
    metriche finali e l'holdout usano la configurazione VERA, keep compreso;
  * il metro della SCELTA e' pesato per recency (`_metrica_scelta`), il verdetto
    pass/fail no: `gate_verdict` resta sui numeri non pesati;
  * `keep_dal_paper` PROPONE un candidato dai verdetti trailing (tutte le coppie
    insieme, solo il timeframe del bot, fail-open) e `candidate_keeps` lo aggiunge
    ai tre fissi senza sostituirli;
  * la scelta viaggia dal worker a `last_params["profit_lock_keep"]` e sopravvive
    al codec compatto e all'alleggerimento del registro;
  * la decisione si VEDE: nella coda del log del giro e in `gate_progress`.
"""
import inspect
from datetime import datetime, timezone
from types import SimpleNamespace

import pandas as pd
import pytest

from backtesting.engine import GateVerdict, SimTrade, StrategyStats
from bot.config import settings
from bot.core.firebase_client import decode_pairs, encode_pairs
from bot.execution.exit_logic import LOCK_KEEP_CANDIDATES, lock_keep
from scripts import discover_strategies as d
from scripts import gate_progress as g
from scripts.optimize import slim_registry


# --------------------------------------------------------------------------- #
# i finti: un motore il cui esito dipende dal keep nei params                  #
# --------------------------------------------------------------------------- #
class _Candle:
    def __init__(self, ts):
        self.open_time = ts


def _trade(pnl: float, ts: float = 1_700_000_000.0) -> SimTrade:
    return SimTrade(strategy="gen_k", regime="sideways", direction="long",
                    entry_price=1.0, exit_price=1.0, pnl_pct=pnl, max_adverse_pct=0.0,
                    confidence=60, is_win=pnl > 0, pnl=pnl * 100, symbol="XUSDT",
                    regime_at_entry="sideways", mfe_r=1.0, bars_held=5, entry_ts=ts)


class _Bt:
    """Motore finto: due trade per finestra, e il pnl del vincente dipende dal
    keep letto in `g.params["profit_lock_keep"]` — e' esattamente il contratto
    che il motore vero onora (`lock_keep(strategy.params)`). Keep assente o
    0,5 -> il default (0,02)."""
    window = 0

    def __init__(self, per_keep=None):
        self.per_keep = dict(per_keep or {})
        self.chiamate: list[dict] = []          # i params visti a ogni passata

    def run_strategy(self, g, symbol, candles, frame=None, context_by_ts=None):
        p = dict(getattr(g, "params", {}) or {})
        self.chiamate.append(p)
        vinto = self.per_keep.get(p.get("profit_lock_keep"), 0.02)
        st = StrategyStats(strategy=g.name)
        st.trades.extend([_trade(vinto, 1_700_000_000.0), _trade(-0.01, 1_700_000_100.0)])
        return st


class _Opt:
    holdout_bars = 1

    def __init__(self, bt):
        self.bt = bt
        self.holdout_params = None

    def split_holdout(self, candles):
        return candles[:-1], len(candles) - 1

    def _windows(self, n):
        return [(0, 0, 0, n)]

    def _holdout_check(self, g, symbol, candles, frame, cut, context_by_ts=None):
        self.holdout_params = dict(getattr(g, "params", {}) or {})
        return {"ok": True}


def _valuta(monkeypatch, bt, passa=True, keep_candidates=None):
    monkeypatch.setattr(d, "gate_verdict",
                        lambda *a, **k: GateVerdict(ok=passa, failed=() if passa else ("pf",),
                                                    binding="" if passa else "pf"))
    monkeypatch.setattr(settings, "SCALE_OUT_ENABLED", True)
    monkeypatch.setattr(settings, "SCALE_OUT_R_MULTIPLES", (1.5, 3.0, 5.0))
    monkeypatch.setattr(settings, "SCALE_OUT_SL_TO_BREAKEVEN", True)
    monkeypatch.setattr(settings, "PROFIT_LOCK_KEEP", 0.5)
    candles = [_Candle(datetime(2026, 9, 25, tzinfo=timezone.utc))] * 4
    frame = pd.DataFrame({"close": [1.0] * 4})
    opt = _Opt(bt)
    # UNA sola scala candidata, uguale al default: cosi' il conto delle passate
    # isola il keep (scala: 1 passata; BE alternativo: 1; keep: una per candidato)
    r = d.evaluate_spec(opt, "XUSDT", candles, frame,
                        {"id": "gen_k", "features": [{"kind": "rsi_extreme"}]},
                        scale_candidates=[(1.5, 3.0, 5.0)], keep_candidates=keep_candidates)
    return r, opt


# --------------------------------------------------------------------------- #
# 1. evaluate_spec: il gate sceglie il keep                                    #
# --------------------------------------------------------------------------- #
def test_i_keep_si_provano_solo_se_la_spec_passa(monkeypatch):
    bt = _Bt({0.65: 0.03})
    r, opt = _valuta(monkeypatch, bt, passa=False)
    assert r["passed"] is False and r["profit_lock_keep"] is None
    assert len(bt.chiamate) == 1                       # la sola preselezione
    assert all("profit_lock_keep" not in p for p in bt.chiamate)
    assert opt.holdout_params is None


def test_vince_il_keep_col_metro_migliore_e_le_metriche_finali_sono_le_sue(monkeypatch):
    bt = _Bt({0.65: 0.03, 0.35: 0.01})
    r, opt = _valuta(monkeypatch, bt)
    assert r["passed"] is True
    assert r["profit_lock_keep"] == pytest.approx(0.65)
    # passate: preselezione, scala, BE alternativo, DUE keep (0,35 e 0,65: il
    # default 0,5 e' gia' misurato e non si rifa'), e la finale col vincitore
    assert len(bt.chiamate) == 6
    provati = sorted(p["profit_lock_keep"] for p in bt.chiamate if "profit_lock_keep" in p)
    assert provati == [0.35, 0.65, 0.65]
    # la passata finale porta TUTTA la configurazione che il bot operera'
    assert bt.chiamate[-1] == {"scale_r_mults": [1.5, 3.0, 5.0], "sl_to_breakeven": True,
                               "profit_lock_keep": 0.65}
    # (d) pf e pnl vengono dal vincitore: +0,03 -0,01, non dal default +0,02 -0,01
    assert r["pnl"] == pytest.approx(0.02) and r["pf"] == pytest.approx(3.0)
    assert r["scale_r_mults"] == [1.5, 3.0, 5.0] and r["sl_to_breakeven"] is True
    # (e) l'holdout ha ricevuto il keep nei params
    assert opt.holdout_params["profit_lock_keep"] == pytest.approx(0.65)
    assert opt.holdout_params["scale_r_mults"] == [1.5, 3.0, 5.0]
    # e le righe del selettore descrivono la configurazione finale
    assert [row["pnl_pct"] for row in r["oos_rows"]] == [0.03, -0.01]


def test_a_parita_vince_il_default_e_non_si_rifa_la_passata_finale(monkeypatch):
    bt = _Bt({})                                        # ogni keep rende uguale
    r, opt = _valuta(monkeypatch, bt)
    assert r["profit_lock_keep"] == pytest.approx(settings.PROFIT_LOCK_KEEP) == 0.5
    # preselezione, scala, BE, due keep: NIENTE passata finale, non e' cambiato nulla
    assert len(bt.chiamate) == 5
    assert r["pnl"] == pytest.approx(0.01)
    assert opt.holdout_params["profit_lock_keep"] == pytest.approx(0.5)


def test_il_candidato_del_paper_entra_in_gara_e_puo_vincere(monkeypatch):
    bt = _Bt({0.25: 0.05, 0.65: 0.03})
    r, _ = _valuta(monkeypatch, bt, keep_candidates=d.candidate_keeps(0.25))
    assert r["profit_lock_keep"] == pytest.approx(0.25)
    provati = {p["profit_lock_keep"] for p in bt.chiamate if "profit_lock_keep" in p}
    assert provati == {0.35, 0.65, 0.25}


def test_senza_candidati_espliciti_si_usano_i_tre_fissi():
    src = inspect.getsource(d.evaluate_spec)
    assert "keep_candidates or LOCK_KEEP_CANDIDATES" in src
    assert '"profit_lock_keep": best_keep' in src          # holdout e ritorno


# --------------------------------------------------------------------------- #
# 2. il metro della scelta e' pesato, il verdetto no                           #
# --------------------------------------------------------------------------- #
def test_la_metrica_di_scelta_pesa_il_recente(monkeypatch):
    vecchio = 1_600_000_000.0
    nuovo = vecchio + 365 * 86400
    # stessa SEQUENZA (drawdown identico) e stessa somma: cambia solo QUANDO e'
    # avvenuto il trade vincente
    a = [_trade(0.03, nuovo), _trade(-0.01, vecchio)]
    b = [_trade(0.03, vecchio), _trade(-0.01, nuovo)]
    monkeypatch.setattr(settings, "GATE_RECENCY_HALFLIFE_DAYS", 180.0)
    assert d._metrica_scelta(a) > d._metrica_scelta(b)
    # emivita 0 = pesi uniformi = il metro di prima, `pnl - dd`
    monkeypatch.setattr(settings, "GATE_RECENCY_HALFLIFE_DAYS", 0.0)
    assert d._metrica_scelta(a) == pytest.approx(d._metrica_scelta(b))
    assert d._metrica_scelta(a) == pytest.approx(0.02 - 0.01)
    assert d._metrica_scelta([]) == 0.0


def test_il_verdetto_resta_sui_numeri_non_pesati():
    """La nota in config lo dice: la recency pesa SOLO la selezione dei parametri.
    Se `gate_verdict` ricevesse il ritorno pesato, il rigore del gate cambierebbe
    di nascosto."""
    src = inspect.getsource(d.evaluate_spec)
    assert src.count("gate_verdict(") == 2
    assert "oos.win_rate(), oos.total_pnl_pct()," in src            # preselezione
    assert "pnl = oos.total_pnl_pct()" in src and "pf, oos.win_rate(), pnl," in src
    for riga in src.splitlines():
        if "gate_verdict(" in riga:
            assert "_metrica_scelta" not in riga and "weighted" not in riga
    assert "weighted_score_parts" not in src              # solo dentro _metrica_scelta
    assert src.count("_metrica_scelta(") == 3             # scala, BE, keep
    assert "weighted_score_parts(trades)" in inspect.getsource(d._metrica_scelta)


# --------------------------------------------------------------------------- #
# 3. il paper propone: keep_dal_paper e candidate_keeps                        #
# --------------------------------------------------------------------------- #
class _Fb:
    def __init__(self, trades=None, rotto=False):
        self.trades = list(trades or [])
        self.rotto = rotto

    def query_collection(self, *a, **k):
        if self.rotto:
            raise RuntimeError("firestore giu'")
        return self.trades


def _verdetti(prem: int, prot: int, tf=None, reason="trailing_stop") -> list[dict]:
    tf = settings.ORCHESTRATOR_TIMEFRAME if tf is None else tf
    return ([{"exit_reason": reason, "timeframe": tf, "trailing_verdict": "premature"}] * prem
            + [{"exit_reason": reason, "timeframe": tf, "trailing_verdict": "protected"}] * prot)


def test_sotto_il_campione_nessuna_proposta(capsys):
    assert d.keep_dal_paper(_Fb(_verdetti(5, 2))) is None
    assert "7 verdetti trailing (5 prematuri, 2 protetti) (ne servono 8): keep fissi" \
        in capsys.readouterr().out
    assert d.keep_dal_paper(_Fb([])) is None


def test_prematuri_dominanti_propongono_un_lock_piu_largo(capsys):
    assert d.keep_dal_paper(_Fb(_verdetti(6, 2))) == 0.25
    out = capsys.readouterr().out
    assert "8 verdetti trailing (6 prematuri, 2 protetti) -> keep candidato dal vissuto: 0.25" in out
    assert "si aggiunge ai 3 fissi, non li sostituisce: sceglie il gate" in out
    assert d.keep_dal_paper(_Fb(_verdetti(5, 3))) == 0.25     # 62,5% >= 60%


def test_protetti_dominanti_propongono_un_lock_piu_stretto():
    assert d.keep_dal_paper(_Fb(_verdetti(2, 6))) == 0.75


def test_verdetti_bilanciati_nessuna_proposta(capsys):
    assert d.keep_dal_paper(_Fb(_verdetti(4, 4))) is None
    assert "-> nessun candidato in piu' (sotto il 60%)" in capsys.readouterr().out
    assert d.keep_dal_paper(_Fb(_verdetti(4, 3))) is None     # 57%: sotto


def test_contano_solo_i_trailing_del_timeframe_del_bot(capsys):
    trades = (_verdetti(6, 2)
              + _verdetti(10, 0, tf="1h")                     # altro timeframe
              + _verdetti(10, 0, reason="take_profit")        # non e' un'uscita trailing
              + [{"exit_reason": "trailing_stop", "timeframe": settings.ORCHESTRATOR_TIMEFRAME,
                  "trailing_verdict": "neutral"}] * 10        # ne' prematuro ne' protetto
              + ["spazzatura", None])                         # documenti storti
    assert d.keep_dal_paper(_Fb(trades)) == 0.25
    assert "8 verdetti trailing (6 prematuri, 2 protetti)" in capsys.readouterr().out


def test_un_guasto_di_firebase_lascia_i_keep_fissi(capsys):
    assert d.keep_dal_paper(_Fb(rotto=True)) is None
    assert "verdetti trailing non disponibili" in capsys.readouterr().out


def test_i_candidati_del_paper_si_aggiungono_e_non_sostituiscono():
    assert d.candidate_keeps(None) == LOCK_KEEP_CANDIDATES
    assert d.candidate_keeps(0.5) == LOCK_KEEP_CANDIDATES        # gia' fra i fissi
    assert d.candidate_keeps("x") == LOCK_KEEP_CANDIDATES        # un valore storto non entra
    fuori = d.candidate_keeps(0.25)
    assert fuori[:len(LOCK_KEEP_CANDIDATES)] == LOCK_KEEP_CANDIDATES   # ordine e presenza
    assert fuori[-1] == 0.25 and len(fuori) == len(LOCK_KEEP_CANDIDATES) + 1
    assert d.candidate_keeps(0.75)[-1] == 0.75
    # i valori proposti stanno nel range che `lock_keep` accetta
    assert lock_keep({"profit_lock_keep": 0.25}) == 0.25
    assert lock_keep({"profit_lock_keep": 0.75}) == 0.75


# --------------------------------------------------------------------------- #
# 4. dal worker al registro, e il registro lo conserva                         #
# --------------------------------------------------------------------------- #
def test_la_proposta_arriva_ai_worker_e_la_scelta_torna_al_main():
    sig = inspect.signature(d._disc_init)
    ultimo = list(sig.parameters)[-1]
    assert ultimo == "keep_paper" and sig.parameters[ultimo].default is None, \
        "initargs e' posizionale: il nuovo argomento va in coda, con default"
    assert "keep_paper=keep_paper" in inspect.getsource(d._disc_init)
    uno = inspect.getsource(d._disc_one)
    assert uno.count('keep_candidates=candidate_keeps(_W.get("keep_paper"))') == 2, \
        "sia la valutazione sia le conferme retroattive devono ricevere i candidati"
    assert '"profit_lock_keep": r.get("profit_lock_keep")' in uno
    assert "keep_candidates=keep_candidates" in inspect.getsource(d.conferme_retroattive)
    main = inspect.getsource(d.main)
    assert "keep_paper = keep_dal_paper(fb)" in main
    assert "bocciate_ok, keep_paper)" in main


def test_disc_init_mette_il_keep_del_paper_nello_stato_del_worker(monkeypatch):
    prima = dict(d._W)
    try:
        monkeypatch.setattr(d, "WalkForwardOptimizer", lambda **k: SimpleNamespace(bt=None))
        monkeypatch.setattr(d, "load_candles", lambda *a, **k: [])
        args = SimpleNamespace(windows=3, interval="15m", start="2022-01-01", source="")
        d._disc_init(args, "2026-09-25", [], None, None, None, False, 0.25)
        assert d._W["keep_paper"] == 0.25
        d._disc_init(args, "2026-09-25", [])            # senza: None, come prima
        assert d._W["keep_paper"] is None
    finally:
        d._W.clear()
        d._W.update(prima)


class _FB:
    def __init__(self):
        self.docs = {}

    def get_doc(self, c, dname):
        return self.docs.get((c, dname), {})

    def set_doc(self, c, dname, data):
        self.docs[(c, dname)] = data


def _entry(**extra) -> dict:
    e = {"symbol": "A", "strategy": "gen_k", "params": {}, "oos_pf": 1.5,
         "oos_pnl_pct": 0.3, "oos_trades": 40, "oos_win_rate": 0.5, "passed": True,
         "holdout": {"ok": True}, "data_end": 1e9, "scale_r_mults": [1.0, 2.0, 3.0],
         "sl_to_breakeven": False}
    e.update(extra)
    return e


def _registro_con_una_validata() -> _FB:
    fb = _FB()
    fb.docs[("strategy_registry", "validated")] = {"pairs": encode_pairs(
        {"A|gen_k": {"pass_count": 3, "generated": True, "symbol": "A",
                     "strategy": "gen_k", "last_seen_at": 1e9, "window_start": 1e9}})}
    return fb


def test_il_keep_scelto_finisce_in_last_params_e_sopravvive_a_codec_e_alleggerimento():
    fb = _registro_con_una_validata()
    d.merge_into_registry(fb, {"A|gen_k": _entry(profit_lock_keep=0.65)}, ["A|gen_k"],
                          evaluated_symbols={"A"})
    # il merge scrive gia' nel formato compatto (slim_registry -> encode_registry)
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    lp = pairs["A|gen_k"]["last_params"]
    assert lp["profit_lock_keep"] == 0.65
    assert lp["scale_r_mults"] == [1.0, 2.0, 3.0] and lp["sl_to_breakeven"] is False
    # ed e' quello che il bot legge
    assert lock_keep(lp) == pytest.approx(0.65)
    # andata e ritorno esplicita nel codec
    assert decode_pairs(encode_pairs(pairs))["A|gen_k"]["last_params"]["profit_lock_keep"] == 0.65
    # alleggerimento normale (coppia non validata) e d'emergenza (tetto a 1 byte):
    # `last_params` e' nel nucleo e viaggia intero
    for tetto in (10**9, 1):
        r = decode_pairs(slim_registry(pairs, [], max_bytes=tetto))["A|gen_k"]
        assert r["last_params"]["profit_lock_keep"] == 0.65, f"perso col tetto {tetto}"


def test_senza_scelta_la_chiave_non_si_scrive():
    """Una coppia valutata con lo scale-out spento (nessuna scala, nessun keep)
    non deve trovarsi un `profit_lock_keep: None` nel registro: assente vuol dire
    «col keep di prima», e `lock_keep` lo legge cosi'."""
    fb = _registro_con_una_validata()
    d.merge_into_registry(fb, {"A|gen_k": _entry(profit_lock_keep=None)}, ["A|gen_k"],
                          evaluated_symbols={"A"})
    pairs = decode_pairs(fb.docs[("strategy_registry", "validated")]["pairs"])
    assert "profit_lock_keep" not in pairs["A|gen_k"]["last_params"]


# --------------------------------------------------------------------------- #
# 5. la decisione si vede                                                      #
# --------------------------------------------------------------------------- #
def test_la_riga_del_cervello_conta_i_keep_delle_passate():
    out = {"A|x": {"profit_lock_keep": 0.35}, "B|x": {"profit_lock_keep": 0.5},
           "C|x": {"profit_lock_keep": 0.5}, "D|x": {"profit_lock_keep": None},
           "E|x": {"profit_lock_keep": 0.25}}
    riga = d.riga_cervello_keep(out, ["A|x", "B|x", "C|x", "D|x", "E|x"], keep_paper=0.25)
    assert riga == ("[cervello] keep del lock scelto dal gate: 0.25 x1 · 0.35 x1 · 0.5 x2"
                    " · non scelto x1 (dal paper 0.25 x1)")
    assert d.riga_cervello_keep({}, [], None) == \
        "[cervello] keep del lock scelto dal gate: nessuna coppia passata"
    assert d.riga_cervello_keep({}, [], 0.75).endswith("nessuna coppia passata (dal paper 0.75 x0)")
    # in coda al log, prima di «GIRO FINITO», come le altre righe del cervello
    src = inspect.getsource(d.main)
    assert src.rindex("print(riga_cervello_keep(out, passed_keys, keep_paper))") \
        < src.index("GIRO FINITO in")


def test_gate_progress_conta_il_keep_delle_validate():
    pairs = {"A|x": {"last_params": {"profit_lock_keep": 0.35}},
             "B|x": {"last_params": {"profit_lock_keep": 0.5}},
             "C|x": {"last_params": {"profit_lock_keep": "0.5"}},     # passato da JSON
             "D|x": {"last_params": {}},                              # validata prima del parametro
             "E|x": {},                                               # senza params affatto
             "F|x": {"last_params": {"profit_lock_keep": 0.65}},
             "Z|x": {"last_params": {"profit_lock_keep": 0.65}}}      # NON validata: non conta
    riga = g.riga_keep_validate(pairs, ["A|x", "B|x", "C|x", "D|x", "E|x", "F|x"])
    assert riga == ("  KEEP DEL LOCK (scelto dal gate per coppia): 0.35 x1 · 0.5 x2 · 0.65 x1"
                    " · non ancora rivalutate x2")
    assert g.riga_keep_validate({}, []).endswith("nessuna coppia validata")
    assert g.riga_keep_validate(pairs, ["E|x"]).endswith("non ancora rivalutate x1")
    assert "print(riga_keep_validate(pairs, validated))" in inspect.getsource(g.main)
