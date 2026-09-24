"""IL SELETTORE, PASSO 1 — il confronto offline non deve mentire.

Il disegno (docs/disegno_cervello.md, Punto 2) chiede un modello leggibile,
addestrato SOLO sui trade del gate, giudicato in walk-forward contro «apri
tutto». Qui si verifica che i pezzi facciano quello che dicono: il vettore
scarta cio' che non puo' inventare (e non scarta per un regime mancante), la
logistica ritrova il segno di un effetto vero e regge una variabile costante,
il walk-forward dice «batte» quando c'e' un segnale e «non batte» quando gli
esiti sono a caso (test di permutazione, audit 24 set 2026), riporta le misure
anche per `passed`, e sotto il campione minimo si ferma invece di dare un
verdetto. La lettura fonde i duplicati e le coppie gemelle: un trade e' un trade.
"""
import argparse
import importlib
import json
import os

import numpy as np
import pytest

from bot.learning import selettore as sel
from scripts import selettore_report


@pytest.fixture(autouse=True)
def _argparse_integro():
    """tests/test_frequenza_segnali.py (`_argomenti`) sostituisce
    `ArgumentParser.parse_args` con una spia e poi lo CANCELLA invece di
    ripristinarlo: ogni test successivo che legge argomenti in-process trova la
    classe senza il metodo. Finche' quel file non ripristina il metodo, qui lo
    si rimette a posto ricaricando il modulo (24 set 2026)."""
    if not hasattr(argparse.ArgumentParser, "parse_args"):
        importlib.reload(argparse)
    yield


# ---- fabbrica di righe sintetiche ---------------------------------------- #
REGIMI = ("bull_trending", "bear_trending", "sideways", "high_uncertainty")


def _riga(i, rsi, win, pnl, direction="long", famiglia="reversion", feats_extra=None,
          t0=1_650_000_000.0, regime="sideways", passed=None, strategy="strat"):
    feats = {"rsi": rsi, "adx": 25.0, "stoch_k": 50.0, "atr_pct": 0.02, "dist_ema": 0.0,
             "bb_pos": 0.5, "vol_ratio": 1.0, "stop_pct": 0.02, "r1": 1.0, "market_up": 1.0}
    feats.update(feats_extra or {})
    row = {"symbol": f"C{i % 7}USDT", "strategy": strategy, "direction": direction,
           "regime": regime, "entry_ts": t0 + i * 6 * 3600.0, "pnl_pct": pnl,
           "pnl": pnl * 100, "is_win": bool(win), "mfe_r": 1.0, "bars_held": 4,
           "hour": i % 24, "famiglia": famiglia, "feats": feats,
           "run_end": "2026-09-24", "interval": "15m"}
    if passed is not None:
        row["passed"] = bool(passed)
    return row


def _righe(n, seed, predittiva=True, quota_bocciate=0.0):
    """Se `predittiva`, rsi basso -> vince l'80%, rsi alto -> il 25%. Altrimenti
    esiti a moneta (45%) senza legame con le variabili. Con `quota_bocciate` > 0
    quella frazione di righe porta `passed: False` (spec bocciate dal gate, come
    nel dataset dal 24 set 2026); le altre non hanno il campo (righe vecchie)."""
    rng = np.random.RandomState(seed)
    out = []
    for i in range(n):
        rsi = rng.uniform(10, 90)
        pw = (0.8 if rsi < 40 else 0.25) if predittiva else 0.45
        win = rng.rand() < pw
        pnl = rng.uniform(0.005, 0.03) if win else -rng.uniform(0.005, 0.02)
        bocciata = rng.rand() < quota_bocciate
        out.append(_riga(i, rsi, win, pnl,
                         direction="long" if rng.rand() < 0.5 else "short",
                         famiglia="reversion" if i % 2 else "momentum",
                         regime=REGIMI[rng.randint(4)],
                         passed=False if bocciata else None,
                         feats_extra={"adx": rng.uniform(10, 50), "stoch_k": rng.uniform(0, 100),
                                      "bb_pos": rng.uniform(0, 1), "vol_ratio": rng.uniform(0.5, 2),
                                      "market_up": float(rng.rand() < 0.5)}))
    return out


def _idx(nome):
    return sel.VARIABILI.index(nome)


