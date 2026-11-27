import sys, re, glob
from datetime import datetime, timezone, timedelta
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma7.misure_g1 import voce14_lettura as v14
R = "/home/user/agentic_trading_system/"
for f in sorted(glob.glob(R + "research/notizie/fatti_gravi/*.md")) + sorted(glob.glob(R + "research/programma7/misure_g1/voce14_letture/*.md")):
    t = open(f).read()
    m = re.search(r"dalle (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) alle (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) UTC: (\d+)", t)
    fine = datetime.strptime(m.group(2), "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    arts = v14.articoli(fine)
    visti_dopo = [a for q, a in arts if datetime.strptime(a["visto"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc) > fine]
    ultime4 = [a for q, a in arts if q >= fine - timedelta(hours=4)]
    print(f.split("/")[-2][:12], f.split("/")[-1], "fine", m.group(2), "nel foglio", m.group(3), "oggi", len(arts), "visti dopo la fine", len(visti_dopo), "pubblicati nelle ultime 4 ore", len(ultime4))
