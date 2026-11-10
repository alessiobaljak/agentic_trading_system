# La scheda «Azioni»: guida per la sessione «trading stock»

La dashboard ha già la scheda **Azioni** (fra Dettagli e Archivio, indirizzo `#azioni`). Oggi è un segnaposto:
`app/components/stock/Azioni.tsx` legge `/azioni` da Firebase con la forma qui sotto e la mostra con i mattoni comuni. Senza dati
scrive una riga sola: «La scheda delle azioni la riempie la sessione “trading stock”: nessun dato ancora su Firebase».

La cartella `app/components/stock/` è vostra: cambiate `Azioni.tsx` come volete e aggiungete lì i vostri componenti.

## 1. Cosa scrivere su Firebase (Realtime Database, sotto `/azioni`)

```text
/azioni
  battito            numero   ora dell'ultimo giro di chi scrive, in secondi (epoch); va scritto a ogni giro
  soglia_battito_s   numero   facoltativo: dopo quanti secondi senza battito la scheda dice «dati fermi?» (di serie 6 ore)
  strategie/
    <id>/                     id stabile, minuscolo, senza spazi (es. momentum_ch); non cambiarlo mai
      nome           testo    «Momentum svizzero»
      descrizione    testo    una riga
      tipo           testo    "paper" (ordini simulati) o "demo" (conto demo della piattaforma)
      ordine         numero   1-7, fisso per sempre: decide il colore (la tavolozza validata della dashboard)
      valuta         testo    "CHF", "USD", "EUR"…
      capitale       numero   capitale di partenza
      valore         numero   valore di adesso
      rendimento     numero   valore / capitale − 1 (facoltativo: la scheda lo ricalcola)
      comprate       numero   quante posizioni comprate
      vendute        numero   quante vendute (0 se solo acquisti)
      pesi           oggetto  { SIMBOLO: frazione del capitale }, + comprata, − venduta (0,21 = 21%)
      ultimo_ribilancio  oggetto  { ora: secondi, entrate: numero, uscite: numero }
      aggiornato     numero   quando è stato scritto `valore`, in secondi
      giorni         oggetto  { "AAAA-MM-GG": valore di fine giorno }: lo storico per le curve e per oggi / 7 giorni
      primo_giorno_dal_capitale  vero/falso  facoltativo: vero se il primo giorno di `giorni` parte dal capitale
  allarmi/
    <tipo>           oggetto  { ora: secondi, testo: "…" }: compare in rosso in cima; si toglie scrivendo null
```

Regole pratiche:

* **Date dei giorni**: le date della borsa, in ora svizzera (`Europe/Zurich`). Niente sabato e domenica. Il giorno di oggi la scheda
  lo ricava da `aggiornato` nello stesso fuso.
* **Simboli nei pesi**: Firebase non accetta `.` `#` `$` `[` `]` `/` nelle chiavi. Scrivete `NESN_SW` al posto di `NESN.SW`: la scheda
  rimette il punto.
* **Numeri veri, non testi**: valori e date in secondi come numeri; percentuali come frazioni (0,021 = 2,1%).
* Un esempio completo è in `prova/dati.ts`, funzione `creaAzioni`.

## 2. I mattoni comuni

Importateli da un punto solo, `app/components/comuni` (`index.ts` li elenca). Non leggono Firebase: i dati arrivano come proprietà.

| Mattone | Cosa fa |
|---|---|
| `SchedaBase` | La scheda di una strategia: valore, dall'inizio, oggi, 7 giorni, giorni in guadagno, posizioni, ultimo ribilancio, etichetta. Con `RigaPosizioni` (es. `cosa="azioni"`) e `SchedaSenzaNumeri` (in attesa o spenta). |
| `metricheDaSerie` | Calcola i numeri della scheda dai `giorni`, dal `valore`, dal `capitale` e da `giornoDiOggi` (per le azioni `giornoNelFuso(aggiornato, 'Europe/Zurich')`). |
| `CurveA100` | Le curve di più strategie messe a 100 alla stessa data: `curve=[{ chiave, nome, colore, giorni }]`. |
| `RigaStatoBase` | Vivo o fermo (dal `battito`), ultimo aggiornamento, avvisi in rosso. |
| `Pesi` | Comprate e vendute come barre orizzontali; `nomeDi` decide come mostrare i simboli. |
| `Info`, `Suggerimento`, `Colonna` | La «i» che si apre al tocco, il riquadro al tocco dei grafici, la colonna arrotondata dei grafici a barre. |
| Formati | `pct`, `punti`, `soldi(x, 'CHF')`, `giornoBreve`, `oraItaliana`, `durataFa`, `useAdesso`. |

I colori sono `var(--serie-1)` … `var(--serie-7)`, validati in chiaro e in scuro. Usateli nell'ordine fisso di `ordine`, mai a rotazione.
Per un grafico nuovo seguite la skill `dataviz`: una sola scala, leggenda, valori al tocco.

`app/components/stock/Azioni.tsx` mostra come si usano tutti questi mattoni insieme.

## 3. Provarla in locale, senza Firebase

```bash
cd dashboard
DASHBOARD_PROVA=1 NEXT_PUBLIC_FIREBASE_API_KEY=prova NEXT_PUBLIC_FIREBASE_PROJECT_ID=prova \
  NEXT_PUBLIC_FIREBASE_APP_ID=prova NEXT_PUBLIC_FIREBASE_DATABASE_URL=https://prova.invalid npx next dev -p 3999
```

* Con i dati finti: <http://localhost:3999/#azioni>.
* Scheda vuota: <http://localhost:3999/?prova=azioni_vuote#azioni>.

I dati finti stanno in `prova/dati.ts` (`creaAzioni`): cambiate lì l'esempio se cambiate la forma. Senza `DASHBOARD_PROVA` (cioè su
Vercel) la dashboard legge il Firebase vero e `prova/` non entra nel sito.

Prima di consegnare: `npx tsc --noEmit -p .` e `npm run build` senza errori.

## 4. Cosa non toccare

* Le schede crypto: `app/components/strategie/`, `app/components/dettagli/`, `app/components/Archivio.tsx` e i componenti del vecchio
  sistema, `app/lib/strategie.ts`, `app/lib/dettagli.ts`.
* I mattoni comuni (`app/components/comuni/`, `app/lib/conti.ts`) si possono ampliare con proprietà nuove facoltative. Non si cambia il
  loro aspetto né il significato di quelle che ci sono: le usano anche le schede crypto.
* In `DashboardShell.tsx` la scheda c'è già: non serve toccarlo.
* Mai credenziali del conto demo in un commit (il repo è pubblico).

## 5. Le regole di Firebase

* **Lettura.** Oggi `firebase/database.rules.json` dà la lettura di tutto, `/azioni` compreso, all'utente del proprietario; la
  scrittura è chiusa (`".write": false`).
* **Scrittura con l'Admin SDK.** Il bot delle crypto scrive con le credenziali di servizio (Admin SDK), che non passano dalle regole.
* **Scrittura in altro modo.** Se chi scrive i dati delle azioni usa un'altra strada (per esempio REST o un client con un utente), le
  regole dovranno permettere la scrittura su `/azioni` a quell'utente: un blocco `"azioni": { ".write": "auth != null && auth.uid ===
  '<UID di chi scrive>'" }`.
* **Chi le pubblica.** Le regole le pubblica il proprietario; ogni modifica di `firebase/` passa dalla revisione del percorso degli
  ordini (CLAUDE.md).
