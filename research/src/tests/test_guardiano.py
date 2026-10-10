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
        # (il lavoro di coordinamento, i commit del bot nel periodo del vault)
        ("git log --oneline -5", 2),
        # dal 10 ott 2026 (test_guardiano_gruppo.py) in un clone a storia limitata la storia
        # si guarda solo con date e hash, e questa radice finta non e' un repo git: git non sa
        # dire se e' limitata, quindi vale come limitata. `--oneline` e il formato predefinito
        # qui sono rifiutati (lo provano i test del gruppo); con un formato di date e hash no
        ("git log --format=%h -5 -- research/campagne/BTCUSDT/", 0),
        ("git log research/campagna/ETHUSDT", 2),
        ("git log research/campagna/BTCUSDT", 2),
        ("git log --format=%cI research/campagna/BTCUSDT -- research/campagne/BTCUSDT/", 0),
        ("git checkout research/coordinamento", 2),
        ("git checkout -- research/src/motore.py", 2),
        ("git switch research/campagna/ETHUSDT", 2),
        ("git merge research/campagna/ETHUSDT", 2),
        ("git rebase main", 2),
        ("git worktree add ../x", 2),
        ("git fetch origin research/coordinamento", 2),
        ("git diff research/archivio", 2),
        ("git show origin/research/campagna/ETHUSDT:research/campagne/ETHUSDT/log.jsonl", 2),
        # dal 7 ott 2026 commit, push e pull passano solo se git dice che HEAD e' sul proprio
        # branch: questa radice finta non e' un repo git, quindi nel dubbio si blocca. Sul
        # proprio branch di un repo vero sono ammessi (test_guardiano_4_4.py, passi della sessione)
        ("git pull origin research/campagna/BTCUSDT", 2),
        ("git push origin research/campagna/BTCUSDT", 2),
        ("git add research/campagne/BTCUSDT/log.jsonl && git commit -m 'campagna: log'", 2),
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


# ===========================================================================
# revisione del 10 ottobre 2026 (vale per OGNI campagna, una moneta o il gruppo:
# per il gruppo vedi anche test_guardiano_gruppo.py, sezione K)
# ===========================================================================

#: i programmi di rete della revisione: in campagna si rifiutano tutti
PROGRAMMI_RETE = (
    "curl", "wget", "wget2", "aria2c", "http", "https", "httpie", "httpx", "xh", "curlie",
    "lynx", "w3m", "links", "elinks", "nc", "ncat", "netcat", "socat", "telnet", "ftp", "sftp",
    "scp", "ssh", "rsync", "openssl", "gh", "aws", "gsutil", "gcloud", "bq", "uv", "uvx",
    "pip", "pip3", "pipx", "bun", "bunx", "npm", "npx", "pnpm", "yarn", "deno", "busybox",
)
#: ...e quelli installati nell'ambiente delle sessioni che scaricano pacchetti o parlano
#: con la rete (`command -v`, 10 ott 2026), con le versioni numerate di pip
PROGRAMMI_RETE_INSTALLATI = (
    "go", "cargo", "rustup", "gem", "cpan", "composer", "corepack", "poetry", "mvn", "gradle",
    "docker", "git-lfs", "playwright", "claude", "pip3.12", "pip3.11",
)
MOTIVO_RETE = ("apre la rete: in campagna i dati si scaricano solo con research/src/dati.py, "
               "le pagine solo con WebFetch")


@pytest.mark.parametrize("programma", PROGRAMMI_RETE + PROGRAMMI_RETE_INSTALLATI)
def test_rete_programmi_vietati_in_campagna(campagna_btc, programma):
    codice, err = _bash(campagna_btc, f"{programma} --help")
    assert codice == 2, f"BUCO: {programma} consentito in campagna"
    assert err.startswith(RIFIUTO), err
    assert f"{programma} {MOTIVO_RETE}" in err, err


