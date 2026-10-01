"""LA FINESTRA DI R1 (1 ott 2026, si' del proprietario: «procedi con R1 al posto
di un giro del gate al giorno»).

R1 (il gate rigiocato nel passato, `scripts/replay_gate.py`) non sta in memoria
insieme al giro del gate (misura del 1 ott, ops 0412: 10 GB su 15 occupati col
gate in corso, 4 liberi; R1 ne chiede ~4,6 con 2 processi), e il gate non lascia
pause: ogni giro dura ~3 ore e il timer scatta ogni 3 ore (00, 03, 06 ... UTC).
Quindi, FINCHE' R1 E' ATTIVO, il giro delle 12:00 UTC (le 14:00 italiane) si
salta e al suo posto lavora R1. Il giro saltato e' uno di giorno («solo
urgenti»): quello completo di notte, che decide declassate e conferme, resta.

R1 e' «attivo» quando esiste il file `data/replay_gate/attivo`: lo crea R1 al
lancio e lo toglie quando tutte le date sono fatte. Cancellarlo a mano (o
`R1_SALTA_GIRO=0` nell'ambiente) rimette subito il gate a 8 giri al giorno.
Tutto fail-open: in caso di dubbio il gate gira.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone

#: l'ora UTC del giro che si salta (14:00 in Italia d'estate)
ORA_SALTATA_UTC = 12
#: il file che dice «R1 sta lavorando»
FILE_ATTIVO = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "data", "replay_gate", "attivo")


def r1_attivo(percorso: str | None = None) -> bool:
    """True se R1 ha ancora date da fare (il file c'e') e non e' spento."""
    if os.getenv("R1_SALTA_GIRO", "1").strip() in ("0", "false", "no"):
        return False
    try:
        return os.path.exists(percorso or FILE_ATTIVO)
    except Exception:  # noqa: BLE001
        return False


def slot_saltato(ts: float, percorso: str | None = None) -> bool:
    """True se il giro del gate che parte all'istante `ts` e' quello saltato."""
    try:
        ora = datetime.fromtimestamp(float(ts), timezone.utc).hour
    except (TypeError, ValueError, OSError):
        return False
    return ora == ORA_SALTATA_UTC and r1_attivo(percorso)


def giro_saltato_per_r1(now: float | None = None, percorso: str | None = None) -> str | None:
    """La frase da stampare se il giro che parte ADESSO va saltato; None se no."""
    now = time.time() if now is None else now
    if not slot_saltato(now, percorso):
        return None
    return (f"[gate] giro delle {ORA_SALTATA_UTC:02d}:00 UTC SALTATO: al suo posto lavora R1 "
            f"(il gate rigiocato nel passato, si' del proprietario del 1 ott). Il prossimo "
            f"giro e' fra 3 ore; il gate torna a 8 giri al giorno quando R1 finisce "
            f"(file {percorso or FILE_ATTIVO}).")
