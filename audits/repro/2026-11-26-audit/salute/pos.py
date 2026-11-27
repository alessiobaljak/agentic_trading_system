import glob, re, sys
keys = ["## G1 sul demo: esecuzioni", "monete del paper G1 che il demo non ha avuto", "Le 10 monete con il funding più grande", "nel paper G1 di oggi ma senza funding", "il paper G1 di oggi contro il funding", "caratteri omessi", "## GATE 1", "| giorno | totale | 00 | 08 | 16"]
for f in sorted(glob.glob("ops/results/07[3-7]*stato*.md")):
    t = open(f, encoding="utf-8").read()
    out = [f.split("/")[-1][:30]]
    for k in keys:
        i = t.find(k)
        out.append(f"{k[:18]}={i}")
    print(" | ".join(out))
