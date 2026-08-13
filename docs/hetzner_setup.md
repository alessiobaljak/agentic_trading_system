# Setup VPS Hetzner — passo per passo

Obiettivo: far girare il **bot core 24/7** in paper trading (`DRY_RUN=true`) su una
VPS Hetzner. Tempo stimato: ~30 minuti.

> Prerequisito: un account su https://www.hetzner.com/cloud

---

## 1. Crea il server
1. Entra nella **Hetzner Cloud Console** → **New Project** (es. "trading") → **Add Server**.
2. **Location**: una EU (Nuremberg / Falkenstein / Helsinki). Vanno bene per Binance.
3. **Image**: **Ubuntu 24.04**.
4. **Type**: **CX22** (2 vCPU, 4 GB RAM, ~€4/mese) — sufficiente per il **bot**.
   Per la **validazione** (GATE 1) serve di più: vedi "Dimensionare la macchina".
5. **SSH Key**: aggiungi la tua chiave pubblica (consigliato). Se non ne hai una:
   ```bash
   # sul TUO computer
   ssh-keygen -t ed25519 -C "trading-vps"
   cat ~/.ssh/id_ed25519.pub   # copia questo e incollalo in Hetzner
   ```
   (In alternativa scegli "password" e Hetzner te ne manda una via email.)
6. **Create & Buy now**. Annota l'**IP** del server.

## 2. Connettiti
```bash
ssh root@IL_TUO_IP        # accetta il fingerprint la prima volta
```

## 3. Aggiorna e installa i pacchetti base
```bash
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip git
```
> Ubuntu 24.04 ha Python 3.12: va bene per questo progetto.

## 4. (Consigliato) firewall minimale
```bash
apt install -y ufw
ufw allow OpenSSH
ufw --force enable
```

## 5. Clona il repository
Il repo è privato, quindi serve autenticarsi. Crea un **Personal Access Token**
GitHub (Settings → Developer settings → Tokens, scope `repo`) e usalo come password:
```bash
cd /root        # o /opt, o dove preferisci: la scelta e' libera (vedi nota sotto)
git clone https://github.com/alessiobaljak/agentic_trading_system.git
# username: alessiobaljak   password: <il-tuo-token>
cd agentic_trading_system
git checkout claude/brave-albattani-1b12fv
export APP_DIR="$(pwd)"   # usato dai comandi piu' avanti
```

> **La directory non e' fissa.** Gli script del repo ricavano il proprio path da soli
> (`APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"`), quindi funzionano ovunque tu abbia
> clonato. Solo la unit systemd qui sotto scrive path assoluti, ed e' l'unica cosa da
> tenere allineata. **L'installazione in produzione sta in `/root/agentic_trading_system`.**
>
> Se apri una shell nuova e non ricordi dove sia, chiedilo al servizio che sta girando:
> ```bash
> systemctl show trading-bot.service -p WorkingDirectory
> ```

