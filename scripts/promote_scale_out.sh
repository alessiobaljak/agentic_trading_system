#!/usr/bin/env bash
# ============================================================================
# PROMUOVE lo SCALE-OUT a modello di uscita STANDARD, in un comando solo:
#   1. attiva SCALE_OUT_ENABLED=true (validazione lanciata qui + bot, via .env)
#   2. AZZERA paper + learning (equity, trade, pesi, memory) -> baseline pulita
#   3. RICOSTRUISCE il registro GATE 1 da ZERO sotto il nuovo modello di uscita
#      (parita' engine<->paper): la prima passata azzera, le altre accumulano
#   4. riavvia il bot cosi' rilegge .env con lo scale-out attivo
#
# DISTRUTTIVO: richiede --yes. Le validazioni fatte col TP-unico vengono purgate;
# il bot resta FLAT finche' la copertura non risale al 60% (ready-gate) -> sicuro.
# NON tocca: strategy_registry viene RICOSTRUITO; user_risk_settings resta.
#
# Uso (sul VPS, dentro tmux cosi' sopravvive alla disconnessione SSH):
#   tmux new -s promote
#   bash scripts/promote_scale_out.sh --yes 6     # 6 passate back-to-back
#   # Ctrl-b d per staccare ; segui su dashboard (GATE 1) + Telegram
#
# Nota win-rate: usa il floor attuale (GATE_WIN_RATE_FLOOR, default 0.45 = opzione A,
# massimo profitto). Per piu' consistenza (opzione B/C) esporta prima di lanciare:
#   export GATE_WIN_RATE_FLOOR=0.55   # e mettilo anche in .env per il bot
# ============================================================================
set -uo pipefail

YES=0
N=3
for a in "$@"; do
  case "$a" in
    --yes) YES=1 ;;
    ''|*[!0-9]*) : ;;              # ignora argomenti non numerici (tranne --yes)
    *) N="$a" ;;                    # primo numero = numero di passate
  esac
done

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"
PY="$APP_DIR/.venv/bin/python"
[ -x "$PY" ] || PY="python3"        # fallback se la venv ha un path diverso

if [ "$YES" -ne 1 ]; then
  echo "ATTENZIONE: operazione DISTRUTTIVA. Fara':"
  echo "  - SCALE_OUT_ENABLED=true (bot + validazione)"
  echo "  - AZZERA paper + learning (equity, trade, pesi, memory)"
  echo "  - RICOSTRUISCE il registro GATE 1 da zero (le validazioni TP-unico vengono purgate)"
  echo "  - il bot resta FLAT finche' la copertura non risale al 60% (ready-gate)"
  echo
  echo "Per eseguire:  bash scripts/promote_scale_out.sh --yes ${N}"
  exit 1
fi

export BACKTEST_ALLOW_SYNTHETIC=false   # MAI validare su dati finti
export SCALE_OUT_ENABLED=true           # per le passate di validazione lanciate QUI

# 1) rendi persistente per bot + timer (idempotente)
if grep -q '^SCALE_OUT_ENABLED=' .env 2>/dev/null; then
  sed -i 's/^SCALE_OUT_ENABLED=.*/SCALE_OUT_ENABLED=true/' .env
  echo "[promote] .env: SCALE_OUT_ENABLED impostato a true"
else
  echo "SCALE_OUT_ENABLED=true" >> .env
  echo "[promote] .env: SCALE_OUT_ENABLED=true aggiunto"
fi

# niente run concorrenti: ferma il timer durante la ricostruzione e RIATTIVALO
# all'uscita (anche se lo script fallisce o viene interrotto)
systemctl stop trading-optimizer.timer trading-optimizer.service 2>/dev/null || true
trap 'systemctl start trading-optimizer.timer 2>/dev/null || true; echo "[promote] timer riattivato"' EXIT

# 2) azzera paper + learning (NON tocca il registro: lo ricostruiamo al passo 3)
echo "[promote] reset paper + learning…"
"$PY" -m scripts.reset_paper --yes --reset-learning || { echo "[promote] reset_paper FALLITO"; exit 1; }

# 3) ricostruisci il registro GATE 1 sotto scale-out: passata 1 azzera, poi accumula
#    (stessi identici parametri del timer/accelerate -> nessuna riduzione di qualita')
OPT_ARGS="--top 200 --windows 3 --max-combos 12 --start 2022-01-01"
DISC_ARGS="--top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01"
echo "[promote] ricostruzione GATE 1 (scale-out ON) · $N passate · inizio $(date -u)"
for i in $(seq 1 "$N"); do
  RESET=""
  [ "$i" -eq 1 ] && RESET="--reset-registry"   # SOLO la prima passata azzera il registro
  echo "[promote] === passata $i/$N · optimize $RESET === $(date -u)"
  "$PY" -m scripts.optimize $OPT_ARGS $RESET \
    || echo "[promote] optimize passata $i FALLITA (continuo)"
  echo "[promote] === passata $i/$N · discover === $(date -u)"
  "$PY" -m scripts.discover_strategies $DISC_ARGS \
    || echo "[promote] discover passata $i FALLITA (continuo)"
done

# 4) riavvia il bot: rilegge .env con lo scale-out attivo (resta flat finche' ready<60%)
systemctl restart trading-bot.service 2>/dev/null \
  || echo "[promote] restart bot fallito: riavvialo a mano (sudo systemctl restart trading-bot.service)"

echo "[promote] FATTO. Registro ricostruito sotto SCALE-OUT, bot riavviato. $(date -u)"
echo "[promote] Il bot ricomincera' a operare (col nuovo modello) appena la copertura torna >= 60%."
