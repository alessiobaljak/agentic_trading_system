"""R1, il gate rigiocato nel passato (1 ott 2026, si' del proprietario).

Cosa si protegge, su dati finti (niente rete, niente Firebase):
  * le 26 date (la piu' recente lascia 14 giorni interi dopo di se', una ogni
    14 giorni, la piu' vecchia circa un anno prima) e le candidate fisse per data;
  * il taglio IN MEMORIA: al gate (candele, indicatori, contesto di mercato)
    non arriva niente dopo la data, e il caricatore si chiama solo con la fine
    di OGGI (con una fine passata riscriverebbe la cache del gate);
  * la finestra dopo: trade entrati in (D, D+14g], R netto = pnl_pct/stop_pct,
    fuori e contati gli ancora aperti e i senza stop; il rigioco parte alla
    data e usa l'uscita scelta dal gate;
  * gruppi e margine: le somme danno gli stessi numeri degli helper del
    `portafoglio` (statistiche, errore per data, errore trade per trade);
  * i tre esiti della regola, compreso «meno di 80 trade»;
  * lucchetto, giro del gate in corso o in arrivo, budget, ripresa dopo un
    worker ucciso, prova piccola;
  * nessuna scrittura Firebase o del registro, la riga della lista bianca.
"""
import datetime as dt
import math
import os
import random
import signal
import time
from datetime import timezone
from types import SimpleNamespace

import pytest

import backtesting.data_loader as dl
from scripts import portafoglio_backtest as pb
from scripts import replay_gate as rv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OGGI = dt.date.today().isoformat()


def _ts(y, m, d, h=0, mi=0):
    return dt.datetime(y, m, d, h, mi, tzinfo=timezone.utc).timestamp()


@pytest.fixture(autouse=True)
def _niente_gate_ne_file_veri(tmp_path, monkeypatch):
    """Nei test il gate non c'e' (nessun processo, unita' o timer) e tutti i
    file di R1 stanno in una cartella temporanea."""
    monkeypatch.setattr(rv, "servizio_gate_attivo", lambda: False)
    monkeypatch.setattr(rv, "secondi_al_prossimo_giro", lambda ora=None: None)
    monkeypatch.setattr(rv, "giro_in_corso", lambda *a, **k: [])
    base = tmp_path / "replay_gate"
    monkeypatch.setattr(rv, "DIR_R1", str(base))
    monkeypatch.setattr(rv, "FILE_PIANO", str(base / "piano.json"))
    monkeypatch.setattr(rv, "DIR_UNITA", str(base / "unita"))
    monkeypatch.setattr(rv, "FILE_ESITO", str(base / "ultimo.txt"))
    monkeypatch.setattr(rv, "FILE_PID", str(base / "ultimo.pid"))
    monkeypatch.setattr(rv, "FILE_LOCK", str(base / "in_corso.lock"))
    # il caricatore vero non deve mai partire (rete, cache del gate)
    monkeypatch.setattr(dl, "_drop_older", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("la cache del gate non si tocca")))
    monkeypatch.setattr(dl, "funding_rate_for", lambda s: None)
    rv._S.clear()
    yield
    rv._S.clear()


# --------------------------------------------------------------------------- #
# 1. date e candidate                                                          #
# --------------------------------------------------------------------------- #
def test_le_26_date():
    date_ = rv.date_del_piano(dt.date(2026, 10, 1))
    assert len(date_) == 26 == len(set(date_))
    assert date_[0] == "2026-09-17"                   # 14 giorni interi dopo
    assert date_[-1] == "2025-10-02"                  # circa un anno prima
    giorni = [dt.date.fromisoformat(g) for g in date_]
    assert all((a - b).days == 14 for a, b in zip(giorni, giorni[1:]))


def test_candidate_fisse_per_data_e_senza_gemelle():
    from scripts.discover_strategies import firma_spec
    a = rv.candidate_della_data("2026-09-17", 30)
    assert a == rv.candidate_della_data("2026-09-17", 30)       # un lancio ripreso: le stesse
    assert [s["id"] for s in a] != [s["id"] for s in rv.candidate_della_data("2026-09-03", 30)]
    assert 0 < len(a) <= 30
    assert len({firma_spec(s) for s in a}) == len(a)
    assert rv.seme_della_data("2025-09-18") == 20250918