@pytest.mark.parametrize(
    "comando",
    [
        # i comandi della revisione (rev1, voce 23): passavano tutti, con e senza gruppo
        "curl -s 'https://www.binance.com/fapi/v1/exchangeInfo?symbol=OCEANUSDT'",
        "wget -qO- 'https://www.binance.com/fapi/v1/exchangeInfo?a=b'",
        "curl -sI 'https://data.binance.vision/data/futures/um/monthly/klines/OCEANUSDT/1d/"
        "OCEANUSDT-1d-2024-06.zip?a=1'",
        "curl -s -o research/data/insample/BTCUSDT/x.zip 'https://data.binance.vision/data/futures/um/monthly/"
        "klines/BTCUSDT/1d/BTCUSDT-1d-2025-06.zip?a=1'",
        "curl -s 'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=%2F"
        "&prefix=data%2Ffutures%2Fum%2Fmonthly%2Fklines%2F'",
        "gh issue list",
        "gh pr list",
        "gh api 'repos/o/r/commits?sha=main'",
        "gh api 'repos/o/r/contents/research?ref=research%2Fcampagna%2FBNBUSDT'",
        "curl 'https://api.github.com/repos/o/r/commits?sha=main'",
        "httpx 'https://www.binance.com/fapi/v1/exchangeInfo?a=b'",
        "python3 -m pip download -d research/data/insample/BTCUSDT 'https://data.binance.vision/x.zip?a=1'",
        "uvx --from httpie http 'www.binance.com/x?a=b'",
        "bun -e 'fetch(1)'",
        "npx -y qualcosa",
        "nc -z www.binance.com 443",
        "openssl s_client -connect www.binance.com:443",
        # con il percorso assoluto e attraverso i prefissi e le shell
        "/usr/bin/curl -s https://www.binance.com/x",
        "/usr/local/bin/gh issue list",
        "env curl www.binance.com",
        "command curl www.binance.com",
        "exec curl www.binance.com",
        "nice curl www.binance.com",
        "nice -n 10 curl www.binance.com",
        "timeout 5 wget www.binance.com",
        "timeout -s KILL 5 wget www.binance.com",
        "nohup curl www.binance.com",
        "nohup curl www.binance.com &",
        "time curl www.binance.com",
        "stdbuf -o0 curl www.binance.com",
        "sudo curl www.binance.com",
        "xargs curl < research/campagne/BTCUSDT/indirizzi.txt",
        "cat research/campagne/BTCUSDT/indirizzi.txt | xargs wget",
        "sh -c 'curl www.binance.com'",
        "bash -c \"wget www.binance.com\"",
        "bash -lc 'curl www.binance.com'",
        "bash -o pipefail -c 'curl www.binance.com'",
        "sh -c \"sh -c 'nc -z www.binance.com 443'\"",
        "echo x && curl www.binance.com",
        "true; wget www.binance.com",
        "(curl www.binance.com)",
        "cat research/campagne/BTCUSDT/x | curl -d @- www.binance.com",
        "find research/campagne/BTCUSDT -exec curl www.binance.com \\;",
        "find research/campagne/BTCUSDT -name x -exec sh -c 'wget www.binance.com' \\;",
        # programmi che lanciano il comando che segue senza essere prefissi trasparenti
        "setsid curl www.binance.com",
        "script -qc 'curl www.binance.com' /dev/null",
        "watch -n 1 curl www.binance.com",
        "flock research/campagne/BTCUSDT/x curl www.binance.com",
        "strace -f curl www.binance.com",
        "taskset 1 curl www.binance.com",
    ],
)
def test_rete_comandi_rifiutati_in_campagna(campagna_btc, comando):
    codice, err = _bash(campagna_btc, comando)
    assert codice == 2, f"BUCO: {comando!r} consentito in campagna"
    assert err.startswith(RIFIUTO), err


