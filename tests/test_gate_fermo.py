"""L'interruttore della ricerca automatica del gate (bot/core/gate_fermo.py, 13 ott 2026)."""
import os

from bot.core import gate_fermo as gf


def test_senza_file_la_ricerca_gira(tmp_path, monkeypatch):
    monkeypatch.delenv("GATE_FERMO_IGNORA", raising=False)
    assert gf.ricerca_ferma(str(tmp_path / "gate_fermo")) is None


def test_con_il_file_la_ricerca_e_ferma_e_stampa_il_motivo(tmp_path, monkeypatch):
    monkeypatch.delenv("GATE_FERMO_IGNORA", raising=False)
    p = tmp_path / "gate_fermo"
    p.write_text("Ferma dal 13 ottobre.\n  Secondo rigo.\n", encoding="utf-8")
    frase = gf.ricerca_ferma(str(p))
    assert frase is not None and "FERMA" in frase
    assert "Ferma dal 13 ottobre. Secondo rigo." in frase


def test_la_variabile_d_ambiente_riaccende(tmp_path, monkeypatch):
    p = tmp_path / "gate_fermo"
    p.write_text("fermo", encoding="utf-8")
    monkeypatch.setenv("GATE_FERMO_IGNORA", "1")
    assert gf.ricerca_ferma(str(p)) is None


def test_il_file_del_repository_esiste_e_dice_il_motivo():
    # il file committato il 13 ott 2026: finche' c'e', il giro non parte
    assert os.path.exists(gf.FILE_FERMO)
    frase = gf.ricerca_ferma()
    assert frase is None or "FERMA" in frase  # None solo se GATE_FERMO_IGNORA e' impostata


def test_gli_script_del_gate_escono_subito(monkeypatch, tmp_path, capsys):
    import importlib
    p = tmp_path / "gate_fermo"
    p.write_text("prova", encoding="utf-8")
    monkeypatch.delenv("GATE_FERMO_IGNORA", raising=False)
    monkeypatch.setattr(gf, "FILE_FERMO", str(p))
    for modulo in ("scripts.optimize", "scripts.discover_strategies"):
        m = importlib.import_module(modulo)
        assert m.main() == 0
        assert "FERMA" in capsys.readouterr().out
