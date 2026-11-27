#!/usr/bin/env bash
# ============================================================================
# Installa sulla macchina il TRADER AI (conto demo SUO di Binance, soldi finti), separato dal bot: il CODICE in /opt/trader-ai (si
# aggiorna solo rilanciando questo script, mai da solo: revisione del 23 novembre 2026, problema 98), i DATI in un'altra copia del
# repository, /opt/trader-ai-dati (stato, diario, resoconti, salvati ogni ora), un ambiente Python suo, le chiavi in un file suo
# (/etc/trader-ai.env, solo root), un servizio sempre acceso (trader-ai.service) e il timer del salvataggio. Non tocca il bot, i suoi servizi né il suo .env
# (lo legge soltanto, per copiare la chiave del modello e controllare che le chiavi nuove non siano quelle di un altro conto).
#
# Da lanciare da root, dentro la cartella del repository che c'è già sulla macchina (/root/agentic_trading_system):
#     bash trader_ai/vps/installa.sh            installa o aggiorna il codice (chiede le chiavi la prima volta); NON avvia
#     bash trader_ai/vps/installa.sh prova      la prova sul demo con la quantità minima (prima del primo avvio, trader spento)
#     bash trader_ai/vps/installa.sh avvia      avvia il trader (solo dopo l'ok del proprietario)
#     bash trader_ai/vps/installa.sh ferma      lo ferma (le posizioni aperte restano con stop e obiettivo sul conto)
#     bash trader_ai/vps/installa.sh chiudi     chiude posizione e ordini del trader e lo tiene fermo finché non arriva «riparti»
#     bash trader_ai/vps/installa.sh riparti
#     bash trader_ai/vps/installa.sh stato      stato del servizio e ultime righe del registro
#     bash trader_ai/vps/installa.sh chiavi     reinserisce le due chiavi del conto demo
#     bash trader_ai/vps/installa.sh togli      toglie servizio e timer (restano /opt/trader-ai e /etc/trader-ai.env)
# ============================================================================
set -euo pipefail
DEST=/opt/trader-ai
DATI=/opt/trader-ai-dati
ENVF=/etc/trader-ai.env
RAMO=claude/brave-albattani-1b12fv
QUI="$(cd "$(dirname "$0")/../.." && pwd)"
ENV_BOT="$QUI/.env"

valore() {   # valore di una variabile in un file .env, senza stamparlo (toglie le virgolette)
  [ -f "$2" ] || return 0
  grep -m1 -E "^[[:space:]]*(export[[:space:]]+)?$1[[:space:]]*=" "$2" 2>/dev/null | cut -d= -f2- \
    | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^["'\'']//' -e 's/["'\'']$//' || true
}

simulato() { grep -q '"conto": "simulato"' "$QUI/trader_ai/config.json"; }

