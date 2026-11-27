"""Quanto conta che il paper controlli l'esecuzione degli ordini limite dalle 00:05 (inizio del giro) invece che dall'ora del prezzo
(~00:09:30): ordini ipotetici di acquisto e vendita al prezzo mark delle 00:09 su monete di G1, 18 giorni, candele mark a 1 minuto
pubbliche di Binance (mercato vero)."""
import json, sys, time, calendar, urllib.request, urllib.parse
MONETE = ["WLFIUSDT","TRXUSDT","XMRUSDT","HYPEUSDT","AEROUSDT","1000SHIBUSDT","RENDERUSDT","XLMUSDT","BCHUSDT","FARTCOINUSDT",
          "ASTERUSDT","ADAUSDT","XPLUSDT","NEARUSDT","ETHFIUSDT","SANDUSDT","GRASSUSDT","SEIUSDT","GTCUSDT","FETUSDT","1000BONKUSDT",
          "WLDUSDT","APTUSDT","TIAUSDT","1000PEPEUSDT","JUPUSDT","VVVUSDT","BEATUSDT","OPUSDT","INJUSDT"]
def get(path, params):
    url = "https://www.binance.com" + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    for prova in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except Exception as exc:
            time.sleep(1 + prova)
    return None
out = {}
for g in range(18):
    giorno = calendar.timegm(time.strptime("2026-11-09", "%Y-%m-%d")) + g * 86400
    for s in MONETE:
        k = get("/fapi/v1/markPriceKlines", {"symbol": s, "interval": "1m", "startTime": (giorno + 300) * 1000,
                                             "endTime": (giorno + 4200) * 1000, "limit": 70})
        out[f"{s}|{giorno}"] = k
        time.sleep(0.12)
json.dump(out, open(sys.argv[1], "w"))
print("scaricati", sum(1 for v in out.values() if v), "su", len(out))