# ---- vettore -------------------------------------------------------------- #
def test_vettore_segue_l_ordine_delle_variabili():
    v = sel.vettore(_riga(0, 30.0, True, 0.01, regime="bull_trending"))
    assert v is not None and len(v) == len(sel.VARIABILI) == 18
    assert v[_idx("rsi")] == 30.0
    assert v[_idx("is_long")] == 1.0
    # ora 0 -> seno 0, coseno 1
    assert v[_idx("hour_sin")] == pytest.approx(0.0)
    assert v[_idx("hour_cos")] == pytest.approx(1.0)
    # long con mercato su (market_up 1) -> concorde, +1; bande al centro -> 0
    assert v[_idx("long_x_mercato")] == pytest.approx(1.0)
    assert v[_idx("long_x_banda")] == pytest.approx(0.0)
    assert (v[_idx("regime_bull")], v[_idx("regime_bear")], v[_idx("regime_incerto")]) == (1, 0, 0)


def test_vettore_interazioni_direzione_per_contesto():
    """+1 quando direzione e contesto concordano, -1 quando sono opposti, 0 se
    il contesto e' ignoto: e' quello che una logistica lineare non sa fare da sola."""
    long_giu = sel.vettore(_riga(0, 30.0, True, 0.01, feats_extra={"market_up": 0.0}))
    short_giu = sel.vettore(_riga(0, 30.0, True, 0.01, direction="short",
                                  feats_extra={"market_up": 0.0}))
    ignoto = sel.vettore(_riga(0, 30.0, True, 0.01, feats_extra={"market_up": None}))
    assert long_giu[_idx("long_x_mercato")] == pytest.approx(-1.0)
    assert short_giu[_idx("long_x_mercato")] == pytest.approx(1.0)
    assert ignoto[_idx("long_x_mercato")] == pytest.approx(0.0)
    # bande, stessa formula: long sulla banda alta (bb_pos 1) = +1, short = -1.
    # Il SEGNO buono lo decide il modello (la reversion vorra' il coefficiente
    # negativo, il momentum positivo): qui conta solo che long e short siano
    # opposti a parita' di contesto.
    long_alto = sel.vettore(_riga(0, 30.0, True, 0.01, feats_extra={"bb_pos": 1.0}))
    short_alto = sel.vettore(_riga(0, 30.0, True, 0.01, direction="short",
                                   feats_extra={"bb_pos": 1.0}))
    assert long_alto[_idx("long_x_banda")] == pytest.approx(1.0)
    assert short_alto[_idx("long_x_banda")] == pytest.approx(-1.0)
    senza_bande = sel.vettore(_riga(0, 30.0, True, 0.01, feats_extra={"bb_pos": None}))
    assert senza_bande[_idx("long_x_banda")] == pytest.approx(0.0)


def test_vettore_dummy_del_regime():
    dummy = ("regime_bull", "regime_bear", "regime_incerto")

    def d(row):
        v = sel.vettore(row)
        return tuple(v[_idx(k)] for k in dummy)

    assert d(_riga(0, 30.0, True, 0.01, regime="bull_trending")) == (1, 0, 0)
    assert d(_riga(0, 30.0, True, 0.01, regime="bear_trending")) == (0, 1, 0)
    assert d(_riga(0, 30.0, True, 0.01, regime="high_uncertainty")) == (0, 0, 1)
    assert d(_riga(0, 30.0, True, 0.01, regime="sideways")) == (0, 0, 0)
    # il gate scrive str(enum): puo' arrivare col prefisso della classe
    assert d(_riga(0, 30.0, True, 0.01, regime="Regime.BEAR_TRENDING")) == (0, 1, 0)


def test_vettore_regime_mancante_non_scarta():
    """Regime assente, None o sconosciuto = sideways: la riga resta usabile con
    le tre dummy a 0, non si scarta un trade per un'etichetta."""
    senza = _riga(0, 30.0, True, 0.01)
    del senza["regime"]
    nullo = _riga(0, 30.0, True, 0.01, regime=None)
    strano = _riga(0, 30.0, True, 0.01, regime="trend")
    for r in (senza, nullo, strano):
        v = sel.vettore(r)
        assert v is not None and len(v) == len(sel.VARIABILI)
        assert (v[_idx("regime_bull")], v[_idx("regime_bear")], v[_idx("regime_incerto")]) == (0, 0, 0)
    # e si addestra/predice senza problemi anche quando NESSUNA riga ha il regime
    righe = _righe(300, seed=21)
    for r in righe:
        del r["regime"]
    m = sel.addestra(righe)
    assert all(m["coef"][_idx(k)] == 0.0 for k in ("regime_bull", "regime_bear", "regime_incerto"))
    assert 0.0 < sel.prob(m, righe[0]) < 1.0