# --------------------------------------------------------------------------- #
# 2. il taglio in memoria: niente dopo la data arriva al gate                  #
# --------------------------------------------------------------------------- #
def _serie(sym, fino=dt.datetime(2026, 10, 1, tzinfo=timezone.utc), giorni=95):
    return dl._synthetic(fino - dt.timedelta(days=giorni), fino, interval_min=15, symbol=sym)


def _cfg(n=3):
    return {"interval": "15m", "start": "2022-01-01", "source": "auto", "windows": 3,
            "candidate_per_data": n}


def test_al_gate_non_arriva_niente_dopo_la_data(monkeypatch):
    """Il cuore della prova, col motore e il gate VERI su candele finte: ogni
    chiamata a `evaluate_spec` e a `compute_indicator_frame` del gate, e il
    contesto di mercato del gate, finiscono prima della data; il caricatore e'
    chiamato solo con la fine di oggi."""
    serie = {s: _serie(s) for s in ("AUSDT", "BTCUSDT")}
    chiamate = []

    def carica(sym, interval, start, end, prefer="auto", **k):
        chiamate.append((sym, end))
        return serie[sym]
    monkeypatch.setattr(rv, "load_candles", carica)
    giorno = "2026-09-10"
    D = rv._ts(giorno)
    gate_visto = []
    vero_eval = rv.d.evaluate_spec

    def spia_eval(opt, sym, candles, frame, spec, **kw):
        gate_visto.append((candles[-1].open_time.timestamp(), len(candles), len(frame)))
        ctx = kw.get("context_by_ts")
        if ctx:
            gate_visto.append((max(c.timestamp() for c in ctx), 0, 0))
        return vero_eval(opt, sym, candles, frame, spec, **kw)
    monkeypatch.setattr(rv.d, "evaluate_spec", spia_eval)
    # tutte candidate di MERCATO: anche il contesto BTC passa dal gate
    specs = [s for s in rv.candidate_della_data(giorno, 60) if rv.usa_mercato(s)][:2]
    specs += [s for s in rv.candidate_della_data(giorno, 60) if not rv.usa_mercato(s)][:1]
    assert len(specs) == 3
    monkeypatch.setattr(rv, "candidate_della_data", lambda g, n: specs)
    rv._init(_cfg(), OGGI, 0.0)
    rv._S["min_history"] = 2000
    rec = rv._una_unita((giorno, "AUSDT"))
    assert rec["stato"] == "ok", rec
    assert rec["n_candidate"] == 3 and rec["bocciate"]["n_candidate"] + len(rec["passate"]) == 3
    assert gate_visto and all(ts < D for ts, _n, _f in gate_visto)
    # il gate ha avuto TUTTE le candele prima della data, e indicatori su quelle sole
    prima = sum(1 for c in serie["AUSDT"] if c.open_time.timestamp() < D)
    assert {(n, f) for _ts_, n, f in gate_visto if n} == {(prima, prima)}
    assert chiamate and all(end == OGGI for _s, end in chiamate)
    # dopo la data si e' rigiocato davvero: le bocciate hanno trade nei 14 giorni
    assert rec["bocciate"]["n"] + sum(len(p["r"]) for p in rec["passate"]) > 0


def test_storia_corta_alla_data(monkeypatch):
    monkeypatch.setattr(rv, "load_candles", lambda *a, **k: _serie("AUSDT", giorni=40))
    monkeypatch.setattr(rv, "candidate_della_data", lambda g, n: [])
    rv._init(_cfg(), OGGI, 0.0)
    rec = rv._una_unita(("2026-09-10", "AUSDT"))
    assert rec["stato"] == "storia"          # un anno di storia alla data, come il gate


