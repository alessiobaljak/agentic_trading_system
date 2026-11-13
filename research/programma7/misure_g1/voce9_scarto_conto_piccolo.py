"""Voce 9 di MIGLIORARE_G1: lo scarto del demo a 1.000 USDT. Solo misura.
Parte A: scomposizione dello scarto per giorno e causa, dalle righe delle risposte della macchina (numeri copiati sotto, con la fonte).
Parte B: G1 ricalcolato con i minimi a 1.000 USDT (motore della prova 148, `ottantaseiesima.conto_vero`) dall'8 al 11 novembre
        (le 4 giornate fino al ribilancio del 12 novembre), contro il demo e il paper; costo delle monete mancanti.
Uso: python3 -m research.programma7.misure_g1.voce9_scarto_conto_piccolo   (scrive voce9_risultati.json)"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as nu
from research.programma7 import ottantaseiesima as o86
from research.programma6.paper.aggiorna import applica_stima
QUI = Path(__file__).parent

# --- Parte A. Per ogni ribilancio: (scarto totale misurato dopo la decisione, % del conto, ora; sotto il minimo % della decisione;
# peso nel paper delle monete mancanti/rifiutate; fonte). Numeri da `ops/results/` (righe "posizioni vere contro volute",
# "ultima decisione", "peso nel paper G1 delle monete rifiutate o mancanti").
A = [
 ("8 nov", 8.9, "8 nov 23:24", 0.8, {"ICPUSDT": 4.36, "龙虾USDT": 1.87}, "0721 (decisione, pesi), 0728 (scarto)"),
 ("9 nov", 13.9, "9 nov 23:31", 6.7, {"ICPUSDT": 4.57, "龙虾USDT": 1.95, "IRYSUSDT": 0.41}, "0728 (decisione, pesi), 0731 (scarto)"),
 ("10 nov", 15.8, "10 nov 23:39", 9.1, {"ICPUSDT": 4.53, "龙虾USDT": 1.92, "IRYSUSDT": 0.41}, "0731 (decisione, pesi), 0733 (scarto)"),
 ("11 nov", 12.2, "11 nov 23:47", 10.0, {"龙虾USDT": 1.90, "IRYSUSDT": 0.42}, "0733 (decisione, pesi), 0735 (scarto)"),
 ("12 nov", 11.8, "12 nov 15:52", 10.4, {"龙虾USDT": 1.86, "IRYSUSDT": 0.42}, "0735 (decisione, pesi), 0736 (scarto)"),
 ("13 nov", 10.2, "13 nov 03:55", 8.2, {"龙虾USDT": 2.16}, "0738 (decisione, pesi, scarto)"),
]
# 8 nov alle 04:18 lo scarto era 7,5% (0721): dopo 4 ore, prima di un riavvio (0724: 9,2% alle 18:22).

def parte_a():
    righe = []
    for g, tot, ora, sotto, manc, fonte in A:
        m = sum(manc.values()); spieg = m + sotto
        righe.append({"giorno": g, "scarto_misurato": tot, "ora": ora, "sotto_il_minimo": sotto, "monete_mancanti": round(m, 2),
                      "dettaglio_mancanti": manc, "somma_spiegata": round(spieg, 2), "non_spiegato": round(tot - spieg, 2), "fonte": fonte})
    return righe

# --- Parte B
def parte_b():
    pan = sc.pannello()
    j = pan["simboli"].index("BTCUSDT"); t_ = pan["close"].shape[0]; i1 = sc.giorno(2026, 11, 1) - pan["t0"]
    prima = [round(float(pan["funding"][i1 + k, j]) * 1e4, 2) for k in range(11)]   # punti base, 1-11 nov, pannello grezzo
    stimati = applica_stima(pan)                                                  # modifica il pannello in place
    dopo = [round(float(pan["funding"][i1 + k, j]) * 1e4, 2) for k in range(11)]
    print("funding BTC 1-11 nov (pb) grezzo", prima, "con stima", dopo, "monete stimate", len(stimati))
    sim = pan["simboli"]
    # banda dei pesi vuota al 23 ottobre come il paper (gate2/reports/2026-11-09-G1.md); i conti si leggono dall'8 al 11 novembre
    g_ini, g0, g1 = sc.giorno(2026, 10, 23), sc.giorno(2026, 11, 8), sc.giorno(2026, 11, 11)
    giorni_t = np.arange(g_ini, g1 + 1, dtype=np.int64); idx_t = giorni_t - pan["t0"]
    U_t = nu.universo_giorni(pan, idx_t); W_t, _, _ = nu.pesi(pan, idx_t, U_t, fisso=(1.0, 1.0))
    k0 = int(g0 - g_ini)
    giorni = giorni_t[k0:]; idx = idx_t[k0:]; W = W_t[k0:]
    R = nu.ritorni_tenuta(pan["open"], pan["close"])[idx]; F = np.nan_to_num(pan["funding"][idx]); O = pan["open"][idx]
    costo = np.array([nu.costo_di(s) for s in sim])
    out = {"giorni": [sc.data(int(g)) for g in giorni]}
    vmin, passo, qmin = o86.carica_filtri(sim)
    # senza minimi: conto a capitale che si compone (nucleo) per il riferimento
    lordo = (W * R).sum(1); fund = (W * F).sum(1); spese_m = np.abs(np.diff(np.vstack([np.zeros(W.shape[1]), W]), axis=0)) @ costo
    out["senza_minimi"] = {"lordo": lordo.tolist(), "funding_pagato": fund.tolist(), "spese_mercato": spese_m.tolist(),
                           "netto_mercato": (lordo - fund - spese_m).tolist()}
    for cap in (1000.0,):
        X, Dd, st = o86.conto_vero(W, R, O, cap, vmin, passo, qmin, True, False)
        lo = (X * R).sum(1); fu = (X * F).sum(1); sp = (np.abs(Dd) * costo).sum(1)
        scarto = np.abs(X - W).sum(1)   # in frazione del capitale, posizioni tenute nel giorno contro volute (senza deriva di prezzo)
        out["con_minimi_1000"] = {"lordo": lo.tolist(), "funding_pagato": fu.tolist(), "spese_mercato": sp.tolist(),
                                  "netto_mercato": (lo - fu - sp).tolist(), "scarto_tenuto_contro_voluto": scarto.tolist(), **st}
    # monete che il demo non ha: contributo del paper (pesi della ricerca; il paper ha le sue ICP/龙虾/IRYS, qui solo se nel pannello)
    manc = {}
    for s in ("ICPUSDT", "IRYSUSDT"):
        if s in sim:
            j = sim.index(s)
            manc[s] = {"peso_ricerca": W[:, j].tolist(), "prezzo": (W[:, j] * R[:, j]).tolist(), "funding_pagato": (W[:, j] * F[:, j]).tolist()}
    out["monete_mancanti_ricerca"] = manc
    out["龙虾_nel_pannello"] = any("龙虾" in s for s in sim)
    out["controllo_funding_btc_1_11_nov_pb"] = {"grezzo": prima, "con_stima": dopo, "monete_stimate": len(stimati)}
    # confronto con il paper: lunghi/corti e ICP nei pesi, giorni 6-7 (controllo) e 8-11
    lo, fu = (W_t * 0), None
    Rt = nu.ritorni_tenuta(pan["open"], pan["close"])[idx_t]; Ft = np.nan_to_num(pan["funding"][idx_t])
    lt, st_, ft, _ = nu.variazioni(W_t, Rt, Ft, costo)
    out["giorni_t"] = [sc.data(int(g)) for g in giorni_t]
    out["netto_composto_giorni_t"] = (lt - st_ - ft).tolist()
    out["lunghi_corti"] = {sc.data(int(g)): [int((W_t[k] > 0).sum()), int((W_t[k] < 0).sum())] for k, g in enumerate(giorni_t)}
    jicp = sim.index("ICPUSDT") if "ICPUSDT" in sim else None
    out["peso_ICP"] = {sc.data(int(g)): (float(W_t[k, jicp]) if jicp is not None else None) for k, g in enumerate(giorni_t)}
    return out

def main():
    ris = {"parte_a": parte_a(), "parte_b": parte_b()}
    (QUI / "voce9_risultati.json").write_text(json.dumps(ris, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in ris["parte_a"]:
        print(r["giorno"], r["scarto_misurato"], "=", r["sotto_il_minimo"], "+", r["monete_mancanti"], "| non spiegato", r["non_spiegato"])
    b = ris["parte_b"]
    for k in ("senza_minimi", "con_minimi_1000"):
        n = np.array(b[k]["netto_mercato"]); print(k, "netto giorni", np.round(n * 100, 3).tolist(), "somma %", round(float(n.sum() * 100), 3))
    for k in ("lordo", "funding_pagato", "spese_mercato"):
        print(k, "senza", round(sum(b["senza_minimi"][k]) * 100, 3), "con", round(sum(b["con_minimi_1000"][k]) * 100, 3))
    print("mancanti", {s: round(sum(v["prezzo"]) * 100, 3) for s, v in b["monete_mancanti_ricerca"].items()}, "龙虾 nel pannello", b["龙虾_nel_pannello"])
    print("ordini voluti/saltati", b["con_minimi_1000"]["ordini_voluti"], b["con_minimi_1000"]["ordini_saltati"])
if __name__ == "__main__":
    main()