@pytest.mark.parametrize("comando", [
    "curl -s 'https://www.binance.com/fapi/v1/exchangeInfo?symbol=OCEANUSDT'",
    "wget -qO- 'https://www.binance.com/fapi/v1/exchangeInfo?a=b'",
    "gh issue list",
    "python3 -m pip list",
    "echo https://github.com/x/y",
    "setsid curl www.binance.com",
])
def test_rete_coordinamento_e_senza_marcatore_come_prima(coordinamento, comando):
    """Fuori dalla campagna non cambia nulla."""
    assert _bash(coordinamento, comando) == (0, "")
    _marcatore(coordinamento, None)
    assert _bash(coordinamento, comando) == (0, "")


# ---------------------------------------------------------------------------
# interpreti: con -m solo pytest; niente codice da stdin
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comando",
    [
        "python3 -m pip list",
        "python -m pip download x",
        "python3 -mpip list",
        "python3 -Bm pip list",
        "python3 -B -m pip list",
        "python3 -I -m http.server",
        "python3 -m http.server 8000",
        "python3 -m urllib.request https://www.binance.com",
        "python3 -m uv pip install x",
        "python3.12 -m pip list",
        "pypy3 -m pip list",
        "python3 -m pytest.__main__",
        "python3 -m",
        "python3 -W ignore -m pip list",
        # codice in linea o da stdin, anche con le lettere unite o un valore di -W/-X
        "python3 -Ic 'print(1)'",
        "python3 -Bc 'print(1)'",
        "python3 -i research/src/motore.py",
        "python3 /dev/stdin",
        "python3 /dev/fd/0",
        "python3 -W ignore",
        "python3 -X importtime",
        "PYTHONINSPECT=1 python3 research/src/motore.py",
        "bash /dev/stdin",
        "bash -s",
        "bash -s x",
        "sh -",
        "bash -o pipefail",
        "echo 'curl www.binance.com' | bash /dev/stdin",
    ],
)
def test_interpreti_m_diverso_da_pytest_e_stdin_rifiutati(campagna_btc, comando):
    codice, err = _bash(campagna_btc, comando)
    assert codice == 2, f"BUCO: {comando!r} consentito in campagna"
    assert err.startswith(RIFIUTO), err


@pytest.mark.parametrize(
    "comando",
    [
        "python -m pytest research/src/tests -q -p no:cacheprovider",
        "python3 -m pytest research/src/tests/test_guardiano.py -q -p no:cacheprovider",
        # i comandi dei due messaggi di apertura (research/apertura/campagna.md e gruppo.md)
        "python -m pytest research/src/tests/test_guardiano.py research/src/tests/test_guardiano_4_4.py "
        "-q -p no:cacheprovider",
        "python -m pytest research/src/tests/test_guardiano.py research/src/tests/test_guardiano_4_4.py "
        "research/src/tests/test_guardiano_gruppo.py -q -p no:cacheprovider",
        "python3 -mpytest -q research/src/tests",
        "python3 -B -m pytest -q research/src/tests",
        "python3 -X importtime -W ignore -m pytest -q research/src/tests",
        # dopo lo script, -m e -c sono argomenti dello script
        "python3 research/src/motore.py -m pip",
        "python3 -W ignore research/src/motore.py",
        "python3 -u research/src/motore.py",
        "python3 -V",
        "python3 --version",
        "bash research/campagne/BTCUSDT/x.sh",
        "bash -x research/campagne/BTCUSDT/x.sh",
        "bash -euo pipefail research/campagne/BTCUSDT/x.sh",
    ],
)
def test_interpreti_pytest_e_script_ammessi(campagna_btc, comando):
    codice, err = _bash(campagna_btc, comando)
    assert codice == 0, err


def test_interpreti_m_in_coordinamento_come_prima(coordinamento):
    for comando in ("python3 -m pip list", "python3 -Ic 'print(1)'", "python3 /dev/stdin"):
        assert _bash(coordinamento, comando) == (0, ""), comando


