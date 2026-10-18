"""Autopsia: le due analisi aggiunte DOPO aver visto i primi numeri (dichiarate in risultati.md).

1. Il ritardo costa? R dopo i costi per terzi del movimento prima del segnale (misura 2, 4 candele), con i tagli
   presi dai trade della strategia di ogni variante e applicati anche ai suoi trade a caso.
2. Il paper: le misure 3, 5 e 6 sui 668 trade delle coppie validate (esplorativi esclusi), dai campi registrati.
"""
from __future__ import annotations

import gzip
import json
import math
from pathlib import Path

import numpy as np

from research.autopsia.autopsia import QUI, RADICE, bootstrap, _media


def ritardo(righe: list) -> dict:
    per_var = []
    for r in righe:
        s = [t for t in r.get("strategia", []) if t and np.isfinite(t.get("pre4", float("nan")))]
        c = [t for t in r.get("caso", []) if t and np.isfinite(t.get("pre4", float("nan")))]
        if len(s) < 30 or len(c) < 30:
            continue
        q1, q2 = np.percentile([t["pre4"] for t in s], [100 / 3, 200 / 3])
        def terzi(ts):
            return [_media([t["r"] for t in ts if t["pre4"] <= q1]),
                    _media([t["r"] for t in ts if q1 < t["pre4"] <= q2]),
                    _media([t["r"] for t in ts if t["pre4"] > q2])]
        per_var.append({"id": f'{r["campagna"]} {r["id"]}', "strategia": terzi(s), "caso": terzi(c)})
    out = {"varianti": len(per_var)}
    for i, nome in enumerate(("terzo_basso", "terzo_medio", "terzo_alto")):
        out[nome] = {"strategia": _media([v["strategia"][i] for v in per_var]),
                     "caso": _media([v["caso"][i] for v in per_var]),
                     "differenza": bootstrap([v["strategia"][i] - v["caso"][i] for v in per_var])}
    out["alto_meno_basso"] = {
        "strategia": bootstrap([v["strategia"][2] - v["strategia"][0] for v in per_var]),
        "caso": bootstrap([v["caso"][2] - v["caso"][0] for v in per_var])}
    return out


def paper() -> dict:
    t = json.loads(gzip.decompress((RADICE / "ops/results/archivio_20261018/firestore/trades.json.gz").read_bytes()))
    v = [x for x in t.values() if not x.get("esplorativa")]
    righe = []
    for x in v:
        try:
            rischio = abs(float(x["entry_price"]) - float(x["orig_stop"])) * float(x["size"])
            r_netto = float(x["pnl"]) / rischio
            lordo = float(x["bot_pnl_r_lordo"]) if x.get("bot_pnl_r_lordo") is not None else None
            ind = (x.get("indicators_at_entry") or {}).get(x.get("timeframe") or "15m") or {}
            atr_pct = float(ind["atr"]) / float(ind["close"]) if ind.get("atr") and ind.get("close") else float("nan")
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            continue
        righe.append({"r": r_netto, "r_lordo": lordo, "mfe": x.get("mfe_r"), "atr": atr_pct,
                      "motivo": x.get("exit_reason")})
    out = {"trade": len(righe)}
    grandi = [r for r in righe if r["mfe"] is not None and r["mfe"] >= 1.0 and r["r_lordo"] is not None]
    out["m3_quota_con_1R"] = _media([1.0 if (r["mfe"] or 0) >= 1.0 else 0.0 for r in righe])
    out["m3_chiusi_sotto_zero"] = _media([1.0 if r["r_lordo"] <= 0 else 0.0 for r in grandi])
    out["m3_restituito"] = _media([(r["mfe"] - r["r_lordo"]) / r["mfe"] for r in grandi])
    out["r_netto"] = _media([r["r"] for r in righe])
    out["r_lordo"] = _media([r["r_lordo"] for r in righe])
    out["m5_costo_r"] = _media([r["r_lordo"] - r["r"] for r in righe if r["r_lordo"] is not None])
    ok = [r for r in righe if np.isfinite(r["atr"]) and r["r_lordo"] is not None]
    tagli = np.percentile([r["atr"] for r in ok], [20, 40, 60, 80])
    for q in range(5):
        lo = -math.inf if q == 0 else tagli[q - 1]
        hi = math.inf if q == 4 else tagli[q]
        f = [r for r in ok if lo < r["atr"] <= hi]
        out[f"m6_Q{q + 1}"] = {"n": len(f), "atr_pct_mediana": float(np.median([r["atr"] for r in f])),
                               "r_netto": _media([r["r"] for r in f]), "r_lordo": _media([r["r_lordo"] for r in f]),
                               "costo": _media([r["r_lordo"] - r["r"] for r in f])}
    return out


def main() -> int:
    righe = [json.loads(r) for r in (QUI / "varianti.jsonl").read_text(encoding="utf-8").splitlines() if r.strip()]
    out = {"ritardo": ritardo(righe), "paper": paper()}
    (QUI / "aggiunte.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
