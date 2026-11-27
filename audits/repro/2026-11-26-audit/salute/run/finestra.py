import json, os, sys, glob, calendar, time, statistics
d = sys.argv[1]
T = {"2026-11-20": 9*60+41, "2026-11-21": 9*60+24, "2026-11-22": 9*60+16, "2026-11-24": 9*60+30, "2026-11-25": 9*60+27, "2026-11-26": 9*60+38}
DA = 5*60 + 15   # ora del giro del paper (secondi dopo mezzanotte), stima
res = {"pap": [], "ver": []}
costi = {"pap": [], "ver": []}
n_ok = 0
for f in sorted(glob.glob(os.path.join(d, "*.json"))):
    s, g = os.path.basename(f)[:-5].rsplit("_", 1)
    try:
        k = json.load(open(f))
    except Exception:
        continue
    if not isinstance(k, list) or len(k) < 75: continue
    t0 = calendar.timegm(time.strptime(g, "%Y-%m-%d")) * 1000
    c = {(int(r[0]) - t0) // 60000: (float(r[1]), float(r[2]), float(r[3]), float(r[4])) for r in k}
    tt = T[g]; mT = tt // 60
    if mT not in c: continue
    o, h, l, cl = c[mT]; frac = (tt % 60) / 60
    p0 = o + (cl - o) * frac
    da_ms = DA * 1000; fino = da_ms + 3600_000
    pap = [c[m] for m in sorted(c) if da_ms <= m * 60000 < fino]
    ver = [c[m] for m in sorted(c) if (tt * 1000) <= m * 60000 < tt * 1000 + 3600_000]
    if len(pap) < 55 or len(ver) < 55: continue
    n_ok += 1
    for nome, w in (("pap", pap), ("ver", ver)):
        for segno in (1, -1):
            preso = (min(x[2] for x in w) < p0) if segno > 0 else (max(x[1] for x in w) > p0)
            res[nome].append(preso)
            costo = 0.0002 if preso else 0.0005 + 0.0002 + segno * (w[-1][3] - p0) / p0
            costi[nome].append(costo)
print("monete-giorno usate:", n_ok)
for nome in ("pap", "ver"):
    print(nome, "eseguiti a limite %.1f%%" % (100 * sum(res[nome]) / len(res[nome])), "costo medio per valore %.4f%%" % (100 * statistics.mean(costi[nome])))
# solo i casi in cui la finestra del paper esegue e quella vera no
diff = sum(1 for a, b in zip(res["pap"], res["ver"]) if a and not b); inv = sum(1 for a, b in zip(res["pap"], res["ver"]) if b and not a)
print("eseguiti solo nella finestra del paper:", diff, "solo in quella vera:", inv, "su", len(res["pap"]))
