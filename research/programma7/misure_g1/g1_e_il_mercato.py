# G1 e il mercato: i giorni in cui il mercato scende sono i migliori? Ricerca (prova 120, giorni_G1) contro BTC e contro l'indice a pesi
# uguali delle monete dell'universo di G1, stessi giorni (rendimento tenuto da apertura ad apertura).
# Uso: python3 -W ignore research/programma7/misure_g1/g1_e_il_mercato.py (domanda del proprietario del 14 novembre 2026)
import numpy as np, pandas as pd
from research.programma6 import seconda as sc
from research.programma7 import prima as pr
from research.programma6 import terza as te, sesta as se
g = pd.read_csv("research/programma7/risultati_prima/giorni_G1.csv.gz")
pan = sc.pannello(); R = sc.rendimenti(pan)
giorni = g["giorno"].to_numpy(); idx = giorni - pan["t0"]
sim = list(pan["simboli"]); btc = R[idx, sim.index("BTCUSDT")]
ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
U = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
Ri = R[idx]; ew = np.array([np.nanmean(np.where(U[i], Ri[i], np.nan)) for i in range(len(idx))])
n = g["netto"].to_numpy()
ok = np.isfinite(btc) & np.isfinite(ew) & np.isfinite(n)
n, btc, ew, gg = n[ok], btc[ok], ew[ok], giorni[ok]
anni = pd.to_datetime(gg * 86400, unit="s").year
def riga(nome, m):
    b = np.polyfit(m, n, 1)[0]; c = np.corrcoef(m, n)[0, 1]
    q = np.quantile(m, [0.2, 0.8])
    giu, su = n[m <= q[0]].mean(), n[m >= q[1]].mean()
    print(f"{nome}: beta {b:+.2f}, correlazione {c:+.2f}; G1 nei giorni col mercato nel 20% peggiore {100*giu:+.2f}% al giorno, "
          f"nel 20% migliore {100*su:+.2f}%, quando scende {100*n[m<0].mean():+.3f}% / sale {100*n[m>0].mean():+.3f}%")
print(f"giorni {len(n)} (dal {sc.data(int(gg[0]))} al {sc.data(int(gg[-1]))})")
riga("Bitcoin", btc); riga("indice a pesi uguali delle 100", ew)
for a in sorted(set(anni)):
    k = anni == a
    print(a, f"beta sull'indice {np.polyfit(ew[k], n[k], 1)[0]:+.2f}, G1 quando l'indice scende {100*n[k][ew[k]<0].mean():+.3f}% / sale {100*n[k][ew[k]>0].mean():+.3f}%")
giu = ew < 0
print(f"giorni con l'indice giù {giu.sum()} su {len(n)}; somma di G1 nei giorni giù {100*n[giu].sum():+.1f} punti, nei giorni su {100*n[~giu].sum():+.1f}")
gr = g.set_index("giorno").loc[gg]
for col in ("lordo", "funding", "spese"):
    if col in gr:
        v = gr[col].to_numpy()
        print(col, f"giorni giù {100*v[giu].mean():+.3f}% / su {100*v[~giu].mean():+.3f}% al giorno")
