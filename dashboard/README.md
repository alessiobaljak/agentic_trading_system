# Plancia (la dashboard)

Next.js 14 (App Router, TypeScript) dashboard for the agentic crypto futures trading bot.
It reads live state from Firebase (Firestore + Realtime Database) using the modular Firebase
Web SDK v9/v10, and lets you adjust risk settings and trigger a kill switch. Deploys to Vercel.

The Python bot writes state to Firebase; this dashboard is read-mostly, with two write paths:

- **Risk settings** → `user_risk_settings/current` (Firestore)
- **Kill switch** → `/commands/kill_switch` (Realtime Database)

## Cosa mostra (dal 10 nov 2026): la Plancia

La dashboard si chiama **Plancia** («crypto e azioni · niente soldi veri»), pensata prima per il telefono:

* **In alto le aree**: la lista è in `app/components/aree.ts`. Oggi Crypto e Azioni; un'area nuova è una riga.
* **A sinistra il menu**: le pagine dell'area scelta. Sul telefono è il pulsante ☰.
* **Gli indirizzi** sono `#<area>/<pagina>/<resto>`, per esempio `#crypto/strategie`, `#crypto/dettagli/g1demo`,
  `#crypto/archivio/gate`, `#azioni/strategie`.
* **I vecchi segnalibri** (`#gate`, `#controllo`, `#dettagli`, `#azioni`…) aprono la pagina giusta. Guscio in
  `app/components/DashboardShell.tsx`.

**Crypto** (`app/components/crypto/area.tsx`), con in cima a ogni pagina il bot vivo e gli allarmi del demo:

- **Strategie** (la principale):
  - una scheda per strategia, con quelle a ordini veri (G1 sul conto demo, con «Chiudi tutto» e «Riparti»; il conto vero, spento)
    separate dal paper (G1, G1 neutra, G11, F5, Eventi);
  - le curve di tutte messe a 100 alla stessa data;
  - G1 demo contro G1 paper dalla partenza del demo.
  
  Dati in `app/lib/strategie.ts`, componenti in `app/components/strategie/`.
- **Dettagli**: una strategia alla volta.
  - riquadri: valore, oggi, 7 giorni, dall'inizio, discesa massima, spese, funding, ordini limite;
  - giorno per giorno (verde in guadagno, arancione in perdita), pesi delle monete, ultimo ribilancio;
  - il conto demo, le operazioni degli eventi, G1 demo contro paper giorno per giorno con le fasi (chiuso).
  
  Dati in `app/lib/dettagli.ts`, componenti in `app/components/dettagli/`.
- **Archivio**: il vecchio sistema, fermo dal 13 ottobre 2026 (report, controllo, operatività, gate, learning, impostazioni con il
  kill switch del vecchio bot).

**Azioni** (`app/components/stock/`): della sessione «trading stock», che ne dichiara le pagine in `stock/area.tsx`. La guida è
`GUIDA_SCHEDA_AZIONI.md`.

**Tema e mattoni comuni.** Il tema resta chiaro; lo scuro si accende dal pulsante in alto e si ricorda sul dispositivo. I mattoni
comuni (scheda, curve a 100, riga di stato, pesi) stanno in `app/components/comuni/`, i conti in `app/lib/conti.ts`.

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

Scenari: `/?prova=calmo` (nessun allarme), `/?prova=fermo` (demo fermo), `/?prova=azioni_vuote#azioni/strategie` (Azioni vuota). Senza la variabile la configurazione è quella di sempre.

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
