"""Registra nel log (prima di eseguirle) le verifiche della Fase 4 di un candidato.

Uso: python registra_verifiche.py verifiche.jsonl
Ogni riga: {"id": ..., "verifica_di": ..., "verifica": ..., "parametri": {...}, "criterio_successo": ...,
            "previsione": ..., "conta": "<nome del file di conta in esiti/, senza .json>"}
Il numero di trade stimati si legge dal file di conta scritto da ``esegui.py conta``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import comune
import registro

if __name__ == "__main__":
    for r in Path(sys.argv[1]).read_text().splitlines():
        if not r.strip():
            continue
        d = json.loads(r)
        conta = json.loads((comune.CARTELLA_DATI / "esiti" / f"{d.pop('conta')}.json").read_text())
        voce = {"id": d["id"], "tipo": "registrazione", "tipo_test": "verifica", "verifica_di": d["verifica_di"],
                "verifica": d["verifica"], "periodo": "costruzione", "parametri": d["parametri"],
                "previsione": d["previsione"], "criterio_successo": d["criterio_successo"],
                "trade_stimati": conta["trade"]}
        print(registro.aggiungi(voce)["id"])
