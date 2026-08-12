"""KILL SWITCH A TRE LIVELLI — fermarsi non e' un'operazione sola.

Un interruttore binario costringe a scegliere fra "non fare niente" e "liquida
tutto adesso". Ma le tre situazioni in cui si vuole fermare un bot sono diverse e
chiedono risposte diverse:

  * PAUSE — "non aprire altro, ma le posizioni che ci sono lasciale lavorare".
    Il caso piu' frequente: un dubbio, una manutenzione, una notizia. Chiudere a
    mercato qui sarebbe un danno gratuito, perche' gli SL/TP sono gia' piazzati e
    stanno gia' proteggendo.
  * STOP AND PROTECT — "voglio uscire, ma non regalando lo spread". Gli stop si
    stringono a una frazione di ATR: le posizioni escono da sole al primo
    movimento avverso, quelle che stanno correndo continuano a correre.
  * EMERGENCY — "fuori, ora, a qualunque prezzo". L'unico caso in cui il costo
    dell'uscita immediata e' preferibile al rischio di restare.

STATO SU FIREBASE, NON COMANDO DIRETTO. La dashboard scrive un campo; il bot lo
legge a ogni tick con priorita' assoluta. Cosi' il kill switch funziona anche se
la VPS e' lenta o mezza bloccata: non c'e' nessun canale da tenere aperto, e se
il bot gira legge lo stato, punto.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional


class BotState(str, Enum):
    NORMAL = "normal"
    PAUSED = "paused"          # niente nuove posizioni, le aperte proseguono
    STOPPING = "stopping"      # stop stretti: uscita graduale
    EMERGENCY = "emergency"    # chiusura immediata a mercato


# ordine di gravita': serve per non "declassare" per errore uno stato piu' grave
_SEVERITY = {BotState.NORMAL: 0, BotState.PAUSED: 1,
             BotState.STOPPING: 2, BotState.EMERGENCY: 3}


def resolve(state_raw: Optional[str], legacy_kill: Optional[bool]) -> BotState:
    """Stato effettivo da `/commands/bot_state` e dal vecchio `/commands/kill_switch`.

    Il flag booleano storico continua a valere EMERGENCY: e' quello che scrivono
    la dashboard attuale e `scripts/reset_paper`, e cambiargli significato di
    nascosto trasformerebbe un "ferma tutto" in un "sospendi" senza che nessuno lo
    sappia. Fra i due vince il piu' GRAVE: un livello di protezione non deve mai
    essere abbassato da un valore rimasto indietro.

    Un valore non riconosciuto vale NORMAL: uno stato illeggibile non deve poter
    bloccare il bot per sempre, ma nemmeno spegnere una protezione richiesta —
    per questo il legacy viene comunque considerato.
    """
    try:
        state = BotState(str(state_raw)) if state_raw else BotState.NORMAL
    except ValueError:
        state = BotState.NORMAL
    if legacy_kill:
        state = max(state, BotState.EMERGENCY, key=lambda s: _SEVERITY[s])
    return state


def blocks_new_positions(state: BotState) -> bool:
    """True se in questo stato non si apre piu' nulla. Vale da PAUSE in su."""
    return _SEVERITY[state] >= _SEVERITY[BotState.PAUSED]


def protect_stop(mark: float, current_stop: float, atr: float, long: bool,
                 atr_mult: float = 0.3) -> float:
    """Stop stretto per l'uscita graduale (livello STOP AND PROTECT).

    Lo stop si porta a `atr_mult` ATR dal prezzo corrente, ma solo se cosi' si
    AVVICINA: allontanarlo allargherebbe la perdita possibile proprio mentre si
    sta cercando di uscire, che e' l'opposto dell'intento. Con ATR mancante o
    assurdo si lascia lo stop invariato — meglio l'uscita lenta di uno stop
    calcolato su un dato sporco.
    """
    if not atr or atr <= 0 or mark <= 0:
        return current_stop
    tight = mark - atr_mult * atr if long else mark + atr_mult * atr
    if long:
        return max(current_stop, tight)
    return min(current_stop, tight)
