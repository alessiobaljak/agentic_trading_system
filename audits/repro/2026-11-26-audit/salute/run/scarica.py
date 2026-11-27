import json, sys, time, urllib.request, os
out = sys.argv[1]; monete = open(sys.argv[2]).read().split()
giorni = ["2026-11-20","2026-11-21","2026-11-22","2026-11-24","2026-11-25","2026-11-26"]
import calendar
n=0
for g in giorni:
    t0 = calendar.timegm(time.strptime(g, "%Y-%m-%d")) * 1000
    for s in monete:
        f = os.path.join(out, f"{s}_{g}.json")
        if os.path.exists(f): continue
        u = f"https://www.binance.com/fapi/v1/markPriceKlines?symbol={s}&interval=1m&startTime={t0}&limit=80"
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            d = urllib.request.urlopen(req, timeout=20).read()
            open(f, "wb").write(d); n+=1
        except Exception as e:
            print("errore", s, g, str(e)[:80])
        time.sleep(0.12)
print("scaricati", n)
