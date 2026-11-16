# Pesi di G1 della ricerca per il 14 novembre, banda portata avanti dal 23 ott (argomento 2: indice di partenza; pannello allungato di una riga vuota: i pesi del giorno i usano solo dati fino a i-1),
# confrontati con quelli del paper letti alle 16:41 del 14 nov (ops/results/0742, sezione «G1 oggi, moneta per moneta»).
import sys, re, json; sys.path.insert(0,'.')
import numpy as np
from research.programma6 import seconda as sc
from research.programma6.paper import aggiorna as ag
from research.programma7.revisione_g1n import nucleo as n
pan=sc.pannello(); ag.applica_stima(pan); T=pan["close"].shape[0]
for k in ("open","high","low","close","quote_volume","taker_buy_quote_volume"):
    pan[k]=np.vstack([pan[k],np.full((1,pan[k].shape[1]),np.nan)])
pan["funding"]=np.vstack([pan["funding"],np.zeros((1,pan["funding"].shape[1]))])
ini=int(sys.argv[2]) if len(sys.argv)>2 else sc.giorno(2026,10,23)-pan['t0']
idx=np.arange(ini,T+1); U=n.universo_giorni(pan,idx); W,_,_=n.pesi(pan,idx,U)
w={pan["simboli"][j]:float(W[-1,j])*100 for j in np.flatnonzero(W[-1])}
txt=open(sys.argv[1]).read().split("## G1 oggi, moneta per moneta")[1]
pap={}
for m in re.finditer(r"(\S+USDT) ([+\-−][0-9.]+)/([+\-−][0-9.]+)",txt):
    pap[m.group(1)]=(float(m.group(2).replace("−","-")),float(m.group(3).replace("−","-")))
print("ricerca monete",len(w),"paper",len(pap),"lorda ricerca %.1f"%sum(abs(x) for x in w.values()))
comuni=[s for s in pap if s in w]; solo_p=[s for s in pap if s not in w]; solo_r=[s for s in w if s not in pap]
print("comuni",len(comuni),"solo paper",solo_p,"solo ricerca",solo_r)
# il paper e' letto ai prezzi delle 16:41: confronto di segno e di grandezza
seg=sum(1 for s in comuni if np.sign(w[s])==np.sign(pap[s][0]))
print("stesso segno",seg,"su",len(comuni))
d=sorted(((abs(w[s]-pap[s][0]),s,round(w[s],2),pap[s][0]) for s in comuni),reverse=True)
print("scarto medio assoluto %.2f max"%np.mean([x[0] for x in d]),d[:6])
