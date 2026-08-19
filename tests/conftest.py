import os
import re
import sys

# rende importabile il package `bot` dalla root del repo
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

# --------------------------------------------------------------------------- #
# ISOLAMENTO DALLA PRODUZIONE — deve stare PRIMA di qualunque import di `bot`.  #
# --------------------------------------------------------------------------- #
# Prima difesa: bot/config.py chiama load_dotenv(). Lanciando pytest dalla cartella
# dell'app sulla VPS, il .env di produzione entrava nei test. Questa variabile lo
# disattiva, e soprattutto tiene fuori FIREBASE_SERVICE_ACCOUNT: senza, la suite si
# collegava al Firebase VERO, leggeva posizioni di produzione e avrebbe potuto
# scriverci.
os.environ["TRADING_BOT_TEST_MODE"] = "1"
os.environ["FIREBASE_SERVICE_ACCOUNT"] = ""

# SECONDA DIFESA, ed e' quella che mancava. Disattivare dotenv non serve a niente se
# le variabili sono GIA' nell'ambiente del processo — ed e' esattamente il caso sulla
# VPS, dove le unit systemd hanno `EnvironmentFile=.env`: i valori arrivano
# dall'ambiente, non dal file, e passano indisturbati.
#
# Il risultato era che la suite falliva 11 test sulla macchina e nessuno qui, per
# ragioni di configurazione (scale-out attivo, cap di rischio diversi). Un suite che
# e' rossa per default sulla macchina non e' una rete di sicurezza: e' rumore, e chi
# la lancia non sa piu' distinguere una regressione vera da uno scarto di
# configurazione. Il canale ops, che serve proprio a fare verifiche da lontano,
# ereditava lo stesso ambiente e restituiva lo stesso rosso.
#
# Si cancellano quindi TUTTE le variabili che il codice legge come configurazione. La
# lista non e' scritta a mano: si ricava dai sorgenti, cosi' una impostazione aggiunta
# domani e' neutralizzata senza che nessuno debba ricordarsene.
_SORGENTI = (
    "bot/config.py",
    "scripts/optimize.py",
    "scripts/gate_progress.py",
    "backtesting/engine.py",
    "backtesting/data_loader.py",
)
_MAI_TOCCARE = {
    "PATH", "HOME", "USER", "LOGNAME", "SHELL", "LANG", "LC_ALL", "PWD", "TMPDIR",
    "PYTHONPATH", "PYTHONUNBUFFERED", "VIRTUAL_ENV", "TERM", "CI",
    "TRADING_BOT_TEST_MODE", "FIREBASE_SERVICE_ACCOUNT",
}
_NOME = re.compile(r"os\.(?:getenv|environ\.get)\(\s*[\"']([A-Z][A-Z0-9_]*)[\"']")

_letti: set[str] = set()
for _rel in _SORGENTI:
    try:
        with open(os.path.join(ROOT, _rel), encoding="utf-8") as _f:
            _letti.update(_NOME.findall(_f.read()))
    except OSError:
        pass                      # sorgente spostato: si perde una difesa, non la suite

for _nome in _letti - _MAI_TOCCARE:
    os.environ.pop(_nome, None)

# --------------------------------------------------------------------------- #
# Configurazione ESPLICITA dei test                                            #
# --------------------------------------------------------------------------- #
# Dopo la pulizia, `setdefault` e' di fatto un assegnamento: e' voluto. I test devono
# girare su una configurazione dichiarata qui, non su quella che capita.
os.environ.setdefault("DRY_RUN", "true")
os.environ.setdefault("BINANCE_TESTNET", "true")
# i test costruiscono gli indicatori sullo slot "15m": teniamo il timeframe unico
# a 15m durante i test. Va impostato PRIMA che bot.config venga importato (il valore
# e' letto a def-time della classe Settings).
os.environ.setdefault("ORCHESTRATOR_TIMEFRAME", "15m")
