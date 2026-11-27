import gzip, json, glob, collections
fs = sorted(glob.glob("/home/user/agentic_trading_system/research/notizie/archivio/2026-*.jsonl.gz"))
per_id = collections.defaultdict(list)
cb = []
for f in fs:
    with gzip.open(f, "rt") as g:
        for r in g:
            if not r.strip(): continue
            a = json.loads(r)
            per_id[a["id"]].append((f[-17:-9], a["fonte"], a["visto"], a["pubblicato"], a["titolo"][:60]))
            if a["fonte"].startswith("cryptobriefing"): cb.append(a)
for k, v in per_id.items():
    if len(v) > 1:
        print(k, v[0][1], [x[2] for x in v], v[0][3], v[0][4])
print()
# cryptobriefing titles sample
import random
random.seed(1)
for a in random.sample(cb, 15):
    print(a["fonte"], a["pubblicato"], a["titolo"][:100])
# pattern counts
pat = collections.Counter()
for a in cb:
    t = a["titolo"].lower()
    for w in ["price", "prediction", "polymarket", "odds", "kalshi", "bet", "traders", "%", "chance", "probability"]:
        if w in t: pat[w] += 1
print(len(cb), pat)
