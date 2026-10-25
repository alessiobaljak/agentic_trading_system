import json, re, sys, datetime as dt
sys.path.insert(0, '/home/user/agentic_trading_system')
from research.programma7 import quarantacinquesima as q
from research.programma7 import quarantunesima as lv
from research.programma6 import seconda as sc
pan = sc.pannello()
sim = set(pan['simboli'])
ev = q.eventi(sim)
print(len(ev))
f = lambda ms: dt.datetime.utcfromtimestamp(ms/1000).strftime('%Y-%m-%d %H:%M')
for s, a, c, i in ev:
    print(i, s, f(a), f(c), round((c-a)/3.6e6,1))
# also all USDT symbols in text not in panel
elenco = json.loads((q.DATI / "elenco.json").read_text())
print('---- per annuncio')
for a in sorted(elenco, key=lambda x: x['ms']):
    fp = q.DATI / f"{a['id']}.json"
    testo = " ".join(lv.frammenti(json.loads(fp.read_text())["body"]))
    ore = [lv._ms(*m.groups()) for m in q.DATA.finditer(testo)]
    dopo = sorted(set(h for h in ore if h > int(a['ms'])))
    sy = sorted(set(re.findall(r"\b[0-9A-Z]{2,20}USDT\b", testo + " " + a["titolo"])))
    print(a['id'], f(a['ms']), 'date:', [f(h) for h in dopo], 'sym:', [(s, s in sim) for s in sy])
