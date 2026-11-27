import json, sys, time, urllib.request, urllib.parse, calendar
OUT = sys.argv[1]
def get(path, params):
    url = "https://www.binance.com" + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            time.sleep(1 + i)
    raise RuntimeError(url)
t0 = calendar.timegm(time.strptime("2026-11-08 22:00", "%Y-%m-%d %H:%M")) * 1000
t1 = calendar.timegm(time.strptime("2026-11-26 05:00", "%Y-%m-%d %H:%M")) * 1000
res = {}
for s in ["LITUSDT", "EVAAUSDT", "UAIUSDT", "PIEVERSEUSDT", "IRYSUSDT", "龙虾USDT", "ICPUSDT"]:
    k, start = [], t0
    while start < t1:
        x = get("/fapi/v1/markPriceKlines", {"symbol": s, "interval": "5m", "startTime": start, "endTime": t1, "limit": 1500})
        if not x: break
        k += x; start = int(x[-1][0]) + 300000
        time.sleep(0.2)
    f = get("/fapi/v1/fundingRate", {"symbol": s, "startTime": t0, "endTime": t1, "limit": 1000})
    res[s] = {"k": k, "f": f}
json.dump(res, open(OUT, "w"))
print({s: (len(v["k"]), len(v["f"])) for s, v in res.items()})
