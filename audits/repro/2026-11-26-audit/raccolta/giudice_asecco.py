import sys
sys.path.insert(0, "/home/user/agentic_trading_system")
from pathlib import Path
from datetime import datetime, timezone
from research.trader_copiati import giudice_balene as gb
gb.USCITA = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/raccolta/giudice_out")
import json
for d in ("2026-11-23", "2026-11-30"):
    l = datetime.strptime(d, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    gb.main(l)
    dd = json.load(open(gb.USCITA / f"{d}.json"))
    dentro = [x for x in dd if not x["fuori"]]
    # da dove vengono i giudicabili
    sc = set()
    for f in Path("/home/user/agentic_trading_system/research/trader_copiati/hyperliquid").glob("scelti_*.json"):
        sc |= {c["indirizzo"] for c in json.load(open(f))["conti"]}
    print("   giudicabili dai file scelti_*:", sum(1 for x in dentro if x["indirizzo"] in sc), "su", len(dentro),
          "; motivi fuori (giorni<10):", sum(1 for x in dd if x["giorni"] < 10), "conti letti:", len(dd))
    nette = sorted(x["netta_media_su_conto"] for x in dentro)
    print("   netta media su conto: min %.2f max %.2f" % (nette[0], nette[-1]) if nette else "")