# --------------------------------------------------------------------------- #
# 3. la finestra dopo                                                          #
# --------------------------------------------------------------------------- #
def test_la_finestra_dopo_confini_e_r():
    D, bar = _ts(2026, 9, 3), 900.0
    fine = D + 14 * 86400

    def t(entry, pnl=0.02, stop=0.01, fine_dati=False):
        return {"entry_ts": entry, "pnl_pct": pnl, "stop_pct": stop, "fine_dati": fine_dati}
    trades = [t(D - bar, 0.05),          # segnale sull'ultima candela prima: entra A D, fuori
              t(D, 0.02),                # entra a D + 15 minuti: dentro
              t(fine - bar, -0.01),      # entra esattamente a D + 14 giorni: dentro
              t(fine, 0.03),             # entra dopo: fuori
              t(D + 3600, 0.01, fine_dati=True),
              t(D + 7200, 0.01, stop=None)]
    out = rv.r_dopo(trades, D, fine, bar)
    assert out == {"r": [2.0, -1.0], "fine_dati": 1, "senza_stop": 1}


class _BtFinto:
    window = 4

    def __init__(self, trades_per_g):
        self.visti = []
        self._prep_cache, self._htf_cache = {}, {}
        self.trades_per_g = trades_per_g

    def run_strategy(self, g, sym, seg, frame=None, context_by_ts=None):
        from backtesting.engine import StrategyStats
        self.visti.append((g.params, seg[0].open_time, seg[-1].open_time, len(frame)))
        return StrategyStats(strategy="s", trades=self.trades_per_g(seg))


def test_il_rigioco_parte_alla_data_e_usa_l_uscita_scelta(monkeypatch):
    import pandas as pd
    monkeypatch.setattr(rv, "compute_indicator_frame", lambda c: pd.DataFrame({"i": range(len(c))}))
    candles = _serie("AUSDT", giorni=40)
    D = rv._ts("2026-09-10")
    k = sum(1 for c in candles if c.open_time.timestamp() < D)

    def trades(seg):
        e = seg[4].open_time.timestamp()        # primo segnale possibile: la candela della data
        return [SimpleNamespace(entry_ts=e, bars_held=3, pnl_pct=0.015, direction="long",
                                mfe_r=1.0, feats={"stop_pct": 0.01})]
    bt = _BtFinto(trades)
    opt = SimpleNamespace(bt=bt)
    rv._S.update(cfg=_cfg(), ctx_dopo={})
    uscita = {"scale_r_mults": [1.0, 2.0], "sl_to_breakeven": False, "profit_lock_keep": 0.75}
    voci = [{"id": "gen_a", "passata": True, "uscita": uscita},
            {"id": "gen_b", "passata": False, "uscita": None}]
    specs = [{"id": "gen_a", "features": []}, {"id": "gen_b", "features": []}]
    monkeypatch.setattr(rv, "crea_operata", lambda spec, lp: (
        lambda: SimpleNamespace(params=dict(lp or {}), name=spec["id"])))
    rv.rigioca_dopo(opt, "AUSDT", candles, D, voci, specs)
    (p1, inizio, fine_seg, nf), (p2, _i, _f, _n) = bt.visti
    assert p1 == uscita and p2 == {}                       # la configurazione del gate
    assert inizio == candles[k - 4].open_time              # riscaldamento: window candele prima
    assert candles[k].open_time.timestamp() == D           # e il primo segnale alla data
    assert fine_seg.timestamp() >= D + 14 * 86400 + rv.HORIZON_BARS * 900
    assert voci[0]["r"] == [1.5] and voci[1]["r"] == [1.5]


# --------------------------------------------------------------------------- #
# 4. gruppi, margine, esiti                                                    #
# --------------------------------------------------------------------------- #
def _per_data(righe_p, righe_b):
    out = {}
    for lato, righe in (("passate", righe_p), ("bocciate", righe_b)):
        for r, g in righe:
            x = out.setdefault(g, {"passate": [0, 0.0, 0.0], "bocciate": [0, 0.0, 0.0],
                                   "conferme3": [0, 0.0, 0.0]})
            x[lato] = rv._piu(x[lato], rv.somme([r]))
    return out


