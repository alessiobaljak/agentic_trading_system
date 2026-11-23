#!/usr/bin/env bash
# Salva nel repository stato, diario e resoconti del trader AI, dalla copia dei DATI (/opt/trader-ai-dati), mai da quella del codice
# (revisione del 23 novembre 2026, problemi 98 e 103). Solo trader_ai/avanti/; mai il file delle chiavi. Prende lo stesso blocco del
# programma (/tmp/trader-ai-dati.lock): git non lavora mentre il programma scrive. Lo lancia ogni ora il timer trader-ai-salva.
#   salva.sh /opt/trader-ai-dati
set -uo pipefail
cd "${1:?serve la cartella dei dati}"
RAMO=claude/brave-albattani-1b12fv
exec 9>/tmp/trader-ai-dati.lock
flock -w 120 9 || { echo "il programma tiene il blocco da più di 2 minuti: salvo al giro dopo"; exit 0; }
git add trader_ai/avanti 2>/dev/null || true
if git diff --cached --quiet; then echo "niente da salvare"; exit 0; fi
git -c user.name="trader-ai-vps" -c user.email="noreply@anthropic.com" commit -q -m "trader_ai: stato e diario del $(date -u +%F\ %H:%M) (macchina) [skip ci]"
for i in 1 2 3 4; do
  git pull -q --rebase --autostash origin "$RAMO" && git push -q origin "HEAD:$RAMO" && exit 0
  git rebase --abort 2>/dev/null
  sleep $((i * 5))
done
echo "salvataggio non riuscito"; exit 1
