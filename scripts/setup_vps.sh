#!/usr/bin/env bash
# ============================================================================
# Bootstrap della VPS Hetzner (Ubuntu 24.04). Da eseguire come root DENTRO il
# repository già clonato:
#
#   apt update && apt install -y git
#   git clone https://github.com/alessiobaljak/agentic_trading_system.git
#   cd agentic_trading_system && git checkout claude/brave-albattani-1b12fv
#   bash scripts/setup_vps.sh
#
# Installa pacchetti, virtualenv, dipendenze e il servizio systemd. NON avvia il
# bot e NON tocca le chiavi: compili tu il .env e poi lo avvii.
# ============================================================================
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"
echo "[setup] directory applicazione: $APP_DIR"

echo "[setup] pacchetti di sistema..."
apt-get update -y
apt-get install -y python3 python3-venv python3-pip git ufw

echo "[setup] firewall (solo SSH)..."
ufw allow OpenSSH || true
yes | ufw enable || true

echo "[setup] virtualenv + dipendenze Python (può richiedere qualche minuto)..."
python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

echo "[setup] file .env..."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  -> creato .env da .env.example (DA COMPILARE con le tue chiavi)"
else
  echo "  -> .env già presente, lasciato invariato"
fi

echo "[setup] servizio systemd..."
cat > /etc/systemd/system/trading-bot.service <<EOF
[Unit]
Description=Agentic Trading Bot
After=network-online.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
Environment=PYTHONUNBUFFERED=1
ExecStart=$APP_DIR/.venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "[setup] timer notturno GATE 1 (optimize + discover su dati reali Binance)..."
# IMPORTANTE: la validazione gira sul VPS (non su GitHub) perche' qui Binance e'
# raggiungibile -> dati reali a 4 anni. Mai dati sintetici (BACKTEST_ALLOW_SYNTHETIC
# =false): senza dato reale la coin viene saltata, non validata su rumore.
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
Environment=OPTIMIZER_MIN_PASSES=1
# priorita' bassa: non deve mai rubare CPU/IO al bot live
Nice=15
IOSchedulingClass=idle
ExecStart=$APP_DIR/.venv/bin/python -m scripts.optimize --top 80 --windows 3 --max-combos 12 --start 2022-01-01
ExecStart=$APP_DIR/.venv/bin/python -m scripts.discover_strategies --top 80 --generate 40 --windows 3 --start 2022-01-01
EOF
cat > /etc/systemd/system/trading-optimizer.timer <<EOF
[Unit]
Description=GATE 1 validazione notturna (dati reali Binance) - accumula validazioni

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true
RandomizedDelaySec=600

[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload

cat <<EOF

============================================================
Setup completato. Prossimi passi (li fai tu):
  1) nano .env
     # inserisci le chiavi. Tieni DRY_RUN=true e BINANCE_TESTNET=true
  2) .venv/bin/python -m scripts.verify_keys
     # verifica che le chiavi rispondano (Binance qui dara' OK)
  3) systemctl enable --now trading-bot
     # avvia il bot in paper trading 24/7
  4) journalctl -u trading-bot -f
     # guarda i log live
  5) systemctl enable --now trading-optimizer.timer
     # attiva la ri-ottimizzazione autonoma ogni notte alle 03:00
============================================================
EOF
