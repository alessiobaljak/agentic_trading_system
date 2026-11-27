import json, numpy as np, warnings
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as n
QUI = "/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati"
info = {x["symbol"]: x for x in json.load(open(QUI + "/api/exchangeInfo.json"))["symbols"]}
nm = json.load(open(QUI + "/non_monete_nel_pannello.json"))
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]
C, V = pan["close"], pan["quote_volume"]
m = sc.giorno(2026, 11, 23) - t0
with warnings.catch_warnings():
    warnings.simplefilter("ignore"); med = np.nan_to_num(np.nanmedian(V[m - 30:m], axis=0))
u = n.universo_lunedi(pan, m)
soglia = med[u].min()
print("lunedi 23 nov: universo", int(u.sum()), "mediana del volume della centesima %.1f M" % (soglia / 1e6))
ok = np.isfinite(C); primo = np.where(ok.any(0), ok.argmax(0), T)
for s in nm:
    j = pan["simboli"].index(s)
    if med[j] >= soglia * 0.8:
        print(f"  {s:12s} tipo {info[s]['underlyingType']}/{info[s]['contractType']} sottotipo {info[s].get('underlyingSubType')} mediana {med[j]/1e6:.1f} M, primo {sc.data(primo[j]+t0)}, 200 giorni il {sc.data(primo[j]+t0+200)}, onboard {sc.data(int(info[s]['onboardDate'])//86400000)}")
for s in ("ANTUSDT", "MDTUSDT"):
    x = info[s]; j = pan["simboli"].index(s)
    print(s, x["underlyingType"], x["contractType"], x.get("underlyingSubType"), "onboard", sc.data(int(x["onboardDate"]) // 86400000), "status", x["status"])
    okj = np.flatnonzero(ok[:, j]); salti = okj[1:][np.diff(okj) > 1]
    for t in salti:
        prima = okj[okj < t][-1]
        print(f"   buco {sc.data(prima+t0)} -> {sc.data(t+t0)}: chiusura prima {C[prima, j]:.6g}, apertura dopo {pan['open'][t, j]:.6g}")
