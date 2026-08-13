#!/usr/bin/env bash
# ============================================================================
# ⚠️  SUPERATO — NON USARE PER ACCUMULARE I PASS. Usa scripts/fast_gate.sh.
#
# Questo script eseguiva N passate optimize+discover back-to-back nella
# convinzione che ognuna incrementasse il pass_count. Da quando esiste il PASS
# ONESTO (OPTIMIZER_NEW_DATA_MIN_HOURS, 168h) non e' piu' vero: passate
# ravvicinate hanno lo stesso `data_end`, quindi valgono UN SOLO pass. Lanciarne
# tre significa spendere nove ore di CPU per l'effetto di una.
#
# Cosa usare al suo posto:
#   * scripts/fast_gate.sh       — tre finestre a date di fine diverse, con
#                                  imbuto sui sopravvissuti (poche ore)
#   * scripts/backfill_passes.sh — stesso principio, senza imbuto (piu' lento)
#
# Resta utile per una cosa sola: POPOLARE il registro e le spec (piu' candidate
# valutate), non per validarle.
#
# NON abbassa la qualita' e NON riduce nulla: usa gli STESSI identici parametri
# del timer (install_optimizer_timer.sh) — stesso universo (--top 200), stesse
# strategie, stesso gate/costi/walk-forward. Niente --reset-registry: ACCUMULA.
#
# Uso sul VPS (dentro tmux, cosi' sopravvive alla disconnessione SSH):
#   tmux new -s val
#   bash scripts/accelerate_validation.sh        # 3 passate (default = MIN_PASSES)
#   bash scripts/accelerate_validation.sh 2       # 2 passate
#   # stacca con Ctrl-b d ; segui i risultati su dashboard (GATE 1) + Telegram
#
# Numero di worker: preso da .env (BACKTEST_WORKERS). Se aumenti la RAM e togli
# quel vincolo, lo script usa piu' worker in automatico -> passate piu' veloci.
# ============================================================================
set -uo pipefail
N="${1:-3}"
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"
PY="$APP_DIR/.venv/bin/python"
export BACKTEST_ALLOW_SYNTHETIC=false      # MAI validare su dati finti

# STESSI parametri del timer -> validazione IDENTICA (nessuna riduzione).
OPT_ARGS="--top 200 --windows 3 --max-combos 12 --start 2022-01-01"
# reeval-cap ALTO: ri-valuta TUTTE le generate a 1-2 passaggi (non solo 80), cosi'
# accumulano fino a 3 e la copertura puo' salire oltre ~80 coppie (verso il 60%).
DISC_ARGS="--top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01"

# niente run concorrenti: ferma il timer durante l'accelerazione e RIATTIVALO
# all'uscita, anche se lo script fallisce o viene interrotto (Ctrl-C).
systemctl stop trading-optimizer.timer trading-optimizer.service 2>/dev/null || true
trap 'systemctl start trading-optimizer.timer 2>/dev/null || true; echo "[accel] timer riattivato"' EXIT

echo "[accel] $N passate back-to-back (stessi parametri del timer) · inizio $(date -u)"
for i in $(seq 1 "$N"); do
  echo "[accel] === passata $i/$N · optimize === $(date -u)"
  "$PY" -m scripts.optimize $OPT_ARGS \
    || echo "[accel] optimize passata $i FALLITA (continuo)"
  echo "[accel] === passata $i/$N · discover === $(date -u)"
  "$PY" -m scripts.discover_strategies $DISC_ARGS \
    || echo "[accel] discover passata $i FALLITA (continuo)"
  echo "[accel] passata $i/$N completata $(date -u)"
done
echo "[accel] FINITO: $N passate. Le coppie a >= MIN_PASSES passaggi sono ora validate."
echo "[accel] Controlla dashboard (tab GATE 1) o il registro. $(date -u)"