## 6. Ambiente Python + dipendenze
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## 7. Configura le chiavi (.env)
```bash
cp .env.example .env
nano .env
```
Compila almeno:
- `DRY_RUN=true` e `BINANCE_TESTNET=true` (lascia così all'inizio!)
- `BINANCE_API_KEY`, `BINANCE_API_SECRET`
- `ANTHROPIC_API_KEY`
- `FIREBASE_SERVICE_ACCOUNT` = **tutto il JSON del service account su UNA riga**
- `FIREBASE_RTDB_URL`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- (opzionali) `LUNARCRUSH_API_KEY`, `COINGLASS_API_KEY`, `NEWSAPI_KEY`

Salva con `Ctrl+O`, `Invio`, `Ctrl+X`.

## 8. Verifica le chiavi
```bash
python -m scripts.verify_keys
```
Da qui Binance dovrebbe finalmente dare **OK** (niente più geo-block 451).

## 9. Prova il bot in paper trading
```bash
python -m bot.main
```
Guarda i log; fermalo con `Ctrl+C`. Se gira senza errori, passa al 24/7.

## 10. Fallo girare 24/7 con systemd
Crea il servizio:
```bash
# NB: heredoc SENZA apici -> $APP_DIR viene espanso nei path assoluti della unit
# (systemd non espande variabili di shell, quindi devono essere gia' risolti qui).
cat > /etc/systemd/system/trading-bot.service <<EOF
[Unit]
Description=Agentic Trading Bot
After=network-online.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/.venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now trading-bot
```
Controlla i log live:
```bash
journalctl -u trading-bot -f
```

## Sicurezza (importante)
- La API key Binance **senza permesso di Withdraw**.
- Tieni `DRY_RUN=true` per **settimane** (GATE 2) prima di pensare al live.
- Aggiornamenti del codice: `cd "$APP_DIR" && git pull && systemctl restart trading-bot`
  (in produzione: `cd /root/agentic_trading_system && git pull && systemctl restart trading-bot`).

> **Una volta sola, per non vedere più `git pull` abortire.** `docs/state.md` è
> generato: lo scrive la GitHub Action, e lo riscrive chiunque lanci
> `scripts.state_snapshot` sulla VPS. Basta un file generato non committato e il
> pull si ferma con *"Your local changes would be overwritten"* — e i comandi
> lanciati subito dopo girano sulla versione vecchia del codice, che è il modo
> peggiore di accorgersene. Rimedio permanente:
> ```bash
> git config pull.rebase true
> git config rebase.autoStash true
> ```
> Da lì in poi il pull mette da parte le modifiche locali, aggiorna e le rimette.

## Passaggio a live (solo dopo paper positivo + GATE 1 superato)
Nel `.env`: `DRY_RUN=false` (e `BINANCE_TESTNET=false` quando pronto), poi
`systemctl restart trading-bot`. Capitale ridotto, leva 1–2x, monitoraggio attivo.

---

## Dimensionare la macchina

Sulla stessa VPS girano due carichi con esigenze opposte, e confonderli porta a
comprare la macchina sbagliata.

**Il bot** (`trading-bot.service`) non consuma quasi nulla: un tick ogni 30
secondi, qualche richiesta REST, un WebSocket. Ci gira su due core condivisi senza
accorgersene, e continuerà a girarci qualunque cosa si decida per il resto.

**La validazione** (`trading-optimizer.service`) è tutt'altro: walk-forward su
centinaia di coin per decine di strategie, oltre ventimila valutazioni per
passata. È il carico che decide la macchina.

### Cosa NON si accorcia con l'hardware

La validazione richiede **tre conferme distanziate da una settimana di dati
nuovi** (`OPTIMIZER_NEW_DATA_MIN_HOURS`). Sono tre settimane di calendario, e
nessuna CPU al mondo fa arrivare prima i dati di mercato. Un processore più veloce
non accorcia di un minuto l'attesa: accorcia solo il tempo di *calcolo* dentro
ogni passata.

L'unico modo onesto di comprimere quelle tre settimane è `scripts/fast_gate.sh`,
che rigioca la storia con tre date di fine diverse — e *quello* sì è
CPU-dipendente.

### Cos'era rete e non CPU

Fino ad agosto 2026 la cache delle candele era indicizzata anche sulla **data di
fine**. Ogni finestra di validazione cambia esattamente quella, quindi ogni
finestra era un buco nella cache: ~140.000 candele per coin (4 anni a 15m)
riscaricate da capo, per duecento coin, decine di migliaia di richieste HTTP a
passata. Su quella parte l'hardware non incideva per niente.

Ora una serie in cache più lunga viene **tagliata** e una più corta viene
**estesa** scaricando la sola coda mancante. Prima di valutare un upgrade, misura
di nuovo: una buona parte del tempo che sembrava calcolo era attesa di rete.

### Se dopo la misura serve davvero più CPU

Il calcolo è parallelo per simbolo (processi separati, `BACKTEST_WORKERS`), quindi
scala quasi linearmente coi core. Regole pratiche:

- **RAM**: circa **1,2 GB per worker**. Con 4 GB si sta a 2 worker, che è il vero
  motivo per cui su CX22 non si va oltre. Vuoi 8 worker? Servono ~12 GB, quindi
  16 GB di taglio.
- **vCPU dedicate, non condivise**: la validazione tiene i core al 100% per ore.
  È il profilo per cui esiste la linea **CCX** (dedicata); sulle linee condivise
  (CX/CPX) un carico così prolungato è esattamente ciò che le condizioni d'uso
  scoraggiano, oltre a subire il "rumore" degli altri tenant.
- **Ordini di grandezza**: passando da 2 core condivisi a 8 dedicati la passata si
  accorcia di circa 4 volte. Verifica i tagli e i prezzi correnti sul sito: qui si
  documenta il criterio, non il listino.

### L'alternativa più economica

Hetzner fattura **a ore**. Il bot può restare sulla CX22 e la macchina grossa si
crea **solo quando serve** una rivalidazione completa, si esegue `fast_gate.sh`, e
si distrugge. Costa qualche centesimo invece di un canone mensile.

Un avvertimento pratico: una macchina nuova ha la cache delle candele **vuota**, e
riempirla è proprio la parte lenta. Se scegli questa strada, copia prima la cache:

```bash
rsync -az /root/agentic_trading_system/.cache/ nuovo-server:/root/agentic_trading_system/.cache/
```

### Come spendere i core in più

Questa è la parte che conta più della macchina. Con più CPU la tentazione è
alzare `--generate`, cioè provare più strategie casuali. **È la scelta peggiore**:
il sistema valuta già ~1.500 coppie per run, e a quella scala ci si aspettano
alcune strategie di puro rumore che superano la soglia per fortuna. Raddoppiare le
candidate raddoppia i falsi positivi, e il paper li scopre pagandoli.

I core in più vanno spesi in **rigore**, non in volume:

- `--windows 5` invece di 3 — più finestre walk-forward, validazione più severa;
- più **conferme** su date di fine diverse (`fast_gate`, `backfill_passes`);
- ricerca **guidata** attorno ai quasi-passaggi (già automatica: vedi
  `scripts/gate_autopsy.py`), che esplora a fondo poche zone promettenti invece di
  estrarre a caso;
- iterazione più rapida sui **criteri**, che è ciò che davvero sblocca il gate.
