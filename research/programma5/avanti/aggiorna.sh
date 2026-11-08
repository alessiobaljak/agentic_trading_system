#!/bin/bash
# Programma 5, prova in avanti (REGOLE.md, sezione 9): scarica i dati delle 100 monete dal 2025-06, l'inizio del periodo WA su cui
# avanti.py sceglie le candidate (candele da 1 minuto, metrics, premio; il funding mensile quando esce), unisce le impronte,
# rilancia avanti.py. I file gia' scaricati e controllati si saltano: dal secondo giro scarica solo i giorni nuovi. Fino all'8
# novembre 2026 scaricava dal 2026-10 e contava sui mesi prima gia' presenti: sul disco nuovo di quel giorno mancavano e la prova
# usciva con meno trade (M-002 600 invece di 1.916).
# Uso: bash research/programma5/avanti/aggiorna.sh <cartella per le impronte temporanee>
set -e
cd "$(dirname "$0")/../../.."
TMP=${1:-/tmp/p5_impronte_avanti}
mkdir -p "$TMP"
CENTO=$(python3 -c "import json; print(' '.join(json.load(open('research/programma5/universo_top100.json'))['scelte']))")
for t in klines metrics premium funding; do
  P5_IMPRONTE="$TMP" python3 -m research.programma5.strumenti.scarico --dal 2025-06 $t $CENTO > "$TMP/scarico_$t.log" 2>&1 || true
done
python3 -m research.programma5.strumenti.scarico unisci "$TMP"
# i giorni che mancano nell'archivio pubblico (il 28 ottobre 2026 per tutte le monete) dall'interfaccia pubblica di Binance
python3 -m research.programma5.strumenti.buchi_archivio_minuti > "$TMP/buchi_archivio_minuti.log" 2>&1 || true
PYTHONPATH=. python3 -W ignore research/programma5/avanti/avanti.py
PYTHONPATH=. python3 -W ignore research/programma5/avanti/avanti2.py
