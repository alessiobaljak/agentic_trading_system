#!/usr/bin/env bash
# ============================================================================
# VALIDAZIONE COMPLETA IN POCHE ORE, CON LO STESSO IDENTICO CRITERIO.
#
# IL VINCOLO. Un pass conta solo se dall'ultimo sono entrate
# OPTIMIZER_NEW_DATA_MIN_HOURS (168 = una settimana) di dati NUOVI. Con
# MIN_PASSES=3 questo significa tre settimane di calendario — e non c'e' modo di
# accorciarle lasciando intatti i pass gia' presi, perche' una coppia il cui
# ultimo pass e' datato OGGI non puo' prenderne un altro prima di sette giorni.
# Qualunque acceleratore deve quindi ripartire da un registro azzerato.
#
# L'IDEA (la stessa di backfill_passes.sh): non serve aspettare che il tempo
# passi, basta far FINIRE i dati in momenti diversi. Tre passate con --end
# distanziati di piu' di una settimana vedono tre finestre OOS e soprattutto tre
# HOLDOUT diversi (gli ultimi GATE_HOLDOUT_DAYS si spostano con la data di fine):
# sono esattamente le tre conferme che avremmo raccolto aspettando tre settimane.
#
# COSA AGGIUNGE QUESTO SCRIPT: L'IMBUTO. Con esattamente MIN_PASSES finestre, una
# coppia si valida solo se le passa TUTTE. Quindi chi fallisce la prima non potra'
# mai validarsi, e ri-testarlo sulle altre due e' tempo buttato. Dalla seconda
# finestra in poi si testano SOLO i sopravvissuti. Il risultato e' identico a
# quello della passata completa — non "simile": identico, perche' le coppie
# saltate sono quelle che il criterio ha gia' escluso — ma costa una passata
# intera invece di tre.
#
# COSA NON E'. Non abbassa nessuna soglia, non tocca il gate, non riduce le
# finestre di walk-forward. Se una coppia passa solo con i dati fino a oggi e non
# con quelli di due settimane fa, NON si valida: e' proprio il caso che la regola
# vuole scartare, e qui viene scartato oggi invece che fra tre settimane.
#
# Uso (sul VPS, dentro tmux — dura ore):
#   tmux new -s fastgate
#   bash scripts/fast_gate.sh --yes            # 3 finestre a 9 giorni
#   bash scripts/fast_gate.sh --yes 3 12       # 3 finestre a 12 giorni
# ============================================================================
set -uo pipefail

YES=0
NUMS=()
for a in "$@"; do
  case "$a" in
    --yes) YES=1 ;;
    ''|*[!0-9]*) : ;;
    *) NUMS+=("$a") ;;
  esac
done
N="${NUMS[0]:-3}"          # quante finestre (deve essere = MIN_PASSES)
STEP="${NUMS[1]:-9}"       # giorni fra una finestra e l'altra

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP_DIR"
PY="$APP_DIR/.venv/bin/python"
[ -x "$PY" ] || PY="python3"

_env() { grep -E "^$1=" .env 2>/dev/null | tail -1 | cut -d= -f2; }
MIN_PASSES="$(_env OPTIMIZER_MIN_PASSES)"; MIN_PASSES="${MIN_PASSES:-3}"
MIN_H="$(_env OPTIMIZER_NEW_DATA_MIN_HOURS)"; MIN_H="${MIN_H:-168}"
MIN_D=$(( (${MIN_H%.*} + 23) / 24 ))

# L'IMBUTO E' ESATTO SOLO SE le finestre sono tante quante i pass richiesti: con
# piu' finestre una coppia potrebbe validarsi saltandone una, e allora scartare
# chi fallisce la prima taglierebbe fuori candidati legittimi. Meglio rifiutare
# che produrre un risultato che si crede completo e non lo e'.
if [ "$N" -ne "$MIN_PASSES" ]; then
  echo "ERRORE: con $N finestre e MIN_PASSES=$MIN_PASSES l'imbuto non e' piu' esatto."
  echo "        Una coppia potrebbe validarsi fallendo la prima finestra, e questo"
  echo "        script non la vedrebbe. Usa $MIN_PASSES finestre, oppure"
  echo "        scripts/backfill_passes.sh (piu' lento, nessun imbuto)."
  exit 1
fi
if [ "$STEP" -le "$MIN_D" ]; then
  echo "ERRORE: passo di $STEP giorni <= soglia del pass onesto ($MIN_D giorni)."
  echo "        Le finestre conterebbero come UN solo pass. Usa almeno $((MIN_D + 1))."
  exit 1
fi

if [ "$YES" -ne 1 ]; then
  echo "Valida il GATE 1 in poche ore invece che in tre settimane."
  echo "  finestre: $N · passo: $STEP giorni · copre $(( (N - 1) * STEP )) giorni di storia"
  echo
  echo "  AZZERA il registro (necessario: i pass datati oggi bloccano le finestre"
  echo "  passate). Prima fa un backup su gate_backup_*.json."
  echo "  NON tocca paper, equity, learning, user_risk."
  echo "  Il bot resta FLAT durante l'esecuzione."
  echo
  echo "Per eseguire:  bash scripts/fast_gate.sh --yes $N $STEP"
  exit 1
