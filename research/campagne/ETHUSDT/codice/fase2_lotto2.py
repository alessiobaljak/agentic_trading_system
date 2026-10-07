"""Fase 2, secondo lotto: le 6 varianti del secondo gruppo di idee con stima sopra il minimo.
Si lancia DOPO la fine del primo lotto (gli id del log sono progressivi e il log e' uno solo).
Le previsioni sono quelle di ipotesi.md (secondo lotto), copiate qui prima di lanciare."""
from __future__ import annotations

import sys
import traceback
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
from fase2_lotto1 import CRITERIO  # noqa: E402  (stesso criterio di successo)
from fase2_test import esegui_variante  # noqa: E402
from log import aggiungi, leggi  # noqa: E402

LOTTO = [
    ("I-14", "short", "R medio +0,02 a +0,06 lordo, profit factor 1,0-1,1; muore a costi doppi; non batte nettamente le entrate casuali"),
    ("I-14", "long", "R medio +0,02 a +0,06 lordo, profit factor 1,0-1,1; stesso andamento dello short"),
    ("I-15", "long", "profit factor 1,0-1,1, R medio 0 a +0,05; non netto rispetto alle entrate casuali long (trend 2020-21)"),
    ("I-15", "short", "profit factor 0,9-1,05, R medio intorno a zero; non batte le baseline"),
    ("I-16", "long", "profit factor 0,95-1,05, R medio circa 0; non batte nettamente le entrate casuali"),
    ("I-16", "short", "profit factor 0,95-1,05, R medio circa 0; non batte nettamente le entrate casuali"),
]

if __name__ == "__main__":
    fatte = {(v.get("idea"), v.get("direzione")) for v in leggi() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante"}
    for codice, direzione, previsione in LOTTO:
        if (codice, direzione) in fatte:
            print("gia' fatta", codice, direzione)
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
