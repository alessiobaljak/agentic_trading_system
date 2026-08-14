#!/usr/bin/env bash
# ============================================================================
# Installa l'agente OPS: legge le richieste committate nel repo, esegue SOLO cio'
# che compare in ops/allowlist, ricommitta le risposte. Vedi ops/README.md.
#
#   bash scripts/install_ops_agent.sh
# ============================================================================
set -uo pipefail
APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"

if [ ! -f ops/allowlist ]; then
  echo "ERRORE: manca ops/allowlist — senza, ogni richiesta verrebbe rifiutata."
  echo "        cp ops/allowlist.example ops/allowlist   (poi adattala: e' TUA)"
  exit 1
fi

echo "[install] lista bianca attiva ($(grep -cE '^[^#]*:' ops/allowlist) voci):"
grep -E '^[^#]*:' ops/allowlist | sed 's/^/           /'

cat > /etc/systemd/system/trading-ops.service <<UNIT
[Unit]
Description=Agentic Trading - agente OPS (comandi via git, lista bianca locale)
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
EnvironmentFile=-$APP_DIR/tuning.env
Environment=PYTHONUNBUFFERED=1
# HOME NON e' impostato di default nei servizi systemd, e senza di esso git non
# trova ne' ~/.gitconfig ne' le credenziali: pull e push falliscono in silenzio, e
# l'agente sembra semplicemente non rispondere. E' il primo posto dove guardare se
# le risposte non arrivano.
Environment=HOME=$HOME
# priorita' bassa: non deve mai rubare CPU al bot, che sorveglia le posizioni
Nice=10
ExecStart=$APP_DIR/.venv/bin/python -m scripts.ops_agent
UNIT

cat > /etc/systemd/system/trading-ops.timer <<UNIT
[Unit]
Description=Agente OPS ogni minuto

[Timer]
OnBootSec=60
OnUnitActiveSec=60
AccuracySec=15

[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable --now trading-ops.timer
systemctl list-timers --no-pager trading-ops.timer || true

cat <<MSG

[install] FATTO. L'agente controlla le richieste ogni minuto.
[install] Per vedere cosa fa:  journalctl -u trading-ops.service -f
[install] Per fermarlo:        sudo systemctl disable --now trading-ops.timer
MSG
