# sola lettura: G1 della ricerca dal 23 ottobre (come gate2/exports/ricalcolo_g1_ricerca_16nov.py) con tre funding
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, "/home/user/agentic_trading_system")
from research.programma6 import seconda as sc
from research.programma6.paper import aggiorna as ag
from research.programma7.revisione_g1n import nucleo as n
LORO = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati")
G2 = json.load(open("/home/user/agentic_trading_system/gate2/exports/ricalcolo_g1_ricerca_2026-11-23.json"))
uni = json.load(open(LORO / "universi_nov.json"))["unione"]
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]; fine = t0 + T - 1
F_pan = pan["funding"].copy()
p2 = {**pan, "funding": pan["funding"].copy()}; ag.applica_stima(p2); F_st = p2["funding"]
oct31 = sc.giorno(2026, 10, 31)
F_vero = F_st.copy()           # fuori dalle 130 monete resta la stima (non entrano nell'universo)
for s in uni:
    j = pan["simboli"].index(s)
    d = json.load(open(LORO / "api" / "funding_nov" / f"{s}.json"))
    df = pd.DataFrame(d).drop_duplicates("fundingTime")
    ts = df["fundingTime"].astype(np.int64).to_numpy()
    v = pd.Series(df["fundingRate"].astype(float).to_numpy(), index=(ts // 60000 - 1) // 1440).groupby(level=0).sum()
    for g in range(oct31, fine + 1):
        if np.isfinite(pan["close"][g - t0, j]):
            F_vero[g - t0, j] = v.get(g, 0.0)
# variante: vero dal 1 nov ma 31 ottobre come nell'archivio (senza le 00:00 del 1 nov)
F_vero_no31 = F_vero.copy(); F_vero_no31[oct31 - t0] = F_st[oct31 - t0]
ini = sc.giorno(2026, 10, 23)
giorni = np.arange(ini, fine + 1); idx = giorni - t0
U = n.universo_giorni(pan, idx)
R = n.ritorni_tenuta(pan["open"], pan["close"])[idx]
costo = np.array([n.costo_di(s) for s in pan["simboli"]])
paper = {'09':0.78,'10':-0.22,'11':-1.38,'12':0.37,'13':2.84,'14':3.51,'15':-0.58,'16':1.49,'17':-0.17,'18':-1.50,'19':-1.13,'20':1.16}
res = {}
for nome, F in (("vero", F_vero), ("vero_senza31", F_vero_no31), ("stima", F_st), ("pannello90", F_pan)):
    W, _, _ = n.pesi({**pan, "funding": F}, idx, U)
    lordo, sp, fu, D = n.variazioni(W, R, F[idx], costo)
    _, _, fuv, _ = n.variazioni(W, R, F_vero[idx], costo)
    splim = np.abs(D) @ np.full(len(costo), n.MAKER)
    res[nome] = dict(W=W, netto_suo=lordo - splim - fu, netto_fvero=lordo - splim - fuv, lordo=lordo, fu=fu)
# controllo: la versione «stima» rifa' i numeri di gate2 del 23 novembre?
dd = []
for k, g in enumerate(giorni):
    d = sc.data(int(g))
    if d in G2:
        dd.append((d, abs(res["stima"]["lordo"][k] - G2[d]["lordo"]), abs(res["stima"]["fu"][k] - G2[d]["funding"])))
dd = pd.DataFrame(dd, columns=["d", "dl", "df"])
print("stima contro gate2 23 nov: giorni", len(dd), "max |lordo| diff", dd.dl.max(), "max |funding| diff", dd["df"].max())
print("   giorni con diff lordo > 1e-9:", dd[dd.dl > 1e-9].d.tolist()[:10])
a, b = sc.giorno(2026, 11, 9), sc.giorno(2026, 11, 20)
m = (giorni >= a) & (giorni <= b)
print("9-20 nov, somma dei giorni (spese a limite 0,02%%), paper %+.2f:" % sum(paper.values()))
for nome in res:
    print(f"  {nome:13s} contato col suo funding {100*res[nome]['netto_suo'][m].sum():+.2f} | col funding vero {100*res[nome]['netto_fvero'][m].sum():+.2f}")
print("giorno  paper  vero  stima  (paper-vero) (paper-stima)")
for k in np.flatnonzero(m):
    d = sc.data(int(giorni[k])); p = paper[d[-2:]]
    v, s_ = 100*res['vero']['netto_suo'][k], 100*res['stima']['netto_suo'][k]
    print(d, f"{p:+.2f} {v:+.2f} {s_:+.2f}   {p-v:+.2f} {p-s_:+.2f}")
for a2, b2 in ((sc.giorno(2026,11,9), sc.giorno(2026,11,14)), (sc.giorno(2026,11,15), sc.giorno(2026,11,20))):
    mm = (giorni >= a2) & (giorni <= b2)
    pp = sum(paper[sc.data(int(g))[-2:]] for g in giorni[mm])
    print(sc.data(a2), sc.data(b2), "paper %+.2f vero %+.2f stima %+.2f" % (pp, 100*res['vero']['netto_suo'][mm].sum(), 100*res['stima']['netto_suo'][mm].sum()))
solo_paper = ["ETHFIUSDT", "INJUSDT", "LITUSDT", "TIAUSDT"]; solo_ric = ["BTCUSDT", "BNBUSDT", "DOTUSDT", "ETCUSDT", "BATUSDT", "FETUSDT", "STXUSDT"]
for g in (sc.giorno(2026,11,17), sc.giorno(2026,11,20)):
    k = int(np.flatnonzero(giorni == g)[0])
    for nome in ("vero", "stima"):
        w = res[nome]["W"][k]
        f = lambda s: f"{100*w[pan['simboli'].index(s)]:+.1f}"
        print(sc.data(g), nome, "solo paper:", " ".join(f"{s[:-4]} {f(s)}" for s in solo_paper), "| solo ricerca:", " ".join(f"{s[:-4]} {f(s)}" for s in solo_ric))
# lati diversi fra vero e stima, dal 1 nov
sel = giorni >= sc.giorno(2026, 11, 1)
Wv, Ws = res["vero"]["W"][sel], res["stima"]["W"][sel]
div = [int(((np.sign(Wv[k]) != np.sign(Ws[k])) & ((Wv[k] != 0) | (Ws[k] != 0))).sum()) for k in range(len(Wv))]
print("monete con lato diverso vero/stima per giorno dal 1 nov: media %.1f max %d; peso spostato medio %.1f%%" % (np.mean(div), max(div), 100*(np.abs(Wv-Ws).sum(1)/2).mean()))
