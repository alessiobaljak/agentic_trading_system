import sys, json, re
sys.path.insert(0, "/home/user/agentic_trading_system")
from datetime import datetime, timedelta, timezone
from research.notizie import raccolta
from research.programma7.misure_g1 import voce14_lettura as v14
from pathlib import Path
ora = datetime(2026, 11, 26, 4, 18, tzinfo=timezone.utc)
elenco = json.loads(raccolta.nomi(ora).read_text())["elenco"]
arts = v14.articoli(ora)
per = {}
for q, a in arts:
    for s in raccolta.citate(f"{a.get('titolo', '')} {a.get('sommario', '')}", elenco):
        per.setdefault(s, []).append((q, a))
foglio = Path("/home/user/agentic_trading_system/research/notizie/fatti_gravi/2026-11-26.md").read_text()
# conta nel foglio del commit originale (1c23344) - lo leggo dal git
import subprocess
orig = subprocess.run(["git", "-C", "/home/user/agentic_trading_system", "show", "1c23344:research/notizie/fatti_gravi/2026-11-26.md"], capture_output=True, text=True).stdout
nel = dict((m.group(1), int(m.group(2))) for m in re.finditer(r"### (\S+) — (\d+) articoli", orig))
print("articoli oggi", len(arts), "monete oggi", len(per), "monete nel foglio", len(nel))
diff = []
for s in sorted(set(per) | set(nel)):
    a, b = len(per.get(s, [])), nel.get(s, 0)
    if a != b:
        diff.append((s, b, a))
print("differenze (moneta, nel foglio, oggi):", diff)
