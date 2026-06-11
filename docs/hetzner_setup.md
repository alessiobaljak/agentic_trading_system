# Setup VPS Hetzner — passo per passo

Obiettivo: far girare il **bot core 24/7** in paper trading (`DRY_RUN=true`) su una
VPS Hetzner. Tempo stimato: ~30 minuti.

> Prerequisito: un account su https://www.hetzner.com/cloud

---

## 1. Crea il server
1. Entra nella **Hetzner Cloud Console** → **New Project** (es. "trading") → **Add Server**.
2. **Location**: una EU (Nuremberg / Falkenstein / Helsinki). Vanno bene per Binance.
3. **Image**: **Ubuntu 24.04**.
4. **Type**: **CX22** (2 vCPU, 4 GB RAM, ~€4/mese) — più che sufficiente.
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
cd /opt
git clone https://github.com/alessiobaljak/agentic_trading_system.git
# username: alessiobaljak   password: <il-tuo-token>
cd agentic_trading_system
git checkout claude/brave-albattani-1b12fv
```

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
cat > /etc/systemd/system/trading-bot.service <<'EOF'
[Unit]
Description=Agentic Trading Bot
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/agentic_trading_system
EnvironmentFile=/opt/agentic_trading_system/.env
ExecStart=/opt/agentic_trading_system/.venv/bin/python -m bot.main
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
- Aggiornamenti del codice: `cd /opt/agentic_trading_system && git pull && systemctl restart trading-bot`.

## Passaggio a live (solo dopo paper positivo + GATE 1 superato)
Nel `.env`: `DRY_RUN=false` (e `BINANCE_TESTNET=false` quando pronto), poi
`systemctl restart trading-bot`. Capitale ridotto, leva 1–2x, monitoraggio attivo.
