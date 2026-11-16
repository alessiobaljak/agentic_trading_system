# Confronto giorno per giorno 9-16 nov: demo e paper (0746, tabelle «demo contro paper» e «funding e spese veri») contro la ricerca
# (ricalcolo_g1_ricerca_2026-11-16.json, funding stimato dal premio; il pannello arriva al 13 nov). Punti percentuali di equity.
import json
r=json.load(open('gate2/exports/ricalcolo_g1_ricerca_2026-11-16.json'))
G=["2026-11-%02d"%d for d in range(9,17)]
dem=[.88,-.13,-1.25,.08,1.69,2.26,-.27,.35]; pap=[.78,-.22,-1.38,.37,2.84,3.51,-.58,.75]
fd=[.198,.272,.203,.194,.255,.149,.179,.039]; fp=[.231,.418,.358,.121,.162,.115,.168,.054]
sd=[.008,.004,.003,.003,.009,.002,.010,.018]; sp=[.010,.004,.007,.004,.012,.003,.010,.017]
tot=dict(d=0,p=0,rl=0,rm=0); print("giorno | demo paper ric_lim ric_mer | prezzo demo paper ric | fund demo paper ric | spese demo paper ric_lim ric_mer")
for i,g in enumerate(G):
    v=r.get(g)
    if v:
        L=v['lordo']*100; F=-v['funding']*100; sl=v['sp_limite']*100; sm=v['sp_mercato']*100
        rl=L+F-sl; rm=L+F-sm
    else: L=F=sl=sm=rl=rm=float('nan')
    pd_=dem[i]-fd[i]+sd[i]; pp=pap[i]-fp[i]+sp[i]
    print(g,"| %.2f %.2f %.2f %.2f | %.2f %.2f %.2f | %.3f %.3f %.3f | %.3f %.3f %.3f %.3f"%(dem[i],pap[i],rl,rm,pd_,pp,L,fd[i],fp[i],F,sd[i],sp[i],sl,sm))
