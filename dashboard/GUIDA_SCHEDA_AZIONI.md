# L'area «Azioni» della Plancia: guida per la sessione «trading stock»

La dashboard si chiama **Plancia**. In alto ci sono le aree (**Crypto**, **Azioni**; la lista è in `app/components/aree.ts`). Toccando
un'area si apre la sua prima pagina, e a sinistra c'è il menu delle sue pagine; sul telefono il menu è il pulsante ☰.

L'area Azioni oggi ha una pagina sola, un segnaposto: `app/components/stock/Azioni.tsx` (indirizzo `#azioni/strategie`). Legge
`/azioni` da Firebase con la forma qui sotto e la mostra con i mattoni comuni. Senza dati scrive una riga sola: «La scheda delle azioni
la riempie la sessione “trading stock”: nessun dato ancora su Firebase».

La cartella `app/components/stock/` è vostra: cambiate `Azioni.tsx` come volete e aggiungete lì i vostri componenti e le vostre
pagine (sezione 2).

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

## 2. Le pagine del menu a sinistra

Le pagine dell'area le dichiarate voi, in `app/components/stock/area.tsx` (`AREA_AZIONI.pagine`), senza toccare il guscio. Una pagina
è una riga:

```tsx
{ id: 'posizioni', nome: 'Posizioni', icona: <svg …/>, Contenuto: PaginaPosizioni },
```

* **`id`**: il nome nell'indirizzo, minuscolo e senza spazi. La pagina sarà `#azioni/posizioni`.
* **`nome`**: la voce del menu.
* **`icona`**: facoltativa, un svg 24×24 con `stroke="currentColor"`.
* **`Contenuto`**: il componente della pagina.
* **L'ordine**: la prima pagina dell'elenco è la schermata principale dell'area.

`Contenuto` riceve due proprietà:

* `resto`: quello che nell'indirizzo viene dopo la pagina (in `#azioni/posizioni/nesn` è `['nesn']`);
* `vai(resto, { sostituisci })`: cambia quel resto restando nella pagina. `sostituisci: true` non lascia un passo nella cronologia;
  è il modo giusto per una scelta dentro la pagina, come i pulsanti delle strategie in Crypto → Dettagli.

**Testata facoltativa.** `Testata` è un componente mostrato in cima a tutte le pagine dell'area. Crypto la usa per «bot vivo» e gli
allarmi del demo. Per le azioni si potrebbe spostare lì la `RigaStatoBase` che oggi sta dentro `Azioni.tsx`.

Un'area nuova in futuro (per esempio «Forex»): una cartella sua con il suo `area.tsx` e una riga in `app/components/aree.ts`.

## 3. I mattoni comuni

Importateli da un punto solo, `app/components/comuni` (`index.ts` li elenca). Non leggono Firebase: i dati arrivano come proprietà.

| Mattone | Cosa fa |
|---|---|
| `SchedaBase` | La scheda di una strategia: valore, dall'inizio, oggi, 7 giorni, giorni in guadagno, posizioni, ultimo ribilancio, etichetta. Con `RigaPosizioni` (es. `cosa="azioni"`) e `SchedaSenzaNumeri` (in attesa o spenta). |
| `metricheDaSerie` | Calcola i numeri della scheda dai `giorni`, dal `valore`, dal `capitale` e da `giornoDiOggi` (per le azioni `giornoNelFuso(aggiornato, 'Europe/Zurich')`). |
| `CurveA100` | Le curve di più strategie messe a 100 alla stessa data: `curve=[{ chiave, nome, colore, giorni }]`. |
| Colonne giorno per giorno | Verde in guadagno, arancione in perdita: `var(--giorno-su)` e `var(--giorno-giu)`, validati in chiaro e in scuro. Esempio: `app/components/dettagli/RisultatoGiorni.tsx` con `Colonna`. |
| `RigaStatoBase` | Vivo o fermo (dal `battito`), ultimo aggiornamento, avvisi in rosso. |
| `Pesi` | Comprate e vendute come barre orizzontali; `nomeDi` decide come mostrare i simboli. |
| `Info`, `Suggerimento`, `Colonna` | La «i» che si apre al tocco, il riquadro al tocco dei grafici, la colonna arrotondata dei grafici a barre. |
| Formati | `pct`, `punti`, `soldi(x, 'CHF')`, `giornoBreve`, `oraItaliana`, `durataFa`, `useAdesso`. |

I colori sono `var(--serie-1)` … `var(--serie-7)`, validati in chiaro e in scuro. Usateli nell'ordine fisso di `ordine`, mai a rotazione.
Per un grafico nuovo seguite la skill `dataviz`: una sola scala, leggenda, valori al tocco.

`app/components/stock/Azioni.tsx` mostra come si usano tutti questi mattoni insieme.

## 4. Provarla in locale, senza Firebase

```bash
cd dashboard
DASHBOARD_PROVA=1 NEXT_PUBLIC_FIREBASE_API_KEY=prova NEXT_PUBLIC_FIREBASE_PROJECT_ID=prova \
  NEXT_PUBLIC_FIREBASE_APP_ID=prova NEXT_PUBLIC_FIREBASE_DATABASE_URL=https://prova.invalid npx next dev -p 3999
```

* Con i dati finti: <http://localhost:3999/#azioni/strategie>.
* Scheda vuota: <http://localhost:3999/?prova=azioni_vuote#azioni/strategie>.

I dati finti stanno in `prova/dati.ts` (`creaAzioni`): cambiate lì l'esempio se cambiate la forma. Senza `DASHBOARD_PROVA` (cioè su
Vercel) la dashboard legge il Firebase vero e `prova/` non entra nel sito.

Prima di consegnare: `npx tsc --noEmit -p .` e `npm run build` senza errori.

## 5. Cosa non toccare

* L'area Crypto: `app/components/crypto/`, `app/components/strategie/`, `app/components/dettagli/`, `app/components/Archivio.tsx` e i
  componenti del vecchio sistema, `app/lib/strategie.ts`, `app/lib/dettagli.ts`.
* I mattoni comuni (`app/components/comuni/`, `app/lib/conti.ts`) si possono ampliare con proprietà nuove facoltative. Non si cambia il
  loro aspetto né il significato di quelle che ci sono: le usano anche le schede crypto.
* Il guscio (`DashboardShell.tsx`) e la lista delle aree (`aree.ts`): l'area Azioni c'è già, le sue pagine si cambiano in
  `stock/area.tsx`.
* Mai credenziali del conto demo in un commit (il repo è pubblico).

## 6. Le regole di Firebase

* **Lettura.** Oggi `firebase/database.rules.json` dà la lettura di tutto, `/azioni` compreso, all'utente del proprietario; la
  scrittura è chiusa (`".write": false`).
* **Scrittura con l'Admin SDK.** Il bot delle crypto scrive con le credenziali di servizio (Admin SDK), che non passano dalle regole.
* **Scrittura in altro modo.** Se chi scrive i dati delle azioni usa un'altra strada (per esempio REST o un client con un utente), le
  regole dovranno permettere la scrittura su `/azioni` a quell'utente: un blocco `"azioni": { ".write": "auth != null && auth.uid ===
  '<UID di chi scrive>'" }`.
* **Chi le pubblica.** Le regole le pubblica il proprietario; ogni modifica di `firebase/` passa dalla revisione del percorso degli
  ordini (CLAUDE.md).
