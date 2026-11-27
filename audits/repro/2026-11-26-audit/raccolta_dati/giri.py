import csv, sys, collections
from datetime import datetime, timedelta
f = "/home/user/agentic_trading_system/research/notizie/archivio/giri.csv"
rows = list(csv.DictReader(open(f)))
ore = sorted(set(r["ora"] for r in rows))
print("giri:", len(ore), "primo", ore[0], "ultimo", ore[-1])
# gaps
dt = [datetime.strptime(o, "%Y-%m-%d %H:%M") for o in ore]
gaps = [(dt[i-1], dt[i], (dt[i]-dt[i-1]).total_seconds()/3600) for i in range(1, len(dt))]
print("intervalli > 4.5h:")
for a,b,h in gaps:
    if h > 4.5:
        print("  ", a, "->", b, round(h,2), "h")
print("intervalli < 3h:")
for a,b,h in gaps:
    if h < 3:
        print("  ", a, "->", b, round(h,2), "h")
# per source: zero counts, piena counts
z = collections.Counter(); p = collections.Counter(); tot = collections.Counter()
for r in rows:
    tot[r["fonte"]] += 1
    if r["articoli"] == "0": z[r["fonte"]] += 1
    if r["nota"] == "piena": p[r["fonte"]] += 1
print("fonte, giri, vuote, piene")
for k in tot:
    print(f"  {k:18s} {tot[k]:4d} {z[k]:4d} {p[k]:4d}")
# piene after first day (excluding first round)
print("piene dopo il primo giro, per fonte e ora:")
for r in rows:
    if r["nota"] == "piena" and r["ora"] != ore[0]:
        print("  ", r["ora"], r["fonte"], r["articoli"], r["nuovi"])
