import numpy as np, pandas as pd
from research.programma6 import seconda as sc, terza as te, sesta as se, ottava as ot, ventiquattresima as vq
from research.programma7 import prima as pr
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]
ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64); idx = giorni - t0
Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
sig = ot.sigma_30(pan, idx)
W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(pan, idx), np.nan), Ud, sig)
R = sc.rendimenti(pan)[idx]; F = np.nan_to_num(pan["funding"][idx])
O, V, C = pan["open"][idx], pan["quote_volume"][idx], pan["close"][idx]
morti = (W != 0) & ~np.isfinite(O)
zero = (W != 0) & np.isfinite(C) & (np.nan_to_num(V) == 0)
print("G1 (prima.py) dal", sc.data(int(giorni[0])), "al", sc.data(int(giorni[-1])))
print("giorni-moneta con peso e senza candela (moneta non quotata quel giorno):", int(morti.sum()), "| peso medio assoluto %.3f" % np.abs(W[morti]).mean() if morti.any() else "")
print("giorni-moneta con peso e volume zero (prezzo fermo):", int(zero.sum()))
lista = {}
for k, j in np.argwhere(morti | zero):
    lista.setdefault(pan["simboli"][j], []).append((sc.data(int(giorni[k])), round(float(W[k, j]) * 100, 1), "senza candela" if morti[k, j] else "volume zero"))
for s, v in lista.items(): print("  ", s, v[:6], "..." if len(v) > 6 else "")
# l'ultimo giorno di vita: rendimento apertura -> chiusura (manca la candela dopo) con peso
ultimo = (W != 0) & np.isfinite(O) & ~np.isfinite(np.vstack([pan["open"][idx[1:]], np.full((1, W.shape[1]), np.nan)]))
print("giorni-moneta con peso nell'ultimo giorno prima di un buco o della fine:", int(ultimo[:-1].sum()))
# ultimo giorno con scambi (volume > 0) di ogni moneta: se e' prima della fine del pannello, la moneta e' stata tolta (o il simbolo riusato)
Vt = pan["quote_volume"]; ok = np.isfinite(pan["close"]) & (np.nan_to_num(Vt) > 0)
ultimo_scambio = np.where(ok.any(0), T - 1 - np.argmax(ok[::-1], axis=0), -1)
tolte = ultimo_scambio < T - 10
contr = np.zeros(len(giorni)); n = 0; per = {}
Rl, Fl = R, F
for k in range(len(giorni)):
    for j in np.flatnonzero(W[k]):
        if not tolte[j]: continue
        mancano = ultimo_scambio[j] - idx[k]
        if 0 <= mancano <= 8 or (mancano < 0 and idx[k] - ultimo_scambio[j] <= 10):
            x = W[k, j] * Rl[k, j] - W[k, j] * Fl[k, j]
            contr[k] += x; n += 1
            per.setdefault(pan["simboli"][j], 0.0); per[pan["simboli"][j]] += x
print("\nG1 ricerca: giorni-moneta tenuti negli ultimi 8 giorni prima dell'ultimo scambio (o dopo, a prezzo fermo):", n)
print("contributo al netto (prezzo + funding, senza spese): somma %+.2f punti in %d anni, %+.3f punti l'anno" % (100*contr.sum(), len(giorni)//365, 100*contr.sum()/(len(giorni)/365)))
print("per moneta (punti):", {s: round(100*v, 2) for s, v in sorted(per.items(), key=lambda x: -abs(x[1]))[:15]})
j = pan["simboli"].index("TONUSDT"); print("TON ultimo scambio", sc.data(int(ultimo_scambio[j]) + t0), "ultima candela", sc.data(int(np.flatnonzero(np.isfinite(pan['close'][:, j]))[-1]) + t0))
import json
info = {x["symbol"]: x for x in json.load(open("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati/api/exchangeInfo.json"))["symbols"]}
print("\nmonete con onboardDate dopo la prima candela: giorni nell'universo di G1 (ricerca) entro 200 giorni dall'onboard (il bot non le prende)")
okc = np.isfinite(pan["close"])
for s in ("LITUSDT", "PUMPUSDT", "CTKUSDT", "SLPUSDT", "CVXUSDT", "CVCUSDT", "MAVIAUSDT", "AIAUSDT", "TLMUSDT", "BNXUSDT"):
    j = pan["simboli"].index(s); ob = int(info[s]["onboardDate"]) // 86400000
    sel = (giorni >= ob) & (giorni < ob + 200)
    nu = int(Ud[sel, j].sum()); nw = int((W[sel, j] != 0).sum())
    x = (W[sel, j] * (R[sel, j] - F[sel, j])).sum()
    print(f"  {s:10s} onboard {sc.data(ob)}: giorni nell'universo {nu}, con peso {nw}, contributo {100*x:+.2f} punti; stato {info[s]['status']}")
for s in ("TONUSDT", "OMUSDT", "IPUSDT"):
    print(s, info.get(s, {}).get("status"), info.get(s, {}).get("contractType"), "deliveryDate", info.get(s, {}).get("deliveryDate"))
print("\ncon la data di chiusura vera (deliveryDate di exchangeInfo, solo i 137 perpetui oggi in SETTLING):")
consegna = {s: int(x["deliveryDate"]) // 86400000 for s, x in info.items() if x.get("contractType") == "PERPETUAL" and x.get("status") == "SETTLING"}
tot = 0.0; nn = 0; per2 = {}
for k in range(len(giorni)):
    for j in np.flatnonzero(W[k]):
        s = pan["simboli"][j]
        if s in consegna and 0 <= consegna[s] - giorni[k] <= 8:
            x = W[k, j] * (R[k, j] - F[k, j]); tot += x; nn += 1; per2[s] = per2.get(s, 0.0) + x
print("giorni-moneta tenuti da G1 negli 8 giorni prima della chiusura (il bot li toglie):", nn, "| contributo %+.2f punti in tutto" % (100 * tot))
print("per moneta:", {s: round(100 * v, 2) for s, v in sorted(per2.items(), key=lambda x: -abs(x[1]))[:10]})
