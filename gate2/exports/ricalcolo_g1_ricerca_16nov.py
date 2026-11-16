# Ricalcolo di G1 della ricerca dal 23 ott, con applica_stima (funding di novembre dalla stima del premio).
# Uso: python3 gate2/exports/ricalcolo_g1_ricerca_16nov.py <uscita.json>   (dalla radice del repo)
import sys, json; sys.path.insert(0,'.')
import numpy as np
from research.programma6 import seconda as sc
from research.programma6.paper import aggiorna as ag
from research.programma7.revisione_g1n import nucleo as n
pan=sc.pannello(); st=ag.applica_stima(pan); t0=pan["t0"]; T=pan["close"].shape[0]; fin=t0+T-1
print("ultimo giorno pannello", sc.data(int(fin)), "monete con stima", len(st))
ini=sc.giorno(2026,10,23)
giorni=np.arange(ini,fin+1); idx=giorni-t0
U=n.universo_giorni(pan,idx)
W,WN,_=n.pesi(pan,idx,U)
R=n.ritorni_tenuta(pan["open"],pan["close"]); F=pan["funding"]
costo=np.array([n.costo_di(s) for s in pan["simboli"]])
lordo,sp,fu,D=n.variazioni(W,R[idx],F[idx],costo)
spm=np.abs(D)@np.full(len(costo),n.MAKER)
out={}
for k,g in enumerate(giorni):
    w=W[k]
    out[sc.data(int(g))]=dict(lordo=lordo[k],sp_mercato=sp[k],sp_limite=spm[k],funding=fu[k],turnover=float(np.abs(D[k]).sum()),
      pesi={pan["simboli"][j]:float(w[j]) for j in np.flatnonzero(w)})
json.dump(out,open(sys.argv[1],'w'),indent=0,default=float)
for d,v in out.items():
    if d>="2026-11-01": print(d,{a:round(b*100,3) for a,b in v.items() if a in("lordo","sp_mercato","sp_limite","funding")})
