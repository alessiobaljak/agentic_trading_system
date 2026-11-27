import sys
sys.path.insert(0, '/home/user/agentic_trading_system')
from research.programma6 import asticella as a, terza as te
serie, soli = a.mazzo()
s2 = {k: v for k, v in serie.items() if k.split()[0] not in ('157', '159', '161')}
gr = a.gruppi(s2, a.TAGLIO)
sr_g, sr_v = a.per_v(gr, soli, False), a.per_v(gr, soli, True)
N = len(sr_g)
def soglia(n):
    lo, hi = 0.0, 12.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if te.sharpe_corretto(mid, n, 0.0, 3.0, sr_v, 52, n_prove=N) < 0.80: lo = mid
        else: hi = mid
    return hi
print('N', N, ' '.join(f"{n} sett: {soglia(n):.2f}" for n in (300, 150, 100, 52, 22)))
