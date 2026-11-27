#!/usr/bin/env bash
# ============================================================================
# Installa sulla VPS gli AVVII DI RISERVA delle azioni (conto demo di Alpaca, soldi finti), separati dal bot delle crypto.
#
# Rifatto il 27 novembre 2026 (audit, stock/AUDIT_2026-11-27.md): un solo scrittore. Il server NON ha il codice né le chiavi del
# conto: ai suoi orari chiede a GitHub di far partire i lavori del demo (gira.sh), come le routine della sessione «trading stock», ma
# senza dipendere da lei. Tutto il resto (ordini, diari, stato) lo fanno solo i lavori di GitHub.
#
# Serve un token di GitHub con il SOLO permesso di avviare i lavori di questo repository (token «fine-grained», repository
# alessiobaljak/agentic_trading_system, permesso «Actions: read and write»). Lo crea il proprietario; lo script lo chiede (non lo
# mostra e non lo scrive nel repository) e lo tiene in /etc/azioni-avanti.env, leggibile solo da root.
#
# Da lanciare UNA volta, da root, dentro la cartella del repository che c'è già sulla macchina:
#     bash stock/avanti/vps/installa.sh
# Per togliere tutto: bash stock/avanti/vps/installa.sh togli
# ============================================================================
set -euo pipefail
DEST=/opt/azioni-avanti
ENVF=/etc/azioni-avanti.env

togli_vecchi() {   # i timer della versione di prima (con la copia del codice), se c'erano
  systemctl disable --now azioni-candela.timer azioni-miscela.timer 2>/dev/null || true
  rm -f /etc/systemd/system/azioni-candela.{service,timer} /etc/systemd/system/azioni-miscela.{service,timer}
}

if [ "${1:-}" = "togli" ]; then
  togli_vecchi
  systemctl disable --now azioni-riserva.timer 2>/dev/null || true
  rm -f /etc/systemd/system/azioni-riserva.{service,timer}
  systemctl daemon-reload
  echo "[azioni] timer tolti. Restano $DEST e $ENVF (con il token): cancellali a mano e revoca il token su GitHub."
  exit 0
fi

QUI="$(cd "$(dirname "$0")" && pwd)"
togli_vecchi
mkdir -p "$DEST"
install -m 755 "$QUI/gira.sh" "$DEST/gira.sh"
if [ -f "$ENVF" ] && grep -q '^GITHUB_TOKEN_AZIONI=.' "$ENVF"; then
  echo "[azioni] $ENVF ha già il token: non lo tocco"
else
  echo "[azioni] Incolla il token di GitHub (solo «Actions: read and write» su questo repository; non compare mentre scrivi)."
  read -r -s -p "  GITHUB_TOKEN_AZIONI: " VALORE; echo
  [ -n "$VALORE" ] || { echo "[azioni] token vuoto: niente installato"; exit 1; }
  echo "[azioni] segnati la data di scadenza del token: quando scade gli avvii falliscono (journalctl -u azioni-riserva.service)"
  umask 077
  printf 'GITHUB_TOKEN_AZIONI=%s\n' "$VALORE" > "$ENVF"
  chmod 600 "$ENVF"
  echo "[azioni] token salvato in $ENVF (solo root)"
fi

cat > /etc/systemd/system/azioni-riserva.service <<UNIT
[Unit]
Description=Azioni: avvii di riserva dei lavori del demo su GitHub
After=network-online.target

[Service]
Type=oneshot
EnvironmentFile=$ENVF
# priorità bassa: non deve mai rubare CPU al bot delle crypto
Nice=10
ExecStart=/usr/bin/env bash $DEST/gira.sh azioni_avanti.yml azioni_miscela.yml azioni_gamma.yml
UNIT

# Gli orari di New York delle routine della sessione: la mattina (la riserva della sera della miscela fino alle 9:15, l'ingresso della
# prima candela alle 9:45, la prova 45 nei giorni a chiusura anticipata), il pomeriggio (la chiusura delle 15:55 e la prova 45 delle
# 15:30) e la sera (la miscela dopo le 19:00). Ogni lavoro guarda l'orologio da solo: un avvio a un'ora sbagliata esce e basta.
cat > /etc/systemd/system/azioni-riserva.timer <<UNIT
[Unit]
Description=Azioni: avvii di riserva, orari di New York

[Timer]
OnCalendar=Mon..Fri *-*-* 08:22:00 America/New_York
OnCalendar=Mon..Fri *-*-* 09:12:00 America/New_York
OnCalendar=Mon..Fri *-*-* 13:36:00 America/New_York
OnCalendar=Mon..Fri *-*-* 15:12:00 America/New_York
OnCalendar=Mon..Fri *-*-* 19:12:00 America/New_York
AccuracySec=5
Persistent=false

[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable --now azioni-riserva.timer
systemctl list-timers --no-pager 'azioni-*' || true
echo "[azioni] fatto. Registro: journalctl -u azioni-riserva.service --since today"
