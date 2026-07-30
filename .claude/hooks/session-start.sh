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

# Il container remoto viene ricreato dallo SNAPSHOT dell'ambiente (un commit
# vecchio, es. d6108e5): a ogni nuova sessione il working tree riparte da li'.
# Qui ci riallineiamo SUBITO al branch remoto (fonte di verita'), ma SOLO se il
# working tree e' pulito: mai buttare via lavoro non committato.
echo "[session-start] Risincronizzazione col branch remoto..."
BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo '')"
if [ -n "$BRANCH" ] && [ "$BRANCH" != "HEAD" ] && [ -z "$(git status --porcelain 2>/dev/null)" ]; then
  if git fetch origin "$BRANCH" 2>/dev/null; then
    LOCAL="$(git rev-parse HEAD)"
    REMOTE="$(git rev-parse "origin/$BRANCH" 2>/dev/null || echo "$LOCAL")"
    if [ "$LOCAL" != "$REMOTE" ]; then
      git reset --hard "origin/$BRANCH" \
        && echo "[session-start] allineato a origin/$BRANCH ($(git rev-parse --short HEAD))" \
        || echo "[session-start] reset fallito (non bloccante)"
    else
      echo "[session-start] gia' allineato ($(git rev-parse --short HEAD))"
    fi
  else
    echo "[session-start] fetch fallito (non bloccante)"
  fi
else
  echo "[session-start] working tree non pulito o branch detached: salto il resync"
fi

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