def test_vettore_short_e_ora_derivata_da_entry_ts():
    r = _riga(0, 30.0, True, 0.01, direction="short")
    del r["hour"]
    r["entry_ts"] = 1_649_980_800.0 + 6 * 3600   # le 06:00 UTC del 15 apr 2022 (mezzanotte + 6 h)
    v = sel.vettore(r)
    assert v[sel.VARIABILI.index("is_long")] == 0.0
    assert v[sel.VARIABILI.index("hour_sin")] == pytest.approx(1.0)   # sin(pi/2)
    assert v[sel.VARIABILI.index("hour_cos")] == pytest.approx(0.0, abs=1e-9)


def test_vettore_manca_una_obbligatoria_e_scarta():
    """Senza rsi non c'e' una condizione da imparare: None, non un valore inventato."""
    r = _riga(0, 30.0, True, 0.01)
    r["feats"]["rsi"] = None
    assert sel.vettore(r) is None
    r2 = _riga(0, 30.0, True, 0.01)
    del r2["feats"]["stop_pct"]
    assert sel.vettore(r2) is None
    r3 = _riga(0, 30.0, True, 0.01)
    r3["feats"] = None
    assert sel.vettore(r3) is None
    r4 = _riga(0, 30.0, True, 0.01, direction="boh")
    assert sel.vettore(r4) is None


def test_vettore_opzionali_prendono_il_neutro():
    r = _riga(0, 30.0, True, 0.01)
    r["feats"].update({"market_up": None, "bb_pos": None, "vol_ratio": None})
    v = sel.vettore(r)
    assert v[sel.VARIABILI.index("market_up")] == 0.5
    assert v[sel.VARIABILI.index("bb_pos")] == 0.5
    assert v[sel.VARIABILI.index("vol_ratio")] == 1.0


# ---- regressione logistica ------------------------------------------------ #
def test_addestra_ritrova_il_segno_su_dati_separabili():
    """rsi basso vince: il coefficiente di rsi deve essere negativo e dominare; e
    la probabilita' deve scendere monotonamente con rsi."""
    righe = _righe(1500, seed=3)
    m = sel.addestra(righe)
    assert m["n"] == 1500 and len(m["coef"]) == len(sel.VARIABILI)
    coef = dict(zip(m["variabili"], m["coef"]))
    assert coef["rsi"] < 0
    assert abs(coef["rsi"]) == max(abs(c) for c in m["coef"])
    ps = [sel.prob(m, _riga(0, rsi, True, 0.01)) for rsi in (15, 30, 45, 60, 75, 90)]
    assert all(a > b for a, b in zip(ps, ps[1:]))
    assert 0.0 < ps[-1] < 0.5 < ps[0] < 1.0
    # serializzabile e deterministico
    json.dumps(m)
    assert sel.addestra(righe) == m


def test_addestra_con_variabile_costante():
    """r1 e' uguale in tutte le righe: scala 0 -> scala 1, coefficiente ~0, e le
    probabilita' restano finite e sensate. Una colonna piatta non deve rompere
    la standardizzazione ne' spostare il modello."""
    righe = _righe(800, seed=13)
    assert len({r["feats"]["r1"] for r in righe}) == 1
    m = sel.addestra(righe)
    assert m["scala"][_idx("r1")] == 1.0
    assert abs(m["coef"][_idx("r1")]) < 1e-6
    assert all(np.isfinite(m["coef"])) and np.isfinite(m["intercetta"])
    ps = [sel.prob(m, r) for r in righe[:50]]
    assert all(0.0 < p < 1.0 for p in ps)
    # cambiare il valore costante non cambia la stima: il coefficiente e' zero
    r = dict(righe[0], feats=dict(righe[0]["feats"], r1=5.0))
    assert sel.prob(m, r) == pytest.approx(sel.prob(m, righe[0]), abs=1e-6)
    json.dumps(m)


