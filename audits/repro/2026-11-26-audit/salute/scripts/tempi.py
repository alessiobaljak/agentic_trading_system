import re, glob, sys, collections
pat = re.compile(r"^(\w{3} \d{2} \d{2}:\d{2}:\d{2}) \S+ python\[\d+\]: \[(paper_g1|paper_g11|paper_g1n|paper_f5|demo_binance)\] (ribilancio del (\S+?):|decisione G1 del (\S+?):|ordini limite del (\S+?):)")
righe = {}
for f in sorted(glob.glob(sys.argv[1] + "/0[67]*log*.md")):
    for l in open(f, encoding="utf-8", errors="replace"):
        m = pat.match(l)
        if m:
            ts, who, _, d1, d2, d3 = m.groups()
            kind = "rib" if d1 else ("dec" if d2 else "lim")
            day = d1 or d2 or d3
            righe[(day, who, kind)] = ts
days = sorted({k[0] for k in righe})
print("giorno      f5rib  g1rib  g11rib g1nrib demo   g1lim  g11lim g1nlim")
for d in days:
    def g(w, k):
        t = righe.get((d, w, k)); return t[7:12] if t else "  -  "
    print(d, g("paper_f5","rib"), g("paper_g1","rib"), g("paper_g11","rib"), g("paper_g1n","rib"), g("demo_binance","dec"), g("paper_g1","lim"), g("paper_g11","lim"), g("paper_g1n","lim"))
