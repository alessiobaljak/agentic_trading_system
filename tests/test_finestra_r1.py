"""LA FINESTRA DI R1 (1 ott 2026): finche' R1 e' attivo il giro del gate delle
12 UTC si salta; R1 lo sa e conta il giro dopo; senza R1 tutto come prima."""
import inspect
from datetime import datetime, timezone

from bot.core import finestra_r1 as fr
import scripts.replay_gate as rv


def _ts(ora, minuto=0):
    return datetime(2026, 10, 2, ora, minuto, tzinfo=timezone.utc).timestamp()


def test_si_salta_solo_alle_12_utc_e_solo_con_r1_attivo(tmp_path, monkeypatch):
    flag = tmp_path / "attivo"
    assert fr.giro_saltato_per_r1(_ts(12, 1), str(flag)) is None      # R1 non attivo
    flag.write_text("1")
    assert "SALTATO" in fr.giro_saltato_per_r1(_ts(12, 1), str(flag))
    assert fr.giro_saltato_per_r1(_ts(15, 0), str(flag)) is None
    assert fr.giro_saltato_per_r1(_ts(9, 0), str(flag)) is None
    monkeypatch.setenv("R1_SALTA_GIRO", "0")
    assert fr.giro_saltato_per_r1(_ts(12, 1), str(flag)) is None      # spento a mano


def test_optimize_e_discovery_saltano_per_primo(monkeypatch, capsys):
    import scripts.discover_strategies as d
    import scripts.optimize as op
    for mod in (op, d):
        src = inspect.getsource(mod.main)
        assert src.index("giro_saltato_per_r1") < src.index("argparse") if "argparse" in src else True
    monkeypatch.setattr(fr, "giro_saltato_per_r1", lambda *a, **k: "[gate] giro SALTATO")
    assert op.main() == 0 and d.main() == 0
    assert capsys.readouterr().out.count("SALTATO") == 2


def test_r1_conta_il_giro_dopo_quello_saltato(tmp_path, monkeypatch):
    flag = tmp_path / "attivo"
    flag.write_text("1")
    monkeypatch.setattr(rv, "FILE_ATTIVO", str(flag))
    monkeypatch.setattr(rv, "giro_in_corso", lambda *a, **k: [])
    monkeypatch.setattr(rv, "servizio_gate_attivo", lambda: False)
    adesso = _ts(11, 50)
    monkeypatch.setattr(rv.time, "time", lambda: adesso)
    monkeypatch.setattr(rv, "secondi_al_prossimo_giro", lambda ora=None: _ts(12) - adesso)
    assert rv.gate_in_arrivo(40 * 60) is None              # il giro delle 12 non conta
    flag.unlink()
    assert "fra 10 minuti" in rv.gate_in_arrivo(40 * 60)   # senza R1, come prima


def test_nell_ora_saltata_un_gate_di_passaggio_si_ricontrolla(tmp_path, monkeypatch):
    flag = tmp_path / "attivo"
    flag.write_text("1")
    monkeypatch.setattr(rv, "FILE_ATTIVO", str(flag))
    monkeypatch.setattr(rv, "RICONTROLLO_SALTATO_S", 0.0)
    monkeypatch.setattr(rv, "secondi_al_prossimo_giro", lambda ora=None: None)
    monkeypatch.setattr(rv, "servizio_gate_attivo", lambda: False)
    monkeypatch.setattr(rv.time, "time", lambda: _ts(12, 0))
    visti = iter([[123], []])                               # c'e', poi non c'e' piu'
    monkeypatch.setattr(rv, "giro_in_corso", lambda *a, **k: next(visti))
    assert rv.gate_in_arrivo(600) is None
    monkeypatch.setattr(rv, "giro_in_corso", lambda *a, **k: [123])   # un giro vero che sfora
    assert "in corso" in rv.gate_in_arrivo(600)
