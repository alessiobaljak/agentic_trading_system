"""Test del guardiano (`research/src/guardiano.py`, PROTOCOLLO.md sezione 2).

Il guardiano si prova come viene usato davvero: eseguito con `python3` da
subprocess, con `CLAUDE_PROJECT_DIR` puntato a una radice TEMPORANEA costruita
qui (marcatore, elenco dei vietati copiato dal repo, cartelle finte), il JSON
dell'azione su stdin. Si controllano codice di uscita e stderr.

Le regole: senza marcatore non interviene; marcatore rotto blocca; in campagna
vale la lista bianca del Passo 3 (mai un'altra moneta, mai il coordinamento, mai
i vietati o i segreti, mai un altro branch); in coordinamento vale la lista nera
(vietati, segreti, vault chiuso). In piu' un test legge il `.claude/settings.json`
del repo e verifica che il guardiano sia registrato senza aver perso il resto.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RADICE_REPO = Path(__file__).resolve().parents[3]
GUARDIANO = RADICE_REPO / "research" / "src" / "guardiano.py"
VIETATI_REPO = RADICE_REPO / "research" / "config" / "percorsi_vietati.txt"

RIFIUTO = "[guardiano] azione rifiutata"


# ---------------------------------------------------------------------------
# attrezzi
# ---------------------------------------------------------------------------


def _radice_finta(tmp_path: Path) -> Path:
    """Una radice di repo finta con le cartelle che il guardiano deve conoscere."""
    radice = tmp_path / "repo"
    for cartella in (
        "research/config",
        "research/src/tests",
        "research/campagne/BTCUSDT",
        "research/campagne/ETHUSDT",
        "research/data/insample/BTCUSDT",
        "research/data/insample/ETHUSDT",
        "research/data/vault/BTCUSDT",
        "research/universo",
        "research/vault",
        "research/lezioni",
        "docs",
        "bot",
        "ops/results",
        ".claude",
    ):
        (radice / cartella).mkdir(parents=True, exist_ok=True)
    shutil.copy(VIETATI_REPO, radice / "research" / "config" / "percorsi_vietati.txt")
    (radice / ".env").write_text("FINTO=1\n")
    (radice / "docs" / "state.md").write_text("stato\n")
    (radice / "research" / "campagne" / "BTCUSDT" / "log.jsonl").write_text("")
    (radice / "research" / "campagne" / "ETHUSDT" / "log.jsonl").write_text("")
    (radice / "research" / "universo" / "monete_campagna.csv").write_text("")
    (radice / "research" / "src" / "motore.py").write_text("")
    return radice


def _marcatore(radice: Path, contenuto) -> None:
    percorso = radice / "research" / ".sessione"
    if contenuto is None:
        if percorso.exists():
            percorso.unlink()
    elif isinstance(contenuto, str):
        percorso.write_text(contenuto)
    else:
        percorso.write_text(json.dumps(contenuto))


def _esegui(radice: Path, tool_name: str, tool_input, *, stdin_grezzo: str | None = None):
    """Lancia il guardiano come hook e restituisce (exit code, stderr)."""
    ambiente = dict(os.environ)
    ambiente["CLAUDE_PROJECT_DIR"] = str(radice)
    carico = stdin_grezzo
    if carico is None:
        carico = json.dumps({"tool_name": tool_name, "tool_input": tool_input, "cwd": str(radice)})
    esito = subprocess.run(
        [sys.executable, str(GUARDIANO)],
        input=carico,
        capture_output=True,
        text=True,
        env=ambiente,
        cwd=str(radice),
        timeout=10,
    )
    return esito.returncode, esito.stderr


def _read(radice: Path, percorso: str):
    return _esegui(radice, "Read", {"file_path": percorso})


def _bash(radice: Path, comando: str):
    return _esegui(radice, "Bash", {"command": comando})


@pytest.fixture
def radice(tmp_path: Path) -> Path:
    return _radice_finta(tmp_path)


@pytest.fixture
def campagna_btc(radice: Path) -> Path:
    _marcatore(radice, {"tipo": "campagna", "simbolo": "BTCUSDT"})
    return radice


@pytest.fixture
def campagna_eth(radice: Path) -> Path:
    _marcatore(radice, {"tipo": "campagna", "simbolo": "ETHUSDT"})
    return radice


@pytest.fixture
def coordinamento(radice: Path) -> Path:
    _marcatore(radice, {"tipo": "coordinamento"})
    return radice


# ---------------------------------------------------------------------------
# senza marcatore e marcatore rotto
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tool_name, tool_input",
    [
        ("Read", {"file_path": "docs/state.md"}),
        ("Read", {"file_path": ".env"}),
        ("Grep", {"pattern": "x"}),
        ("Bash", {"command": "printenv"}),
        ("Bash", {"command": "git checkout research/coordinamento"}),
        ("Write", {"file_path": "research/campagne/ETHUSDT/log.jsonl", "content": ""}),
    ],
)
def test_senza_marcatore_consente_tutto(radice, tool_name, tool_input):
    codice, err = _esegui(radice, tool_name, tool_input)
    assert codice == 0
    assert err == ""


def test_marcatore_vuoto_vale_come_assente(radice):
    _marcatore(radice, "   \n")
    assert _read(radice, "docs/state.md")[0] == 0


@pytest.mark.parametrize("rotto", ["{non json", '{"tipo": "boh"}', '{"tipo": "campagna"}', "[1, 2]"])
def test_marcatore_rotto_blocca(radice, rotto):
    _marcatore(radice, rotto)
    codice, err = _read(radice, "research/src/motore.py")
    assert codice == 2
    assert "marcatore" in err


def test_stdin_rotto_con_marcatore_blocca(campagna_btc):
    codice, _ = _esegui(campagna_btc, "", {}, stdin_grezzo="non e' json")
    assert codice == 2


def test_stdin_rotto_senza_marcatore_consente(radice):
    codice, _ = _esegui(radice, "", {}, stdin_grezzo="non e' json")
    assert codice == 0


# ---------------------------------------------------------------------------
# campagna: file singoli
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "percorso, atteso",
    [
        ("research/campagne/BTCUSDT/log.jsonl", 0),
        ("research/campagne/ETHUSDT/log.jsonl", 2),
        ("research/universo/monete_campagna.csv", 2),
        ("research/data/insample/BTCUSDT/x.zip", 0),
        ("research/data/insample/ETHUSDT/x.zip", 2),
        ("research/data/vault/BTCUSDT/x.zip", 2),
        ("research/vault/APERTURA.md", 2),
        ("research/prova_processo/x.md", 2),
        ("research/trasferimento/x.md", 2),
        ("research/confronto/x.md", 2),
        ("research/paper/x.md", 2),
        ("docs/state.md", 2),
        ("bot/config.py", 2),
        ("backtesting/engine.py", 2),
        ("ops/results/0001.md", 2),
        (".env", 2),
        ("tuning.env", 2),
        ("bot/firebase-service-account.json", 2),
        ("research/src/motore.py", 0),
        ("research/src/tests/test_motore.py", 0),
        ("research/config/parametri.yaml", 0),
        ("research/PROTOCOLLO.md", 0),
        ("research/CHANGELOG.md", 0),
        ("research/lezioni/metodo.md", 0),
        ("research/lezioni/altro.md", 2),
        ("research/.sessione", 0),
        ("CLAUDE.md", 0),
        (".gitignore", 0),
        (".claude/settings.json", 0),
        ("README.md", 2),
        # ".." che esce dai percorsi ammessi
        ("research/campagne/BTCUSDT/../ETHUSDT/log.jsonl", 2),
        ("research/src/../../docs/state.md", 2),
        ("research/src/../src/motore.py", 0),
        ("../repo/research/campagne/BTCUSDT/log.jsonl", 0),
        ("../altro/research/campagne/BTCUSDT/log.jsonl", 2),
        ("/etc/passwd", 2),
        ("~/.ssh/id_rsa", 2),
    ],
)
def test_campagna_btc_read(campagna_btc, percorso, atteso):
    codice, err = _read(campagna_btc, percorso)
    assert codice == atteso, err
    if atteso == 2:
        assert err.startswith(RIFIUTO)
        assert "sessione campagna BTCUSDT" in err
        assert "Passo 3" in err
        assert err.count("\n") <= 1  # una riga sola


def test_campagna_percorso_assoluto_dentro_la_radice(campagna_btc):
    assoluto = str(campagna_btc / "research" / "campagne" / "BTCUSDT" / "log.jsonl")
    assert _read(campagna_btc, assoluto)[0] == 0
    assoluto_vietato = str(campagna_btc / "research" / "campagne" / "ETHUSDT" / "log.jsonl")
    assert _read(campagna_btc, assoluto_vietato)[0] == 2


def test_campagna_eth_vede_i_dati_btc_ma_non_la_campagna_btc(campagna_eth):
    assert _read(campagna_eth, "research/data/insample/BTCUSDT/x.zip")[0] == 0
    assert _read(campagna_eth, "research/data/insample/ETHUSDT/x.zip")[0] == 0
    assert _read(campagna_eth, "research/campagne/ETHUSDT/consegna.md")[0] == 0
    codice, err = _read(campagna_eth, "research/campagne/BTCUSDT/consegna.md")
    assert codice == 2
    assert "sessione campagna ETHUSDT" in err


@pytest.mark.parametrize("tool_name", ["Write", "Edit", "MultiEdit"])
def test_campagna_scrittura_segue_le_stesse_regole(campagna_btc, tool_name):
    assert _esegui(campagna_btc, tool_name, {"file_path": "research/campagne/BTCUSDT/log.jsonl"})[0] == 0
    assert _esegui(campagna_btc, tool_name, {"file_path": "research/campagne/ETHUSDT/log.jsonl"})[0] == 2
    assert _esegui(campagna_btc, tool_name, {"file_path": "docs/state.md"})[0] == 2


def test_campagna_notebook_path(campagna_btc):
    assert _esegui(campagna_btc, "NotebookEdit", {"notebook_path": "research/campagne/BTCUSDT/n.ipynb"})[0] == 0
    assert _esegui(campagna_btc, "NotebookEdit", {"notebook_path": "docs/n.ipynb"})[0] == 2


def test_campagna_read_senza_percorso_blocca(campagna_btc):
    assert _esegui(campagna_btc, "Read", {})[0] == 2


# ---------------------------------------------------------------------------
# campagna: ricerche
# ---------------------------------------------------------------------------


def test_campagna_grep_senza_path_blocca(campagna_btc):
    codice, err = _esegui(campagna_btc, "Grep", {"pattern": "rsi"})
    assert codice == 2
    assert err.startswith(RIFIUTO)


def test_campagna_grep_con_glob_ma_senza_path_blocca(campagna_btc):
    assert _esegui(campagna_btc, "Grep", {"pattern": "rsi", "glob": "research/campagne/BTCUSDT/*"})[0] == 2


def test_campagna_grep_con_path_ammesso(campagna_btc):
    assert _esegui(campagna_btc, "Grep", {"pattern": "rsi", "path": "research/campagne/BTCUSDT"})[0] == 0
    assert _esegui(campagna_btc, "Grep", {"pattern": "rsi", "path": "research/src"})[0] == 0


def test_campagna_grep_con_path_vietato(campagna_btc):
    assert _esegui(campagna_btc, "Grep", {"pattern": "rsi", "path": "research/campagne/ETHUSDT"})[0] == 2
    assert _esegui(campagna_btc, "Grep", {"pattern": "rsi", "path": "."})[0] == 2


def test_campagna_glob(campagna_btc):
    assert _esegui(campagna_btc, "Glob", {"pattern": "*.md"})[0] == 2
    assert _esegui(campagna_btc, "Glob", {"pattern": "*.md", "path": "research/campagne"})[0] == 2
    assert _esegui(campagna_btc, "Glob", {"pattern": "*.md", "path": "research/campagne/BTCUSDT"})[0] == 0


# ---------------------------------------------------------------------------
# campagna: comandi di shell
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comando, atteso",
    [
        ("python -m pytest research/src/tests -q", 0),
        ("python -m pytest research/src/tests/test_guardiano.py -q -p no:cacheprovider", 0),
        ("ls", 0),
        ("ls research/campagne/BTCUSDT", 0),
        ("ls research/campagne", 2),
        ("ls docs", 2),
        ("ls ops", 2),
        ("cat ops/results/0001.md", 2),
        ("cat research/campagne/ETHUSDT/log.jsonl", 2),
        ("cat research/campagne/BTCUSDT/log.jsonl", 0),
        ("cat research/campagne/BTCUSDT/../ETHUSDT/log.jsonl", 2),
        ("cat research/src/motore.py && cat research/campagne/ETHUSDT/log.jsonl", 2),
        ("cat research/src/motore.py | head", 0),
        ("cat .env", 2),
        ("cat ./.env", 2),
        ("cat $HOME/.env", 2),
        ("cat ~/.ssh/id_rsa", 2),
        ("cat /etc/passwd", 2),
        ("printenv", 2),
        ("env", 2),
        ("env | grep KEY", 2),
        ("set", 2),
        ("/usr/bin/printenv", 2),
        ("git status", 0),
        # dal 7 ott 2026 (test_guardiano_4_4.py) `git log` senza un percorso della propria
        # cartella e' vietato in campagna: stampava i messaggi di tutto il branch principale
        # (come e' finito il tentativo precedente, i commit del bot nel periodo del vault)
        ("git log --oneline -5", 2),
        ("git log --oneline -5 -- research/campagne/BTCUSDT/", 0),
        ("git log research/campagna/ETHUSDT", 2),
        ("git log research/campagna/BTCUSDT", 2),
        ("git log research/campagna/BTCUSDT -- research/campagne/BTCUSDT/", 0),
        ("git checkout research/coordinamento", 2),
        ("git checkout -- research/src/motore.py", 2),
        ("git switch research/campagna/ETHUSDT", 2),
        ("git merge research/campagna/ETHUSDT", 2),
        ("git rebase main", 2),
        ("git worktree add ../x", 2),
        ("git fetch origin research/coordinamento", 2),
        ("git diff research/archivio", 2),
        ("git show origin/research/campagna/ETHUSDT:research/campagne/ETHUSDT/log.jsonl", 2),
        ("git pull origin research/campagna/BTCUSDT", 0),
        ("git push origin research/campagna/BTCUSDT", 0),
        ("git add research/campagne/BTCUSDT/log.jsonl && git commit -m 'campagna: log'", 0),
        ("git diff research/src/motore.py", 0),
        ("grep -r rsi research/campagne/ETHUSDT", 2),
        ("grep -r rsi .", 2),
        ("python research/src/dati.py --simbolo BTCUSDT --uscita=research/data/insample/BTCUSDT", 0),
        ("python research/src/dati.py --uscita=research/data/vault/BTCUSDT", 2),
        ("echo ciao > research/campagne/ETHUSDT/x.md", 2),
        ("echo ciao > research/campagne/BTCUSDT/x.md", 0),
    ],
)
def test_campagna_bash(campagna_btc, comando, atteso):
    codice, err = _bash(campagna_btc, comando)
    assert codice == atteso, err
    if atteso == 2:
        assert err.startswith(RIFIUTO)


def test_campagna_cd_nella_radice_consentito(campagna_btc):
    comando = f"cd {campagna_btc} && python -m pytest research/src/tests -q"
    assert _bash(campagna_btc, comando)[0] == 0
    # ma la radice come argomento di una ricerca no: guarda tutto
    assert _bash(campagna_btc, f"grep -r rsi {campagna_btc}")[0] == 2


def test_campagna_bash_senza_comando_blocca(campagna_btc):
    assert _esegui(campagna_btc, "Bash", {})[0] == 2


# ---------------------------------------------------------------------------
# coordinamento
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "percorso, atteso",
    [
        ("research/campagne/ETHUSDT/consegna.md", 0),
        ("research/campagne/BTCUSDT/log.jsonl", 0),
        ("research/universo/monete_campagna.csv", 0),
        ("research/trasferimento/x.md", 0),
        ("research/prova_processo/x.md", 0),
        ("research/data/insample/BTCUSDT/x.zip", 0),
        ("research/data/vault/BTCUSDT/x.zip", 2),
        ("bot/config.py", 0),
        ("backtesting/engine.py", 0),
        ("backtesting/output/x.json", 2),
        ("ops/results/x.md", 2),
        ("ops/heartbeat.md", 2),
        ("docs/state.md", 2),
        ("data_cache/x.json", 2),
        ("data/x.json", 2),
        ("tests/test_x.py", 2),
        ("dashboard/x.tsx", 2),
        ("firebase/x.json", 2),
        (".env", 2),
        ("tuning.env", 2),
        ("bot/.env", 2),
        ("x/service-account.json", 2),
        ("trades_backup_2026.json", 2),
        ("gate_backup_2026.json", 2),
        ("bot/x.jsonl", 2),
        ("bot/x.log", 2),
        ("bot/x.db", 2),
        ("bot/x.sqlite", 2),
        ("bot/x.parquet", 2),
        ("bot/x.csv", 2),
        ("README.md", 0),
        ("CLAUDE.md", 0),
    ],
)
def test_coordinamento_read(coordinamento, percorso, atteso):
    codice, err = _read(coordinamento, percorso)
    assert codice == atteso, err
    if atteso == 2:
        assert err.startswith(RIFIUTO)
        assert "sessione coordinamento" in err


def test_coordinamento_vault_si_apre_con_apertura(coordinamento):
    assert _read(coordinamento, "research/data/vault/BTCUSDT/x.zip")[0] == 2
    (coordinamento / "research" / "vault" / "APERTURA.md").write_text("aperto\n")
    assert _read(coordinamento, "research/data/vault/BTCUSDT/x.zip")[0] == 0


def test_coordinamento_ricerche_senza_path_consentite(coordinamento):
    assert _esegui(coordinamento, "Grep", {"pattern": "x"})[0] == 0
    assert _esegui(coordinamento, "Glob", {"pattern": "*.md"})[0] == 0
    assert _esegui(coordinamento, "Grep", {"pattern": "x", "path": "ops"})[0] == 2


@pytest.mark.parametrize(
    "comando, atteso",
    [
        ("git checkout research/campagna/ETHUSDT", 0),
        ("git log research/coordinamento", 0),
        ("cat research/campagne/ETHUSDT/log.jsonl", 0),
        ("cat ops/results/0001.md", 2),
        ("cat .env", 2),
        ("ls docs", 2),
        ("cat research/data/vault/BTCUSDT/x.csv", 2),
    ],
)
def test_coordinamento_bash(coordinamento, comando, atteso):
    codice, err = _bash(coordinamento, comando)
    assert codice == atteso, err


# ---------------------------------------------------------------------------
# funzioni pure (senza subprocess)
# ---------------------------------------------------------------------------


def test_normalizza():
    from research.src import guardiano as g

    r = "/repo"
    assert g.normalizza("research/src/../src/motore.py", r) == "research/src/motore.py"
    assert g.normalizza("/repo/docs/state.md", r) == "docs/state.md"
    assert g.normalizza("/altro/x", r).startswith("..")
    assert g.normalizza("research/../..", r).startswith("..")
    assert g.normalizza("/repo", r) == "."


def test_elenco_vietati_del_repo_si_legge():
    from research.src import guardiano as g

    voci = g.leggi_vietati(str(RADICE_REPO))
    assert "ops/" in voci and "*.csv" in voci and "docs/" in voci
    assert all(not v.startswith("#") for v in voci)
    # i pattern di file valgono solo fuori da research/
    assert g.e_vietato_da_elenco("bot/x.csv", voci)
    assert not g.e_vietato_da_elenco("research/universo/monete_campagna.csv", voci)
    assert not g.e_vietato_da_elenco("research/data/insample/BTCUSDT/x.csv", voci)
    assert not g.e_vietato_da_elenco("research/campagne/BTCUSDT/log.jsonl", voci)
    assert g.e_vietato_da_elenco("data/x.json", voci)
    assert not g.e_vietato_da_elenco("research/data/x.json", voci)


def test_percorsi_vietati_ha_il_commento_di_proposta():
    testo = VIETATI_REPO.read_text(encoding="utf-8")
    assert testo.lstrip().startswith("#")
    assert "Passo 0" in testo


# ---------------------------------------------------------------------------
# registrazione in .claude/settings.json del repo
# ---------------------------------------------------------------------------


def test_guardiano_registrato_in_settings():
    settings = json.loads((RADICE_REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    hooks = settings["hooks"]
    pre = hooks["PreToolUse"]
    assert isinstance(pre, list) and pre
    voce = next(v for v in pre if "guardiano.py" in json.dumps(v))
    # dal 7 ott 2026 il guardiano vede TUTTI gli strumenti (prima solo file, ricerche e
    # Bash): in campagna gli strumenti MCP e WebFetch leggono altri branch del repo
    assert voce["matcher"] == "*"
    comando = voce["hooks"][0]
    assert comando["type"] == "command"
    assert comando["command"] == 'python3 "$CLAUDE_PROJECT_DIR/research/src/guardiano.py"'
    # il resto non deve essere stato toccato
    assert "SessionStart" in hooks
    assert settings["permissions"]["deny"]
    assert "Bash(printenv*)" in settings["permissions"]["deny"]
    assert settings["permissions"]["allow"]
