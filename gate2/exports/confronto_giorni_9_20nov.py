import sys,json,re,glob
sys.path.insert(0,'.')
r=json.load(open(sys.argv[1]))
paper={'09':0.78,'10':-0.22,'11':-1.38,'12':0.37,'13':2.84,'14':3.51,'15':-0.58,'16':1.49,'17':-0.17,'18':-1.50,'19':-1.13,'20':1.16}
demo={'09':0.88,'10':-0.13,'11':-1.25,'12':0.08,'13':1.69,'14':2.26,'15':-0.27,'16':1.37,'17':-0.79,'18':-0.99,'19':-1.11,'20':1.88}
sp=0;sd=0;sr=0;n=0;ok=0
for d in paper:
    k='2026-11-'+d; v=r[k]
    ric=(v['lordo']-v['sp_limite']-v['funding'])*100
    print(k,'ric %+.2f pap %+.2f dem %+.2f | pap-ric %+.2f dem-ric %+.2f'%(ric,paper[d],demo[d],paper[d]-ric,demo[d]-ric), 'lordo %+.2f fund %+.3f'%(v['lordo']*100,-v['funding']*100))
    sr+=ric;sp+=paper[d];sd+=demo[d]
print('somme 9-20: ric %.2f paper %.2f demo %.2f'%(sr,sp,sd))
# giorni 16-20
sr=sum((r['2026-11-%d'%d]['lordo']-r['2026-11-%d'%d]['sp_limite']-r['2026-11-%d'%d]['funding'])*100 for d in range(16,21))
print('ric 16-20 %.2f paper %.2f demo %.2f'%(sr,sum(paper[x] for x in ['16','17','18','19','20']),sum(demo[x] for x in ['16','17','18','19','20'])))
