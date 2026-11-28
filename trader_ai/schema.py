"""Lo schema della risposta del modello (REGOLE.md, versione 7, sezione 5): una decisione per chiamata. L'SDK lo manda come
uscita strutturata e lo valida; i limiti veri li controlla `limiti.py`.

Niente lunghezze massime nei testi (controllo del 26 novembre 2026, punto 2.5): l'API non le applica e l'SDK le controlla solo dopo,
così un diario di 601 caratteri buttava via tutta la decisione. Le lunghezze sono indicazioni nella descrizione; il programma taglia
i testi quando li salva in memoria. La leva è un numero intero: il formato lo garantisce l'API."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Azione = Literal["aspetta", "apri_lungo", "apri_corto", "chiudi", "modifica"]


# versione 9, 28 novembre 2026: quando richiamare il modello lo decide lui (sveglia.py); la descrizione qui sotto la legge il modello
class Sveglia(BaseModel):
    """Quando vuoi essere richiamato."""
    sopra: Optional[float] = Field(None, description="richiamami appena il prezzo mark arriva a questo prezzo o sopra (facoltativo)")
    sotto: Optional[float] = Field(None, description="richiamami appena il prezzo mark arriva a questo prezzo o sotto (facoltativo)")
    entro_minuti: int = Field(description="richiamami comunque dopo questi minuti, da 1 a 240")


class Risposta(BaseModel):
    azione: Azione
    margine_usdt: Optional[float] = Field(None, description="aprire: USDT del conto messi come margine")
    leva: Optional[int] = Field(None, description="aprire: leva, numero intero da 1 a 10")
    stop_prezzo: Optional[float] = Field(None, description="aprire (obbligatorio) e modifica: prezzo dello stop")
    obiettivo_prezzo: Optional[float] = Field(None, description="aprire e modifica: prezzo dell'obiettivo (facoltativo)")
    tipo_ordine: Literal["mercato", "limite"] = Field(
        "mercato", description="aprire: «mercato» (subito) o «limite» (con prezzo_limite; si esegue solo quando il prezzo degli "
                               "scambi va oltre il limite)")
    prezzo_limite: Optional[float] = Field(None, description="solo con tipo_ordine «limite»: il prezzo dell'ordine")
    approccio: str = Field(description="il tuo metodo in una frase, circa 200 caratteri, senza i livelli di prezzo di oggi "
                                       "(quelli vanno nel diario)")
    cambio_approccio: bool = Field(description="vero se hai deciso adesso di cambiare metodo")
    perche: Optional[str] = Field(None, description="se cambi approccio: perché, circa 300 caratteri")
    lezione: Optional[str] = Field(None, description="quando sei chiamato per un'operazione chiusa: che cosa avevi previsto, che "
                                                     "cosa è successo, che cosa cambi (circa 300 caratteri); resta nella tua "
                                                     "memoria anche nei giorni dopo")
    diario: str = Field(description="cosa vedi e perché decidi così, circa 600 caratteri")
    sveglia: Optional[Sveglia] = Field(None, description="quando vuoi essere richiamato: un prezzo sopra, un prezzo sotto e un "
                                                         "tempo massimo; senza, vieni richiamato a ogni candela da 15 minuti chiusa")
