import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.notizie import fatti_gravi as fg
fg.FOGLI = Path(sys.argv[2])
fg.RADICE = Path("/")
ora = datetime.strptime(sys.argv[1], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
out = fg.main(ora)