def test_addestra_con_una_sola_classe_non_esplode():
    righe = [_riga(i, 30.0, True, 0.01) for i in range(30)]
    m = sel.addestra(righe)
    assert all(c == 0.0 for c in m["coef"])
    assert 0.9 < sel.prob(m, righe[0]) < 1.0
    assert sel.addestra([])["n"] == 0


def test_prob_fail_open():
    assert sel.prob(None, _riga(0, 30.0, True, 0.01)) is None
    m = sel.addestra(_righe(200, seed=1))
    r = _riga(0, 30.0, True, 0.01)
    r["feats"]["adx"] = "boh"
    assert sel.prob(m, r) is None


def test_regolarizzazione_forte_stringe_i_coefficienti():
    righe = _righe(600, seed=4)
    lasco = sel.addestra(righe, lam=0.01)
    stretto = sel.addestra(righe, lam=1000.0)
    assert sum(abs(c) for c in stretto["coef"]) < sum(abs(c) for c in lasco["coef"])


def test_size_da_p_e_dentro_i_limiti():
    assert sel.size_da_p(0.5, 0.5) == 0.5
    assert sel.size_da_p(0.9, 0.5) == 1.25
    assert sel.size_da_p(0.6, 0.5) == pytest.approx(0.7)


# ---- walk-forward --------------------------------------------------------- #
def test_walk_forward_batte_quando_la_variabile_predice():
    wf = sel.walk_forward(_righe(3000, seed=11))
    assert wf["verdetto"] == sel.BATTE
    assert wf["vittorie"] >= 2 and len(wf["finestre"]) == 3
    assert wf["n_permutazioni"] == sel.N_PERMUTAZIONI == 200
    for f in wf["finestre"]:
        assert not f["insufficiente"]
        assert f["train_n"] >= 500
        assert f["soglia"] in sel.SOGLIE
        # il test e' DOPO il train, e il train cresce (finestra espansiva)
        assert f["train_a"] <= f["test_da"]
        assert f["selettore"]["n"] <= f["baseline"]["n"]
        assert 0.0 <= f["p_perm"] <= 1.0 and f["soglia_perm"] is not None
        if f["batte"]:
            # con un segnale vero quasi nessuna permutazione fa altrettanto
            assert f["p_perm"] <= 0.05
            assert f["selezione"]["metro"] > f["soglia_perm"]
            assert f["selezione"]["metro"] > f["baseline"]["metro"]
    assert [f["train_n"] for f in wf["finestre"]] == sorted(f["train_n"] for f in wf["finestre"])
    assert wf["modello"] is not None and wf["soglia_consigliata"] in sel.SOGLIE
    json.dumps(wf)
    # deterministico: le permutazioni hanno seme fisso
    assert sel.walk_forward(_righe(3000, seed=11)) == wf


@pytest.mark.parametrize("seed", [7, 70, 700])
def test_walk_forward_su_esiti_casuali_non_batte(seed):
    """Esiti a moneta: prima dell'audit del 24 set 2026 il selettore vinceva
    2 finestre su 3 una volta su due. Col test di permutazione deve dire
    «non batte» (o al piu' «insufficiente»), qualunque sia il seme."""
    wf = sel.walk_forward(_righe(3000, seed=seed, predittiva=False))
    assert wf["verdetto"] in (sel.NON_BATTE, sel.INSUFFICIENTE)
    assert wf["verdetto"] != sel.INSUFFICIENTE
    for f in wf["finestre"]:
        assert f["baseline"]["n"] > 0
        assert f["baseline"]["dd"] >= 0 and f["selettore"]["dd"] >= 0
        assert f["p_perm"] is not None
        # se non batte, o non supera la baseline o non supera i permutati
        if not f["batte"]:
            assert (f["selezione"]["metro"] <= f["baseline"]["metro"]
                    or f["selezione"]["metro"] <= f["soglia_perm"])
    json.dumps(wf)


