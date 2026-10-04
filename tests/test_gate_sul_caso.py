"""G7, il gate sul prezzo casuale (4 ott 2026, si' del proprietario).

Cosa si protegge, su dati finti (niente rete, niente Firebase):
  * il rimescolamento: stesse candele (forma rispetto alla chiusura prima e
    volume), stessi orari, stesso prezzo di partenza e di arrivo, ordine
    diverso e ripetibile col seme;
  * le candidate: fisse col seme, nuove, col timeframe della passata nel nome;
  * l'unita' vera, col gate VERO su candele finte: la variante «caso» giudica
    davvero le candele rimescolate;
  * la regola scritta prima dei numeri (i tre esiti e il «troppo poche passate»);
  * nel lancio di R1: dopo R2 e prima delle unita' di R1, solo file nella
    cartella di R1, e l'esito che lo stampa.
"""
import datetime as dt
import os
from datetime import timezone

import pytest

import backtesting.data_loader as dl
from scripts import gate_sul_caso as g7
from scripts import replay_gate as rv

OGGI = dt.date.today().isoformat()


@pytest.fixture(autouse=True)
def _niente_gate_ne_file_veri(tmp_path, monkeypatch):
    monkeypatch.setattr(rv, "servizio_gate_attivo", lambda: False)
    monkeypatch.setattr(rv, "secondi_al_prossimo_giro", lambda ora=None: None)
    monkeypatch.setattr(rv, "giro_in_corso", lambda *a, **k: [])
    base = tmp_path / "replay_gate"
    for nome, rel in (("DIR_R1", ""), ("FILE_PIANO", "piano.json"), ("DIR_UNITA", "unita"),
                      ("FILE_ESITO", "ultimo.txt"), ("FILE_PID", "ultimo.pid"),
                      ("FILE_LOCK", "in_corso.lock"), ("FILE_ATTIVO", "attivo"),
                      ("DIR_R2", "r2"), ("DIR_UNITA_R2", "r2/unita"),
                      ("FILE_R2_ESITO", "r2/esito.json")):
        monkeypatch.setattr(rv, nome, str(base / rel) if rel else str(base))
    monkeypatch.setattr(dl, "_drop_older", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("la cache del gate non si tocca")))
    monkeypatch.setattr(dl, "funding_rate_for", lambda s: None)
    monkeypatch.setattr(g7, "G7_ATTIVO", True)
    rv._S.clear()
    yield
    rv._S.clear()


def _serie(sym, giorni=200, minuti=60):
    fino = dt.datetime(2026, 10, 1, tzinfo=timezone.utc)
    return dl._synthetic(fino - dt.timedelta(days=giorni), fino, interval_min=minuti, symbol=sym)


# --------------------------------------------------------------------------- #
# 1. il rimescolamento e le candidate                                          #
# --------------------------------------------------------------------------- #
def test_rimescola_stesse_candele_altro_ordine():
    c = _serie("AUSDT", giorni=30)
    r = g7.rimescola(c, 123)
    assert len(r) == len(c)
    assert [x.open_time for x in r] == [x.open_time for x in c]      # orari al loro posto
    assert r[0] == c[0]
    assert r[-1].close == pytest.approx(c[-1].close, rel=1e-9)       # stesso arrivo

    def pezzi(s):
        return sorted((round(b.close / a.close, 12), round(b.high / a.close, 12),
                       round(b.low / a.close, 12), b.volume) for a, b in zip(s, s[1:]))
    assert pezzi(r) == pezzi(c)                                       # stessi movimenti
    assert [x.close for x in r] != [x.close for x in c]               # ordine diverso
    assert [x.close for x in g7.rimescola(c, 123)] == [x.close for x in r]   # ripetibile
    assert [x.close for x in g7.rimescola(c, 124)] != [x.close for x in r]
    assert all(x.low <= min(x.open, x.close) and x.high >= max(x.open, x.close) for x in r)
    assert g7.seme_moneta("AUSDT") != g7.seme_moneta("BUSDT")


