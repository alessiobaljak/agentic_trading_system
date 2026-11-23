"""Quando chiamare il modello (REGOLE.md, versione 3, sezione 2): a ogni candela da 15 minuti chiusa e subito quando
un'operazione si chiude. Il programma controlla ogni minuto senza costi."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

PASSO = timedelta(minutes=15)


def inizio_candela(ora: datetime) -> datetime:
    return ora.replace(minute=ora.minute - ora.minute % 15, second=0, microsecond=0)


def motivo(ora: datetime, ultima: Optional[datetime], operazione_chiusa: Optional[str] = None) -> Optional[str]:
    """Perché chiamare adesso, o None. `operazione_chiusa`: come si è chiusa l'operazione dall'ultimo controllo (stop,
    obiettivo, liquidazione), se si è chiusa."""
    if operazione_chiusa:
        return f"operazione chiusa ({operazione_chiusa})"
    if ultima is None:
        return "primo avvio"
    if inizio_candela(ora) > inizio_candela(ultima):
        return "candela da 15 minuti chiusa"
    return None