def test_walk_forward_addestra_su_tutte_e_riporta_per_passed():
    """Le righe bocciate entrano nel train e nel test; ogni finestra riporta le
    misure anche separate per `passed`, e le due parti sommano all'intero."""
    righe = _righe(3000, seed=17, quota_bocciate=0.3)
    wf = sel.walk_forward(righe)
    assert wf["n_righe"] == 3000
    assert wf["n_passate"] + wf["n_bocciate"] == 3000
    assert 600 < wf["n_bocciate"] < 1200
    for f in wf["finestre"]:
        sp, sb = f["solo_passate"], f["solo_bocciate"]
        assert sp["n"] + sb["n"] == f["baseline"]["n"]
        assert sb["n"] > 0 and sp["n"] > 0
        assert sp["baseline"]["n"] == sp["n"] and sb["baseline"]["n"] == sb["n"]
        assert sp["selezione"]["n"] + sb["selezione"]["n"] == f["selezione"]["n"]
        assert sp["baseline"]["pnl"] + sb["baseline"]["pnl"] == pytest.approx(f["baseline"]["pnl"], abs=1e-5)
        for k in ("n", "pnl", "metro"):
            assert k in sp["baseline"] and k in sp["selezione"]
    # senza il campo (righe vecchie) e' tutto «passato»
    wf2 = sel.walk_forward(_righe(1500, seed=17), min_train=200)
    assert wf2["n_bocciate"] == 0
    assert all(f["solo_bocciate"]["n"] == 0 for f in wf2["finestre"])
    assert all(f["solo_bocciate"]["baseline"]["metro"] == 0.0 for f in wf2["finestre"])
    json.dumps(wf)


def test_walk_forward_campione_insufficiente():
    wf = sel.walk_forward(_righe(400, seed=2))
    assert wf["verdetto"] == sel.INSUFFICIENTE
    assert all(f["insufficiente"] for f in wf["finestre"])
    assert sel.walk_forward([])["verdetto"] == sel.INSUFFICIENTE
    # con un minimo piu' basso le stesse righe bastano
    assert sel.walk_forward(_righe(400, seed=2), min_train=100)["verdetto"] != sel.INSUFFICIENTE


def test_report_per_famiglia_raggruppa_e_include_tutte():
    rep = sel.report_per_famiglia(_righe(1200, seed=5), min_train=100)
    assert set(rep) == {"tutte", "reversion", "momentum"}
    assert rep["tutte"]["n_righe"] == 1200
    assert rep["reversion"]["n_righe"] + rep["momentum"]["n_righe"] == 1200
    assert rep["reversion"]["modello"]["famiglia"] == "reversion"


def test_drawdown():
    assert sel._drawdown(np.array([0.01, -0.02, 0.005, -0.01])) == pytest.approx(0.025)
    assert sel._drawdown(np.array([0.01, 0.02])) == 0.0
    assert sel._drawdown(np.zeros(0)) == 0.0


# ---- carica_righe ---------------------------------------------------------- #
def _scrivi(cartella, nome, righe):
    with open(os.path.join(cartella, nome), "w", encoding="utf-8") as f:
        for r in righe:
            f.write(r if isinstance(r, str) else json.dumps(r))
            f.write("\n")


def test_carica_righe_dedup_ultima_occorrenza_e_riga_rotta(tmp_path):
    a = _riga(0, 30.0, True, 0.01)
    b = _riga(1, 60.0, False, -0.01)
    a_bis = dict(a, pnl_pct=0.02)          # stesso trade, rivalutato il giorno dopo
    _scrivi(tmp_path, "2026-09-24_15m.jsonl", [a, b, "{questa riga e' rotta", ""])
    _scrivi(tmp_path, "2026-09-25_15m.jsonl", [a_bis, {"symbol": "X"}])
    righe = sel.carica_righe(str(tmp_path))
    assert len(righe) == 2
    per_chiave = {(r["symbol"], r["entry_ts"]): r for r in righe}
    assert per_chiave[(a["symbol"], a["entry_ts"])]["pnl_pct"] == 0.02
    assert sel.ULTIMA_LETTURA == {"file": 2, "scartate": 2, "duplicate": 1,
                                  "gemelle_fuse": 0, "righe": 2}
    # ordinate per tempo
    assert righe[0]["entry_ts"] < righe[1]["entry_ts"]


