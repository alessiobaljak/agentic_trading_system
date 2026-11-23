"""Un giro di decisione: controllo del rischio, del tetto di spesa, chiamata, controllo dei limiti, diario.

Qui non si mandano ordini: il giro ritorna le decisioni accettate (o «chiudi tutto»); gli ordini sul conto demo suo li manda il
collegamento con la macchina, rivisto da live-path-reviewer (REGOLE.md, sezione 9).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from trader_ai.costi import Budget, costo_dollari
from trader_ai.limiti import Portafoglio, controlla, stato_rischio
from trader_ai.modello import Esito
from trader_ai.schema import Decisione


@dataclass
class Risultato:
    stato: str                                  # «ok», «chiudi_tutto», «tetto», o lo stato dell'esito del modello
    esito: Optional[Esito] = None
    accettate: List[Decisione] = field(default_factory=list)
    scartate: List[Tuple[Decisione, str]] = field(default_factory=list)
    costo: float = 0.0


def decidi(ora: datetime, motivo: str, budget: Budget, port: Portafoglio, prezzi: Dict[str, float],
           volumi_24h: Dict[str, float], chiama_modello: Callable[[], Esito], costo_massimo: float,
           diario: Optional[Path] = None) -> Risultato:
    """`costo_massimo`: il costo più alto possibile della chiamata (`costi.costo_massimo` sul messaggio già costruito)."""
    rischio = stato_rischio(port)
    if rischio and port.posizioni:
        ris = Risultato("chiudi_tutto")          # perdita del giorno o massima: si chiude senza chiedere al modello
    elif rischio:
        ris = Risultato(rischio)                 # già tutto chiuso: nessuna chiamata (costerebbe senza poter aprire)
    elif not budget.puo_chiamare(ora, costo_massimo):
        ris = Risultato("tetto")
    else:
        esito = chiama_modello()
        costo = costo_dollari(esito.usage) if esito.usage else 0.0
        budget.registra(ora, costo)
        ris = Risultato(esito.stato, esito, costo=costo)
        if esito.risposta is not None:
            ris.accettate, ris.scartate = controlla(esito.risposta.decisioni, port, prezzi, volumi_24h)
    if diario is not None:
        scrivi_diario(diario, ora, motivo, budget, ris)
    return ris


def scrivi_diario(percorso: Path, ora: datetime, motivo: str, budget: Budget, ris: Risultato) -> None:
    riga = {
        "ora": ora.isoformat(), "motivo": motivo, "stato": ris.stato, "costo": round(ris.costo, 4),
        "speso_oggi": round(budget.speso(ora), 4),
        "accettate": [d.model_dump(exclude_none=True) for d in ris.accettate],
        "scartate": [{**d.model_dump(exclude_none=True), "scarto": m} for d, m in ris.scartate],
    }
    if ris.esito is not None:
        riga["usage"] = ris.esito.usage
        riga["dettaglio"] = ris.esito.dettaglio
        if ris.esito.risposta is not None:
            r = ris.esito.risposta
            riga.update(diario=r.diario, prossimo=r.prossimo_controllo_minuti, segui=r.segui,
                        allarmi=[a.model_dump(exclude_none=True) for a in r.allarmi])
    percorso.parent.mkdir(parents=True, exist_ok=True)
    with open(percorso, "a") as f:
        f.write(json.dumps(riga, ensure_ascii=False) + "\n")
