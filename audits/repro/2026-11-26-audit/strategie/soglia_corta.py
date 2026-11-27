import sys
sys.path.insert(0, '/home/user/agentic_trading_system')
from research.programma6 import asticella as a, terza as te
serie, soli = a.mazzo()
gr = a.gruppi(serie, a.TAGLIO)
sr_g, sr_v = a.per_v(gr, soli, False), a.per_v(gr, soli, True)
N = len(sr_g)
def soglia(n_sett, N):
    lo, hi = 0.0, 12.0
    for _ in range(60):
        mid = (lo+hi)/2
        if te.sharpe_corretto(mid, n_sett, 0.0, 3.0, sr_v, 52, n_prove=N) < 0.80: lo = mid
        else: hi = mid
    return hi
for n in (22, 26, 300):
    print(f"settimane {n}: N={N} -> {soglia(n, N):.2f}; N=57 -> {soglia(n, 57):.2f}; N=10 -> {soglia(n, 10):.2f}")
