import csv, collections
rows = list(csv.DictReader(open("/home/user/agentic_trading_system/research/notizie/archivio/giri.csv")))
per = collections.defaultdict(list)
for r in rows: per[r["fonte"]].append(r)
for fo in ("coinjournal", "zycrypto", "bitcoinist", "cryptopotato", "cryptobriefing", "cryptonewsdotnet", "cryptobriefing2", "cryptobriefing3"):
    seq = per[fo]
    s = "".join("0" if r["articoli"] == "0" else ("P" if r["nota"] == "piena" else ".") for r in seq)
    print(f"{fo:16s} {s}")
# empty followed by piena (single-page sources)
print()
for fo, seq in per.items():
    for a, b in zip(seq, seq[1:]):
        if a["articoli"] == "0" and b["nota"] == "piena":
            print("vuota poi piena:", fo, a["ora"], "->", b["ora"], b["articoli"], b["nuovi"])
# check cryptobriefing: last page piena by round
ore = sorted(set(r["ora"] for r in rows))
byora = collections.defaultdict(dict)
for r in rows: byora[r["ora"]][r["fonte"]] = r
print()
for o in ore:
    d = byora[o]
    pages = [k for k in ("cryptobriefing", "cryptobriefing2", "cryptobriefing3", "cryptobriefing4") if k in d]
    last = pages[-1]
    if d[last]["nota"] == "piena":
        print("ultima pagina di CryptoBriefing piena:", o, last, [ (k, d[k]["articoli"], d[k]["nuovi"]) for k in pages])
    if d.get("beincrypto", {}).get("nota") == "piena" and ("beincrypto2" not in d or d["beincrypto2"]["nota"] == "piena"):
        print("BeInCrypto ultima pagina piena:", o, d.get("beincrypto2"))
