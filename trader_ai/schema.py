"""Lo schema della risposta del modello (REGOLE.md, versione 3, sezione 5): una decisione per chiamata. L'SDK lo manda come
uscita strutturata e lo valida; i limiti veri li controlla `limiti.py`."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Azione = Literal["aspetta", "apri_lungo", "apri_corto", "chiudi", "modifica"]


class Risposta(BaseModel):
    azione: Azione
    margine_usdt: Optional[float] = Field(None, description="aprire: USDT del conto messi come margine")
    leva: Optional[float] = Field(None, description="aprire: leva da 1 a 10")
    stop_prezzo: Optional[float] = Field(None, description="aprire (obbligatorio) e modifica: prezzo dello stop")
    obiettivo_prezzo: Optional[float] = Field(None, description="aprire e modifica: prezzo dell'obiettivo (facoltativo)")
    tipo_ordine: Literal["mercato", "limite"] = "mercato"
    prezzo_limite: Optional[float] = None
    approccio: str = Field(max_length=200, description="il metodo che stai usando adesso, in una frase")
    cambio_approccio: bool = Field(description="vero se hai deciso adesso di cambiare metodo")
    perche: Optional[str] = Field(None, max_length=300, description="se cambi approccio: perché")
    diario: str = Field(max_length=600, description="cosa vedi e perché decidi così")
