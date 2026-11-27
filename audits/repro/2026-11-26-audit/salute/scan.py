import glob, re, datetime, statistics
ev = {}
for f in sorted(glob.glob("ops/results/0[67]*log*.md")):
    for line in open(f, encoding="utf-8"):
        m = re.match(r"(\w{3} \d+ \d\d:\d\d:\d\d) \S+ python\[\d+\]: (.*)", line)
        if not m: continue
        t = datetime.datetime.strptime("2026 "+m.group(1), "%Y %b %d %H:%M:%S")
        msg = m.group(2)
        if msg.startswith("[main] market scan"): ev[(t,"S")] = 1
        elif msg.startswith("[main] valutate"): ev[(t,"E")] = 1
        elif "openInterest fallito" in msg:
            mm = re.search(r"symbol=(\w+)", msg); ev[(t,"OI:"+(mm.group(1) if mm else "?"))] = 1
evs = sorted(ev)
durs = []; starts=[]
for i,(t,k) in enumerate(evs):
    if k=="S":
        starts.append(t)
        for t2,k2 in evs[i+1:]:
            if k2=="E":
                d=(t2-t).total_seconds()
                if d<600: durs.append(d)
                break
            if k2=="S": break
print("scansioni con fine:", len(durs), "mediana", statistics.median(durs), "max", max(durs), "min", min(durs))
from collections import Counter
c = Counter(k for t,k in evs if k.startswith("OI:"))
print(c)
print([s.strftime("%m-%d %H:%M:%S") for s in starts if s.hour==23])
