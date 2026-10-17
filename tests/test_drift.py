"""RILEVATORE DI DERIVA — l'anello che chiude paper -> gate.

Il gate promette (PF validato, TP raggiungibili) sulla storia; il paper vive il
presente. Quando il vissuto contraddice la promessa: freno immediato in produzione
e l'evidenza pesa alla passata successiva del gate come FALLIMENTO.

Il paper FALSIFICA, non ottimizza: tararci i parametri lo consumerebbe come
training set — lo stesso difetto rimosso dal gate con l'holdout.
"""
import pytest

from bot.config import settings
from bot.learning.drift import (DRIFT, OK, WATCH, compute_drift, drifted_keys,
                                motivi_freno, serie_perdite, weight_factor)


def _t(sym="AUSDT", strat="s1", pnl=-5.0, mfe=0.4, reason="stop_loss", ts=None):
    t = {"symbol": sym, "strategy": strat, "pnl": pnl, "mfe_r": mfe,
         "exit_reason": reason}
    if ts is not None:
        t["exit_ts"] = ts
    return t


def _pairs(pf=1.5, mults=(1.5, 3.0, 5.0)):
    return {"AUSDT|s1": {"last_pf": pf, "last_params": {"scale_r_mults": list(mults)}}}


# ---- rilevamento ---------------------------------------------------------- #
def test_drift_when_live_pf_betrays_the_promise():
    """Il gate prometteva PF 1.5, il vissuto e' 0: deriva conclamata."""
    d = compute_drift([_t() for _ in range(10)], _pairs())
    rec = d["pairs"]["AUSDT|s1"]
    assert rec["verdict"] == DRIFT
    assert "PF" in rec["reason"] and rec["trades"] == 10


def test_drift_when_tp_ladder_is_unreachable():
    """Segnale INDIPENDENTE dal PF: anche con trade in utile, se il prezzo non
    arriva mai al primo gradino la scala e' un desiderio. Basta UN numero per
    trade (mfe_r), non serve attendere esiti completi."""
    trades = [_t(pnl=+1.0, mfe=0.5) for _ in range(10)]      # in utile ma mfe 0.5R
    d = compute_drift(trades, _pairs(pf=1.2, mults=(3.0, 6.0, 9.0)))
    rec = d["pairs"]["AUSDT|s1"]
    assert rec["verdict"] == DRIFT
    assert "mfe" in rec["reason"]
    assert rec["first_rung_r"] == 3.0


def test_healthy_pair_is_ok():
    trades = [_t(pnl=+8.0, mfe=2.5) for _ in range(10)]
    d = compute_drift(trades, _pairs())
    assert d["pairs"]["AUSDT|s1"]["verdict"] == OK
    assert d["pairs"]["AUSDT|s1"]["reason"] == ""


def test_small_sample_is_watch_not_drift():
    """Con pochi trade il sospetto si VEDE ma non si AGISCE: frenare su 2 trade
    sarebbe reagire al rumore."""
    d = compute_drift([_t() for _ in range(2)], _pairs())
    assert d["pairs"]["AUSDT|s1"]["verdict"] == WATCH
    assert weight_factor(d, "AUSDT", "s1") == 1.0        # nessun freno
    assert drifted_keys(d) == []                         # nulla arriva al gate


def test_pairs_without_a_gate_promise_are_skipped():
    """Senza un atteso non c'e' niente da falsificare."""
    d = compute_drift([_t() for _ in range(10)], {})
    assert d["pairs"] == {}


def test_external_exits_are_excluded():
    """Chiusure manuali / kill switch non dicono nulla sull'edge della strategia."""
    trades = [_t(reason="manual") for _ in range(10)]
    d = compute_drift(trades, _pairs())
    assert "AUSDT|s1" not in d["pairs"]


