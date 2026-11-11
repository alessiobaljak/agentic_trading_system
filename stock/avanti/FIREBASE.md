# Chi scrive le azioni su Firebase

Per la Plancia (`dashboard/GUIDA_SCHEDA_AZIONI.md`): quale percorso, quale account e con quali permessi, così le regole di Firebase si
preparano insieme a quelle delle crypto.

* **Percorso:** solo `/azioni` del Realtime Database (battito, `strategie/prima_candela_15m`, allarmi). Nient'altro.
* **Chi scrive:** il programma `stock/avanti/plancia.py`, lanciato dalla sessione «trading stock» dopo gli ordini delle 9:45 e dopo la
  chiusura delle 15:55 di New York (routine nei giorni di borsa), e a mano con `python -m stock.avanti.plancia`.
* **Come:** con un **utente dedicato** di Firebase Authentication (email e password), non con le credenziali di servizio del bot:
  accesso con l'API REST di Firebase Authentication, poi `PUT /azioni.json?auth=<token>`. Così, anche se le credenziali delle azioni
  uscissero, si potrebbe scrivere solo sotto `/azioni`.
* **Dove stanno le credenziali:** solo nelle variabili dell'ambiente della sessione «trading stock», mai nel repository:
  `AZIONI_FIREBASE_URL` (indirizzo del database), `AZIONI_FIREBASE_API_KEY` (chiave web del progetto, la stessa della dashboard),
  `AZIONI_FIREBASE_EMAIL`, `AZIONI_FIREBASE_PASSWORD`.

## Cosa serve dal proprietario (una volta)

1. In Firebase → Authentication, creare un utente con email e password solo per le azioni (per esempio `azioni@<tuo dominio>`), e
   copiarne l'**UID**.
2. Aggiungere alle regole del Realtime Database il blocco qui sotto, con quell'UID (le regole le pubblica il proprietario; il file
   `firebase/database.rules.json` è della parte crypto e passa dalla revisione del percorso degli ordini):

   ```json
   "azioni": {
     ".write": "auth != null && auth.uid === '<UID DELL'UTENTE AZIONI>'"
   }
   ```

   La lettura di `/azioni` resta quella di oggi (l'utente del proprietario legge tutto).
3. Mettere le quattro variabili nell'ambiente della sessione (impostazioni dell'ambiente → variabili), poi riaprire la sessione.

Senza questi passi `plancia.py` non scrive e lo dice; gli ordini sul conto demo vanno avanti lo stesso.

## Dove stanno le chiavi (dall'11 novembre 2026)

Come per le crypto, nei **segreti del repository su GitHub** (Settings → Secrets and variables → Actions), letti dal lavoro automatico
`.github/workflows/azioni_avanti.yml`: `ALPACA_API_KEY_ID`, `ALPACA_API_SECRET_KEY` (conto demo), `AZIONI_FIREBASE_URL`,
`AZIONI_FIREBASE_API_KEY`, `AZIONI_FIREBASE_EMAIL`, `AZIONI_FIREBASE_PASSWORD`. Il lavoro apre gli ordini, chiude, scrive il diario e
pubblica sulla Plancia nei giorni di borsa; gli orari programmati partono solo se esiste `stock/avanti/acceso_su_github`. Quando è
acceso, le routine della sessione «trading stock» si spengono e le chiavi si tolgono dall'ambiente «Default» delle sessioni.
