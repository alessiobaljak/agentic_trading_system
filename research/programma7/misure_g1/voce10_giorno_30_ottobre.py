"""Voce 10 di MIGLIORARE_G1: il giorno non spiegato del 30 ottobre 2026. Solo misura, nessun dato a mano.
Parte A: finestre da ribilancio a ribilancio del paper G1 (equity scritta dal bot alle 00:09, piu' i costi del ribilancio dopo, da
         ops/results 0676-0679) contro la ricerca (pannello, funding vero, ordini limite) per le stesse finestre: la finestra «29 ott»
         e' dal ribilancio del 29 a quello del 30.
Parte B: per le finestre del 29 e del 30, i pesi del giorno e il contributo di ogni moneta nella ricerca (prezzo da apertura ad apertura,
         funding). Il prezzo di ingresso del paper (mark delle 00:05) non si puo' ricostruire qui: le candele da 1 minuto del periodo A
         sono chiuse al guardiano dei periodi (motore5.controlla_periodo) e non lo si aggira.
Uso: python3 -m research.programma7.misure_g1.voce10_giorno_30_ottobre   (scrive voce10_risultati.json)"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as n
QUI = Path(__file__).parent
EQ = {"2026-10-26": (9814.27, 1.29), "2026-10-27": (10078.39, 0.37), "2026-10-28": (9906.10, 0.88), "2026-10-29": (9807.40, 0.63), "2026-10-30": (10237.30, 1.26), "2026-10-31": (10399.79, 0.74)}
pan = sc.pannello(); t0 = pan["t0"]; fin = t0 + pan["close"].shape[0] - 1
giorni = np.arange(sc.giorno(2026, 10, 23), fin + 1); idx = giorni - t0   # come gate2/exports/ricalcolo_g1_ricerca.py (i pesi hanno memoria)
U = n.universo_giorni(pan, idx); W, WN, _ = n.pesi(pan, idx, U)
R = n.ritorni_tenuta(pan["open"], pan["close"]); F = pan["funding"]
costo = np.array([n.costo_di(s) for s in pan["simboli"]])
lordo, sp, fu, D = n.variazioni(W, R[idx], F[idx], costo)
spl = np.abs(D) @ np.full(len(costo), n.MAKER)
sim = pan["simboli"]
out = {"A": {}, "B": {}}
ks = sorted(EQ)
for a, b in zip(ks[:-1], ks[1:]):
    d = sc.giorno(*map(int, b.split("-"))) ; k = list(giorni).index(sc.giorno(*map(int, a.split("-"))))
    paper = (EQ[b][0] + EQ[b][1]) / EQ[a][0] - 1
    ric = lordo[k] - fu[k] - spl[k]
    out["A"][a] = dict(paper=round(paper * 100, 3), ricerca=round(ric * 100, 3), lordo_ric=round(lordo[k] * 100, 3),
                       funding_ric=round(-fu[k] * 100, 3), spese_limite_ric=round(spl[k] * 100, 3), differenza=round((paper - ric) * 100, 3))
for g in ("2026-10-29", "2026-10-30"):
    k = list(giorni).index(sc.giorno(*map(int, g.split("-")))); w = W[k]; wn = WN[k]; r = R[idx][k]; f = F[idx][k]
    righe = [(sim[j], round(float(w[j]) * 100, 2), round(float(r[j]) * 100, 2), round(float(w[j] * r[j]) * 100, 3), round(float(-w[j] * f[j]) * 100, 4))
             for j in np.flatnonzero(w)]
    righe.sort(key=lambda x: -abs(x[3]))
    out["B"][g] = dict(n_long=int((w > 0).sum()), n_short=int((w < 0).sum()), lungo_tot=round(float(w[w > 0].sum()) * 100, 1),
                       corto_tot=round(float(w[w < 0].sum()) * 100, 1), colonne="simbolo, peso%, ritorno%, contributo% di prezzo, funding incassato%",
                       per_moneta=righe)
json.dump(out, open(QUI / "voce10_risultati.json", "w"), indent=1, default=float, ensure_ascii=False)
for a, v in out["A"].items(): print(a, v)
for g, v in out["B"].items():
    print(g, v["n_long"], v["n_short"], v["lungo_tot"], v["corto_tot"])
    for r in v["per_moneta"][:6]: print("  ", r)
