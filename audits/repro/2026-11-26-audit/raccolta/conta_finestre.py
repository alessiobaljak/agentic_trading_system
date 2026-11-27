import sys
sys.path.insert(0, "/home/user/agentic_trading_system")
from datetime import datetime, timedelta, timezone
from research.programma7.misure_g1 import voce14_lettura as v14
casi = [("fg", "2026-11-23 04:19", 173), ("fg", "2026-11-24 04:18", 552), ("fg", "2026-11-25 04:19", 555), ("fg", "2026-11-26 04:18", 548),
        ("v14", "2026-11-22 04:20", 204), ("v14", "2026-11-23 04:19", 173), ("v14", "2026-11-24 04:20", 551), ("v14", "2026-11-25 04:20", 554), ("v14", "2026-11-26 04:20", 548)]
for tipo, t, nel_foglio in casi:
    fine = datetime.strptime(t, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    arts = v14.articoli(fine)
    ultime4 = [a for q, a in arts if q >= fine - timedelta(hours=4)]
    # quanti visti DOPO la fine (raccolti dopo)
    visti_dopo = [a for q, a in arts if a.get("visto") and datetime.strptime(a["visto"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) >= fine]
    visti_dopo_ultime4 = [a for q, a in arts if q >= fine - timedelta(hours=4) and a.get("visto") and datetime.strptime(a["visto"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) >= fine]
    print(f"{tipo:4} {t} foglio={nel_foglio} oggi={len(arts)} mancano={len(arts)-nel_foglio} visti_dopo_fine={len(visti_dopo)} di_cui_ultime4h={len(visti_dopo_ultime4)} ultime4h_tot={len(ultime4)}")
