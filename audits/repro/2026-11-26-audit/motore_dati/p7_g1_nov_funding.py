import json, numpy as np, pandas as pd
from pathlib import Path
from research.programma6 import seconda as sc
from research.programma6.paper import aggiorna as ag
from research.programma7.revisione_g1n import nucleo as n
QUI = Path("/tmp/claude-0/-home-user-agentic-trading-system/9da12ffe-13c5-5904-8f7e-5ce576103042/scratchpad/audit/motore_dati")
uni = json.load(open(QUI / "universi_nov.json"))
pan = sc.pannello(); t0 = pan["t0"]; T = pan["close"].shape[0]
nov1 = sc.giorno(2026, 11, 1); fine = t0 + T - 1
F_pan = pan["funding"].copy()
p2 = {**pan, "funding": pan["funding"].copy()}; ag.applica_stima(p2); F_st = p2["funding"]
F_vero = F_pan.copy()
for s in uni["unione"]:
    j = pan["simboli"].index(s)
    d = json.load(open(QUI / "api" / "funding_nov" / f"{s}.json"))
    df = pd.DataFrame(d); df["ts"] = df["fundingTime"].astype(np.int64); df["r"] = df["fundingRate"].astype(float)
    df = df.drop_duplicates("ts"); df["g"] = (df["ts"] // 60000 - 1) // 1440
    v = df.groupby("g")["r"].sum()
    for g in range(nov1, fine + 1):
        F_vero[g - t0, j] = v.get(g, 0.0) if np.isfinite(pan["close"][g - t0, j]) else F_vero[g - t0, j]
ini = sc.giorno(2026, 10, 1)
giorni = np.arange(ini, fine + 1); idx = giorni - t0
U = n.universo_giorni(pan, idx)
R = n.ritorni_tenuta(pan["open"], pan["close"])[idx]
costo = np.array([n.costo_di(s) for s in pan["simboli"]])
res = {}
for nome, F in (("vero", F_vero), ("stima", F_st), ("pannello", F_pan)):
    W, _, _ = n.pesi({**pan, "funding": F}, idx, U)
    lordo, sp, fu_vero, D = n.variazioni(W, R, F_vero[idx], costo)   # conto con il funding vero
    _, _, fu_suo, _ = n.variazioni(W, R, F[idx], costo)               # conto con il funding della versione (come lo misura la ricerca)
    res[nome] = dict(W=W, netto_vero=lordo - sp - fu_vero, netto_suo=lordo - sp - fu_suo)
sel = giorni >= nov1
print("giorni dal 1 nov:", int(sel.sum()), sc.data(int(giorni[sel][0])), "-", sc.data(int(giorni[sel][-1])))
Wv = res["vero"]["W"][sel]
for nome in ("stima", "pannello"):
    Wx = res[nome]["W"][sel]
    diversi = [int(((np.sign(Wv[k]) != np.sign(Wx[k])) & ((Wv[k] != 0) | (Wx[k] != 0))).sum()) for k in range(len(Wv))]
    peso_diverso = np.abs(Wv - Wx).sum(axis=1) / 2
    print(f"[{nome}] monete con lato diverso dal vero, per giorno: media {np.mean(diversi):.1f}, max {max(diversi)}; "
          f"peso spostato medio {100*peso_diverso.mean():.1f}% del lordo di un lato")
    nv = res[nome]["netto_vero"][sel]; ns = res[nome]["netto_suo"][sel]
    print(f"   netto (funding vero) somma {100*nv.sum():+.2f}% | netto come lo conta la ricerca con il suo funding {100*ns.sum():+.2f}%")
print(f"[vero] netto somma {100*res['vero']['netto_vero'][sel].sum():+.2f}%")
print("\ngiorno | netto vero | netto stima (contato dalla ricerca) | netto pannello (contato)")
for k in np.flatnonzero(sel):
    print(sc.data(int(giorni[k])), f"{100*res['vero']['netto_vero'][k]:+.2f} {100*res['stima']['netto_suo'][k]:+.2f} {100*res['pannello']['netto_suo'][k]:+.2f}")
for a, b in ((sc.giorno(2026,11,9), sc.giorno(2026,11,14)), (sc.giorno(2026,11,9), sc.giorno(2026,11,20)), (sc.giorno(2026,11,9), sc.giorno(2026,11,22))):
    m = (giorni >= a) & (giorni <= b)
    print(sc.data(a), "-", sc.data(b), "vero %+.2f stima %+.2f pannello %+.2f" % tuple(100*np.prod(1+res[x]["netto_vero" if x=="vero" else "netto_suo"][m]) - 100 for x in ("vero","stima","pannello")))
# parita' sulla base: quante coppie moneta-giorno di novembre sono esattamente al tasso di base (0,03% al giorno)
fv = F_vero[(np.arange(nov1, fine+1) - t0)][:, [pan["simboli"].index(s) for s in uni["unione"]]]
fs = F_st[(np.arange(nov1, fine+1) - t0)][:, [pan["simboli"].index(s) for s in uni["unione"]]]
print("al tasso di base 0,0003: vero %.1f%%, stima %.1f%%" % (100*np.mean(np.isclose(fv, 0.0003, atol=1e-9)), 100*np.mean(np.isclose(fs, 0.0003, atol=1e-9))))
print()
solo_paper = ["ETHFIUSDT", "INJUSDT", "LITUSDT", "TIAUSDT"]; solo_ricerca = ["BTCUSDT", "BNBUSDT", "DOTUSDT", "ETCUSDT", "BATUSDT", "FETUSDT", "STXUSDT"]
for g in (sc.giorno(2026,11,17), sc.giorno(2026,11,18), sc.giorno(2026,11,19), sc.giorno(2026,11,20)):
    k = int(np.flatnonzero(giorni == g)[0])
    riga = []
    for nome in ("vero", "stima"):
        w = res[nome]["W"][k]
        def q(s):
            if s not in pan["simboli"]: return "assente"
            x = w[pan["simboli"].index(s)]
            return f"{100*x:+.1f}" if x else "0"
        riga.append(nome + ": solo paper " + " ".join(f"{s[:-4]} {q(s)}" for s in solo_paper) + " | solo ricerca " + " ".join(f"{s[:-4]} {q(s)}" for s in solo_ricerca))
    print(sc.data(g)); print("  " + riga[0]); print("  " + riga[1])
print("\ncon le spese a limite 0,02% su tutte le variazioni (come gate2/exports/ricalcolo_g1_ricerca_16nov.py):")
for nome, F in (("vero", F_vero), ("stima", F_st)):
    W = res[nome]["W"]
    lordo, sp, fu, D = n.variazioni(W, R, F[idx], costo)
    netto = lordo - np.abs(D) @ np.full(len(costo), n.MAKER) - fu
    for a, b in ((sc.giorno(2026,11,9), sc.giorno(2026,11,14)), (sc.giorno(2026,11,9), sc.giorno(2026,11,20))):
        m = (giorni >= a) & (giorni <= b)
        print(f"  {nome}: {sc.data(a)} - {sc.data(b)} somma dei giorni {100*netto[m].sum():+.2f} punti")
