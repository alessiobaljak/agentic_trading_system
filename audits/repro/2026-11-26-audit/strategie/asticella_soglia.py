import sys, math, json, time
sys.path.insert(0, '/home/user/agentic_trading_system')
t0 = time.time()
import numpy as np
from research.programma6 import asticella as a
from research.programma6 import terza as te
serie, soli = a.mazzo()
gr = a.gruppi(serie, a.TAGLIO)
sr_g, sr_v = a.per_v(gr, soli, False), a.per_v(gr, soli, True)
print("serie", len(serie), "senza serie", len(soli), "famiglie", len(sr_g), "in V", len(sr_v), "dev V", round(float(np.std(sr_v, ddof=1)),3), f"{time.time()-t0:.0f}s")
alti = sorted([(g['sharpe'], g['membri'][:4], g['settimane']) for g in gr if g['sharpe'] > 2.0], reverse=True)
print("famiglie con Sharpe > 2:", [(round(s,2), m, n) for s, m, n in alti])
def soglia(n_sett, srv, N):
    lo, hi = 0.0, 6.0
    for _ in range(60):
        mid = (lo+hi)/2
        p = te.sharpe_corretto(mid, n_sett, 0.0, 3.0, srv, 52, n_prove=N)
        if p < 0.80: lo = mid
        else: hi = mid
    return hi
N = len(sr_g)
for n_sett in (300, 200, 150, 100, 52):
    print(f"settimane {n_sett}: Sharpe annuo minimo per 0,80 = {soglia(n_sett, sr_v, N):.2f}")
# senza le serie a incasso quasi fisso (Sharpe > 3)
sr_v2 = [x for x in sr_v if x <= 3.0]
print("V senza Sharpe>3:", len(sr_v2), "dev", round(float(np.std(sr_v2, ddof=1)),3))
for n_sett in (300, 150, 100):
    print(f"  senza: settimane {n_sett}: minimo {soglia(n_sett, sr_v2, N):.2f}")
# sr0 annuo
var = float(np.var([x/math.sqrt(52) for x in sr_v], ddof=1)); g=0.5772156649
from scipy import stats
sr0 = math.sqrt(var)*((1-g)*stats.norm.ppf(1-1/N)+g*stats.norm.ppf(1-1/(N*math.e)))*math.sqrt(52)
print("sr0 annuo (fortuna da battere) =", round(sr0,2))
# G1 a N=57
print("tempo", f"{time.time()-t0:.0f}s")