def test_three_granularities_have_different_sample_needs():
    """Per-coppia i trade arrivano lentissimi, per strategia molto prima: la stessa
    evidenza puo' essere 'watch' sulla coppia e gia' 'drift' aggregata."""
    trades = ([_t(sym="AUSDT") for _ in range(5)] + [_t(sym="BUSDT") for _ in range(5)]
              + [_t(sym="CUSDT") for _ in range(10)])
    pairs = {f"{s}USDT|s1": {"last_pf": 1.5} for s in ("A", "B", "C")}
    d = compute_drift(trades, pairs)
    assert d["pairs"]["AUSDT|s1"]["verdict"] == WATCH        # 5 < 8
    assert d["strategies"]["s1"]["verdict"] == DRIFT         # 20 aggregati
    assert d["global"]["trades"] == 20


# ---- freno immediato in produzione ---------------------------------------- #
def test_weight_factor_brakes_but_never_kills(monkeypatch):
    """Frena, non spegne: rimuovere spetta al gate, che decide sulla storia."""
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    d = compute_drift([_t() for _ in range(10)], _pairs())
    f = weight_factor(d, "AUSDT", "s1")
    assert settings.DRIFT_WEIGHT_FLOOR <= f < 1.0


def test_pair_and_strategy_drift_compound_down_to_the_floor(monkeypatch):
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    trades = [_t() for _ in range(25)]                # coppia E strategia in deriva
    d = compute_drift(trades, _pairs())
    assert d["pairs"]["AUSDT|s1"]["verdict"] == DRIFT
    assert d["strategies"]["s1"]["verdict"] == DRIFT
    assert weight_factor(d, "AUSDT", "s1") == pytest.approx(settings.DRIFT_WEIGHT_FLOOR)


def test_global_drift_alone_brakes_every_pair(monkeypatch):
    """Il livello GLOBALE deve frenare da solo.

    E' la granularita' che matura per prima: i trade si spargono su decine di
    coppie, quindi nessuna raggiunge DRIFT_MIN_TRADES_PAIR mentre l'aggregato ha
    gia' campione abbondante. Finche' weight_factor leggeva solo pairs/strategies,
    il rilevatore pubblicava 'drift' globale e il bot continuava a size piena.
    Qui: coppie e strategie restano sotto soglia (una coppia diversa per trade),
    solo il globale supera -> il freno deve comunque scattare.
    """
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    monkeypatch.setattr(settings, "DRIFT_MIN_TRADES_GLOBAL", 10)
    trades, pairs = [], {}
    for i in range(30):        # 30 coppie/strategie diverse, 1 solo trade ciascuna
        sym, strat = f"C{i}USDT", f"gen_{i}"
        trades.append(_t(sym=sym, strat=strat))
        pairs[f"{sym}|{strat}"] = {"last_pf": 1.6}
    d = compute_drift(trades, pairs)
    assert all(v["verdict"] != DRIFT for v in d["pairs"].values()), "nessuna coppia in DRIFT"
    assert all(v["verdict"] != DRIFT for v in d["strategies"].values())
    assert d["global"]["verdict"] == DRIFT
    assert weight_factor(d, "C0USDT", "gen_0") == pytest.approx(settings.DRIFT_WEIGHT_FACTOR)


def test_drift_disabled_means_no_brake(monkeypatch):
    monkeypatch.setattr(settings, "DRIFT_ENABLED", False)
    d = compute_drift([_t() for _ in range(10)], _pairs())
    assert weight_factor(d, "AUSDT", "s1") == 1.0


def test_allocation_applies_the_brake_to_risk_and_leverage(monkeypatch):
    """Il freno arriva dove nascono size e leva, e puo' solo RIDURRE."""
    from bot.core.firebase_client import FirebaseClient
    from bot.core.models import Regime
    from bot.learning.adaptation import AdaptationEngine
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    a = AdaptationEngine(FirebaseClient())
    base_r, base_l, _ = a.allocation("s1", Regime.SIDEWAYS, 60.0)
    a._drift = compute_drift([_t() for _ in range(10)], _pairs())
    r, l, note = a.allocation("s1", Regime.SIDEWAYS, 60.0, drift_key=("AUSDT", "s1"))
    assert r < base_r and l < base_l
    assert "FRENO" in note and "deriva coppia" in note


