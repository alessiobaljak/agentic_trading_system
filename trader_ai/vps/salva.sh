#!/usr/bin/env bash
# Salva nel repository stato, diario e resoconti del trader AI, dalla copia dei DATI (/opt/trader-ai-dati), mai da quella del codice
# (revisioni del 23 novembre 2026, problemi 98, 103, 119 e 126). Solo trader_ai/avanti/; mai il file delle chiavi.
# Fuori dal blocco del programma (/tmp/trader-ai-dati.lock) solo la rete (fetch e push, con limite di tempo); dentro il blocco add,
# commit e rebase, SENZA scorta automatica: subito dopo il commit l'albero è pulito e il programma intanto non scrive.
#   salva.sh /opt/trader-ai-dati
set -uo pipefail
cd "${1:?serve la cartella dei dati}"
RAMO=claude/brave-albattani-1b12fv
# il nome dei commit (anche quelli riscritti dal rebase): la macchina potrebbe non averne uno configurato
export GIT_AUTHOR_NAME=trader-ai-vps GIT_AUTHOR_EMAIL=noreply@anthropic.com
export GIT_COMMITTER_NAME=trader-ai-vps GIT_COMMITTER_EMAIL=noreply@anthropic.com
exec 8>/tmp/trader-ai-salva.lock
flock -n 8 || { echo "un altro salvataggio è in corso"; exit 0; }
for i in 1 2 3 4; do
  timeout 60 git fetch -q origin "$RAMO" || { sleep $((i * 5)); continue; }
  (
    flock -w 120 9 || exit 3
    git add trader_ai/avanti 2>/dev/null || true
    git diff --cached --quiet || git commit -q -m "trader_ai: stato e diario del $(date -u +%F\ %H:%M) (macchina) [skip ci]"
    git rebase -q FETCH_HEAD || { git rebase --abort; exit 5; }
  ) 9>/tmp/trader-ai-dati.lock
  case $? in
    0) ;;
    3) echo "il programma tiene il blocco da più di 2 minuti: salvo al giro dopo"; exit 0 ;;
    *) echo "riallineamento non riuscito"; sleep $((i * 5)); continue ;;
  esac
  [ "$(git rev-parse HEAD)" = "$(git rev-parse FETCH_HEAD)" ] && { echo "niente da salvare"; exit 0; }
  # le credenziali sono quelle già salvate sulla macchina per la copia del bot (helper «store»): un servizio non può rispondere a
  # una richiesta di password (25-26 novembre 2026: «could not read Username», nessun salvataggio per 22 ore)
  timeout 60 git -c credential.helper=store push -q origin "HEAD:$RAMO" && exit 0
  sleep $((i * 5))
done
echo "salvataggio non riuscito"; exit 1
