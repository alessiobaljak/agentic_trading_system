import json, math, os, datetime as dt
import numpy as np, pandas as pd
from statistics import NormalDist
N=NormalDist().cdf
MON=["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
def bs(S,K,T,s,call):
    d1=(math.log(S/K)+0.5*s*s*T)/(s*math.sqrt(T)); d2=d1-s*math.sqrt(T)
    return S*N(d1)-K*N(d2) if call else K*N(-d2)-S*N(-d1)
base=pd.read_csv('/tmp/revisore110/dati/base.csv')
out=[]
for _,r in base.iterrows():
    g0=dt.date.fromisoformat(r.data); g1=g0+dt.timedelta(days=7)
    t0=int(dt.datetime(g0.year,g0.month,g0.day,8,tzinfo=dt.timezone.utc).timestamp()*1000)
    tr=json.load(open(f"/tmp/revisore110/dati/trades/{r.moneta}_{t0}_{t0+3600000}.json"))
    cc=f"{g1.day}{MON[g1.month-1]}{g1:%y}"; exp=int(dt.datetime(g1.year,g1.month,g1.day,8,tzinfo=dt.timezone.utc).timestamp()*1000)
    xs=[x for x in tr if x["instrument_name"].split("-")[1]==cc]
    if not xs: continue
    # metodo 2: mediana dell'IV di scambio (entrambe le direzioni, senza blocchi) con |ln K/S|<2%
    iv2=[x["iv"]/100 for x in xs if "block_trade_id" not in x and x.get("iv") and abs(math.log(float(x["instrument_name"].split("-")[2])/x["index_price"]))<0.02]
    # metodo 3: valore della coppia (acquisto+vendita) allo strike piu' vicino dai prezzi di riferimento, nel primo quarto d'ora con entrambi
    S_first=xs[0]["index_price"]
    Ks=sorted(set(float(x["instrument_name"].split("-")[2]) for x in xs), key=lambda k: abs(k-S_first))
    val=np.nan; Kn=np.nan
    for K in Ks[:3]:
        c=[x for x in xs if x["instrument_name"].endswith(f"-{int(K)}-C")]; p=[x for x in xs if x["instrument_name"].endswith(f"-{int(K)}-P")]
        if c and p:
            best=min(((a,b) for a in c for b in p), key=lambda ab: abs(ab[0]["timestamp"]-ab[1]["timestamp"]))
            a,b=best
            if abs(a["timestamp"]-b["timestamp"])<15*60000:
                S=(a["index_price"]+b["index_price"])/2; T=(exp-(a["timestamp"]+b["timestamp"])/2)/1000/86400/365
                real=(a["mark_price"]*a["index_price"]+b["mark_price"]*b["index_price"])/S   # USD / S
                mod=(bs(S,K,T,r.dvol/100,True)+bs(S,K,T,r.dvol/100,False))/S
                val=real/mod; Kn=K; break
    out.append(dict(moneta=r.moneta,data=r.data,iv2_ratio=np.median(iv2)/(r.dvol/100) if iv2 else np.nan,n2=len(iv2),straddle_ratio=val))
V=pd.DataFrame(out)
C=pd.read_csv('/tmp/revisore110/dati/confronto.csv'); C['r1']=C.iv_atm/(C.dvol/100)
V=V.merge(C[['moneta','data','r1']],on=['moneta','data'])
print(V.groupby('moneta')[['r1','iv2_ratio','straddle_ratio']].agg(['mean','median','count']).round(3).to_string())
print("correlazione r1 - straddle_ratio:", V[['r1','straddle_ratio']].corr().iloc[0,1].round(3))
V.to_csv('/tmp/revisore110/dati/verifica_iv.csv',index=False)
