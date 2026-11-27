import numpy as np, pandas as pd
from research.programma6 import seconda as sc, terza as te, sesta as se, ottava as ot, ventiquattresima as vq, cinquantaseiesima as cs
from research.programma7 import prima as pr
from research.src.dati import funding_da_zip
pan = sc.pannello(); t0 = pan["t0"]
ps = te.pannello_settimane(pan, log=lambda x: None, indicatori_si=False)
giorni = np.arange(se.INIZIO, pr.FINE, dtype=np.int64); idx = giorni - t0
Ud = pr.universo_del_giorno(giorni, ps["lunedi"], ps["U"])
def g1(F_full):
    p = {**pan, "funding": F_full}
    sig = ot.sigma_30(p, idx)
    W = vq.pesi_banda(np.where(np.isfinite(sig), -se.funding_7(p, idx), np.nan), Ud, sig)
    R = sc.rendimenti(p)[idx]; F = np.nan_to_num(F_full[idx])
    costo = sc.costi_moneta(pan["simboli"])
    m = te.conto(W, R, F, costo)
    sp, *_ = cs.spese_a_limite(W, R, giorni, pan["simboli"], costo)
    m["spese"] = sp; m["netto"] = m["lordo"] - m["spese"] - m["funding"]
    return pr.per_settimana(m, giorni)
oggi = g1(pan["funding"])
# il funding come il 23 ottobre: ottobre senza file mensile (media dei 90 giorni coperti prima), 30 settembre senza il regolamento delle 00:00 del 1 ottobre
F23 = pan["funding"].copy(); ott1 = sc.giorno(2026, 10, 1); T = F23.shape[0]
for j, s in enumerate(pan["simboli"]):
    zz = sorted((sc.DATI / s / "funding").glob("*2026-10.zip"))
    if not zz: continue
    for ts, ore, tasso in funding_da_zip(zz[0]):
        if ts == ott1 * 86_400_000: F23[ott1 - 1 - t0, j] -= tasso
    col = F23[:, j].copy(); c_ok = np.isfinite(pan["close"][:, j])
    cop = np.zeros(T, bool); cop[: ott1 - t0] = True
    prima_ok = np.flatnonzero(cop & c_ok)
    if not len(prima_ok): continue
    for t in range(ott1 - t0, T):
        if c_ok[t]:
            col[t] = F23[prima_ok[-90:], j].mean()
    F23[:, j] = np.where(c_ok & (np.nan_to_num(pan["quote_volume"][:, j]) == 0), 0.0, col)
allora = g1(F23)
salvate = pd.read_csv(pr.RIS / "settimane_G1.csv.gz", index_col=0)
w = sc.giorno(2026, 9, 28)
for nome, d in (("salvata (23 ott)", salvate), ("rifatta oggi", oggi), ("rifatta col funding del 23 ott", allora)):
    r = d.loc[w]
    print(f"{nome:32s} settimana 28 set: netto {100*r['netto']:+.3f}  lordo {100*r['lordo']:+.3f}  funding {100*r['funding']:+.3f}  spese {100*r['spese']:+.3f}")
diff = (oggi["spese"] - salvate["spese"]).abs()
print("settimane con spese diverse (oggi contro salvata) > 1e-6:", int((diff > 1e-6).sum()), "; prima del 2023-09:", int((diff[diff.index < sc.giorno(2023, 9, 1)] > 1e-6).sum()))
