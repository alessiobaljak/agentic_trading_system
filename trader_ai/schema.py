"""Lo schema della risposta del modello (REGOLE.md, sezione 5). L'SDK lo manda come uscita strutturata e lo valida;
i limiti numerici veri li controlla `limiti.py`, non lo schema."""
from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

Azione = Literal["apri_lungo", "apri_corto", "chiudi", "riduci", "sposta_stop", "metti_obiettivo"]


class Decisione(BaseModel):
    moneta: str = Field(description="simbolo del perpetuo, per esempio BTCUSDT")
    azione: Azione
    quota_conto: Optional[float] = Field(
        None, description="aprire: margine come frazione del conto (al massimo 0.20); riduci: frazione della posizione da chiudere")
    leva: Optional[float] = Field(None, description="aprire: leva da 1 a 3")
    stop_prezzo: Optional[float] = Field(None, description="aprire e sposta_stop: prezzo dello stop")
    obiettivo_prezzo: Optional[float] = None
    tipo_ordine: Literal["mercato", "limite"] = "mercato"
    prezzo_limite: Optional[float] = None
    motivo: str = Field(max_length=300)


class Allarme(BaseModel):
    moneta: str
    sopra: Optional[float] = None
    sotto: Optional[float] = None


class Risposta(BaseModel):
    decisioni: List[Decisione]
    segui: List[str] = Field(description="monete di cui vuoi il dettaglio la prossima volta, al massimo 15")
    prossimo_controllo_minuti: int = Field(description="fra quanti minuti vuoi guardare di nuovo, da 15 a 1440")
    allarmi: List[Allarme] = Field(description="prezzi a cui vuoi essere svegliato prima, al massimo 20")
    diario: str = Field(max_length=600, description="cosa pensi del mercato e perché")