def test_candidate_fisse_nuove_e_a_un_ora():
    a = g7.candidate_g7(30, "1h")
    assert a == g7.candidate_g7(30, "1h")
    assert 0 < len(a) <= 30 and len({s["id"] for s in a}) == len(a)
    assert all(s["timeframe"] == "1h" for s in a)
    assert [s["id"] for s in a] != [s["id"] for s in g7.candidate_g7(30, "1h", seme=1)]


# --------------------------------------------------------------------------- #
# 2. l'unita' vera, col gate vero su candele finte                             #
# --------------------------------------------------------------------------- #
def test_l_unita_caso_giudica_le_candele_rimescolate(monkeypatch):
    serie = {s: _serie(s) for s in ("AUSDT", "BTCUSDT")}
    chiamate = []

    def carica(sym, interval, start, end, prefer="auto", **k):
        chiamate.append((sym, interval, end))
        return serie[sym]
    monkeypatch.setattr(rv, "load_candles", carica)
    specs = g7.candidate_g7(40, "1h")[:2]
    monkeypatch.setattr(g7, "candidate_g7", lambda **k: specs)
    visto = []
    vero_eval = rv.d.evaluate_spec

    def spia(opt, sym, candles, frame, spec, **kw):
        visto.append((candles[10].close, candles[-1].close, len(candles), kw.get("interval")))
        return vero_eval(opt, sym, candles, frame, spec, **kw)
    monkeypatch.setattr(rv.d, "evaluate_spec", spia)
    cfg = {"interval": "1h", "start": "2022-01-01", "source": "auto", "windows": 3,
           "candidate_per_data": 50}
    rv._init(cfg, OGGI, 0.0)
    rv._S["min_history"] = 1000
    vero = g7._una_unita_g7(("vero", "AUSDT"))
    caso = g7._una_unita_g7(("caso", "AUSDT"))
    assert vero["stato"] == caso["stato"] == "ok", (vero, caso)
    assert vero["n_candidate"] == caso["n_candidate"] == 2
    assert vero["data"] == "vero" and caso["data"] == "caso"
    (v10, vfine, vn, vi), (c10, cfine, cn, ci) = visto[0], visto[-1]
    assert vn == cn == len(serie["AUSDT"]) and vi == ci == "1h"      # tutte le candele, a 1 ora
    assert v10 != c10 and cfine == pytest.approx(vfine, rel=1e-9)    # rimescolate, stesso arrivo
    assert chiamate and all(end == OGGI and iv == "1h" for _s, iv, end in chiamate)


# --------------------------------------------------------------------------- #
# 3. la regola                                                                 #
# --------------------------------------------------------------------------- #
def _fatte(monete, passate_vero, passate_caso, prove=100):
    out = {}
    for v, tot in (("vero", passate_vero), ("caso", passate_caso)):
        for i, c in enumerate(monete):
            n = tot // len(monete) + (1 if i < tot % len(monete) else 0)
            out[(v, c)] = {"data": v, "coin": c, "stato": "ok", "n_candidate": prove,
                           "passate": [f"gen_{k}" for k in range(n)],
                           "per_criterio": {"total_return": prove - n}}
    return out


