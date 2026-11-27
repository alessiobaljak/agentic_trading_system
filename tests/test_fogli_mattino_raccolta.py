"""I fogli del mattino (fatti gravi e voce 14) non partono se la raccolta delle notizie è vecchia (audit del 26 novembre 2026)."""
from datetime import datetime, timezone

import pytest

from research.notizie import raccolta
from research.programma7.misure_g1 import voce14_lettura as v14


def _giri(tmp_path, ultima: str):
    (tmp_path / "giri.csv").write_text("ora,fonte,articoli,nuovi,nota\n"
                                       "2026-11-27 00:18,coindesk,25,3,\n"
                                       f"{ultima},coindesk,25,1,\n", encoding="utf-8")


def test_raccolta_vecchia_ferma_il_foglio(tmp_path, monkeypatch):
    _giri(tmp_path, "2026-11-27 00:18")
    monkeypatch.setattr(raccolta, "ARCHIVIO", tmp_path)
    with pytest.raises(SystemExit, match="lancia prima"):
        v14.raccolta_fresca(datetime(2026, 11, 27, 4, 18, tzinfo=timezone.utc))


def test_raccolta_fresca_lascia_partire(tmp_path, monkeypatch):
    _giri(tmp_path, "2026-11-27 04:20")
    monkeypatch.setattr(raccolta, "ARCHIVIO", tmp_path)
    assert v14.raccolta_fresca(datetime(2026, 11, 27, 4, 18, tzinfo=timezone.utc)).hour == 4
    # anche una raccolta di pochi minuti prima della fine della finestra va bene
    _giri(tmp_path, "2026-11-27 04:10")
    v14.raccolta_fresca(datetime(2026, 11, 27, 4, 18, tzinfo=timezone.utc))
