import sys, json, gzip, glob, re, collections
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.notizie import raccolta
e = json.load(open("/home/user/agentic_trading_system/research/notizie/nomi_2026-11.json"))["elenco"]
scelte = ["ANTUSDT", "ARKUSDT", "HIVEUSDT", "GENIUSUSDT", "1000SATSUSDT", "APRUSDT", "ERAUSDT"]
sub = {s: e[s] for s in scelte if s in e}
cnt = collections.Counter(); es = collections.defaultdict(list)
for f in sorted(glob.glob("/home/user/agentic_trading_system/research/notizie/archivio/2026-11-*.jsonl.gz")):
    for r in gzip.open(f, "rt"):
        a = json.loads(r); t = a["titolo"] + " " + a["sommario"]
        for s in raccolta.citate(t, sub):
            cnt[s] += 1
            if len(es[s]) < 4: es[s].append(a["titolo"][:90])
for s in scelte:
    print(s, sub.get(s), cnt[s], es[s][:4])
