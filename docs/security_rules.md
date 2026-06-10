# Security rules Firebase (Firestore + Realtime DB)

Le regole vivono in `firebase/firestore.rules` e `firebase/database.rules.json`,
wired in `firebase.json` per il deploy via Firebase CLI.

## Modello di sicurezza
- **Il bot** usa il Firebase **Admin SDK** (service account): **bypassa** le
  regole. Scrive liberamente `trades`, `memory`, `strategy_weights`, `insights`,
  `/positions`, `/bot_status`, `/risk_state`.
- **La dashboard** (client) è soggetta alle regole. Due strati:
  1. **Vercel Deployment Protection** — decide chi può aprire la pagina.
  2. **Firebase Auth (Google)** — la dashboard fa login; le regole richiedono un
     utente autenticato per leggere e per scrivere.

## Cosa permette il client
- **Firestore**: lettura di tutto se autenticato; scrittura **solo** su
  `user_risk_settings/current` ed **entro gli hard cap** (leverage 1–5,
  risk 0.5%–3%) — difesa in profondità che rispecchia i limiti del codice.
  Nessun'altra scrittura dal client.
- **Realtime DB**: lettura di tutto se autenticato; scrittura **solo** su
  `/commands/kill_switch` (booleano). Nient'altro.

## Deploy delle regole
```bash
npm i -g firebase-tools
firebase login
firebase use <project-id>
firebase deploy --only firestore:rules,database
```

## Abilitare il login Google (una volta)
Firebase Console → **Authentication** → *Sign-in method* → abilita **Google**.
Aggiungi i domini autorizzati: `localhost` e il dominio Vercel
(`agentic-trading-system.vercel.app`).

## Hardening consigliato: blocca al TUO UID
Dopo il primo login, prendi il tuo UID (Console → Authentication → Users) e:
- in `firebase/firestore.rules` decommenta `isOwner()` e usalo al posto di
  `signedIn()`;
- in `firebase/database.rules.json` sostituisci `auth != null` con
  `auth.uid === 'IL_TUO_UID'`.

Così, anche se qualcuno ottenesse un token anonimo/Google per il progetto, non
potrebbe né leggere lo stato né toccare il kill switch: solo il tuo account.

## Nota
Senza login, la dashboard mostra "Accesso richiesto". Con Vercel protetto +
Google login + UID lock hai tre strati: solo tu apri la pagina, solo tu ti
autentichi, solo il tuo UID può agire.