def test_le_somme_danno_gli_stessi_numeri_degli_helper():
    rnd = random.Random(3)
    date_ = [f"2026-0{m}-01" for m in range(1, 8)]
    p = [(rnd.gauss(0.2, 1.1), rnd.choice(date_)) for _ in range(140)]
    b = [(rnd.gauss(0.0, 0.9) + (0.3 if g == date_[2] else 0), g)
         for g in date_ for _ in range(60)]
    let = rv.lettura(_per_data(p, b))
    sp = pb.statistiche_lato([(r, None, None) for r, _ in p])
    sb = pb.statistiche_lato([(r, None, None) for r, _ in b])
    assert let["passate"]["n"] == sp["n"]
    assert let["passate"]["r_medio"] == pytest.approx(sp["r_medio"], abs=1e-12)
    assert let["passate"]["dev_std"] == pytest.approx(sp["dev_std"], abs=1e-9)
    assert let["differenza"] == pytest.approx(sp["r_medio"] - sb["r_medio"], abs=1e-12)
    assert let["errore_trade"] == pytest.approx(pb.errore_standard_differenza(sp, sb), abs=1e-9)
    assert let["errore_data"] == pytest.approx(pb.errore_standard_per_giorno(p, b), abs=1e-9)
    assert let["margine"] == pytest.approx(2 * max(let["errore_trade"], let["errore_data"]))


def _gruppo(media, n, date_, spread=0.5):
    """n righe intorno a `media`, sparse sulle date, con dispersione nota."""
    out = []
    for i in range(n):
        out.append((media + (spread if i % 2 else -spread), date_[i % len(date_)]))
    return out


def test_i_tre_esiti_della_regola():
    date_ = [f"2026-{m:02d}-01" for m in range(1, 11)]
    # meno di 80 trade delle passate: non si sa, anche con una differenza enorme
    let = rv.lettura(_per_data(_gruppo(2.0, 79, date_), _gruppo(0.0, 4000, date_)))
    assert let["esito"] == "non si sa" and "79 trade" in let["perche"]
    # differenza oltre il margine: vantaggio vero
    let = rv.lettura(_per_data(_gruppo(0.5, 400, date_), _gruppo(0.0, 4000, date_)))
    assert let["differenza"] > let["margine"]
    assert let["esito"] == "il gate ha un vantaggio vero"
    # nessuna differenza e margine stretto: fortuna
    let = rv.lettura(_per_data(_gruppo(0.0, 4000, date_, 0.3), _gruppo(0.0, 4000, date_, 0.3)))
    assert let["differenza"] + let["margine"] < rv.SOGLIA_FORTUNA_R
    assert let["esito"] == "il gate sceglie soprattutto fortuna"
    # nessuna differenza ma margine largo: non si sa
    let = rv.lettura(_per_data(_gruppo(0.0, 90, date_, 1.5), _gruppo(0.0, 4000, date_)))
    assert let["esito"] == "non si sa" and "caso migliore" in let["perche"]
    # una data sola: senza l'errore per data la regola non decide
    let = rv.lettura(_per_data(_gruppo(0.5, 400, date_[:1]), _gruppo(0.0, 4000, date_[:1])))
    assert let["errore_data"] is None and let["esito"] == "non si sa"


def test_il_record_dell_unita_e_piccolo_e_porta_le_somme():
    voci = [{"id": "a", "passata": True, "binding": None, "r": [1.0, -0.5], "fine_dati": 0,
             "senza_stop": 0, "uscita": None},
            {"id": "b", "passata": False, "binding": "pf", "r": [0.2, 0.4, -1.0], "fine_dati": 1,
             "senza_stop": 0, "uscita": None},
            {"id": "c", "passata": False, "binding": "trades", "r": [], "fine_dati": 0,
             "senza_stop": 2, "uscita": None}]
    rec = rv.record_unita(voci)
    assert [p["id"] for p in rec["passate"]] == ["a"]
    b = rec["bocciate"]
    assert (b["n_candidate"], b["n"], b["con_trade"], b["fine_dati"], b["senza_stop"]) == (2, 3, 1, 1, 2)
    assert b["s"] == pytest.approx(-0.4) and b["q"] == pytest.approx(1.2)
    assert b["per_criterio"] == {"pf": 1, "trades": 1}
    per_data = rv.somme_per_data([{**rec, "data": "2026-09-17"}])
    assert per_data["2026-09-17"]["passate"] == [2, 0.5, 1.25]


# --------------------------------------------------------------------------- #
# 5. ripresa, prova piccola, salvataggio                                       #
# --------------------------------------------------------------------------- #
def _piano(date_=("2026-09-17", "2026-09-03", "2026-08-20"), monete=("AUSDT", "BUSDT")):
    return {"versione": rv.VERSIONE, "oggi": "2026-10-01", "date": list(date_),
            "universo": list(monete), "candidate_per_data": 3, "interval": "15m",
            "start": "2022-01-01", "source": "auto", "windows": 3}


