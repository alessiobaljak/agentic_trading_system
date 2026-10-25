import sys; sys.path.insert(0,'/tmp/revisore107')
from candele import *
import json, re
from research.programma7 import quarantacinquesima as q
from research.programma7 import quarantunesima as lv
from research.programma6 import seconda as sc

def eventi_corretti(pan):
    ev = q.eventi(set(pan['simboli']))
    elenco = {a['id']: a for a in json.loads((q.DATI / "elenco.json").read_text())}
    out = []
    for s, a, c, i in ev:
        testo = " ".join(lv.frammenti(json.loads((q.DATI / f"{i}.json").read_text())["body"]))
        date = sorted(set(lv._ms(*m.groups()) for m in q.DATA.finditer(testo)))
        date = [d for d in date if d > a]
        v = orev(s)
        if v.empty:
            out.append((s, a, c, i, None, 'nessuna candela')); continue
        dopo = v[v.index >= a//3_600_000 + 1]
        z = dopo[dopo['volume'] == 0]
        pz = int(z.index.min()) if len(z) else None
        if pz is None:
            out.append((s, a, c, i, None, 'nessuna ora morta')); continue
        cand = [d for d in date if pz - 1 <= d // 3_600_000 <= pz]
        # prefer the full hour of settlement (minute 00) among candidates; take the max (settlement, not reduce-only at :30)
        cc = max(cand) if cand else None
        out.append((s, a, c, i, cc, '' if cc else f'nessuna data vicina alla prima ora morta {f(pz)}'))
    return out

if __name__ == '__main__':
    pan = sc.pannello()
    for s, a, c, i, cc, nota in eventi_corretti(pan):
        flag = '' if cc == c else '  <== DIVERSA'
        print(i, s, 'testo', f(c//3600000) + f":{(c//60000)%60:02d}", 'corretta', (f(cc//3600000)+f":{(cc//60000)%60:02d}") if cc else None, nota, flag)
