"""Fase 2, primo lotto: le 9 varianti con stima sopra il minimo, in ordine. Ogni variante si
registra nel log immediatamente prima della sua esecuzione (dentro esegui_variante) e il
risultato si scrive subito dopo. Le previsioni sono quelle di ipotesi.md, copiate qui prima
di lanciare."""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

QUI = Path(__file__).resolve().parent
sys.path.insert(0, str(QUI))
from fase2_test import esegui_variante  # noqa: E402
from log import aggiungi, leggi  # noqa: E402

CRITERIO = ("almeno 100 trade; batte nettamente (oltre 2 errori standard, bootstrap a blocchi) la strategia casuale mediana "
            "con la stessa uscita e sta oltre il 90° percentile delle 200 entrate casuali; R medio sopra la baseline a ogni barra; "
            "profit factor dopo costi sopra 1")

LOTTO = [
    ("I-01", "long", "R medio fra 0 e +0,10, profit factor 1,0-1,15, forte nel 2020-21 e nullo nel 2022; NON batte nettamente le entrate casuali long (e' il trend di fondo)"),
    ("I-01", "short", "R medio intorno a zero o negativo, profit factor sotto 1, con il 2022 positivo; non batte le baseline"),
    ("I-03", "long", "win rate 60-65 %, R medio 0 a +0,05, profit factor 1,0-1,1 a costi semplici; non batte nettamente le entrate casuali"),
    ("I-03", "short", "win rate 55-62 %, R medio intorno a zero o negativo nel 2020-21; profit factor sotto 1; non batte le baseline"),
    ("I-05", "long", "R medio +0,02 a +0,08, win rate 52-55 %, profit factor 1,0-1,1; vantaggio decrescente per anno; forse netto rispetto alle entrate casuali ma non a costi doppi"),
    ("I-05", "short", "R medio +0,02 a +0,08, win rate 52-55 %, profit factor 1,0-1,1; stesso andamento del long"),
    ("I-09", "long", "profit factor 0,9-1,05, R medio 0 a -0,03: i costi mangiano l'effetto; non batte le baseline"),
    ("I-09", "short", "profit factor 0,9-1,05, R medio 0 a -0,03; non batte le baseline"),
    ("I-10", "short", "profit factor 1,0-1,2 grazie al funding incassato; sul solo prezzo circa 1,0; non batte nettamente le entrate casuali short sull'R"),
]

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
    except Exception as e:  # il test e' registrato: l'errore si registra anche lui
        aggiungi({"id": None, "tipo": "nota", "oggetto": f"errore durante {codice} {direzione}", "testo": traceback.format_exc()[-1500:]})
        print("ERRORE", codice, direzione, e, flush=True)