def test_prova_piccola_poi_il_resto():
    piano = _piano()
    lavoro, prova = rv.lavoro_da_fare(piano, {})
    assert prova and {g for g, _c in lavoro} == {"2026-09-17", "2026-09-03"}
    fatte = {("2026-09-17", "AUSDT"): {"stato": "ok"}, ("2026-09-17", "BUSDT"): {"stato": "storia"}}
    lavoro, prova = rv.lavoro_da_fare(piano, fatte)
    assert not prova
    assert lavoro == [("2026-09-03", "AUSDT"), ("2026-09-03", "BUSDT"),
                      ("2026-08-20", "AUSDT"), ("2026-08-20", "BUSDT")]


def test_salva_solo_gli_esiti_veri_e_riprova_un_errore():
    for stato in ("tempo", "giro", "interrotta"):
        assert not rv.salva_unita({"data": "2026-09-17", "coin": "AUSDT", "stato": stato})
    assert rv.leggi_unita() == {}
    rec = {"data": "2026-09-17", "coin": "AUSDT", "stato": "errore", "errore": "x"}
    assert rv.salva_unita(rec)
    fatte = rv.leggi_unita()
    assert fatte[("2026-09-17", "AUSDT")]["tentativi"] == 1
    assert not rv.unita_chiusa(fatte[("2026-09-17", "AUSDT")])       # si riprova
    rv.salva_unita(rec)
    assert rv.unita_chiusa(rv.leggi_unita()[("2026-09-17", "AUSDT")])  # poi basta
    rv.salva_unita({"data": "2026-09-17", "coin": "BUSDT", "stato": "ok", "n_candidate": 0})
    assert rv.unita_chiusa(rv.leggi_unita()[("2026-09-17", "BUSDT")])


def _unita_o_muori(item):
    """Il worker dell'unita' «KILL» si uccide (come l'OOM del kernel)."""
    giorno, sym = item
    if sym == "KILL":
        time.sleep(1.0)
        os.kill(os.getpid(), signal.SIGKILL)
    return {"data": giorno, "coin": sym, "stato": "ok", "n_candidate": 1, "passate": [],
            "bocciate": {"n": 2, "s": 0.1, "q": 0.5}}


def test_un_worker_ucciso_non_perde_le_unita_finite_e_il_lancio_dopo_riprende(monkeypatch):
    monkeypatch.setattr(rv, "_una_unita", _unita_o_muori)
    monkeypatch.setattr(rv, "_init", lambda *a: None)
    piano = _piano(date_=("2026-09-17",), monete=("AUSDT", "BUSDT", "KILL"))
    lavoro, _ = rv.lavoro_da_fare(piano, rv.leggi_unita())
    righe, interrotta = rv.esegui_e_salva(lavoro, 2, (None, OGGI, 0.0), rv.salva_unita)
    assert interrotta and "worker" in interrotta
    assert {r["coin"]: r["stato"] for r in righe}["KILL"] == "interrotta"
    fatte = rv.leggi_unita()
    assert set(fatte) == {("2026-09-17", "AUSDT"), ("2026-09-17", "BUSDT")}
    lavoro, _ = rv.lavoro_da_fare(piano, fatte)
    assert lavoro == [("2026-09-17", "KILL")]                     # solo quella da rifare


def test_budget_scaduto_e_gate_in_arrivo_prima_di_ogni_unita(monkeypatch):
    monkeypatch.setattr(rv, "load_candles", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("non si carica niente")))
    rv._S.update(deadline=time.time() - 1, cfg=_cfg(), end=OGGI)
    assert rv._una_unita(("2026-09-17", "AUSDT"))["stato"] == "tempo"
    rv._S.update(deadline=0.0)
    monkeypatch.setattr(rv, "giro_in_corso", lambda *a, **k: [4242])
    rec = rv._una_unita(("2026-09-17", "AUSDT"))
    assert rec["stato"] == "giro" and "pid 4242" in rec["errore"]
    monkeypatch.setattr(rv, "giro_in_corso", lambda *a, **k: [])
    monkeypatch.setattr(rv, "secondi_al_prossimo_giro", lambda ora=None: 5 * 60.0)
    assert rv._una_unita(("2026-09-17", "AUSDT"))["stato"] == "giro"
    assert not rv.salva_unita({"data": "2026-09-17", "coin": "AUSDT", "stato": "giro"})