# ---- freno di serie: matura in giorni, non in settimane ------------------- #
def _no_drift(monkeypatch):
    """Disattiva i tre verdetti di deriva alzando le soglie: cosi' si isola il
    solo freno di serie (i trade di _t sono tutti in perdita e farebbero scattare
    anche la deriva)."""
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    monkeypatch.setattr(settings, "STREAK_BRAKE_ENABLED", True)
    monkeypatch.setattr(settings, "STREAK_BRAKE_LOSSES", 4)
    monkeypatch.setattr(settings, "STREAK_BRAKE_FACTOR", 0.5)
    monkeypatch.setattr(settings, "DRIFT_MIN_TRADES_PAIR", 10_000)
    monkeypatch.setattr(settings, "DRIFT_MIN_TRADES_STRATEGY", 10_000)
    monkeypatch.setattr(settings, "DRIFT_MIN_TRADES_GLOBAL", 10_000)


def test_streak_is_counted_on_exit_ts_not_list_order():
    """La serie e' quella che chiude la sequenza NEL TEMPO: Firestore non
    garantisce l'ordine della lista. Qui la lista mette il guadagno per ultimo,
    ma per exit_ts e' il primo: le 4 perdite successive sono la serie corrente."""
    trades = [_t(pnl=-1, ts=200), _t(pnl=-1, ts=300), _t(pnl=-1, ts=400),
              _t(pnl=-1, ts=500), _t(pnl=+3, ts=100)]
    assert serie_perdite(trades) == {"s1": 4}


def test_streak_resets_on_a_gain_and_a_flat_trade():
    """Un trade in guadagno (o in pari: pnl >= 0) azzera la serie: la domanda e'
    'sta perdendo ADESSO', non 'quanto ha perso in totale'."""
    trades = [_t(pnl=-1, ts=1), _t(pnl=-1, ts=2), _t(pnl=-1, ts=3), _t(pnl=-1, ts=4),
              _t(pnl=+2, ts=5), _t(pnl=-1, ts=6)]
    assert serie_perdite(trades) == {"s1": 1}
    flat = trades[:4] + [_t(pnl=0.0, ts=5)]
    assert serie_perdite(flat) == {"s1": 0}


def test_streak_ignores_external_exits_and_is_per_strategy():
    """Kill switch e chiusure manuali non sono decisioni della strategia: non
    allungano la serie e non la interrompono. Ogni strategia ha la sua serie,
    sommata su tutte le coin."""
    trades = [_t(sym="AUSDT", pnl=-1, ts=1), _t(sym="BUSDT", pnl=-1, ts=2),
              _t(sym="AUSDT", pnl=+5, ts=3, reason="kill_switch"),   # ignorato
              _t(sym="CUSDT", pnl=-1, ts=4), _t(sym="AUSDT", pnl=-1, ts=5),
              _t(strat="s2", pnl=-1, ts=1), _t(strat="s2", pnl=+1, ts=2)]
    assert serie_perdite(trades) == {"s1": 4, "s2": 0}
    d = compute_drift(trades, {})            # anche SENZA promessa del gate
    assert d["pairs"] == {} and d["serie"] == {"s1": 4, "s2": 0}


def test_streak_without_exit_ts_keeps_stable_order():
    """Trade senza exit_ts -> 0 per tutti: l'ordinamento e' stabile, quindi
    resta l'ordine di arrivo (i test esistenti contano su questo)."""
    trades = [_t(pnl=+1), _t(pnl=-1), _t(pnl=-1)]
    assert serie_perdite(trades) == {"s1": 2}


