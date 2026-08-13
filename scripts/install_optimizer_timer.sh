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
# storia minima in GIORNI (convertita in candele nel timeframe corrente dal codice):
# NON usare OPTIMIZER_MIN_HISTORY (in candele), non scala col timeframe.
Environment=OPTIMIZER_MIN_HISTORY_DAYS=180
# priorita' bassa: non deve mai rubare CPU/IO al bot live
Nice=15
IOSchedulingClass=idle
ExecStart=$APP_DIR/.venv/bin/python -m scripts.optimize --top 200 --windows 3 --max-combos 12 --start 2022-01-01
ExecStart=$APP_DIR/.venv/bin/python -m scripts.discover_strategies --top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01
EOF

cat > /etc/systemd/system/trading-optimizer.timer <<EOF
[Unit]
Description=GATE 1 validazione ogni 3h (dati reali Binance) - accumula validazioni

[Timer]
# OGNI 3 ORE (era 8). Il passo da 8h nasceva quando una passata durava quasi tutto
# l'intervallo su 2 core condivisi e con la cache che riscaricava l'intera storia a
# ogni finestra. Con piu' core e la cache incrementale una passata costa una frazione
# di quel tempo, e passate piu' frequenti significano piu' candidate provate al
# giorno. NB: NON accelerano la validazione — un pass conta solo con una settimana di
# dati nuovi — accelerano la SCOPERTA. E ogni estrazione in piu' entra nel budget di
# falsi positivi del supervisore, che se ne accorge e reagisce.
OnCalendar=*-*-* 00/3:00:00
Persistent=true
RandomizedDelaySec=600

[Install]
WantedBy=timers.target
EOF

# ---- SUPERVISORE: decide da solo, ogni ora ----------------------------------
cat > /etc/systemd/system/trading-supervisor.service <<EOF
[Unit]
Description=Agentic Trading - supervisore (taratura automatica dentro il budget)
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
EnvironmentFile=-$APP_DIR/tuning.env
Environment=PYTHONUNBUFFERED=1
ExecStart=$APP_DIR/.venv/bin/python -m scripts.supervisor
EOF

cat > /etc/systemd/system/trading-supervisor.timer <<EOF
[Unit]
Description=Supervisore ogni ora (guarda l'autopsia, tara, decide se rivalidare)

[Timer]
OnCalendar=hourly
Persistent=true
RandomizedDelaySec=300

[Install]
WantedBy=timers.target
EOF

systemctl daemon-reload
systemctl enable trading-optimizer.timer
systemctl enable trading-supervisor.timer

cat <<MSG

[install] FATTO. Unit installate e timer notturno abilitato (03:00).
[install] Per lanciare la validazione ADESSO (in background, sopravvive all'SSH):
            sudo systemctl start trading-optimizer.service
[install] Per seguire i log live:
            journalctl -u trading-optimizer.service -f
MSG