# --------------------------------------------------------------------------- #
# 6. lucchetto e giro del gate                                                 #
# --------------------------------------------------------------------------- #
def test_giro_in_corso_vede_gate_e_voto_t(tmp_path, monkeypatch):
    monkeypatch.undo()
    for pid, cmd in (("101", b"python\0-m\0scripts.discover_strategies\0--top\0200"),
                     ("102", b"python\0-m\0scripts.portafoglio_backtest"),
                     ("103", b"python\0-m\0scripts.t_validate\0--su-file"),
                     ("104", b"python\0-m\0scripts.replay_gate\0--su-file"),
                     ("self", b"x")):
        (tmp_path / pid).mkdir()
        (tmp_path / pid / "cmdline").write_bytes(cmd)
    assert rv.giro_in_corso(str(tmp_path)) == [101, 103]
    assert rv.giro_in_corso(str(tmp_path / "manca")) == []


def test_col_lucchetto_tenuto_non_parte(monkeypatch, capsys):
    monkeypatch.setattr(rv, "top_symbols_by_volume", lambda n: (_ for _ in ()).throw(
        AssertionError("non doveva partire")))
    os.makedirs(rv.DIR_R1, exist_ok=True)
    assert rv.prendi_lucchetto(rv.FILE_LOCK) == os.getpid()
    try:
        # un'altra apertura dello stesso file: per flock e' un altro lancio
        assert rv.main([]) == 0
        assert "gia' in corso" in capsys.readouterr().out
        assert not os.path.exists(rv.FILE_PIANO)
    finally:
        rv.lascia_lucchetto(rv.FILE_LOCK)


def test_col_gate_in_corso_in_primo_piano_esce_in_sfondo_aspetta(monkeypatch, capsys):
    monkeypatch.setattr(rv, "top_symbols_by_volume", lambda n: (_ for _ in ()).throw(
        AssertionError("non doveva partire")))
    monkeypatch.setattr(rv, "giro_in_corso", lambda *a, **k: [4242])
    assert rv.main([]) == 0
    assert "pid 4242" in capsys.readouterr().out
    assert rv.prendi_lucchetto(rv.FILE_LOCK) == os.getpid()      # lucchetto lasciato
    rv.lascia_lucchetto(rv.FILE_LOCK)
    monkeypatch.setattr(rv, "giro_in_corso", lambda *a, **k: [])
    monkeypatch.setattr(rv, "secondi_al_prossimo_giro", lambda ora=None: 15 * 60.0)
    assert rv.main([]) == 0
    assert "parte fra 15 minuti" in capsys.readouterr().out
    # in sfondo (come da systemd-run): aspetta che il giro finisca, poi parte
    monkeypatch.setattr(rv, "secondi_al_prossimo_giro", lambda ora=None: None)
    giri = iter([[4242], [4242], []])
    monkeypatch.setattr(rv, "giro_in_corso", lambda *a, **k: next(giri))
    dormite, partito = [], []
    monkeypatch.setattr(rv.time, "sleep", lambda s: dormite.append(s))
    monkeypatch.setattr(rv, "_lancio", lambda args: partito.append(1) or 0)
    assert rv._sotto_lucchetto(SimpleNamespace(), aspetta=True) == 0
    assert dormite == [rv.ATTESA_PASSO_S] * 2 and partito == [1]


def test_su_file_in_modalita_test_non_parte(monkeypatch, capsys):
    monkeypatch.setenv("TRADING_BOT_TEST_MODE", "1")
    assert rv.main(["--su-file"]) == 0
    assert "modalita' test" in capsys.readouterr().out
    assert not os.path.exists(rv.FILE_ESITO)


