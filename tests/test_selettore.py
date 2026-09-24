"""IL SELETTORE, PASSO 1 — il confronto offline non deve mentire.

Il disegno (docs/disegno_cervello.md, Punto 2) chiede un modello leggibile,
addestrato SOLO sui trade del gate, giudicato in walk-forward contro «apri
tutto». Qui si verifica che i pezzi facciano quello che dicono: il vettore
scarta cio' che non puo' inventare, la logistica ritrova il segno di un effetto
vero, il walk-forward dice «batte» quando c'e' un segnale e non crolla quando
non c'e', e sotto il campione minimo si ferma invece di dare un verdetto.
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
def _riga(i, rsi, win, pnl, direction="long", famiglia="reversion", feats_extra=None,
          t0=1_650_000_000.0):
    feats = {"rsi": rsi, "adx": 25.0, "stoch_k": 50.0, "atr_pct": 0.02, "dist_ema": 0.0,
             "bb_pos": 0.5, "vol_ratio": 1.0, "stop_pct": 0.02, "r1": 1.0, "market_up": 1.0}
    feats.update(feats_extra or {})
    return {"symbol": f"C{i % 7}USDT", "strategy": "strat", "direction": direction,
            "regime": "trend", "entry_ts": t0 + i * 6 * 3600.0, "pnl_pct": pnl,
            "pnl": pnl * 100, "is_win": bool(win), "mfe_r": 1.0, "bars_held": 4,
            "hour": i % 24, "famiglia": famiglia, "feats": feats,
            "run_end": "2026-09-24", "interval": "15m"}


def _righe(n, seed, predittiva=True):
    """Se `predittiva`, rsi basso -> vince l'80%, rsi alto -> il 25%. Altrimenti
    esiti a moneta (45%) senza legame con le variabili."""
    rng = np.random.RandomState(seed)
    out = []
    for i in range(n):
        rsi = rng.uniform(10, 90)
        pw = (0.8 if rsi < 40 else 0.25) if predittiva else 0.45
        win = rng.rand() < pw
        pnl = rng.uniform(0.005, 0.03) if win else -rng.uniform(0.005, 0.02)
        out.append(_riga(i, rsi, win, pnl,
                         direction="long" if rng.rand() < 0.5 else "short",
                         famiglia="reversion" if i % 2 else "momentum",
                         feats_extra={"adx": rng.uniform(10, 50), "stoch_k": rng.uniform(0, 100),
                                      "bb_pos": rng.uniform(0, 1), "vol_ratio": rng.uniform(0.5, 2),
                                      "market_up": float(rng.rand() < 0.5)}))
    return out


# ---- vettore -------------------------------------------------------------- #
def test_vettore_segue_l_ordine_delle_variabili():
    v = sel.vettore(_riga(0, 30.0, True, 0.01))
    assert v is not None and len(v) == len(sel.VARIABILI)
    assert v[sel.VARIABILI.index("rsi")] == 30.0
    assert v[sel.VARIABILI.index("is_long")] == 1.0
    # ora 0 -> seno 0, coseno 1
    assert v[sel.VARIABILI.index("hour_sin")] == pytest.approx(0.0)
    assert v[sel.VARIABILI.index("hour_cos")] == pytest.approx(1.0)


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
    for f in wf["finestre"]:
        assert not f["insufficiente"]
        assert f["train_n"] >= 500
        assert f["soglia"] in sel.SOGLIE
        # il test e' DOPO il train, e il train cresce (finestra espansiva)
        assert f["train_a"] <= f["test_da"]
        assert f["selettore"]["n"] <= f["baseline"]["n"]
    assert [f["train_n"] for f in wf["finestre"]] == sorted(f["train_n"] for f in wf["finestre"])
    assert wf["modello"] is not None and wf["soglia_consigliata"] in sel.SOGLIE
    json.dumps(wf)


def test_walk_forward_su_esiti_casuali_non_crasha_e_da_un_verdetto():
    wf = sel.walk_forward(_righe(3000, seed=7, predittiva=False))
    assert wf["verdetto"] in (sel.BATTE, sel.NON_BATTE, sel.INSUFFICIENTE)
    assert wf["verdetto"] != sel.INSUFFICIENTE
    for f in wf["finestre"]:
        assert f["baseline"]["n"] > 0
        assert f["baseline"]["dd"] >= 0 and f["selettore"]["dd"] >= 0
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
    assert sel.ULTIMA_LETTURA == {"file": 2, "scartate": 2, "duplicate": 1, "righe": 2}
    # ordinate per tempo
    assert righe[0]["entry_ts"] < righe[1]["entry_ts"]


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
    _scrivi(tmp_path, "2026-09-24_15m.jsonl", _righe(1500, seed=9))
    rc = selettore_report.main(["--cartella", str(tmp_path), "--min-train", "200"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "1500 trade da 1 file" in out
    assert "[tutte]" in out and "[reversion]" in out and "[momentum]" in out
    assert "VERDETTO: BATTE" in out
    assert "apri tutto:" in out and "selezione :" in out and "con size  :" in out
    assert "rsi" in out and "intercetta" in out
    assert "NON usa ancora il selettore" in out
    assert "[firebase]" in out          # in test non e' connesso: lo dice


def test_report_da_env_dir(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(sel, "SELETTORE_DIR", str(tmp_path))
    assert selettore_report.main([]) == 0
    assert "nessun dataset" in capsys.readouterr().out