fi

export BACKTEST_ALLOW_SYNTHETIC=false     # MAI validare su dati finti

systemctl stop trading-optimizer.timer trading-optimizer.service 2>/dev/null || true
trap 'systemctl start trading-optimizer.timer 2>/dev/null || true; echo "[fast-gate] timer riattivato"' EXIT

# BACKUP PRIMA DI AZZERARE. Lezione pagata: le spec delle strategie generate
# vengono eliminate insieme alle coppie purgate, e senza di esse i trade gia'
# fatti non sono piu' rigiocabili (30 coppie su 31 perse dopo un reset).
STAMP="$(date -u +%Y%m%d_%H%M%S)"
"$PY" - "$STAMP" <<'PYEOF'
import json, sys
from bot.core.firebase_client import get_firebase
fb = get_firebase()
dump = {"registry": fb.get_doc("strategy_registry", "validated") or {},
        "specs": fb.get_doc("discovered_strategies", "specs") or {},
        "params": fb.get_doc("strategy_params", "current") or {}}
path = f"gate_backup_{sys.argv[1]}.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(dump, f)
print(f"[fast-gate] backup in {path}")
fb.set_doc("strategy_registry", "validated", {})
fb.set_doc("discovered_strategies", "specs", {"specs": {}})
fb.set_doc("strategy_params", "current", {})
print("[fast-gate] registro azzerato")
PYEOF

# il bot deve andare FLAT subito: senza restart tiene in memoria il registro
# vecchio fino a ADAPT_RELOAD_SECONDS e continuerebbe ad aprire posizioni su
# coppie che stiamo ri-validando
systemctl restart trading-bot.service 2>/dev/null \
  || echo "[fast-gate] riavvia il bot A MANO ORA: sudo systemctl restart trading-bot.service"

OPT_FULL="--top 200 --windows 3 --max-combos 12 --start 2022-01-01"
DISC_FULL="--top 200 --generate 100 --reeval-cap 500 --windows 3 --start 2022-01-01"

echo "[fast-gate] $N finestre · passo $STEP giorni · soglia pass onesto ${MIN_H}h"
for i in $(seq $((N - 1)) -1 0); do
  END="$(date -u -d "-$((i * STEP)) days" +%F)"
  W=$((N - i))
  if [ "$W" -eq 1 ]; then
    # PRIMA FINESTRA: universo intero. E' l'unica passata cara, e serve a
    # scoprire CHI sono i candidati.
    echo "[fast-gate] === finestra 1/$N · universo intero · dati fino al $END === $(date -u)"
    "$PY" -m scripts.optimize $OPT_FULL --end "$END" \
      || echo "[fast-gate] optimize finestra 1 FALLITA (continuo)"
    "$PY" -m scripts.discover_strategies $DISC_FULL --end "$END" \
      || echo "[fast-gate] discover finestra 1 FALLITA (continuo)"
  else
    # FINESTRE SUCCESSIVE: solo le coin dei sopravvissuti. Chi non ha ancora
    # W-1 pass non puo' piu' arrivare a MIN_PASSES, quindi non c'e' niente da
    # sapere su di lui.
    COINS="$("$PY" -m scripts.gate_progress --coins-min-pass $((W - 1)) 2>/dev/null | tail -1)"
    # la lista finisce dentro --symbols: se non ha la forma attesa (traceback, riga
    # di log) meglio fermarsi che validare un universo inventato
    if ! echo "$COINS" | grep -qE '^[A-Z0-9]+(,[A-Z0-9]+)*$'; then
      echo "[fast-gate] lista coin non valida ('$COINS'): mi fermo invece di indovinare."
      break
    fi
    if [ -z "$COINS" ]; then
      echo "[fast-gate] === finestra $W/$N: NESSUN sopravvissuto dalla precedente."
      echo "[fast-gate]     Nessuna coppia puo' piu' raggiungere $MIN_PASSES pass: mi fermo."
      break
    fi
    NCOINS="$(echo "$COINS" | tr ',' '\n' | grep -c .)"
    echo "[fast-gate] === finestra $W/$N · $NCOINS coin sopravvissute · fino al $END === $(date -u)"
    "$PY" -m scripts.optimize --symbols "$COINS" --windows 3 --max-combos 12 \
        --start 2022-01-01 --end "$END" \
      || echo "[fast-gate] optimize finestra $W FALLITA (continuo)"
    # --generate 0: dalla seconda finestra in poi si CONFERMA, non si scopre.
    # Una candidata nuova qui nascerebbe con 1 pass e non potrebbe comunque
    # arrivare a $MIN_PASSES prima della fine dello script.
    "$PY" -m scripts.discover_strategies --symbols "$COINS" --generate 0 \
        --reeval-cap 500 --windows 3 --start 2022-01-01 --end "$END" \
      || echo "[fast-gate] discover finestra $W FALLITA (continuo)"
  fi
done

systemctl restart trading-bot.service 2>/dev/null \
  || echo "[fast-gate] riavvia il bot a mano: sudo systemctl restart trading-bot.service"

echo
echo "[fast-gate] FATTO $(date -u). Esito:"
"$PY" -m scripts.gate_progress || true
