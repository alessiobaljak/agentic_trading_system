# Trading Bot Dashboard

Next.js 14 (App Router, TypeScript) dashboard for the agentic crypto futures trading bot.
It reads live state from Firebase (Firestore + Realtime Database) using the modular Firebase
Web SDK v9/v10, and lets you adjust risk settings and trigger a kill switch. Deploys to Vercel.

The Python bot writes state to Firebase; this dashboard is read-mostly, with two write paths:

- **Risk settings** → `user_risk_settings/current` (Firestore)
- **Kill switch** → `/commands/kill_switch` (Realtime Database)

## Cosa mostra (dal 10 nov 2026)

Tre schede in alto, pensate prima per il telefono (`app/components/DashboardShell.tsx`):

- **Strategie** (la prima): il bot è vivo (`/bot_status/heartbeat`) e gli allarmi del demo ben visibili
  (`/demo_binance/allarme`, `/demo_binance/allarmi/<tipo>`, `/demo_binance/fermo`); una scheda per strategia, con quelle a
  ordini veri (G1 sul conto demo, con «Chiudi tutto» e «Riparti»; il conto vero, spento) separate da quelle del paper (G1,
  G1 neutra, G11, F5, Eventi): valore, dall'inizio, oggi, ultimi 7 giorni, giorni in guadagno, posizioni, ultimo ribilancio;
  le curve di tutte messe a 100 alla stessa data e G1 demo contro G1 paper giorno per giorno. Dati e conti in
  `app/lib/strategie.ts`, componenti in `app/components/strategie/`.
- **Dettagli**: regole, posizioni e pesi, diario giorno per giorno, il passato, il paper del programma 6.
- **Archivio**: il vecchio sistema, fermo dal 13 ottobre 2026 (report, controllo, operatività, gate, learning,
  impostazioni con il kill switch del vecchio bot). I vecchi segnalibri (`#gate`, `#controllo`…) aprono la loro sezione.

Il tema resta chiaro; lo scuro si accende dal pulsante in alto e si ricorda sul dispositivo.

## Hard limits

The UI mirrors the bot's hardcoded caps (`bot/risk/hard_limits.py`) and **never** lets a value
above them be sent. Single source of truth: `app/lib/hardLimits.ts`.

- `MAX_LEVERAGE = 5`
- `MAX_RISK_PER_TRADE = 0.03` (3%)

Values are clamped on the client before writing. The bot's final risk gate re-enforces the same
caps as the authoritative boundary — the client clamp is a UX guardrail, not a security control.

## Environment variables

All client config uses `NEXT_PUBLIC_*` so it can ship in the browser bundle. Copy
`.env.local.example` to `.env.local` and fill in (Firebase Console → Project settings → General →
Your apps → Web app → SDK setup):

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_FIREBASE_API_KEY` | Web API key |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | Auth domain (`your-project.firebaseapp.com`) |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | Firebase project id |
| `NEXT_PUBLIC_FIREBASE_DATABASE_URL` | Realtime Database URL (required for live data) |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | Storage bucket |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | Messaging sender id |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | App id |

If the required vars (API key, project id, app id, database URL) are missing, the dashboard
renders a "configure Firebase" notice instead of crashing.

## Local development

```bash
npm install
cp .env.local.example .env.local   # then fill in your Firebase values
npm run dev                        # http://localhost:3000
```

Scripts: `dev`, `build`, `start`, `lint`.

**Prova senza Firebase** (solo in locale, mai su Vercel): con `DASHBOARD_PROVA=1` `next.config.mjs` sostituisce i moduli di
firebase con quelli finti di `prova/` (dati inventati, nessuna rete, utente finto). Servono anche quattro variabili qualsiasi
perché la pagina si accenda:

```bash
DASHBOARD_PROVA=1 NEXT_PUBLIC_FIREBASE_API_KEY=prova NEXT_PUBLIC_FIREBASE_PROJECT_ID=prova \
  NEXT_PUBLIC_FIREBASE_APP_ID=prova NEXT_PUBLIC_FIREBASE_DATABASE_URL=https://prova.invalid npx next dev -p 3999
```

Scenari: `/?prova=calmo` (nessun allarme), `/?prova=fermo` (demo fermo). Senza la variabile la configurazione è quella di sempre.

## Deploy to Vercel

1. Push this repo to GitHub.
2. In Vercel, **New Project** → import the repo.
3. Set the project **Root Directory** to `dashboard/`.
4. Framework preset: **Next.js** (auto-detected). Build command `next build`, output handled by
   the framework.
5. Add all `NEXT_PUBLIC_FIREBASE_*` variables under **Settings → Environment Variables** (they are
   safe to expose to the browser; secure your data with Firebase Security Rules, not by hiding the
   web config).
6. Deploy.

## Firebase security note

Because all config is public by design, protect your data with Firestore and Realtime Database
**Security Rules**. At minimum, restrict who can write `user_risk_settings/current` and
`/commands/kill_switch` (e.g. require authentication) and keep the bot's service-account writes
server-side. The hard caps here do not replace server-side enforcement.

## Schema

This dashboard matches the contract documented in the repo. See the project root `README.md`
(section 4 — risk, and the Dashboard section) and `docs/firebase_schema.md` if present. Shared
types live in `app/lib/types.ts`.
