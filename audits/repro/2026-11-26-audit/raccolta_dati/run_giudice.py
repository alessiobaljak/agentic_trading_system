import sys, json
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.trader_copiati import giudice_balene as gb
gb.USCITA = Path(sys.argv[2])
lun = datetime.strptime(sys.argv[1], "%Y-%m-%d").replace(tzinfo=timezone.utc)
md = gb.main(lun)
