#!/bin/bash
# Programma 6, il paper delle candidate (research/programma6/paper/REGOLE.md): scarica le candele giornaliere nuove e
# l'indice del premio del mese senza funding, unisce le impronte, ricalcola F2, C1 e A1 e scrive PAPER.md e paper.json.
# Uso: bash research/programma6/paper/aggiorna.sh <cartella per le impronte temporanee>
set -e
cd "$(dirname "$0")/../../.."
TMP=${1:-/tmp/p6_impronte}
mkdir -p "$TMP"
P6_PREMIO=1 P6_FILI=16 P6_IMPRONTE="$TMP" python3 -m research.programma6.scarico_giorni > "$TMP/scarico_giorni.log" 2>&1 || true
[ -f "$TMP/scarico_giorni.json" ] && cp "$TMP/scarico_giorni.json" research/programma6/scarico_giorni.json
P6_IMPRONTE="$TMP" P6_FILI=16 python3 -W ignore -m research.programma6.paper.aggiorna
[ -f "$TMP/scarico_metrics.json" ] && cp "$TMP/scarico_metrics.json" research/programma6/scarico_metrics.json
