#!/usr/bin/env bash
# ============================================================================
# Consolida GATE 1 in fretta: esegue la validazione (optimize + discover) N volte
# di fila, per accumulare i MIN_PASSES senza aspettare le notti. Da usare col BOT
# FERMO (cosi' c'e' tutta la CPU). Usa il service gia' configurato -> stessi env:
# dati reali Binance, niente sintetici, MIN_PASSES, priorita' bassa.
#
# Uso (sul VPS):
#   sudo nohup bash scripts/consolidate_now.sh 3 > /tmp/consolidate.log 2>&1 &
#   tail -f /tmp/consolidate.log
#
# N (default 3) = quante passate di fila. Ogni passata e' ~2h sul VPS a 2 core.
# ============================================================================
N="${1:-3}"
echo "[consolidate] avvio: $N passate consecutive di GATE 1 ($(date -u))"
for i in $(seq 1 "$N"); do
  echo "[consolidate] === passata $i/$N === inizio $(date -u)"
  # Type=oneshot: 'systemctl start' BLOCCA fino a fine run (optimize + discover)
  if systemctl start trading-optimizer.service; then
    echo "[consolidate] passata $i/$N OK $(date -u)"
  else
    echo "[consolidate] passata $i/$N FALLITA (continuo) $(date -u)"
  fi
done
echo "[consolidate] FINITO: $N passate. Controlla la copertura nel dashboard/Telegram."
