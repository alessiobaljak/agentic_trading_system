import sys
sys.path.insert(0, "/home/user/agentic_trading_system")
from datetime import datetime, timezone, timedelta
from research.trader_copiati import giudice_balene as gb
pos, prezzi = gb.giri(datetime(2026,11,2,tzinfo=timezone.utc), datetime(2026,11,30,tzinfo=timezone.utc))
ore = sorted(prezzi)
print("giri con prezzi", len(ore), ore[0], ore[-1])
for t in ore[::14] + [ore[-1]]:
    p = prezzi[t]
    print(t, {m: round(p.get(m, 0), 2) for m in ("BTC", "ETH", "SOL")}, "monete con prezzo", len(p), "conti", len(pos[t]))
