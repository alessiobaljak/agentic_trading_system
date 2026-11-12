"""Audit G1 (12 nov 2026): pesi piu' grandi per moneta, esposizione netta del conto A a 280 USDT e quanto del suo guadagno in piu'
rispetto a G1 viene dal mercato (pendenza della differenza giornaliera sul Bitcoin); Sharpe corretto di A con l'ordine limite piu' severo."""
import importlib.util, json, math, sys
from pathlib import Path
import numpy as np, pandas as pd
from research.programma6 import seconda as sc
QUI = Path(__file__).parent
spec = importlib.util.spec_from_file_location("g1a", QUI / "g1_2026-11-12.py"); g1a = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0], "esposizione"]; spec.loader.exec_module(g1a)
b = g1a.basi(); pan = sc.pannello()
W, giorni = b["W"], b["giorni"]
X = np.load(g1a.CACHE / "X_A280.npy")
g = pd.read_csv(g1a.CACHE / "giorni.csv", index_col=0)
out = {}
k, j = np.unravel_index(np.argmax(np.abs(W)), W.shape)
grandi = [(sc.data(int(giorni[a])), b["simboli"][c], float(W[a, c])) for a, c in zip(*np.nonzero(np.abs(W) > 0.25))]
out["pesi_oltre_25pc"] = {"giorni_moneta": len(grandi), "monete": sorted({x[1] for x in grandi}), "esempi": grandi[:8]}
out["peso_massimo"] = (sc.data(int(giorni[k])), b["simboli"][j], float(W[k, j]))
out["giorni_con_una_moneta_oltre_10pc"] = int((np.abs(W) > 0.10).any(axis=1).sum())
netto = X.sum(axis=1)
out["A280_esposizione_netta"] = {"media": float(netto.mean()), "p5": float(np.percentile(netto, 5)), "p95": float(np.percentile(netto, 95)),
                                 "giorni_oltre_30pc": int((np.abs(netto) > 0.3).sum()), "massimo": float(netto.max()), "minimo": float(netto.min())}
out["G1_esposizione_netta"] = {"media": float(W.sum(axis=1).mean()), "p5": float(np.percentile(W.sum(axis=1), 5)), "p95": float(np.percentile(W.sum(axis=1), 95))}
jb = b["simboli"].index("BTCUSDT")
rb = b["R"][:, jb]
for nome in ("A280", "G1"):
    y = g[nome].to_numpy()
    out[f"pendenza_{nome}_su_BTC"] = float(np.polyfit(rb, y, 1)[0])
diff = g["A280"].to_numpy() - g["G1fisso"].to_numpy()
p = np.polyfit(rb, diff, 1)
out["differenza_A_meno_G1"] = {"annuo": float(diff.mean() * 365), "pendenza_su_BTC": float(p[0]),
                               "parte_dal_mercato_annua": float(p[0] * rb.mean() * 365), "BTC_annuo_medio": float(rb.mean() * 365)}
anni = pd.to_datetime(giorni * 86400, unit="s").year
out["differenza_per_anno"] = {int(a): float(diff[anni == a].mean() * 365) for a in sorted(set(anni))}
out["netto_A_per_anno_medio"] = {int(a): float(netto[anni == a].mean()) for a in sorted(set(anni))}
print(json.dumps(out, default=float, ensure_ascii=False)[:3500])
(QUI / "g1_esposizione_2026-11-12_esito.json").write_text(json.dumps(out, indent=1, default=float, ensure_ascii=False))
