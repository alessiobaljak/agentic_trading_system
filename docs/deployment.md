# Deployment

Tutto gira su cloud; nessun componente sul computer dell'utente.

## 1. Bot core 24/7 — VPS Hetzner
```bash
# sulla VPS (Ubuntu 22.04+)
sudo apt update && sudo apt install -y python3.11 python3.11-venv git
git clone <repo> && cd agentic_trading_system
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # compila le chiavi
python -m bot.main     # avvio in DRY_RUN (paper)
```

### systemd (24/7 con restart automatico)
`/etc/systemd/system/trading-bot.service`:
```ini
[Unit]
Description=Agentic Trading Bot
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/USER/agentic_trading_system
EnvironmentFile=/home/USER/agentic_trading_system/.env
ExecStart=/home/USER/agentic_trading_system/.venv/bin/python -m bot.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now trading-bot
journalctl -u trading-bot -f   # log live
```

## 2. Firebase
1. Crea progetto, abilita **Firestore** e **Realtime Database**.
2. Project settings → Service accounts → genera chiave JSON.
3. Metti il JSON (una riga) in `FIREBASE_SERVICE_ACCOUNT` (`.env` VPS + GitHub
   Secret). Imposta `FIREBASE_RTDB_URL`.
4. Applica le regole di sicurezza consigliate in `docs/firebase_schema.md`.

## 3. Dashboard — Vercel
1. Importa il repo su Vercel, **Root Directory = `dashboard`**.
2. Imposta le env `NEXT_PUBLIC_FIREBASE_*` (config client web Firebase).
3. Deploy. La dashboard legge RTDB/Firestore in tempo reale.

## 4. GitHub Actions
Imposta i Secrets (README §7.1). I workflow in `.github/workflows/`:
- `learning.yml` — nightly 02:00 UTC
- `monitoring.yml` — ogni 15 min (heartbeat + alert)
- `tests.yml` — su push/PR
- `backtest.yml` — manuale (GATE 1)

## 5. Procedura di go-live (gates)
1. **GATE 1**: esegui il backtest finché il verdetto è "passed".
2. Avvia il bot in **DRY_RUN=True** (GATE 2 paper trading).
3. Mantieni il paper per **settimane** con risultati positivi; verifica che il
   learning loop produca pesi sensati e che gli alert funzionino.
4. Solo allora imposta **`DRY_RUN=False`** con capitale ridotto, leva bassa
   (1–2x) e API key Binance **senza** permesso di withdraw.
