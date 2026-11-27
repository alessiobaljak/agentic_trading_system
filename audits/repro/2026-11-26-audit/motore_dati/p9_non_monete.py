import json, numpy as np
from research.programma6 import seconda as sc
from research.programma6.esclusi import ESCLUSI
from research.programma7.revisione_g1n import nucleo as n
QUI = "/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati"
info = {x["symbol"]: x for x in json.load(open(QUI + "/api/exchangeInfo.json"))["symbols"]}
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]
def non_moneta(x):
    return (x.get("underlyingType", "COIN") != "COIN" or "TradFi" not in [] and "TradFi" in (x.get("underlyingSubType") or [])
            or x.get("contractType") == "TRADIFI_PERPETUAL")
nm = [s for s in pan["simboli"] if s in info and non_moneta(info[s])]
print("nel pannello:", len(pan["simboli"]), "simboli; non monete per il tipo ufficiale:", len(nm))
print("  tipi:", sorted({(info[s]["underlyingType"], info[s]["contractType"]) for s in nm}))
print("  esempi:", nm[:40])
# primo giorno con prezzo e volume mediano recente
C, V = pan["close"], pan["quote_volume"]
for s in nm:
    j = pan["simboli"].index(s)
    ok = np.flatnonzero(np.isfinite(C[:, j]))
    med = float(np.nanmedian(V[-30:, j])) if len(ok) else 0
    print(f"   {s:14s} dal {sc.data(int(ok[0]) + t0) if len(ok) else '-'}  giorni {len(ok)}  volume mediano 30g {med/1e6:.1f} M")
# sono mai entrate fra le 100 di G1 (ogni lunedi' dal 2021)?
lun = [m for m in range(sc.giorno(2021, 1, 4) - t0, T) if (m + t0 + 3) % 7 == 0]
dentro = {}
for m in lun:
    u = n.universo_lunedi(pan, m)
    for s in nm:
        if u[pan["simboli"].index(s)]: dentro.setdefault(s, []).append(sc.data(m + t0))
print("entrate fra le 100 di G1:", {s: (len(v), v[0], v[-1]) for s, v in dentro.items()})
json.dump(nm, open(QUI + "/non_monete_nel_pannello.json", "w"))
