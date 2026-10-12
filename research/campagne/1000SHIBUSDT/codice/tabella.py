"""Stampa la tabella delle varianti testate (dal log) in Markdown, per la consegna."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quadro as q  # noqa: E402

voci = [json.loads(r) for r in (q.CARTELLA_CAMPAGNA / "log.jsonl").read_text(encoding="utf-8").splitlines() if r.strip()]
reg = [v for v in voci if v["tipo"] == "registrazione" and v.get("tipo_test") == "variante"]
ris = {v["id"]: v for v in voci if v["tipo"] == "risultato"}
print("| N | id | variante | tf | dir. | trade | R medio | senza 3 migliori | t (a) | t (b) | percentile | esito |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|")


def f(x, n=3):
    return "—" if x is None else f"{x:.{n}f}".replace(".", ",")


for v in reg:
    r = ris[v["id"]]
    m = r["metriche"]
    a, b = r["baseline_a"], r["baseline_b"]
    if r.get("candidato_fase_2"):
        esito = "candidato, scartato in Fase 4 (costi doppi)"
    elif a.get("netta") and b.get("netta"):
        esito = "netta ma R non positivo"
    else:
        esito = "non netta"
    print(f"| {v['variante_n']} | {v['id'].split('-')[-1]} | {v['variante']} | {v['timeframe']} | {v['direzione']} | "
          f"{m['trade']} | {f(m['r_medio'])} | {f(m['r_medio_senza_3_migliori'])} | {f(a.get('t'), 2)} | "
          f"{f(b.get('t'), 2)} | {f(r.get('percentile_caso'), 1)} | {esito} |")
