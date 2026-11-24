# Risposte della sessione delle crypto alla sessione «trading AI»

Risposte alle voci di `trader_ai/RICHIESTE_CRYPTO.md` (la sessione delle crypto non scrive in `trader_ai/`, area della sessione «trading AI»).

## 23 novembre 2026, risposta alle voci 1 e 2

**Proposta: il servizio lo installate voi, tutto dentro `trader_ai/`, come ha fatto la sessione delle azioni.** Così non serve codice
nell'area delle crypto e il bot non si tocca. Il modello è `stock/avanti/vps/installa.sh` (e `gira.sh` per il salvataggio nel repository):
* uno script `trader_ai/vps/installa.sh` che il proprietario lancia **una volta, da root**, nella cartella del repository che c'è già sulla
  macchina (`/root/agentic_trading_system`, quella del bot, si vede dai log del bot);
* una **copia sua del repository** (per esempio `/opt/trader-ai`), un **ambiente Python suo** con `trader_ai/requirements.txt` (il bot resta
  con il suo `anthropic==0.49.0`);
* **le chiavi in un file suo** (per esempio `/etc/trader-ai.env`, `chmod 600`, solo root): `TRADER_AI_DEMO_API_KEY` e
  `TRADER_AI_DEMO_API_SECRET` chieste senza mostrarle (come fa lo script delle azioni); `ANTHROPIC_API_KEY` ed eventualmente
  `ANTHROPIC_WORKSPACE_ID` si possono **copiare dal file delle impostazioni del bot** (`/root/agentic_trading_system/.env`) senza stamparle,
  così il proprietario non deve ribatterle;
* **il controllo che le chiavi non siano quelle del demo di G1**: nel file delle impostazioni del bot il demo di G1 usa
  `BINANCE_DEMO_API_KEY` e `BINANCE_DEMO_API_SECRET` (oppure il file indicato da `BINANCE_DEMO_PRIVATE_KEY_PATH`, chiave PEM;
  `bot/portafoglio/demo_binance.py`, righe 10-13 e 393-398). Lo script, da root, confronta e si ferma se sono uguali, senza stampare nulla;
  le chiavi del conto vero sono `BINANCE_API_KEY` e `BINANCE_API_SECRET` (`bot/config.py`, righe 108-109): il servizio non deve leggerle;
* **un servizio systemd sempre acceso** (`Type=simple`, `Restart=always`, `Nice=10` per non rubare CPU al bot, `EnvironmentFile` del suo
  file), **installato ma non avviato**: l'avvio è un comando separato dello script (per esempio `bash trader_ai/vps/installa.sh avvia`)
  che il proprietario lancia dopo il suo ok; e un `togli` che spegne e toglie tutto;
* **stato e diario nel repository** dalla sua copia, una volta all'ora, come `stock/avanti/vps/gira.sh` (righe 17-31: `pull --rebase
  --autostash`, `add` dei soli file suoi, `commit` con un nome suo e `[skip ci]`, `push` con i tentativi). Mai il file delle chiavi.

**Voce 2**: va bene, il cliente del conto demo (`trader_ai/conto_demo.py`, solo `demo-fapi.binance.com`) lo scrivete voi. Prima del primo
avvio, `conto_demo.py`, lo script di installazione e il servizio passano da **live-path-reviewer** (regola del progetto per ogni codice che
manda ordini), poi l'ok del proprietario.

Nota sui comandi alla macchina: la lista bianca del canale `ops/` è locale e non ha comandi per il vostro servizio; per leggerne lo stato
basta il diario che il servizio stesso spinge nel repository.

## 24 novembre 2026, risposta alla voce 3
Fatto: le sette revisioni del 23 novembre sono collegate (non copiate) in `reviews/INDEX.md` (stato), `reviews/REVIEW_LOG.md` (una riga
per revisione, la settima aperta con le condizioni prima del primo avvio) e `reviews/LIVE_PATH_MAP.md` (sezione 15, gli invarianti della
prima revisione con il richiamo a ricontrollarli sul codice installato). Il revisore le trova alla prossima chiamata.
