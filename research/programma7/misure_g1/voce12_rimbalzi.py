"""Voce 12 (23 nov 2026): G1, lato comprato e venduto nei giorni dopo un crollo del Bitcoin. Solo misura.
Regole in voce12_rimbalzi.md. Uso: python3 -W ignore -m research.programma7.misure_g1.voce12_rimbalzi"""
from __future__ import annotations
import json, warnings
from pathlib import Path
import numpy as np
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as nu
QUI = Path(__file__).parent
H = (1, 3, 7)

def main():
    pan = sc.pannello(); sim = pan["simboli"]; costo = np.array([nu.costo_di(s) for s in sim])
    g = np.arange(sc.giorno(2021, 1, 1), sc.giorno(2026, 10, 5), dtype=np.int64); idx = g - pan["t0"]
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]; F = np.nan_to_num(pan["funding"][idx])
    U = nu.universo_giorni(pan, idx); W, _, _ = nu.pesi(pan, idx, U, fisso=(1.0, 1.0))
    _, _, _, D = nu.variazioni(W, R, F, costo)
    Wp = np.vstack([np.zeros((1, W.shape[1])), W[:-1]])
    spese = -(np.abs(D) * costo)
    lato = np.where(W != 0, np.sign(W), np.sign(Wp))
    Wl = np.where(W > 0, W, 0.0); Ws = np.where(W < 0, W, 0.0)
    cl = Wl * R - Wl * F + np.where(lato > 0, spese, 0.0)
    cs = Ws * R - Ws * F + np.where(lato < 0, spese, 0.0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        V = pan["quote_volume"]; vol = np.stack([np.nanmean(V[i - 30:i], axis=0) for i in idx])
    fascia = np.full(W.shape, -1)
    for k in range(len(idx)):
        j = np.flatnonzero(U[k] if U.dtype == bool else U[k] > 0)
        if len(j):
            o = np.argsort(np.argsort(-np.nan_to_num(vol[k, j], nan=-1))) + 1
            fascia[k, j] = np.where(o <= 10, 0, np.where(o <= 50, 1, 2))
    b = sim.index("BTCUSDT"); c = pan["close"][idx, b]
    caduta = np.full(len(idx), np.nan); caduta[3:] = c[3:] / c[:-3] - 1
    ev, ult = [], -999
    for k in range(3, len(idx)):
        if caduta[k] <= -0.10 and k - ult >= 14: ev.append(k); ult = k
    ev = np.array(ev); isev = np.zeros(len(idx), bool); isev[ev] = True
    n = len(idx)
    def fin(x, s, h): return x[s + 1:s + 1 + h].sum()
    out = {"eventi": [sc.data(int(g[k])) for k in ev], "n_eventi": len(ev), "h": {}}
    cg = cl + cs
    serie = {"G1": cg.sum(1), "comprato": cl.sum(1), "venduto": cs.sum(1)}
    for f, nm in enumerate(("1-10", "11-50", "51-100")):
        serie["comp " + nm] = np.where(fascia == f, cl, 0).sum(1); serie["vend " + nm] = np.where(fascia == f, cs, 0).sum(1)
    righe = []
    for h in H:
        e = ev[ev + h < n]
        start = [s for s in range(0, n - h - 1) if not isev[max(0, s - 7):s].any()]
        d = {}
        for nm, x in serie.items():
            a = np.array([fin(x, s, h) for s in e]); bb = np.array([fin(x, s, h) for s in start])
            d[nm] = {"media_dopo": float(a.mean()), "scarto": float(a.std(ddof=1)), "errore": float(a.std(ddof=1) / np.sqrt(len(a))),
                     "positivi": int((a > 0).sum()), "n": int(len(a)), "media_normale": float(bb.mean()), "scarto_normale": float(bb.std(ddof=1))}
        out["h"][h] = d
    # per unita' di peso, dopo (7 giorni) contro normale
    pu = {}
    post = np.zeros(n, bool)
    for k in ev: post[k + 1:k + 8] = True
    norm = np.array([not isev[max(0, s - 7):s].any() for s in range(n)]) & ~post
    for lat, cc, ww in (("comprato", cl, Wl), ("venduto", cs, Ws)):
        for f, nm in enumerate(("1-10", "11-50", "51-100")):
            m = fascia == f
            pu[f"{lat} {nm}"] = {"dopo7": float(np.where(m & post[:, None], cc, 0).sum() / np.abs(np.where(m & post[:, None], ww, 0)).sum()),
                                  "normale": float(np.where(m & norm[:, None], cc, 0).sum() / np.abs(np.where(m & norm[:, None], ww, 0)).sum())}
    out["per_unita_di_peso_giornaliero"] = pu
    (QUI / "voce12_rimbalzi_risultati.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print("eventi", len(ev), out["eventi"][:3], "...")
    print("dopo | media dopo (errore, positivi/n) | media normale   [somme % non composte]")
    for h in H:
        for nm in ("G1", "comprato", "venduto", "vend 1-10", "vend 11-50", "vend 51-100"):
            d = out["h"][h][nm]
            print(f"{h}g {nm:11s} {d['media_dopo']*100:+6.2f} (±{d['errore']*100:.2f}, {d['positivi']}/{d['n']}) | {d['media_normale']*100:+6.2f}")
    print("per peso/giorno (punti base) dopo7 vs normale:", {k: (round(v['dopo7']*1e4, 1), round(v['normale']*1e4, 1)) for k, v in pu.items() if k.startswith('venduto')})
main()
