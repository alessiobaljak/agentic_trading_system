import json, time, sys, urllib.request, urllib.parse
OUT = sys.argv[1]
def get(path, params):
    url = "https://www.binance.com" + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())
start = int(time.mktime(time.strptime("2026-11-07", "%Y-%m-%d")) - time.timezone) * 1000
res = {}
for s in ["LITUSDT","EVAAUSDT","UAIUSDT","PIEVERSEUSDT","IRYSUSDT","龙虾USDT","ICPUSDT","BTCUSDT"]:
    k = get("/fapi/v1/markPriceKlines", {"symbol": s, "interval": "1h", "startTime": start, "limit": 500})
    f = get("/fapi/v1/fundingRate", {"symbol": s, "startTime": start, "limit": 1000})
    res[s] = {"k": k, "f": f}
    time.sleep(0.3)
json.dump(res, open(OUT, "w"))
print({s: (len(v["k"]), len(v["f"])) for s, v in res.items()})
