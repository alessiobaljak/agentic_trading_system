"""Test del guardiano per la campagna del protocollo 4 (`research/PROTOCOLLO_4.md`, sezioni 0,
3 e 12): marcatore `{"tipo": "campagna", "simbolo": "LINK6"}`.

La sessione di ricerca legge solo il testo del protocollo 4, i quattro file di configurazione
del protocollo 4, gli strumenti (in sola lettura), la propria cartella (con `risposte/` e il via
libera in sola lettura) e i dati di LINKUSDT. Niente campagne precedenti (anche
`campagne/LINKUSDT/`, la campagna del protocollo 1 sulla stessa moneta), niente protocolli o
configurazioni precedenti, niente vault, `altre_monete_3/`, `monete_di_controllo_4/`,
`collaudo_4/`, `universo/`, `docs/`, e niente dati delle monete di controllo, BTCUSDT compresa.

Gli attrezzi sono quelli di `test_guardiano.py` (il guardiano lanciato come hook vero).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from research.src import guardiano
from research.src.tests.test_guardiano import (RIFIUTO, _bash, _esegui, _marcatore,
                                               _radice_finta, _read)


@pytest.fixture
def link6(tmp_path: Path) -> Path:
    radice = _radice_finta(tmp_path)
    for cartella in ("research/campagne/LINK6/codice", "research/campagne/LINK6/risposte",
                     "research/campagne/LINK6/richieste", "research/campagne/LINKUSDT",
                     "research/data/insample/LINKUSDT", "research/data/insample/BTCUSDT"):
        (radice / cartella).mkdir(parents=True, exist_ok=True)
    for nome in ("PROTOCOLLO_4.md", "PROTOCOLLO_3.md", "PROTOCOLLO.md", "CHANGELOG.md", "protocollo_4_note.md"):
        (radice / "research" / nome).write_text("testo\n")
    for nome in ("parametri_4.yaml", "bot_4.md", "guida_pratica_4.md", "parametri_3.yaml", "bot_3.md"):
        (radice / "research" / "config" / nome).write_text("x\n")
    (radice / "research" / "campagne" / "LINK6" / "log.jsonl").write_text("")
    (radice / "research" / "campagne" / "LINK6" / "risposte" / "V-001.json").write_text("{}\n")
    (radice / "research" / "campagne" / "LINKUSDT" / "consegna.md").write_text("vecchia\n")
    (radice / "CLAUDE.md").write_text("istruzioni\n")
    (radice / ".gitignore").write_text("research/data/\n")
    _marcatore(radice, {"tipo": "campagna", "simbolo": "LINK6"})
    return radice


@pytest.mark.parametrize(
    "percorso, atteso",
    [
        # ammessi
        ("research/PROTOCOLLO_4.md", 0),
        ("research/config/parametri_4.yaml", 0),
        ("research/config/bot_4.md", 0),
        ("research/config/guida_pratica_4.md", 0),
        ("research/config/percorsi_vietati.txt", 0),
        ("research/src/motore3.py", 0),
        ("research/src/tests/test_motore3.py", 0),
        ("research/campagne/LINK6/log.jsonl", 0),
        ("research/campagne/LINK6/risposte/V-001.json", 0),
        ("research/campagne/LINK6/via_libera_validazione.md", 0),
        ("research/data/insample/LINKUSDT/x.zip", 0),
        ("research/.sessione", 0),
        ("CLAUDE.md", 0),
        (".gitignore", 0),
        (".claude/settings.json", 0),
        # vietati: protocolli, note e configurazioni precedenti
        ("research/PROTOCOLLO_3.md", 2),
        ("research/PROTOCOLLO.md", 2),
        ("research/protocollo_4_note.md", 2),
        ("research/CHANGELOG.md", 2),
        ("research/config/parametri_3.yaml", 2),
        ("research/config/bot_3.md", 2),
        ("research/config/guida_pratica_3.md", 2),
        # vietati: le campagne precedenti, anche quella del protocollo 1 su LINKUSDT
        ("research/campagne/LINKUSDT/consegna.md", 2),
        ("research/campagne/BTC51/lezioni.md", 2),
        ("research/campagne/BTC51/consegna.md", 2),
        # vietati: tutto quello che contiene fatti dal 2024 o risultati delle monete di controllo
        ("research/vault/APERTURA_3.md", 2),
        ("research/vault/BTC51_risultati.md", 2),
        ("research/altre_monete_3/risultati.md", 2),
        ("research/monete_di_controllo_4/V-001.json", 2),
        ("research/collaudo_4/esiti.md", 2),
        ("research/collaudo_3/esiti.md", 2),
        ("research/universo/candidate.csv", 2),
        ("docs/state.md", 2),
        ("docs/andremo_live.md", 2),
        # i dati: solo LINKUSDT, mai le monete di controllo, mai il vault
        ("research/data/insample/BTCUSDT/x.zip", 2),
        ("research/data/insample/ETHUSDT/x.zip", 2),
        ("research/data/insample/MATICUSDT/x.zip", 2),
        ("research/data/insample/LINK6/x.zip", 2),
        ("research/data/insample", 2),
        ("research/data/vault/LINKUSDT/x.zip", 2),
        # il resto del repo
        ("bot/config.py", 2),
        ("ops/results/0001.md", 2),
        (".env", 2),
    ],
)
def test_link6_lettura(link6, percorso, atteso):
    codice, err = _read(link6, percorso)
    assert codice == atteso, err
    if atteso == 2:
        assert err.startswith(RIFIUTO)
        assert "sessione campagna LINK6" in err
        assert "PROTOCOLLO_4.md, sezioni 0, 3 e 12" in err


@pytest.mark.parametrize(
    "percorso, atteso",
    [
        ("research/campagne/LINK6/log.jsonl", 0),
        ("research/campagne/LINK6/codice/v001.py", 0),
        ("research/campagne/LINK6/richieste/V-001.json", 0),
        ("research/data/insample/LINKUSDT/nota.txt", 0),
        # sola lettura per la sessione di ricerca
        ("research/campagne/LINK6/risposte/V-001.json", 2),
        ("research/campagne/LINK6/risposte/V-002.json", 2),
        ("research/campagne/LINK6/via_libera_validazione.md", 2),
        ("research/PROTOCOLLO_4.md", 2),
        ("research/src/statistica3.py", 2),
        ("research/src/dati.py", 2),
        ("research/config/parametri_4.yaml", 2),
        ("research/config/bot_4.md", 2),
        ("research/config/guida_pratica_4.md", 2),
        ("research/.sessione", 2),
        ("CLAUDE.md", 2),
        (".gitignore", 2),
    ],
)
def test_link6_scrittura(link6, percorso, atteso):
    codice, err = _esegui(link6, "Write", {"file_path": percorso, "content": "x"})
    assert codice == atteso, err


def test_link6_non_cancella_le_risposte(link6):
    assert _bash(link6, "rm -rf research/campagne/LINK6/risposte")[0] == 2
    assert _bash(link6, "rm -rf research/campagne/LINK6")[0] == 2
    assert _bash(link6, "rm research/campagne/LINK6/log.jsonl")[0] == 0


def test_link6_comandi(link6):
    assert _bash(link6, "cat research/PROTOCOLLO_4.md")[0] == 0
    assert _bash(link6, "cat research/PROTOCOLLO_3.md")[0] == 2
    assert _bash(link6, "cat research/campagne/LINKUSDT/consegna.md")[0] == 2
    assert _bash(link6, "ls research/data/insample/LINKUSDT")[0] == 0
    assert _bash(link6, "ls research/data/insample/BTCUSDT")[0] == 2
    assert _bash(link6, "echo x > research/campagne/LINK6/risposte/V-009.json")[0] == 2
    assert _bash(link6, "echo x > research/campagne/LINK6/richieste/V-009.json")[0] == 0


def test_link6_branch(link6):
    assert _bash(link6, "git status")[0] == 0
    assert _bash(link6, "git log research/campagna/BTC51")[0] == 2
    assert _bash(link6, "git log --oneline -- research/campagne/LINKUSDT")[0] == 2


@pytest.mark.parametrize(
    "url, atteso",
    [
        ("https://arxiv.org/abs/1234.5678", 0),
        ("https://en.wikipedia.org/wiki/Chainlink", 2),
    ],
)
def test_link6_web(link6, url, atteso):
    codice, err = _esegui(link6, "WebFetch", {"url": url, "prompt": "x"})
    assert codice == atteso, err


def test_link6_vault_solo_con_apertura_4(link6):
    (link6 / "research" / "data" / "vault" / "LINKUSDT").mkdir(parents=True, exist_ok=True)
    (link6 / "research" / "vault").mkdir(parents=True, exist_ok=True)
    (link6 / "research" / "vault" / "APERTURA_3.md").write_text("aperto per il protocollo 3\n")
    marcatore = {"tipo": "campagna", "simbolo": "LINK6"}
    assert guardiano.costruisci_contesto(str(link6), marcatore).vault_aperto is False
    assert _read(link6, "research/data/vault/LINKUSDT/x.zip")[0] == 2
    (link6 / "research" / "vault" / "APERTURA_4.md").write_text("APRI IL VAULT 4\n")
    assert guardiano.costruisci_contesto(str(link6), marcatore).vault_aperto is True
    assert guardiano.marcatore_vault("LINK6") == "APERTURA_4.md"
    assert guardiano.marcatore_vault("BTC51") == "APERTURA_3.md"


def test_monete_ammesse_link6():
    assert guardiano.monete_dati_ammesse("LINK6") == frozenset({"LINKUSDT"})
