import json,numpy as np
d=json.load(open('gate2/exports/ricalcolo_g1_ricerca_2026-11-09.json'))
pap=[-0.27,3.36,-2.13,-0.92,2.25,3.41,-0.68,-0.34,-1.02,-0.58,2.16,0.93]
dem=[-0.27,3.05,-1.85,-0.90,3.47,1.87,-0.49,-0.48,-1.11,-0.59,2.01,1.20]
days=sorted(d)[2:14]
rm=[];rl=[]
for g in days:
    v=d[g]; rm.append((v['lordo']-v['sp_mercato']-v['funding'])*100); rl.append((v['lordo']-v['sp_limite']-v['funding'])*100)
def cum(x): return (np.prod(1+np.array(x)/100)-1)*100
print("giorno ric_lim ric_mer paper demo")
for g,a,b,p,m in zip(days,rl,rm,pap,dem): print(g,round(a,2),round(b,2),p,m,"p-r",round(p-a,2),"m-r",round(m-a,2))
print("cum 25ott-5nov ricerca_limite",cum(rl),"mercato",cum(rm),"paper",cum(pap),"demo",cum(dem))
l=[d[g]['lordo']*100 for g in days]; print("lordo cum",cum(l), "spese lim",sum(d[g]['sp_limite'] for g in days)*100,"spese mer",sum(d[g]['sp_mercato'] for g in days)*100,"fund",sum(d[g]['funding'] for g in days)*100)
# 23-24 e 6-7 nov
for g in ['2026-10-23','2026-10-24','2026-11-06','2026-11-07']:
    v=d[g]; print(g,round((v['lordo']-v['sp_limite']-v['funding'])*100,2))
allr=[(d[g]['lordo']-d[g]['sp_limite']-d[g]['funding'])*100 for g in sorted(d)]
print("cum 23ott-7nov ricerca limite",cum(allr))
print("corr",np.corrcoef(pap,rl)[0,1],np.corrcoef(dem,rl)[0,1],np.corrcoef(pap,dem)[0,1])
print("sd diff paper-ric",np.std(np.array(pap)-np.array(rl),ddof=1),"max",np.max(np.abs(np.array(pap)-np.array(rl))))
