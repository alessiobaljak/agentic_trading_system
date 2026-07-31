#!/usr/bin/env bash
# ============================================================================
# RICOSTRUISCE il registro GATE 1 da zero sotto il gate RIFORMATO:
#   * HOLDOUT mai riusato (ultimi GATE_HOLDOUT_DAYS esclusi dalla selezione)
#   * pass_count ONESTO (incrementa solo con dati nuovi -> >=1 giorno tra i pass)
#   * PF per-regime esportato (filtro di regime live + prior per il learning)
#   * scala di TP dinamica per coppia (al posto del parametro morto `rr`)
#   * GATE_MIN_TRADES 30 (era 20)
#
# PERCHE' da zero: i pass_count esistenti contano rivalutazioni degli stessi
# dati (non conferme indipendenti) e nessuna coppia attuale ha superato
# l'holdout: sono numeri gonfiati dal difetto che questa riforma corregge.
#
# NON tocca: paper (trade chiusi/equity), learning (pesi/memory), user_risk.
# A differenza di promote_scale_out.sh qui si azzera SOLO il registro.
#
# CONSEGUENZA da conoscere: col pass onesto servono >= MIN_PASSES giorni di
# passate perche' una coppia torni validata -> il bot resta FLAT (ready<60%)
# per ALMENO 3 giorni. E' il costo di una validazione vera. Il timer riprende
# ad accumulare pass da solo, una passata al giorno che conta.
#
# Uso (sul VPS, dentro tmux):
#   tmux new -s rebuild
#   bash scripts/rebuild_gate.sh --yes 3
# ============================================================================
set -uo pipefail

YES=0
N=3
for a in "$@"; do
  case "$a" in
    --yes) YES=1 ;;
    ''|*[!0-9]*) : ;;
    *) N="$a" ;;
  esac
done

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"
PY="$APP_DIR/.venv/bin/python"
[ -x "$PY" ] || PY="python3"

if [ "$YES" -ne 1 ]; then
  echo "ATTENZIONE: azzera il REGISTRO GATE 1 e lo ricostruisce col gate riformato."
  echo "  - paper e learning NON vengono toccati"
  echo "  - il bot restera' FLAT finche' la copertura non torna >= 60%"
  echo "  - col pass onesto servono >= 3 GIORNI di passate (1 pass utile/giorno)"
  echo
  echo "Per eseguire:  bash scripts/rebuild_gate.sh --yes ${N}"
  exit 1
fi

export BACKTEST_ALLOW_SYNTHETIC=false     # MAI validare su dati finti

# niente run concorrenti: ferma il timer e riattivalo comunque all'uscita
systemctl stop trading-optimizer.timer trading-optimizer.service 2>/dev/null || true
trap 'systemctl start trading-optimizer.timer 2>/dev/null || true; echo "[rebuild] timer riattivato"' EXIT

OPT_ARGS="--top 200 --windows 3 --max-combos 12 --start 2022-01-01"
DISC_ARGS="--top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01"
echo "[rebuild] GATE 1 riformato · $N passate back-to-back · inizio $(date -u)"
echo "[rebuild] NB: le passate nello stesso giorno accumulano AL MASSIMO 1 pass"
echo "[rebuild]     (pass onesto): le successive arrivano dal timer nei giorni dopo."
for i in $(seq 1 "$N"); do
  RESET=""
  [ "$i" -eq 1 ] && RESET="--reset-registry"     # SOLO la prima passata azzera
  echo "[rebuild] === passata $i/$N · optimize $RESET === $(date -u)"
  "$PY" -m scripts.optimize $OPT_ARGS $RESET \
    || echo "[rebuild] optimize passata $i FALLITA (continuo)"
  echo "[rebuild] === passata $i/$N · discover === $(date -u)"
  "$PY" -m scripts.discover_strategies $DISC_ARGS \
    || echo "[rebuild] discover passata $i FALLITA (continuo)"
done

# il bot rilegge il registro ogni ora da solo; il restart accorcia solo l'attesa
systemctl restart trading-bot.service 2>/dev/null \
  || echo "[rebuild] restart bot fallito: riavvialo a mano"

echo "[rebuild] FATTO $(date -u). Il registro si ripopola col timer (1 pass utile/giorno):"
echo "[rebuild] copertura e ready su dashboard/Telegram; il bot riparte da solo al 60%."