def test_streak_brake_applies_only_at_the_threshold(monkeypatch):
    """3 perdite di fila: size piena. 4: dimezzata. Il 4 e' dichiarato prima
    (STREAK_BRAKE_LOSSES), non tarato sul paper."""
    _no_drift(monkeypatch)
    tre = compute_drift([_t(pnl=-1, ts=i) for i in range(3)], _pairs())
    assert tre["serie"] == {"s1": 3}
    assert weight_factor(tre, "AUSDT", "s1") == 1.0
    assert motivi_freno(tre, "AUSDT", "s1") == []
    quattro = compute_drift([_t(pnl=-1, ts=i) for i in range(4)], _pairs())
    assert weight_factor(quattro, "AUSDT", "s1") == pytest.approx(0.5)
    assert motivi_freno(quattro, "AUSDT", "s1") == ["serie 4 perdite"]
    # una coin MAI vista frena lo stesso: la serie e' della strategia
    assert weight_factor(quattro, "ZUSDT", "s1") == pytest.approx(0.5)
    # un'altra strategia no
    assert weight_factor(quattro, "AUSDT", "s2") == 1.0


def test_streak_brake_can_be_switched_off(monkeypatch):
    """STREAK_BRAKE_ENABLED=false -> comportamento identico a prima."""
    _no_drift(monkeypatch)
    d = compute_drift([_t(pnl=-1, ts=i) for i in range(6)], _pairs())
    assert weight_factor(d, "AUSDT", "s1") == pytest.approx(0.5)
    monkeypatch.setattr(settings, "STREAK_BRAKE_ENABLED", False)
    assert weight_factor(d, "AUSDT", "s1") == 1.0
    assert motivi_freno(d, "AUSDT", "s1") == []


def test_motivi_freno_lists_every_active_brake(monkeypatch):
    """La nota del trade deve dire PERCHE' la size era ridotta: tutti i motivi
    attivi, nell'ordine coppia / strategia / globale / serie."""
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    monkeypatch.setattr(settings, "STREAK_BRAKE_ENABLED", True)
    monkeypatch.setattr(settings, "STREAK_BRAKE_LOSSES", 4)
    d = compute_drift([_t(pnl=-1, ts=i) for i in range(45)], _pairs())
    assert motivi_freno(d, "AUSDT", "s1") == [
        "deriva coppia", "deriva strategia", "deriva globale", "serie 45 perdite"]
    assert motivi_freno(None, "AUSDT", "s1") == []
    monkeypatch.setattr(settings, "DRIFT_ENABLED", False)
    assert motivi_freno(d, "AUSDT", "s1") == []


def test_floor_holds_with_drift_and_streak_together(monkeypatch):
    """Deriva su tre livelli + serie: quattro dimezzamenti farebbero 0.0625, ma
    DRIFT_WEIGHT_FLOOR resta il pavimento di tutto. Frena, non spegne."""
    monkeypatch.setattr(settings, "DRIFT_ENABLED", True)
    monkeypatch.setattr(settings, "STREAK_BRAKE_ENABLED", True)
    monkeypatch.setattr(settings, "STREAK_BRAKE_LOSSES", 4)
    d = compute_drift([_t(pnl=-1, ts=i) for i in range(45)], _pairs())
    assert d["global"]["verdict"] == DRIFT and d["serie"]["s1"] == 45
    assert weight_factor(d, "AUSDT", "s1") == pytest.approx(settings.DRIFT_WEIGHT_FLOOR)


def test_allocation_note_names_the_streak(monkeypatch):
    """Dalla nota del trade si legge il freno di serie, col fattore applicato."""
    from bot.core.firebase_client import FirebaseClient
    from bot.core.models import Regime
    from bot.learning.adaptation import AdaptationEngine
    _no_drift(monkeypatch)
    a = AdaptationEngine(FirebaseClient())
    base_r, _, _ = a.allocation("s1", Regime.SIDEWAYS, 60.0)
    a._drift = compute_drift([_t(pnl=-1, ts=i) for i in range(4)], _pairs())
    r, _, note = a.allocation("s1", Regime.SIDEWAYS, 60.0, drift_key=("AUSDT", "s1"))
    assert r == pytest.approx(base_r * 0.5)
    assert "FRENO x0.50 (serie 4 perdite)" in note


