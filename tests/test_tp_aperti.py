"""I TP delle posizioni aperte sono raggiungibili? (2 ott 2026)."""
import json
import time
from datetime import datetime, timedelta, timezone

import scripts.tp_aperti as tp


def _pos(lado="long", entry=100.0, stop_r=2.0, mults=(2, 4, 6)):
    R = stop_r  # in prezzo
    segno = 1 if lado == "long" else -1
    return {"symbol": "AUSDT", "strategy": "gen_a", "direction": lado, "entry_price": entry,
            "timeframe": "15m",
            "tp_ladder": [{"price": entry + segno * m * R, "r": m, "hit": False} for m in mults]}


def test_livelli_ricava_stop_e_tp_in_percentuale():
    lv = tp.livelli(_pos())
    assert abs(lv["stop_pct"] - 0.02) < 1e-12
    assert [round(t["pct"], 4) for t in lv["tps"]] == [0.04, 0.08, 0.12]
    short = tp.livelli(_pos("short"))
    assert short["lato"] == "short" and abs(short["tps"][0]["pct"] - 0.04) < 1e-12
    assert tp.livelli({"entry_price": 1, "direction": "long"}) is None
    # RTDB puo' restituire la lista come oggetto con chiavi numeriche
    p = _pos()
    p["tp_ladder"] = {str(i): v for i, v in enumerate(p["tp_ladder"])}
    assert tp.livelli(p)["tps"][2]["r"] == 6


def test_raggiungibilita_su_serie_costruita():
    # sale dello 0,5% a candela: in 96 candele arriva lontano, lo stop mai
    c = [(100 * 1.005 ** i * 1.001, 100 * 1.005 ** i * 0.999, 100 * 1.005 ** i) for i in range(300)]
    r = tp.raggiungibilita(c, "long", 0.02, [0.04, 0.08, 0.8], orizzonte=96)
    assert r["n"] == 300 - 96
    assert r["prima_dello_stop"][0] == 1.0 and r["prima_dello_stop"][1] == 1.0
    assert r["prima_dello_stop"][2] == 0.0          # +80% non arriva in 96 candele (1,005^96 = +61%)
    # lo short sulla stessa serie prende sempre lo stop prima
    s = tp.raggiungibilita(c, "short", 0.02, [0.04], orizzonte=96)
    assert s["prima_dello_stop"][0] == 0.0 and s["comunque"][0] == 0.0


def test_stop_e_tp_nella_stessa_candela_vale_lo_stop():
    c = [(100, 100, 100), (105, 97, 100)] + [(100, 100, 100)] * 5
    r = tp.raggiungibilita(c, "long", 0.02, [0.04], orizzonte=5)
    assert r["prima_dello_stop"][0] == 0.0 and r["comunque"][0] > 0


def test_quote_paper():
    q = tp.quote_paper([{"scale_stage_reached": 0}, {"scale_stage_reached": 1},
                        {"scale_stage_reached": 3}, {"scale_stage_reached": 0}, {}])
    assert q == [0.5, 0.25, 0.25]


def test_stampa_senza_cache_e_senza_posizioni(capsys):
    tp.stampa({}, [])
    assert "nessuna posizione aperta" in capsys.readouterr().out
    tp.stampa({"AUSDT": _pos()}, [], carica=lambda s, t: None)
    out = capsys.readouterr().out
    assert "stop 2.0%" in out and "TP3 6R = 12.0%" in out and "storia non in cache" in out
    c = [(100 * 1.001, 100 * 0.999, 100)] * 300
    tp.stampa({"AUSDT": _pos()}, [{"scale_stage_reached": 1}], carica=lambda s, t: c)
    out = capsys.readouterr().out
    assert "TP prima dello stop" in out and "Nel paper" in out


def test_carica_cache_preferisce_il_file_che_copre_i_giorni(tmp_path, monkeypatch):
    """La sezione A5 di mfe_report scrive nella cache file corti con la fine piu'
    recente: non devono vincere sul file lungo del gate (2 ott 2026, ops 0419)."""
    from backtesting import data_loader as dl
    from scripts import tp_aperti as tp

    monkeypatch.setattr(dl, "_CACHE_DIR", str(tmp_path))
    oggi = datetime.now(timezone.utc)
    t0 = int(time.time()) // 900 * 900
    righe = [[(t0 - 900 * k) * 1000, 1.0, 1.0, 1.0, 1.0, 1.0] for k in range(120 * 96, 0, -1)]
    g = lambda d: (oggi + timedelta(days=d)).strftime("%Y-%m-%d")  # noqa: E731
    (tmp_path / f"AUSDT_15m_2022-01-01_{g(0)}.json").write_text(
        json.dumps({"source": "binance", "rows": righe}))
    (tmp_path / f"AUSDT_15m_{g(-20)}_{g(1)}.json").write_text(
        json.dumps({"source": "binance", "rows": righe[-20 * 96:]}))
    c = tp.carica_cache("AUSDT", "15m", 60)
    assert len(c) == 60 * 96 + tp.ORIZZONTE