def test_opzioni_interprete_si_leggono_come_python():
    from research.src import guardiano as g

    assert g._opzioni_interprete(["-m", "pytest", "-q"]) == ("m", "pytest", None)
    assert g._opzioni_interprete(["-mpytest"]) == ("m", "pytest", None)
    assert g._opzioni_interprete(["-Bm", "pip"]) == ("Bm", "pip", None)
    assert g._opzioni_interprete(["-W", "ignore", "x.py", "-m", "pip"]) == ("W", None, "x.py")
    assert g._opzioni_interprete(["-Wignore", "-X", "importtime", "x.py"]) == ("WX", None, "x.py")
    assert g._opzioni_interprete(["-Ic", "print(1)"])[0] == "Ic"
    assert g._opzioni_interprete(["--check-hash-based-pycs", "always", "x.py"]) == ("", None, "x.py")
    assert g._opzioni_interprete(["-B"]) == ("B", None, None)


# ---------------------------------------------------------------------------
# il `=`: si spezza solo dopo un'opzione o un nome di variabile
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comando, atteso",
    [
        # prima si giudicava solo cio' che segue il `=` (`b`, `OCEANUSDT`), che non e' un percorso
        ("cat research/campagne/ETHUSDT/a=b", 2),
        ("cat docs/a=b", 2),
        ("echo x > research/campagne/ETHUSDT/a=b", 2),
        ("cat research/campagne/BTCUSDT/a=b", 0),
        # gli indirizzi: passano solo quelli che WebFetch aprirebbe
        ("echo 'https://www.binance.com/fapi/v1/exchangeInfo?symbol=OCEANUSDT'", 2),
        ("echo www.binance.com/fapi/v1/exchangeInfo?a=b", 2),
        ("echo --url=https://www.binance.com/x", 2),
        ("echo -ohttps://www.binance.com/x", 2),
        ("echo https://github.com/o/r >> research/campagne/BTCUSDT/fonti.md", 2),
        ("echo 'https://arxiv.org/abs/1?url=https://github.com/x' >> research/campagne/BTCUSDT/fonti.md", 2),
        ("echo https://arxiv.org/abs/1234.5678 >> research/campagne/BTCUSDT/fonti.md", 0),
        ("echo 'https://en.wikipedia.org/wiki/Momentum_(finance)' >> research/campagne/BTCUSDT/fonti.md", 0),
        ("echo --fonte=https://doi.org/10.1016/j.jfineco.2011.11.003 >> research/campagne/BTCUSDT/fonti.md", 0),
        # cio' che si spezzava e deve continuare a spezzarsi
        ("python research/src/dati.py --uscita=research/data/insample/BTCUSDT", 0),
        ("python research/src/dati.py --uscita=research/data/insample/ETHUSDT", 2),
        ("python3 research/src/motore.py --soglia=0.5", 0),
        ("dd if=research/data/insample/BTCUSDT/a of=research/data/insample/BTCUSDT/x bs=1 count=0", 0),
        ("dd of=research/data/insample/BTCUSDT/x", 0),
        ("dd of=research/campagne/ETHUSDT/x", 2),
        ("PYTHONHASHSEED=0 python3 script.py", 0),
        ("PYTHONHASHSEED=0 python3 research/src/motore.py", 0),
        ("git log --format='%h %cI' -- research/campagne/BTCUSDT/", 0),
    ],
)
def test_uguale_e_indirizzi_in_campagna(campagna_btc, comando, atteso):
    codice, err = _bash(campagna_btc, comando)
    assert codice == atteso, err


