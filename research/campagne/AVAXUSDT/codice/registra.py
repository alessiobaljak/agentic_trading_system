"""Registrazioni nel log (prima del test) delle varianti, dai metadati di ipotesi.md.

Uso: python registra.py <file_registrazioni.json> dove il file e' una lista di
{"chiave": "V-01", "idea": ..., "fonte": ..., "meccanismo": ..., "previsione": ..., "trade_stimati": n,
 "ritocco_di": null o id, "famiglia": id o null, "cosa_cambia": ...}.
variante_n si calcola dal log (cresce di uno per ogni registrazione di tipo variante).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from log_campagna import aggiungi, ids_esistenti  # noqa: E402
from varianti import VARIANTI  # noqa: E402

CRITERIO = ("candidato se batte nettamente la (a) e la (b) con contro_baseline (t oltre la soglia di Student) "
            "e R medio dopo i costi positivo, sui dati di costruzione")

voci = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for meta in voci:
    var = VARIANTI[meta["chiave"]]
    n = sum(1 for v in ids_esistenti() if v.get("tipo") == "registrazione" and v.get("tipo_test") == "variante")
    voce = {
        "id": var.id, "tipo": "registrazione", "tipo_test": "variante",
        "idea": meta["idea"], "famiglia": meta.get("famiglia") or var.id, "ritocco_di": meta.get("ritocco_di"),
        "fonte": meta["fonte"], "meccanismo": meta["meccanismo"], "timeframe": var.tf, "direzione": var.direzione,
        "parametri": dict(var.parametri, regola=meta["regola"]), "periodo": "costruzione",
        "previsione": meta["previsione"], "criterio_successo": meta.get("criterio_successo", CRITERIO),
        "trade_stimati": meta["trade_stimati"], "variante_n": n + 1,
    }
    if meta.get("cosa_cambia"):
        voce["cosa_cambia"] = meta["cosa_cambia"]
    print(aggiungi(voce)["data"], var.id, "variante_n", n + 1)
