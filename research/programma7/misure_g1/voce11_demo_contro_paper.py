"""Voce 11 di MIGLIORARE_G1: perche' il demo fa meglio del paper dall'8 novembre. Solo misura.
Parte A: differenza demo - paper giorno per giorno (8-13 nov) in prezzo / funding / spese, da `ops/results/0738` (tabelle) e
         `0720-0728` (equity dell'8 nov). Il prezzo e' il resto: differenza di equity meno differenza di funding e di spese.
Parte B: per l'8 nov, nel modello della ricerca (motore della prova 148, funding corretto con `applica_stima`), il prezzo della
         differenza tra posizioni tenute dal conto a 1.000 USDT (X) e posizioni volute (W): per moneta.
Uso: python3 -m research.programma7.misure_g1.voce11_demo_contro_paper  (scrive voce11_risultati.json)"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as nu
from research.programma7 import ottantaseiesima as o86
from research.programma6.paper.aggiorna import applica_stima
QUI = Path(__file__).parent

# Parte A. Tabelle di 0738 (in % dell'equity del giorno). Equity di fine giorno 9-13 nov: demo e paper G1 (0738, "demo contro paper").
G = ["9 nov", "10 nov", "11 nov", "12 nov", "13 nov*"]
EQ_D = [0.88, -0.13, -1.25, 0.08, 0.10]; EQ_P = [0.78, -0.22, -1.38, 0.37, 0.35]
FU_D = {"8 nov": 0.155, "9 nov": 0.198, "10 nov": 0.272, "11 nov": 0.203, "12 nov": 0.194, "13 nov*": 0.075}
FU_P = {"8 nov": 0.174, "9 nov": 0.231, "10 nov": 0.418, "11 nov": 0.358, "12 nov": 0.121, "13 nov*": 0.044}
SP_D = {"8 nov": 0.074, "9 nov": 0.008, "10 nov": 0.004, "11 nov": 0.003, "12 nov": 0.003, "13 nov*": 0.009}
SP_P = {"8 nov": 0.014, "9 nov": 0.010, "10 nov": 0.004, "11 nov": 0.007, "12 nov": 0.004, "13 nov*": 0.013}
# 8 nov: equity dall'inizio (demo 1.000; paper 10.619,33 alle 00:21 dell'8 nov, 0720) a fine 8 nov. Demo: 995,20 alle 23:24 (0728, -0,48%).
# Paper: 10.478,03 alle 00:09 del 9 nov (0728; contiene gia' le spese del ribilancio del 9: costi 23,86 contro 22,85 = 1,01 USD).
DEMO_8 = (995.20 / 1000 - 1) * 100
PAPER_8_GREZZO = (10478.03 / 10619.33 - 1) * 100
PAPER_8_SENZA_SPESE_9 = ((10478.03 + (23.86 - 22.85)) / 10619.33 - 1) * 100
# controlli intermedi dell'8 nov: (ora, demo equity, paper G1 equity) da 0720 (00:17/00:21), 0721 (04:18/04:05), 0724 (18:22/18:09), 0726 (20:23/20:09)
CHECK = [("00:2x", 999.59, 10619.33), ("04:xx", 1001.80, 10658.02), ("18:xx", 994.82, 10399.32), ("20:xx", 994.08, 10314.80),
         ("23:24/00:09", 995.20, 10478.03)]

def parte_a():
    righe = []
    # 8 nov
    d8 = DEMO_8 - PAPER_8_SENZA_SPESE_9
    righe.append({"giorno": "8 nov", "demo": round(DEMO_8, 2), "paper": round(PAPER_8_SENZA_SPESE_9, 2), "diff": round(d8, 2),
                  "funding": round(FU_D["8 nov"] - FU_P["8 nov"], 3), "spese": round(-(SP_D["8 nov"] - SP_P["8 nov"]), 3)})
    for g, d, p in zip(G, EQ_D, EQ_P):
        righe.append({"giorno": g, "demo": d, "paper": p, "diff": round(d - p, 2), "funding": round(FU_D[g] - FU_P[g], 3), "spese": round(-(SP_D[g] - SP_P[g]), 3)})
    for r in righe: r["prezzo_resto"] = round(r["diff"] - r["funding"] - r["spese"], 2)
    return righe

def parte_b():
    pan = sc.pannello(); applica_stima(pan); sim = pan["simboli"]
    g_ini, g0, g1 = sc.giorno(2026, 10, 23), sc.giorno(2026, 11, 8), sc.giorno(2026, 11, 11)
    giorni_t = np.arange(g_ini, g1 + 1, dtype=np.int64); idx_t = giorni_t - pan["t0"]
    U_t = nu.universo_giorni(pan, idx_t); W_t, _, _ = nu.pesi(pan, idx_t, U_t, fisso=(1.0, 1.0))
    k0 = int(g0 - g_ini); idx = idx_t[k0:]; W = W_t[k0:]
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]; O = pan["open"][idx]
    vmin, passo, qmin = o86.carica_filtri(sim)
    X, Dd, st = o86.conto_vero(W, R, O, 1000.0, vmin, passo, qmin, True, False)
    out = {"giorni": [sc.data(int(g)) for g in idx_t[k0:] + pan["t0"]]}
    out["esposizione_lorda_voluta"] = np.abs(W).sum(1).round(3).tolist()
    out["esposizione_lorda_tenuta"] = np.abs(X).sum(1).round(3).tolist()
    out["esposizione_netta_voluta"] = W.sum(1).round(4).tolist()
    out["esposizione_netta_tenuta"] = X.sum(1).round(4).tolist()
    out["prezzo_voluto_pct"] = ((W * R).sum(1) * 100).round(3).tolist()
    out["prezzo_tenuto_pct"] = ((X * R).sum(1) * 100).round(3).tolist()
    diff = (X - W) * R
    out["prezzo_gap_pct"] = (diff.sum(1) * 100).round(3).tolist()
    per = {}
    for k, g in enumerate(out["giorni"]):
        o = np.argsort(-np.abs(diff[k]))[:6]
        per[g] = [[sim[j], round(float(W[k, j] * 100), 2), round(float(X[k, j] * 100), 2), round(float(R[k, j] * 100), 2), round(float(diff[k, j] * 100), 3)] for j in o]
    out["gap_per_moneta_(moneta,peso_voluto%,peso_tenuto%,rendimento%,contributo_pts)"] = per
    out["prezzo_gap_senza_BTC_ETH_SOL"] = None
    # quanto del gap e' la parte lunga e quella corta
    out["gap_lunghi_pts"] = (np.where(W > 0, diff, 0).sum(1) * 100).round(3).tolist()
    out["gap_corti_pts"] = (np.where(W < 0, diff, 0).sum(1) * 100).round(3).tolist()
    out["lunghi_voluti_tenuti_%"] = [(np.where(W > 0, W, 0).sum(1)[0] * 100).round(1).item(), (np.where(X > 0, X, 0).sum(1)[0] * 100).round(1).item()]
    out["corti_voluti_tenuti_%"] = [(-np.where(W < 0, W, 0).sum(1)[0] * 100).round(1).item(), (-np.where(X < 0, X, 0).sum(1)[0] * 100).round(1).item()]
    out["mercato_medio_8nov_pct"] = round(float(np.nanmean(R[0][np.abs(W[0]) > 0]) * 100), 3)
    return out

def main():
    A = parte_a()
    for r in A: print(r)
    B = parte_b()
    for k in ("giorni", "esposizione_lorda_voluta", "esposizione_lorda_tenuta", "esposizione_netta_voluta", "esposizione_netta_tenuta",
              "prezzo_voluto_pct", "prezzo_tenuto_pct", "prezzo_gap_pct", "gap_lunghi_pts", "gap_corti_pts"): print(k, B[k])
    print("lunghi voluti/tenuti", B["lunghi_voluti_tenuti_%"], "corti", B["corti_voluti_tenuti_%"])
    print("8 nov per moneta", B["gap_per_moneta_(moneta,peso_voluto%,peso_tenuto%,rendimento%,contributo_pts)"]["2026-11-08"])
    (QUI / "voce11_risultati.json").write_text(json.dumps({"parte_a": A, "parte_b": B, "controlli_8nov": CHECK}, indent=1, ensure_ascii=False), encoding="utf-8")
if __name__ == "__main__":
    main()
