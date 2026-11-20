# Perché G1 non guadagna nel ribasso del 18-19 novembre 2026 (domanda del proprietario del 20 novembre): il paper di G1 diviso fra
# lato comprato e lato venduto, giorno per giorno, con i pesi del paper (lettura delle 04:20 di ogni giorno, ops/results/0759 e 0761:
# il paper e' scritto ai prezzi del ribilancio) e i prezzi mark del mercato vero dalle 00:05 alle 00:05 del giorno dopo. Senza funding
# e spese. Uso (dalla radice): python3 research/programma7/misure_g1/voce12_ribasso_18_19nov.py
import json, re, time, urllib.request, urllib.parse, datetime as dt
GIORNI = [("2026-11-18", "ops/results/0759-18nov-stato-ribilancio-1000.md"), ("2026-11-19", "ops/results/0761-19nov-stato-ribilancio-1000.md")]
def mark(sym, ora):
    a = int(dt.datetime.fromisoformat(ora).timestamp() * 1000)
    u = f"https://www.binance.com/fapi/v1/markPriceKlines?symbol={urllib.parse.quote(sym)}&interval=1m&startTime={a}&limit=1"
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read())
    except Exception:
        return None
    return float(d[0][1]) if d else None
for giorno, f in GIORNI:
    t = open(f, encoding="utf-8").read().split("## G1 oggi")[1].split("\n## ")[0]
    celle = re.findall(r"(\S+USDT) ([+-]\d+\.\d+)/([+-]\d+\.\d+|—)", t)
    g = dt.date.fromisoformat(giorno); inizio = f"{giorno}T00:05:00+00:00"; fine = f"{g + dt.timedelta(days=1)}T00:05:00+00:00"
    lati = {"comprato": [], "venduto": []}; mancano = []
    for s, p, _ in celle:
        a, b = mark(s, inizio), mark(s, fine); time.sleep(0.05)
        if not (a and b):
            mancano.append(s); continue
        w = float(p) / 100; r = b / a - 1
        lati["comprato" if w > 0 else "venduto"].append((s, w, r, w * r))
    btc = mark("BTCUSDT", fine) / mark("BTCUSDT", inizio) - 1
    print(f"{giorno}: Bitcoin {100*btc:+.2f}%; monete lette {sum(len(v) for v in lati.values())} su {len(celle)}" + (f", senza prezzi {mancano}" if mancano else ""))
    for k, v in lati.items():
        peso = sum(x[1] for x in v); contr = sum(x[3] for x in v); media = sum(x[2] * abs(x[1]) for x in v) / sum(abs(x[1]) for x in v)
        peggio = sorted(v, key=lambda x: x[3])[:3]
        print(f"  lato {k}: {len(v)} monete, peso {100*peso:+.1f}%, movimento medio pesato {100*media:+.2f}%, contributo {100*contr:+.2f} punti;"
              f" i tre peggiori: " + ", ".join(f"{s} {100*c:+.2f} (peso {100*w:+.1f}, prezzo {100*r:+.1f}%)" for s, w, r, c in peggio))
    print(f"  totale da prezzo: {100*sum(x[3] for v in lati.values() for x in v):+.2f} punti")
