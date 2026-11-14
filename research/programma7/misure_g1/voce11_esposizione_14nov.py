# Il paper di G1 portato ai prezzi delle 16:41 del 14 novembre: quanto dell'esposizione 200% → 179% del demo è movimento dei prezzi.
# Uso (dalla radice del repository): python3 research/programma7/misure_g1/voce11_esposizione_14nov.py (prezzi mark pubblici di Binance)
import json, re, sys, time, urllib.request, urllib.parse, datetime as dt
testo = open("ops/results/0742-14nov-stato-pesi-di-oggi.md", encoding="utf-8").read()
celle = re.findall(r"(\S+USDT) ([+-]\d+\.\d+)/([+-]\d+\.\d+|—)", testo.split("## G1 oggi")[1])
def mark(sym, ora):
    a = int(dt.datetime.fromisoformat(ora).timestamp() * 1000)
    u = f"https://www.binance.com/fapi/v1/markPriceKlines?symbol={urllib.parse.quote(sym)}&interval=1m&startTime={a}&limit=1"
    d = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read())
    return float(d[0][1]) if d else None
tot_p = tot_pa = tot_d = 0.0; righe = []
for s, p, d in celle:
    p = float(p) / 100; dd = float(d) / 100 if d != "—" else 0.0
    if p == 0: tot_d += abs(dd); continue
    a, b = mark(s, "2026-11-14T00:05:00+00:00"), mark(s, "2026-11-14T16:41:00+00:00")
    r = b / a if a and b else 1.0
    pa = p * r
    tot_p += abs(p); tot_pa += abs(pa); tot_d += abs(dd)
    righe.append((s, p, pa, dd))
    time.sleep(0.1)
print(f"paper ai prezzi del ribilancio {100*tot_p:.1f}%, paper portato alle 16:41 {100*tot_pa:.1f}%, demo {100*tot_d:.1f}%")
dif = [(s, pa - dd) for s, p, pa, dd in righe]
print("somma |paper alle 16:41 - demo|", f"{100*sum(abs(x) for _, x in dif):.1f}%")
print("le 8 differenze più grandi:", ", ".join(f"{s} {100*x:+.2f}" for s, x in sorted(dif, key=lambda t: -abs(t[1]))[:8]))
