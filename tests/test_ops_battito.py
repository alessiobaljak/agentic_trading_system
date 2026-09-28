"""
IL BATTITO DELL'AGENTE OPS SU FIREBASE (28 set 2026).

Il battito dell'agente viveva solo in `ops/heartbeat.md` (git): la dashboard e il
controllo orario non potevano dire se il canale ops era vivo. Ora
`write_heartbeat` scrive anche `rtdb:/ops/battito = {at, pendenti, ramo}` col
client del progetto, e il controllo pubblica `salute.ops_battito_at/_eta_s` con
l'anomalia OPS_FERMO oltre 3 ore.

Il vincolo che conta di piu': il battito NON deve poter fermare ne' rallentare
l'agente (gira ogni minuto da un timer systemd). Quindi: import pigro (niente
Firebase importato all'avvio), ogni errore stampato e ignorato, un tetto di tempo.
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
from types import SimpleNamespace

import pytest

import bot.core.firebase_client as fc
from tests.test_controllo import NOW, _codici, _doc, _fb

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class _FintoFirebase:
    def __init__(self, esito=True, errore: Exception | None = None, blocca: threading.Event | None = None):
        self.scritti: dict = {}
        self.esito, self.errore, self.blocca = esito, errore, blocca

    def set_rtdb(self, path, data):
        if self.blocca is not None:
            self.blocca.wait(5)
        if self.errore:
            raise self.errore
        self.scritti[path] = data
        return self.esito


@pytest.fixture
def ops(tmp_path, monkeypatch):
    import scripts.ops_agent as mod
    monkeypatch.setattr(mod, "HEARTBEAT", str(tmp_path / "heartbeat.md"))
    return mod


# --------------------------------------------------------------------------- #
# 1. l'agente scrive il battito, fail-open                                      #
# --------------------------------------------------------------------------- #
def test_write_heartbeat_scrive_anche_su_firebase(ops, monkeypatch, tmp_path):
    finto = _FintoFirebase()
    monkeypatch.setattr(fc, "get_firebase", lambda: finto)
    ops.write_heartbeat("mio-ramo", 2, 1_700_000_000.0)
    assert finto.scritti == {"/ops/battito": {"at": 1_700_000_000.0, "pendenti": 2, "ramo": "mio-ramo"}}
    assert "mio-ramo" in (tmp_path / "heartbeat.md").read_text()


def test_un_errore_di_firebase_non_ferma_l_agente(ops, monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(fc, "get_firebase", lambda: _FintoFirebase(errore=RuntimeError("credenziali")))
    ops.write_heartbeat("r", 0, 1_700_000_000.0)            # nessuna eccezione
    assert "battito su Firebase non scritto (credenziali)" in capsys.readouterr().out
    assert (tmp_path / "heartbeat.md").exists()             # il file in git c'e' lo stesso

    def _rotto():
        raise ImportError("firebase_admin assente")
    monkeypatch.setattr(fc, "get_firebase", _rotto)
    ops.write_heartbeat("r", 0, 1_700_000_000.0)
    assert "firebase_admin assente" in capsys.readouterr().out


def test_un_client_non_collegato_lo_dice(ops, monkeypatch, capsys):
    monkeypatch.setattr(fc, "get_firebase", lambda: _FintoFirebase(esito=False))
    ops.battito_firebase("r", 0, 1.0)
    assert "client non collegato" in capsys.readouterr().out


def test_un_firebase_appeso_non_trattiene_l_agente(ops, monkeypatch, capsys):
    ferma = threading.Event()
    monkeypatch.setattr(fc, "get_firebase", lambda: _FintoFirebase(blocca=ferma))
    import time
    t0 = time.time()
    ops.battito_firebase("r", 0, 1.0, timeout_s=0.2)
    assert time.time() - t0 < 2
    assert "nessuna risposta entro 0.2s" in capsys.readouterr().out
    ferma.set()


def test_l_agente_non_importa_firebase_all_avvio():
    """L'agente gira ogni minuto: importarlo non deve tirarsi dietro Firebase ne'
    la configurazione del bot (il battito serve una volta l'ora)."""
    codice = ("import sys, scripts.ops_agent; "
              "print(any(m in sys.modules for m in ('bot.core.firebase_client', 'firebase_admin', "
              "'bot.config')))")
    out = subprocess.run([sys.executable, "-c", codice], cwd=ROOT, capture_output=True,
                         text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "False"
    with open(os.path.join(ROOT, "scripts", "ops_agent.py"), encoding="utf-8") as f:
        righe = [r for r in f if r.startswith(("import ", "from "))]
    assert not any("firebase" in r or "bot." in r for r in righe), righe


# --------------------------------------------------------------------------- #
# 2. il controllo lo legge                                                      #
# --------------------------------------------------------------------------- #
def test_il_controllo_pubblica_il_battito_ops_e_la_voce_di_manca_sparisce():
    senza = _doc()
    assert senza["salute"]["ops_battito_at"] is None and senza["salute"]["ops_battito_eta_s"] is None
    assert "OPS_FERMO" not in _codici(senza)                # mai visto: non misurato, non fermo
    assert any(m["evidenza"] == "battito dell'agente ops" for m in senza["manca"])

    fb = _fb()
    fb.set_rtdb("/ops/battito", {"at": NOW - 720, "pendenti": 0, "ramo": "r"})
    con = _doc(fb=fb)
    assert con["salute"]["ops_battito_at"] == NOW - 720
    assert con["salute"]["ops_battito_eta_s"] == 720
    assert "OPS_FERMO" not in _codici(con)
    assert not any(m["evidenza"] == "battito dell'agente ops" for m in con["manca"])
    assert len(con["manca"]) == len(senza["manca"]) - 1
    assert "rtdb:/ops/battito" in con["salute"]["fonti"]


@pytest.mark.parametrize("eta, fermo", [(3 * 3600, False), (3 * 3600 + 1, True), (26 * 3600, True)])
def test_ops_fermo_oltre_tre_ore(eta, fermo):
    fb = _fb()
    fb.set_rtdb("/ops/battito", {"at": NOW - eta, "pendenti": 1, "ramo": "r"})
    doc = _doc(fb=fb)
    codici = _codici(doc)
    assert ("OPS_FERMO" in codici) is fermo
    if fermo:
        a = codici["OPS_FERMO"]
        assert a["famiglia"] == "sistema" and a["gravita"] == "giallo"
        assert a["valore"] == eta and a["soglia"] == 3 * 3600
        assert a["testo"].startswith("canale ops fermo da ") and "non vengono eseguite" in a["testo"]
        assert doc["meta"]["semaforo_sistema"] in ("giallo", "rosso")
        assert "canale ops fermo" in doc["salute"]["lettura"]
