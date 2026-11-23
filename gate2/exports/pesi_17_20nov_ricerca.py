import sys,json,re
r=json.load(open(sys.argv[1]))
files={'2026-11-17':'0756-17nov-stato-ribilancio-1000.md','2026-11-18':'0759-18nov-stato-ribilancio-1000.md','2026-11-19':'0761-19nov-stato-ribilancio-1000.md','2026-11-20':'0763-20nov-stato-ribilancio-1000.md'}
for d,f in files.items():
    txt=open('ops/results/'+f).read().split('## G1 oggi, moneta per moneta')[1].split('\n## ')[0]
    pap={}
    for m,a,b in re.findall(r'([^\s·]+USDT) ([+-]?\d+\.\d+)/([+-]?\d+\.\d+)',txt): pap[m]=float(a)
    ric={k:v*100 for k,v in r[d]['pesi'].items()}
    com=set(pap)&set(ric)
    solo_p=sorted(set(pap)-set(ric)); solo_r=sorted(set(ric)-set(pap))
    dm=sum(abs(pap[m]-ric[m]) for m in com)/max(len(com),1)
    print(d,'paper',len(pap),'ric',len(ric),'comuni',len(com),'segno diverso',[m for m in com if pap[m]*ric[m]<0],'scarto medio %.2f'%dm,'lordo paper %.0f ric %.0f'%(sum(map(abs,pap.values())),sum(map(abs,ric.values()))))
    print('  solo paper',[(m,pap[m]) for m in solo_p]); print('  solo ric',[(m,round(ric[m],2)) for m in solo_r])
