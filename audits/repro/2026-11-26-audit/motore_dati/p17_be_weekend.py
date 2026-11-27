import numpy as np, warnings
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as n
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]; C, V, O = pan["close"], pan["quote_volume"], pan["open"]
for s in ("BEUSDT", "SNXXUSDT", "MUUUSDT", "MVLLUSDT", "ZHONGJIUSDT", "SKDDUSDT", "SKUUUSDT"):
    j = pan["simboli"].index(s)
    ultimi = range(T - 14, T)
    print(s, " ".join(f"{sc.data(t+t0)[5:]}:{'-' if not np.isfinite(C[t,j]) else round(V[t,j]/1e6,1)}" for t in ultimi))
# simulazione: universo del lunedi' 14 dicembre con le regole di oggi, se i volumi restano quelli delle ultime 30 giornate
m = T - 1   # ultimo giorno (23 nov, lunedi')
with warnings.catch_warnings():
    warnings.simplefilter("ignore"); med = np.nan_to_num(np.nanmedian(V[m - 30:m], axis=0))
ok = np.isfinite(C); primo = np.where(ok.any(0), ok.argmax(0), T)
amm = ok[m - 1] & (med >= 2e6) & np.isfinite(O[m]) & (np.nan_to_num(V[m - 1]) > 0)
lun14 = sc.giorno(2026, 12, 14) - t0
cand = np.flatnonzero(amm & (lun14 - primo >= 200))
scelte = cand[np.argsort(-med[cand], kind="stable")][:100]
print("con i volumi di oggi, fra le 100 del 14 dicembre:", [pan["simboli"][j] for j in scelte if pan["simboli"][j] in ("BEUSDT", "SNXXUSDT", "MUUUSDT", "MVLLUSDT", "ZHONGJIUSDT")])
