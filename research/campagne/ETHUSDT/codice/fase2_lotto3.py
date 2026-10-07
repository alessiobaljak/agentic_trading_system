"""Fase 2, terzo lotto: le varianti del terzo gruppo di idee con stima sopra il minimo.
Si lancia DOPO la fine del secondo lotto. Previsioni da ipotesi.md (terzo lotto)."""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
from fase2_lotto1 import CRITERIO  # noqa: E402
from fase2_test import esegui_variante  # noqa: E402
from log import aggiungi, leggi  # noqa: E402

LOTTO = [
    ("I-17", "long", "profit factor 1,0-1,15 per il trend 2020-21, non netto rispetto alle entrate casuali long"),
    ("I-17", "short", "profit factor 0,85-1,0; R medio negativo nel 2020-21, positivo nel 2022; non batte le baseline"),
    ("I-18", "long", "profit factor 0,8-0,95 (costi a 1 ora); percentile sotto 90 fra le entrate casuali; non batte le baseline"),
    ("I-18", "short", "profit factor 0,8-0,95; non batte le baseline"),
    ("I-19", "long", "profit factor 1,0-1,2 ma non netto rispetto alle entrate casuali long (trend)"),
    ("I-19", "short", "profit factor 0,8-1,0; non batte le baseline"),
]

if __name__ == "__main__":
    stime: dict = {}
    for f in sorted(QUI.parent.glob("fase1_stime*.json")):
        stime.update(json.loads(f.read_text(encoding="utf-8")))
    fatte = {(v.get("idea"), v.get("direzione")) for v in leggi() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
    for codice, direzione, previsione in LOTTO:
        if (codice, direzione) in fatte:
            print("gia' fatta", codice, direzione)
            continue
        if stime[f"{codice}-{direzione}"]["sotto_minimo"]:
            print("sotto il minimo, scartata altrove", codice, direzione)
            continue
        try:
            esito = esegui_variante(codice, direzione, {"previsione": previsione, "criterio_successo": CRITERIO})
            aggiungi(esito)
            m, c = esito["metriche"], esito["confronto_baseline"]
            print(f"{esito['id']} {codice} {direzione}: n {m['n_trade']} pf {m['profit_factor']} r {m['r_medio']} wr {m['win_rate']} "
                  f"pct_caso {c.get('baseline_b_casuale', {}).get('percentile_del_candidato')} netto_b {c.get('netto_vs_b')} -> {esito['esito_fase2']}", flush=True)
        except Exception as e:
            aggiungi({"id": None, "tipo": "nota", "oggetto": f"errore durante {codice} {direzione}", "testo": traceback.format_exc()[-1500:]})
            print("ERRORE", codice, direzione, e, flush=True)
