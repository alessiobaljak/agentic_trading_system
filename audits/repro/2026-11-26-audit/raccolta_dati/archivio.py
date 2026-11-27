import gzip, json, glob, collections, statistics
from datetime import datetime
fs = sorted(glob.glob("/home/user/agentic_trading_system/research/notizie/archivio/2026-*.jsonl.gz"))
n = 0; perfonte = collections.Counter(); futuro = collections.Counter(); nopub = collections.Counter()
ritardi = collections.defaultdict(list); ids = collections.Counter(); links = collections.Counter()
titoli = collections.Counter(); fonte_titolo = collections.Counter()
for f in fs:
    with gzip.open(f, "rt") as g:
        for r in g:
            if not r.strip(): continue
            a = json.loads(r); n += 1
            fo = a["fonte"]; perfonte[fo] += 1
            ids[a["id"]] += 1
            links[a["link"]] += 1
            titoli[(a["titolo"])] += 1
            if not a.get("pubblicato"):
                nopub[fo] += 1; continue
            p = datetime.strptime(a["pubblicato"], "%Y-%m-%d %H:%M:%S"); v = datetime.strptime(a["visto"], "%Y-%m-%d %H:%M:%S")
            d = (v - p).total_seconds()/3600
            ritardi[fo].append(d)
            if d < -0.05: futuro[fo] += 1
print("articoli totali", n, "file", len(fs))
print("id doppi:", sum(1 for k,v in ids.items() if v>1), "link doppi:", sum(1 for k,v in links.items() if v>1))
print("titoli doppi (stesso titolo, link diversi):", sum(v-1 for k,v in titoli.items() if v>1))
print("fonte, articoli, senza ora, nel futuro, ritardo mediano h, min h")
for fo in perfonte:
    rr = ritardi[fo]
    print(f"  {fo:18s} {perfonte[fo]:6d} {nopub[fo]:5d} {futuro[fo]:5d} {statistics.median(rr) if rr else float('nan'):8.2f} {min(rr) if rr else float('nan'):8.2f}")
