from pathlib import Path
import collections
D = Path('/home/user/agentic_trading_system/research/data/p6g')
mesi = collections.Counter(); n_sim = 0; ultimo_f = collections.Counter()
for s in sorted(p.name for p in D.iterdir() if p.is_dir()):
    pr = sorted((D / s / 'premio').glob('*.zip'))
    if pr:
        n_sim += 1
        for p in pr: mesi[p.name.split('-1h-')[1][:7]] += 1
    fu = sorted((D / s / 'funding').glob('*.zip'))
    if fu: ultimo_f[fu[-1].name[-11:-4]] += 1
print('simboli con premio', n_sim); print('file premio per mese', dict(sorted(mesi.items())))
print('ultimo file mensile funding per simbolo (conteggio)', dict(sorted(ultimo_f.items())[-6:]))
