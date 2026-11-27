import sys, json, gzip, glob, re, collections
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.notizie import raccolta
e = json.load(open("/home/user/agentic_trading_system/research/notizie/nomi_2026-11.json"))["elenco"]
arts = []
for f in sorted(glob.glob("/home/user/agentic_trading_system/research/notizie/archivio/2026-11-*.jsonl.gz")):
    for r in gzip.open(f, "rt"):
        a = json.loads(r); arts.append(a["titolo"] + " " + a["sommario"])
cnt = collections.Counter(); via = collections.defaultdict(collections.Counter)
for t in arts:
    for s, x in e.items():
        sig, nome = x["sigla"], x["nome"]
        how = None
        if re.search(r"\$" + re.escape(sig) + r"\b", t, re.I): how = "$"
        elif len(sig) >= 3 and sig not in raccolta.PAROLE and re.search(r"(?<![A-Za-z0-9])" + re.escape(sig) + r"(?![A-Za-z0-9])", t): how = "sigla"
        elif len(nome) >= 5 and nome not in raccolta.PAROLE and nome.upper() not in raccolta.PAROLE and re.search(r"\b" + re.escape(nome) + r"\b", t): how = "nome"
        if how:
            cnt[s] += 1; via[s][how] += 1
print("articoli di novembre:", len(arts))
for s, n in cnt.most_common(60):
    print(s, e[s]["sigla"], "|", e[s]["nome"], "|", n, dict(via[s]))
json.dump({s: n for s, n in cnt.items()}, open(sys.argv[1], "w"))
