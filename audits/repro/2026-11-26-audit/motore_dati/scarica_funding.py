import json, time, urllib.request, sys
from pathlib import Path
QUI = Path(__file__).parent
u = json.load(open(QUI / "universi_nov.json"))["unione"]
dest = QUI / "api" / "funding_nov"; dest.mkdir(parents=True, exist_ok=True)
start = 1759276800000  # 2026-10-01? computed below
import datetime
start = int(datetime.datetime(2026, 10, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)
for s in u:
    f = dest / f"{s}.json"
    if f.exists(): continue
    out = []
    st = start
    for _ in range(5):
        url = f"https://www.binance.com/fapi/v1/fundingRate?symbol={s}&startTime={st}&limit=1000"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=30))
        except Exception as e:
            print(s, "errore", e); d = []
        if not isinstance(d, list) or not d: break
        out += d
        if len(d) < 1000: break
        st = int(d[-1]["fundingTime"]) + 1
    f.write_text(json.dumps(out))
    time.sleep(0.15)
print("fatto", len(u))