chiedi_chiavi() {
  if simulato; then          # conto simulato (24 novembre 2026): nessuna chiave di Binance, solo quella del modello
    A="$(valore ANTHROPIC_API_KEY "$ENV_BOT")"
    W="$(valore ANTHROPIC_WORKSPACE_ID "$ENV_BOT")"
    [ -n "$A" ] || { echo "[trader-ai] manca ANTHROPIC_API_KEY nelle impostazioni del bot: mi fermo"; exit 1; }
    umask 077
    { printf 'ANTHROPIC_API_KEY=%s\n' "$A"; [ -n "$W" ] && printf 'ANTHROPIC_WORKSPACE_ID=%s\n' "$W"; true; } > "$ENVF"
    chmod 600 "$ENVF"
    echo "[trader-ai] conto simulato: nessuna chiave di Binance; chiave del modello copiata dalle impostazioni del bot in $ENVF (solo root)"
    return 0
  fi
  echo "[trader-ai] Chiavi del conto demo NUOVO (non quello di G1). Non compaiono mentre scrivi."
  read -r -s -p "  TRADER_AI_DEMO_API_KEY: " K; echo
  read -r -s -p "  TRADER_AI_DEMO_API_SECRET: " S; echo
  [ -n "$K" ] && [ -n "$S" ] || { echo "[trader-ai] chiavi vuote: mi fermo"; exit 1; }
  for NOME in BINANCE_DEMO_API_KEY BINANCE_DEMO_API_SECRET BINANCE_API_KEY BINANCE_API_SECRET; do
    ALTRA="$(valore "$NOME" "$ENV_BOT")"
    if [ -n "$ALTRA" ] && { [ "$ALTRA" = "$K" ] || [ "$ALTRA" = "$S" ]; }; then
      echo "[trader-ai] queste chiavi sono uguali a $NOME del bot: servono quelle del conto demo NUOVO. Mi fermo."; exit 1
    fi
  done
  PEM="$(valore BINANCE_DEMO_PRIVATE_KEY_PATH "$ENV_BOT")"
  if [ -n "$PEM" ] && [ -f "$PEM" ] && grep -qF -- "$S" "$PEM" 2>/dev/null; then
    echo "[trader-ai] il segreto coincide con la chiave del demo di G1. Mi fermo."; exit 1
  fi
  A="$(valore ANTHROPIC_API_KEY "$ENV_BOT")"
  W="$(valore ANTHROPIC_WORKSPACE_ID "$ENV_BOT")"
  [ -n "$A" ] || { echo "[trader-ai] manca ANTHROPIC_API_KEY nel .env del bot: mi fermo"; exit 1; }
  umask 077
  {
    printf 'TRADER_AI_DEMO_API_KEY=%s\n' "$K"
    printf 'TRADER_AI_DEMO_API_SECRET=%s\n' "$S"
    printf 'ANTHROPIC_API_KEY=%s\n' "$A"
    [ -n "$W" ] && printf 'ANTHROPIC_WORKSPACE_ID=%s\n' "$W"
  } > "$ENVF"
  chmod 600 "$ENVF"
  echo "[trader-ai] chiavi salvate in $ENVF (solo root); la chiave del modello è stata copiata dal .env del bot"
}

case "${1:-installa}" in
  avvia)
    systemctl enable --now trader-ai.service trader-ai-salva.timer
    sleep 5; systemctl --no-pager status trader-ai.service | head -n 12; exit 0 ;;
  ferma)
    systemctl disable --now trader-ai.service; echo "[trader-ai] fermo; stop e obiettivo restano sul conto demo"; exit 0 ;;
  stato)
    systemctl --no-pager status trader-ai.service | head -n 12 || true
    journalctl -u trader-ai.service -n 30 --no-pager || true; exit 0 ;;
  chiavi)
    chiedi_chiavi; exit 0 ;;
  prova)
    simulato && { echo "[trader-ai] conto simulato: la prova sul demo non serve (nessun ordine va a Binance)"; exit 0; }
    systemctl is-active --quiet trader-ai.service && { echo "[trader-ai] il trader è acceso: prima «ferma»"; exit 1; }
    ( set -a; . "$ENVF"; set +a; export TRADER_AI_DATI="$DATI/trader_ai/avanti"; cd "$DEST" && .venv/bin/python -m trader_ai.prova )
    exit $? ;;
  chiudi|riparti)
    ( set -a; . "$ENVF"; set +a; export TRADER_AI_DATI="$DATI/trader_ai/avanti"; cd "$DEST" && .venv/bin/python -m trader_ai.avvio "$1" )
    exit $? ;;
  togli)
    systemctl disable --now trader-ai.service trader-ai-salva.timer 2>/dev/null || true
    rm -f /etc/systemd/system/trader-ai.service /etc/systemd/system/trader-ai-salva.{service,timer}
    systemctl daemon-reload
    echo "[trader-ai] servizio e timer tolti. Restano $DEST e $ENVF: cancellali a mano se non servono più."; exit 0 ;;
  installa) ;;
  *) echo "uso: installa.sh [installa|avvia|ferma|stato|chiavi|togli]"; exit 2 ;;
esac

if [ ! -d "$DEST/.git" ]; then
  # stesso indirizzo (e stesse credenziali) della copia che c'è già; l'indirizzo non si stampa: può contenere il token
  git clone -q --branch "$RAMO" "$(git -C "$QUI" remote get-url origin)" "$DEST"
  echo "[trader-ai] copia del repository in $DEST"
