import re, sys, collections
f = sys.argv[1]
t = open(f, encoding="utf-8").read()
body = t.split("```",2)[1] if "```" in t else t
c = collections.Counter()
for line in body.splitlines():
    n = len(line)
    m = re.search(r"python\[\d+\]: (.*)$", line)
    msg = m.group(1) if m else line
    if "UserWarning" in msg or "query.where" in msg: k="firestore_warn"
    elif msg.startswith("[demo_binance]") or "demo" in msg[:20]: k="demo"
    elif msg.startswith("[paper") or msg.startswith("[portafoglio") or msg.startswith("[f5") or msg.startswith("[g1"): k="paper"
    elif msg.startswith("[controllo]") or msg.startswith("[firebase] letture"): k="controllo_letture"
    elif msg.startswith("[main]") or msg.startswith("[price_agent]") or msg.startswith("[scanner]") or msg.startswith("[regime") or msg.startswith("[supervisor") or msg.startswith("[telegram") or msg.startswith("[notifier"): k="vecchio"
    elif "caratteri omessi" in msg: k="cut"
    else: k="altro:"+msg[:30]
    c[k]+=n
tot=sum(v for k,v in c.items() if k!="cut")
for k,v in c.most_common(): print(f"{k:40s} {v:6d} {100*v/tot:5.1f}%")
print("tot",tot)
