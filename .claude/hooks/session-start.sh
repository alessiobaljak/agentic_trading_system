#!/bin/bash
# SessionStart hook per Claude Code on the web.
# Installa le dipendenze Python del bot e Node della dashboard così che test,
# linter e backtest funzionino nelle sessioni remote.
set -euo pipefail

# Esegui solo nell'ambiente remoto (Claude Code on the web).
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$PROJECT_DIR"

echo "[session-start] Installazione dipendenze Python..."
python -m pip install --quiet --upgrade pip || echo "[session-start] upgrade pip saltato (non bloccante)"
python -m pip install --quiet -r requirements.txt

echo "[session-start] Installazione dipendenze Node (dashboard)..."
if [ -f dashboard/package.json ]; then
  ( cd dashboard && npm install --no-audit --no-fund ) || echo "[session-start] npm install fallito (non bloccante)"
fi

# Rende importabile il package `bot` senza installazione.
echo 'export PYTHONPATH="."' >> "${CLAUDE_ENV_FILE:-/dev/null}"

# Nota sull'accesso di rete: le API esterne (Binance, Anthropic, LunarCrush,
# Coinglass, Firebase, Telegram, NewsAPI, alternative.me, CoinMetrics) richiedono
# rete in uscita. In Claude Code on the web l'accesso è regolato dalla network
# policy dell'ambiente: assicurarsi che consenta HTTPS verso questi domini.
echo "[session-start] Completato."
