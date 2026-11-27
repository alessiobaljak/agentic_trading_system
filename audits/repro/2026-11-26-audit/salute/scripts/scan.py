import re, glob, sys, datetime
pat = re.compile(r"^(\w{3} \d{2} \d{2}:\d{2}:\d{2}) \S+ python\[(\d+)\]: \[main\] (market scan\.\.\.|valutate)")
seen = {}
inizio = None
durate = []
for f in sorted(glob.glob(sys.argv[1] + "/07[4-7]*log*.md")):
    for l in open(f, encoding="utf-8", errors="replace"):
        m = pat.match(l)
        if not m: continue
        ts = datetime.datetime.strptime("2026 " + m.group(1), "%Y %b %d %H:%M:%S")
        if m.group(3).startswith("market"):
            inizio = ts
        elif inizio is not None:
            d = (ts - inizio).total_seconds()
            if 0 < d < 3600 and (inizio not in seen):
                seen[inizio] = d
            inizio = None
vals = sorted(seen.items())
for k, v in vals[-12:]:
    print(k, f"{v:.0f} s")
import statistics
print("scan:", len(vals), "mediana s", statistics.median([v for _, v in vals]), "max", max(v for _, v in vals))
