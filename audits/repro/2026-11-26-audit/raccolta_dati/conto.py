import gzip, json, sys
pref = sys.argv[1]
f = "/home/user/agentic_trading_system/research/trader_copiati/hyperliquid/posizioni_2026-11.jsonl.gz"
n = 0
for r in gzip.open(f, "rt"):
    x = json.loads(r)
    if x["indirizzo"].startswith(pref):
        n += 1
        if n % 12 == 1:
            net = sum(p["quantita"] * abs(p["valore"]/p["quantita"]) for p in x["posizioni"] if p["quantita"])
            gross = sum(abs(p["valore"]) for p in x["posizioni"])
            lev = sorted(set(str(p.get("leva")) for p in x["posizioni"]))
            print(x["ora"], "conto", round(x["conto"]), "pos", len(x["posizioni"]), "netta", round(net), "lorda", round(gross), "netta/conto", round(net/x["conto"],2) if x["conto"] else None, "leve", lev[:6])
print("righe", n)
