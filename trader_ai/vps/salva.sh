#!/usr/bin/env bash
# Salva nel repository stato, diario e resoconti del trader AI, dalla copia dei DATI (/opt/trader-ai-dati), mai da quella del codice
# (revisioni del 23 novembre 2026, problemi 98, 103 e 119). Solo trader_ai/avanti/; mai il file delle chiavi. Il blocco del programma
# (/tmp/trader-ai-dati.lock) si tiene solo per «add» e «commit»; i comandi di rete hanno un limite di tempo e girano senza blocco.
#   salva.sh /opt/trader-ai-dati
set -uo pipefail
cd "${1:?serve la cartella dei dati}"
RAMO=claude/brave-albattani-1b12fv
exec 8>/tmp/trader-ai-salva.lock
flock -n 8 || { echo "un altro salvataggio è in corso"; exit 0; }
(
  flock -w 120 9 || { echo "il programma tiene il blocco da più di 2 minuti: salvo al giro dopo"; exit 3; }
  git add trader_ai/avanti 2>/dev/null || true
  git diff --cached --quiet && exit 4
  git -c user.name="trader-ai-vps" -c user.email="noreply@anthropic.com" commit -q -m "trader_ai: stato e diario del $(date -u +%F\ %H:%M) (macchina) [skip ci]"
) 9>/tmp/trader-ai-dati.lock
case $? in 0) ;; 4) echo "niente da salvare"; exit 0 ;; *) exit 0 ;; esac
for i in 1 2 3 4; do
  # il rebase tocca solo i commit dei dati; il programma intanto scrive in file che git non ha in sospeso (già nel commit)
  timeout 60 git fetch -q origin "$RAMO" && git rebase -q --autostash FETCH_HEAD && timeout 60 git push -q origin "HEAD:$RAMO" && exit 0
  git rebase --abort 2>/dev/null
  sleep $((i * 5))
done
echo "salvataggio non riuscito"; exit 1
