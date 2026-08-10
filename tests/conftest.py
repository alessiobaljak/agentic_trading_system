import os
import sys

# rende importabile il package `bot` dalla root del repo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ISOLAMENTO DALLA PRODUZIONE — deve stare PRIMA di qualunque import di `bot`.
# bot/config.py chiama load_dotenv(): lanciando pytest dalla cartella dell'app
# sulla VPS, il .env di produzione entrava nei test. I test assumono i default,
# quindi 14 di essi fallivano solo li' (scale-out attivo, leva e cap diversi,
# parita' backtest attiva). E soprattutto entrava FIREBASE_SERVICE_ACCOUNT: la
# suite si collegava al Firebase VERO, leggeva posizioni di produzione e avrebbe
# potuto scriverci. Questa variabile disattiva la lettura del .env.
os.environ["TRADING_BOT_TEST_MODE"] = "1"
# cintura di sicurezza: anche se qualcuno esportasse le credenziali nella shell,
# il client cade sullo store in-memory invece di toccare il Firebase reale.
os.environ["FIREBASE_SERVICE_ACCOUNT"] = ""

# forza modalità sicura/offline nei test
os.environ.setdefault("DRY_RUN", "true")
os.environ.setdefault("BINANCE_TESTNET", "true")
# i test costruiscono gli indicatori sullo slot "15m": teniamo il timeframe unico
# a 15m durante i test (in produzione il default e' 1h). Va impostato PRIMA che
# bot.config venga importato (il valore e' letto a def-time della classe Settings).
os.environ.setdefault("ORCHESTRATOR_TIMEFRAME", "15m")
