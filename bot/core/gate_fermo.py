"""L'INTERRUTTORE DELLA RICERCA AUTOMATICA DEL GATE (13 ott 2026, si' del
proprietario: «procedi con tutto», dopo la proposta di spegnere la ricerca
automatica ogni tre ore).

Perche': il giro del gate (`scripts/optimize.py` + `scripts/discover_strategies.py`,
timer `trading-optimizer.timer`, ogni 3 ore) fa circa 27.000 prove per giro, ne
passa lo 0,29% con un t richiesto di 3,96, e le coppie passate fanno -0,06 R a
trade in paper (ops 0601 e 0604, 12 ott 2026): produce rumore, non informazione.
Il paper resta acceso come banco di misura; il registro delle validate non si
tocca; nessun giro nuovo lo riscrive finche' l'interruttore e' giu'.

Come funziona: se esiste il file `ops/gate_fermo` nella radice del repository, i
due script escono subito (prima di caricare qualunque dato) stampando il motivo
scritto nel file. L'agente ops fa `git pull` ogni minuto, quindi un commit che
crea o toglie il file vale dal giro successivo. Per riaccendere la ricerca si
toglie il file (un commit) oppure si imposta `GATE_FERMO_IGNORA=1` nell'ambiente
del servizio. Fail-open: in caso di dubbio il gate gira, come per la finestra di R1.
"""
from __future__ import annotations

import os

#: il file che dice «la ricerca automatica del gate e' ferma»
FILE_FERMO = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "ops", "gate_fermo")


def ricerca_ferma(percorso: str | None = None) -> str | None:
    """La frase da stampare se la ricerca del gate e' ferma; None se deve girare."""
    if os.getenv("GATE_FERMO_IGNORA", "0").strip() in ("1", "true", "yes"):
        return None
    p = percorso or FILE_FERMO
    try:
        if not os.path.exists(p):
            return None
        with open(p, encoding="utf-8") as f:
            motivo = " ".join(riga.strip() for riga in f.read().splitlines() if riga.strip())
    except Exception:  # noqa: BLE001
        return None
    return (f"[gate] RICERCA AUTOMATICA FERMA: il giro non parte (file {p}). "
            f"Motivo: {motivo or 'non scritto'}. Per riaccenderla: togliere il file con un "
            f"commit, oppure GATE_FERMO_IGNORA=1 nell'ambiente del servizio.")
