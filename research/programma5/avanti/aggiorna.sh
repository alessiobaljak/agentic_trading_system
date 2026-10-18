#!/bin/bash
# Programma 5, prova in avanti (REGOLE.md, sezione 9): scarica i dati nuovi delle 100 monete dal 2026-10 (candele da
# 1 minuto, metrics, premio; il funding mensile quando esce), unisce le impronte, rilancia avanti.py.
# Uso: bash research/programma5/avanti/aggiorna.sh <cartella per le impronte temporanee>
set -e
cd "$(dirname "$0")/../../.."
TMP=${1:-/tmp/p5_impronte_avanti}
mkdir -p "$TMP"
CENTO=$(python3 -c "import json; print(' '.join(json.load(open('research/programma5/universo_top100.json'))['scelte']))")
for t in klines metrics premium funding; do
  P5_IMPRONTE="$TMP" python3 -m research.programma5.strumenti.scarico --dal 2026-10 $t $CENTO > "$TMP/scarico_$t.log" 2>&1 || true
done
python3 -m research.programma5.strumenti.scarico unisci "$TMP"
PYTHONPATH=. python3 -W ignore research/programma5/avanti/avanti.py
PYTHONPATH=. python3 -W ignore research/programma5/avanti/avanti2.py
