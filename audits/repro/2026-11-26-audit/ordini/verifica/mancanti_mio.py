"""Problema 1, controprova: guadagno del paper G1 sulle monete che il demo non ha, con le posizioni fissate al ribilancio (00:10) e i
giorni del paper (ultimo valore verso le 23:05; il 26 fino alle 04:05). Pesi dalle righe dello stato (0720-0776)."""
import json, sys, calendar, time
import numpy as np
D = json.load(open(sys.argv[1]))
W = {"2026-11-08": {"龙虾USDT": -1.87, "ICPUSDT": -4.36},
"2026-11-09": {"龙虾USDT": -1.95, "ICPUSDT": -4.57, "IRYSUSDT": 0.41}, "2026-11-10": {"龙虾USDT": -1.92, "ICPUSDT": -4.53, "IRYSUSDT": 0.41},
"2026-11-11": {"龙虾USDT": -1.90, "IRYSUSDT": 0.42}, "2026-11-12": {"龙虾USDT": -1.86, "IRYSUSDT": 0.42}, "2026-11-13": {"龙虾USDT": -2.16},
"2026-11-14": {"龙虾USDT": -3.21}, "2026-11-15": {"龙虾USDT": -3.31}, "2026-11-16": {"EVAAUSDT": -0.90, "UAIUSDT": -1.36},
"2026-11-17": {"EVAAUSDT": -0.87, "LITUSDT": 3.31, "UAIUSDT": -1.32}, "2026-11-18": {"EVAAUSDT": -0.88, "LITUSDT": 3.34, "UAIUSDT": -1.33},
"2026-11-19": {"EVAAUSDT": -0.92, "LITUSDT": 3.04, "UAIUSDT": -1.39, "IRYSUSDT": 0.37},
"2026-11-20": {"EVAAUSDT": -0.87, "LITUSDT": 3.29, "UAIUSDT": -1.33, "IRYSUSDT": 0.38},
"2026-11-21": {"EVAAUSDT": -0.88, "LITUSDT": 3.44, "UAIUSDT": -1.34, "IRYSUSDT": 0.41},
"2026-11-22": {"EVAAUSDT": -0.84, "LITUSDT": 3.48, "UAIUSDT": -1.27, "IRYSUSDT": 0.40},
"2026-11-23": {"EVAAUSDT": -0.87, "LITUSDT": 3.15, "PIEVERSEUSDT": -1.82, "UAIUSDT": -1.45, "IRYSUSDT": 1.46},
"2026-11-24": {"EVAAUSDT": -0.88, "LITUSDT": 3.12, "PIEVERSEUSDT": -1.83, "UAIUSDT": -1.45, "IRYSUSDT": 1.86},
"2026-11-25": {"EVAAUSDT": -0.83, "LITUSDT": 3.13, "PIEVERSEUSDT": -1.73, "UAIUSDT": -1.40, "IRYSUSDT": 1.87},
"2026-11-26": {"EVAAUSDT": -0.83, "LITUSDT": 3.20, "PIEVERSEUSDT": -1.73, "UAIUSDT": -1.41, "IRYSUSDT": 2.13}}
DIF = [.10, .08, .12, -.29, -1.15, -1.25, .31, -.12, -.62, .51, .02, .72, -.06, -.76, .74, -.82, .68, .05]
px = {s: {int(r[0]) // 1000: float(r[1]) for r in v["k"]} for s, v in D.items()}          # apertura delle candele da 5 minuti
fu = {s: [(int(x["fundingTime"]) // 1000, float(x["fundingRate"])) for x in v["f"]] for s, v in D.items()}
PRIMO = {s: min(v) for s, v in px.items()}
def p(s, t):
    t = max(t - t % 300, PRIMO[s])
    while t not in px[s]: t -= 300
    return px[s][t]
def g(d): return calendar.timegm(time.strptime(d, "%Y-%m-%d"))
def giorno(t): return time.strftime("%Y-%m-%d", time.gmtime(t))
giorni = [time.strftime("%Y-%m-%d", time.gmtime(g("2026-11-09") + i * 86400)) for i in range(18)]
def pnl(t_a, t_b):
    """guadagno del paper sulle monete mancanti fra t_a e t_b (in punti % del conto), prezzo e funding"""
    prezzo = fund = 0.0
    cuts = sorted({t_a, t_b} | {g(d) + 600 for d in W if t_a < g(d) + 600 < t_b})
    for a, b in zip(cuts[:-1], cuts[1:]):
        dec = giorno(a) if a >= g(giorno(a)) + 600 else giorno(a - 86400)        # decisione in vigore (dalle 00:10)
        reb = g(dec) + 600
        for s, w in W.get(dec, {}).items():
            pr = p(s, reb)
            prezzo += w * (p(s, b) - p(s, a)) / pr
            fund += sum(-w * r * p(s, t) / pr for t, r in fu[s] if a < t <= b)
    return prezzo, fund
tot_p = tot_f = 0.0; resti = []
for i, d in enumerate(giorni):
    a = g(d) - 86400 + 23 * 3600 + 300
    b = g(d) + 23 * 3600 + 300 if d != "2026-11-26" else g(d) + 4 * 3600 + 300
    pp, ff = pnl(a, b)
    tot_p += pp; tot_f += ff
    resti.append(DIF[i] + pp + ff)
    print(f"{d}: paper sulle mancanti prezzo {pp:+.3f} funding {ff:+.3f}; demo-paper {DIF[i]:+.2f}; resto sulle comuni {DIF[i]+pp+ff:+.2f}")
r = np.array(resti)
print(f"TOTALE mancanti: prezzo {tot_p:+.3f}, funding {tot_f:+.3f}, insieme {tot_p+tot_f:+.3f}; resto sulle comuni {r.sum():+.2f}; "
      f"media {r.mean():+.3f} al giorno, t {r.mean()/(r.std(ddof=1)/np.sqrt(len(r))):+.2f}; senza il 13 nov: somma {r.sum()-r[4]:+.2f}, "
      f"t {np.delete(r,4).mean()/(np.delete(r,4).std(ddof=1)/np.sqrt(17)):+.2f}; mediana {np.median(r):+.3f}")
