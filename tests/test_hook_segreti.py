"""L'hook dei segreti (.claude/hooks/segreti.py): blocca i file di segreti, l'ambiente intero e il remoto di git in ogni sessione e in
ogni subagent, e lascia passare i comandi normali del lavoro di ogni giorno."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "segreti.py"
spec = importlib.util.spec_from_file_location("segreti", HOOK)
seg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seg)

BLOCCATI = [
    ("Bash", "cat .env"),
    ("Bash", "python3 -c \"print(open('/root/agentic_trading_system/.env').read())\""),
    ("Bash", "xxd .env | head"),
    ("Bash", "cp tuning.env /tmp/x"),
    ("Bash", "cat .env.local"),
    ("Bash", "cat firebase-service-account.json"),
    ("Bash", "openssl pkey -in chiave.pem -text"),
    ("Bash", "cat ~/.git-credentials"),
    ("Bash", "cat ~/.ssh/id_ed25519"),
    ("Bash", "env"),
    ("Bash", "env | grep KEY"),
    ("Bash", "cd x && printenv"),
    ("Bash", "cat /proc/self/environ"),
    ("Bash", "python3 -c 'import os; print(os.environ)'"),
    ("Bash", "git remote -v"),
    ("Bash", "git config --list"),
    ("Read", {"file_path": "/home/user/agentic_trading_system/.env"}),
    ("Read", {"file_path": "/x/firebase-service-account.json"}),
    ("Grep", {"pattern": "KEY", "path": ".env"}),
]
PERMESSI = [
    ("Bash", "cat .env.example"),
    ("Bash", ".venv/bin/python -m pytest -q"),
    ("Bash", "python3 -m research.notizie.raccolta"),
    ("Bash", "grep -n environment docs/state.md"),
    ("Bash", "CACHE_G1N=/tmp/x python3 -m research.programma7.ottantaseiesima"),
    ("Bash", "git log --oneline -3"),
    ("Bash", "git push -q origin HEAD:claude/brave-albattani-1b12fv"),
    ("Bash", "python3 -c \"import os; print(os.environ.get('CACHE_G1N'))\""),
    ("Bash", "grep -rn load_dotenv bot/config.py"),
    ("Read", {"file_path": "/home/user/agentic_trading_system/bot/portafoglio/demo_binance.py"}),
    ("Read", {"file_path": "/home/user/agentic_trading_system/.env.example"}),
    ("Glob", {"pattern": "**/*.py"}),
]


def _ingresso(x):
    return x if isinstance(x, dict) else {"command": x}


@pytest.mark.parametrize("strumento,x", BLOCCATI)
def test_bloccati(strumento, x):
    assert seg.motivo(strumento, _ingresso(x)), x


@pytest.mark.parametrize("strumento,x", PERMESSI)
def test_permessi(strumento, x):
    assert seg.motivo(strumento, _ingresso(x)) == "", x


def test_come_hook_vero():
    def gira(dati):
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(dati), capture_output=True, text=True)
    r = gira({"tool_name": "Bash", "tool_input": {"command": "cat .env"}})
    assert r.returncode == 2 and "segreti" in r.stderr
    assert gira({"tool_name": "Bash", "tool_input": {"command": "ls"}}).returncode == 0
    assert subprocess.run([sys.executable, str(HOOK)], input="non e' json", capture_output=True, text=True).returncode == 0
