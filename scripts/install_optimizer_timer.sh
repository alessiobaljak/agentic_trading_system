#!/usr/bin/env bash
# ============================================================================
# Installa/aggiorna le unit systemd della validazione GATE 1 sul VPS, senza dover
# incollare heredoc a mano (paste-safe). Esegui come root DAL repo:
#
#   sudo bash scripts/install_optimizer_timer.sh
#
# Scrive trading-optimizer.service (+ .timer): optimize + discover su dati REALI
# Binance (mai sintetici), priorita' bassa, una volta a notte. NON tocca il bot.
# ============================================================================
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
echo "[install] APP_DIR=$APP_DIR"

cat > /etc/systemd/system/trading-optimizer.service <<EOF
[Unit]
Description=Agentic Trading - GATE 1 (optimize + discover, dati reali, autonomo)
After=network-online.target

[Service]
Type=oneshot
# la validazione dura 30-90 min: senza questo un oneshot verrebbe ucciso a 90s
TimeoutStartSec=infinity
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
Environment=PYTHONUNBUFFERED=1
Environment=BACKTEST_ALLOW_SYNTHETIC=false
Environment=OPTIMIZER_MIN_PASSES=3
Environment=OPTIMIZER_MIN_HISTORY=17520
# priorita' bassa: non deve mai rubare CPU/IO al bot live
Nice=15
IOSchedulingClass=idle
ExecStart=$APP_DIR/.venv/bin/python -m scripts.optimize --top 80 --windows 3 --max-combos 12 --start 2022-01-01
ExecStart=$APP_DIR/.venv/bin/python -m scripts.discover_strategies --top 80 --generate 40 --windows 3 --start 2022-01-01
EOF

cat > /etc/systemd/system/trading-optimizer.timer <<EOF
[Unit]
Description=GATE 1 validazione ogni 8h (dati reali Binance) - accumula validazioni

[Timer]
OnCalendar=*-*-* 00,08,16:00:00
Persistent=true
RandomizedDelaySec=600

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable trading-optimizer.timer

cat <<MSG

[install] FATTO. Unit installate e timer notturno abilitato (03:00).
[install] Per lanciare la validazione ADESSO (in background, sopravvive all'SSH):
            sudo systemctl start trading-optimizer.service
[install] Per seguire i log live:
            journalctl -u trading-optimizer.service -f
MSG
