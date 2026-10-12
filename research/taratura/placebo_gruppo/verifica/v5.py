import json
import numpy as np
from collections import Counter
D = "/home/user/coordinamento/research/taratura/placebo_gruppo"
righe = [json.loads(l) for k in range(4) for l in open(f"{D}/esiti_k{k}.jsonl") if l.strip()]
xs = []
for r in righe:
    v = (r.get("esame") or {}).get("sfasate", {}).get("senza_la_piu_vicina")
    if v and v.get("scarto_in_sd") is not None:
        # posizione degli ingressi della sfasata rispetto a quelli veri: (d + d_s) mod L, in (-L/2, L/2]
        L = r["L"]; s = (r["d"] + v["d_s"]) % L
        if s > L // 2: s -= L
        xs.append((r["regola"], r["timeframe"], v["distanza_barre"], s, v["scarto_in_sd"]))
big = [x for x in xs if x[4] > 2]
print("scarto > 2 sd:", len(big), "su", len(xs))
print("  per regola", Counter(x[0] for x in big))
print("  segno della posizione (negativo = ingressi prima del segnale vero)", Counter(np.sign(x[3]) for x in big))
print("  distanza mediana", np.median([x[2] for x in big]), "max", max(x[2] for x in big))
print("  esempi", sorted(big, key=lambda x: -x[4])[:5])
neg = [x for x in xs if x[4] < -2]
print("scarto < -2 sd:", len(neg), Counter(np.sign(x[3]) for x in neg), Counter(x[0] for x in neg))
# effetto grappolo per timeframe
def valutabile(r):
    e = r.get("esame")
    if not e or not e.get("contro_b") or not e["contro_b"].get("valutabile"): return False
    if r["periodo"] == "costruzione": return r["conta"]["esito"] == "registrabile" and e["trade"] >= 700
    return e["trade"] >= 300
for tf in ("1h", "4h"):
    for p in ("costruzione", "validazione"):
        eg = [r["esame"]["effetto_grappolo"] for r in righe if valutabile(r) and r["timeframe"] == tf and r["periodo"] == p]
        print("effetto grappolo", tf, p, "mediana %.1f" % np.median(eg))
