# Scrivere a Claude dalla dashboard

Serve a un caso preciso: essere in viaggio, senza poter aprire Claude Code, e avere
comunque bisogno di chiedere qualcosa al sistema. La tab **Claude** della dashboard
apre una barra di testo; la risposta arriva nella stessa pagina.

## Come funziona davvero

Claude non è un servizio sempre acceso a cui mandare una richiesta: esiste quando una
sessione parte. Quindi "scrivergli" vuol dire **far partire una sessione**, e l'unico
innesco che questo progetto ha già è GitHub Actions. Il giro è questo:

```
dashboard  ──►  /api/claude  ──►  commento su issue #1  ──►  workflow claude.yml
                                                                    │
dashboard  ◄──  /api/claude  ◄──  commenti della issue  ◄──  risposta di Claude
```

La conversazione **vive su GitHub**, non nella dashboard. Due conseguenze utili:
sopravvive ai deploy di Vercel, e se la dashboard non fosse raggiungibile il thread si
legge (e si scrive) direttamente da
[issue #1](https://github.com/alessiobaljak/agentic_trading_system/issues/1), anche dal
telefono. È il piano B, ed è già pronto: basta che il commento contenga `@claude`.

## Le due cose da sapere prima di usarla

1. **La risposta non è immediata.** Deve avviarsi una macchina su GitHub Actions,
   scaricare il repo e leggerlo: **uno-tre minuti**. La tab lo dice esplicitamente
   invece di far girare uno spinner.
2. **La sessione che risponde è nuova ogni volta.** Non ha la memoria delle chat fatte
   dentro Claude Code. Ha il repo, questo thread e `CLAUDE.md` (che le spiega il
   progetto, le regole e come usare il canale ops). Conviene scrivere domande che
   stanno in piedi da sole: «com'è messo il gate?» funziona, «e quell'altra cosa di
   ieri?» no.

Cosa **può** fare: leggere tutto il codice e i documenti, rispondere, modificare il
codice e committare, mettere in coda una richiesta per la VPS in `ops/requests/`.

Cosa **non può** fare: entrare sulla VPS o leggere Firebase direttamente. Per sapere
cosa sta succedendo adesso sulla macchina deve passare dal canale ops, e l'esito arriva
qualche minuto dopo in `ops/results/`.

## Configurazione — quattro passi

La issue **#1 esiste già**. Restano le chiavi.

### 1. Il segreto di Anthropic (su GitHub)

`Settings → Secrets and variables → Actions → New repository secret`

| Nome | Valore |
|---|---|
| `ANTHROPIC_API_KEY` | la chiave API di Anthropic |

Senza questa il workflow parte e fallisce subito.

### 2. Un token GitHub per la dashboard

`github.com/settings/personal-access-tokens/new` — **fine-grained**, non classico.

* Repository access: **solo** `alessiobaljak/agentic_trading_system`
* Permissions → Repository → **Issues: Read and write**. Nient'altro.
* Scadenza: metti la più lunga che accetti di rinnovare.

È il token con cui la dashboard scrive il commento. Non serve altro: con questi soli
permessi non può toccare il codice.

### 3. Le variabili su Vercel

`Project → Settings → Environment Variables`. **Nessuna con il prefisso
`NEXT_PUBLIC_`**: quel prefisso le mette dentro il pacchetto che arriva al browser, e
un token nel browser ce l'ha chiunque apra la pagina.

| Nome | Valore |
|---|---|
| `GH_TOKEN` | il token del passo 2 |
| `CLAUDE_CHAT_ISSUE` | `1` |
| `CLAUDE_CHAT_UIDS` | il tuo UID Firebase (vedi sotto) |
| `GH_REPO` | *(facoltativa)* `alessiobaljak/agentic_trading_system` |

**Come trovi il tuo UID:** fai il deploy con le prime due variabili, apri la tab
Claude, e il pannello ti risponderà *«CLAUDE_CHAT_UIDS non è impostata, il tuo UID è:
…»*. Copialo, incollalo nella variabile, redeploy. È fatto apposta: la rotta nasce
chiusa e ti dice come aprirla, invece di nascere aperta.

### 4. Redeploy

Vercel non ricarica le variabili senza un nuovo deploy.

## Perché è chiusa così

**Questo repo è pubblico.** Due porte, entrambe da sbarrare:

* **La rotta della dashboard** ha un token che può scrivere sulle issue. Riusa il login
  Google che la dashboard ha già: il browser manda il suo ID token, il server lo fa
  validare a Google e controlla che l'UID sia nella lista. Senza la lista non lascia
  passare nessuno.
* **Il workflow** risponde a `issue_comment`, e su un repo pubblico chiunque può
  commentare. La condizione in testa al job (`comment.user.login ==
  repository_owner`) è l'unica cosa che separa "il proprietario chiede" da "chiunque
  comanda". L'azione ha una sua difesa, ma scatta dopo l'avvio del job — e il job usa
  già il segreto. Il filtro ferma prima.

Se un giorno il repo diventasse privato, il filtro resta corretto: non costa nulla.

## Costi

Ogni messaggio è una passata di GitHub Actions (minuti gratuiti sui repo pubblici) più
il consumo API di Anthropic della sessione. Una domanda di riepilogo costa poco; «leggi
tutto il backtesting e dimmi cosa non va» costa quanto una sessione vera.

## Se non funziona

| Sintomo | Causa quasi certa |
|---|---|
| «non configurato: mancano GH_TOKEN e/o CLAUDE_CHAT_ISSUE» | variabili non impostate, o deploy non rifatto |
| «CLAUDE_CHAT_UIDS non è impostata… il tuo UID è» | passo 3, incolla l'UID |
| «utente non autorizzato» | l'UID nella variabile non è quello con cui sei loggato |
| «GitHub ha risposto 401/403» | token scaduto o senza permesso Issues |
| il messaggio parte ma non risponde nessuno | manca `ANTHROPIC_API_KEY`, oppure il workflow è fallito — guarda la tab Actions |
| risponde ma dice cose vaghe sul presente | è normale: non vede Firebase. Chiedi di passare dal canale ops |
