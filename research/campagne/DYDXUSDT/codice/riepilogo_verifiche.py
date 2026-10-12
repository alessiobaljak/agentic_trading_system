"""Riepilogo (sola lettura del log) delle verifiche della Fase 4 di un candidato: una riga per verifica."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import registro  # noqa: E402

cand = sys.argv[1] if len(sys.argv) > 1 else "DYDXUSDT-008"
reg = {v["id"]: v for v in registro.voci() if v.get("tipo") == "registrazione" and v.get("verifica_di") == cand}
for v in registro.voci():
    if v.get("tipo") == "risultato" and v["id"] in reg:
        m = v.get("metriche") or {}
        b = v.get("baseline_b") or {}
        a = v.get("baseline_a") or {}
        print(json.dumps({"id": v["id"], "verifica": v.get("verifica"), "trade": m.get("trade"),
                          "r": round(m["r_medio"], 4) if m.get("r_medio") is not None else None,
                          "t_a": round(a["t"], 2) if isinstance(a.get("t"), float) else a.get("t"),
                          "t_b": round(b["t"], 2) if isinstance(b.get("t"), float) else b.get("t"),
                          "soglia": round(b["soglia"], 2) if isinstance(b.get("soglia"), float) else b.get("soglia"),
                          "netta_b": b.get("netta"), "esito": v.get("esito")}, ensure_ascii=False))
