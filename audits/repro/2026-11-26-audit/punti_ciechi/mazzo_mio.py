import sys, time, pickle
sys.path.insert(0, '/home/user/agentic_trading_system')
t0 = time.time()
import numpy as np
from research.programma6 import asticella as a
serie, soli = a.mazzo()
gr = a.gruppi(serie, a.TAGLIO)
sr_g, sr_v = a.per_v(gr, soli, False), a.per_v(gr, soli, True)
print("serie", len(serie), "soli", len(soli), "famiglie N", len(sr_g), "in V", len(sr_v), "dev V", round(float(np.std(sr_v, ddof=1)), 4), f"{time.time()-t0:.0f}s")
pickle.dump({"serie": serie, "soli": soli, "gr": gr, "sr_g": sr_g, "sr_v": sr_v}, open("mazzo_mio.pkl", "wb"))
