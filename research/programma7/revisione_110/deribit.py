import json, time, urllib.request, urllib.parse, datetime as dt, os
BASE = "https://history.deribit.com/api/v2/public/"
def get(meth, **p):
    u = BASE + meth + "?" + urllib.parse.urlencode(p)
    for k in range(5):
        try:
            with urllib.request.urlopen(u, timeout=60) as r:
                return json.load(r)["result"]
        except Exception as e:
            time.sleep(2 + 3 * k)
    raise RuntimeError(u)

def trades_window(cur, t0, t1, cache_dir="/tmp/revisore110/dati/trades"):
    os.makedirs(cache_dir, exist_ok=True)
    f = f"{cache_dir}/{cur}_{t0}_{t1}.json"
    if os.path.exists(f):
        return json.load(open(f))
    out, a = [], t0
    seen = set()
    while True:
        r = get("get_last_trades_by_currency_and_time", currency=cur, kind="option", start_timestamp=a, end_timestamp=t1,
                count=1000, include_old="true", sorting="asc")
        tr = r["trades"]
        for x in tr:
            if x["trade_id"] not in seen:
                seen.add(x["trade_id"]); out.append(x)
        if not r.get("has_more") or not tr:
            break
        nxt = tr[-1]["timestamp"]
        if nxt <= a:
            nxt = a + 1
        a = nxt
        time.sleep(0.15)
    json.dump(out, open(f, "w"))
    return out
