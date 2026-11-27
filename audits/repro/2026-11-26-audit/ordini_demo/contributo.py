import json, sys, calendar, time
D = json.load(open(sys.argv[1]))
W = {  # pesi del paper G1 (in % del conto) delle monete che il demo non ha avuto, dalle risposte 0728-0776
"2026-11-09": {"龙虾USDT": -1.95, "ICPUSDT": -4.57, "IRYSUSDT": 0.41},
"2026-11-10": {"龙虾USDT": -1.92, "ICPUSDT": -4.53, "IRYSUSDT": 0.41},
"2026-11-11": {"龙虾USDT": -1.90, "IRYSUSDT": 0.42},
"2026-11-12": {"龙虾USDT": -1.86, "IRYSUSDT": 0.42},
"2026-11-13": {"龙虾USDT": -2.16},
"2026-11-14": {"龙虾USDT": -3.21},
"2026-11-15": {"龙虾USDT": -3.31},
"2026-11-16": {"EVAAUSDT": -0.90, "UAIUSDT": -1.36},
"2026-11-17": {"EVAAUSDT": -0.87, "LITUSDT": 3.31, "UAIUSDT": -1.32},
"2026-11-18": {"EVAAUSDT": -0.88, "LITUSDT": 3.34, "UAIUSDT": -1.33},
"2026-11-19": {"EVAAUSDT": -0.92, "LITUSDT": 3.04, "UAIUSDT": -1.39, "IRYSUSDT": 0.37},
"2026-11-20": {"EVAAUSDT": -0.87, "LITUSDT": 3.29, "UAIUSDT": -1.33, "IRYSUSDT": 0.38},
"2026-11-21": {"EVAAUSDT": -0.88, "LITUSDT": 3.44, "UAIUSDT": -1.34, "IRYSUSDT": 0.41},
"2026-11-22": {"EVAAUSDT": -0.84, "LITUSDT": 3.48, "UAIUSDT": -1.27, "IRYSUSDT": 0.40},
"2026-11-23": {"EVAAUSDT": -0.87, "LITUSDT": 3.15, "PIEVERSEUSDT": -1.82, "UAIUSDT": -1.45, "IRYSUSDT": 1.46},
"2026-11-24": {"EVAAUSDT": -0.88, "LITUSDT": 3.12, "PIEVERSEUSDT": -1.83, "UAIUSDT": -1.45, "IRYSUSDT": 1.86},
"2026-11-25": {"EVAAUSDT": -0.83, "LITUSDT": 3.13, "PIEVERSEUSDT": -1.73, "UAIUSDT": -1.40, "IRYSUSDT": 1.87},
"2026-11-26": {"EVAAUSDT": -0.83, "LITUSDT": 3.20, "PIEVERSEUSDT": -1.73, "UAIUSDT": -1.41, "IRYSUSDT": 2.13},
}
# differenza demo meno paper della tabella di 0776
DIF = {"2026-11-09": .10, "2026-11-10": .08, "2026-11-11": .12, "2026-11-12": -.29, "2026-11-13": -1.15, "2026-11-14": -1.25,
       "2026-11-15": .31, "2026-11-16": -.12, "2026-11-17": -.62, "2026-11-18": .51, "2026-11-19": .02, "2026-11-20": .72,
       "2026-11-21": -.06, "2026-11-22": -.76, "2026-11-23": .74, "2026-11-24": -.82, "2026-11-25": .68, "2026-11-26": .05}
def ora(ms): return int(ms) // 1000
kl = {s: {ora(r[0]): (float(r[1]), float(r[4])) for r in v["k"]} for s, v in D.items()}
fu = {s: [(ora(x["fundingTime"]), float(x["fundingRate"])) for x in v["f"]] for s, v in D.items()}
tot_p, tot_f = 0.0, 0.0
righe = []
for g, w in W.items():
    t0 = calendar.timegm(time.strptime(g, "%Y-%m-%d"))
    # dalle 00:20 (il demo esegue alle 00:18) a fine giorno; per il 26 fino alle 04:00 (lettura delle 04:20)
    fine = t0 + 86400 if g != "2026-11-26" else t0 + 4 * 3600
    prezzo, fund = 0.0, 0.0
    dett = []
    for s, x in w.items():
        k = kl[s]
        a = k.get(t0)[0] if t0 in k else None
        ultimo = max(h for h in k if h < fine)
        b = k[ultimo][1]
        r = b / a - 1
        f = sum(rate for t, rate in fu[s] if t0 < t <= fine)
        prezzo += x * r
        fund += -x * f
        dett.append(f"{s[:-4]} {x:+.2f}%x{100*r:+.1f}%")
    tot_p += prezzo; tot_f += fund
    righe.append((g, prezzo, fund, DIF[g], dett))
for g, p, f, d, dett in righe:
    print(f"{g} prezzo {p:+.3f} funding {f:+.3f} -> paper ha in piu' {p+f:+.3f} pp | demo-paper {d:+.2f} | resto {d+(p+f):+.2f} | {'; '.join(dett)}")
print(f"TOTALE monete assenti: prezzo {tot_p:+.3f} pp, funding {tot_f:+.3f} pp, insieme {tot_p+tot_f:+.3f} pp; differenza totale somma {sum(DIF.values()):+.2f} pp")

# controllo di robustezza: ora per ora, pesi della decisione del giorno dalle 00:00 (il paper esegue alle 00:09), giorno della tabella
# dalle 23:00 del giorno prima alle 23:00 (il paper scrive l'ultimo valore verso le 23:06)
print("--- controllo ora per ora (giorno 23:00-23:00) ---")
giorni = sorted(W)
tot = 0.0
for g in giorni:
    t_fine = calendar.timegm(time.strptime(g, "%Y-%m-%d")) + 23 * 3600
    if g == "2026-11-26":
        t_fine = calendar.timegm(time.strptime(g, "%Y-%m-%d")) + 4 * 3600
    t_ini = calendar.timegm(time.strptime(g, "%Y-%m-%d")) - 3600
    somma = 0.0
    for h in range(t_ini, t_fine, 3600):
        dec = time.strftime("%Y-%m-%d", time.gmtime(h))     # la decisione in vigore in quell'ora
        w = W.get(dec, {})
        for s, x in w.items():
            k = kl[s]
            if h in k:
                o, c = k[h]
                somma += x * (c / o - 1)
            somma += -x * sum(rate for t, rate in fu[s] if h < t <= h + 3600)
    tot += somma
    print(g, f"{somma:+.3f}")
print(f"TOTALE ora per ora {tot:+.3f} pp")