def test_carica_righe_fonde_le_coppie_gemelle(tmp_path):
    """Stessa coin, strategie diverse, stesso ingresso nello stesso verso: e' UN
    trade, non tre. Si tiene l'ultima riga e si conta in `gemelle_fuse`. Lo
    stesso ingresso nel verso opposto e' un altro trade. Se una delle gemelle
    era di una spec passata, la riga fusa resta passata."""
    a = _riga(0, 30.0, True, 0.01, strategy="rev_a", passed=True)
    a2 = _riga(0, 30.0, True, 0.012, strategy="rev_b", passed=False)   # gemella bocciata
    a3 = _riga(0, 30.0, True, 0.011, strategy="rev_c")                 # gemella, riga vecchia
    a_short = _riga(0, 30.0, False, -0.01, strategy="rev_a", direction="short")
    b = _riga(1, 60.0, False, -0.01, strategy="rev_a")
    _scrivi(tmp_path, "2026-09-24_15m.jsonl", [a, a2, a3, a_short, b])
    righe = sel.carica_righe(str(tmp_path))
    assert len(righe) == 3
    assert sel.ULTIMA_LETTURA == {"file": 1, "scartate": 0, "duplicate": 0,
                                  "gemelle_fuse": 2, "righe": 3}
    fuse = [r for r in righe if r["entry_ts"] == a["entry_ts"] and r["direction"] == "long"]
    assert len(fuse) == 1 and fuse[0]["strategy"] == "rev_c" and fuse[0]["pnl_pct"] == 0.011
    assert sel._passata(fuse[0])
    # ordine inverso: la bocciata arriva per ultima ma il trade era di una passata
    _scrivi(tmp_path, "2026-09-24_15m.jsonl", [a3, a, a2])
    righe = sel.carica_righe(str(tmp_path))
    assert len(righe) == 1 and righe[0]["strategy"] == "rev_b" and righe[0]["passed"] is True
    # senza direzione non e' un trade identificabile: scartata
    c = _riga(2, 30.0, True, 0.01)
    del c["direction"]
    _scrivi(tmp_path, "2026-09-24_15m.jsonl", [c])
    assert sel.carica_righe(str(tmp_path)) == []
    assert sel.ULTIMA_LETTURA["scartate"] == 1


def test_carica_righe_giorni_filtra_rispetto_al_piu_recente(tmp_path):
    righe = [_riga(i, 30.0, True, 0.01) for i in range(0, 40, 4)]   # ogni 24 h
    _scrivi(tmp_path, "2026-09-24_15m.jsonl", righe)
    assert len(sel.carica_righe(str(tmp_path))) == 10
    assert len(sel.carica_righe(str(tmp_path), giorni=3)) == 4
    assert sel.carica_righe(str(tmp_path / "vuota")) == []


# ---- lo script ------------------------------------------------------------ #
def test_report_cartella_vuota(tmp_path, capsys):
    rc = selettore_report.main(["--cartella", str(tmp_path)])
    out = capsys.readouterr().out
    assert rc == 0
    assert "nessun dataset: il gate lo scrive dal 24 set a ogni giro" in out
    assert "NON usa" in out


def test_report_cartella_piena(tmp_path, capsys):
    _scrivi(tmp_path, "2026-09-24_15m.jsonl", _righe(1500, seed=9, quota_bocciate=0.2))
    rc = selettore_report.main(["--cartella", str(tmp_path), "--min-train", "200"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "1500 trade da 1 file" in out and "gemelle fuse" in out
    assert "[tutte]" in out and "[reversion]" in out and "[momentum]" in out
    assert "VERDETTO: BATTE" in out
    assert "apri tutto:" in out and "selezione :" in out and "con size  :" in out
    assert "solo passate" in out and "solo bocciate" in out
    assert "di spec passate e" in out and "di bocciate" in out
    assert "p_perm" in out and "permutazioni" in out
    assert "rsi" in out and "intercetta" in out and "long_x_mercato" in out
    assert "NON usa ancora il selettore" in out
    assert "[firebase]" in out          # in test non e' connesso: lo dice


def test_report_da_env_dir(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(sel, "SELETTORE_DIR", str(tmp_path))
    assert selettore_report.main([]) == 0
    assert "nessun dataset" in capsys.readouterr().out
