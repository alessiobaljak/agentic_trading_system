import os, sys, types
os.environ["TRADING_BOT_TEST_MODE"] = "1"; os.environ["FIREBASE_SERVICE_ACCOUNT"] = ""
os.environ.setdefault("DRY_RUN", "true"); os.environ.setdefault("BINANCE_TESTNET", "true")
sys.path.insert(0, "/home/user/agentic_trading_system")
from bot.main import TradingBot
inviati, scritti = [], []
stub = types.SimpleNamespace(
    executor=types.SimpleNamespace(open_positions={}, force_close_all=lambda prices, reason: []),
    _mark_for=lambda s: None, _settle_realized=lambda: None, _log_closed=lambda t: None,
    notifier=types.SimpleNamespace(send=lambda t: inviati.append(t)),
    fb=types.SimpleNamespace(set_rtdb=lambda p, v: scritti.append((p, v))))
for _ in range(3):          # tre giri del ciclo con lo stato EMERGENCY e nessuna posizione
    TradingBot._emergency_close(stub)
print("messaggi inviati:", len(inviati), "| scritture RTDB:", len(scritti))
print(inviati[0].splitlines()[:3])
