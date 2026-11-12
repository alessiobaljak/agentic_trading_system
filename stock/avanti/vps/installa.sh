#!/usr/bin/env bash
# ============================================================================
# Installa sulla VPS la misura in avanti delle AZIONI (conto demo di Alpaca, soldi finti), separata dal bot delle crypto:
# una copia sua del repository in /opt/azioni-avanti, un ambiente Python suo, le chiavi in un file suo (/etc/azioni-avanti.env,
# leggibile solo da root) e due timer di systemd con l'ora di New York. Non tocca il bot, i suoi servizi né il suo .env.
#
# Da lanciare UNA volta, da root, dentro la cartella del repository che c'è già sulla macchina:
#     bash stock/avanti/vps/installa.sh
# Chiede le sei chiavi (non le mostra e non le scrive nel repository). Per togliere tutto: bash stock/avanti/vps/installa.sh togli
# ============================================================================
set -euo pipefail
DEST=/opt/azioni-avanti
ENVF=/etc/azioni-avanti.env
RAMO=claude/brave-albattani-1b12fv

if [ "${1:-}" = "togli" ]; then
  systemctl disable --now azioni-candela.timer azioni-miscela.timer 2>/dev/null || true
  rm -f /etc/systemd/system/azioni-candela.{service,timer} /etc/systemd/system/azioni-miscela.{service,timer}
  systemctl daemon-reload
  echo "[azioni] timer tolti. Restano $DEST e $ENVF: cancellali a mano se non servono più."
  exit 0
fi

QUI="$(cd "$(dirname "$0")/../../.." && pwd)"
if [ ! -d "$DEST/.git" ]; then
  # stesso indirizzo (e stesse credenziali) della copia che c'è già; l'indirizzo non si stampa: può contenere il token
  git clone -q --branch "$RAMO" "$(git -C "$QUI" remote get-url origin)" "$DEST"
  echo "[azioni] copia del repository in $DEST"
fi
python3 -m venv "$DEST/.venv"
"$DEST/.venv/bin/pip" install -q --upgrade pip
"$DEST/.venv/bin/pip" install -q pandas numpy requests
echo "[azioni] ambiente Python pronto"

if [ ! -f "$ENVF" ]; then
  echo "[azioni] Inserisci le chiavi (non compaiono mentre scrivi). Sono le stesse dei segreti di GitHub Actions."
  umask 077
  : > "$ENVF"
  for NOME in ALPACA_API_KEY_ID ALPACA_API_SECRET_KEY AZIONI_FIREBASE_URL AZIONI_FIREBASE_API_KEY AZIONI_FIREBASE_EMAIL AZIONI_FIREBASE_PASSWORD; do
    read -r -s -p "  $NOME: " VALORE; echo
    printf '%s=%s\n' "$NOME" "$VALORE" >> "$ENVF"
  done
  chmod 600 "$ENVF"
  echo "[azioni] chiavi salvate in $ENVF (solo root)"
else
  echo "[azioni] $ENVF c'è già: non lo tocco"
fi

servizio() {   # nome, strategia
cat > "/etc/systemd/system/azioni-$1.service" <<UNIT
[Unit]
Description=Azioni, misura in avanti sul conto demo: $2 (comando auto)
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$DEST
EnvironmentFile=$ENVF
Environment=PYTHONUNBUFFERED=1
Environment=HOME=$HOME
Environment=GIT_TERMINAL_PROMPT=0
# il giro può restare acceso ad aspettare l'ora giusta (al massimo 5 ore e 20 minuti)
TimeoutStartSec=21600
# priorità bassa: non deve mai rubare CPU al bot delle crypto
Nice=10
ExecStart=/usr/bin/env bash $DEST/stock/avanti/vps/gira.sh $2
UNIT
}
servizio candela prima_candela
servizio miscela miscela

# Prima candela: acceso dalle 9:30 (aspetta le 9:45), poi dalle 15:40 (aspetta le 15:55), poi il controllo a seduta finita.
# In più ogni 10 minuti fra le 9:00 e le 16:30: se un giro è già in corso il nuovo esce subito, altrimenti «auto» fa la cosa giusta.
cat > /etc/systemd/system/azioni-candela.timer <<UNIT
[Unit]
Description=Azioni, prima candela: orari di New York

[Timer]
OnCalendar=Mon..Fri *-*-* 09..16:00/10:00 America/New_York
OnCalendar=Mon..Fri *-*-* 16:03:00 America/New_York
OnCalendar=Mon..Fri *-*-* 17:00:00 America/New_York
AccuracySec=5
Persistent=false

[Install]
WantedBy=timers.target
UNIT

# Miscela: la sera dopo le 19:00 (ordini all'apertura del giorno dopo), una riserva la mattina presto, e ogni 10 minuti fra le 9:00
# e le 14:00 per la regola della banca centrale (negli altri giorni «auto» risponde «niente» ed esce).
cat > /etc/systemd/system/azioni-miscela.timer <<UNIT
[Unit]
Description=Azioni, miscela: orari di New York

[Timer]
OnCalendar=Mon..Fri *-*-* 19:02:00 America/New_York
OnCalendar=Mon..Fri *-*-* 21:00:00 America/New_York
OnCalendar=Mon..Fri *-*-* 07:00:00 America/New_York
OnCalendar=Mon..Fri *-*-* 09..13:00/10:00 America/New_York
AccuracySec=5
Persistent=false

[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable --now azioni-candela.timer azioni-miscela.timer
echo "[azioni] prova del collegamento al conto demo:"
( set -a; . "$ENVF"; set +a; cd "$DEST" && .venv/bin/python -m stock.avanti.avanti controlla ) || echo "[azioni] ATTENZIONE: il collegamento non va, controlla le chiavi in $ENVF"
systemctl list-timers --no-pager 'azioni-*' || true
echo "[azioni] fatto. Registro dei giri: journalctl -u azioni-candela.service -u azioni-miscela.service --since today"