else
  git -C "$DEST" pull -q --ff-only origin "$RAMO" || { echo "[trader-ai] aggiornamento del codice non riuscito: mi fermo"; exit 1; }
  echo "[trader-ai] codice aggiornato (servirà «ferma» e «avvia» perché il servizio lo usi)"
fi
if [ ! -d "$DATI/.git" ]; then
  git clone -q --branch "$RAMO" "$(git -C "$QUI" remote get-url origin)" "$DATI"
  echo "[trader-ai] copia per i dati in $DATI"
fi
# il salvataggio deve scrivere su GitHub senza chiedere la password: si usano le credenziali già salvate sulla macchina per il bot
git -C "$DATI" config credential.helper store
echo "[trader-ai] codice al commit $(git -C "$DEST" rev-parse --short HEAD)"
python3 -m venv "$DEST/.venv"
"$DEST/.venv/bin/pip" install -q --upgrade pip
"$DEST/.venv/bin/pip" install -q -r "$DEST/trader_ai/requirements.txt"
echo "[trader-ai] ambiente Python pronto"

# con il conto simulato il file si riscrive SEMPRE (solo la chiave del modello): non deve restarci nessuna chiave di Binance
# (revisione del 24 novembre 2026, problema 157)
if simulato || [ ! -f "$ENVF" ]; then chiedi_chiavi; else echo "[trader-ai] $ENVF c'è già: non lo tocco (per cambiarle: installa.sh chiavi)"; fi
if simulato && grep -q "TRADER_AI_DEMO" "$ENVF"; then echo "[trader-ai] ATTENZIONE: chiavi di Binance ancora nel file: mi fermo"; exit 1; fi

cat > /etc/systemd/system/trader-ai.service <<UNIT
[Unit]
Description=Trader AI sul conto demo suo di Binance (soldi finti)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$DEST
EnvironmentFile=$ENVF
Environment=PYTHONUNBUFFERED=1
Environment=TRADER_AI_DATI=$DATI/trader_ai/avanti
ExecStart=$DEST/.venv/bin/python -m trader_ai.avvio gira
Restart=always
RestartSec=30
# priorità bassa: non deve mai rubare CPU al bot
Nice=10

[Install]
WantedBy=multi-user.target
UNIT

cat > /etc/systemd/system/trader-ai-salva.service <<UNIT
[Unit]
Description=Trader AI: stato e diario nel repository

[Service]
Type=oneshot
WorkingDirectory=$DATI
Environment=HOME=$HOME
Environment=GIT_TERMINAL_PROMPT=0
Nice=10
ExecStart=/usr/bin/env bash $DEST/trader_ai/vps/salva.sh $DATI
UNIT

cat > /etc/systemd/system/trader-ai-salva.timer <<UNIT
[Unit]
Description=Trader AI: salvataggio ogni 10 minuti (la scheda della plancia li legge dal repository)

[Timer]
OnCalendar=*-*-* *:02/10:00
Persistent=false

[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
# il salvataggio è già acceso: lo si riparte perché prenda l'orario nuovo (non tocca il trader né gli ordini)
systemctl is-active --quiet trader-ai-salva.timer && systemctl restart trader-ai-salva.timer \
  && echo "[trader-ai] salvataggio nel repository: adesso ogni 10 minuti"
echo "[trader-ai] prova del collegamento al conto demo (nessun ordine, nessuna chiamata al modello):"
( set -a; . "$ENVF"; set +a; export TRADER_AI_DATI="$DATI/trader_ai/avanti"; cd "$DEST" && .venv/bin/python -m trader_ai.avvio controlla ) \
  || echo "[trader-ai] ATTENZIONE: il collegamento non va, controlla le chiavi (installa.sh chiavi)"
if systemctl is-active --quiet trader-ai.service; then
  echo "[trader-ai] il trader è acceso e gira con il codice che aveva all'avvio (per il codice nuovo: «ferma» e «avvia»)"
else
  echo "[trader-ai] installato ma NON avviato. Per avviarlo, dopo l'ok: bash trader_ai/vps/installa.sh avvia"
fi
