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
ExecStart=$APP_DIR/.venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "[setup] timer notturno di ottimizzazione strategie (universo top-N)..."
cat > /etc/systemd/system/trading-optimizer.service <<EOF
[Unit]
Description=Agentic Trading - Strategy Optimizer (walk-forward, autonomo)
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/.venv/bin/python -m scripts.optimize --top 40 --windows 3 --max-combos 12
EOF
cat > /etc/systemd/system/trading-optimizer.timer <<EOF
[Unit]
Description=Esegue l'ottimizzatore ogni notte alle 03:00

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

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
