# Attribuzione demo-paper del giorno per moneta (prezzi pubblici mark di Binance). Uso: python3 gate2/exports/attribuzione_posizioni_demo_paper.py AAAA-MM-GG ops/results/<stato>.md uscita.json  (dalla radice)
import json, re, time, sys, urllib.request, urllib.parse, datetime as dt
giorno, f = sys.argv[1], sys.argv[2]
t = open(f, encoding="utf-8").read().split("## G1 oggi")[1].split("\n## ")[0]
celle = re.findall(r"(\S+USDT) ([+-]\d+\.\d+)/([+-]\d+\.\d+|—)", t)
g = dt.date.fromisoformat(giorno); g2 = g + dt.timedelta(days=1)
LETTO, INIZIO, FINE = f"{giorno}T04:20:00+00:00", f"{giorno}T00:05:00+00:00", f"{g2}T00:05:00+00:00"
def mark(sym, ora):
    a = int(dt.datetime.fromisoformat(ora).timestamp() * 1000)
    u = f"https://www.binance.com/fapi/v1/markPriceKlines?symbol={urllib.parse.quote(sym)}&interval=1m&startTime={a}&limit=1"
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read())
    except Exception as e:
        return None
    return float(d[0][1]) if d else None
tot_p = tot_d = 0.0; contrib = []; mancano=[]
for s, p, d in celle:
    p = float(p) / 100; dd = float(d) / 100 if d != "—" else 0.0
    a, m, b = mark(s, INIZIO), mark(s, LETTO), mark(s, FINE)
    time.sleep(0.05)
    if not (a and m and b):
        mancano.append(s); continue
    d0 = dd / (m / a); r = b / a - 1
    tot_p += p * r; tot_d += d0 * r
    contrib.append((s, (d0 - p) * r, p, d0, r))
print(giorno, f"monete lette {len(contrib)} su {len(celle)}; senza prezzi: {mancano[:6]}")
print(f"paper {100*tot_p:+.2f}%, demo con i suoi pesi {100*tot_d:+.2f}%, differenza {100*(tot_d-tot_p):+.2f} punti")
print("pesano di piu:", ", ".join(f"{s} {100*c:+.2f} (peso {100*p:+.1f}/{100*d0:+.1f}, prezzo {100*r:+.1f}%)" for s, c, p, d0, r in sorted(contrib, key=lambda x: -abs(x[1]))[:6]))
json.dump(contrib, open(sys.argv[3],"w"))
