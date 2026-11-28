"""Quando chiamare il modello.

Dalla versione 9 (28 novembre 2026) lo decide il modello. Il proprietario: «perché non facciamo gestire all'AI quando vuole fare la
chiamata [...] il sistema è come se fosse sempre in ascolto e analizza sempre e poi decide quando è meglio entrare», poi «ok».

In ogni risposta il modello mette una sveglia: un prezzo sopra, un prezzo sotto e un tempo massimo. Il programma guarda il prezzo mark a
ogni passo (30 secondi, senza costi) e lo chiama quando il prezzo ci arriva o quando il tempo passa. Lo chiama comunque subito quando
un'operazione si chiude, quando un suo ordine limite si esegue e a mezzanotte UTC (giorno nuovo, obiettivo nuovo). Il proprietario:
«non voglio limitare il modello nel decidere quando entrare oppure perdere opportunità»: il ritmo lo sceglie lui, da 1 a 240 minuti;
fra due chiamate della sveglia passa almeno un minuto (un controllo tecnico, non una scelta di ritmo). Lo paga con il tetto di spesa.

Senza sveglia (la prima chiamata, una risposta non letta, il tetto di spesa finito) vale la regola di prima (versione 3): una chiamata
a ogni candela da 15 minuti chiusa.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

PASSO = timedelta(minutes=15)
MINUTI_MIN, MINUTI_MAX = 1, 240
INTERVALLO_MIN = timedelta(minutes=MINUTI_MIN)


def inizio_candela(ora: datetime) -> datetime:
    return ora.replace(minute=ora.minute - ora.minute % 15, second=0, microsecond=0)


def _p(x: float) -> str:
    return f"{x:.1f}".rstrip("0").rstrip(".")


def nuova(ora: datetime, prezzo: float, richiesta) -> Tuple[Optional[dict], List[str]]:
    """La sveglia da salvare nello stato, dalla risposta del modello (`schema.Sveglia`, o None), e le note per il modello. Un prezzo
    già superato non si mette (scatterebbe subito); il tempo si porta fra 1 e 240 minuti."""
    if richiesta is None:
        return None, []
    note: List[str] = []
    minuti = max(MINUTI_MIN, min(MINUTI_MAX, int(richiesta.entro_minuti)))
    if minuti != richiesta.entro_minuti:
        note.append(f"entro_minuti {richiesta.entro_minuti} portato a {minuti} (va da {MINUTI_MIN} a {MINUTI_MAX})")
    sopra, sotto = richiesta.sopra, richiesta.sotto
    if sopra is not None and sopra <= prezzo:
        note.append(f"«sopra» {_p(sopra)} non messa: il prezzo era già {_p(prezzo)}")
        sopra = None
    if sotto is not None and sotto >= prezzo:
        note.append(f"«sotto» {_p(sotto)} non messa: il prezzo era già {_p(prezzo)}")
        sotto = None
    return {"sopra": sopra, "sotto": sotto, "minuti": minuti, "messa": ora.isoformat(),
            "entro": (ora + timedelta(minutes=minuti)).isoformat()}, note


def motivo(ora: datetime, ultima: Optional[datetime], operazione_chiusa: Optional[str] = None, sveglia: Optional[dict] = None,
           prezzo: Optional[float] = None) -> Optional[str]:
    """Perché chiamare adesso, o None. `operazione_chiusa`: come si è chiusa l'operazione dall'ultimo controllo, se si è chiusa;
    `sveglia`: quella messa dal modello alla chiamata prima (None: la regola delle candele da 15 minuti); `prezzo`: il mark di adesso."""
    if operazione_chiusa:
        return f"operazione chiusa ({operazione_chiusa})"
    if ultima is None:
        return "primo avvio"
    if sveglia is None:
        if inizio_candela(ora) > inizio_candela(ultima):
            return "candela da 15 minuti chiusa"
        return None
    if ora - ultima < INTERVALLO_MIN:
        return None
    if prezzo is not None:
        if sveglia.get("sopra") is not None and prezzo >= sveglia["sopra"]:
            return f"la tua sveglia: il prezzo è salito a {_p(prezzo)} (avevi chiesto sopra {_p(sveglia['sopra'])})"
        if sveglia.get("sotto") is not None and prezzo <= sveglia["sotto"]:
            return f"la tua sveglia: il prezzo è sceso a {_p(prezzo)} (avevi chiesto sotto {_p(sveglia['sotto'])})"
    if ora >= datetime.fromisoformat(sveglia["entro"]):
        return f"la tua sveglia: sono passati i {sveglia['minuti']} minuti che avevi chiesto"
    return None
