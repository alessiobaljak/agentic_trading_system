#!/usr/bin/env bash
# ============================================================================
# Ricostruisce GATE 1 da ZERO con il requisito di storia attuale: azzera il
# registro (purga le coin "thin-history" gia' validate) e ri-valida SOLO coin con
# storia vera (>= OPTIMIZER_MIN_HISTORY candele), poi consolida fino a N passate.
# Da usare col BOT FERMO (full CPU). Le credenziali Firebase arrivano da .env
# (caricato da load_dotenv nel processo Python).
#
# Uso (sul VPS):
#   nohup bash scripts/rebuild_clean.sh 3 > /tmp/rebuild.log 2>&1 &
#   tail -f /tmp/rebuild.log
#
# N (default 3) = passate totali (la prima azzera). Ogni passata ~2h a 2 core.
# ============================================================================
set -uo pipefail
N="${1:-3}"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"
PY="$APP_DIR/.venv/bin/python"
export BACKTEST_ALLOW_SYNTHETIC=false
export OPTIMIZER_MIN_PASSES=3
export OPTIMIZER_MIN_HISTORY="${OPTIMIZER_MIN_HISTORY:-17520}"   # ~2 anni di candele 1h

# evita run concorrenti: ferma il timer (e un eventuale run in corso) durante la
# ricostruzione, e RIATTIVA il timer all'uscita (anche se lo script fallisce).
systemctl stop trading-optimizer.timer trading-optimizer.service 2>/dev/null || true
trap 'systemctl start trading-optimizer.timer 2>/dev/null || true; echo "[rebuild] timer riattivato"' EXIT

echo "[rebuild] min_history=$OPTIMIZER_MIN_HISTORY · $N passate · inizio $(date -u)"
for i in $(seq 1 "$N"); do
  RESET=""
  [ "$i" -eq 1 ] && RESET="--reset-registry"   # SOLO la prima passata azzera il registro
  echo "[rebuild] === passata $i/$N · optimize $RESET === $(date -u)"
  "$PY" -m scripts.optimize --top 80 --windows 3 --max-combos 12 --start 2022-01-01 $RESET \
    || echo "[rebuild] optimize passata $i FALLITA (continuo)"
  echo "[rebuild] === passata $i/$N · discover === $(date -u)"
  "$PY" -m scripts.discover_strategies --top 80 --generate 40 --windows 3 --start 2022-01-01 \
    || echo "[rebuild] discover passata $i FALLITA (continuo)"
done
echo "[rebuild] FINITO: registro pulito su coin con >= $OPTIMIZER_MIN_HISTORY candele, $N passate. $(date -u)"
