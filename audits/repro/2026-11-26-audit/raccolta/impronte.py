import json, subprocess, collections, sys
R = "/home/user/agentic_trading_system"
for c in sys.argv[1:]:
    d = json.loads(subprocess.run(["git", "-C", R, "show", f"{c}:research/programma6/scarico_giorni.json"], capture_output=True, text=True).stdout)
    cnt = collections.Counter()
    for s, v in d.items():
        u = v.get("giorni", {}).get("ultimo", "")
        cnt[u[len(s)+4:].replace(".zip", "")] += 1
    top = sorted(cnt.items(), key=lambda x: x[0], reverse=True)[:5]
    print(c, len(d), top)
