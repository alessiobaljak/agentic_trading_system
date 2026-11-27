# sola lettura: G1 della ricerca (prima.py, come la prova 57) sui simboli rilanciati, nei 200 giorni dopo l'onboardDate
import json, sys
import numpy as np
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc, terza as te, sesta as se, ottava as ot, ventiquattresima as vq
from research.programma7 import prima as pr
info = {x["symbol"]: x for x in json.load(open("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore/verifica/api/exchangeInfo.json"))["symbols"]}
pan = sc.pannello(); t0 = pan["t0"]
ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64); idx = giorni - t0
Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
sig = ot.sigma_30(pan, idx)
W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
R = sc.rendimenti(pan)[idx]; F = np.nan_to_num(pan["funding"][idx])
tot = 0.0
for s in ("LITUSDT", "PUMPUSDT", "CTKUSDT", "SLPUSDT", "CVXUSDT", "CVCUSDT", "MAVIAUSDT", "AIAUSDT", "TLMUSDT", "BNXUSDT"):
    if s not in info: print(s, "non in exchangeInfo"); continue
    j = pan["simboli"].index(s); ob = int(info[s]["onboardDate"]) // 86400000
    sel = (giorni >= ob) & (giorni < ob + 200)
    x = float((W[sel, j] * (R[sel, j] - F[sel, j])).sum()); tot += x
    print(f"{s:10s} onboard {sc.data(ob)} prima candela {sc.data(int(np.flatnonzero(np.isfinite(pan['close'][:, j]))[0]) + t0)}: giorni con peso {int((W[sel, j] != 0).sum())}, contributo {100*x:+.2f} punti")
print("totale %+.2f punti" % (100 * tot))
# il salto del rilancio entra in G1? peso il giorno prima dell'onboard
for s in ("LITUSDT", "PUMPUSDT", "CTKUSDT", "SLPUSDT", "CVXUSDT", "CVCUSDT", "MAVIAUSDT"):
    j = pan["simboli"].index(s); ob = int(info[s]["onboardDate"]) // 86400000
    k = np.flatnonzero(giorni == ob - 1)
    if len(k): print(s, "peso di G1 il giorno prima del rilancio:", float(W[k[0], j]), "rendimento quel giorno %.3f" % R[k[0], j])
