import sys, json; sys.path.insert(0,'.')
import numpy as np
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as n
pan=sc.pannello(); t0=pan["t0"]; T=pan["close"].shape[0]; fin=t0+T-1
ini=sc.giorno(2026,10,23)
giorni=np.arange(ini,fin+1); idx=giorni-t0
U=n.universo_giorni(pan,idx)
W,WN,_=n.pesi(pan,idx,U)
R=n.ritorni_tenuta(pan["open"],pan["close"]); F=pan["funding"]
costo=np.array([n.costo_di(s) for s in pan["simboli"]])
lordo,sp,fu,D=n.variazioni(W,R[idx],F[idx],costo)
spm=np.abs(D)@np.full(len(costo),n.MAKER)
# solo funding vero (fino 31 ott)
out={}
for k,g in enumerate(giorni):
    w=W[k]; top=sorted(np.flatnonzero(w),key=lambda j:-abs(w[j]))[:10]
    out[sc.data(int(g))]=dict(lordo=lordo[k],sp_mercato=sp[k],sp_limite=spm[k],funding=fu[k],n_long=int((w>0).sum()),n_short=int((w<0).sum()),
       top=[(pan["simboli"][j],round(float(w[j])*100,1)) for j in top], turnover=float(np.abs(D[k]).sum()))
json.dump(out,open(sys.argv[1],'w'),indent=1,default=float)
for d,v in out.items(): print(d,{a:(round(b*100,3) if isinstance(b,float) else b) for a,b in v.items() if a!='top'})
print(out["2026-10-23"]["top"])
