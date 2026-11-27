"""Problema 2: minimi di Binance del mercato vero e quante monete di G1 di oggi non si aprono da zero a 280/300/1000 USDT."""
import json, sys, math, collections
ei = json.load(open(sys.argv[1])); prem = json.load(open(sys.argv[2])); fissi = json.load(open(sys.argv[3]))["filtri"]
f = {}
stati = {}
for x in ei["symbols"]:
    g = {h["filterType"]: h for h in x["filters"]}
    stati[x["symbol"]] = (x.get("status"), x.get("contractType"), x.get("quoteAsset"))
    try:
        f[x["symbol"]] = (float(g["LOT_SIZE"]["stepSize"]), float(g["LOT_SIZE"]["minQty"]), float(g["MIN_NOTIONAL"]["notional"]))
    except KeyError:
        pass
# minimi fra i perpetui USDT in TRADING
cnt = collections.Counter(); grandi = {}
for s, (st, ct, q) in stati.items():
    if st == "TRADING" and ct == "PERPETUAL" and q == "USDT" and s in f:
        cnt[f[s][2]] += 1
        if f[s][2] > 5: grandi[s] = f[s][2]
print("minimi (perpetui USDT in TRADING):", dict(cnt), "sopra 5:", grandi)
# confronto con la copia fissa del 6 novembre
diversi = [(s, fissi[s]["valore_minimo"], f[s][2]) for s in fissi if s in f and abs(fissi[s]["valore_minimo"] - f[s][2]) > 1e-9]
print("monete della copia del 6 nov con minimo diverso oggi:", len(diversi), diversi[:10])
mark = {x["symbol"]: float(x["markPrice"]) for x in prem if float(x.get("markPrice") or 0) > 0}
# i 58 pesi del paper G1 (0776, sezione «G1 oggi, moneta per moneta»), in % del conto
testo = open(sys.argv[4], encoding="utf-8").read()
import re
sez = testo.split("## G1 oggi, moneta per moneta")[1].split("- monete:")[0]
pesi = {m.group(1): float(m.group(2)) / 100 for m in re.finditer(r"([0-9A-Z一-鿿]+USDT) ([+-][0-9.]+)/", sez)}
print("pesi letti:", len(pesi), "somma lorda", round(sum(abs(w) for w in pesi.values()), 4))
for cap in (280, 300, 1000):
    fuori = []
    for s, w in pesi.items():
        if s not in f or s not in mark:
            fuori.append((s, w, "senza filtri o prezzo")); continue
        passo, qmin, vmin = f[s]
        p = mark[s]
        q = math.floor(abs(w) * cap / p / passo + 1e-9) * passo
        if q < qmin or q * p < vmin:
            fuori.append((s, w, round(abs(w) * cap, 2)))
    lorda = sum(abs(w) for w in pesi.values())
    peso_fuori = sum(abs(w) for s, w, _ in fuori)
    print(f"capitale {cap}: fuori {len(fuori)} su {len(pesi)}, {100*peso_fuori/lorda:.1f}% dell'esposizione lorda;",
          " ".join(f"{s[:-4]}({x})" for s, w, x in sorted(fuori)))
# stato delle monete che il demo non ha
for s in ["LITUSDT", "EVAAUSDT", "UAIUSDT", "PIEVERSEUSDT", "IRYSUSDT", "龙虾USDT", "ICPUSDT"]:
    x = next((y for y in ei["symbols"] if y["symbol"] == s), None)
    print(s, None if x is None else (x["status"], x["contractType"], x.get("deliveryDate"), f.get(s)))
