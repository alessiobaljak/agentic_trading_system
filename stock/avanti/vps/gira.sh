#!/usr/bin/env bash
# Un giro della misura in avanti delle azioni sulla VPS: aggiorna il codice, lancia il comando «auto» della strategia chiesta
# (prima_candela o miscela), salva diario e stato nel repository. Lo lancia systemd (stock/avanti/vps/installa.sh).
#   gira.sh prima_candela | miscela
set -uo pipefail
cd "$(dirname "$0")/../../.."
RAMO=claude/brave-albattani-1b12fv
case "${1:-}" in
  prima_candela) MODULO=stock.avanti.avanti ;;
  miscela) MODULO=stock.avanti.miscela; [ -f stock/avanti/miscela_accesa ] || { echo "miscela spenta"; exit 0; } ;;
  *) echo "uso: gira.sh prima_candela|miscela"; exit 2 ;;
esac
# un giro alla volta per strategia: un secondo avvio mentre il primo aspetta l'ora giusta esce subito
exec 9>"/tmp/azioni-avanti-$1.lock"
flock -n 9 || { echo "un altro giro di $1 è in corso"; exit 0; }

# le due strategie usano la stessa copia del repository: git si usa uno alla volta, e senza mai buttare i file non ancora salvati
aggiorna() {
  flock 8
  git pull -q --rebase --autostash origin "$RAMO" || { git rebase --abort 2>/dev/null; echo "aggiornamento del codice non riuscito: si usa quello che c'è"; }
  flock -u 8
}
salva() {
  flock 8
  git add stock/avanti/giorni stock/avanti/diario.csv stock/avanti/riepilogo.md stock/avanti/elenco_*.csv stock/avanti/valori.csv \
          stock/avanti/miscela_stato.json stock/avanti/miscela_diario.csv stock/avanti/conto_condiviso.json 2>/dev/null || true
  if ! git diff --cached --quiet; then
    git -c user.name="azioni-vps" -c user.email="noreply@anthropic.com" commit -q -m "stock: $1, auto del $(date -u +%F) (VPS) [skip ci]"
    for i in 1 2 3 4; do
      git pull -q --rebase --autostash origin "$RAMO" && git push -q origin "HEAD:$RAMO" && break
      git rebase --abort 2>/dev/null
      sleep $((i * 5))
    done
  fi
  flock -u 8
}
exec 8>"/tmp/azioni-avanti-git.lock"
aggiorna
.venv/bin/python -m "$MODULO" auto
ESITO=$?
salva "$1"
exit $ESITO
