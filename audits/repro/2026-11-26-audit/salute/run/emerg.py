import os, sys
os.environ["TRADING_BOT_TEST_MODE"] = "1"
sys.path.insert(0, "/home/user/agentic_trading_system")
sys.dont_write_bytecode = True
from bot.main import TradingBot
class N:
    def __init__(s): s.msgs=[]
    def send(s, t): s.msgs.append(t)
class F:
    def __init__(s): s.w=[]
    def set_rtdb(s, p, v): s.w.append((p, v))
class E:
    open_positions = {}
    def force_close_all(s, prices, reason): return []
b = object.__new__(TradingBot)
b.executor = E(); b.notifier = N(); b.fb = F()
b._settle_realized = lambda: None
b._log_closed = lambda t: None
for _ in range(3):
    b._emergency_close()
print(len(b.notifier.msgs), "messaggi;", len(b.fb.w), "scritture")
print(b.notifier.msgs[0].splitlines()[:3])
print(b.fb.w[:3])
