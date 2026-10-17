import json, sys
import numpy as np
sys.path.insert(0, ".")
from research.src import catalogo3 as cat
import research.collaudo_3.collaudo as co
co.GIRO = 1  # diagnosi del primo giro: candele rimescolate
righe = {json.loads(x)["numero"]: json.loads(x) for x in open("research/collaudo_3/esiti/giro1/prova_a.jsonl")}
d = json.load(open("research/collaudo_3/diagnosi/diagnosi_a.json"))
for o in sorted(d, key=lambda o: o["p"])[:6]:
    r = righe[o["numero"]]; v = r["variante"]; s = co.serie_rimescolata(v["timeframe"], r["serie"])
    c = cat.compila(v, s)
    sig = np.flatnonzero(c.segnale); amm = np.flatnonzero(c.ammessa)
    lr = np.log(s.close)
    for h in (1, 5, 20):
        def fwd(idx):
            idx = idx[idx + h < len(s)]
            return (np.log(s.close[idx + h]) - np.log(s.open[idx + 1])).mean() * 1e4
        print(o["numero"], v["timeframe"], v["direzione"], v["ingresso"]["codice"], "h", h, "segnali bp %.2f" % fwd(sig), "tutte bp %.2f" % fwd(amm), "n", len(sig))
    # rendimento del salto alla candela dopo
    print("   salto dopo segnale bp %.2f, tutte %.2f" % (((s.open[sig+1]/s.close[sig])-1).mean()*1e4 if sig[-1]+1<len(s) else 0, ((s.open[amm[:-1]+1]/s.close[amm[:-1]])-1).mean()*1e4))
