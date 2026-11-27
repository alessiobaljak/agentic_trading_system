"""Controprova del problema 3: ordini limite ipotetici, finestra che parte prima del prezzo contro finestra dal prezzo.
Varianti: prezzo p0 = chiusura del minuto P (mark alla fine del minuto P); finestra 'paper' = candele [P-k+1 .. P-k+60] (k minuti
prima del prezzo inclusi), finestra 'giusta' = candele [P+1 .. P+60]."""
import json, sys
import numpy as np
D = json.load(open(sys.argv[1]))
TAKER, MAKER, SCARTO = 0.0005, 0.0002, 0.0002
def corri(P, k):
    n = 0; mp = mg = solo_prima = 0; cp_tot = cg_tot = 0.0; extra = []
    for key, kk in D.items():
        if not kk: continue
        s, g = key.split("|"); g = int(g)
        c = {int(r[0]) // 1000: (float(r[1]), float(r[2]), float(r[3]), float(r[4])) for r in kk}
        tP = g + P * 60
        if tP not in c: continue
        p0 = c[tP][3]
        pap = [c[t] for t in range(tP - (k - 1) * 60, tP - (k - 1) * 60 + 3600, 60) if t in c]
        giu = [c[t] for t in range(tP + 60, tP + 60 + 3600, 60) if t in c]
        if len(pap) < 58 or len(giu) < 58: continue
        for dq in (1.0, -1.0):
            n += 1
            fp = (min(x[2] for x in pap) < p0) if dq > 0 else (max(x[1] for x in pap) > p0)
            fg = (min(x[2] for x in giu) < p0) if dq > 0 else (max(x[1] for x in giu) > p0)
            cp = MAKER if fp else TAKER + SCARTO + dq * (pap[-1][3] - p0) / p0
            cg = MAKER if fg else TAKER + SCARTO + dq * (giu[-1][3] - p0) / p0
            cp_tot += cp; cg_tot += cg
            mp += not fp; mg += not fg; solo_prima += fp and not fg
            extra.append(cg - cp)
    e = np.array(extra) * 1e4
    return n, mp, mg, solo_prima, 1e4 * cp_tot / n, 1e4 * cg_tot / n, e.mean(), e.std(ddof=1) / np.sqrt(len(e))
for P, k, nome in [(9, 5, "revisore (p0=chiusura 00:09, finestra 00:05-01:04)"), (9, 4, "revisore _06 (00:06-01:05)"),
                   (8, 4, "p0=chiusura 00:08, 4 minuti prima"), (8, 3, "p0=chiusura 00:08, 3 minuti prima"),
                   (9, 1, "solo il minuto del prezzo (00:09) in piu'"), (9, 0, "nessun minuto prima (controllo: deve dare 0)")]:
    if k == 0:
        n, mp, mg, sp, cp, cg, m, se = corri(P, 0)
    else:
        n, mp, mg, sp, cp, cg, m, se = corri(P, k)
    print(f"{nome}: n {n}; non eseguiti paper {100*mp/n:.1f}% giusta {100*mg/n:.1f}%; solo grazie ai minuti prima {100*sp/n:.1f}%; "
          f"costo paper {cp:.2f} pb, giusto {cg:.2f} pb, differenza {m:.2f} pb (errore {se:.2f})")