# ---- anello di ritorno: l'evidenza pesa nel gate -------------------------- #
def test_drifted_pair_counts_as_a_gate_failure():
    """IL CUORE DELL'ANELLO: una coppia smentita dal vivo non accumula un pass
    nemmeno se la storia la promuove ancora — e va verso l'auto-purge.

    IL CONTO PERO' E' QUELLO DELLA FINESTRA. Questo test chiedeva `fail_count == 1`
    subito, al primo run: era la fotografia del difetto, non del comportamento
    voluto. Contando a ogni run, col timer ogni tre ore una coppia in deriva spariva
    dal registro in sei ore e non poteva piu' redimersi, perche' il contatore si
    azzera solo alla chiusura di una finestra e la coppia non ne vedeva mai una.
    Ora la deriva fa la cosa giusta: impedisce alla finestra di chiudersi con una
    conferma, e il fallimento arriva quando la finestra finisce."""
    from scripts.optimize import update_registry
    from bot.core.firebase_client import decode_pairs

    class FB:
        def __init__(self):
            self.docs = {("drift", "current"): {
                "pairs": {"AUSDT|s1": {"verdict": DRIFT}}}}
        def get_doc(self, c, d):
            return self.docs.get((c, d), {})
        def set_doc(self, c, d, data):
            self.docs[(c, d)] = data

    fb = FB()
    key = "AUSDT|s1"
    entry = {"symbol": "AUSDT", "strategy": "s1", "params": {}, "oos_pf": 1.5,
             "oos_pnl_pct": 0.4, "oos_trades": 40, "oos_win_rate": 0.5,
             "passed": True, "data_end": 1_700_000_000.0}
    update_registry(fb, {key: entry}, [key])          # la STORIA la promuove...
    rec = decode_pairs(fb.get_doc("strategy_registry", "validated")["pairs"])[key]
    assert rec["pass_count"] == 0                     # ...ma il vivo la smentisce
    assert rec.get("fail_count", 0) == 0, "dentro la finestra non si viene purgati"
    assert "drift_seen_at" in rec
    assert rec["window_start"] > 0                    # la finestra e' aperta e conta

    # una settimana di dati nuovi dopo, sempre in deriva: ORA arriva il fallimento
    entry_dopo = {**entry, "data_end": entry["data_end"] + 169 * 3600.0}
    update_registry(fb, {key: entry_dopo}, [key])
    rec = decode_pairs(fb.get_doc("strategy_registry", "validated")["pairs"])[key]
    assert rec["fail_count"] == 1 and rec["pass_count"] == 0


def test_without_drift_the_pass_is_normal():
    """Nessuna deriva -> il percorso resta identico a prima (nessuna regressione)."""
    from scripts.optimize import update_registry
    from bot.core.firebase_client import decode_pairs

    class FB:
        def __init__(self):
            self.docs = {}
        def get_doc(self, c, d):
            return self.docs.get((c, d), {})
        def set_doc(self, c, d, data):
            self.docs[(c, d)] = data

    fb = FB()
    key = "AUSDT|s1"
    entry = {"symbol": "AUSDT", "strategy": "s1", "params": {}, "oos_pf": 1.5,
             "oos_pnl_pct": 0.4, "oos_trades": 40, "oos_win_rate": 0.5,
             "passed": True, "data_end": 1_700_000_000.0}
    update_registry(fb, {key: entry}, [key])
    rec = decode_pairs(fb.get_doc("strategy_registry", "validated")["pairs"])[key]
    assert rec["pass_count"] == 1 and rec.get("fail_count", 0) == 0


def test_serie_con_exit_ts_illeggibile_non_fa_saltare_la_deriva():
    """Un exit_ts scritto male (stringa ISO) non deve spegnere l'intero
    documento di deriva: quel trade va in coda-zero e il resto si calcola."""
    from bot.learning.drift import serie_perdite
    trades = [_t(pnl=-1.0), {**_t(pnl=-1.0), "exit_ts": "2026-09-23T10:00:00"},
              {**_t(pnl=-1.0), "exit_ts": 5.0}]
    assert serie_perdite(trades) == {"s1": 3}
    d = compute_drift(trades, _pairs())
    assert d["serie"] == {"s1": 3}