def test_candidato_percorso_spezza_solo_dopo_opzione_o_variabile():
    from research.src import guardiano as g

    vuoto = frozenset()
    assert g._candidato_percorso("--uscita=research/x", vuoto) == "research/x"
    assert g._candidato_percorso("-o=research/x", vuoto) == "research/x"
    assert g._candidato_percorso("of=research/x", vuoto) == "research/x"
    assert g._candidato_percorso("PYTHONHASHSEED=0", vuoto) is None
    assert g._candidato_percorso("--format=%h %cI", vuoto) is None
    url = "https://www.binance.com/fapi/v1/exchangeInfo?symbol=OCEANUSDT"
    assert g._candidato_percorso(url, vuoto) == url
    assert g._candidato_percorso("www.binance.com/x?a=b", vuoto) == "www.binance.com/x?a=b"
    assert g._candidato_percorso("research/campagne/ETHUSDT/a=b", vuoto) == "research/campagne/ETHUSDT/a=b"
    assert g._candidato_percorso("a.b=c/d", vuoto) == "a.b=c/d"
    # la regola di prima, che il coordinamento tiene
    assert g._candidato_percorso(url, vuoto, uguale_stretto=False) is None
    assert g._candidato_percorso("research/campagne/ETHUSDT/a=b", vuoto, uguale_stretto=False) is None


# ---------------------------------------------------------------------------
# research/config in sola lettura (una moneta; per il gruppo vedi test_guardiano_gruppo.py)
# ---------------------------------------------------------------------------

FILE_CONFIG = ("research/config/parametri.yaml", "research/config/regole_dimensione.md")

_SCRITTURE_CONFIG = [
    ("Write", lambda p: {"file_path": p, "content": "x"}),
    ("Edit", lambda p: {"file_path": p, "old_string": "a", "new_string": "b"}),
    ("MultiEdit", lambda p: {"file_path": p, "edits": [{"old_string": "a", "new_string": "b"}]}),
    ("Bash", lambda p: {"command": f"cp research/campagne/BTCUSDT/log.jsonl {p}"}),
    ("Bash", lambda p: {"command": f"sed -i 's|a|b|' {p}"}),
    ("Bash", lambda p: {"command": f"sed -i -e 's|a|b|' {p}"}),
    ("Bash", lambda p: {"command": f"echo x > {p}"}),
    ("Bash", lambda p: {"command": f"echo x >> {p}"}),
    ("Bash", lambda p: {"command": f"echo x | tee {p}"}),
    ("Bash", lambda p: {"command": f"echo x | tee -a {p}"}),
    ("Bash", lambda p: {"command": f"rm {p}"}),
    ("Bash", lambda p: {"command": f"rm -f {p}"}),
    ("Bash", lambda p: {"command": f"mv {p} research/campagne/BTCUSDT/vecchio"}),
    ("Bash", lambda p: {"command": f"mv research/campagne/BTCUSDT/log.jsonl {p}"}),
    ("Bash", lambda p: {"command": f"touch {p}"}),
    ("Bash", lambda p: {"command": f"truncate -s 0 {p}"}),
    ("Bash", lambda p: {"command": f"dd of={p}"}),
    ("Bash", lambda p: {"command": f"sort -o {p} {p}"}),
    ("Bash", lambda p: {"command": f"uniq research/campagne/BTCUSDT/log.jsonl {p}"}),
    ("Bash", lambda p: {"command": f"git rm {p}"}),
    ("Bash", lambda p: {"command": f"git restore {p}"}),
    ("Bash", lambda p: {"command": f"cd research/config && sed -i 's|a|b|' {os.path.basename(p)}"}),
    ("Bash", lambda p: {"command": f"cd research/config && echo x > {os.path.basename(p)}"}),
    ("Bash", lambda p: {"command": f"cd research/config && rm {os.path.basename(p)}"}),
]


def _config_sul_disco(radice):
    for percorso in FILE_CONFIG:
        (radice / percorso).write_text("a\n")


@pytest.mark.parametrize("percorso", FILE_CONFIG)
@pytest.mark.parametrize("strumento, ingresso", _SCRITTURE_CONFIG,
                         ids=[f"{s}-{i}" for i, (s, _) in enumerate(_SCRITTURE_CONFIG)])
