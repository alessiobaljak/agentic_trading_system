import sys; sys.path.insert(0,'/tmp/revisore107')
from rifai import *
import json
from research.programma7 import quarantunesima as lv
el = {a['id']: a for a in json.load(open('/home/user/agentic_trading_system/research/data/annunci/chiusure/elenco.json'))}
mancati = [(87665, '1000BTTCUSDT', '2022-04-11', '09', '00'), (87665, 'YFIIUSDT', '2022-04-12', '09', '00'), (92501, 'AKROUSDT', '2022-05-26', '09', '00'),
           (92501, 'DODOUSDT', '2022-05-27', '09', '00'), (94026, 'TLMUSDT', '2022-06-09', '09', '00'), (94026, 'ICPUSDT', '2022-06-10', '09', '00'),
           (94643, 'SCUSDT', '2022-06-17', '09', '00'), (99511, 'BTSUSDT', '2022-08-18', '09', '00'), (100176, 'BLZUSDT', '2022-08-25', '09', '00'),
           (244031, 'MEMEFIUSDT', '2025-08-11', '09', '00')]
ev_m = [(s, int(el[i]['ms']), lv._ms(d, h, m), i) for i, s, d, h, m in mancati]
for s, a, c, i in ev_m:
    v = orev(s); hc = c // 3_600_000
    dopo = v[v.index >= a//3_600_000 + 1]; z = dopo[dopo.volume == 0]
    print(s, 'chiusura testo', f(hc), 'prima ora morta', f(int(z.index.min())) if len(z) else None)
om = corri(ev_m, 'solo i mancati', controllo=False)
print(om['df'][['data','simbolo','ore','r','fermata','r_senza']].round(3).to_string())
evc = [(s, a, cc, i) for s, a, c, i, cc, nota in eventi_corretti(pan) if cc is not None]
tutti = evc + ev_m
ot = corri(tutti, 'corrette + mancati 2022/2025')
ot['df'].to_csv('/tmp/revisore107/eventi_corretti_piu.csv', index=False)
# also keep OMG with announced date (live trader would exit at announced time)
evo = [(s, a, (cc if cc is not None else c), i) for s, a, c, i, cc, nota in eventi_corretti(pan) if (cc is not None or s == 'OMGUSDT')]
oo = corri(evo, 'corrette + OMG')
oo2 = corri(evo + ev_m, 'corrette + OMG + mancati')
oo2['df'].to_csv('/tmp/revisore107/eventi_finale.csv', index=False)
