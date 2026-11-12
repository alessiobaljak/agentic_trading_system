"""Audit G1 (12 nov 2026): i giorni tenuti da G1 senza il dato vero del funding e quelli diversi dal vero, per anno e per causa."""
import importlib.util, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from research.programma6 import seconda as sc
QUI = Path(__file__).parent
spec = importlib.util.spec_from_file_location("g1a", QUI / "g1_2026-11-12.py"); g1a = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], "funding"]; spec.loader.exec_module(g1a)
b = g1a.basi(); pan = sc.pannello()
W, giorni, idx = b["W"], b["giorni"], b["idx"]
V = pan["quote_volume"][idx]
righe = []
for j in np.flatnonzero(np.abs(W).sum(axis=0) > 0):
    s = b["simboli"][j]
    vero = sc.funding_giorni(s)
    for k in np.flatnonzero(W[:, j] != 0):
        g = int(giorni[k]); fv = vero.get(g, np.nan); fp = b["F"][k, j]
        if np.isnan(fv) or abs(fv - fp) > 1e-9:
            righe.append((s, sc.data(g), g, float(W[k, j]), fv, fp, float(np.nan_to_num(V[k, j]))))
d = pd.DataFrame(righe, columns=["moneta", "data", "g", "peso", "vero", "pannello", "volume"])
d["anno"] = d["data"].str[:4]
d["causa"] = np.where(d["vero"].isna(), np.where(d["pannello"] == 0, "senza dato, zero", "senza dato, stimato"),
                      np.where(d["volume"] == 0, "volume zero, azzerato", "diverso"))
d["effetto"] = -d["peso"] * (np.nan_to_num(d["vero"]) - d["pannello"])   # netto vero - netto pannello sul giorno
out = {"per_causa": d.groupby("causa").size().to_dict(), "per_anno": d.groupby(["anno", "causa"]).size().unstack(fill_value=0).to_dict(),
       "monete_senza_dato": d[d["vero"].isna()].groupby("moneta").size().sort_values(ascending=False).head(15).to_dict(),
       "effetto_su_G1_somma": float(d["effetto"].sum()), "diversi_esempi": d[d["causa"] == "diverso"].head(10).values.tolist(),
       "ultimi_giorni_del_periodo_senza_dato": d[(d["g"] >= sc.giorno(2026, 9, 1)) & d["vero"].isna()].groupby("data").size().to_dict()}
print(json.dumps(out, default=str)[:4000])
(QUI / "g1_funding_2026-11-12_esito.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
