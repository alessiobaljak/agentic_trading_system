import sys, json, gzip, glob, re, collections
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.notizie import raccolta
e = json.load(open("/home/user/agentic_trading_system/research/notizie/nomi_2026-11.json"))["elenco"]
arts = []
for f in sorted(glob.glob("/home/user/agentic_trading_system/research/notizie/archivio/2026-11-*.jsonl.gz")):
    for r in gzip.open(f, "rt"):
        a = json.loads(r); arts.append(a["titolo"] + " " + a["sommario"])
tok = re.compile(r"(?<![A-Za-z0-9])([A-Za-z0-9]+)(?![A-Za-z0-9])")
dollar = re.compile(r"\$([A-Za-z0-9]+)\b")
sig_by = collections.defaultdict(list)
for s, x in e.items():
    sig_by[x["sigla"]].append(s)
cnt = collections.Counter(); esempi = collections.defaultdict(list)
for t in arts:
    toks = set(tok.findall(t)); dl = {d.upper() for d in dollar.findall(t)}
    for sig, ss in sig_by.items():
        ok = sig.upper() in dl or (len(sig) >= 3 and sig not in raccolta.PAROLE and sig in toks)
        if ok:
            for s in ss:
                cnt[s] += 1
                if len(esempi[s]) < 3: esempi[s].append(t[:110])
print("articoli di novembre:", len(arts))
for s, n in cnt.most_common(45):
    print(f"{s:14s} {e[s]['sigla']:8s} {e[s]['nome'][:22]:22s} {n:5d} | {esempi[s][0][:100]}")
