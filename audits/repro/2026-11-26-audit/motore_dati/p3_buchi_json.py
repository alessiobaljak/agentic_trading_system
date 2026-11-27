import json
d = json.load(open('/home/user/agentic_trading_system/research/programma6/buchi_archivio.json'))
print({k: v for k, v in d.items() if k != 'non_riempiti'})
nr = d.get('non_riempiti', {})
print('non_riempiti', len(nr), list(nr.items())[:10])
