#!/usr/bin/env bash
# ============================================================================
# ACCUMULA I PASS SUBITO, SENZA ASPETTARE LE SETTIMANE — rigiocando la storia.
#
# IL PROBLEMA. Il pass onesto conta una conferma solo se dall'ultima sono entrate
# OPTIMIZER_NEW_DATA_MIN_HOURS di dati NUOVI (168h = 7 giorni). Con MIN_PASSES=3
# significa aspettare ~3 settimane di calendario prima che una coppia torni
# operabile. Lanciare piu' passate oggi non aiuta: hanno tutte lo stesso
# `data_end`, quindi valgono UN pass solo.
#
# L'IDEA. Non serve aspettare che il tempo passi: basta far finire i dati in
# momenti diversi. Una passata con --end di due settimane fa vede un'altra
# finestra OOS e soprattutto un ALTRO HOLDOUT (gli ultimi 45 giorni si spostano
# con la data di fine). Tre passate a --end distanziati di 8 giorni producono
# esattamente le tre conferme che avremmo raccolto aspettando tre settimane, con
# lo stesso contenuto informativo: ogni conferma vede dati che la precedente non
# aveva, ed e' su quello che la regola del pass onesto insiste.
#
# COSA NON E'. Non e' un modo di aggirare il criterio. Se una coppia passa solo
# con i dati fino a oggi e non con quelli fino a due settimane fa, NON accumula i
# tre pass: e' proprio il caso che la regola vuole scartare, e qui viene scartato
# subito invece che fra tre settimane.
#
# Uso (sul VPS, dentro tmux — dura ore):
#   tmux new -s backfill
#   bash scripts/backfill_passes.sh --yes           # 3 passate a 8 giorni
#   bash scripts/backfill_passes.sh --yes 4 10      # 4 passate a 10 giorni
# ============================================================================
set -uo pipefail

YES=0
NUMS=()
for a in "$@"; do
  case "$a" in
    --yes) YES=1 ;;
    ''|*[!0-9]*) : ;;
    *) NUMS+=("$a") ;;
  esac
done
N="${NUMS[0]:-3}"          # quante passate (= pass da accumulare)
STEP="${NUMS[1]:-8}"       # giorni fra una passata e l'altra

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"
PY="$APP_DIR/.venv/bin/python"
[ -x "$PY" ] || PY="python3"

# il passo DEVE superare la soglia del pass onesto, altrimenti le passate
# contano una volta sola e lo script gira per ore senza effetto.
MIN_H="$(grep -E '^OPTIMIZER_NEW_DATA_MIN_HOURS=' .env 2>/dev/null | tail -1 | cut -d= -f2)"
MIN_H="${MIN_H:-168}"
MIN_D=$(( (${MIN_H%.*} + 23) / 24 ))
if [ "$STEP" -le "$MIN_D" ]; then
  echo "ERRORE: passo di $STEP giorni <= soglia del pass onesto ($MIN_D giorni)."
  echo "        Le passate conterebbero come UN solo pass. Usa almeno $((MIN_D + 1))."
  exit 1
fi

if [ "$YES" -ne 1 ]; then
  echo "Accumula $N pass rigiocando la storia a passi di $STEP giorni."
  echo "  - NON azzera il registro (usa scripts/rebuild_gate.sh per quello)"
  echo "  - ogni passata e' una validazione vera su una finestra diversa"
  echo "  - dura ore: lancialo dentro tmux"
  echo
  echo "Per eseguire:  bash scripts/backfill_passes.sh --yes $N $STEP"
  exit 1
fi

export BACKTEST_ALLOW_SYNTHETIC=false     # MAI validare su dati finti

systemctl stop trading-optimizer.timer trading-optimizer.service 2>/dev/null || true
trap 'systemctl start trading-optimizer.timer 2>/dev/null || true; echo "[backfill] timer riattivato"' EXIT

OPT_ARGS="--top 200 --windows 3 --max-combos 12 --start 2022-01-01"
DISC_ARGS="--top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01"

echo "[backfill] $N passate · passo $STEP giorni · soglia pass onesto ${MIN_H}h"
# ORDINE CRESCENTE obbligatorio: il pass conta se data_end AUMENTA rispetto
# all'ultimo. Partendo da oggi e andando indietro, nessuna passata conterebbe.
for i in $(seq $((N - 1)) -1 0); do
  END="$(date -u -d "-$((i * STEP)) days" +%F)"
  STEPNO=$((N - i))
  echo "[backfill] === passata $STEPNO/$N · dati fino al $END === $(date -u)"
  "$PY" -m scripts.optimize $OPT_ARGS --end "$END" \
    || echo "[backfill] optimize passata $STEPNO FALLITA (continuo)"
  "$PY" -m scripts.discover_strategies $DISC_ARGS --end "$END" \
    || echo "[backfill] discover passata $STEPNO FALLITA (continuo)"
done

systemctl restart trading-bot.service 2>/dev/null \
  || echo "[backfill] riavvia il bot a mano: sudo systemctl restart trading-bot.service"

echo "[backfill] FATTO $(date -u). Controlla quante coppie hanno accumulato i pass:"
echo "  .venv/bin/python -m scripts.state_snapshot | head -20"
