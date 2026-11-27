#!/usr/bin/env bash
# Un avvio di riserva delle azioni dalla VPS: chiede a GitHub di far partire i lavori del demo con il comando «auto».
#
# Rifatto il 27 novembre 2026 (audit, stock/AUDIT_2026-11-27.md): il server non tiene più una copia del codice né le chiavi del conto
# e non scrive diari né stato. Prima avrebbe scritto gli stessi file dei lavori di GitHub (conflitti a ogni salvataggio, poi una copia
# ferma su codice vecchio senza avviso) e non conosceva la prova 45. Ora l'unico che scrive è GitHub: il server avvia e basta, come le
# routine della sessione «trading stock», ma senza dipendere da lei. I doppioni sono impossibili (lavori in fila, ordini con nome
# unico) e un avvio in più esce da solo. Serve solo GITHUB_TOKEN_AZIONI nell'ambiente (dal file /etc/azioni-avanti.env, che legge
# systemd): un token di GitHub con il solo permesso di avviare i lavori di questo repository. Lo lancia systemd (installa.sh).
#   gira.sh azioni_avanti.yml [azioni_miscela.yml] [azioni_gamma.yml]
set -uo pipefail
REPO=alessiobaljak/agentic_trading_system
RAMO=claude/brave-albattani-1b12fv
[ -n "${GITHUB_TOKEN_AZIONI:-}" ] || { echo "ATTENZIONE: manca GITHUB_TOKEN_AZIONI (/etc/azioni-avanti.env)"; exit 1; }
ESITO=0
for LAVORO in "$@"; do
  case "$LAVORO" in
    azioni_avanti.yml|azioni_miscela.yml|azioni_gamma.yml) ;;
    *) echo "lavoro non ammesso: $LAVORO"; ESITO=2; continue ;;
  esac
  # il token passa da stdin, non dagli argomenti (che ogni utente della macchina vede con ps)
  CODICE=$(printf 'Authorization: Bearer %s\n' "$GITHUB_TOKEN_AZIONI" | curl -s -o /dev/null -w '%{http_code}' --max-time 30 -X POST \
    -H @- -H "Accept: application/vnd.github+json" \
    "https://api.github.com/repos/$REPO/actions/workflows/$LAVORO/dispatches" \
    -d "{\"ref\":\"$RAMO\",\"inputs\":{\"comando\":\"auto\"}}")
  if [ "$CODICE" = "204" ]; then
    echo "$LAVORO avviato"
  else
    echo "ATTENZIONE: $LAVORO non avviato (risposta di GitHub $CODICE)"
    ESITO=1
  fi
done
exit $ESITO
