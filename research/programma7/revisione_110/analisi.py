import sys; sys.path.insert(0,'/tmp/revisore110/script')
import json, math, os, datetime as dt
import numpy as np, pandas as pd
MON = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
def N(x): return 0.5*(1+math.erf(x/math.sqrt(2)))
def phi(x): return math.exp(-0.5*x*x)/math.sqrt(2*math.pi)
def bs(S,K,T,s,call):
    d1=(math.log(S/K)+0.5*s*s*T)/(s*math.sqrt(T)); d2=d1-s*math.sqrt(T)
    return S*N(d1)-K*N(d2) if call else K*N(-d2)-S*N(-d1)
def vega(S,K,T,s):
    d1=(math.log(S/K)+0.5*s*s*T)/(s*math.sqrt(T)); return S*phi(d1)*math.sqrt(T)
def code(d): return f"{d.day}{MON[d.month-1]}{d:%y}"
base = pd.read_csv('/tmp/revisore110/dati/base.csv')
righe=[]; spr=[]
for _, r in base.iterrows():
    g0=dt.date.fromisoformat(r.data); g1=g0+dt.timedelta(days=7)
    t0=int(dt.datetime(g0.year,g0.month,g0.day,8,tzinfo=dt.timezone.utc).timestamp()*1000)
    f=f"/tmp/revisore110/dati/trades/{r.moneta}_{t0}_{t0+3600000}.json"
    if not os.path.exists(f): continue
    tr=json.load(open(f))
    exp_ms=int(dt.datetime(g1.year,g1.month,g1.day,8,tzinfo=dt.timezone.utc).timestamp()*1000)
    cc=code(g1)
    pts=[]
    for x in tr:
        p=x["instrument_name"].split("-")
        if p[1]!=cc: continue
        K=float(p[2]); call=p[3]=="C"; S=x["index_price"]; T=(exp_ms-x["timestamp"])/1000/86400/365
        iv=x.get("iv"); 
        if not iv or iv<=1 or T<=0: continue
        s=iv/100; m=math.log(K/S)
        v=vega(S,K,T,s)
        if v<=0: continue
        ivm = s - (x["price"]-x["mark_price"])*S/v          # IV al prezzo di riferimento (mark), via vega
        blk = "block_trade_id" in x
        pts.append(dict(K=K,call=call,S=S,T=T,m=m,iv=s,ivm=ivm,price=x["price"],mark=x["mark_price"],dir=x["direction"],blk=blk,
                        ts=x["timestamp"],amt=x["amount"]))
        if abs(m)<0.03 and not blk and x["mark_price"]>0:
            sg = 1 if x["direction"]=="buy" else -1
            spr.append(dict(moneta=r.moneta,data=r.data,anno=g0.year,m=m,half=sg*(x["price"]-x["mark_price"])/x["mark_price"],
                            dir=x["direction"],min=(x["timestamp"]-t0)/60000, tick=0.0001 if r.moneta=="BTC" else 0.0001, mark=x["mark_price"]))
    d=pd.DataFrame(pts)
    out=dict(moneta=r.moneta,data=r.data,S0=r.S0,S1=r.S1,dvol=r.dvol,premio_codice=r.premio,pagato=r.pagato,r_codice=r.r,n_scambi=len(d))
    if len(d):
        w=d[(d.m.abs()<0.04)]
        out["n_atm"]=len(w); out["n_strike"]=w.K.nunique() if len(w) else 0
        iv0=np.nan; metodo=""
        if len(w)>=5 and w.K.nunique()>=2:
            X=np.vstack([np.ones(len(w)),w.m,w.m**2]).T
            try:
                coef,*_=np.linalg.lstsq(X,w.ivm.values,rcond=None); iv0=coef[0]; metodo="fit"
            except Exception: pass
            # robustezza: mediana degli strike piu' vicini
        near=d.iloc[(d.m.abs()).argsort()[:max(1,min(10,len(d)))]]
        out["iv_vicini"]=float(near.ivm.median())
        out["m_vicini"]=float(near.m.abs().median())
        if not np.isfinite(iv0) or abs(iv0-out["iv_vicini"])>0.15:
            iv0=out["iv_vicini"]; metodo="vicini"
        out["iv_atm"]=float(iv0); out["metodo"]=metodo
        # IV di scambio (non mark) per le vendite dei clienti (direction sell = chi prende vende = prezzo denaro)
        ws=w[(w.dir=="sell")&(~w.blk)]
        out["iv_vendite"]=float(ws.iv.median()) if len(ws) else np.nan
        out["prima_ora_min"]=float((d.ts.min()-t0)/60000)
    righe.append(out)
R=pd.DataFrame(righe); R.to_csv('/tmp/revisore110/dati/confronto.csv',index=False)
pd.DataFrame(spr).to_csv('/tmp/revisore110/dati/scarti.csv',index=False)
print(len(R), R.iv_atm.notna().sum())
