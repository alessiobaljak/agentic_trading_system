"""Voce 12 di MIGLIORARE_G1: il lato venduto di G1 nel 2026 contro gli anni prima (1 gen - 4 ott di ogni anno).
Solo misura. Rendimento del lato venduto = prezzo (-S*R... qui S*R, negativo se sale) + funding incassato - spese.
Uso: python3 -m research.programma7.misure_g1.voce12_venduto_2026"""
from __future__ import annotations
import json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from research.programma6 import seconda as sc
from research.programma7.revisione_g1n import nucleo as nu
QUI = Path(__file__).parent

def main():
    pan = sc.pannello(); sim = pan["simboli"]
    costo = np.array([nu.costo_di(s) for s in sim])
    C, V = pan["close"], pan["quote_volume"]
    ok = np.isfinite(C); primo = np.where(ok.any(0), ok.argmax(0), C.shape[0])
    out = {}; righe = []
    for anno in range(2021, 2027):
        g = np.arange(sc.giorno(anno, 1, 1), sc.giorno(anno, 10, 5), dtype=np.int64); idx = g - pan["t0"]
        R = nu.ritorni_tenuta(pan["open"], C)[idx]; F = np.nan_to_num(pan["funding"][idx])
        U = nu.universo_giorni(pan, idx)
        W, _, _ = nu.pesi(pan, idx, U, fisso=(1.0, 1.0))
        # spese per moneta (variazioni con deriva, come nucleo.variazioni)
        _, _, _, D = nu.variazioni(W, R, F, costo)
        S = np.where(W < 0, W, 0.0)
        prezzo = S * R; fund = -(S * F); spese = -(np.abs(np.where(W < 0, D, 0.0)) * costo)
        tot = prezzo + fund + spese
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            vol30 = np.stack([np.nanmean(V[i - 30:i], axis=0) for i in idx])
        età = idx[:, None] - primo[None, :]
        # terzili di volume tra le monete vendute del giorno
        terz = np.full(W.shape, -1)
        for k in range(len(idx)):
            j = np.flatnonzero(W[k] < 0)
            if len(j) >= 3:
                r = pd.Series(vol30[k, j]).rank(method="first").values / len(j)
                terz[k, j] = np.minimum((r * 3).astype(int), 2) if False else np.minimum(((r - 1e-9) * 3).astype(int), 2)
        def gr(mask): return float(tot[mask].sum())
        o = {"prezzo": float(prezzo.sum()), "funding": float(fund.sum()), "spese": float(spese.sum()), "totale": float(tot.sum())}
        o["volume_piccole_medie_grandi"] = [gr(terz == t) for t in (0, 1, 2)]
        o["eta_200-365_365-730_oltre730"] = [gr((W < 0) & (età >= a) & (età < b)) for a, b in ((0, 365), (365, 730), (730, 99999))]
        gran = (W < 0) & (R > 0.20)
        o["fiammate_oltre20"] = {"n": int(gran.sum()), "prezzo": float(prezzo[gran].sum()), "resto_totale": float(tot[~gran].sum())}
        m = pd.Series(tot.sum(1), index=pd.to_datetime(g * 86400, unit="s").strftime("%m")).groupby(level=0).sum()
        o["per_mese"] = {k: round(float(v), 4) for k, v in m.items()}
        mc = np.where(W < 0, tot, np.nan).ravel(); o_idx = np.argsort(np.nan_to_num(mc, nan=0.0))[:10]
        pe = [(sc.data(int(g[i // W.shape[1]])), sim[i % W.shape[1]], round(float(mc[i]), 4)) for i in o_idx]
        o["10_peggiori"] = {"somma": float(sum(p[2] for p in pe)), "elenco": pe}
        o["monete_vendute_diverse"] = int((W < 0).any(0).sum())
        # quante monete diverse nel 10 peggiori e quota monete con tot>0 per moneta
        per_moneta = tot.sum(0); att = (W < 0).any(0)
        o["monete_in_perdita_quota"] = float((per_moneta[att] < 0).mean())
        out[anno] = o
    (QUI / "voce12_risultati.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    p = lambda l: " ".join(f"{x*100:+.1f}" for x in l)
    print("anno | prezzo funding spese TOT | vol piccole/medie/grandi | eta<1a/1-2a/>2a | fiamm(n,prezzo) | 10 peggiori | monete perdita%")
    for a, o in out.items():
        print(a, f"{o['prezzo']*100:+.1f} {o['funding']*100:+.1f} {o['spese']*100:+.1f} {o['totale']*100:+.1f}", "|", p(o["volume_piccole_medie_grandi"]), "|",
              p(o["eta_200-365_365-730_oltre730"]), "|", o["fiammate_oltre20"]["n"], f"{o['fiammate_oltre20']['prezzo']*100:+.1f}", "|",
              f"{o['10_peggiori']['somma']*100:+.1f}", "|", f"{o['monete_in_perdita_quota']*100:.0f}")
    print("2026 mesi:", out[2026]["per_mese"]); print("2026 peggiori:", out[2026]["10_peggiori"]["elenco"][:5])
main()
