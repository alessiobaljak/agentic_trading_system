"""Il blocco delle aree (`.claude/hooks/aree.py`, richiesta del proprietario dell'11 novembre 2026): ogni sessione scrive solo nella
sua area e nei file in comune; leggere e' sempre permesso."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RADICE = Path(__file__).resolve().parents[1]
HOOK = RADICE / ".claude" / "hooks" / "aree.py"
sys.path.insert(0, str(HOOK.parent))
import aree  # noqa: E402

MAPPA = aree.carica()
R = str(RADICE)


def _m(strumento, x, area):
    ingresso = x if isinstance(x, dict) else {"command": x}
    return aree.motivo(strumento, ingresso, area, MAPPA, R)


def test_la_mappa_conosce_le_due_sessioni():
    assert MAPPA["sessioni"]["01Cp2h5z2VoCmU6nnMGp1yEh"] == "crypto"
    assert MAPPA["sessioni"]["017Vw3XC56GxQ5Fj3d48vf6H"] == "stock"


@pytest.mark.parametrize("rel,chi", [
    ("bot/main.py", "crypto"), ("research/REGISTRO.md", "crypto"), ("ops/requests/x.req", "crypto"), ("docs/andremo_live.md", "crypto"),
    ("stock/avanti/a.py", "stock"), ("dashboard/app/components/stock/Azioni.tsx", "stock"),
    ("dashboard/app/page.tsx", "comune"), ("dashboard/prova/dati.ts", "comune"), (".github/workflows/x.yml", "comune"),
    ("AREE.json", "comune"), ("CLAUDE.md", "comune"), (".claude/settings.json", "comune"),
])
def test_proprietario(rel, chi):
    assert aree.proprietario(rel, MAPPA) == chi


@pytest.mark.parametrize("strumento,x", [
    ("Write", {"file_path": f"{R}/bot/portafoglio/f5.py"}),
    ("Edit", {"file_path": f"{R}/research/REGISTRO.md"}),
    ("Write", {"file_path": f"{R}/dashboard/app/page.tsx"}),
    ("Write", {"file_path": "/tmp/claude-0/scratchpad/x.py"}),
    ("Bash", "cat >> docs/andremo_live.md <<'EOF'\nrm stock/x\nEOF"),
    ("Bash", "git add research/notizie research/trader_copiati && git commit -q -m \"a > stock/b\""),
    ("Bash", "cat stock/README.md > /tmp/claude-0/x.txt"),
    ("Bash", "grep -n x stock/README.md"),
])
def test_crypto_scrive_le_sue_cartelle_e_le_comuni(strumento, x):
    assert _m(strumento, x, "crypto") == "", x


@pytest.mark.parametrize("strumento,x", [
    ("Write", {"file_path": f"{R}/stock/avanti/a.py"}),
    ("Edit", {"file_path": f"{R}/dashboard/app/components/stock/Azioni.tsx"}),
    ("Bash", "echo x > stock/nota.md"),
    ("Bash", "rm -rf stock/avanti/giorni"),
    ("Bash", "git add stock/avanti"),
    ("Bash", "cp /tmp/a.py dashboard/app/components/stock/a.tsx"),
    ("Bash", "sed -i 's/a/b/' stock/README.md"),
])
def test_crypto_non_scrive_le_azioni(strumento, x):
    assert "area «stock»" in _m(strumento, x, "crypto"), x


@pytest.mark.parametrize("strumento,x,bloccato", [
    ("Write", {"file_path": f"{R}/stock/avanti/a.py"}, False),
    ("Write", {"file_path": f"{R}/dashboard/app/components/stock/Operazioni.tsx"}, False),
    ("Write", {"file_path": f"{R}/.github/workflows/stock.yml"}, False),
    ("Write", {"file_path": f"{R}/bot/main.py"}, True),
    ("Edit", {"file_path": f"{R}/research/REGISTRO.md"}, True),
    ("Bash", "echo x >> docs/andremo_live.md", True),
    ("Bash", "git add ops/requests/0800-x.req", True),
])
def test_stock_scrive_solo_le_sue_cartelle(strumento, x, bloccato):
    assert bool(_m(strumento, x, "stock")) is bloccato, x


def test_sessione_non_registrata_scrive_solo_i_comuni():
    assert _m("Write", {"file_path": f"{R}/dashboard/app/page.tsx"}, None) == ""
    assert "non ha un'area registrata" in _m("Write", {"file_path": f"{R}/bot/main.py"}, None)
    assert "non ha un'area registrata" in _m("Write", {"file_path": f"{R}/stock/a.py"}, None)


def test_come_hook_vero():
    def gira(sessione, dati):
        amb = dict(os.environ)
        amb.pop("CLAUDE_CODE_REMOTE_SESSION_ID", None)
        if sessione:
            amb["CLAUDE_CODE_REMOTE_SESSION_ID"] = sessione
        return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(dati), capture_output=True, text=True, env=amb)
    scrivi_stock = {"tool_name": "Write", "tool_input": {"file_path": f"{R}/stock/x.md"}, "cwd": R}
    r = gira("cse_01Cp2h5z2VoCmU6nnMGp1yEh", scrivi_stock)
    assert r.returncode == 2 and "[aree]" in r.stderr
    assert gira("cse_017Vw3XC56GxQ5Fj3d48vf6H", scrivi_stock).returncode == 0
    assert gira("", scrivi_stock).returncode == 0                          # fuori da una sessione remota: niente blocco
    assert subprocess.run([sys.executable, str(HOOK)], input="non e' json", capture_output=True, text=True).returncode == 0
