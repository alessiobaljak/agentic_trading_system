import numpy as np
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as n
pan = sc.pannello(); t0 = pan["t0"]; C, O, V = pan["close"], pan["open"], pan["quote_volume"]
T, S = C.shape
for s in ("LITUSDT", "CTKUSDT", "CVCUSDT", "PUMPUSDT", "SLPUSDT"):
    j = pan["simboli"].index(s)
    rc = C[1:, j] / C[:-1, j] - 1
    k = np.nanargmax(np.abs(rc))
    print(f"{s}: salto massimo chiusura su chiusura {100*rc[k]:+.0f}% il {sc.data(k+1+t0)}  (chiusure {C[k,j]:.5g} -> {C[k+1,j]:.5g}, volume {V[k+1,j]/1e6:.1f} M)")
# rendimenti di tenuta estremi (apertura -> apertura dopo) per monete nell'universo di G1 di quella settimana
idx = np.arange(sc.giorno(2021, 1, 4) - t0, T)
U = n.universo_giorni(pan, idx)
R = n.ritorni_tenuta(O, C)[idx]
grossi = np.argwhere(U & ((R > 1.0) | (R < -0.6)))
print("rendimenti di tenuta oltre +100% o sotto -60% dentro l'universo di G1:", len(grossi))
for k, j in grossi[:20]:
    print(f"   {pan['simboli'][j]:12s} {sc.data(idx[k]+t0)} {100*R[k,j]:+.0f}%  apertura {O[idx[k],j]:.5g} apertura dopo {O[idx[k]+1,j] if idx[k]+1<T else float('nan'):.5g} volume {V[idx[k],j]/1e6:.0f} M")
# prezzi fermi: giorni con volume zero dentro l'universo
z = np.argwhere(U & (np.nan_to_num(V[idx]) == 0) & np.isfinite(C[idx]))
print("giorni-moneta a volume zero dentro l'universo di G1:", len(z), [ (pan['simboli'][j], sc.data(idx[k]+t0)) for k, j in z[:10]])
# monete nell'universo della settimana senza candela (tolte dal listino a meta' settimana)
m = np.argwhere(U & ~np.isfinite(O[idx]))
print("giorni-moneta dentro l'universo della settimana senza candela:", len(m), sorted({pan['simboli'][j] for k, j in m})[:30])
