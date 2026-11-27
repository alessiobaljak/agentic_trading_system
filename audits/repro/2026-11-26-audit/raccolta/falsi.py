import sys, json, gzip, re
from pathlib import Path
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.notizie import raccolta
R = Path("/home/user/agentic_trading_system/research/notizie")
elenco = json.load(open(R / "nomi_2026-11.json"))["elenco"]
arts = []
for f in sorted((R / "archivio").glob("2026-11-*.jsonl.gz")):
    for r in gzip.open(f, "rt", encoding="utf-8"):
        if r.strip():
            arts.append(json.loads(r))
print("articoli di novembre:", len(arts))
guarda = ["ANTUSDT", "ARKUSDT", "HIVEUSDT", "GENIUSUSDT", "1000SATSUSDT", "APRUSDT"]
for s in guarda:
    print(s, elenco.get(s))
cnt = {s: [] for s in guarda}
for a in arts:
    t = f"{a.get('titolo','')} {a.get('sommario','')}"
    for s in raccolta.citate(t, {k: elenco[k] for k in guarda if k in elenco}):
        cnt[s].append(a["titolo"])
for s in guarda:
    print(f"== {s}: {len(cnt[s])}")
    for t in cnt[s][:5]:
        print("    ", t[:110])
for s in ["RAYSOLUSDT", "BEAMXUSDT", "LUNA2USDT", "DODOXUSDT"]:
    print(s, "in elenco:", s in elenco)
