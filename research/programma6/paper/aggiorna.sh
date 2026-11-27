#!/bin/bash
# Programma 6, il paper delle candidate (research/programma6/paper/REGOLE.md): scarica le candele giornaliere nuove e
# l'indice del premio del mese senza funding, unisce le impronte, ricalcola F2, C1 e A1 e scrive PAPER.md e paper.json.
# Uso: bash research/programma6/paper/aggiorna.sh <cartella per le impronte temporanee>
set -e
cd "$(dirname "$0")/../../.."
TMP=${1:-/tmp/p6_impronte}
mkdir -p "$TMP"
# l'esito dello scarico si controlla (audit del 26 novembre 2026: con «|| true» uno scarico caduto a meta' passava per un
# archivio in ritardo): 0 completo, 2 finito ma incompleto (monete senza l'ultimo giorno, errori, monete saltate), altro
# caduto prima della fine; il resto dello script va avanti lo stesso
CODICE_SCARICO=0
P6_PREMIO=1 P6_FILI=16 P6_IMPRONTE="$TMP" python3 -m research.programma6.scarico_giorni > "$TMP/scarico_giorni.log" 2>&1 \
  || CODICE_SCARICO=$?
[ -f "$TMP/scarico_giorni.json" ] && cp "$TMP/scarico_giorni.json" research/programma6/scarico_giorni.json
# i giorni che mancano nell'archivio pubblico (il 28 ottobre 2026 per tutte le monete) dall'interfaccia pubblica di Binance
python3 -m research.programma6.buchi_archivio > "$TMP/buchi_archivio.log" 2>&1 || true
P6_IMPRONTE="$TMP" P6_FILI=16 python3 -W ignore -m research.programma6.paper.aggiorna
[ -f "$TMP/scarico_metrics.json" ] && cp "$TMP/scarico_metrics.json" research/programma6/scarico_metrics.json
# in fondo a PAPER.md, appena rigenerato, la riga «Scarico incompleto: N monete senza il giorno ...» (nessuna riga se lo
# scarico e' completo): il pannello toglie senza dirlo l'ultimo giorno se ha meno del 90% delle monete (seconda.py)
python3 -m research.programma6.scarico_giorni --riga "$TMP/scarico_giorni.json" "$CODICE_SCARICO" research/programma6/paper/PAPER.md \
  || printf '\nScarico incompleto: controllo dello scarico non riuscito (codice %s).\n' "$CODICE_SCARICO" >> research/programma6/paper/PAPER.md