def test_la_regola_i_quattro_esiti():
    m = ["AUSDT", "BUSDT"]
    assert "RUMORE" in g7.lettura_g7(m, _fatte(m, 20, 10))["esito"]          # 0,5
    assert "FILTRA" in g7.lettura_g7(m, _fatte(m, 20, 4))["esito"]           # 0,2
    assert "fra un quinto e la meta'" in g7.lettura_g7(m, _fatte(m, 20, 6))["esito"]
    r = g7.lettura_g7(m, _fatte(m, 9, 0))
    assert "NON SI SA" in r["esito"] and "solo 9" in r["esito"]
    r = g7.lettura_g7(m, _fatte(m, 20, 4))
    assert r["vero"]["prove"] == 200 and r["vero"]["quota"] == pytest.approx(0.10)
    assert r["rapporto"] == pytest.approx(0.2)
    # incompleta: in corso; e il confronto e' a parita' di monete
    f = _fatte(m, 20, 4)
    del f[("caso", "BUSDT")]
    r = g7.lettura_g7(m, f)
    assert r["esito"] == "in corso" and r["a_pari"] == 1
    assert [c for v, c in g7.lavoro_g7(m, f)] == ["BUSDT"]
    assert g7.lavoro_g7(m, {})[:2] == [("vero", "AUSDT"), ("vero", "BUSDT")]   # prima il vero
    assert (g7.MIN_PASSATE_VERE, g7.SOGLIA_RUMORE, g7.SOGLIA_FILTRA) == (10, 0.5, 0.2)


# --------------------------------------------------------------------------- #
# 4. nel lancio di R1                                                          #
# --------------------------------------------------------------------------- #
def test_nel_lancio_dopo_r2_e_prima_di_r1(monkeypatch, capsys, tmp_path):
    import bot.core.firebase_client as fc
    monkeypatch.setattr(fc, "get_firebase", lambda: (_ for _ in ()).throw(
        AssertionError("niente Firebase")))
    monkeypatch.setattr(rv, "top_symbols_by_volume", lambda n: ["AUSDT", "BUSDT"])
    monkeypatch.setattr(rv, "_init", lambda *a: None)
    monkeypatch.setattr(rv, "_una_unita", lambda item: {"data": item[0], "coin": item[1],
                                                         "stato": "storia"})
    monkeypatch.setattr(rv, "_una_unita_r2", lambda item: {
        "data": item[0], "coin": item[1], "stato": "ok", "n_candidate": 50, "passate": [],
        "per_criterio": {"total_return": 50}})
    ordine = []

    def finta_g7(item):
        ordine.append(item)
        v, c = item
        n = 12 if v == "vero" else 1
        return {"data": v, "coin": c, "stato": "ok", "n_candidate": 100,
                "passate": [f"gen_{k}" for k in range(n)], "per_criterio": {"trades": 100 - n}}
    monkeypatch.setattr(g7, "_una_unita_g7", finta_g7)
    assert rv.main(["--workers", "1"]) == 0
    out = capsys.readouterr().out
    assert out.index("[r2] TARATURA") < out.index("[g7] IL GATE SUL PREZZO CASUALE") \
        < out.index("PROVA PICCOLA")
    assert ordine[:2] == [("vero", "AUSDT"), ("vero", "BUSDT")]
    assert "FILTRA" in out                                   # 2 su 200 contro 24 su 200
    assert os.path.exists(os.path.join(g7.dir_g7(), "esito.json"))
    scritti = [os.path.join(r, f) for r, _d, fs in os.walk(tmp_path) for f in fs]
    assert all(p.startswith(rv.DIR_R1) for p in scritti)
    # al lancio dopo non si rifa'
    ordine.clear()
    assert rv.main(["--workers", "1"]) == 0
    assert ordine == []
    # e l'esito lo stampa fra R2 e R1
    capsys.readouterr()
    assert rv.main(["--esito"]) == 0
    out = capsys.readouterr().out
    assert out.index("[r2] TARATURA") < out.index("[g7] IL GATE") < out.index("[r1] AVANZAMENTO")
    assert "24 passate su 200 prove = 12.00%" in out and "rapporto caso/vero: 0.08" in out


def test_niente_firebase_ne_registro():
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "scripts", "gate_sul_caso.py"), encoding="utf-8") as f:
        src = f.read()
    for vietato in ("get_firebase", "set_doc", "set_rtdb", "merge_into_registry", "_disc_one"):
        assert vietato not in src, vietato
