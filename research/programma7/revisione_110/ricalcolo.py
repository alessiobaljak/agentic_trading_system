import json, math, datetime as dt
import numpy as np, pandas as pd
from statistics import NormalDist
N=NormalDist().cdf
FEE,CAP,SC,SET=0.0003,0.125,0.03,0.00015
def straddle(s,T=7/365):           # ATM, r=0, in frazione di S
    d1=0.5*s*math.sqrt(T); return 2*(N(d1)-N(-d1))
def costo(p1, sc=SC):              # p1 = premio di UNA opzione in frazione di S
    return min(FEE,CAP*p1)+sc*p1
R=pd.read_csv('/tmp/revisore110/dati/confronto.csv')
dl={}
for m,idx in [("BTC","btc_usd"),("ETH","eth_usd")]:
    dl[m]={x['date']:x['delivery_price'] for x in json.load(open(f'/tmp/revisore110/dati/delivery_{idx}.json'))}
R['D1']=[dl[m][str(dt.date.fromisoformat(d)+dt.timedelta(days=7))] for m,d in zip(R.moneta,R.data)]
def risultato(prem, pag, sc=SC, S1S0=None):
    return prem - pag - 2*costo(prem/2, sc) - SET*(S1S0 if S1S0 is not None else 1)
def boot(x, n=10000):
    rng=np.random.default_rng(2026); mm=rng.choice(x,size=(n,len(x)),replace=True).mean(axis=1)
    return float((np.sum(mm<=0)+1)/(n+1)), float(np.quantile(mm,.025)), float(np.quantile(mm,.975))
def descr(R, col, nome):
    port=R.groupby('data')[col].mean().sort_index()
    p,lo,hi=boot(port.to_numpy())
    anni=pd.to_datetime(port.index).year
    eq=(1+port).cumprod(); dd=float((eq/eq.cummax()-1).min())
    sh=port.mean()/port.std(ddof=1)*math.sqrt(52)
    pa={int(a):round(100*port[anni==a].mean()*52,1) for a in sorted(set(anni))}
    p23=port[anni>=2023]; p23b=boot(p23.to_numpy())[0]
    print(f"{nome}: n {len(port)}, media {100*port.mean():+.3f}%/sett (IC {100*lo:+.2f};{100*hi:+.2f}, p {p:.4f}), Sharpe {sh:.2f}, discesa {100*dd:.1f}%, per anno {pa}; dal 2023 media {100*p23.mean():+.3f}% p {p23b:.3f} Sharpe {p23.mean()/p23.std(ddof=1)*math.sqrt(52):.2f}; per moneta "+
          ", ".join(f"{m} {100*g[col].mean():+.3f}%" for m,g in R.groupby('moneta')))
    return port
R['S1S0']=R.S1/R.S0
R['prem_vero']=[straddle(s) for s in R.iv_atm]
R['rapporto_premio']=R.prem_vero/R.premio_codice
print("rapporto premio vero/premio codice: media %.3f mediana %.3f; per moneta:"%(R.rapporto_premio.mean(),R.rapporto_premio.median()),
      R.groupby('moneta').rapporto_premio.agg(['mean','median']).round(3).to_dict())
print("per anno e moneta (media):"); print(R.assign(anno=R.data.str[:4]).pivot_table(index='anno',columns='moneta',values='rapporto_premio',aggfunc='mean').round(3).to_string())
print("quota venerdi con premio vero > stimato: %.1f%%"%(100*(R.rapporto_premio>1).mean()))
R['pag_deribit']=(R.D1-R.S0).abs()/R.S0
R['A_codice']=R.r_codice
R['B_vero']=[risultato(p,g,S1S0=s) for p,g,s in zip(R.prem_vero,R.pagato,R.S1S0)]
R['C_vero_regol']=[risultato(p,g,S1S0=s) for p,g,s in zip(R.prem_vero,R.pag_deribit,R.D1/R.S0)]
R['D_meno15']=[risultato(0.85*p,g,S1S0=s) for p,g,s in zip(R.premio_codice,R.pagato,R.S1S0)]
R['E_vero_sc12']=[risultato(p,g,sc=0.012,S1S0=s) for p,g,s in zip(R.prem_vero,R.pag_deribit,R.D1/R.S0)]
R['F_vero_mark0']=[risultato(p,g,sc=0.0,S1S0=s) for p,g,s in zip(R.prem_vero,R.pag_deribit,R.D1/R.S0)]
print("premio medio codice %.3f%%, vero %.3f%%, pagato medio %.3f%% (Binance) %.3f%% (regolamento Deribit)"%(100*R.premio_codice.mean(),100*R.prem_vero.mean(),100*R.pagato.mean(),100*R.pag_deribit.mean()))
for c,n in [('A_codice','A codice (DVOL)'),('B_vero','B premio vero, costi del codice'),('C_vero_regol','C premio vero + regolamento Deribit'),
            ('D_meno15','D premio del codice -15%'),('E_vero_sc12','E premio vero, scarto 1,2% (misurato)'),('F_vero_mark0','F premio vero al prezzo di riferimento, scarto 0')]:
    descr(R,c,n)
# pareggio
for k in np.arange(0.80,1.001,0.01):
    x=[risultato(k*p,g,S1S0=s) for p,g,s in zip(R.premio_codice,R.pagato,R.S1S0)]
    pass
lo,hi=0.5,1.0
for _ in range(40):
    k=(lo+hi)/2; x=R.assign(z=[risultato(k*p,g,S1S0=s) for p,g,s in zip(R.premio_codice,R.pagato,R.S1S0)]).groupby('data').z.mean().mean()
    lo,hi=(k,hi) if x<0 else (lo,k)
print("pareggio: il premio vero deve essere almeno il %.1f%% di quello del codice"%(100*k))
R.to_csv('/tmp/revisore110/dati/ricalcolo.csv',index=False)