def test_config_in_sola_lettura_in_campagna(campagna_btc, percorso, strumento, ingresso):
    _config_sul_disco(campagna_btc)
    codice, err = _esegui(campagna_btc, strumento, ingresso(percorso))
    assert codice == 2, f"BUCO: {strumento} {ingresso(percorso)} consentito"
    assert err.startswith(RIFIUTO), err


@pytest.mark.parametrize("comando", ["rm -rf research/config", "rm -r research/config/", "mv research/config x",
                                     "find research/config -delete", "cp -r research/campagne/BTCUSDT research/config"])
def test_config_cartella_intera_in_sola_lettura(campagna_btc, comando):
    _config_sul_disco(campagna_btc)
    assert _bash(campagna_btc, comando)[0] == 2


@pytest.mark.parametrize("percorso", FILE_CONFIG)
def test_config_si_legge_in_campagna(campagna_btc, percorso):
    _config_sul_disco(campagna_btc)
    assert _read(campagna_btc, percorso)[0] == 0
    for comando in (f"cat {percorso}", "ls research/config", "grep -r gruppo research/config",
                    f"head -5 {percorso}", f"sha256sum {percorso}", f"sort {percorso}",
                    f"diff {percorso} research/campagne/BTCUSDT/log.jsonl"):
        codice, err = _bash(campagna_btc, comando)
        assert codice == 0, f"{comando}: {err}"
    assert _esegui(campagna_btc, "Grep", {"pattern": "x", "path": "research/config"})[0] == 0
    assert _esegui(campagna_btc, "Glob", {"pattern": "*", "path": "research/config"})[0] == 0


def test_config_in_coordinamento_si_scrive_come_prima(coordinamento):
    _config_sul_disco(coordinamento)
    for percorso in FILE_CONFIG:
        assert _esegui(coordinamento, "Write", {"file_path": percorso, "content": "x"}) == (0, "")
        assert _bash(coordinamento, f"sed -i 's|a|b|' {percorso}") == (0, "")


# ---------------------------------------------------------------------------
# cio' che la sessione fa davvero resta ammesso (comandi senza git; quelli con git,
# in un repo vero, in test_guardiano_4_4.py e test_guardiano_gruppo.py)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "comando",
    [
        "python3 research/campagne/BTCUSDT/codice/x.py",
        "python3 research/campagne/BTCUSDT/codice/x.py --simbolo BTCUSDT --uscita=research/campagne/BTCUSDT/r.json",
        # (`2>&1` resta rifiutato come prima: lezioni/metodo.md lo sa)
        "nohup python3 research/campagne/BTCUSDT/codice/x.py > research/campagne/BTCUSDT/x.log &",
        "python -m pytest research/src/tests -q -p no:cacheprovider",
        "dd of=research/data/insample/BTCUSDT/x",
        "PYTHONHASHSEED=0 python3 script.py",
        "date -u",
        "ls research/campagne/BTCUSDT",
        "cat research/lezioni/metodo.md",
        "sha256sum research/data/insample/BTCUSDT/x.zip",
        "echo nota >> research/campagne/BTCUSDT/ipotesi.md",
        "find research/campagne/BTCUSDT -name '*.pyc' -delete",
        "find research/campagne/BTCUSDT/codice -name '*.py' -exec python3 {} \\;",
        "sort -o research/campagne/BTCUSDT/ordinato.txt research/campagne/BTCUSDT/log.jsonl",
        "cd research/campagne/BTCUSDT && sed -i 's|a|b|' log.jsonl",
        "cd research/data/insample/BTCUSDT && touch nuovo.csv",
    ],
)
def test_comandi_della_sessione_ammessi(campagna_btc, comando):
    codice, err = _bash(campagna_btc, comando)
    assert codice == 0, err
