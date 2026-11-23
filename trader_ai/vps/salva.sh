#!/usr/bin/env bash
# Salva nel repository stato, diario e resoconti del trader AI (solo trader_ai/avanti/; mai il file delle chiavi).
# Lo lancia ogni ora il timer trader-ai-salva (trader_ai/vps/installa.sh).
set -uo pipefail
cd "$(dirname "$0")/../.."
RAMO=claude/brave-albattani-1b12fv
exec 9>/tmp/trader-ai-git.lock
flock -n 9 || { echo "salvataggio già in corso"; exit 0; }
git add trader_ai/avanti 2>/dev/null || true
if git diff --cached --quiet; then echo "niente da salvare"; exit 0; fi
git -c user.name="trader-ai-vps" -c user.email="noreply@anthropic.com" commit -q -m "trader_ai: stato e diario del $(date -u +%F\ %H:%M) (macchina) [skip ci]"
for i in 1 2 3 4; do
  git pull -q --rebase --autostash origin "$RAMO" && git push -q origin "HEAD:$RAMO" && exit 0
  git rebase --abort 2>/dev/null
  sleep $((i * 5))
done
echo "salvataggio non riuscito"; exit 1
