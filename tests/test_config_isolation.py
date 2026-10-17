"""La suite non deve vedere la configurazione di produzione.

Motivo concreto: `bot/config.py` chiama `load_dotenv()`, che legge il .env della
directory corrente. Lanciando pytest dalla cartella dell'app sulla VPS, l'intera
configurazione live entrava nei test — che assumono i default — e 14 test
fallivano solo su quella macchina. Peggio ancora entrava
FIREBASE_SERVICE_ACCOUNT: la suite si collegava al Firebase VERO, tanto che un
test ha trovato una posizione di produzione aperta e avrebbe potuto scriverci.

Questi test falliscono se l'isolamento si rompe di nuovo.
"""
import os
import subprocess
import sys

from bot.config import settings
from bot.core.firebase_client import FirebaseClient


def test_test_mode_flag_is_set_before_config_import():
    assert os.environ.get("TRADING_BOT_TEST_MODE") == "1"


def test_firebase_is_never_the_real_one_in_tests():
    assert settings.FIREBASE_SERVICE_ACCOUNT == ""
    fb = FirebaseClient()
    # store in-memory: scrivere qui non puo' raggiungere la produzione
    fb.set_doc("__isolation__", "probe", {"v": 1})
    assert fb.get_doc("__isolation__", "probe") == {"v": 1}


def test_dry_run_is_on():
    assert settings.DRY_RUN is True


def test_env_file_is_not_loaded(tmp_path):
    """Con TRADING_BOT_TEST_MODE impostata, un .env presente non deve entrare.

    Si usa un SOTTOPROCESSO e non importlib.reload: ricaricare bot.config nel
    processo dei test sostituisce l'oggetto `settings`, mentre gli altri moduli
    tengono un riferimento a quello vecchio -> test successivi rotti a caso.
    """
    (tmp_path / ".env").write_text("MAX_OPEN_POSITIONS=999\n")
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    code = ("import os,sys;sys.path.insert(0,%r);"
            "import bot.config;"
            "print(os.getenv('MAX_OPEN_POSITIONS'))" % repo)

    env = {**os.environ, "TRADING_BOT_TEST_MODE": "1"}
    out = subprocess.run([sys.executable, "-c", code], cwd=tmp_path, env=env,
                         capture_output=True, text=True, timeout=120)
    assert out.stdout.strip().endswith("None"), \
        f"il .env e' stato letto nonostante TRADING_BOT_TEST_MODE: {out.stdout!r}"

    # controprova: SENZA il flag il .env viene letto (cioe' il test sopra e'
    # sensibile davvero, e non passa perche' load_dotenv non funziona mai)
    env.pop("TRADING_BOT_TEST_MODE")
    out2 = subprocess.run([sys.executable, "-c", code], cwd=tmp_path, env=env,
                          capture_output=True, text=True, timeout=120)
    assert out2.stdout.strip().endswith("999"), \
        f"controprova fallita: load_dotenv non legge il .env ({out2.stdout!r})"
