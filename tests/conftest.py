import os
import sys

# rende importabile il package `bot` dalla root del repo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# forza modalità sicura/offline nei test
os.environ.setdefault("DRY_RUN", "true")
os.environ.setdefault("BINANCE_TESTNET", "true")
# i test costruiscono gli indicatori sullo slot "15m": teniamo il timeframe unico
# a 15m durante i test (in produzione il default e' 1h). Va impostato PRIMA che
# bot.config venga importato (il valore e' letto a def-time della classe Settings).
os.environ.setdefault("ORCHESTRATOR_TIMEFRAME", "15m")
