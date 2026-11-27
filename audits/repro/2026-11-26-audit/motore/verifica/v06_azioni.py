# sola lettura: contratti che non sono monete nel pannello della ricerca, e quando entrano fra le 100 di G1
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc
from research.programma6.esclusi import ESCLUSI
from research.programma7.revisione_g1n import nucleo as n
QUI = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore/verifica")
info = {x["symbol"]: x for x in json.load(open(QUI / "api" / "exchangeInfo.json"))["symbols"]}
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]; S = pan["simboli"]
C, V = pan["close"], pan["quote_volume"]
def non_moneta(x):
    return not (x.get("contractType") == "PERPETUAL" and x.get("underlyingType", "COIN") == "COIN" and "TradFi" not in (x.get("underlyingSubType") or []))
nm = [s for s in S if s in info and non_moneta(info[s])]
assenti = [s for s in S if s not in info]
print("simboli del pannello:", len(S), "| in exchangeInfo:", len(S) - len(assenti), "| non monete secondo exchangeInfo:", len(nm),
      "| di queste in ESCLUSI:", sum(s in ESCLUSI for s in nm))
ok = np.isfinite(C); primo = np.where(ok.any(0), ok.argmax(0), T)
m23 = sc.giorno(2026, 11, 23) - t0
u23 = n.universo_lunedi(pan, m23)
with warnings.catch_warnings():
    warnings.simplefilter("ignore"); med = np.nan_to_num(np.nanmedian(V[m23 - 30:m23], axis=0))
scelte = np.flatnonzero(u23)
print("universo del 23 nov:", int(u23.sum()), "monete; mediana minima fra le scelte %.1f milioni" % (med[scelte].min() / 1e6))
print("non monete nell'universo del 23 nov:", [S[j] for j in scelte if S[j] in nm])
righe = []
for s in nm:
    j = S.index(s)
    if med[j] < med[scelte].min():
        continue
    # primo lunedi' con 200 giorni di vita dal primo giorno del pannello
    lun = next(m for m in range(m23, T + 400) if (m + t0 + 3) % 7 == 0 and m - primo[j] >= n.STORIA)
    onb = pd.Timestamp(int(info[s]["onboardDate"]), unit="ms").date()
    righe.append((s, info[s]["underlyingType"], str(onb), sc.data(int(primo[j] + t0)), round(med[j] / 1e6, 1), sc.data(int(lun + t0))))
print("non monete con la mediana sopra la centesima (simbolo, tipo, onboard, prima candela, mediana mln, primo lunedi' con 200 giorni):")
for r in sorted(righe, key=lambda r: r[-1]): print("  ", r)
j = S.index("BEUSDT")
for d in ((2026, 11, 14), (2026, 11, 15), (2026, 11, 21), (2026, 11, 22)):
    i = sc.giorno(*d) - t0
    print("BEUSDT", sc.data(i + t0), "volume %.2f mln" % (V[i, j] / 1e6))
# universo simulato del 14 dicembre: si allunga il pannello copiando l'ultima settimana (volumi di oggi)
m14 = sc.giorno(2026, 12, 14) - t0
ext = {}
for k in ("close", "open", "quote_volume"):
    a = pan[k]; extra = m14 + 1 - T
    blocco = np.vstack([a[T - 7:]] * (extra // 7 + 1))[:extra]
    ext[k] = np.vstack([a, blocco])
u14 = n.universo_lunedi(ext, m14)
print("universo simulato del 14 dic (ultima settimana ripetuta):", int(u14.sum()), "| non monete dentro:", [S[jj] for jj in np.flatnonzero(u14) if S[jj] in nm])
# ANT, MDT, NU: simboli di vecchie monete oggi azioni
for s in ("ANTUSDT", "MDTUSDT", "NUUSDT"):
    jj = S.index(s); fin = np.flatnonzero(ok[:, jj])
    print(s, "candele dal", sc.data(int(fin[0] + t0)), "al", sc.data(int(fin[-1] + t0)), "| giorni:", len(fin))
jj = S.index("MDTUSDT")
for d in ((2026, 10, 12), (2026, 10, 21)):
    i = sc.giorno(*d) - t0; print("MDTUSDT", sc.data(i + t0), "chiusura", C[i, jj])
lun_all = [m for m in range(400, T) if (m + t0 + 3) % 7 == 0]
jj = S.index("ANTUSDT")
dentro = [sc.data(m + t0) for m in lun_all if n.universo_lunedi(pan, m)[jj]]
print("ANTUSDT fra le 100 di G1 in", len(dentro), "lunedi':", dentro[:1], "...", dentro[-1:])
