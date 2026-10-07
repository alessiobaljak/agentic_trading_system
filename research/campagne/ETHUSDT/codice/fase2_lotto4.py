"""Fase 2, quarto lotto: le varianti del quarto gruppo con stima sopra il minimo.
Si lancia DOPO la fine del terzo lotto. Previsioni da ipotesi.md (quarto lotto)."""
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
    ("I-20i", "long", "profit factor 1,0-1,15 (rimbalzo dopo discese a volume alto, la piu' promettente del lotto); non netta"),
    ("I-20i", "short", "profit factor 0,85-1,0 nel 2020-21; non netta"),
    ("I-21", "short", "profit factor 0,9-1,1; non netta (la fonte prevede nessun valore)"),
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
