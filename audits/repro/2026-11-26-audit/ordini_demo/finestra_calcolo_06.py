import json, sys
D = json.load(open(sys.argv[1]))
TAKER, MAKER, SCARTO = 0.0005, 0.0002, 0.0002
n = 0; diversi = 0; costo_paper = 0.0; costo_giusto = 0.0; mancati_giusti = 0; mancati_paper = 0
for key, k in D.items():
    if not k: continue
    s, giorno = key.split("|"); giorno = int(giorno)
    c = {int(r[0]) // 1000: (float(r[1]), float(r[2]), float(r[3]), float(r[4])) for r in k}
    t9 = giorno + 9 * 60
    if t9 not in c: continue
    p0 = c[t9][3]                                  # il mark alla fine del minuto 00:09 (il paper lo legge verso le 00:09:30)
    paper = [c[t] for t in sorted(c) if giorno + 360 <= t < giorno + 360 + 3600]       # finestra del paper: 00:05-01:05
    giusta = [c[t] for t in sorted(c) if giorno + 600 <= t < giorno + 600 + 3600]      # dall'ordine: 00:10-01:10
    if len(paper) < 55 or len(giusta) < 55: continue
    for dq in (1.0, -1.0):                         # un acquisto e una vendita da 1 USDT di valore
        n += 1
        f_p = (min(x[2] for x in paper) < p0) if dq > 0 else (max(x[1] for x in paper) > p0)
        f_g = (min(x[2] for x in giusta) < p0) if dq > 0 else (max(x[1] for x in giusta) > p0)
        cp = MAKER if f_p else TAKER + SCARTO + dq * (paper[-1][3] - p0) / p0
        cg = MAKER if f_g else TAKER + SCARTO + dq * (giusta[-1][3] - p0) / p0
        costo_paper += cp; costo_giusto += cg
        diversi += f_p and not f_g
        mancati_paper += not f_p; mancati_giusti += not f_g
print(f"ordini ipotetici {n}; non eseguiti: finestra del paper {mancati_paper} ({100*mancati_paper/n:.1f}%), finestra giusta {mancati_giusti} ({100*mancati_giusti/n:.1f}%)")
print(f"eseguiti solo grazie ai minuti prima del prezzo: {diversi} ({100*diversi/n:.1f}%)")
print(f"costo medio per ordine: paper {10000*costo_paper/n:.2f} punti base, finestra giusta {10000*costo_giusto/n:.2f} punti base; "
      f"differenza {10000*(costo_giusto-costo_paper)/n:.2f} punti base del valore scambiato")
