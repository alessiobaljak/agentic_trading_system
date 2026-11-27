import json, os, sys, glob, calendar, time, statistics, random
d = sys.argv[1]
T = {"2026-11-20": 9*60+41, "2026-11-21": 9*60+24, "2026-11-22": 9*60+16, "2026-11-24": 9*60+30, "2026-11-25": 9*60+27, "2026-11-26": 9*60+38}
DA = 5*60 + 15
casi = []
for f in sorted(glob.glob(os.path.join(d, "*.json"))):
    s, g = os.path.basename(f)[:-5].rsplit("_", 1)
    k = json.load(open(f))
    if not isinstance(k, list) or len(k) < 75: continue
    t0 = calendar.timegm(time.strptime(g, "%Y-%m-%d")) * 1000
    c = {(int(r[0]) - t0) // 60000: (float(r[1]), float(r[2]), float(r[3]), float(r[4])) for r in k}
    mT = T[g] // 60
    if any(m not in c for m in range(5, mT + 61)): continue
    p0 = c[mT][0]                                   # prezzo all'inizio del minuto della lettura
    pap = [c[m] for m in range(DA // 60 + 1, DA // 60 + 61)]       # come il paper: dal giro (00:06) per 60 minuti
    ric = [c[m] for m in range(mT, mT + 60)]                       # come la ricerca: dal minuto della lettura per 60 minuti
    for segno in (1, -1):
        r = {}
        for nome, w in (("pap", pap), ("ric", ric)):
            preso = (min(x[2] for x in w) < p0) if segno > 0 else (max(x[1] for x in w) > p0)
            r[nome] = (preso, 0.0002 if preso else 0.0007 + segno * (w[-1][3] - p0) / p0)
        casi.append((g, s, segno, r))
print("casi (moneta, giorno, lato):", len(casi))
for nome in ("pap", "ric"):
    print(nome, "eseguiti %.1f%%" % (100 * statistics.mean(r[nome][0] for *_, r in casi)),
          "costo medio %.4f%% del valore" % (100 * statistics.mean(r[nome][1] for *_, r in casi)))
# per giorno
for g in sorted(T):
    cc = [r for gg, s, sg, r in casi if gg == g]
    print(g, "ric eseguiti %.1f%%, costo %.4f%%" % (100 * statistics.mean(r["ric"][0] for r in cc), 100 * statistics.mean(r["ric"][1] for r in cc)))
# intervallo con ricampionamento per moneta-giorno
random.seed(1); diffs = []
idx = list(range(len(casi)))
for _ in range(2000):
    b = [casi[random.choice(idx)] for _ in idx]
    diffs.append(statistics.mean(r["ric"][1] - r["pap"][1] for *_, r in b))
diffs.sort(); print("differenza di costo ric-pap: %.4f%% (90%%: %.4f%% - %.4f%%)" % (100*statistics.mean(r["ric"][1]-r["pap"][1] for *_, r in casi), 100*diffs[100], 100*diffs[1900]))
