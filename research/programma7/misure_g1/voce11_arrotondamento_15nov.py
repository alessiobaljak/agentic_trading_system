# Il demo tiene posizioni un po' più piccole del paper: è l'arrotondamento delle quantità? Pesi dopo il ribilancio del 15 novembre
# (ops/results/0744, 04:18 UTC), passi delle quantità pubblici di Binance (exchangeInfo), prezzi mark pubblici alle 04:18.
# Uso (dalla radice): python3 research/programma7/misure_g1/voce11_arrotondamento_15nov.py (dati pubblici di Binance)
import json, re, math, urllib.request, urllib.parse, datetime as dt
t = open("ops/results/0744-15nov-stato-ribilancio-1000.md", encoding="utf-8").read().split("## G1 oggi")[1]
equity = float(re.search(r"conto ridotto \(([\d,\.]+) USDT\)", t).group(1).replace(",", ""))
celle = re.findall(r"(\S+USDT) ([+-]\d+\.\d+)/([+-]\d+\.\d+|—)", t)
def get(u):
    return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
info = {s["symbol"]: s for s in get("https://www.binance.com/fapi/v1/exchangeInfo")["symbols"]}
a = int(dt.datetime.fromisoformat("2026-11-15T04:18:00+00:00").timestamp() * 1000)
righe = []
for s, p, d in celle:
    p = float(p) / 100; dd = float(d) / 100 if d != "—" else None
    if dd is None or p == 0 or dd == 0 or s not in info:
        continue
    passo = float(next(f["stepSize"] for f in info[s]["filters"] if f["filterType"] == "MARKET_LOT_SIZE"))
    k = get(f"https://www.binance.com/fapi/v1/markPriceKlines?symbol={urllib.parse.quote(s)}&interval=1m&startTime={a}&limit=1")
    prezzo = float(k[0][1])
    q_voluta = abs(p) * equity / prezzo
    atteso = (q_voluta - math.floor(q_voluta / passo + 1e-9) * passo) * prezzo / equity      # quanto si perde arrotondando verso zero
    righe.append((s, abs(p), abs(dd), abs(p) - abs(dd), atteso, passo * prezzo / equity))
n = len(righe)
piu_piccolo = sum(1 for r in righe if r[3] > 0)
print(f"monete in tutti e due: {n}; il demo più piccolo del paper in {piu_piccolo}; differenza media {100*sum(r[3] for r in righe)/n:+.3f} punti, "
      f"attesa dall'arrotondamento {100*sum(r[4] for r in righe)/n:+.3f} punti (passo medio {100*sum(r[5] for r in righe)/n:.3f} punti)")
print(f"somma: differenza {100*sum(r[3] for r in righe):.2f} punti del conto, attesa dall'arrotondamento {100*sum(r[4] for r in righe):.2f}")
for r in sorted(righe, key=lambda r: -r[3])[:6]:
    print(f"  {r[0]}: paper {100*r[1]:.2f}, demo {100*r[2]:.2f}, differenza {100*r[3]:+.2f}, arrotondamento atteso {100*r[4]:.2f}, un passo vale {100*r[5]:.2f}")
