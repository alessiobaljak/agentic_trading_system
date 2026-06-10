import os
import sys

# rende importabile il package `bot` dalla root del repo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# forza modalità sicura/offline nei test
os.environ.setdefault("DRY_RUN", "true")
os.environ.setdefault("BINANCE_TESTNET", "true")