# --------------------------------------------------------------------------- #
# 7. il lancio intero, l'esito, la sicurezza                                   #
# --------------------------------------------------------------------------- #
def _finta(item):
    giorno, sym = item
    rnd = random.Random(f"{giorno}{sym}")
    r = [round(rnd.gauss(0.3, 1.0), 3) for _ in range(30)]
    rb = [rnd.gauss(0.0, 1.0) for _ in range(200)]
    return {"data": giorno, "coin": sym, "secondi": 12.0,
            **rv.record_unita([{"id": "gen_p", "passata": True, "binding": None, "r": r,
                                "fine_dati": 0, "senza_stop": 0, "uscita": None},
                               {"id": "gen_b", "passata": False, "binding": "pf", "r": rb,
                                "fine_dati": 0, "senza_stop": 0, "uscita": None}])}


def test_il_lancio_scrive_solo_i_suoi_file_poi_esito_parziale(monkeypatch, capsys, tmp_path):
    import bot.core.firebase_client as fc
    monkeypatch.setattr(fc, "get_firebase", lambda: (_ for _ in ()).throw(
        AssertionError("niente Firebase")))
    monkeypatch.setattr(rv, "top_symbols_by_volume", lambda n: ["AUSDT", "BUSDT"])
    monkeypatch.setattr(rv, "_una_unita", _finta)
    monkeypatch.setattr(rv, "_init", lambda *a: None)
    monkeypatch.setattr(rv.d, "motore_del_giro", lambda args: {"gate": {}})
    assert rv.main(["--workers", "1"]) == 0
    out = capsys.readouterr().out
    assert "PROVA PICCOLA" in out and "PROVA PICCOLA FINITA" in out
    piano = rv.leggi_piano()
    assert len(piano["date"]) == 26 and piano["universo"] == ["AUSDT", "BUSDT"]
    fatte = rv.leggi_unita()
    assert {g for g, _c in fatte} == set(piano["date"][:rv.PROVA_DATE])
    # tutto cio' che e' stato scritto sta nella cartella di R1
    scritti = [os.path.join(r, f) for r, _d, fs in os.walk(tmp_path) for f in fs]
    assert scritti and all(p.startswith(rv.DIR_R1) for p in scritti)
    # l'esito: avanzamento, regola PRIMA dei numeri, lettura PARZIALE
    assert rv.main(["--esito"]) == 0
    out = capsys.readouterr().out
    assert "date complete 2 su 26" in out
    assert out.index("REGOLA R1") < out.index("passate: 120 trade") < out.index("LETTURA PARZIALE")
    assert "non decide ancora" in out and "limiti dichiarati" in out


def test_il_codice_non_tocca_firebase_ne_registro():
    with open(os.path.join(ROOT, "scripts", "replay_gate.py"), encoding="utf-8") as f:
        src = f.read()
    for vietato in ("set_doc", "get_firebase", "backfill_passes", "merge_into_registry",
                    "finalizza_registro", "scrivi_righe_worker", "_disc_one", "_disc_init"):
        assert vietato not in src, vietato
    # e il caricatore solo con la fine del lancio (oggi)
    assert "load_candles(sym, cfg[\"interval\"], cfg[\"start\"], _S[\"end\"]" in src


def test_la_riga_della_lista_bianca():
    from scripts.ops_agent import parse_allowlist
    with open(os.path.join(ROOT, "ops", "allowlist.example"), encoding="utf-8") as f:
        voci = parse_allowlist(f.read())
    assert voci["replay-gate"]["cmd"] == (
        "systemd-run --no-block --collect --unit=replay-gate "
        "--nice=15 --property=IOSchedulingClass=idle "
        "--property=WorkingDirectory=/root/agentic_trading_system "
        "/root/agentic_trading_system/.venv/bin/python -m scripts.replay_gate --su-file")
    assert voci["replay-gate-esito"]["cmd"] == ".venv/bin/python -m scripts.replay_gate --esito"
    for k in ("replay-gate", "replay-gate-esito"):
        assert voci[k]["args"] is False
        assert "|" not in voci[k]["cmd"] and ">" not in voci[k]["cmd"] and "&&" not in voci[k]["cmd"]
    with open(os.path.join(ROOT, ".gitignore"), encoding="utf-8") as f:
        assert "data/replay_gate/" in f.read()
    # le soglie della regola scritta il 1 ott (docs/andremo_live.md)
    assert math.isclose(rv.SOGLIA_FORTUNA_R, 0.10) and rv.MIN_TRADE_PASSATE == 80
    assert rv.N_DATE == 26 and rv.PASSO_GIORNI == 14 == rv.DOPO_GIORNI
