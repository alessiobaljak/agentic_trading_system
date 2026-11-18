# Il 17 novembre moneta per moneta: quanto dello scarto demo − paper (−0,62 punti, ops/results/0759) viene dalle posizioni diverse.
# Stesso metodo di voce11_attribuzione_14nov.py. Pesi: lettura delle 04:20 del 17 novembre (ops/results/0756); il demo riportato ai
# prezzi delle 00:05 dividendo per il movimento. Uso (dalla radice): python3 research/programma7/misure_g1/voce11_attribuzione_17nov.py
import json, re, time, urllib.request, urllib.parse, datetime as dt
t = open("ops/results/0756-17nov-stato-ribilancio-1000.md", encoding="utf-8").read().split("## G1 oggi")[1].split("\n## ")[0]
celle = re.findall(r"(\S+USDT) ([+-]\d+\.\d+)/([+-]\d+\.\d+|—)", t)
LETTO, INIZIO, FINE = "2026-11-17T04:20:00+00:00", "2026-11-17T00:05:00+00:00", "2026-11-18T00:05:00+00:00"
def mark(sym, ora):
    a = int(dt.datetime.fromisoformat(ora).timestamp() * 1000)
    u = f"https://www.binance.com/fapi/v1/markPriceKlines?symbol={urllib.parse.quote(sym)}&interval=1m&startTime={a}&limit=1"
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read())
    except Exception:
        return None
    return float(d[0][1]) if d else None
tot_p = tot_d = 0.0; contrib = []
for s, p, d in celle:
    p = float(p) / 100; dd = float(d) / 100 if d != "—" else 0.0
    a, m, b = mark(s, INIZIO), mark(s, LETTO), mark(s, FINE)
    time.sleep(0.05)
    if not (a and m and b):
        print("senza prezzi:", s, p, dd); continue
    d0 = dd / (m / a)
    r = b / a - 1
    tot_p += p * r; tot_d += d0 * r
    contrib.append((s, (d0 - p) * r, p, d0, r))
print(f"monete lette {len(contrib)} su {len(celle)}")
print(f"dal mark delle 00:05 del 17 a quello delle 00:05 del 18: paper {100*tot_p:+.2f}%, demo con i suoi pesi {100*tot_d:+.2f}%, differenza {100*(tot_d-tot_p):+.2f} punti")
print("le monete che pesano di più nella differenza:", ", ".join(f"{s} {100*c:+.2f} (peso {100*p:+.1f}/{100*d0:+.1f}, prezzo {100*r:+.1f}%)" for s, c, p, d0, r in sorted(contrib, key=lambda x: -abs(x[1]))[:6]))
