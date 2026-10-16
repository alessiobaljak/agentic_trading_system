"""Test del guardiano per la campagna del protocollo 3 (`research/PROTOCOLLO_3.md`, sezioni 0,
3 e 12): marcatore `{"tipo": "campagna", "simbolo": "BTC51"}`.

La sessione di ricerca vede solo il testo del protocollo 3, gli strumenti (in sola lettura),
i due file di configurazione del protocollo 3, la propria cartella e i dati di BTCUSDT.
Niente protocolli, lezioni, changelog o configurazioni delle edizioni precedenti, niente
cartelle di altre campagne (BTCUSDT compresa), niente vault, niente Wikipedia. Il via libera
alla validazione lo scrive solo il coordinamento.

Gli attrezzi sono quelli di `test_guardiano.py` (il guardiano lanciato come hook vero).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from research.src.tests.test_guardiano import (RIFIUTO, _bash, _esegui, _marcatore,
                                               _radice_finta, _read)


@pytest.fixture
def btc51(tmp_path: Path) -> Path:
    radice = _radice_finta(tmp_path)
    for cartella in ("research/campagne/BTC51/codice", "research/data/insample/BTC51"):
        (radice / cartella).mkdir(parents=True, exist_ok=True)
    (radice / "research" / "PROTOCOLLO_3.md").write_text("protocollo 3\n")
    (radice / "research" / "PROTOCOLLO.md").write_text("protocollo 1\n")
    (radice / "research" / "PROTOCOLLO_2.md").write_text("protocollo 2\n")
    (radice / "research" / "CHANGELOG.md").write_text("changelog\n")
    (radice / "research" / "lezioni" / "metodo.md").write_text("lezioni\n")
    (radice / "research" / "config" / "parametri.yaml").write_text("x: 1\n")
    (radice / "research" / "config" / "parametri_2.yaml").write_text("x: 2\n")
    (radice / "research" / "config" / "parametri_3.yaml").write_text("x: 3\n")
    (radice / "research" / "config" / "bot_3.md").write_text("bot\n")
    (radice / "research" / "campagne" / "BTC51" / "log.jsonl").write_text("")
    (radice / "research" / "campagne" / "BTC51" / "STATO.md").write_text("stato\n")
    (radice / "CLAUDE.md").write_text("istruzioni\n")
    (radice / ".gitignore").write_text("research/data/\n")
    _marcatore(radice, {"tipo": "campagna", "simbolo": "BTC51"})
    return radice


@pytest.mark.parametrize(
    "percorso, atteso",
    [
        # ammessi
        ("research/PROTOCOLLO_3.md", 0),
        ("research/config/parametri_3.yaml", 0),
        ("research/config/bot_3.md", 0),
        ("research/config/percorsi_vietati.txt", 0),
        ("research/src/motore.py", 0),
        ("research/src/tests/test_motore.py", 0),
        ("research/campagne/BTC51/log.jsonl", 0),
        ("research/campagne/BTC51/via_libera_validazione.md", 0),
        ("research/data/insample/BTCUSDT/x.zip", 0),
        ("research/.sessione", 0),
        ("CLAUDE.md", 0),
        (".gitignore", 0),
        (".claude/settings.json", 0),
        # vietati: le edizioni precedenti e i loro risultati
        ("research/PROTOCOLLO.md", 2),
        ("research/PROTOCOLLO_2.md", 2),
        ("research/CHANGELOG.md", 2),
        ("research/lezioni/metodo.md", 2),
        ("research/config/parametri.yaml", 2),
        ("research/config/parametri_2.yaml", 2),
        ("research/config/regole_dimensione.md", 2),
        ("research/campagne/BTCUSDT/log.jsonl", 2),
        ("research/campagne/ETHUSDT/log.jsonl", 2),
        ("research/vault/APERTURA.md", 2),
        ("research/vault/BTCUSDT-V10_vault.md", 2),
        ("research/collaudo_3/esiti.md", 2),
        # i dati: solo BTCUSDT, mai il simbolo della campagna, mai il vault
        ("research/data/insample/BTC51/x.zip", 2),
        ("research/data/insample/ETHUSDT/x.zip", 2),
        ("research/data/insample", 2),
        ("research/data/vault/BTCUSDT/x.zip", 2),
        # il resto del repo
        ("bot/config.py", 2),
        ("docs/state.md", 2),
        ("ops/results/0001.md", 2),
        (".env", 2),
    ],
)
def test_btc51_lettura(btc51, percorso, atteso):
    codice, err = _read(btc51, percorso)
    assert codice == atteso, err
    if atteso == 2:
        assert err.startswith(RIFIUTO)
        assert "sessione campagna BTC51" in err
        assert "PROTOCOLLO_3.md, sezioni 0, 3 e 12" in err


@pytest.mark.parametrize(
    "percorso, atteso",
    [
        ("research/campagne/BTC51/log.jsonl", 0),
        ("research/campagne/BTC51/codice/v001.json", 0),
        ("research/data/insample/BTCUSDT/nota.txt", 0),
        # sola lettura per la sessione di ricerca
        ("research/campagne/BTC51/via_libera_validazione.md", 2),
        ("research/PROTOCOLLO_3.md", 2),
        ("research/src/motore3.py", 2),
        ("research/src/statistica3.py", 2),
        ("research/src/tests/test_nuovo.py", 2),
        ("research/config/parametri_3.yaml", 2),
        ("research/config/bot_3.md", 2),
        ("research/src/guardiano.py", 2),
        ("research/.sessione", 2),
        ("CLAUDE.md", 2),
        (".gitignore", 2),
    ],
)
def test_btc51_scrittura(btc51, percorso, atteso):
    codice, err = _esegui(btc51, "Write", {"file_path": percorso, "content": "x"})
    assert codice == atteso, err


def test_btc51_non_cancella_la_cartella_con_il_via_libera(btc51):
    (btc51 / "research" / "campagne" / "BTC51" / "via_libera_validazione.md").write_text("si'\n")
    assert _bash(btc51, "rm -rf research/campagne/BTC51")[0] == 2
    assert _bash(btc51, "rm research/campagne/BTC51/log.jsonl")[0] == 0


def test_btc51_comandi(btc51):
    assert _bash(btc51, "cat research/PROTOCOLLO_3.md")[0] == 0
    assert _bash(btc51, "cat research/PROTOCOLLO.md")[0] == 2
    assert _bash(btc51, "cat research/campagne/BTCUSDT/log.jsonl")[0] == 2
    assert _bash(btc51, "ls research/data/insample/BTCUSDT")[0] == 0
    assert _bash(btc51, "echo x > research/src/motore3.py")[0] == 2
    assert _bash(btc51, "echo x > research/campagne/BTC51/nota.md")[0] == 0


def test_btc51_branch(btc51):
    assert _bash(btc51, "git status")[0] == 0
    assert _bash(btc51, "git log research/campagna/BTCUSDT")[0] == 2
    assert _bash(btc51, "git log research/coordinamento")[0] == 2
    assert _bash(btc51, "git log --oneline -- research/campagne/BTCUSDT")[0] == 2


@pytest.mark.parametrize(
    "url, atteso",
    [
        ("https://arxiv.org/abs/1234.5678", 0),
        ("https://www.ssrn.com/abstract=1", 0),
        ("https://en.wikipedia.org/wiki/Bitcoin", 2),
        ("https://wikipedia.org/wiki/Momentum", 2),
    ],
)
def test_btc51_web(btc51, url, atteso):
    codice, err = _esegui(btc51, "WebFetch", {"url": url, "prompt": "x"})
    assert codice == atteso, err


def test_btc51_ricerca_web_senza_wikipedia(btc51):
    assert _esegui(btc51, "WebSearch", {"query": "momentum crypto"})[0] == 0
    assert _esegui(btc51, "WebSearch", {"query": "momentum site:wikipedia.org"})[0] == 2


def test_le_altre_campagne_non_cambiano(tmp_path):
    """Le regole del protocollo 3 valgono solo per BTC51: una campagna a moneta singola del
    primo protocollo legge ancora PROTOCOLLO.md e la sua cartella e scrive in src/."""
    radice = _radice_finta(tmp_path)
    (radice / "research" / "PROTOCOLLO.md").write_text("protocollo 1\n")
    _marcatore(radice, {"tipo": "campagna", "simbolo": "BTCUSDT"})
    assert _read(radice, "research/PROTOCOLLO.md")[0] == 0
    assert _read(radice, "research/campagne/BTCUSDT/log.jsonl")[0] == 0
    assert _esegui(radice, "Write", {"file_path": "research/src/nuovo.py", "content": "x"})[0] == 0
    assert _esegui(radice, "WebFetch", {"url": "https://en.wikipedia.org/wiki/Momentum", "prompt": "x"})[0] == 0
