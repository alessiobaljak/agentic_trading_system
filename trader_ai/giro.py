"""Un giro di decisione (REGOLE.md, versione 3): obiettivo del giorno, tetto di spesa, chiamata, controllo, diario.

Qui non si mandano ordini: il giro ritorna la decisione accettata (o «obiettivo»: chiudere tutto e fermarsi fino a mezzanotte);
gli ordini sul conto demo suo li manda `conto_demo.py`, rivisto da live-path-reviewer prima del primo avvio.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from trader_ai.costi import Budget, costo_dollari
from trader_ai.limiti import Conto, controlla, obiettivo_raggiunto
from trader_ai.modello import Esito
from trader_ai.schema import Risposta


@dataclass
class Risultato:
    stato: str                       # «ok», «obiettivo», «tetto», o lo stato dell'esito del modello
    esito: Optional[Esito] = None
    accettata: Optional[Risposta] = None
    scarto: Optional[str] = None
    costo: float = 0.0


def decidi(ora: datetime, motivo: str, budget: Budget, conto: Conto, prezzo: float, chiama_modello: Callable[[], Esito],
           costo_massimo: float, diario: Optional[Path] = None, extra: Optional[dict] = None) -> Risultato:
    """`costo_massimo`: il costo più alto possibile della chiamata (`costi.costo_massimo` sul messaggio già costruito); `extra`:
    campi in più per la riga del diario (per esempio l'impronta del messaggio)."""
    if obiettivo_raggiunto(conto):
        ris = Risultato("obiettivo")                     # chiudere tutto, niente chiamate fino a mezzanotte UTC
    elif not budget.puo_chiamare(ora, costo_massimo):
        ris = Risultato("tetto")
    else:
        budget.registra(ora, costo_massimo)            # prima della chiamata: il costo più alto possibile
        esito = chiama_modello()
        # dopo: si corregge con il costo vero solo se la risposta dichiara i token; senza (risposta non valida, tagliata, errore,
        # tempo scaduto) resta contato il massimo, perché la chiamata può essere stata pagata comunque
        costo = costo_dollari(esito.usage) if esito.usage else costo_massimo
        if esito.usage:
            budget.registra(ora, costo - costo_massimo)
        ris = Risultato(esito.stato, esito, costo=costo)
        if esito.risposta is not None:
            ris.scarto = controlla(esito.risposta, conto, prezzo)
            if ris.scarto is None:
                ris.accettata = esito.risposta
    if diario is not None:
        scrivi_diario(diario, ora, motivo, budget, conto, prezzo, ris, extra)
    return ris


#: Quanto del riassunto del ragionamento entra nel diario (che va nel repository ogni ora); il testo intero resta sulla macchina,
#: nel file dei messaggi del giorno (controllo del 26 novembre 2026, punto 2.7).
PENSIERO_NEL_DIARIO = 1500


def scrivi_diario(percorso: Path, ora: datetime, motivo: str, budget: Budget, conto: Conto, prezzo: float,
                  ris: Risultato, extra: Optional[dict] = None) -> None:
    riga = {"ora": ora.isoformat(), "motivo": motivo, "stato": ris.stato, "prezzo": prezzo, "conto": round(conto.conto, 2),
            "guadagno_giorno": round(conto.conto - conto.conto_mezzanotte, 2), "costo": round(ris.costo, 4),
            "speso_oggi": round(budget.speso(ora), 4), **(extra or {})}
    if ris.esito is not None:
        riga["usage"] = ris.esito.usage
        riga["dettaglio"] = ris.esito.dettaglio
        riga["durata_s"] = ris.esito.durata_s
        if ris.esito.pensiero:
            riga["pensiero"] = ris.esito.pensiero[:PENSIERO_NEL_DIARIO]
        if ris.esito.risposta is not None:
            riga["risposta"] = ris.esito.risposta.model_dump(exclude_none=True)
            riga["scarto"] = ris.scarto
    percorso.parent.mkdir(parents=True, exist_ok=True)
    with open(percorso, "a") as f:
        f.write(json.dumps(riga, ensure_ascii=False) + "\n")
