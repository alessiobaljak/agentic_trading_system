import zipfile, io, glob, datetime as dt, numpy as np, pandas as pd
base=pd.read_csv('/tmp/revisore110/dati/base.csv')
out=[]
for f in sorted(glob.glob('/tmp/revisore110/dl_binance/*.zip')):
    nm=f.split('/')[-1]; s=nm.split('-')[0]; d=dt.date.fromisoformat(nm.split('EOHSummary-')[1][:10])
    try:
        z=zipfile.ZipFile(f); df=pd.read_csv(io.BytesIO(z.read(z.namelist()[0])))
    except Exception: continue
    if df.empty: continue
    moneta=s[:3]
    b=base[(base.moneta==moneta)&(base.data==str(d))]
    if b.empty: continue
    S0=float(b.S0.iloc[0]); dvol=float(b.dvol.iloc[0])
    g1=d+dt.timedelta(days=7); e=g1.strftime('%y%m%d')
    for hr in (8,9):
        x=df[(df.hour==hr)&(df.symbol.str.split('-').str[1]==e)].copy()
        if x.empty: continue
        x['K']=x.symbol.str.split('-').str[2].astype(float)
        K=x.K.iloc[(x.K-S0).abs().argsort().iloc[0]]
        for typ in ('C','P'):
            y=x[(x.K==K)&(x.type==typ)]
            if y.empty: continue
            y=y.iloc[0]
            bid,ask,mark=y.best_bid_price,y.best_ask_price,y.mark_price
            out.append(dict(moneta=moneta,data=str(d),ora=hr,K=K,S0=S0,tipo=typ,bid=bid,ask=ask,mark=mark,
                            spread_mid=(ask-bid)/(0.5*(ask+bid)) if bid>0 and ask>0 else np.nan,
                            half_vs_mark=(mark-bid)/mark if bid>0 else np.nan,
                            mark_iv=y.mark_iv, bid_iv=y.best_buy_iv, dvol=dvol/100, vol=y.volume_contracts))
R=pd.DataFrame(out); R.to_csv('/tmp/revisore110/dati/binance_eoh.csv',index=False)
for (m,h),g in R.groupby(['moneta','ora']):
    print(m,"ora",h,"n",len(g),"venerdi",g.data.nunique(),"scarto pieno/mezzo: mediana %.1f%% media %.1f%%; (mark-denaro)/mark mediana %.1f%%; mark_iv/DVOL mediana %.3f media %.3f; senza denaro %d; volume medio %.1f"%(
        100*g.spread_mid.median(),100*g.spread_mid.mean(),100*g.half_vs_mark.median(),(g.mark_iv/g.dvol).median(),(g.mark_iv/g.dvol).mean(),(g.bid<=0).sum(),g.vol.mean()))
print(R[R.ora==8].head(12).to_string())
