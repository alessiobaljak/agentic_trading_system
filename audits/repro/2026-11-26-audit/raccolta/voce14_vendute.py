import sys, json, re, subprocess
sys.path.insert(0, "/home/user/agentic_trading_system")
from datetime import datetime, timedelta, timezone
from research.notizie import raccolta
from research.programma7.misure_g1 import voce14_lettura as v14
R = "/home/user/agentic_trading_system"
for d in ["2026-11-22", "2026-11-23", "2026-11-24", "2026-11-25", "2026-11-26"]:
    t = open(f"{R}/research/programma7/misure_g1/voce14_letture/{d}.md").read()
    m = re.search(r"alle (\d\d:\d\d) UTC\): ", t) or re.search(r"letti alle (\d\d:\d\d) UTC", t)
    hh = re.search(r"letti alle (\d\d:\d\d) UTC", t).group(1)
    ora = datetime.strptime(f"{d} {hh}", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    elenco = json.loads(raccolta.nomi(ora).read_text())["elenco"]
    arts = v14.articoli(ora)
    righe = re.findall(r"^\| (\S+USDT) \| ([+-]\d+\.\d+)% \| (\d+) \|", t, re.M)
    diffs = []
    for s, p, n in righe:
        trovati = [(q, a) for q, a in arts if v14.cita(f"{a.get('titolo', '')} {a.get('sommario', '')}", s, elenco)]
        if len(trovati) != int(n):
            nuovi = [(q.strftime('%m-%d %H:%M'), a['titolo'][:90]) for q, a in trovati if datetime.strptime(a['visto'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc) >= ora]
            diffs.append((s, p, int(n), len(trovati), nuovi))
    print(d, hh, "vendute", len(righe), "con differenze:", [(x[0], x[2], x[3]) for x in diffs])
    for x in diffs:
        for y in x[4]:
            print("    ", x[0], y)
