"""Stampa una riga per voce del log: id, tipo e i numeri principali (solo lettura).

Uso: python research/campagne/ETHUSDT/codice/elenco_log.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import registro  # noqa: E402


def main() -> None:
    for i, v in enumerate(registro.voci(), 1):
        chiavi = ("id", "tipo", "tipo_test", "variante_ipotesi", "verifica", "variante_n", "trade_stimati")
        x = {k: v.get(k) for k in chiavi if v.get(k) is not None}
        extra = ""
        if v["tipo"] == "risultato":
            m = v.get("metriche") or {}
            b = v.get("baseline_b") or {}
            extra = f" r={m.get('r_medio')} n={m.get('trade')} tb={b.get('t')} cand={v.get('candidato')} sup={v.get('superata')}"
        if v["tipo"] in ("nota", "correzione"):
            extra = " " + json.dumps({k: w for k, w in v.items() if k not in ("id", "tipo", "data")}, ensure_ascii=False)[:300]
        print(i, x, extra)


if __name__ == "__main__":
    main()
