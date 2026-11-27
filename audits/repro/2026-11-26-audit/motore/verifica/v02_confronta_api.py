import json
from pathlib import Path
MIA = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore/verifica/api")
LORO = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati/api/funding_nov")
for s in ("BTCUSDT", "LITUSDT", "INJUSDT", "BNBUSDT", "TRXUSDT", "ETHFIUSDT"):
    a = {int(x["fundingTime"]): float(x["fundingRate"]) for x in json.load(open(MIA / f"fr_{s}.json"))}
    b = {int(x["fundingTime"]): float(x["fundingRate"]) for x in json.load(open(LORO / f"{s}.json"))}
    comuni = sorted(set(a) & set(b))
    diff = max(abs(a[t] - b[t]) for t in comuni) if comuni else None
    print(s, "miei", len(a), "loro", len(b), "comuni", len(comuni), "max diff", diff,
          "primo mio", min(a), "ultimo mio", max(a), "ultimo loro", max(b))
