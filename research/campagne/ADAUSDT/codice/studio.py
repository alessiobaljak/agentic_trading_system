"""Fase 3: studio dei fallimenti di una variante gia' testata, solo sui suoi trade di costruzione.
R medio e numero di trade per gruppi di caratteristiche note all'ingresso (nessun dato dopo l'ingresso
tranne l'esito). Scrive in research/data/insample/ADAUSDT/studio_<ID>.json e stampa.

  python studio.py <ID>
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comune as C  # noqa: E402
import varianti as V  # noqa: E402

ident = sys.argv[1]
var = V.VARIANTI[ident]
D = C.carica(var.tf)
A = C.arrays(D["candele"])
idx = {int(t): k for k, t in enumerate(A["ts"])}
atr = C.atr(A["h"], A["l"], A["c"], 14) / A["c"]
passo = D["passo"]
n24 = max(1, int(86_400_000 // passo))
ret24 = C.rendimento(A["c"], n24)
b = D["btc_close"]
bret24 = np.full(len(b), np.nan)
bret24[n24:] = b[n24:] / b[:-n24] - 1
ma = C.sma(A["c"], max(2, int(20 * 86_400_000 // passo)))  # media a 20 giorni
trades = json.loads((C.RADICE / "research" / "data" / "insample" / "ADAUSDT" / f"trade_{ident}.json").read_text())
righe = []
for t in trades:
    k = idx[t["e"]] - 1  # barra di segnale
    d = datetime.fromtimestamp(t["e"] / 1000, tz=timezone.utc)
    righe.append({"r": t["r"], "esito": t["esito"], "anno": d.year, "ora": d.hour, "giorno": d.weekday(),
                  "stop_pct": abs(t["entrata"] - t["stop"]) / t["entrata"], "atr_pct": atr[k],
                  "ret24": ret24[k], "btc24": bret24[k], "sopra_ma20g": bool(A["c"][k] > ma[k]) if np.isfinite(ma[k]) else None})


def gruppi(chiave, f):
    g = {}
    for r in righe:
        x = f(r)
        if x is None:
            continue
        g.setdefault(x, []).append(r["r"])
    return {str(k): {"n": len(v), "r_medio": round(float(np.mean(v)), 4)} for k, v in sorted(g.items())}


def quintili(campo):
    vals = np.array([r[campo] for r in righe if np.isfinite(r[campo])])
    q = np.quantile(vals, [0.2, 0.4, 0.6, 0.8])
    return gruppi(campo, lambda r: int(np.searchsorted(q, r[campo])) if np.isfinite(r[campo]) else None), [round(float(x), 5) for x in q]


out = {"id": ident, "n": len(righe), "r_medio": float(np.mean([r["r"] for r in righe])),
       "esito": gruppi("esito", lambda r: r["esito"]), "anno": gruppi("anno", lambda r: r["anno"]),
       "ora": gruppi("ora", lambda r: r["ora"] // 4 * 4), "giorno_settimana": gruppi("g", lambda r: r["giorno"]),
       "sopra_media_20_giorni": gruppi("ma", lambda r: r["sopra_ma20g"]),
       "btc_24h_su": gruppi("b", lambda r: bool(r["btc24"] > 0) if np.isfinite(r["btc24"]) else None),
       "ada_24h_su": gruppi("a", lambda r: bool(r["ret24"] > 0) if np.isfinite(r["ret24"]) else None)}
for campo in ("stop_pct", "atr_pct"):
    out[f"quintili_{campo}"], out[f"soglie_{campo}"] = quintili(campo)
(C.RADICE / "research" / "data" / "insample" / "ADAUSDT" / f"studio_{ident}.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
